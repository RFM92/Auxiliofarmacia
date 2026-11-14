"""
Auxílio Farmácia Backend - Configuração do Banco de Dados
SQLAlchemy async com SQLite (dev) ou PostgreSQL (prod)
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# ========== ENGINE ==========
# Pool apenas para PostgreSQL (SQLite usa NullPool para evitar problemas de thread)
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# ========== SESSION FACTORY ==========
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# ========== BASE ==========
Base = declarative_base()

# ========== DEPENDENCY ==========
async def get_db() -> AsyncSession:
    """Dependency para injetar sessão do banco"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ========== INIT ==========
async def init_db():
    """Cria todas as tabelas (apenas se não existirem)"""
    from .models import user, license, payment, telemetry  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database initialized")


async def close_db():
    """Fecha conexões"""
    await engine.dispose()
    logger.info("👋 Database closed")
