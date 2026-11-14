"""
Auxílio Farmácia Backend - Configurações
Carregado via variáveis de ambiente (.env)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List, Optional


class Settings(BaseSettings):
    """Configurações centralizadas"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ========== APP ==========
    APP_NAME: str = "Auxílio Farmácia API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | staging | production
    APP_DEBUG: bool = True
    APP_URL: str = "http://localhost:8000"
    # Em producao: liste explicitamente os dominios permitidos.
    # "*" com allow_credentials=True e inseguro (qualquer origem le credenciais).
    APP_CORS_ORIGINS: List[str] = [
        "http://localhost:9090",
        "http://localhost:8000",
        "http://127.0.0.1:9090",
    ]

    # ========== SERVER ==========
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True

    # ========== ARQUIVOS PARA DOWNLOAD ==========
    # Caminho onde ficam os PDFs/ZIPs servidos pelos endpoints de download.
    # No HF Space: /app/output (montado pelo Dockerfile).
    OUTPUT_DIR: str = "/workspace/output"
    # Diretorio do banco SQLite (persistent storage no HF: /app/data)
    DATA_DIR: str = "./data"

    # ========== DATABASE ==========
    # SQLite (dev) ou PostgreSQL (prod)
    DATABASE_URL: str = "sqlite+aiosqlite:///./auxfarmacia.db"
    # Para PostgreSQL: postgresql+asyncpg://user:pass@localhost:5432/auxfarmacia
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False  # SQL logging

    # ========== SECURITY ==========
    SECRET_KEY: str = "change-me-in-production-use-a-strong-random-key-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    BCRYPT_ROUNDS: int = 12

    # CORS
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_ORIGINS: List[str] = [
        "http://localhost:9090",
        "http://localhost:8000",
        "http://127.0.0.1:9090",
    ]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    # Quando True, endpoints sensiveis exigem rate limiting (default True)
    RATE_LIMIT_ENABLED: bool = True
    # Expor chaves demo sem autenticacao (apenas dev)
    DEMO_KEYS_PUBLIC: bool = False

    # ========== LICENSE ==========
    LICENSE_KEY_LENGTH: int = 20
    LICENSE_FINGERPRINT_REQUIRED: bool = True
    LICENSE_OFFLINE_CACHE_DAYS: int = 7
    LICENSE_DEMO_KEYS: List[str] = [
        "AUXFARMA-DEMO1-DEMO2-DEMO3-DEMO4",  # Pro
        "AUXFARMA-DEMO5-DEMO6-DEMO7-DEMO8",  # Premium
        "AUXFARMA-INST1-INST2-INST3-INST4",  # Institutional
    ]

    # Planos
    PLAN_PRICE_PRO: float = 29.90
    PLAN_PRICE_PREMIUM: float = 79.90
    PLAN_PRICE_INSTITUTIONAL: float = 297.00

    # ========== STRIPE ==========
    STRIPE_API_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_PRO: str = "price_xxx_pro"
    STRIPE_PRICE_ID_PREMIUM: str = "price_xxx_premium"
    STRIPE_PRICE_ID_INSTITUTIONAL: str = "price_xxx_institutional"

    # ========== ASAAS (BRASIL) ==========
    ASAAS_API_KEY: str = ""
    ASAAS_ENVIRONMENT: str = "sandbox"  # sandbox | production
    ASAAS_WEBHOOK_TOKEN: str = ""

    # ========== EMAIL ==========
    EMAIL_FROM: str = "noreply@auxfarmacia.com.br"
    EMAIL_FROM_NAME: str = "Auxílio Farmácia"
    EMAIL_REPLY_TO: str = "suporte@auxfarmacia.com.br"

    # SMTP (ou SendGrid, Mailgun, etc)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True

    # SendGrid (alternativa)
    SENDGRID_API_KEY: str = ""

    # ========== ADMIN ==========
    ADMIN_EMAILS: List[str] = ["admin@auxfarmacia.com.br"]
    ADMIN_DEFAULT_PASSWORD: str = "admin123"  # Trocar em prod!

    # ========== REDIS ==========
    REDIS_URL: str = "redis://localhost:6379/0"

    # ========== MONITORING ==========
    SENTRY_DSN: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações"""
    return Settings()


# Configuração global
settings = get_settings()
