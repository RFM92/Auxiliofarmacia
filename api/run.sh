#!/bin/sh
# Sobe a API do Auxilio Farmacia na porta do Space
set -e
PORT="${PORT:-7860}"
echo "Iniciando Auxilio Farmacia API na porta $PORT"
exec uvicorn api.main:app --host 0.0.0.0 --port "$PORT"
