#!/usr/bin/env node
/**
 * Validação em navegador real (Playwright/Chromium).
 * Uso: NODE_PATH=$(npm root -g) node scripts/e2e_check.js [arquivo.html ...]
 */
const { chromium } = require('playwright');
const path = require('path');

const BASE = process.env.BASE || 'http://localhost:9090';
const ARGS = process.argv.slice(2);
const FILES = ARGS.length ? ARGS : [
  'dashboard-auxfarmacia.html',
  'dashboard-auxfarmacia-FREE.html',
  'dashboard-auxfarmacia-PRO.html',
  'dashboard-auxfarmacia-PREMIUM.html',
  'dashboard-auxfarmacia-ENTERPRISE.html',
  'dashboard-auxfarmacia-educativo.html',
];

(async () => {
  const b = await chromium.launch({
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
  });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  await ctx.route('**/*', (r) =>
    r.request().url().startsWith(BASE) ? r.continue() : r.abort()
  );
  const page = await ctx.newPage();
  let falhas = 0;

  for (const f of FILES) {
    const errs = [];
    page.removeAllListeners('pageerror');
    page.removeAllListeners('console');
    page.on('pageerror', (e) => errs.push('JS: ' + e.message.slice(0, 110)));
    page.on('console', (m) => {
      if (m.type() === 'error' && !m.text().includes('ERR_FAILED'))
        errs.push('C: ' + m.text().slice(0, 110));
    });
    try {
      await page.goto(`${BASE}/${f}`, { waitUntil: 'commit', timeout: 15000 });
    } catch (e) { /* timeout: pagina grande */ }
    await page.waitForTimeout(6000);

    let r = {};
    try {
      r = await page.evaluate(() => ({
        meds: Array.isArray(window.meds) ? window.meds.length : 'UNDEFINED',
        opcoes: document.querySelectorAll('#medSelect option').length,
        api: typeof window.AUXF_API,
        drawer: typeof window.toggleSiteDrawer,
        tabs: typeof window.activateTabById,
        h1: document.querySelectorAll('h1').length,
        skipLink: !!document.querySelector('.skip-link'),
        ariaLabels: document.querySelectorAll('[aria-label]').length,
        roleBtn: document.querySelectorAll('[role="button"],[role="tab"]').length,
        noopener: document.querySelectorAll('a[target="_blank"][rel*="noopener"]').length,
        blankTotal: document.querySelectorAll('a[target="_blank"]').length,
        texto: document.body.innerText.length,
      }));
    } catch (e) { r = { erro: e.message.slice(0, 60) }; }

    const ehDashboard = f.startsWith('dashboard-auxfarmacia');
    const ok = errs.length === 0 && !r.erro &&
      (!ehDashboard || (typeof r.meds === 'number' && r.meds >= 61));
    if (!ok) falhas++;
    console.log(`${ok ? 'OK  ' : 'FALHA'} ${f}`);
    console.log('     ' + JSON.stringify(r));
    if (errs.length) console.log('     erros: ' + JSON.stringify(errs.slice(0, 3)));
  }

  await b.close();
  console.log(falhas === 0 ? '\nTODOS OS BUILDS OK' : `\n${falhas} build(s) com problema`);
  process.exit(falhas === 0 ? 0 : 1);
})();
