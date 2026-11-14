"""
Rotas de Telemetria
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
import logging

from ..database import get_db
from ..models import User, TelemetryEvent, EventType
from ..schemas import TelemetryBatch, TelemetryEventIn
from ..dependencies import get_optional_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])


@router.post("/track")
async def track_event(
    event: TelemetryEventIn,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Registra um evento de telemetria
    """
    try:
        # Detecta contexto
        ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        referrer = request.headers.get("referer", "")

        # Detecta device
        device_type = "desktop"
        if "Mobile" in user_agent:
            device_type = "mobile"
        elif "Tablet" in user_agent:
            device_type = "tablet"

        browser = "unknown"
        for b in ["Chrome", "Firefox", "Safari", "Edge", "Opera"]:
            if b in user_agent:
                browser = b
                break

        os_name = "unknown"
        for o in ["Windows", "Mac", "Linux", "Android", "iOS"]:
            if o in user_agent:
                os_name = o
                break

        # Valida event_type
        try:
            event_type_enum = EventType(event.event_type)
        except ValueError:
            event_type_enum = None  # custom

        # Cria evento
        evt = TelemetryEvent(
            session_id=event.session_id,
            user_id=current_user.id if current_user else None,
            event_type=event.event_type,
            data=event.data or {},
            path=event.path,
            referrer=event.referrer or referrer,
            user_agent=user_agent[:500],
            ip_address=ip,
            device_type=device_type,
            browser=browser,
            os=os_name,
            duration_ms=event.duration_ms,
            timestamp=event.timestamp or datetime.utcnow(),
        )

        db.add(evt)
        await db.commit()

        return {"success": True, "event_id": evt.id}

    except Exception as e:
        logger.error(f"Erro tracking: {e}")
        return {"success": False, "error": str(e)}


@router.post("/batch")
async def track_batch(
    batch: TelemetryBatch,
    request: Request,
    current_user: User = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Registra múltiplos eventos de uma vez
    """
    try:
        ip = request.client.host
        user_agent = request.headers.get("user-agent", "")

        for event_data in batch.events:
            evt = TelemetryEvent(
                session_id=event_data.get("session_id", "unknown"),
                user_id=current_user.id if current_user else None,
                event_type=event_data.get("event_type", "unknown"),
                data=event_data.get("data", {}),
                path=event_data.get("path"),
                user_agent=user_agent[:500],
                ip_address=ip,
            )
            db.add(evt)

        await db.commit()

        return {"success": True, "count": len(batch.events)}

    except Exception as e:
        logger.error(f"Erro batch tracking: {e}")
        return {"success": False, "error": str(e)}
