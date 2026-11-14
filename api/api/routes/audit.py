"""
Rotas de Auditoria
- GET /api/audit/logs - Lista logs (admin only)
- GET /api/audit/logs/{user_id} - Logs de um usuario especifico
- GET /api/audit/stats - Estatisticas
- POST /api/audit/log - Registra evento (interno)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import User, UserRole
from ..models.audit import AuditLog, AuditAction, AuditSeverity
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/audit", tags=["Audit"])


# ========== SCHEMAS ==========
class LogCreate(BaseModel):
    action: str
    resource: Optional[str] = None
    description: Optional[str] = None
    severity: str = "low"
    meta: Optional[dict] = {}


class LogResponse(BaseModel):
    id: str
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    severity: str
    resource: Optional[str]
    description: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    meta: dict
    created_at: datetime


class StatsResponse(BaseModel):
    total_logs: int
    last_24h: int
    last_7d: int
    by_severity: dict
    top_actions: List[dict]
    top_users: List[dict]


# ========== HELPERS ==========
def get_client_ip(request: Request) -> str:
    """Extrai IP real do cliente (considera proxy)"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return "unknown"


def _check_admin(user: User):
    """Verifica role admin"""
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return user


# ========== ENDPOINTS ==========

@router.post("/log", status_code=status.HTTP_201_CREATED)
async def create_log(
    data: LogCreate,
    request: Request,
    user: Optional[User] = Depends(lambda: None),  # opcional
    db: AsyncSession = Depends(get_db),
):
    """
    Registra um evento de auditoria.
    Pode ser chamado por usuarios logados ou anonimos.
    """
    try:
        action = AuditAction(data.action)
    except ValueError:
        # Cria generico se nao existir
        action = AuditAction.SECURITY_ALERT

    try:
        severity = AuditSeverity(data.severity)
    except ValueError:
        severity = AuditSeverity.LOW

    log = AuditLog(
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        action=action,
        severity=severity,
        resource=data.resource,
        description=data.description,
        meta=data.meta or {},
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent", "")[:500],
        request_method=request.method,
        request_path=str(request.url.path),
    )
    db.add(log)
    await db.commit()

    return {"success": True, "id": log.id}


@router.get("/logs", response_model=List[LogResponse])
async def list_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    severity: Optional[str] = None,
    days: int = 30,
    limit: int = 200,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista logs (apenas admin)"""
    _check_admin(current_user)

    query = select(AuditLog).where(
        AuditLog.created_at >= datetime.utcnow() - timedelta(days=days)
    )

    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        try:
            action_enum = AuditAction(action)
            query = query.where(AuditLog.action == action_enum)
        except ValueError:
            pass
    if severity:
        try:
            sev_enum = AuditSeverity(severity)
            query = query.where(AuditLog.severity == sev_enum)
        except ValueError:
            pass

    query = query.order_by(AuditLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        LogResponse(
            id=l.id,
            user_id=l.user_id,
            user_email=l.user_email or "anonimo",
            action=l.action.value,
            severity=l.severity.value,
            resource=l.resource,
            description=l.description,
            ip_address=l.ip_address,
            user_agent=l.user_agent,
            meta=l.meta or {},
            created_at=l.created_at,
        )
        for l in logs
    ]


@router.get("/logs/{user_id}", response_model=List[LogResponse])
async def user_logs(
    user_id: str,
    days: int = 90,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Logs de um usuario especifico"""
    _check_admin(current_user)

    query = select(AuditLog).where(
        and_(
            AuditLog.user_id == user_id,
            AuditLog.created_at >= datetime.utcnow() - timedelta(days=days)
        )
    ).order_by(AuditLog.created_at.desc()).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


@router.get("/stats", response_model=StatsResponse)
async def stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Estatisticas de auditoria"""
    _check_admin(current_user)

    cutoff = datetime.utcnow() - timedelta(days=days)
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)
    cutoff_7d = datetime.utcnow() - timedelta(days=7)

    # Total
    total = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= cutoff)
    )
    total_count = total.scalar() or 0

    # Ultimas 24h
    last_24h = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= cutoff_24h)
    )
    last_24h_count = last_24h.scalar() or 0

    # Ultimas 7 dias
    last_7d = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= cutoff_7d)
    )
    last_7d_count = last_7d.scalar() or 0

    # Por severidade
    by_sev = await db.execute(
        select(AuditLog.severity, func.count(AuditLog.id))
        .where(AuditLog.created_at >= cutoff)
        .group_by(AuditLog.severity)
    )
    by_severity = {s.value: c for s, c in by_sev.all()}

    # Top acoes
    top_actions_q = await db.execute(
        select(AuditLog.action, func.count(AuditLog.id).label("count"))
        .where(AuditLog.created_at >= cutoff)
        .group_by(AuditLog.action)
        .order_by(func.count(AuditLog.id).desc())
        .limit(10)
    )
    top_actions = [{"action": a.value, "count": c} for a, c in top_actions_q.all()]

    # Top usuarios
    top_users_q = await db.execute(
        select(AuditLog.user_email, func.count(AuditLog.id).label("count"))
        .where(
            and_(
                AuditLog.user_id.isnot(None),
                AuditLog.created_at >= cutoff
            )
        )
        .group_by(AuditLog.user_email)
        .order_by(func.count(AuditLog.id).desc())
        .limit(10)
    )
    top_users = [{"user": e or "anonimo", "count": c} for e, c in top_users_q.all()]

    return StatsResponse(
        total_logs=total_count,
        last_24h=last_24h_count,
        last_7d=last_7d_count,
        by_severity=by_severity,
        top_actions=top_actions,
        top_users=top_users,
    )


@router.get("/downloads/recent")
async def recent_downloads(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista os downloads recentes (admin only)"""
    _check_admin(current_user)

    query = select(AuditLog).where(
        and_(
            AuditLog.action.in_([
                AuditAction.DOWNLOAD_MANUAL,
                AuditAction.DOWNLOAD_FULL_ZIP,
                AuditAction.DOWNLOAD_PUBLIC_FILE,
            ]),
            AuditLog.created_at >= datetime.utcnow() - timedelta(days=days)
        )
    ).order_by(AuditLog.created_at.desc()).limit(50)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        {
            "id": l.id,
            "user_email": l.user_email or "anonimo",
            "action": l.action.value,
            "resource": l.resource,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat(),
            "meta": l.meta or {},
        }
        for l in logs
    ]