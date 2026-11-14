"""
Auxílio Farmácia Backend - FastAPI Application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .config import settings
from .database import init_db, close_db

# ========== LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("auxfarmacia")


# ========== LIFESPAN ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown"""
    # Startup
    logger.info("🚀 Starting Auxílio Farmácia API...")
    await init_db()

    # Cria admin default se não existir
    from sqlalchemy import select
    from .models import User, UserRole
    from .database import AsyncSessionLocal
    from .utils.security import hash_password

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == settings.ADMIN_EMAILS[0])
        )
        admin = result.scalar_one_or_none()

        if not admin:
            admin = User(
                email=settings.ADMIN_EMAILS[0],
                hashed_password=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                name="Administrador",
                role=UserRole.SUPER_ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            await db.commit()
            logger.info(f"👤 Admin criado: {settings.ADMIN_EMAILS[0]} / {settings.ADMIN_DEFAULT_PASSWORD}")

    logger.info(f"✅ API ready at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"📚 Docs at http://{settings.HOST}:{settings.PORT}/docs")

    yield

    # Shutdown
    logger.info("👋 Shutting down...")
    await close_db()


# ========== APP ==========
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API do Dashboard Pediátrico de Posologia - Auxílio Farmácia",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ========== MIDDLEWARE ==========
app.add_middleware(
    CORSMiddleware,
    # Nunca combinar "*" com allow_credentials=True: o navegador enviaria
    # cookies/Authorization para qualquer origem. Se "*" estiver configurado,
    # desliga credenciais.
    allow_origins=(
        ["*"] if "*" in settings.APP_CORS_ORIGINS
        else settings.APP_CORS_ORIGINS
    ),
    allow_credentials=(
        settings.CORS_ALLOW_CREDENTIALS
        and "*" not in settings.APP_CORS_ORIGINS
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== ROUTES ==========
from .routes import auth, licenses, payments, telemetry, admin, courses, downloads, audit  # noqa

app.include_router(auth.router)
app.include_router(licenses.router)
app.include_router(payments.router)
app.include_router(telemetry.router)
app.include_router(admin.router)
app.include_router(courses.router)
app.include_router(downloads.router)
app.include_router(audit.router)


# ========== HEALTH CHECK ==========
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
    }


@app.get("/api/info")
async def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "plans": {
            "free": {"price": 0, "currency": "BRL"},
            "pro": {"price": settings.PLAN_PRICE_PRO, "currency": "BRL"},
            "premium": {"price": settings.PLAN_PRICE_PREMIUM, "currency": "BRL"},
            "institutional": {"price": settings.PLAN_PRICE_INSTITUTIONAL, "currency": "BRL"},
        },
    }


# ========== SERVE FRONTEND ==========
# Serve static files do frontend (opcional)
FRONTEND_DIR = Path(__file__).parent.parent.parent / "output"
ADMIN_DIR = Path(__file__).parent.parent / "admin"

if ADMIN_DIR.exists():
    @app.get("/admin")
    async def serve_admin():
        return FileResponse(str(ADMIN_DIR / "index.html"))

    @app.get("/admin/")
    async def serve_admin_slash():
        return FileResponse(str(ADMIN_DIR / "index.html"))

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(FRONTEND_DIR / "landing.html"))

    @app.get("/dashboard")
    async def serve_dashboard():
        return FileResponse(str(FRONTEND_DIR / "dashboard-pediatrico.html"))

    @app.get("/checkout")
    async def serve_checkout():
        return FileResponse(str(FRONTEND_DIR / "checkout.html"))


# ========== EXCEPTION HANDLERS ==========
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": str(type(exc).__name__)},
    )
