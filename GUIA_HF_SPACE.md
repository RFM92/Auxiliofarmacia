# 🐧 Guia: Publicar o Backend no Hugging Face Spaces

O backend (FastAPI + SQLite) precisa de um processo **sempre ligado** — por isso
vai num Space com Docker, não no Pages.

> **Nome do site sem nome pessoal:** crie a conta do Hugging Face com o
> username **`auxiliofarmacia`** (está livre ✅) e o Space se chama **`api`**.
> A URL final fica `https://auxiliofarmacia-api.hf.space` — **sem seu nome**.
> O GitHub pode continuar no seu usuário: ele só aparece nos links de
> download, que é normal em qualquer projeto open-source.

---

## ⚠️ Antes de começar: o disco do HF grátis é EFÉMERO

| | |
|---|---|
| Disco no plano grátis | 50 GB **efêmero** — **apagado a cada reinício** do Space |
| Persistent storage | 20 GB = **US$ 5/mês** (100 GB = US$ 25/mês) |
| Sleep | o Space CPU Basic **dorme** após um período sem uso |

O Auxílio Farmácia guarda **usuários, licenças, auditoria e histórico de
pagamentos** no SQLite. Em disco efêmero, **um reinício apaga tudo** — e
com plano pago no Asaas, isso é inaceitável.

### Escolha o seu caminho

| Opção | Custo | Persistência | URL | Esforço |
|---|---|---|---|---|
| **A. HF + persistent storage** | US$ 5/mês | ✅ real | `auxiliofarmacia-api.hf.space` | baixo |
| **B. Oracle Cloud Always Free** | **grátis** | ✅ real (200 GB) | IP ou domínio próprio | médio |
| **C. Render (plano pago)** | ~US$ 7/mês | ✅ disco | `auxiliofarmacia-api.onrender.com` | baixo |
| **D. HF grátis** | grátis | ❌ efêmero | `auxiliofarmacia-api.hf.space` | baixo |

**Minha recomendação: A para começar** (5 dólares, zero configuração extra,
URL limpa e o webhook do Asaas pronto em minutos). Se o custo incomodar, **B**
é o melhor FREE de verdade — 4 CPUs ARM e 200 GB no Always Free da Oracle.

Enquanto isso (opção D), o backend serve para **testar** — nunca para
production com pagamento real.

---

## Passo 1 — Criar a conta no Hugging Face

1. Acesse https://huggingface.co/join
2. Username: **`auxiliofarmacia`** (ou `auxfarmacia`)
3. Confirme o e-mail
4. Crie um token em https://huggingface.co/settings/tokens
   - **Role: `write`**
   - Nome: `Auxilio Farmacia Deploy`

---

## Passo 2 — Publicar (automático)

Com o token em mãos, **um comando faz tudo**:

```bash
HF_TOKEN=hf_xxx HF_USERNAME=auxiliofarmacia HF_SPACE=api \
  node scripts/deploy-hf-space.js
```

Ele cria o Space, sobe a pasta `api/` (renomeando `Dockerfile.hf` →
`Dockerfile` e `requirements.hf.txt` → `requirements.txt`) e escreve o
`README.md` com o frontmatter do Docker.

**Ou manualmente:** https://huggingface.co/new-space
- Space name: `api`
- SDK: **Docker**
- Licença: MIT

Depois suba a pasta `api/` inteira pela aba **Files**.

---

## Passo 3 — Secrets

Na aba **Settings → Variables and secrets**:

| Chave | Valor |
|---|---|
| `SECRET_KEY` | `openssl rand -hex 32` |
| `ADMIN_DEFAULT_PASSWORD` | senha forte do admin |
| `ASAAS_API_KEY` | do painel Asaas (sandbox ou produção) |
| `ASAAS_ENVIRONMENT` | `sandbox` ou `production` |
| `ASAAS_WEBHOOK_TOKEN` | string aleatória que você inventar |
| `APP_CORS_ORIGINS` | `https://auxiliofarmacia.pages.dev` |
| `APP_URL` | `https://auxiliofarmacia-api.hf.space` |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/auxfarmacia.db` |

> ⚠️ `SECRET_KEY` e as chaves **nunca** entram no GitHub. Ficam só nos
> secrets do Space.

---

## Passo 4 — Conferir

```bash
curl https://auxiliofarmacia-api.hf.space/api/health
```

Resposta esperada: `{"status":"ok", ...}`

Docs interativos: `https://auxiliofarmacia-api.hf.space/api/docs`

---

## Passo 5 — Apontar o frontend

Edite `site/config.js` (única linha):

```js
apiBase: 'https://auxiliofarmacia-api.hf.space',
```

```bash
git add -A && git commit -m "chore: apiBase do backend em producao" && git push
```

O Cloudflare Pages redeploya em segundos.

---

## Passo 6 — Webhook do Asaas (precisa de URL fixa)

No painel Asaas → **Configurações → Webhooks**:

| Campo | Valor |
|---|---|
| URL | `https://auxiliofarmacia-api.hf.space/api/payments/webhook/asaas` |
| Token | o mesmo valor de `ASAAS_WEBHOOK_TOKEN` |
| Eventos | `PAYMENT_RECEIVED`, `PAYMENT_CONFIRMED`, `PAYMENT_OVERDUE`, `PAYMENT_REFUNDED` |

> A URL precisa ser **fixa e pública** — o tunnel `trycloudflare.com` morre
> a cada reinício do sandbox e o webhook deixaria de funcionar.

---

## Passo 7 — CORS

O backend precisa aceitar o domínio do frontend. Em `APP_CORS_ORIGINS`:

```
https://auxiliofarmacia.pages.dev
```

Se você criar um domínio próprio depois, acrescente com vírgula.

---

## Estrutura do Space

```
.
├── Dockerfile          (era Dockerfile.hf)
├── requirements.txt    (era requirements.hf.txt)
├── README.md           (frontmatter: sdk: docker, app_port: 7860)
├── run.sh
└── api/
    ├── main.py
    ├── config.py
    ├── database.py
    ├── routes/
    ├── services/
    ├── models/
    ├── schemas.py
    └── utils/
```

O `Dockerfile` já cria o usuário sem privilégios, monta o SQLite em
`/app/data` (é onde o persistent storage do HF é montado) e sobe o uvicorn
na porta `${PORT:-7860}`.
