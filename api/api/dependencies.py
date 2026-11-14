"""
Dependencies para injeção nas rotas FastAPI
"""
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from .database import get_db
from .models import User, UserRole
from .utils.security import decode_token
from .config import settings


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extrai usuário atual do JWT
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    # Busca usuário
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )

    if user.is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta bloqueada por violação dos termos",
        )

    return user


async def get_current_admin(
    user: User = Depends(get_current_user)
) -> User:
    """Requer que usuário seja admin"""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Usuário opcional (retorna None se não autenticado)"""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# ========== RATE LIMITING (stub simples) ==========
_rate_limit_store: dict = {}


async def check_rate_limit(
    request: Request,
    identifier: str = None,
    limit: int = None
):
    """
    Rate limiter in-memory (em produção, usar Redis)
    """
    limit = limit or settings.RATE_LIMIT_PER_MINUTE
    identifier = identifier or request.client.host

    import time
    current_minute = int(time.time() / 60)
    key = f"{identifier}:{current_minute}"

    _rate_limit_store[key] = _rate_limit_store.get(key, 0) + 1

    if _rate_limit_store[key] > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite de {limit} requisições por minuto excedido",
        )

    # Limpa contadores de minutos antigos (evita crescimento ilimitado de memória)
    if len(_rate_limit_store) > 10_000:
        now_minute = int(time.time() / 60)
        for k in [
            k for k in _rate_limit_store
            if not k.endswith(f":{now_minute}") and not k.endswith(f":{now_minute - 1}")
        ]:
            _rate_limit_store.pop(k, None)


# ========== RATE LIMITER PRONTO PARA USO EM ROTAS ==========
async def rate_limit_auth(request: Request):
    """Rate limit para endpoints de autenticação (10/min por IP)."""
    if not settings.RATE_LIMIT_ENABLED:
        return
    await check_rate_limit(request, limit=settings.RATE_LIMIT_AUTH_PER_MINUTE)


async def rate_limit_general(request: Request):
    """Rate limit geral (60/min por IP)."""
    if not settings.RATE_LIMIT_ENABLED:
        return
    await check_rate_limit(request, limit=settings.RATE_LIMIT_PER_MINUTE)
