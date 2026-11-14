#!/usr/bin/env node
/**
 * Envia APENAS os arquivos de workflow (.github/workflows/*).
 *
 * Use depois de adicionar a permissao "Workflows: Read and write" ao token:
 *   https://github.com/settings/personal-access-tokens
 *     -> clique no seu token -> Edit -> Repository permissions
 *     -> Workflows: Read and write -> Save
 *
 *   GITHUB_TOKEN=xxx node enviar-workflows.js
 */
const fs = require('fs');
const path = require('path');

const OWNER = process.env.GITHUB_OWNER || 'RFM92';
const REPO = process.env.GITHUB_REPO || 'Auxiliofarmacia';
const BRANCH = process.env.GITHUB_BRANCH || 'main';
const API = 'https://api.github.com';
const TOKEN = process.env.GITHUB_TOKEN;
const PASTA = path.join(__dirname, '.github', 'workflows');

async function gh(method, url, body) {
  const r = await fetch(API + url, {
    method,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'auxilio-farmacia-publisher',
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const t = await r.text();
  let d = {};
  try { d = t ? JSON.parse(t) : {}; } catch (e) { d = { raw: t.slice(0, 200) }; }
  if (!r.ok) throw new Error(`${method} ${url} -> ${d.message || d.raw || 'HTTP ' + r.status}`);
  return d;
}

(async () => {
  if (!TOKEN) { console.error('GITHUB_TOKEN nao definido'); process.exit(1); }
  if (!fs.existsSync(PASTA)) { console.error('Pasta .github/workflows nao encontrada'); process.exit(1); }

  const arquivos = fs.readdirSync(PASTA).filter(f => !f.startsWith('.'));
  console.log(`📁 ${arquivos.length} arquivos em .github/workflows/`);

  let ok = 0;
  for (const f of arquivos) {
    const rel = `.github/workflows/${f}`;
    const buf = fs.readFileSync(path.join(PASTA, f));
    let sha = null;
    try {
      const d = await gh('GET', `/repos/${OWNER}/${REPO}/contents/${rel}?ref=${BRANCH}`);
      sha = d.sha || null;
    } catch (e) { /* novo arquivo */ }
    const payload = {
      message: `chore: adiciona ${rel}`,
      content: buf.toString('base64'),
      branch: BRANCH,
    };
    if (sha) payload.sha = sha;
    try {
      await gh('PUT', `/repos/${OWNER}/${REPO}/contents/${rel}`, payload);
      console.log(`  ✅ ${rel}`);
      ok++;
    } catch (e) {
      console.log(`  ❌ ${rel}: ${e.message}`);
    }
  }
  console.log(`\n${ok}/${arquivos.length} enviados.`);
  if (ok < arquivos.length) {
    console.log('\nSe ainda falhar: a permissao "Workflows: Read and write" nao esta salva no token.');
    console.log('https://github.com/settings/personal-access-tokens -> seu token -> Edit -> Workflows: Read and write -> Save');
  }
})().catch(e => { console.error('❌', e.message); process.exit(1); });
