#!/usr/bin/env node
/**
 * Configura um dominio .com.br na Cloudflare e o liga ao projeto Pages.
 *
 *   # 1) cria a zona (precisa de Zone:Zone:Edit + Zone:DNS:Edit)
 *   node scripts/adicionar-dominio-cloudflare.js auxiliofarmacia.com.br
 *
 *   # 2) ja com a zona criada, adiciona o custom domain no Pages
 *   node scripts/adicionar-dominio-cloudflare.js --pages auxiliofarmacia.com.br
 *
 * O token precisa de:
 *   - Account > Workers Scripts > Edit
 *   - Account > Account Settings > Read
 *   - Account > Pages > Edit
 *   - Zone > Zone > Edit
 *   - Zone > DNS > Edit
 */
const { spawnSync } = require('child_process');

const TOKEN = process.env.CLOUDFLARE_API_TOKEN || '';
const API = 'https://api.cloudflare.com/client/v4';
const PROJECT = process.env.CLOUDFLARE_PROJECT || 'auxilio-farmacia';

if (!TOKEN) {
  console.error('\n❌ CLOUDFLARE_API_TOKEN ausente.\n');
  process.exit(2);
}

async function api(method, pathname, body) {
  const r = await fetch(API + pathname, {
    method,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const t = await r.text();
  let j;
  try { j = JSON.parse(t); } catch { j = { raw: t }; }
  if (!r.ok || j.success === false) {
    const err = (j.errors || []).map((e) => `${e.code}: ${e.message}`).join('; ') || t.slice(0, 300);
    throw new Error(`${method} ${pathname} -> ${r.status} ${err}`);
  }
  return j.result;
}

(async () => {
  const args = process.argv.slice(2);
  const soPages = args.includes('--pages');
  const dominio = (args.find((a) => !a.startsWith('--')) || '').replace(/^https?:\/\//, '').replace(/\/.*$/, '');
  if (!dominio) {
    console.error('\nuso: node scripts/adicionar-dominio-cloudflare.js [--pages] <dominio>\n');
    process.exit(2);
  }

  console.log(`\n=== DOMINIO: ${dominio} ===\n`);
  const accs = await api('GET', '/accounts');
  const acc = accs[0];
  console.log(`  conta: ${acc.name}`);

  if (!soPages) {
    // ---------- 1) cria a zona ----------
    const zonas = await api('GET', `/zones?name=${encodeURIComponent(dominio)}`);
    let zona = zonas[0];
    if (!zona) {
      console.log('  criando a zona...');
      zona = await api('POST', '/zones', {
        name: dominio,
        account: { id: acc.id },
        type: 'full',
      });
      console.log('  zona criada ✅');
    } else {
      console.log('  zona já existe');
    }
    console.log(`  nameservers da Cloudflare:`);
    (zona.name_servers || []).forEach((ns) => console.log(`    ${ns}`));
    console.log(`\n  >>> Troque os nameservers do dominio no Registro.br por esses 2.`);
    console.log(`  >>> Propagacao: de minutos a 24h.\n`);
    return;
  }

  // ---------- 2) custom domain no Pages ----------
  console.log('  adicionando o custom domain no Pages...');
  try {
    const d = await api('POST', `/accounts/${acc.id}/pages/projects/${PROJECT}/domains`, { name: dominio });
    console.log(`  ✅ dominio adicionado: ${d.name}  (status: ${d.status || 'pendente'})`);
  } catch (e) {
    console.log(`  ⚠️  ${e.message}`);
    console.log('  (se já existir, tudo bem — a Cloudflare ignora duplicados)');
  }

  console.log('\n  dominios do projeto:');
  const doms = await api('GET', `/accounts/${acc.id}/pages/projects/${PROJECT}/domains`);
  doms.forEach((d) => console.log(`    ${d.name}  [${d.status}]`));

  console.log('\n  ⏱️  O SSL e emitido automaticamente (Universal SSL, gratis).');
  console.log('     Verifique em: Workers & Pages → ' + PROJECT + ' → Custom domains\n');
})().catch((e) => {
  console.error('\n❌ ERRO:', e.message, '\n');
  process.exit(1);
});
