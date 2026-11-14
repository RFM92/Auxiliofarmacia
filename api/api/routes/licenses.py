"""
Rotas de Licenciamento
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import User, License, LicenseTier
from ..schemas import (
    LicenseActivate, LicenseValidate,
    LicenseResponse, LicenseCreate,
)
from ..dependencies import get_current_user, get_current_admin, rate_limit_auth
from ..services.license_service import LicenseService
from ..services.email_service import EmailService

router = APIRouter(prefix="/api/licenses", tags=["Licenses"])


@router.post("/activate")
async def activate_license(
    data: LicenseActivate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _rl: None = Depends(rate_limit_auth)):
    """
    Ativa uma chave de licença no dispositivo do usuário
    """
    service = LicenseService(db)
    result = await service.activate_license(
        key=data.key,
        fingerprint=data.fingerprint,
        device_name=data.device_name,
        fingerprint_data=data.fingerprint_data,
    )

    if not result["success"]:
        reason = result.get("reason", "unknown")
        error_messages = {
            "invalid_format": "Formato de chave inválido",
            "not_found": "Chave não encontrada",
            "revoked": "Esta chave foi revogada",
            "suspended": "Esta chave está suspensa",
            "expired": "Esta chave expirou",
            "device_limit_reached": "Limite de dispositivos atingido. Desative um dispositivo primeiro.",
        }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_messages.get(reason, "Erro ao ativar licença"),
        )

    # Envia email de ativação
    if not result.get("demo") and result.get("license"):
        email_service = EmailService()
        license_info = result["license"]
        background_tasks.add_task(
            email_service.send_license_activated,
            current_user.name,
            current_user.email,
            license_info["key"],
            license_info["tier"],
            max(1, (datetime_diff_days(license_info.get("expires_at")))),
        )

    return result


@router.post("/validate")
async def validate_license(
    data: LicenseValidate,
    db: AsyncSession = Depends(get_db),
    _rl: None = Depends(rate_limit_auth)):
    """
    Valida uma chave (não requer auth)
    """
    service = LicenseService(db)
    return await service.validate_license(
        key=data.key,
        fingerprint=data.fingerprint,
    )


@router.post("/deactivate")
async def deactivate_license(
    key: str,
    fingerprint: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Desativa licença (remove dispositivo)"""
    service = LicenseService(db)

    # Verifica propriedade
    license = await service.get_license_by_key(key)
    if not license or license.user_id != current_user.id:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão",
            )

    return await service.deactivate_license(key, fingerprint)


@router.get("/my", response_model=List[LicenseResponse])
async def get_my_licenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna licenças do usuário logado"""
    service = LicenseService(db)
    licenses = await service.get_user_licenses(current_user)

    return [
        LicenseResponse(
            key=lic.key,
            tier=lic.tier,
            status=str(lic.status),
            issued_at=lic.issued_at,
            activated_at=lic.activated_at,
            expires_at=lic.expires_at,
            days_remaining=lic.days_remaining,
            devices_used=lic.devices_used or 0,
            max_devices=lic.max_devices,
            features=[],
            user_email=current_user.email,
            user_name=current_user.name,
        )
        for lic in licenses
    ]


@router.get("/demo-keys")
async def get_demo_keys(admin: User = Depends(get_current_admin)):
    """
    Retorna chaves demo.

    SEGURANCA: exige autenticacao de admin. Antes era publico e permitia
    obter chaves Premium/Institutional gratuitamente.
    """
    from ..config import settings

    if not settings.DEMO_KEYS_PUBLIC and not admin.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )

    return {
        "demo_keys": [
            {
                "key": "AUXFARMA-DEMO1-DEMO2-DEMO3-DEMO4",
                "tier": "pro",
                "description": "Pro - Recursos completos para pediatras",
            },
            {
                "key": "AUXFARMA-DEMO5-DEMO6-DEMO7-DEMO8",
                "tier": "premium",
                "description": "Premium - Inclui bulas FDA/EMA",
            },
            {
                "key": "AUXFARMA-INST1-INST2-INST3-INST4",
                "tier": "institutional",
                "description": "Institucional - Multi-usuário",
            },
        ]
    }


def datetime_diff_days(iso_str: str) -> int:
    """Helper para calcular dias restantes"""
    if not iso_str:
        return 30
    from datetime import datetime
    try:
        expires = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = expires - datetime.utcnow().replace(tzinfo=expires.tzinfo)
        return max(1, delta.days)
    except Exception:
        return 30
