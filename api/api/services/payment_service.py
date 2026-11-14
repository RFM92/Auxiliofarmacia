"""
PaymentService - Integração com Stripe e Asaas
"""
import logging
import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, Payment, PaymentStatus, PaymentMethod, License, LicenseTier
from ..config import settings
from .license_service import LicenseService

logger = logging.getLogger(__name__)


class PaymentService:
    """Serviço de pagamentos"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.license_service = LicenseService(db)

    # ========== STRIPE ==========
    async def create_stripe_checkout(
        self,
        user: User,
        plan: str,
        success_url: str,
        cancel_url: str,
        cpf_cnpj: str = None,
    ) -> Dict:
        """
        Cria sessão de checkout no Stripe
        """
        if not settings.STRIPE_SECRET_KEY:
            return self._mock_checkout_response(user, plan, "stripe")

        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Determina price_id
            price_id_map = {
                "pro": settings.STRIPE_PRICE_ID_PRO,
                "premium": settings.STRIPE_PRICE_ID_PREMIUM,
                "institutional": settings.STRIPE_PRICE_ID_INSTITUTIONAL,
            }
            price_id = price_id_map.get(plan)

            if not price_id:
                raise ValueError(f"Plano inválido: {plan}")

            # Cria checkout session
            checkout_session = stripe.checkout.Session.create(
                customer_email=user.email,
                payment_method_types=["card", "boleto"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
                metadata={
                    "user_id": user.id,
                    "plan": plan,
                    "cpf_cnpj": cpf_cnpj or "",
                },
            )

            # Salva payment pending
            payment = Payment(
                user_id=user.id,
                plan=plan,
                value=self._plan_price(plan),
                currency="BRL",
                method=PaymentMethod.STRIPE_CARD,
                gateway="stripe",
                gateway_id=checkout_session.id,
                status=PaymentStatus.PENDING,
            )
            self.db.add(payment)
            await self.db.commit()

            return {
                "success": True,
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "payment_id": payment.id,
            }

        except Exception as e:
            logger.error(f"Erro Stripe: {e}")
            return {"success": False, "error": str(e)}

    # ========== ASAAS (BRASIL) ==========
    async def create_asaas_payment(
        self,
        user: User,
        plan: str,
        method: str = "pix",  # pix, boleto, card
        cpf_cnpj: str = None,
    ) -> Dict:
        """
        Cria cobrança no Asaas
        """
        if not settings.ASAAS_API_KEY:
            return self._mock_checkout_response(user, plan, "asaas")

        # Mapear método
        method_map = {
            "pix": (PaymentMethod.ASAAS_PIX, "PIX"),
            "boleto": (PaymentMethod.ASAAS_BOLETO, "BOLETO"),
            "card": (PaymentMethod.ASAAS_CARD, "CREDIT_CARD"),
        }
        payment_method, billing_type = method_map.get(method, method_map["pix"])

        try:
            base_url = (
                "https://api.asaas.com/v3"
                if settings.ASAAS_ENVIRONMENT == "production"
                else "https://sandbox.asaas.com/v3"
            )
            headers = {
                "access_token": settings.ASAAS_API_KEY,
                "Content-Type": "application/json",
            }

            # 1. Cria ou busca cliente
            customer_id = await self._get_or_create_asaas_customer(
                user, cpf_cnpj, base_url, headers
            )

            # 2. Cria cobrança
            value = self._plan_price(plan)
            due_date = (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")

            payload = {
                "customer": customer_id,
                "billingType": billing_type,
                "value": value,
                "dueDate": due_date,
                "description": f"Auxílio Farmácia {plan.upper()} - 1 mês",
                "externalReference": f"user_{user.id}_plan_{plan}",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{base_url}/payments",
                    json=payload,
                    headers=headers,
                    timeout=10.0,
                )

            if response.status_code not in (200, 201):
                logger.error(f"Erro Asaas: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}

            data = response.json()

            # Salva payment
            payment = Payment(
                user_id=user.id,
                plan=plan,
                value=value,
                currency="BRL",
                method=payment_method,
                gateway="asaas",
                gateway_id=data["id"],
                status=PaymentStatus.PENDING,
                gateway_response=data,
                cpf_cnpj=cpf_cnpj or (user.crm or ""),
            )
            self.db.add(payment)
            await self.db.commit()
            await self.db.refresh(payment)

            # PIX: busca QR code
            qr_code = None
            if billing_type == "PIX":
                async with httpx.AsyncClient() as client:
                    qr_response = await client.get(
                        f"{base_url}/payments/{data['id']}/pixQrCode",
                        headers=headers,
                        timeout=10.0,
                    )
                if qr_response.status_code == 200:
                    qr_data = qr_response.json()
                    qr_code = qr_data

            return {
                "success": True,
                "payment_id": payment.id,
                "asaas_id": data["id"],
                "status": data.get("status"),
                "value": value,
                "due_date": data.get("dueDate"),
                "invoice_url": data.get("invoiceUrl"),
                "bank_slip_url": data.get("bankSlipUrl"),
                "pix_qr_code": qr_code,
            }

        except Exception as e:
            logger.error(f"Erro Asaas: {e}")
            return {"success": False, "error": str(e)}

    async def _get_or_create_asaas_customer(
        self,
        user: User,
        cpf_cnpj: str,
        base_url: str,
        headers: dict,
    ) -> str:
        """Busca ou cria cliente no Asaas"""
        # Busca por email
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/customers",
                params={"email": user.email},
                headers=headers,
                timeout=10.0,
            )

        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                return data["data"][0]["id"]

        # Cria novo
        payload = {
            "name": user.name,
            "email": user.email,
            "phone": user.phone or "",
            "cpfCnpj": cpf_cnpj or user.crm or "00000000000",
            "notificationDisabled": False,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/customers",
                json=payload,
                headers=headers,
                timeout=10.0,
            )

        if response.status_code in (200, 201):
            return response.json()["id"]

        raise Exception(f"Falha ao criar cliente Asaas: {response.text}")

    # ========== WEBHOOKS ==========
    async def handle_stripe_webhook(self, event_data: dict) -> bool:
        """Processa webhook do Stripe"""
        try:
            event_type = event_data.get("type")
            logger.info(f"📨 Stripe webhook: {event_type}")

            if event_type == "checkout.session.completed":
                session = event_data["data"]["object"]
                await self._fulfill_payment(
                    gateway_id=session["id"],
                    gateway="stripe",
                    gateway_data=session,
                )
            elif event_type == "invoice.paid":
                invoice = event_data["data"]["object"]
                await self._fulfill_payment(
                    gateway_id=invoice.get("subscription"),
                    gateway="stripe",
                    gateway_data=invoice,
                )
            elif event_type == "customer.subscription.deleted":
                subscription = event_data["data"]["object"]
                # Cancela assinatura
                logger.info(f"Subscription cancelled: {subscription['id']}")

            return True
        except Exception as e:
            logger.error(f"Erro webhook Stripe: {e}")
            return False

    async def handle_asaas_webhook(self, event_data: dict) -> bool:
        """Processa webhook do Asaas"""
        try:
            event_type = event_data.get("event")
            payment_data = event_data.get("payment", {})

            logger.info(f"📨 Asaas webhook: {event_type}")

            if event_type in ("PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"):
                await self._fulfill_payment(
                    gateway_id=payment_data.get("id"),
                    gateway="asaas",
                    gateway_data=payment_data,
                )
            elif event_type == "PAYMENT_OVERDUE":
                # Marca como overdue
                result = await self.db.execute(
                    select(Payment).where(Payment.gateway_id == payment_data.get("id"))
                )
                payment = result.scalar_one_or_none()
                if payment:
                    payment.status = PaymentStatus.FAILED

            return True
        except Exception as e:
            logger.error(f"Erro webhook Asaas: {e}")
            return False

    # ========== FULFILLMENT ==========
    async def _fulfill_payment(
        self,
        gateway_id: str,
        gateway: str,
        gateway_data: dict,
    ):
        """Após pagamento confirmado, cria licença"""
        from sqlalchemy import select

        result = await self.db.execute(
            select(Payment).where(
                Payment.gateway_id == gateway_id,
                Payment.gateway == gateway,
            )
        )
        payment = result.scalar_one_or_none()

        if not payment:
            logger.warning(f"Payment não encontrado: {gateway_id}")
            return

        if payment.status == PaymentStatus.PAID:
            return  # já processado

        # Marca como pago
        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.utcnow()

        # Busca usuário
        result = await self.db.execute(
            select(User).where(User.id == payment.user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return

        # Cria licença
        license = await self.license_service.create_license(
            user=user,
            tier=payment.plan,
            duration_days=30,
            source=f"{gateway}",
        )

        # Vincula
        payment.license_id = license.id
        payment.expires_at = license.expires_at

        await self.db.commit()

        logger.info(f"✅ Licença criada para pagamento {payment.id}: {license.key}")

    # ========== HELPERS ==========
    def _plan_price(self, plan: str) -> float:
        prices = {
            "pro": settings.PLAN_PRICE_PRO,
            "premium": settings.PLAN_PRICE_PREMIUM,
            "institutional": settings.PLAN_PRICE_INSTITUTIONAL,
        }
        return prices.get(plan, 0.0)

    def _mock_checkout_response(self, user: User, plan: str, gateway: str) -> Dict:
        """Resposta mock quando gateway não está configurado (dev)"""
        return {
            "success": True,
            "mock": True,
            "message": f"Gateway {gateway} não configurado - modo dev",
            "checkout_url": f"/checkout/mock?plan={plan}",
            "payment_id": "mock_payment_id",
        }
