#!/usr/bin/env node
/**
 * Verifica se alguma pagina renderiza CSS como texto (bug de <style> orfao).
 * Uso: NODE_PATH=$(npm root -g) node scripts/check_css_orphan.js
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = '/workspace/output';
const BASE = process.env.BASE || 'http://localhost:9090';
const files = fs.readdirSync(OUT)
  .filter((f) => f.endsWith('.html'))
  .filter((f) => !/^(debug|test-|diag-|check-|show-meds|force-meds|load\.|dashboard-FREE|dashboard-free-v2|VISUALIZAR)/.test(f));

(async () => {
  const b = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const ctx = await b.newContext();
  await ctx.route('**/*', (r) =>
    r.request().url().startsWith(BASE) ? r.continue() : r.abort()
  );
  const page = await ctx.newPage();
  let problemas = 0;
  for (const f of files) {
    try {
      await page.goto(`${BASE}/${f}`, { waitUntil: 'commit', timeout: 12000 });
      await page.waitForTimeout(2200);
      const n = await page.evaluate(() =>
        document.body.innerText.split('\n')
          .filter((l) => /\{[^}]*:[^}]*;/.test(l) && l.length > 40).length
      );
      if (n > 0) { console.log(`  ❌ ${f}: ${n} linhas de CSS como texto`); problemas++; }
      else console.log(`  ✅ ${f}`);
    } catch (e) {
      console.log(`  ⚠️  ${f}: ${e.message.slice(0, 45)}`);
    }
  }
  console.log(problemas === 0
    ? '\nNENHUMA PAGINA COM CSS COMO TEXTO'
    : `\n${problemas} pagina(s) com problema`);
  await b.close();
  process.exit(problemas === 0 ? 0 : 1);
})();
