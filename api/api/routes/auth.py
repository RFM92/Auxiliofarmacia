"""
Rotas de Autenticação
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..database import get_db
from ..models import User
from ..schemas import (
    UserRegister, UserLogin, TokenResponse,
    UserResponse, RefreshTokenRequest, UserUpdate,
)
from ..utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_secure_token,
)
from ..dependencies import get_current_user, rate_limit_auth
from ..services.email_service import EmailService

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _rl: None = Depends(rate_limit_auth)):
    """Registra novo usuário"""
    # Verifica se email já existe
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado",
        )

    # Cria usuário
    user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        name=user_data.name,
        crm=user_data.crm,
        specialty=user_data.specialty,
        institution=user_data.institution,
        phone=user_data.phone,
        verification_token=generate_secure_token(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Envia emails em background
    email_service = EmailService()
    background_tasks.add_task(
        email_service.send_welcome, user.name, user.email
    )
    background_tasks.add_task(
        email_service.send_verification,
        user.name, user.email, user.verification_token,
    )

    # Gera tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
    _rl: None = Depends(rate_limit_auth)):
    """Login com email e senha"""
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )

    if user.is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta bloqueada. Entre em contato com o suporte.",
        )

    # Atualiza last_login
    user.last_login_at = datetime.utcnow()
    user.last_seen_at = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Renova access token"""
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido",
        )

    new_access = create_access_token(subject=user.id)
    new_refresh = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retorna dados do usuário logado"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza perfil"""
    update_data = updates.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Verifica email via token"""
    result = await db.execute(
        select(User).where(User.verification_token == token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado",
        )

    user.is_verified = True
    user.verification_token = None
    await db.commit()

    return {"success": True, "message": "Email verificado"}


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _rl: None = Depends(rate_limit_auth)):
    """Solicita reset de senha"""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        from datetime import timedelta
        user.reset_token = generate_secure_token()
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        await db.commit()

        email_service = EmailService()
        background_tasks.add_task(
            email_service.send_password_reset,
            user.name, user.email, user.reset_token,
        )

    # Sempre retorna sucesso (privacidade)
    return {"success": True, "message": "Se o email existir, enviaremos instruções"}


@router.post("/reset-password")
async def reset_password(
    request: Request,
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    _rl: None = Depends(rate_limit_auth)):
    """Redefine senha via token"""
    from pydantic import Field

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha deve ter no mínimo 8 caracteres",
        )

    result = await db.execute(
        select(User).where(User.reset_token == token)
    )
    user = result.scalar_one_or_none()

    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado",
        )

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()

    return {"success": True, "message": "Senha redefinida"}
