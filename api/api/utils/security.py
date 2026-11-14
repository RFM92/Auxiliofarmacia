"""
Utilitários de Segurança
- Hashing de senhas
- JWT
- License key generation
"""
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import secrets
import string
import re

from ..config import settings


# ========== PASSWORD HASHING ==========
# Usa bcrypt diretamente para evitar incompatibilidade de versão com passlib
import bcrypt


def _truncate_password(password: str) -> bytes:
    """Bcrypt só aceita até 72 bytes - truncar preventivamente"""
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    """Gera hash bcrypt de uma senha"""
    pwd_bytes = _truncate_password(password)
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica se senha corresponde ao hash"""
    try:
        pwd_bytes = _truncate_password(plain)
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
    except Exception:
        return False


# ========== JWT ==========
def create_access_token(
    subject: str,
    extra_data: dict = None,
    expires_minutes: int = None
) -> str:
    """Cria JWT token"""
    expires_minutes = expires_minutes or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    if extra_data:
        payload.update(extra_data)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Cria refresh token (longa duração)"""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decodifica e valida JWT"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


# ========== LICENSE KEY GENERATION ==========
def generate_license_key() -> str:
    """
    Gera uma chave de licença no formato:
    AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX
    Onde cada X é um caractere alfanumérico
    """
    chars = string.ascii_uppercase + string.digits
    def random_block() -> str:
        return ''.join(secrets.choice(chars) for _ in range(5))
    return f"AUXFARMA-{random_block()}-{random_block()}-{random_block()}-{random_block()}"


def validate_license_key_format(key: str) -> bool:
    """Valida formato da chave"""
    pattern = r"^AUXFARMA-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$"
    return bool(re.match(pattern, key.upper().strip()))


def mask_license_key(key: str) -> str:
    """Mascara chave para display: AUXFARMA-XXXXX-...-A4F2"""
    parts = key.split("-")
    if len(parts) == 5:
        return f"{parts[0]}-{parts[1]}-****-****-{parts[4]}"
    return key


# ========== RANDOM UTILS ==========
def generate_idempotency_key() -> str:
    """Gera chave de idempotência"""
    return ''.join(secrets.token_hex(16))


def generate_secure_token(length: int = 32) -> str:
    """Token seguro para URLs (verificação de email, etc)"""
    return secrets.token_urlsafe(length)
