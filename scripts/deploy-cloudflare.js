#!/usr/bin/env node
/**
 * Deploy direto do frontend no Cloudflare Pages (API Direct Upload).
 *
 * Nao depende do build do GitHub: publica o conteudo de site/ direto.
 * Uso:
 *   CLOUDFLARE_API_TOKEN=xxx CLOUDFLARE_ACCOUNT_ID=xxx \
 *   node scripts/deploy-cloudflare.js [--dry-run]
 *
 * Token precisa das permissoes:
 *   - Cloudflare Pages: Edit
 *   - Account Settings: Read
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const TOKEN = process.env.CLOUDFLARE_API_TOKEN || '';
const ACCOUNT = process.env.CLOUDFLARE_ACCOUNT_ID || '';
const PROJECT = process.env.CLOUDFLARE_PROJECT || 'auxiliofarmacia';
const SITE = path.resolve(__dirname, '..', 'site');
const DRY = process.argv.includes('--dry-run');

if (!TOKEN) {
  console.error('\n❌ CLOUDFLARE_API_TOKEN ausente.\n');
  process.exit(2);
}

function api(pathname, opts = {}) {
  return fetch(`https://api.cloudflare.com/client/v4${pathname}`, {
    ...opts,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      ...(opts.headers || {}),
    },
  }).then(async (r) => {
    const t = await r.text();
    let j;
    try { j = JSON.parse(t); } catch { j = { raw: t }; }
    if (!r.ok) {
      const err = (j.errors || []).map((e) => `${e.code}: ${e.message}`).join('; ') || t.slice(0, 300);
      throw new Error(`${opts.method || 'GET'} ${pathname} -> ${r.status} ${err}`);
    }
    return j;
  });
}

function coletar(dir, base = '') {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const abs = path.join(dir, e.name);
    const rel = base ? `${base}/${e.name}` : e.name;
    if (e.isDirectory()) out.push(...coletar(abs, rel));
    else out.push({ path: rel, abs, size: fs.statSync(abs).size });
  }
  return out;
}

(async () => {
  console.log('\n=== DEPLOY CLOUDFLARE PAGES (direct upload) ===\n');

  // 1) account id
  let account = ACCOUNT;
  if (!account) {
    const r = await api('/accounts?per_page=5');
    if (!r.result || !r.result.length) throw new Error('Nenhuma conta encontrada com este token.');
    account = r.result[0].id;
    console.log(`  conta: ${r.result[0].name} (${account})`);
  } else {
    console.log(`  conta: ${account}`);
  }

  // 2) garante que o projeto existe
  const proj = await api(`/accounts/${account}/pages/projects/${PROJECT}`);
  if (proj.success) {
    console.log(`  projeto "${PROJECT}" ja existe`);
  } else {
    console.log(`  criando projeto "${PROJECT}"...`);
    const cr = await api(`/accounts/${account}/pages/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: PROJECT, production_branch: 'main' }),
    });
    console.log(`  projeto criado: ${cr.result?.name || 'ok'}`);
  }

  // 3) arquivos
  const files = coletar(SITE);
  const total = files.reduce((s, f) => s + f.size, 0);
  console.log(`\n  arquivos: ${files.length}  |  tamanho: ${(total / 1024 / 1024).toFixed(2)} MB`);
  if (DRY) {
    console.log('\n  --dry-run: nada foi enviado.\n');
    files.forEach((f) => console.log(`    ${f.path}  (${(f.size / 1024).toFixed(1)} KB)`));
    return;
  }

  // 4) manifest + upload
  const manifest = files.map((f) => ({
    id: crypto.createHash('sha256').update(f.path).digest('hex').slice(0, 16),
    path: f.path,
    size: f.size,
  }));

  const fd = new FormData();
  fd.append('manifest', JSON.stringify(manifest), 'manifest.json');
  for (const f of files) {
    fd.append('file', new Blob([fs.readFileSync(f.abs)]), f.path);
  }

  console.log('\n  enviando arquivos...');
  const res = await api(`/accounts/${account}/pages/projects/${PROJECT}/deployments`, {
    method: 'POST',
    headers: { 'Content-Type': 'multipart/form-data' },
    body: fd,
  });

  const id = res.result?.id;
  const url = res.result?.url;
  console.log(`\n  ✅ DEPLOY CONCLUIDO`);
  console.log(`     deployment: ${id}`);
  console.log(`     url:       ${url}`);
  console.log(`     aliases:   ${(res.result?.aliases || []).join(', ') || '(nenhum)'}`);
  console.log(`\n  Dominio padrao: https://${PROJECT}.pages.dev\n`);
})().catch((e) => {
  console.error('\n❌ ERRO:', e.message, '\n');
  process.exit(1);
});
