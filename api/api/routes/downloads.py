"""
Rotas de Downloads RESTRITOS com AUDITORIA
- Manual do Admin: requer login de admin + log
- Apresentacao Comercial: publica + log
- Pacotes ZIP: variavel + log
"""
import os
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse

from ..dependencies import get_current_user, get_optional_user
from ..models import User, UserRole
from ..models.audit import AuditLog, AuditAction, AuditSeverity
from ..database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/downloads", tags=["Downloads"])

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/workspace/output"))


def _check_admin(user: User = Depends(get_current_user)):
    """Verifica se o usuario e admin/super_admin"""
    if user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    return user


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return "unknown"


async def _audit_download(
    request: Request,
    user: User,
    action: AuditAction,
    resource: str,
    severity: AuditSeverity,
    db: AsyncSession,
    success: bool = True,
):
    """Registra log de auditoria para downloads"""
    log = AuditLog(
        user_id=user.id if user else None,
        user_email=user.email if user else None,
        action=action,
        severity=severity,
        resource=resource,
        description=f"Download {resource} - {'sucesso' if success else 'falha'}",
        meta={
            "success": success,
            "method": request.method,
            "endpoint": str(request.url.path),
        },
        ip_address=get_client_ip(request),
        user_agent=request.headers.get("User-Agent", "")[:500],
        request_method=request.method,
        request_path=str(request.url.path),
    )
    db.add(log)
    await db.commit()


# ========== LISTAGEM ==========
@router.get("/list")
async def list_public_downloads():
    """Lista downloads publicos e restritos (metadados)"""
    return {
        "public": [
            {
                "id": "comercial",
                "name": "Auxilio_Farmacia-Apresentacao_Comercial.pdf",
                "title": "Apresentacao Comercial",
                "description": "Material de vendas para clientes",
                "size_kb": 18, "pages": 11, "type": "pdf"
            },
            {
                "id": "site-zip",
                "name": "auxfarmacia_site.zip",
                "title": "Site Completo (HTML)",
                "description": "Todos os dashboards sem PDFs",
                "size_kb": 800, "type": "zip"
            }
        ],
        "internal": [
            {
                "id": "admin-manual",
                "title": "Manual do Administrador",
                "description": "Guia interno para setup e operacao",
                "size_kb": 23, "pages": 13, "type": "pdf",
                "access": "admin_only",
                "endpoint": "/api/downloads/admin/manual"
            },
            {
                "id": "full-zip",
                "name": "auxfarmacia_completo.zip",
                "title": "Pacote Completo (com Manuais)",
                "description": "Inclui Manual do Admin",
                "size_kb": 1200, "type": "zip",
                "access": "admin_only",
                "endpoint": "/api/downloads/admin/full-zip"
            }
        ]
    }


# ========== PUBLICOS ==========
@router.get("/comercial")
async def download_comercial(
    request: Request,
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Download PUBLICO da Apresentacao Comercial - logado ou nao"""
    path = OUTPUT_DIR / "Auxilio_Farmacia-Apresentacao_Comercial.pdf"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado")

    # Log
    await _audit_download(
        request, user, AuditAction.DOWNLOAD_PUBLIC_FILE,
        "Auxilio_Farmacia-Apresentacao_Comercial.pdf",
        AuditSeverity.LOW, db
    )

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename="Auxilio_Farmacia-Apresentacao_Comercial.pdf"
    )


@router.get("/site-zip")
async def download_site_zip(
    request: Request,
    user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Download PUBLICO do ZIP do site"""
    path = OUTPUT_DIR / "auxfarmacia_site.zip"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado")

    await _audit_download(
        request, user, AuditAction.DOWNLOAD_PUBLIC_FILE,
        "auxfarmacia_site.zip",
        AuditSeverity.LOW, db
    )

    return FileResponse(
        path=str(path),
        media_type="application/zip",
        filename="auxfarmacia_site.zip"
    )


# ========== RESTRITOS (APENAS ADMIN) ==========
@router.get("/admin/manual")
async def download_admin_manual(
    request: Request,
    user: User = Depends(_check_admin),
    db: AsyncSession = Depends(get_db),
):
    """Download RESTRITO do Manual do Admin - requer login de admin + log"""
    path = OUTPUT_DIR / "Auxilio_Farmacia-Manual_do_Administrador.pdf"
    if not path.exists():
        # Log falha tambem
        await _audit_download(
            request, user, AuditAction.DOWNLOAD_MANUAL,
            "Auxilio_Farmacia-Manual_do_Administrador.pdf",
            AuditSeverity.HIGH, db, success=False
        )
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado")

    await _audit_download(
        request, user, AuditAction.DOWNLOAD_MANUAL,
        "Auxilio_Farmacia-Manual_do_Administrador.pdf",
        AuditSeverity.MEDIUM, db, success=True
    )

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename="Auxilio_Farmacia-Manual_do_Administrador.pdf",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, private"}
    )


@router.get("/admin/full-zip")
async def download_full_zip(
    request: Request,
    user: User = Depends(_check_admin),
    db: AsyncSession = Depends(get_db),
):
    """Download RESTRITO do pacote completo"""
    path = OUTPUT_DIR / "auxfarmacia_completo.zip"
    if not path.exists():
        await _audit_download(
            request, user, AuditAction.DOWNLOAD_FULL_ZIP,
            "auxfarmacia_completo.zip",
            AuditSeverity.HIGH, db, success=False
        )
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado")

    await _audit_download(
        request, user, AuditAction.DOWNLOAD_FULL_ZIP,
        "auxfarmacia_completo.zip",
        AuditSeverity.MEDIUM, db, success=True
    )

    return FileResponse(
        path=str(path),
        media_type="application/zip",
        filename="auxfarmacia_completo.zip",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, private"}
    )