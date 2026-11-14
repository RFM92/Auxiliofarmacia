---
title: Auxilio Farmacia API
emoji: 💊
colorFrom: teal
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# Auxílio Farmácia — API

Backend FastAPI do Auxílio Farmácia (posologia e dispensação farmacêutica, BR).

- 38 endpoints REST
- JWT (HS256) + bcrypt
- Licenciamento com chave `AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX` + device fingerprint
- Pagamentos: PIX, boleto e cartão (Asaas / Stripe) via checkout hospedado
- Auditoria: 25+ tipos de ação, 4 severidades
- SQLite persistente (em `/app/data`)

**Variáveis de ambiente obrigatórias** (Settings → Variables and secrets):

| Nome | Exemplo |
|---|---|
| `SECRET_KEY` | uma string forte e aleatória (mín. 32 chars) |
| `ADMIN_DEFAULT_PASSWORD` | senha do admin (troque!) |
| `ASAAS_API_KEY` | `$aact_prod_…` (ou `$aact_hmlg_…` no sandbox) |
| `ASAAS_ENVIRONMENT` | `production` ou `sandbox` |
| `ASAAS_WEBHOOK_TOKEN` | mesmo valor configurado no webhook do Asaas |
| `STRIPE_SECRET_KEY` | opcional (fallback do Stripe) |
| `APP_CORS_ORIGINS` | `["https://SEU-SITE.pages.dev"]` |

⚠️ **Ferramenta educacional.** Não substitui bula, prescrição ou avaliação
médica individualizada. Consulte sempre um médico ou farmacêutico habilitado.
