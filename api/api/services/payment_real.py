"""
Servico de Pagamento REAL
- Stripe: cartao internacional
- Asaas: PIX + Boleto (Brasil)

Implementa integracao completa com webhooks e fallback para modo demo.
"""
import os
import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from decimal import Decimal

import httpx
import stripe

from ..config import settings

logger = logging.getLogger(__name__)


# ========== PLANOS ==========
PLANS = {
    'pro': {
        'name': 'Pro',
        'description': 'Dashboard Pro - 30 dias',
        'prices': {
            'brl': 29.90,
            'usd': 5.99,
        },
        'duration_days': 30,
    },
    'premium': {
        'name': 'Premium',
        'description': 'Dashboard Premium - 90 dias',
        'prices': {
            'brl': 79.90,
            'usd': 15.99,
        },
        'duration_days': 90,
    },
    'institutional': {
        'name': 'Institucional',
        'description': 'Dashboard Institucional - 365 dias',
        'prices': {
            'brl': 297.00,
            'usd': 59.99,
        },
        'duration_days': 365,
    },
    'curso_antibioticos': {
        'name': 'Curso Antibioticoterapia',
        'description': 'Curso individual',
        'prices': {'brl': 197.00, 'usd': 39.99},
        'duration_days': 36500,  # vitalicio
    },
    'curso_aines': {
        'name': 'Curso AINEs',
        'description': 'Curso individual',
        'prices': {'brl': 147.00, 'usd': 29.99},
        'duration_days': 36500,
    },
    'curso_analgesicos': {
        'name': 'Curso Analgesicos',
        'description': 'Curso individual',
        'prices': {'brl': 167.00, 'usd': 33.99},
        'duration_days': 36500,
    },
    'curso_antihipertensivos': {
        'name': 'Curso Anti-hipertensivos',
        'description': 'Curso individual',
        'prices': {'brl': 197.00, 'usd': 39.99},
        'duration_days': 36500,
    },
    'curso_diabeticos': {
        'name': 'Curso Antidiabeticos',
        'description': 'Curso individual',
        'prices': {'brl': 177.00, 'usd': 35.99},
        'duration_days': 36500,
    },
    'curso_psicotropicos': {
        'name': 'Curso Psicotropicos',
        'description': 'Curso individual',
        'prices': {'brl': 197.00, 'usd': 39.99},
        'duration_days': 36500,
    },
    'curso_corticoides': {
        'name': 'Curso Corticoides',
        'description': 'Curso individual',
        'prices': {'brl': 127.00, 'usd': 25.99},
        'duration_days': 36500,
    },
    'curso_anticoagulantes': {
        'name': 'Curso Anticoagulantes',
        'description': 'Curso individual',
        'prices': {'brl': 167.00, 'usd': 33.99},
        'duration_days': 36500,
    },
    'bundle_curso_pro': {
        'name': 'Bundle: Curso + Pro',
        'description': '1 curso + Dashboard Pro (30 dias)',
        'prices': {'brl': 297.00, 'usd': 59.99},
        'duration_days': 30,
    },
    'bundle_trilha_completa': {
        'name': 'Trilha Completa',
        'description': 'Todos os 8 cursos + Premium (12 meses)',
        'prices': {'brl': 1297.00, 'usd': 259.99},
        'duration_days': 365,
    },
    'bundle_institucional_cursos': {
        'name': 'Bundle Institucional',
        'description': 'Ate 50 usuarios + todos os cursos',
        'prices': {'brl': 1997.00, 'usd': 399.99},
        'duration_days': 365,
    },
}


def _is_configured(value: Optional[str]) -> bool:
    """
    Detecta se uma credencial esta REALMENTE configurada.

    Placeholders comuns ("your_key_here", "REPLACE", "xxx", "CHANGE_ME",
    "<sua_chave>", "invalid") sao detectados para nao tentar chamar a API
    de producao com uma chave falsa.
    """
    if not value:
        return False
    v = value.strip().lower()
    if len(v) < 12:
        return False
    marcadores = ('replace', 'your_', 'your-', 'sua_chave', 'sua-chave', 'xxx',
                  'change_me', 'change-me', 'placeholder', 'example', 'invalid',
                  '<', '>', 'aqui', 'cole_aqui', 'test123', 'fake', 'demo_key')
    return not any(m in v for m in marcadores)


class StripePaymentService:
    """Integracao com Stripe (cartao internacional)"""

    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        if _is_configured(self.api_key):
            stripe.api_key = self.api_key
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Stripe nao configurado - usando modo demo")

    async def create_checkout_session(
        self,
        plan_id: str,
        user_email: str,
        success_url: str,
        cancel_url: str,
        currency: str = 'brl'
    ) -> Dict[str, Any]:
        """Cria sessao de checkout Stripe"""
        plan = PLANS.get(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")

        amount_cents = int(plan['prices'][currency] * 100)

        if not self.enabled:
            # Modo demo - retorna URL fake
            return {
                'id': f'cs_demo_{uuid.uuid4().hex[:16]}',
                'url': f'{success_url}&demo=true&session_id=demo_{uuid.uuid4().hex[:8]}',
                'amount_total': amount_cents,
                'currency': currency,
                'mode': 'demo'
            }

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card', 'pix'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'unit_amount': amount_cents,
                        'product_data': {
                            'name': plan['name'],
                            'description': plan['description'],
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={
                    'plan_id': plan_id,
                    'user_email': user_email,
                }
            )
            return {
                'id': session.id,
                'url': session.url,
                'amount_total': amount_cents,
                'currency': currency,
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro Stripe: {e}")
            raise

    async def create_payment_intent(
        self,
        plan_id: str,
        amount: float,
        currency: str = 'brl'
    ) -> Dict[str, Any]:
        """Cria PaymentIntent para integracao customizada"""
        amount_cents = int(amount * 100)

        if not self.enabled:
            return {
                'id': f'pi_demo_{uuid.uuid4().hex[:16]}',
                'client_secret': f'pi_demo_secret_{uuid.uuid4().hex[:24]}',
                'amount': amount_cents,
                'currency': currency,
                'mode': 'demo'
            }

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                automatic_payment_methods={'enabled': True},
                metadata={'plan_id': plan_id}
            )
            return {
                'id': intent.id,
                'client_secret': intent.client_secret,
                'amount': amount_cents,
                'currency': currency,
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro PaymentIntent: {e}")
            raise

    async def handle_webhook(self, payload: bytes, sig: str) -> Dict[str, Any]:
        """Processa webhook do Stripe"""
        if not self.enabled or not self.webhook_secret:
            # Modo demo - parse direto
            try:
                event = json.loads(payload)
                return {'received': True, 'demo': True, 'event': event}
            except json.JSONDecodeError:
                return {'received': True, 'demo': True, 'event': {}}

        try:
            event = stripe.Webhook.construct_event(
                payload, sig, self.webhook_secret
            )

            # Processa eventos
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                return {
                    'received': True,
                    'event_type': 'checkout.session.completed',
                    'session_id': session['id'],
                    'customer_email': session.get('customer_email'),
                    'metadata': session.get('metadata', {}),
                    'amount_total': session.get('amount_total'),
                    'currency': session.get('currency'),
                    'payment_status': session.get('payment_status'),
                }
            elif event['type'] == 'payment_intent.succeeded':
                intent = event['data']['object']
                return {
                    'received': True,
                    'event_type': 'payment_intent.succeeded',
                    'intent_id': intent['id'],
                    'amount': intent['amount'],
                    'currency': intent['currency'],
                    'metadata': intent.get('metadata', {})
                }
            return {'received': True, 'event_type': event['type']}

        except ValueError as e:
            logger.error(f"Webhook invalido: {e}")
            return {'received': False, 'error': str(e)}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Assinatura invalida: {e}")
            return {'received': False, 'error': 'invalid signature'}


class AsaasPaymentService:
    """Integracao com Asaas (PIX + Boleto - Brasil)"""

    BASE_URL_SANDBOX = 'https://sandbox.asaas.com/api/v3'
    BASE_URL_PRODUCTION = 'https://www.asaas.com/api/v3'

    def __init__(self):
        self.api_key = settings.ASAAS_API_KEY
        self.environment = settings.ASAAS_ENVIRONMENT
        self.webhook_token = settings.ASAAS_WEBHOOK_TOKEN

        if _is_configured(self.api_key):
            self.base_url = (
                self.BASE_URL_PRODUCTION if self.environment == 'production'
                else self.BASE_URL_SANDBOX
            )
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Asaas nao configurado - usando modo demo")

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Faz request autenticada"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json',
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method, url, headers=headers, **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def create_customer(self, name: str, email: str, cpf_cnpj: str = None) -> Dict[str, Any]:
        """Cria ou busca cliente"""
        if not self.enabled:
            return {
                'id': f'cus_demo_{uuid.uuid4().hex[:16]}',
                'name': name,
                'email': email,
                'mode': 'demo'
            }

        try:
            # Busca cliente existente
            existing = await self._request(
                'GET',
                f'/customers?email={email}'
            )
            if existing.get('data'):
                return existing['data'][0]

            # Cria novo
            payload = {
                'name': name,
                'email': email,
            }
            if cpf_cnpj:
                payload['cpfCnpj'] = cpf_cnpj

            customer = await self._request('POST', '/customers', json=payload)
            return customer
        except Exception as e:
            logger.error(f"Erro Asaas customer: {e}")
            raise

    async def create_pix_payment(
        self,
        plan_id: str,
        user_email: str,
        user_name: str,
        user_cpf: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria cobranca PIX"""
        plan = PLANS.get(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")

        amount = plan['prices']['brl']
        due_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

        if not self.enabled:
            # Demo - gera PIX code fake + QR placeholder
            return {
                'id': f'pay_demo_{uuid.uuid4().hex[:16]}',
                'status': 'PENDING',
                'value': amount,
                'due_date': due_date,
                'billing_type': 'PIX',
                'pix_code': self._generate_demo_pix_code(amount, plan_id),
                'pix_qr_code': f'data:image/svg+xml;base64,demo_qr_code_{plan_id}',
                'invoice_url': f'https://demo.asaas.com/i/{uuid.uuid4().hex[:10]}',
                'mode': 'demo'
            }

        try:
            # Cria cliente
            customer = await self.create_customer(user_name, user_email, user_cpf)

            # Cria cobranca
            payment = await self._request('POST', '/payments', json={
                'customer': customer['id'],
                'billingType': 'PIX',
                'value': amount,
                'dueDate': due_date,
                'description': f'{plan["name"]} - Auxílio Farmácia',
                'externalReference': plan_id,
            })

            # Busca QR Code PIX
            pix_data = await self._request(
                'GET',
                f'/payments/{payment["id"]}/pixQrCode'
            )

            return {
                'id': payment['id'],
                'status': payment['status'],
                'value': payment['value'],
                'due_date': payment['dueDate'],
                'billing_type': 'PIX',
                'pix_code': pix_data.get('payload', ''),
                'pix_qr_code': pix_data.get('encodedImage', ''),
                'invoice_url': payment.get('invoiceUrl', ''),
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro Asaas PIX: {e}")
            raise

    async def create_boleto_payment(
        self,
        plan_id: str,
        user_email: str,
        user_name: str,
        user_cpf: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria cobranca por Boleto"""
        plan = PLANS.get(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")

        amount = plan['prices']['brl']
        due_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

        if not self.enabled:
            return {
                'id': f'pay_demo_{uuid.uuid4().hex[:16]}',
                'status': 'PENDING',
                'value': amount,
                'due_date': due_date,
                'billing_type': 'BOLETO',
                'boleto_url': f'https://demo.asaas.com/b/{uuid.uuid4().hex[:10]}.pdf',
                'barcode': '00190.00009 01234.567890 12345.678901 2 12345678901234',
                'mode': 'demo'
            }

        try:
            customer = await self.create_customer(user_name, user_email, user_cpf)

            payment = await self._request('POST', '/payments', json={
                'customer': customer['id'],
                'billingType': 'BOLETO',
                'value': amount,
                'dueDate': due_date,
                'description': f'{plan["name"]} - Auxílio Farmácia',
                'externalReference': plan_id,
            })

            return {
                'id': payment['id'],
                'status': payment['status'],
                'value': payment['value'],
                'due_date': payment['dueDate'],
                'billing_type': 'BOLETO',
                'boleto_url': payment.get('bankSlipUrl', ''),
                'invoice_url': payment.get('invoiceUrl', ''),
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro Asaas Boleto: {e}")
            raise

    async def create_credit_card_payment(
        self,
        plan_id: str,
        user_email: str,
        user_name: str,
        credit_card: Dict[str, str],
        user_cpf: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria cobranca via Cartao de Credito"""
        plan = PLANS.get(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")

        if not self.enabled:
            return {
                'id': f'pay_demo_{uuid.uuid4().hex[:16]}',
                'status': 'PENDING',
                'value': plan['prices']['brl'],
                'billing_type': 'CREDIT_CARD',
                'invoice_url': f'https://demo.asaas.com/i/{uuid.uuid4().hex[:10]}',
                'mode': 'demo'
            }

        try:
            customer = await self.create_customer(user_name, user_email, user_cpf)

            # Cobranca de cartao SEM enviar dados do cartao para o nosso
            # servidor (PCI-DSS). O Asaas gera um checkout hospedado
            # (invoiceUrl) onde o proprio cliente digita o cartao.
            due = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
            payment = await self._request('POST', '/payments', json={
                'customer': customer['id'],
                'billingType': 'CREDIT_CARD',
                'value': plan['prices']['brl'],
                'dueDate': due,
                'description': f'{plan["name"]} - Auxilio Farmacia',
                'externalReference': plan_id,
            })

            return {
                'id': payment['id'],
                'status': payment['status'],
                'value': payment['value'],
                'due_date': payment.get('dueDate', due),
                'billing_type': 'CREDIT_CARD',
                'invoice_url': payment.get('invoiceUrl', ''),
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro Asaas Cartao: {e}")
            raise

    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Consulta status do pagamento"""
        if not self.enabled:
            return {
                'id': payment_id,
                'status': 'CONFIRMED',
                'mode': 'demo'
            }

        try:
            payment = await self._request('GET', f'/payments/{payment_id}')
            return {
                'id': payment['id'],
                'status': payment['status'],
                'value': payment['value'],
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro status: {e}")
            raise

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Processa webhook do Asaas"""
        event_type = payload.get('event')

        event_map = {
            'PAYMENT_CREATED': 'payment_created',
            'PAYMENT_AWAITING_RISK_ANALYSIS': 'payment_risk_analysis',
            'PAYMENT_APPROVED_BY_RISK_ANALYSIS': 'payment_risk_approved',
            'PAYMENT_REPROVED_BY_RISK_ANALYSIS': 'payment_risk_reproved',
            'PAYMENT_UPDATED': 'payment_updated',
            'PAYMENT_CONFIRMED': 'payment_confirmed',
            'PAYMENT_RECEIVED': 'payment_received',
            'PAYMENT_OVERDUE': 'payment_overdue',
            'PAYMENT_DELETED': 'payment_deleted',
            'PAYMENT_REFUNDED': 'payment_refunded',
            'PAYMENT_REFUND_REQUESTED': 'payment_refund_requested',
            'PAYMENT_REFUND_IN_PROGRESS': 'payment_refund_in_progress',
            'PAYMENT_CHARGEBACK_REQUESTED': 'payment_chargeback',
            'PAYMENT_CHARGEBACK_DISPUTE': 'payment_chargeback_dispute',
            'PAYMENT_AWAITING_CHARGEBACK_REVERSAL': 'payment_awaiting_reversal',
        }

        mapped = event_map.get(event_type, event_type)

        payment = payload.get('payment', {})

        return {
            'received': True,
            'event_type': mapped,
            'raw_event': event_type,
            'payment_id': payment.get('id'),
            'status': payment.get('status'),
            'value': payment.get('value'),
            'external_reference': payment.get('externalReference'),
            'billing_type': payment.get('billingType'),
        }

    def _generate_demo_pix_code(self, amount: float, plan_id: str) -> str:
        """Gera codigo PIX demo (formato BR Code simplificado)"""
        merchant = 'AUXFARMA'
        city = 'SAO PAULO'
        amount_str = f'{amount:.2f}'
        txid = f'AUX{uuid.uuid4().hex[:8].upper()}'

        # Padroes EMV (simplificado)
        payload = (
            '00020126'
            f'360014BR.GOV.BCB.PIX0114{merchant}@auxfarmacia.com.br'
            f'520400005303986540{len(amount_str):02d}{amount_str}'
            f'5802BR5910{merchant}6009{city}'
            f'62{len(txid)+4:02d}05{len(txid):02d}{txid}'
            '6304ABCD'
        )
        return payload


class PaymentService:
    """Facade unificando Stripe + Asaas"""

    def __init__(self):
        self.stripe = StripePaymentService()
        self.asaas = AsaasPaymentService()

    async def create_payment(
        self,
        plan_id: str,
        method: str,
        user_email: str,
        user_name: str,
        user_cpf: Optional[str] = None,
        credit_card: Optional[Dict] = None,
        success_url: str = None,
        cancel_url: str = None,
    ) -> Dict[str, Any]:
        """Cria pagamento no provedor adequado"""
        plan = PLANS.get(plan_id)
        if not plan:
            raise ValueError(f"Plano invalido: {plan_id}")

        # Normaliza os aliases vindos do schema (PaymentCreate) para os
        # metodos implementados pelos provedores.
        #   stripe_card/stripe_pix/stripe_boleto -> stripe (checkout hospedado)
        #   asaas_pix -> pix | asaas_boleto -> boleto | asaas_card -> cartao
        method = (method or '').strip().lower()
        aliases = {
            'stripe': 'stripe',
            'stripe_card': 'stripe',
            'stripe_pix': 'stripe',
            'stripe_boleto': 'stripe',
            'pix': 'pix',
            'asaas_pix': 'pix',
            'boleto': 'boleto',
            'asaas_boleto': 'boleto',
            'cartao': 'cartao',
            'card': 'cartao',
            'asaas_card': 'cartao',
        }
        method = aliases.get(method, method)

        # Escolhe o provedor disponivel: Asaas tem PIX nativo e checkout
        # hospedado para cartao; o Stripe e o plano B (tambem com PIX).
        if method == 'stripe':
            return await self.stripe.create_checkout_session(
                plan_id, user_email, success_url or '', cancel_url or ''
            )
        elif method == 'pix':
            if self.asaas.enabled:
                return await self.asaas.create_pix_payment(
                    plan_id, user_email, user_name, user_cpf
                )
            # Sem Asaas: Stripe Checkout com PIX
            return await self.stripe.create_checkout_session(
                plan_id, user_email, success_url or '', cancel_url or ''
            )
        elif method == 'boleto':
            if self.asaas.enabled:
                return await self.asaas.create_boleto_payment(
                    plan_id, user_email, user_name, user_cpf
                )
            return await self.stripe.create_checkout_session(
                plan_id, user_email, success_url or '', cancel_url or ''
            )
        elif method == 'cartao':
            # O cartao NAO trafega pelo nosso servidor (PCI-DSS).
            # Com Asaas: checkout hospedado (invoiceUrl).
            # Sem Asaas: Stripe Checkout hospedado.
            if self.asaas.enabled:
                return await self.asaas.create_credit_card_payment(
                    plan_id, user_email, user_name, credit_card, user_cpf
                )
            return await self.stripe.create_checkout_session(
                plan_id, user_email, success_url or '', cancel_url or ''
            )
        else:
            raise ValueError(f"Metodo invalido: {method}")

    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Retorna dados de um plano"""
        return PLANS.get(plan_id)

    def list_plans(self) -> Dict[str, Any]:
        """Lista todos os planos"""
        return PLANS


# Singleton
payment_service = PaymentService()