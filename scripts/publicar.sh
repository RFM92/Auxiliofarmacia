#!/usr/bin/env bash
# ===================================================================
# Publica o Auxílio Farmácia no GitHub
#
#   ./scripts/publicar.sh SEU_USUARIO NomeDoRepo
#
# Exemplo:
#   ./scripts/publicar.shSeuUsuario auxilio-farmacia
# ===================================================================
set -euo pipefail

ARG="${1:-}"
DEST="${2:-/workspace/repo_github}"

# aceita:
#   SEU_USUARIO
#   SEU_USUARIO/nome-do-repo
#   https://github.com/SEU_USUARIO/nome-do-repo
REPO="auxilio-farmacia"
case "$ARG" in
  */*)  USUARIO="${ARG%%/*}"; REPO="${ARG##*/}" ;;
  "")   USUARIO="" ;;
  *)    USUARIO="$ARG" ;;
esac
# tira o prefixo github.com de uma URL colada
USUARIO="${USUARIO#github.com/}"
USUARIO="${USUARIO#https://github.com/}"

if [ -z "$USUARIO" ]; then
  echo "Uso: $0 SEU_USUARIO [nome-do-repo] [caminho]"
  echo ""
  echo "Exemplos:"
  echo "  $0 GitHubUsername"
  echo "  $0 GitHubUsername/auxilio-farmacia"
  echo "  $0 https://github.com/GitHubUsername/auxilio-farmacia"
  echo ""
  echo "Descubra seu usuario em 3 cliques:"
  echo "  1) https://github.com/settings/profile"
  echo "  2) ou: clique no seu avatar (canto superior direito) > 'Your username'"
  echo "  3) ou: a URL do seu repo ja mostra: github.com/SEU_USUARIO/REPO"
  exit 1
fi

cd "$DEST"

if [ ! -d .git ]; then
  git init -b main
fi

git config user.name "Auxilio Farmacia"
git config user.email "dev@auxfarmacia.local"

git add -A
if git diff --cached --quiet; then
  echo "Nada novo para commitar."
else
  git commit -q -m "feat: Auxilio Farmacia v2026.08.1

Plataforma de apoio a posologia e dispensacao farmaceutica (BR).

- 61 medicamentos, 10 classes terapeuticas, 9 calculadoras clinicas
- Tela de acesso unico (login) + paywall por plano
- Checkout com API real: PIX, boleto e cartao (PCI-DSS via checkout hospedado)
- Backend FastAPI + SQLite: 38 endpoints, JWT + bcrypt, auditoria
- Acessibilidade WCAG 2.1 AA: 0 achados
- CI com auditoria automatica (JS, a11y, links, sintaxe do backend)"
  echo "✅ Commit feito."
fi

REMOTE="https://github.com/$USUARIO/$REPO.git"
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$REMOTE"
else
  git remote add origin "$REMOTE"
fi

echo ""
echo "🚀 Enviando para $REMOTE"
if git push -u origin main 2>&1 | tail -5; then
  echo ""
  echo "✅ PUBLICADO!"
  echo ""
  echo "Próximos passos:"
  echo ""
  echo "1) CRIE o repositório vazio no GitHub (se ainda não existe):"
  echo "   https://github.com/new  → nome: $REPO  → sem README e sem .gitignore"
  echo ""
  echo "2) Cloudflare Pages (frontend):"
  echo "   https://dash.cloudflare.com/ → Workers & Pages → Create → Connect to Git"
  echo "   → repositório: $REPO"
  echo "   → Build command: (vazio)"
  echo "   → Build output directory: site"
  echo "   → Deploy"
  echo ""
  echo "3) Hugging Face Spaces (backend):"
  echo "   https://huggingface.co/new-space → Docker → copie a pasta api/ do repo"
  echo "   → Settings → Variables and secrets → configure as chaves"
  echo "   → Settings → Persistent storage → ATIVE"
  echo ""
  echo "4) Aponte o frontend para o backend em site/config.js:"
  echo "   apiBase: 'https://SEU_USUARIO-auxilio-farmacia.hf.space'"
  echo ""
  echo "5) Crie a release:"
  echo "   git tag -a v2026.08.1 -m 'v2026.08.1' && git push origin v2026.08.1"
else
  echo ""
  echo "⚠️  O push falhou. Crie o repositório vazio em https://github.com/new"
  echo "    (nome: $REPO, sem README e sem .gitignore) e rode este script de novo."
fi
