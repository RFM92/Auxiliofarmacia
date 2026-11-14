"""
Rotas de Pagamento - Integracao REAL Stripe + Asaas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import User, Payment
from ..dependencies import get_current_user
from ..services.payment_real import payment_service, PLANS

router = APIRouter(prefix="/api/payments", tags=["Payments"])


# ========== SCHEMAS ==========
class PaymentCreate(BaseModel):
    plan: str
    method: str  # 'stripe' | 'pix' | 'boleto' | 'cartao'
    cpf_cnpj: Optional[str] = None
    credit_card: Optional[dict] = None


class PaymentResponse(BaseModel):
    id: Optional[str] = None
    plan: str
    amount: float
    method: str
    status: str
    payment_id: Optional[str] = None
    checkout_url: Optional[str] = None
    pix_code: Optional[str] = None
    pix_qr_code: Optional[str] = None
    boleto_url: Optional[str] = None
    invoice_url: Optional[str] = None
    client_secret: Optional[str] = None
    mode: str = 'demo'
    created_at: datetime


# ========== ENDPOINTS ==========


def _frontend_base(request: Request) -> str:
    """Base do frontend para montar URLs de retorno do gateway."""
    origin = request.headers.get("origin") or request.headers.get("referer")
    if origin:
        return origin.rstrip("/")
    from ..config import settings
    return settings.APP_URL.rstrip("/")


@router.post("/create")
async def create_payment(
    request: Request,
    data: PaymentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cria pagamento real (Stripe ou Asaas)
    """
    try:
        result = await payment_service.create_payment(
            plan_id=data.plan,
            method=data.method,
            user_email=current_user.email,
            user_name=current_user.name,
            user_cpf=data.cpf_cnpj,
            credit_card=getattr(data, 'credit_card', None),
            success_url=f"{_frontend_base(request)}/success.html?plan={data.plan}",
            cancel_url=f"{_frontend_base(request)}/checkout.html?plan={data.plan}",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger_msg = str(e)
        # Salva pagamento pendente no DB
        plan_info = payment_service.get_plan(data.plan)
        amount = plan_info['prices']['brl'] if plan_info else 0

        payment = Payment(
            user_id=current_user.id,
            plan=data.plan, value=amount,
            currency='BRL',
            method=data.method,
            status='pending',
            # description removed
        )
        db.add(payment)
        await db.commit()

        return {
            'success': False,
            'error': logger_msg,
            'payment_id': str(payment.id)
        }

    # Sucesso - salva no DB
    plan_info = payment_service.get_plan(data.plan)
    amount = plan_info['prices']['brl'] if plan_info else 0

    payment = Payment(
        user_id=current_user.id,
        plan=data.plan, value=amount,
        currency='BRL',
        method=data.method,
        status='pending' if 'demo' in result.get('mode', '') else 'processing',
        gateway_id=result.get('id'),
        # description removed
    )
    db.add(payment)
    await db.commit()

    return {
        'success': True,
        'payment_id': str(payment.id),
        'external_id': result.get('id'),
        'plan': data.plan,
        'amount': amount,
        'method': data.method,
        'mode': result.get('mode', 'demo'),
        # Stripe
        'checkout_url': result.get('url'),
        'client_secret': result.get('client_secret'),
        # Asaas
        'status': result.get('status'),
        'pix_code': result.get('pix_code'),
        'pix_qr_code': result.get('pix_qr_code'),
        'boleto_url': result.get('boleto_url'),
        'invoice_url': result.get('invoice_url'),
        'due_date': result.get('due_date'),
        'value': result.get('value'),
    }


@router.get("/my", response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Historico de pagamentos do usuario"""
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .limit(50)
    )
    payments = result.scalars().all()
    return payments


@router.get("/plans")
async def list_plans():
    """Lista todos os planos disponiveis"""
    plans = []
    for plan_id, plan in PLANS.items():
        plans.append({
            'id': plan_id,
            **plan
        })
    return plans


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: str):
    """Detalhes de um plano"""
    plan = payment_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return {'id': plan_id, **plan}


# ========== WEBHOOKS ==========

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Webhook do Stripe
    Documentacao: https://stripe.com/docs/webhooks
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    # SEGURANCA: sem STRIPE_WEBHOOK_SECRET nao ha como validar a assinatura.
    # Aceitar o payload assim permitiria forjar um pagamento e ativar licenca.
    from ..config import settings
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook Stripe nao configurado (STRIPE_WEBHOOK_SECRET ausente)",
        )
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assinatura Stripe ausente (stripe-signature)",
        )

    result = await payment_service.stripe.handle_webhook(payload, sig_header)

    # Processa evento confirmado
    if result.get('event_type') == 'checkout.session.completed':
        session_id = result.get('session_id')
        if session_id:
            # Busca pagamento no DB
            payment_result = await db.execute(
                select(Payment).where(Payment.gateway_id == session_id)
            )
            payment = payment_result.scalar_one_or_none()
            if payment:
                # Idempotencia: nao reprocessar pagamento ja confirmado
                if payment.status == 'paid':
                    return {"received": True, "duplicate": True, "payment_id": session_id}
                payment.status = 'paid'
                payment.paid_at = datetime.utcnow()

                # Ativa licenca do usuario
                plan_id = result.get('metadata', {}).get('plan_id')
                if plan_id and payment.user_id:
                    from ..services.license_service import LicenseService
                    license_svc = LicenseService(db)
                    await license_svc.activate_demo_or_create(
                        user_id=payment.user_id,
                        tier='pro' if 'pro' in plan_id else plan_id,
                    )

                await db.commit()

    return result


@router.post("/webhook/asaas")
async def asaas_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Webhook do Asaas
    Documentacao: https://docs.asaas.com/docs/webhooks
    """
    from ..config import settings

    # Valida token
    auth_token = request.headers.get('asaas-access-token')
    # SEGURANCA: sem token configurado qualquer pessoa forjava um pagamento.
    if not settings.ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook Asaas nao configurado (ASAAS_WEBHOOK_TOKEN ausente)",
        )
    if auth_token != settings.ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido"
        )

    payload = await request.json()
    result = await payment_service.asaas.handle_webhook(payload)

    # Pagamento confirmado/recebido - ativa licenca
    if result.get('event_type') in ('payment_confirmed', 'payment_received'):
        payment_id = result.get('payment_id')
        external_ref = result.get('external_reference')

        if payment_id:
            payment_result = await db.execute(
                select(Payment).where(Payment.gateway_id == payment_id)
            )
            payment = payment_result.scalar_one_or_none()
            if payment:
                # Idempotencia: nao reprocessar pagamento ja confirmado
                if payment.status == 'paid':
                    return {"received": True, "duplicate": True, "payment_id": session_id}
                payment.status = 'paid'
                payment.paid_at = datetime.utcnow()

                # Ativa licenca
                if external_ref and payment.user_id:
                    from ..services.license_service import LicenseService
                    license_svc = LicenseService(db)
                    tier = 'pro' if 'pro' in external_ref else external_ref
                    await license_svc.activate_demo_or_create(
                        user_id=payment.user_id,
                        tier=tier,
                    )

                await db.commit()

    return result


@router.get("/check/{payment_id}")
async def check_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Consulta status de pagamento no provedor"""
    payment_result = await db.execute(
        select(Payment).where(
            (Payment.id == payment_id) | (Payment.gateway_id == payment_id)
        )
    )
    payment = payment_result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Pagamento nao encontrado")

    if payment.user_id != current_user.id and current_user.role.value != 'super_admin':
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Consulta no provedor se ainda pendente
    if payment.status in ('pending', 'processing') and payment.gateway_id:
        try:
            if payment.method == 'pix' or payment.method == 'boleto' or payment.method == 'cartao':
                result = await payment_service.asaas.get_payment_status(payment.gateway_id)
                if result.get('status') in ('CONFIRMED', 'RECEIVED'):
                    payment.status = 'paid'
                    payment.paid_at = datetime.utcnow()
                    await db.commit()
            elif payment.method == 'stripe':
                # Stripe e confirmado via webhook, nao via polling
                pass
        except Exception as e:
            return {
                'id': payment.gateway_id,
                'status': payment.status,
                'error': str(e)
            }

    return {
        'id': payment.gateway_id,
        'status': payment.status,
        'amount': payment.value,
        'method': payment.method,
        'paid_at': payment.paid_at,
    }