# Guia: Publicar o Frontend no Cloudflare Pages

> Tempo: ~5 minutos. Nenhum knowledge de npm/wrangler necessário.

## Por que Pages (e não Worker)

O frontend do Auxílio Farmácia é 100% estático (HTML + CSS + JS), sem build.
O Cloudflare Pages serve a pasta direto — sem `npm install`, sem `wrangler`,
sem Dockerfile. O Worker (Static Assets) exige toolchain Node e foi o que
falhou no build.

---

## Passo 1 — (opcional) Apagar o projeto Worker que falhou

Se você criou o projeto em **Workers & Pages → auxiliofarmacia** (build com
`npx wrangler deploy`), ele pode estar ocupando o nome. Apague para evitar
conflito:

1. **Workers & Pages** → clique em `auxiliofarmacia`
2. **Settings** → **Delete** → confirmar

> Não é obrigatório. Se preferir manter, use o nome `auxiliofarmacia-site`
> no passo 2 e a URL será `https://auxiliofarmacia-site.pages.dev`.

---

## Passo 2 — Criar o projeto Pages

1. No dashboard do Cloudflare: **Workers & Pages** → botão **Create application**
2. Escolha **Pages** → **Connect to Git**
3. Em **Select a repository**:
   - conta: `raphaelmenossi-maker`
   - repositório: `Auxiliofarmacia`
   - → **Next**
4. Em **Set up builds and deployments**:

| Campo | Valor |
|---|---|
| Project name | `auxiliofarmacia` |
| Production branch | `main` |
| Framework preset | **None** |
| Build command | `exit 0` |
| Build output directory | `site` |
| Root directory | *(vazio)* |
| Environment variables | *(nenhuma)* |

5. **Save and Deploy**

Aguarde ~1 minuto. O endereço aparece no topo:

```
🎉 https://auxiliofarmacia.pages.dev
```

---

## Passo 3 — Conferir

Rode na sua máquina (ou me mande a URL que eu confiro):

```bash
node scripts/verificar-deploy.js https://auxiliofarmacia.pages.dev
```

O script testa 14 páginas, confere o aviso médico, o acesso único, os
dashboards e a saude do backend.

---

## O que NÃO precisa fazer

- ❌ `npm install` — não há dependências de runtime
- ❌ `npm run build` — não há build
- ❌ `wrangler` — só para a alternativa Worker (`deploy/package.worker.json`)
- ❌ `package.json` na raiz — foi removido de propósito (o Pages tentaria
  `npm run build` e falharia)
- ❌ configuração de domínio — `*.pages.dev` já vem pronto e com HTTPS

---

## Atualizar depois

Qualquer `git push` na branch `main` redeploya sozinho.

Para publicar sem Git (upload direto pela API):

```bash
CLOUDFLARE_API_TOKEN=xxx node scripts/deploy-cloudflare.js
```

---

## Próximo passo: o backend

O Pages serve só o site. A API FastAPI fica no **Hugging Face Spaces**
(guia completo em `GUIA_HF_SPACE.md`). Depois de subir o Space, atualize
`site/config.js`:

```js
apiBase: 'https://SEU-USUARIO-SEU-SPACE.hf.space',
```

e faça o push — o Pages redeploya em segundos.

---

## Troubleshooting

| Sintoma | Causa | Solução |
|---|---|---|
| Build termina mas o site não abre | Build output directory errado | Deve ser `site` (não `/site` nem `dist`) |
| "No preset detected" | — | Não é erro; escolha **None** manualmente |
| Build falha em `npm run build` | `package.json` na raiz | Removido do repo — se reapareceu, delete no GitHub |
| 404 nas subpáginas | Build output errado | Confirme que `site/index.html` existe no repo |
| Erro 404 no `wrangler.toml` | Não se aplica ao Pages | Ele é só da alternativa Worker |
