#!/usr/bin/env node
/**
 * Publica o frontend estatico no Cloudflare Pages (Direct Upload).
 *
 *   CLOUDFLARE_API_TOKEN=xxx node scripts/deploy-cloudflare.js [projeto]
 *
 * Usa o wrangler por baixo dos panos (o upload direto via API crua exige um
 * formato de manifest que so o wrangler monta direito).
 *
 * O token precisa de:
 *   - Account > Workers Scripts > Edit
 *   - Account > Account Settings > Read
 *   - Account > Pages > Edit
 */
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const TOKEN = process.env.CLOUDFLARE_API_TOKEN || '';
const ACCOUNT = process.env.CLOUDFLARE_ACCOUNT_ID || '';
const SITE = path.resolve(__dirname, '..', 'site');
const PROJECT = process.argv[2] || process.env.CLOUDFLARE_PROJECT || 'auxilio-farmacia';

if (!TOKEN) {
  console.error('\n❌ CLOUDFLARE_API_TOKEN ausente.\n');
  process.exit(2);
}

function api(method, pathname) {
  const r = spawnSync('curl', [
    '-s', '--max-time', '30',
    '-X', method,
    '-H', `Authorization: Bearer ${TOKEN}`,
    `https://api.cloudflare.com/client/v4${pathname}`,
  ], { encoding: 'utf8' });
  try { return JSON.parse(r.stdout); } catch { return { success: false, raw: r.stdout }; }
}

(async () => {
  console.log(`\n=== DEPLOY CLOUDFLARE PAGES: ${PROJECT} ===\n`);

  const accs = api('GET', '/accounts');
  if (!accs.success) {
    console.error('  ❌ token invalido:', JSON.stringify(accs.errors || accs.raw).slice(0, 200));
    process.exit(1);
  }
  const acc = accs.result[0];
  console.log(`  conta: ${acc.name}`);
  if (ACCOUNT && ACCOUNT !== acc.id) console.log(`  ⚠️  CLOUDFLARE_ACCOUNT_ID diverge; usando o da conta do token`);

  const proj = api('GET', `/accounts/${acc.id}/pages/projects/${PROJECT}`);
  if (!proj.success) {
    console.log(`  criando o projeto "${PROJECT}"...`);
    const cr = api('POST', `/accounts/${acc.id}/pages/projects`);
    if (!cr.success) {
      console.error('  ❌ nao foi possivel criar o projeto:', JSON.stringify(cr.errors).slice(0, 300));
      process.exit(1);
    }
    console.log('  criado ✅');
  } else {
    console.log(`  projeto: https://${proj.result.subdomain}`);
  }

  const arquivos = fs.readdirSync(SITE).filter((f) => !f.startsWith('.'));
  console.log(`\n  enviando ${arquivos.length} entradas de site/ ...`);

  const env = { ...process.env, CLOUDFLARE_API_TOKEN: TOKEN, CLOUDFLARE_ACCOUNT_ID: acc.id };
  const raiz = path.resolve(__dirname, '..');

  // O Pages exige que o wrangler.toml fique na RAIZ do projeto, mas a raiz
  // tem o config do WORKER. Troca um pelo outro durante o deploy.
  const cfgRaiz = path.join(raiz, 'wrangler.toml');
  const cfgWorker = fs.readFileSync(cfgRaiz, 'utf8');
  const cfgPages = fs.readFileSync(path.join(raiz, 'deploy', 'wrangler.pages.toml'), 'utf8');

  let r;
  try {
    fs.writeFileSync(cfgRaiz, cfgPages);
    r = spawnSync('npx', ['wrangler', 'pages', 'deploy', './site',
      '--project-name', PROJECT, '--branch', 'main', '--commit-dirty=true'], {
      cwd: raiz,
      env,
      encoding: 'utf8',
    });
  } finally {
    fs.writeFileSync(cfgRaiz, cfgWorker);
  }

  const out = (r.stdout || '') + (r.stderr || '');
  out.split('\n').filter((l) => l.trim()).forEach((l) => console.log('   ' + l.slice(0, 160)));

  if (r.status !== 0) {
    console.error('\n❌ FALHA no deploy.\n');
    process.exit(1);
  }
  console.log(`\n  🎉  https://${PROJECT}.pages.dev\n`);
})();
