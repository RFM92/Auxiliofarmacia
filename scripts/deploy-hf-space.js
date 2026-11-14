#!/usr/bin/env node
/**
 * Cria e publica o backend (FastAPI + SQLite) no Hugging Face Spaces via API.
 *
 *   HF_TOKEN=hf_xxx HF_USERNAME=auxiliofarmacia HF_SPACE=api \
 *   node scripts/deploy-hf-space.js
 *
 * O token precisa do role "write" e de acesso ao Space.
 *
 * O que ele faz:
 *   1. cria o Space (Docker) se ainda nao existir
 *   2. sobe a pasta api/ com os nomes exigidos pelo HF
 *      (Dockerfile.hf -> Dockerfile, requirements.hf.txt -> requirements.txt)
 *   3. grava o README com o frontmatter YAML (sdk: docker, app_port: 7860)
 *   4. imprime a URL final da API
 */
const fs = require('fs');
const path = require('path');

const TOKEN = process.env.HF_TOKEN || '';
const USERNAME = process.env.HF_USERNAME || 'auxiliofarmacia';
const SPACE = process.env.HF_SPACE || 'api';
const API_DIR = path.resolve(__dirname, '..', 'api');
const DRY = process.argv.includes('--dry-run');

if (!TOKEN) {
  console.error('\n❌ HF_TOKEN ausente (crie em https://huggingface.co/settings/tokens, role "write").\n');
  process.exit(2);
}

const HF = 'https://huggingface.co';
const REPO = `${USERNAME}/${SPACE}`;
const APP_PORT = 7860;

function hfHeaders(extra = {}) {
  return { Authorization: `Bearer ${TOKEN}`, ...extra };
}

async function hf(method, url, opts = {}) {
  const r = await fetch(HF + url, { ...opts, headers: hfHeaders(opts.headers || {}) });
  const t = await r.text();
  if (!r.ok) throw new Error(`${method} ${url} -> ${r.status} ${t.slice(0, 300)}`);
  try { return JSON.parse(t); } catch { return { raw: t }; }
}

// nomes que o HF exige (renomeia na hora do upload)
const RENOMEIA = {
  'Dockerfile.hf': 'Dockerfile',
  'requirements.hf.txt': 'requirements.txt',
};

function coletar(dir, base = '', out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === '__pycache__' || e.name === '.pytest_cache' || e.name === 'data') continue;
    const abs = path.join(dir, e.name);
    const rel = base ? `${base}/${e.name}` : e.name;
    if (e.isDirectory()) coletar(abs, rel, out);
    else out.push({ path: rel, abs });
  }
  return out;
}

(async () => {
  console.log(`\n=== DEPLOY HUGGING FACE SPACE: ${REPO} ===\n`);

  // 1) existe?
  let existe = true;
  try {
    await hf('GET', `/api/spaces/${REPO}`);
  } catch {
    existe = false;
  }

  if (!existe) {
    console.log(`  criando o Space "${REPO}"...`);
    await hf('POST', '/api/repos/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'space',
        name: SPACE,
        organization: USERNAME,
        sdk: 'docker',
        hardware: 'cpu-basic',
        private: false,
      }),
    });
    console.log('  Space criado ✅');
  } else {
    console.log('  Space já existe');
  }

  const arquivos = coletar(API_DIR);
  const mapa = arquivos.map((f) => ({
    path: RENOMEIA[f.path] || f.path,
    abs: f.abs,
  }));

  if (DRY) {
    console.log(`\n  --dry-run: ${mapa.length} arquivo(s) que seriam enviados:`);
    mapa.forEach((f) => console.log(`    ${f.path}`));
    return;
  }

  // 2) upload
  console.log(`\n  enviando ${mapa.length} arquivo(s)...`);
  const fd = new FormData();
  for (const f of mapa) {
    const buf = fs.readFileSync(f.abs);
    fd.append('path', f.path);
    fd.append('file', new Blob([buf]), path.basename(f.path));
  }
  await hf('POST', `/api/spaces/${REPO}/upload/main`, {
    method: 'POST',
    body: fd,
  });
  console.log('  upload concluído ✅');

  // 3) README com frontmatter (o HF usa isso pra decidir o SDK e a porta)
  const readme = `---
title: Auxilio Farmacia API
emoji: 🏥
colorFrom: teal
colorTo: green
sdk: docker
app_port: ${APP_PORT}
pinned: false
license: mit
short_description: API de apoio a posologia e dispensacao farmaceutica (BR)
---

# Auxílio Farmácia — API

FastAPI + SQLite. Endpoints de licenca, pagamento (PIX/boleto/cartao via
Asaas), downloads, auditoria e administracao.

- Health: \`/api/health\`
- Docs: \`/api/docs\`
`;
  await hf('PUT', `/api/spaces/${REPO}/upload/main/README.md`, {
    method: 'PUT',
    headers: { 'Content-Type': 'text/markdown' },
    body: readme,
  });
  console.log('  README escrito ✅');

  const url = `https://${USERNAME}-${SPACE}.hf.space`;
  console.log(`\n  ✅ SPACE PUBLICADO`);
  console.log(`     URL:    ${url}`);
  console.log(`     Health: ${url}/api/health`);
  console.log(`\n  Configure os secrets na aba Settings > Variables and secrets:\n`);
  console.log('     SECRET_KEY              (openssl rand -hex 32)');
  console.log('     ADMIN_DEFAULT_PASSWORD  (senha forte do admin)');
  console.log('     ASAAS_API_KEY           (do painel Asaas, modo sandbox ou producao)');
  console.log('     ASAAS_ENVIRONMENT       sandbox | production');
  console.log('     ASAAS_WEBHOOK_TOKEN     (valor aleatorio que voce inventar)');
  console.log('     APP_CORS_ORIGINS       https://auxiliofarmacia.pages.dev');
  console.log('     APP_URL                 ' + url);
  console.log(`\n  ATENCAO - disco do HF gratuito e EFEMERO:`);
  console.log(`  o SQLite e apagado quando o Space reinicia. Para persistir de verdade:`);
  console.log(`    a) assinar persistent storage (20GB = US$ 5/mes), ou`);
  console.log(`    b) hospedar em Oracle Cloud Always Free / Render com disco, ou`);
  console.log(`    c) usar o HF como demo e mover o banco quando crescer.\n`);
})().catch((e) => {
  console.error('\n❌ ERRO:', e.message, '\n');
  process.exit(1);
});
