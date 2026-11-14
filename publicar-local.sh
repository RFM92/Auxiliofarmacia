#!/usr/bin/env bash
# ===================================================================
# Publica o Auxílio Farmácia no GitHub — RODE NA SUA MÁQUINA
#
#   1) Descompacte o ZIP (tem a pasta 'auxilio-farmacia' com tudo)
#   2) cd auxilio-farmacia
#   3) bash publicar-local.sh
# ===================================================================
set -euo pipefail

USUARIO="${GITHUB_USER:-raphaelmenossi-maker}"
REPO="${GITHUB_REPO:-Auxiliofarmacia}"
PASTA="$(cd "$(dirname "$0")" && pwd)"

echo "═══════════════════════════════════════════════"
echo "  Auxílio Farmácia — publicação no GitHub"
echo "═══════════════════════════════════════════════"
echo "  Usuário: $USUARIO"
echo "  Repositório: $REPO"
echo "  Pasta: $PASTA"
echo ""

cd "$PASTA"

# ---------- 1. Segurança: nenhum segredo pode ir ----------
echo "1) Verificando segredos..."
PROBLEMAS=0
if git ls-files 2>/dev/null | grep -qE '\.env$|venv/|\.db$|\.key$'; then
  echo "   ❌ Arquivos sensíveis versionados! Corrigindo..."
  git rm -r --cached .env venv *.db 2>/dev/null || true
  PROBLEMAS=1
fi
if grep -rlE 'aact_prod_[A-Za-z0-9]{10}|aact_hmlg_[A-Za-z0-9]{10}|sk_live_[A-Za-z0-9]{10}' \
     --include="*.js" --include="*.html" --include="*.md" --include="*.py" . 2>/dev/null | grep -v GUIA; then
  echo "   ❌ Chave de API encontrada nos arquivos! NÃO continue."
  exit 1
fi
echo "   ✅ Nenhum segredo encontrado"

# ---------- 2. Git ----------
echo ""
echo "2) Preparando o git..."
if [ ! -d .git ]; then
  git init -b main
fi
git config user.name "$(git config user.name 2>/dev/null || echo 'Auxilio Farmacia')"
git config user.email "$(git config user.email 2>/dev/null || echo 'dev@auxfarmacia.local')"
git add -A
if git diff --cached --quiet; then
  echo "   (tudo já commitado)"
else
  git commit -q -m "feat: Auxílio Farmácia v2026.08.1

Plataforma de apoio à posologia e dispensação farmacêutica (BR).

- 61 medicamentos, 10 classes terapêuticas, 9 calculadoras clínicas
- Tela de acesso único (login) + paywall por plano
- Checkout com API real: PIX, boleto e cartão (PCI-DSS via checkout hospedado)
- Backend FastAPI + SQLite: 38 endpoints, JWT + bcrypt, auditoria
- Acessibilidade WCAG 2.1 AA: 0 achados
- CI com auditoria automática"
  echo "   ✅ Commit feito"
fi

# ---------- 3. Remote ----------
REMOTE="https://github.com/$USUARIO/$REPO.git"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE"
else
  git remote add origin "$REMOTE"
fi
echo "   ✅ Remote: $REMOTE"

# ---------- 4. Push ----------
echo ""
echo "3) Enviando para o GitHub..."
echo "   (pode pedir login/senha ou token do GitHub)"
if git push -u origin main; then
  echo ""
  echo "═══════════════════════════════════════════════"
  echo "  ✅ PUBLICADO COM SUCESSO!"
  echo "═══════════════════════════════════════════════"
  echo ""
  echo "  Repo: https://github.com/$USUARIO/$REPO"
  echo ""
  echo "  PRÓXIMO PASSO — Cloudflare Pages (frontend):"
  echo "    1) https://dash.cloudflare.com/ → Workers & Pages → Create"
  echo "    2) Connect to Git → autorize → escolha o repositório"
  echo "    3) Build command: (vazio)"
  echo "    4) Build output directory: site"
  echo "    5) Deploy  →  https://auxilio-farmacia.pages.dev"
  echo ""
  echo "  Depois: huggingface.co/new-space (Docker) para o backend."
  echo "  Detalhes: GUIA_DEPLOY.md e GUIA_HF_SPACE.md"
else
  echo ""
  echo "⚠️  O push falhou. Se o repositório não existe ainda:"
  echo "    Crie em https://github.com/new  (nome: $REPO, sem README/.gitignore)"
  echo "    e rode este script de novo."
  exit 1
fi
