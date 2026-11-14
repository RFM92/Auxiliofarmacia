"""
Script para rodar o servidor
Uso: python run.py [dev|prod]
"""
import sys
import uvicorn
from pathlib import Path

# Adiciona o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from api.config import settings


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"

    if mode == "prod":
        # Produção: sem reload, múltiplos workers
        uvicorn.run(
            "api.main:app",
            host=settings.HOST,
            port=settings.PORT,
            workers=settings.WORKERS,
            log_level="info",
            access_log=True,
        )
    else:
        # Dev: com reload
        uvicorn.run(
            "api.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            log_level="debug",
        )


if __name__ == "__main__":
    main()
