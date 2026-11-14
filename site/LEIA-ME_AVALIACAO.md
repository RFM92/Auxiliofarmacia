# Auxílio Farmácia — Código-Fonte Completo para Avaliação

Plataforma de apoio à prescrição e dispensação farmacêutica (Brasil).
Todos os arquivos de produção estão incluídos, organizados por função.

---

## 📁 Estrutura

```
avaliacao/
├── 01-frontend-principal/      Entrada do usuário, login, checkout, admin, landing
│   ├── index.html               Tela inicial (portal de navegação + auth bar)
│   ├── login.html               Login/cadastro standalone (funcional)
│   ├── landing.html             Página de apresentação comercial
│   ├── checkout.html            Assinatura (Stripe + Asaas)
│   ├── admin.html               Painel administrativo (11 páginas, 25 KPIs)
│   ├── ABRA-AQUI.html           Menu de acesso
│   └── api-client.js            Cliente HTTP (38 endpoints do backend)
│
├── 02-dashboards-builds/        Builds por plano de licenciamento
│   ├── dashboard-auxfarmacia.html              Master (todas as features)
│   ├── dashboard-auxfarmacia-FREE.html         Build Free
│   ├── dashboard-auxfarmacia-PRO.html          Build Pro
│   ├── dashboard-auxfarmacia-PREMIUM.html      Build Premium
│   ├── dashboard-auxfarmacia-ENTERPRISE.html   Build Institutional
│   └── dashboard-auxfarmacia-educativo.html    Build educativo
│
├── 03-legais-suporte/          Conformidade e transparência
│   ├── termos.html              Termos de uso
│   ├── privacidade.html         Política de privacidade (LGPD)
│   ├── sobre.html               Sobre a plataforma
│   ├── contato.html             Contato
│   ├── ajuda.html               Central de ajuda / FAQ
│   ├── anvisa.html              Bulas e法规 ANVISA (interna, não redireciona)
│   └── VISUALIZAR.html          Visualizador de bulas
│
├── 04-backend-api/              FastAPI + SQLite
│   ├── api/
│   │   ├── main.py              App, middlewares, CORS, static mount
│   │   ├── config.py            Configuração e variáveis de ambiente
│   │   ├── database.py          Setup SQLite, migrations
│   │   ├── dependencies.py      Dependências de auth (JWT, roles)
│   │   ├── schemas.py           Schemas Pydantic
│   │   ├── models/              user, license, payment, audit, telemetry
│   │   ├── routes/              auth, licenses, payments, admin, audit,
│   │   │                        courses, downloads, telemetry
│   │   ├── services/            email, license, payment (Stripe+Asaas)
│   │   └── utils/               fingerprint (device ID), security (bcrypt/JWT)
│   ├── tests/test_api.py        Testes automatizados
│   ├── run.py                   Entry point
│   ├── requirements.txt
│   ├── Dockerfile / docker-compose.yml
│   └── .env.example             Variáveis de ambiente (modelo)
│
├── 05-dados-conteudo/           Conteúdo clínico
│   ├── meds_array.js            Catálogo: 61 medicamentos (posologia, bulas)
│   ├── classes_array.js         50 classes terapêuticas
│   └── RESUMO_CATALOGO.json
│
├── 06-scripts-dev/              Scripts de build e manutenção (45 .py)
│   └── keepalive.sh             Watchdog de servidor/tunnel
│
├── 07-documentacao/             Documentos
│   ├── README.md
│   ├── RELATORIO_AUDITORIA.md
│   ├── Auxilio_Farmacia-Apresentacao_Comercial.pdf
│   └── Auxilio_Farmacia-Manual_do_Administrador.pdf
│
└── 08-debug-testes/             Páginas de diagnóstico (27 arquivos)
    ├── debug-*.html              Diagnósticos de UI, tabs, meds, redirect
    ├── test-*.html               Testes de auth, login, meds, e2e
    ├── diag-*.html               Diagnóstico de medicamentos e posologia
    ├── check*.html               Verificações rápidas
    ├── force-meds.html           Força renderização do catálogo
    ├── show-meds.html            Exibe catálogo renderizado
    └── dashboard-FREE.html       Dashboards de teste
```

### Backend — subpastas

```
04-backend-api/
├── api/
│   ├── models/       user, license, payment, audit, telemetry
│   ├── routes/       auth, licenses, payments, admin, audit,
│   │                 courses, downloads, telemetry
│   ├── services/     email, license, payment (Stripe + Asaas)
│   └── utils/        fingerprint, security
├── emails/           6 templates HTML (welcome, verify, reset_password,
│                     license_activated, license_expiring, payment_receipt)
├── deploy/           nginx.conf (reverse proxy de produção)
├── admin/            index.html (painel admin servido pelo backend)
└── tests/            test_api.py
```

---

## 🏗️ Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | HTML5 + CSS3 + JavaScript vanilla (zero dependências, zero build) |
| Backend | Python 3 + FastAPI + SQLite (SQLAlchemy) |
| Auth | JWT (HS256) + bcrypt |
| Pagamento | Stripe + Asaas (PIX, Boleto, Cartão) |
| Email | SMTP / SendGrid |
| Licenciamento | Chave `AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX` + device fingerprint SHA-256 |

---

## ▶️ Como Rodar

### Frontend (estático)
```bash
cd 01-frontend-principal
python3 -m http.server 9090
# abre http://localhost:9090/index.html
```

### Backend
```bash
cd 04-backend-api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # preencha as chaves
python run.py              # http://localhost:8000/docs
```

### Credenciais de teste
| Perfil | Email | Senha | Destino |
|--------|-------|-------|---------|
| Admin | `admin@auxfarmacia.com.br` | `admin123` | `admin.html` |
| Usuário | qualquer e-mail | ≥6 chars | registro local |

---

## ⚠️ Aviso Médico (obrigatório em todo o produto)

> As informações herein não constituem recomendação de uso.
> Consulte sempre um médico ou farmacêutico habilitado antes de prescrever.

Este aviso aparece **sempre visível** em todos os dashboards, builds e páginas
de cálculo. Não é removível por configuração.

---

## 🔒 Controles de Licensing

| Plano | Preço | Acesso |
|-------|-------|--------|
| Free | Grátis | 70% do catálogo |
| Pro | R$ 29,90 | 100% + calculadoras + comparador |
| Premium | R$ 79,90 | Pro + cursos + downloads + auditoria |
| Institutional | R$ 297 | Premium + multi-usuário + API |

**Regras de visibilidade (não de ocultação):**
- Antibióticos e controlados: **visíveis mas bloqueados** no Free/Premium
  (nunca escondidos — o usuário precisa saber que existe)
- Itens bloqueados exibem o motivo e o CTA de upgrade
- Anti-pirataria: device fingerprint (SHA-256 de UA + screen + canvas)
  limita ativações por licença

---

## 📊 Escala do produto

- 61 medicamentos com posologia, bulas e alertas
- 50 classes terapêuticas
- 9 calculadoras clínicas (mg/kg/dia, mg/kg/dose, mg/m²/BSA Mosteller,
  UI/kg/dia, volume por concentração, + comparadores)
- 12 abas com deep-linking por hash
- 2 cursos completos + trilha de 12 semanas / 3 níveis
- 38 endpoints REST
- 25+ tipos de ação de auditoria em 4 severidades
- Sistema de downloads restrito + trilha de auditoria
- 11 páginas de admin com 25 KPIs

---

## 🧪 Verificação

Todos os 46 HTML foram auditados:
- `<style>` balanceado (sem CSS renderizado como texto)
- `<script>` balanceado
- Todos os links internos resolvem
- 0 erros estruturais

---

*Gerado em 29/10/2026 — versão 2026.08*
