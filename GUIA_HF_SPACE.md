# 🐧 Guia: Publicar o Backend no Hugging Face Spaces

O backend (FastAPI + SQLite) precisa de um processo **sempre ligado** — por isso
vai num Space com Docker, não no Pages.

**Custo: grátis.** CPU básica persistente, sem suspensão.

---

## Passo 1 — Criar o Space

1. Acesse https://huggingface.co/new-space
2. **Space name:** `auxilio-farmacia-api`
3. **Space SDK:** **Docker**
4. Licença: MIT
5. Clique **Create Space**

O Space abre com um `Dockerfile` e `README.md` de exemplo.

---

## Passo 2 — Subir os arquivos

O repositório já tem tudo pronto em `api/`. Dentro do Space, use a aba
**Files** e suba:

| Arquivo | Para quê |
|---|---|
| `Dockerfile.hf` | → renomeie para **`Dockerfile`** |
| `requirements.hf.txt` | → renomeie para **`requirements.txt`** |
| `README.md` | mantém o frontmatter YAML (`sdk: docker`, `app_port: 7860`) |
| `run.sh` | script de start (opcional, o Dockerfile já sobe o uvicorn) |
| `api/` | toda a pasta do backend (routes, models, services, utils) |

**Atalho:** baixe o `AuxilioFarmacia_REPO_GITHUB.zip`, extraia e use a pasta
`api/` inteira.

### Estrutura final no Space
```
.
├── Dockerfile          (era Dockerfile.hf)
├── requirements.txt    (era requirements.hf.txt)
├── README.md
└── api/
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── database.py
    ├── dependencies.py
    ├── schemas.py
    ├── models/
    ├── routes/
    ├── services/
    └── utils/
```

> ⚠️ **Atenção ao `api/`:** dentro do Space, o backend fica em `/app/api/`,
> e o comando é `uvicorn api.main:app`. O `Dockerfile.hf` já faz `COPY . .`
> a partir da raiz do Space — então a pasta `api/` precisa estar **na raiz
> do Space**, não dentro de outra pasta.

---

## Passo 3 — Variáveis e segredos

**Settings → Variables and secrets → New variable**

| Nome | Tipo | Valor |
|---|---|---|
| `SECRET_KEY` | **Secret** | string forte e aleatória (mín. 32 chars) |
| `ADMIN_DEFAULT_PASSWORD` | **Secret** | senha do admin (TROQUE!) |
| `ASAAS_API_KEY` | **Secret** | `$aact_prod_…` ou `$aact_hmlg_…` |
| `ASAAS_ENVIRONMENT` | Variable | `production` ou `sandbox` |
| `ASAAS_WEBHOOK_TOKEN` | **Secret** | o mesmo configurado no webhook do Asaas |
| `STRIPE_SECRET_KEY` | **Secret** | opcional (fallback) |
| `STRIPE_WEBHOOK_SECRET` | **Secret** | opcional (fallback) |
| `APP_CORS_ORIGINS` | Variable | `["https://auxilio-farmacia.pages.dev"]` |
| `APP_URL` | Variable | `https://auxilio-farmacia.pages.dev` |
| `APP_ENV` | Variable | `production` |

**Gerar um SECRET_KEY forte:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## Passo 4 — Persistent storage (OBRIGRATÓRIO)

**Settings → Persistent storage → Enable**

Sem isso o SQLite é apagado a cada restart e as licenses somem.

O `Dockerfile.hf` já cria `/app/data` e o `DATABASE_URL` aponta para lá:
```
DATABASE_URL=sqlite+aiosqlite:///./data/auxfarmacia.db
```

---

## Passo 5 — Build

O Space constrói sozinho (~3-5 min). Acompanhe na aba **Build**.

Quando terminar, a URL será:
```
https://SEU_USUARIO-auxilio-farmacia-api.hf.space
```

Teste:
```bash
curl https://SEU_USUARIO-auxilio-farmacia-api.hf.space/docs
```

---

## Passo 6 — Apontar o frontend para a API

No repositório GitHub, edite `site/config.js`:

```js
window.AUXF_CONFIG = {
  apiBase: 'https://SEU_USUARIO-auxilio-farmacia-api.hf.space',
};
```

Commit + push → o Cloudflare Pages faz o deploy automático (1-2 min).

---

## Passo 7 — Webhook do Asaas

Agora a URL da API é **fixa** 🎉

**Painel Asaas → Integração → Webhooks:**
- Eventos: `PAYMENT_RECEIVED`, `PAYMENT_CONFIRMED`, `PAYMENT_OVERDUE`, `PAYMENT_REFUNDED`
- Tipo: `AUTOMATIC`
- URL: `https://SEU_USUARIO-auxilio-farmacia-api.hf.space/api/payments/webhook/asaas`
- Token: o mesmo valor de `ASAAS_WEBHOOK_TOKEN`

---

## ⚠️ Limitações do Space (saiba antes)

| Limite | Impacto |
|---|---|
| CPU básica (2 vCPU) | API com poucos usuários simultâneos — ok para começar |
| 16 GB de disco | SQLite cabe folgado |
| Hiberna após 48h sem uso | pode demorar ~30s para acordar na 1ª visita |
| Sem HTTPS customizado | a URL já é HTTPS (`hf.space`) ✓ |
| Subdomínio `*.hf.space` | sem problema |

Para escalar depois: Render (plano pago) ou Oracle Cloud Always Free (2 VMs).

---

## Checklist

- [ ] Space criado com SDK Docker
- [ ] `Dockerfile` (do `Dockerfile.hf`) na raiz
- [ ] `requirements.txt` (do `requirements.hf.txt`) na raiz
- [ ] pasta `api/` na raiz do Space
- [ ] `SECRET_KEY` forte e único
- [ ] `ADMIN_DEFAULT_PASSWORD` trocada
- [ ] Persistent storage **ativado**
- [ ] Build concluído sem erro
- [ ] `/docs` responde 200
- [ ] `config.js` apontando para a URL do Space
- [ ] `APP_CORS_ORIGINS` com o domínio do frontend
- [ ] Webhook do Asaas cadastrado
