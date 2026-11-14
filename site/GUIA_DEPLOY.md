# 🚀 Guia de Deploy — Onde hospedar de graça

## TL;DR

| Parte | Onde | Custo | Por quê |
|---|---|---|---|
| **Frontend** | Cloudflare Pages / Netlify / Vercel | Grátis | Estático, CDN global, URL fixa |
| **Backend (API)** | Hugging Face Spaces / Render / Fly.io / Oracle Cloud | Grátis (com limites) | Precisa de Python + SQLite persistente |
| **Código** | GitHub | Grátis | Repositório + Releases (ZIPs) + Actions (CI/CD) |
| **Gateway PIX/cartão** | Asaas | Sem mensalidade (taxa por transação) | PIX nativo BR |

---

## ⚠️ Sobre usar GitHub Pages para este projeto

O GitHub Pages **é gratuito**, mas a documentação oficial diz:

> *"GitHub Pages is not intended for or allowed to be used as a free web-hosting
> service to run your online business, e-commerce site, or any other website
> that is primarily directed at either facilitating commercial transactions or
> providing commercial software as a service (SaaS)."*

Como o Auxílio Farmácia tem **checkout com assinatura (transações
comerciais)**, usar GitHub Pages para o site comercial **viola os Termos de
Serviço do GitHub** e pode resultar em suspensão da conta.

**Alternativas que são 100% gratuitas e permitidas:**

| Opção | Frontend | Backend | Observação |
|---|---|---|---|
| **Cloudflare Pages + HF Spaces** ⭐ | Pages | Spaces (Docker) | Recomendado. URL fixa, grátis, sem límite de banda |
| **Netlify + Render** | Netlify | Render (free tier, hiberna) | Render hiberna após 15 min sem uso |
| **Vercel + Fly.io** | Vercel | Fly.io (free tier) | Fly tem limite de horas/mês |
| **Oracle Cloud Always Free** | Pages | 2 VMs permanentes | Melhor para produção real |
| **GitHub Pages** ⚠️ | Pages | — | **Não recomendado** (uso comercial) |

---

## 1️⃣ Publicar o código no GitHub

```bash
# estrutura do repo
cd /caminho/auxilio-farmacia

git init -b main
git add .
git commit -m "feat: Auxílio Farmácia v2026.08.1 — 61 medicamentos, paywall por plano, PIX/cartão"

git remote add origin https://github.com/SEU_USUARIO/auxilio-farmacia.git
git push -u origin main
```

O `.gitignore` já garante que **`.env`, `venv/`, `*.db` e `*.zip` nunca sejam
versionados**. Confira:

```bash
git ls-files | grep -E "\.env$|venv/|\.db$"   # deve retornar vazio
```

### Releases (os ZIPs para download)
```bash
git tag -a v2026.08.1 -m "v2026.08.1"
git push origin v2026.08.1
```
O workflow `release.yml` roda, monta o ZIP e publica na aba **Releases**.
Os arquivos ficam disponíveis em `github.com/SEU_USUARIO/auxilio-farmacia/releases`.

---

## 2️⃣ Frontend — Cloudflare Pages (grátis, URL fixa)

1. Dashboard Cloudflare → **Workers & Pages** → **Create** → **Pages**
2. Conecte o repositório GitHub
3. Configurações de build:
   - **Build command:** `echo "build estatico"`
   - **Build output directory:** `site`
4. Deploy

Pronto: `https://auxilio-farmacia.pages.dev`

**Aponte o frontend para a API:** edite `site/config.js` no repositório:
```js
window.AUXF_CONFIG = {
  apiBase: 'https://SEU-USUARIO-auxilio-farmacia.hf.space',
};
```

### Alternativas
- **Netlify:** arraste a pasta `site/` em app.netlify.com/drop → URL na hora
- **Vercel:** `npx vercel --cwd site`

---

## 3️⃣ Backend — Hugging Face Spaces (grátis, persistente)

O backend é um servidor FastAPI com SQLite — precisa de um processo sempre
ligado, então Pages não serve.

**Por que Spaces:** Docker + CPU básica persistente, **sem suspensão**, perfeito
para API com SQLite.

### Passo a passo

1. Crie uma conta em https://huggingface.co
2. **New Space** → **Docker** → nome `auxilio-farmacia-api`
3. Crie these files no Space:

**`Dockerfile`**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "uvicorn run:app --host 0.0.0.0 --port ${PORT:-7860}"]
```

**`requirements.txt`** (o mesmo do repo)
**`run.py`** — sobe a app do FastAPI na porta do Space:
```python
import os
from api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "7860")))
```

4. Em **Settings → Variables and secrets**, adicione:
   - `SECRET_KEY` *(secret)*
   - `DATABASE_URL` = `sqlite+aiosqlite:///./data/auxfarmacia.db`
   - `ASAAS_API_KEY` *(secret)*
   - `ASAAS_WEBHOOK_TOKEN` *(secret)*
   - `STRIPE_SECRET_KEY` *(secret)*
   - `APP_URL` = `https://auxilio-farmacia.pages.dev`

5. Em **Settings → Persistent storage**, ative para o SQLite não perder dados
6. A URL do Space: `https://SEU-USUARIO-auxilio-farmacia.hf.space`

### Alternativas
- **Render:** `render.com` → New → Web Service → Root Dir `api` → Build
  `pip install -r requirements.txt` → Start `uvicorn run:app --host 0.0.0.0 --port $PORT`
  (plano free **hiberna** após 15 min)
- **Fly.io:** `fly launch` (free tier com limite de horas)

---

## 4️⃣ Conectar tudo

```js
// site/config.js
window.AUXF_CONFIG = {
  apiBase: 'https://SEU-USUARIO-auxilio-farmacia.hf.space',
};
```

Depois **CORS** no backend precisa permitir o domínio do frontend:

```bash
# no Space (Settings → Variables)
APP_CORS_ORIGINS='["https://auxilio-farmacia.pages.dev","http://localhost:9090"]'
```

---

## 5️⃣ Webhook do Asaas (para o pagamento ativar a licença)

O webhook precisa de **URL pública fixa** — agora você tem uma!

```
https://SEU-USUARIO-auxilio-farmacia.hf.space/api/payments/webhook/asaas
```

No painel Asaas → Integração → Webhooks:
- Eventos: `PAYMENT_RECEIVED`, `PAYMENT_CONFIRMED`, `PAYMENT_OVERDUE`
- Tipo: `AUTOMATIC`
- Token: o mesmo valor de `ASAAS_WEBHOOK_TOKEN`

---

## 6️⃣ Checklist de publicação

- [ ] `git push` com o código (sem `.env`, sem `venv/`, sem `*.db`)
- [ ] Frontend no Cloudflare Pages / Netlify / Vercel
- [ ] Backend no HF Spaces / Render / Fly.io
- [ ] `config.js` apontando para a URL da API
- [ ] `APP_CORS_ORIGINS` com o domínio do frontend
- [ ] Webhook do Asaas cadastrado com a URL do backend
- [ ] `SECRET_KEY` forte (não a padrão!)
- [ ] `ADMIN_DEFAULT_PASSWORD` trocada
- [ ] Testar: login → dashboard → checkout → pagar → licença ativa
- [ ] Criar a tag e gerar a Release

---

## 🔒 Checklist de segurança

```bash
# nenhum segredo versionado
git ls-files | grep -E "\.env$|\.key$|venv/"     # vazio
git log -p | grep -E "aact_prod_|aact_hmlg_|sk_live_|sk_test_[A-Za-z0-9]{10}"   # vazio
```

- `SECRET_KEY` forte e único (nunca o padrão `change-me-in-production...`)
- `ADMIN_DEFAULT_PASSWORD` trocada antes de publicar
- CORS com origens explícitas (nunca `*` com credentials)
- Webhook do Asaas com token conferido
