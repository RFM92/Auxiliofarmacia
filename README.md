# 💊 Auxílio Farmácia

Plataforma de apoio à **posologia e dispensação farmacêutica** para profissionais
de saúde no Brasil — adultos e pediátricos, com bulas oficiais ANVISA,
calculadoras clínicas, material educativo e sistema de licenciamento.

> ⚠️ **Ferramenta educacional.** Não substitui bula, prescrição médica ou
> avaliação clínica individualizada. Consulte sempre um **médico ou farmacêutico
> habilitado**. O aviso está presente em todas as telas.

---

## 📊 O que tem dentro

| Módulo | Detalhe |
|---|---|
| **Catálogo** | 61 medicamentos · 10 classes terapêuticas (40 sub-classes) |
| **Calculadoras** | 9 clínicas: mg/kg/dia, mg/kg/dose, mg/m²/dia (BSA Mosteller), UI/kg/dia, volume por concentração |
| **Bulas** | Fontes oficiais ANVISA, links diretos por medicamento |
| **Educativo** | 2 cursos completos + trilha de 12 semanas (3 níveis) + quiz + certificado + gamificação (XP) |
| **Comparador** | Comparação de classes, MOA, RAM, contraindicações, gestação |
| **Paywall** | Free / Pro R$ 29,90 / Premium R$ 79,90 / Institucional R$ 297 |
| **Pagamento** | PIX (QR + copia-e-cola), boleto, cartão — checkout hospedado do gateway |
| **Admin** | Painel com 11 páginas, 25 KPIs, auditoria (25+ tipos de ação) |
| **Acessibilidade** | WCAG 2.1 AA: 0 achados, skip-link, foco visível, teclado |

---

## 🏗️ Estrutura

```
.
├── site/                    # frontend (HTML/CSS/JS estático, zero build)
│   ├── index.html           # tela de acesso único (login)
│   ├── config.js            # ÚNICO ponto de configuração da URL da API
│   ├── login.html           # login/cadastro/recuperação
│   ├── checkout.html        # checkout (PIX / boleto / cartão)
│   ├── success.html         # confirmação de pagamento
│   ├── dashboard-auxfarmacia*.html   # builds por plano
│   ├── api-client.js        # cliente HTTP (38 endpoints)
│   └── *.html               # legais, ajuda, anvisa, landing
├── api/                     # backend FastAPI + SQLite
│   ├── api/
│   │   ├── routes/          # auth, licenses, payments, admin, audit, courses, downloads, telemetry
│   │   ├── models/          # user, license, payment, audit, telemetry
│   │   ├── services/        # email, license, payment (Stripe + Asaas)
│   │   └── utils/           # fingerprint (anti-pirataria), security (JWT + bcrypt)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── scripts/                 # auditoria e reparo (24 scripts)
├── .github/workflows/       # pages.yml · ci.yml · release.yml
├── GUIA_ASAAS.md            # como ativar PIX/cartão
└── GUIA_DEPLOY.md           # onde hospedar (grátis)
```

---

## 🚀 Rodar localmente

### Frontend
```bash
cd site
python3 -m http.server 9090
# http://localhost:9090/index.html
```

### Backend
```bash
cd api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # preencha as chaves
python run.py               # http://localhost:8000/docs
```

A URL da API é resolvida por `site/config.js`:
```js
window.AUXF_CONFIG = {
  apiBase: '',   // vazio = mesma origem (produção com proxy)
  // apiBase: 'http://localhost:8000'  (desenvolvimento)
};
```

---

## 🔐 Licenciamento

| Plano | Preço | Acesso |
|---|---|---|
| Free | R$ 0 | 70% do catálogo · calculadoras básicas |
| Pro | R$ 29,90 | 100% do catálogo · comparador · casos clínicos |
| Premium | R$ 79,90 | Pro + cursos + bulas internacionais + materiais |
| Institucional | R$ 297 | Premium + até 50 usuários + painel admin |

**Anti-pirataria:** chave `AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX` + device fingerprint
(SHA-256 de UA + tela + canvas) com limite de dispositivos por plano.

---

## 🧪 Auditoria automática (CI)

Cada push roda a auditoria completa:

```bash
python scripts/check_js_syntax.py   # sintaxe JS de todos os <script>
python scripts/audit_ux.py           # acessibilidade WCAG 2.1 AA
```

Status atual: **0 achados** de acessibilidade, **47/47** arquivos JS válidos,
**0** links internos quebrados.

---

## 📄 Licença

MIT — ver [LICENSE](LICENSE).

**Aviso médico:** ferramenta educacional. Não substitui bula, prescrição ou
avaliação médica individualizada.
