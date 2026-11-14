"""
Rotas Admin
"""
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List

from ..database import get_db
from ..models import (
    User, UserRole, License, LicenseStatus, LicenseTier,
    Payment, PaymentStatus, TelemetryEvent,
)
from ..schemas import AdminStats, LicenseCreate, LicenseResponse, UserResponse
from ..dependencies import get_current_admin
from ..services.license_service import LicenseService

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStats)
async def get_dashboard_stats(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Estatísticas do dashboard admin
    """
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)

    # Total users
    total_users = await db.scalar(select(func.count(User.id)))

    # Active users
    active_24h = await db.scalar(
        select(func.count(User.id)).where(User.last_seen_at >= last_24h)
    )
    active_7d = await db.scalar(
        select(func.count(User.id)).where(User.last_seen_at >= last_7d)
    )

    # Licenses
    total_licenses = await db.scalar(select(func.count(License.id)))
    active_licenses = await db.scalar(
        select(func.count(License.id)).where(License.status == LicenseStatus.ACTIVE)
    )

    # Licenses por tier
    licenses_by_tier = {}
    for tier in LicenseTier:
        count = await db.scalar(
            select(func.count(License.id)).where(License.tier == tier)
        )
        licenses_by_tier[tier.value] = count or 0

    # Revenue
    total_revenue = await db.scalar(
        select(func.sum(Payment.value)).where(Payment.status == PaymentStatus.PAID)
    ) or 0.0

    revenue_30d = await db.scalar(
        select(func.sum(Payment.value)).where(
            and_(
                Payment.status == PaymentStatus.PAID,
                Payment.paid_at >= last_30d,
            )
        )
    ) or 0.0

    # Conversions
    conversions_7d = await db.scalar(
        select(func.count(TelemetryEvent.id)).where(
            and_(
                TelemetryEvent.event_type == "conversion",
                TelemetryEvent.timestamp >= last_7d,
            )
        )
    ) or 0

    # Churn
    total_30d_ago = await db.scalar(
        select(func.count(License.id)).where(
            and_(
                License.issued_at <= last_30d,
            )
        )
    ) or 1
    churned_30d = await db.scalar(
        select(func.count(License.id)).where(
            and_(
                License.status == LicenseStatus.EXPIRED,
                License.expires_at >= last_30d,
            )
        )
    ) or 0
    churn_rate = (churned_30d / total_30d_ago) * 100 if total_30d_ago > 0 else 0

    # Top medications (últimos 7 dias)
    result = await db.execute(
        select(
            TelemetryEvent.data,
            func.count(TelemetryEvent.id).label("count")
        ).where(
            and_(
                TelemetryEvent.event_type == "medication_view",
                TelemetryEvent.timestamp >= last_7d,
            )
        ).group_by(TelemetryEvent.data).order_by(func.count(TelemetryEvent.id).desc()).limit(10)
    )
    top_meds = []
    for row in result:
        med_id = (row.data or {}).get("med_id", "unknown")
        top_meds.append({"med_id": med_id, "count": row.count})

    # Top calculators
    result = await db.execute(
        select(
            TelemetryEvent.data,
            func.count(TelemetryEvent.id).label("count")
        ).where(
            and_(
                TelemetryEvent.event_type == "calculator_use",
                TelemetryEvent.timestamp >= last_7d,
            )
        ).group_by(TelemetryEvent.data).order_by(func.count(TelemetryEvent.id).desc()).limit(10)
    )
    top_calcs = []
    for row in result:
        calc = (row.data or {}).get("calculator", "unknown")
        top_calcs.append({"calculator": calc, "count": row.count})

    return AdminStats(
        total_users=total_users or 0,
        active_users_24h=active_24h or 0,
        active_users_7d=active_7d or 0,
        total_licenses=total_licenses or 0,
        active_licenses=active_licenses or 0,
        licenses_by_tier=licenses_by_tier,
        total_revenue=float(total_revenue),
        revenue_this_month=float(revenue_30d),
        conversions_7d=conversions_7d,
        churn_rate=round(churn_rate, 2),
        top_medications=top_meds,
        top_calculators=top_calcs,
    )


@router.get("/users")
async def list_users(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    search: Optional[str] = None,
    role: Optional[str] = None,
):
    """Lista usuários"""
    from sqlalchemy.orm import selectinload
    query = select(User)

    if search:
        query = query.where(
            or_(
                User.email.contains(search),
                User.name.contains(search),
                User.crm.contains(search),
            )
        )

    if role:
        query = query.where(User.role == role)

    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    users = result.scalars().all()

    return [UserResponse.model_validate(u) for u in users]


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza role do usuário"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    try:
        user.role = UserRole(new_role)
    except ValueError:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Role inválida",
        )

    await db.commit()
    return {"success": True, "user_id": user.id, "new_role": new_role}


@router.post("/users/{user_id}/blacklist")
async def blacklist_user(
    user_id: str,
    reason: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Coloca usuário na blacklist"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    user.is_blacklisted = True
    user.blacklist_reason = reason
    user.fraud_score = 100
    user.is_active = False

    await db.commit()
    return {"success": True, "user_id": user.id}


@router.get("/licenses")
async def list_licenses(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    status_filter: Optional[str] = None,
    tier: Optional[str] = None,
):
    """Lista licenças"""
    from sqlalchemy.orm import selectinload
    query = select(License).options(selectinload(License.user)).order_by(License.created_at.desc())

    if status_filter:
        query = query.where(License.status == status_filter)
    if tier:
        query = query.where(License.tier == tier)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    licenses = result.scalars().all()

    return [
        {
            "id": lic.id,
            "key": lic.key,
            "tier": lic.tier,
            "status": str(lic.status),
            "user_email": lic.user.email if lic.user else None,
            "user_name": lic.user.name if lic.user else None,
            "issued_at": lic.issued_at.isoformat(),
            "expires_at": lic.expires_at.isoformat(),
            "days_remaining": lic.days_remaining,
            "devices_used": lic.devices_used or 0,
            "max_devices": lic.max_devices,
            "source": lic.source,
            "campaign": lic.campaign,
        }
        for lic in licenses
    ]


@router.post("/licenses/create")
async def admin_create_license(
    data: LicenseCreate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Admin cria licença manualmente"""
    # Busca usuário por email
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Usuário com email {data.email} não encontrado",
        )

    service = LicenseService(db)
    license = await service.create_license(
        user=user,
        tier=data.tier,
        duration_days=data.duration_days,
        max_devices=data.max_devices,
        source="manual_admin",
        notes=data.notes,
        campaign=data.campaign,
    )

    # Envia email
    from ..services.email_service import EmailService
    email_service = EmailService()
    background_tasks.add_task(
        email_service.send_license_activated,
        user.name, user.email, license.key, license.tier, data.duration_days,
    )

    return {
        "key": license.key,
        "tier": license.tier,
        "status": str(license.status),
        "issued_at": license.issued_at.isoformat() if license.issued_at else None,
        "activated_at": license.activated_at.isoformat() if license.activated_at else None,
        "expires_at": license.expires_at.isoformat() if license.expires_at else None,
        "days_remaining": license.days_remaining,
        "devices_used": 0,
        "max_devices": license.max_devices,
        "features": [],
        "user_email": user.email,
        "user_name": user.name,
    }


@router.post("/licenses/{key}/revoke")
async def admin_revoke_license(
    key: str,
    reason: str = "Revogada por administrador",
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Revoga licença"""
    service = LicenseService(db)
    success = await service.revoke_license(key, reason)

    if not success:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada",
        )

    return {"success": True, "key": key}


@router.get("/payments")
async def list_payments(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    status_filter: Optional[str] = None,
):
    """Lista pagamentos"""
    from sqlalchemy.orm import selectinload
    query = select(Payment).options(selectinload(Payment.user)).order_by(Payment.created_at.desc())

    if status_filter:
        query = query.where(Payment.status == status_filter)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    payments = result.scalars().all()

    return [
        {
            "id": p.id,
            "user_email": p.user.email if p.user else None,
            "plan": p.plan,
            "value": float(p.value),
            "status": str(p.status),
            "method": p.method.value,
            "gateway": p.gateway,
            "created_at": p.created_at.isoformat(),
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
        }
        for p in payments
    ]


@router.get("/telemetry/recent")
async def recent_events(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, le=500),
):
    """Eventos recentes"""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(TelemetryEvent)
        .order_by(TelemetryEvent.timestamp.desc())
        .limit(limit)
    )
    events = result.scalars().all()

    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "session_id": e.session_id,
            "user_email": e.user.email if e.user else None,
            "path": e.path,
            "data": e.data,
            "timestamp": e.timestamp.isoformat(),
        }
        for e in events
    ]
