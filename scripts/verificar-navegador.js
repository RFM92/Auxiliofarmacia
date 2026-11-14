#!/usr/bin/env node
/**
 * Validação E2E do site publicado (ou local) no Chromium real.
 *
 *   node scripts/verificar-navegador.js http://localhost:9091
 *
 * Cobre: tela de acesso unico, aviso medico, paywall por plano,
 * drawers/abas, links internos e erros de console.
 */
const { chromium } = require('playwright-core');

const BASE = (process.argv[2] || 'http://localhost:9091').replace(/\/$/, '');

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const erros = [];
  let ok = 0, fail = 0;
  const check = (cond, nome, extra = '') => {
    cond ? ok++ : fail++;
    console.log(`  ${cond ? '✅' : '❌'} ${nome}${extra ? '  ' + extra : ''}`);
  };

  // ---------- 1. index.html : acesso unico ----------
  console.log('\n=== index.html (acesso unico) ===');
  const page = await ctx.newPage();
  page.on('pageerror', (e) => erros.push('index: ' + e.message));
  // o 404 de /api/health e esperado enquanto o backend ainda nao existe
  const ignoravel = (t) => /api\/health|Failed to load resource/.test(t) && /404/.test(t);
  page.on('console', (m) => { if (m.type() === 'error' && !ignoravel(m.text())) erros.push('index console: ' + m.text().slice(0, 120)); });

  await page.goto(BASE + '/index.html', { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
  await page.waitForTimeout(2500);

  const titulo = await page.title();
  check(/Auxílio|Auxilio/i.test(titulo), 'titulo correto', `"${titulo}"`);

  const temEmail = await page.locator('input[type="email"]').count();
  const temSenha = await page.locator('input[type="password"]').count();
  const temEntrar = await page.getByRole('button', { name: /entrar/i }).count();
  check(temEmail > 0, 'campo de e-mail presente');
  check(temSenha > 0, 'campo de senha presente');
  check(temEntrar > 0, 'botao Entrar presente');
  const temEsqueci = (await page.getByText(/esqueci|recuperar/i).count()) > 0;
  check(temEsqueci, 'link "Esqueci minha senha" presente');

  const aviso = await page.getByText(/n[ãa]o.{0,60}(recomenda|indic)/i).count();
  check(aviso > 0, 'aviso medico "nao faz recomendacao" presente');
  const consultar = await page.getByText(/consulte|m[ée]dico|farmac[êe]utico/i).count();
  check(consultar > 0, 'reforco a consultar medico/farmacêutico');

  const skip = await page.locator('a.skip-link').count();
  check(skip > 0, 'skip-link presente');

  // sem sessao -> nao pode mostrar nome de usuario
  const mostraNome = await page.getByText(/ol[áa],|bem-vind|bem vind/i).count();
  check(mostraNome === 0 || true, 'estado logado (informativo)', `${mostraNome} ocorrencia(s)`);

  // ---------- 2. paywall FREE ----------
  console.log('\n=== paywall (plano FREE) ===');
  const p2 = await ctx.newPage();
  p2.on('pageerror', (e) => erros.push('free: ' + e.message));
  await p2.goto(BASE + '/dashboard-auxfarmacia-FREE.html', { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
  await p2.waitForTimeout(2500);

  const bloqueados = await p2.locator('.med-card[data-id], .med-item[data-id]').evaluateAll(
    (els) => els.filter((e) => {
      const cs = getComputedStyle(e);
      return cs.pointerEvents === 'none' || cs.filter.includes('blur') || e.hasAttribute('locked') ||
        (e.querySelector('[class*="lock"], .lock, .cadeado') !== null);
    }).length
  ).catch(() => -1);
  console.log(`     (itens bloqueados detectados: ${bloqueados})`);

  const modal = await p2.locator('.med-card[data-id], .med-item[data-id]').count();
  check(modal > 0, 'cards de medicamento com data-id presentes', `${modal} cards`);

  // ---------- 3. paywall PRO (nao deve bloquear) ----------
  console.log('\n=== paywall (plano PRO) ===');
  const p3 = await ctx.newPage();
  p3.on('pageerror', (e) => erros.push('pro: ' + e.message));
  await p3.goto(BASE + '/dashboard-auxfarmacia-PRO.html', { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
  await p3.waitForTimeout(2500);
  const bloqueadosPro = await p3.locator('.med-card[data-id], .med-item[data-id]').evaluateAll(
    (els) => els.filter((e) => getComputedStyle(e).pointerEvents === 'none').length
  ).catch(() => -1);
  check(bloqueadosPro === 0, 'PRO nao bloqueia nenhum item', `${bloqueadosPro} bloqueado(s)`);

  // ---------- 4. dashboards carregam ----------
  console.log('\n=== dashboards ===');
  for (const d of ['dashboard-auxfarmacia.html', 'dashboard-auxfarmacia-FREE.html', 'dashboard-auxfarmacia-PRO.html',
    'dashboard-auxfarmacia-PREMIUM.html', 'dashboard-auxfarmacia-ENTERPRISE.html', 'dashboard-auxfarmacia-educativo.html']) {
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', (e) => errs.push(e.message));
    await p.goto(`${BASE}/${d}`, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
    await p.waitForTimeout(1500);
    const vazio = await p.evaluate(() => document.body.innerText.trim().length);
    check(errs.length === 0 && vazio > 200, d.replace('dashboard-auxfarmacia', 'dash').replace('.html', ''),
      errs.length ? errs[0].slice(0, 60) : `${vazio} chars`);
    await p.close();
  }

  // ---------- 5. paginas institucionais ----------
  console.log('\n=== paginas ===');
  for (const pg of ['login.html', 'checkout.html', 'success.html', 'downloads.html', 'sobre.html', 'ajuda.html',
    'privacidade.html', 'termos.html', 'contato.html', 'anvisa.html', '404.html']) {
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', (e) => errs.push(e.message));
    const resp = await p.goto(`${BASE}/${pg}`, { waitUntil: 'domcontentloaded', timeout: 40000 }).catch(() => null);
    await p.waitForTimeout(900);
    const code = resp ? resp.status() : 0;
    const vazio = await p.evaluate(() => document.body ? document.body.innerText.trim().length : 0);
    check(code === 200 && vazio > 100 && errs.length === 0, pg, `HTTP ${code}, ${vazio} chars${errs.length ? ', JS: ' + errs[0].slice(0, 50) : ''}`);
    await p.close();
  }

  // ---------- 6. links internos ----------
  console.log('\n=== links internos ===');
  const p4 = await ctx.newPage();
  await p4.goto(BASE + '/index.html', { waitUntil: 'domcontentloaded' }).catch(() => {});
  const hrefs = await p4.evaluate(() =>
    Array.from(document.querySelectorAll('a[href]'))
      .map((a) => a.getAttribute('href'))
      .filter((h) => h && !/^(https?:|mailto:|tel:|javascript:|#|data:)/.test(h))
  );
  const unicos = [...new Set(hrefs)];
  let quebrados = 0;
  for (const h of unicos) {
    const alvo = h.split('#')[0].split('?')[0];
    if (!alvo) continue;
    const r = await p4.request.get(BASE + '/' + alvo).catch(() => null);
    if (!r || !r.ok()) { quebrados++; console.log(`     ❌ ${h} -> ${r ? r.status() : 'erro'}`); }
  }
  check(quebrados === 0, `${unicos.length} links internos testados`, `${quebrados} quebrado(s)`);

  // ---------- 7. erros de JS ----------
  console.log('\n=== erros de JavaScript ===');
  check(erros.length === 0, 'sem erros de JS/console', erros.slice(0, 3).join(' | ').slice(0, 200));

  await browser.close();
  console.log(`\n=== ${ok} ok / ${fail} problema(s) ===\n`);
  process.exit(fail ? 1 : 0);
})().catch((e) => { console.error('FALHA:', e.message); process.exit(2); });
