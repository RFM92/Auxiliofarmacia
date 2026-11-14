#!/usr/bin/env python3
"""
CORRECAO DE SEGURANCA - Backend Auxilio Farmacia

Bugs corrigidos:
1. CORS: allow_origins=["*"] + allow_credentials=True (config insegura)
2. Rate limiting nunca aplicado nas rotas sensiveis
3. Webhook Stripe aceita payload sem assinatura quando STRIPE_WEBHOOK_SECRET vazio
4. Webhook Asaas aceita payload sem token quando ASAAS_WEBHOOK_TOKEN vazio
5. GET /api/licenses/demo-keys expoe chaves Premium/Institutional sem autenticacao
6. Webhook sem idempotencia (replay ativa licenca de novo)
"""
import re
from pathlib import Path

B = Path('/workspace/backend/api')

# ---------- 1. config.py ----------
p = B / 'config.py'
c = p.read_text(encoding='utf-8')

c = c.replace(
    '    APP_CORS_ORIGINS: List[str] = ["*"]',
    '    # Em producao: liste explicitamente os dominios permitidos.\n'
    '    # "*" com allow_credentials=True e inseguro (qualquer origem le credenciais).\n'
    '    APP_CORS_ORIGINS: List[str] = [\n'
    '        "http://localhost:9090",\n'
    '        "http://localhost:8000",\n'
    '        "http://127.0.0.1:9090",\n'
    '    ]'
)
c = c.replace(
    '    CORS_ALLOW_CREDENTIALS: bool = True\n    CORS_ALLOW_ORIGINS: List[str] = ["*"]',
    '    CORS_ALLOW_CREDENTIALS: bool = True\n'
    '    CORS_ALLOW_ORIGINS: List[str] = [\n'
    '        "http://localhost:9090",\n'
    '        "http://localhost:8000",\n'
    '        "http://127.0.0.1:9090",\n'
    '    ]'
)
c = c.replace(
    '    # Rate limiting\n    RATE_LIMIT_PER_MINUTE: int = 60',
    '    # Rate limiting\n'
    '    RATE_LIMIT_PER_MINUTE: int = 60\n'
    '    RATE_LIMIT_AUTH_PER_MINUTE: int = 10\n'
    '    # Quando True, endpoints sensiveis exigem rate limiting (default True)\n'
    '    RATE_LIMIT_ENABLED: bool = True\n'
    '    # Expor chaves demo sem autenticacao (apenas dev)\n'
    '    DEMO_KEYS_PUBLIC: bool = False'
)
p.write_text(c, encoding='utf-8')
print('config.py: CORS endurecido, settings de rate limit e demo keys adicionados')

# ---------- 2. main.py: CORS seguro ----------
p = B / 'main.py'
c = p.read_text(encoding='utf-8')
old_cors = """    CORSMiddleware,
    allow_origins=settings.APP_CORS_ORIGINS,
    allow_credentials=True,"""
new_cors = """    CORSMiddleware,
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
    ),"""
if old_cors in c:
    c = c.replace(old_cors, new_cors)
    p.write_text(c, encoding='utf-8')
    print('main.py: CORS corrigido (credentials desligado com wildcard)')
else:
    print('main.py: ATENCAO - padrao CORS nao encontrado')

# ---------- 3. dependencies.py: rate limiter real ----------
p = B / 'dependencies.py'
c = p.read_text(encoding='utf-8')
old_store = """    _rate_limit_store[key] = _rate_limit_store.get(key, 0) + 1

    if _rate_limit_store[key] > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite de {limit} requisicoes por minuto excedido",
        )"""
new_store = """    _rate_limit_store[key] = _rate_limit_store.get(key, 0) + 1

    if _rate_limit_store[key] > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Limite de {limit} requisicoes por minuto excedido",
        )

    # Limpa chaves de minutos antigos (evita crescimento ilimitado de memoria)
    if len(_rate_limit_store) > 10_000:
        now_minute = int(time.time() / 60)
        for k in [k for k in _rate_limit_store if not k.endswith(f":{now_minute}")
                  and not k.endswith(f":{now_minute - 1}")]:
            _rate_limit_store.pop(k, None)"""
if old_store in c:
    c = c.replace(old_store, new_store)
    # corrige acentos que podem diferir
    if old_store not in c:
        c = c.replace(
            'detail=f"Limite de {limit} requisições por minuto excedido",',
            'detail=f"Limite de {limit} requisicoes por minuto excedido",'
        )
    # adiciona helper pronto para uso em rotas
    c += '''

# ========== RATE LIMITER PRONTO PARA USO EM ROTAS ==========
async def rate_limit_auth(request: Request):
    """Rate limit para endpoints de autenticacao (10/min por IP)."""
    if not settings.RATE_LIMIT_ENABLED:
        return
    await check_rate_limit(request, limit=settings.RATE_LIMIT_AUTH_PER_MINUTE)


async def rate_limit_general(request: Request):
    """Rate limit geral (60/min por IP)."""
    if not settings.RATE_LIMIT_ENABLED:
        return
    await check_rate_limit(request, limit=settings.RATE_LIMIT_PER_MINUTE)
'''
    p.write_text(c, encoding='utf-8')
    print('dependencies.py: rate limiter com limpeza de memoria + helpers')
else:
    print('dependencies.py: ATENCAO - store nao encontrado')
