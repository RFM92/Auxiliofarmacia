#!/usr/bin/env node
/**
 * Teste E2E do FLUXO DE PAGAMENTO (via navegador real).
 *
 * Cenarios:
 *  1. checkout chama POST /api/payments/create (nao simula mais)
 *  2. PIX gera codigo copia-e-cola + QR
 *  3. Boleto gera link
 *  4. Cartao NAO coleta dados no site (PCI) e usa checkout hospedado
 *  5. activateLicense valida no BACKEND
 *
 * Uso: NODE_PATH=$(npm root -g) node scripts/test_payment_flow.js
 */
const { chromium } = require('playwright');
const BASE = process.env.BASE || 'http://localhost:9090';
const API = process.env.API || 'http://localhost:8000';

async function getToken() {
  const r = await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'admin@auxfarmacia.com.br', password: 'admin123' }),
  });
  const d = await r.json();
  return d.access_token || '';
}

(async () => {
  const token = await getToken();
  if (!token) { console.log('FALHA: nao obtive token'); process.exit(1); }

  const b = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const ctx = await b.newContext({ viewport: { width: 1366, height: 950 } });
  const ALLOW = [BASE, API, 'http://127.0.0.1:8000'];
  await ctx.route('**/*', (r) =>
    ALLOW.some((u) => r.request().url().startsWith(u)) ? r.continue() : r.abort()
  );
  const page = await ctx.newPage();
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message.slice(0, 90)));
  const chamadas = [];
  page.on('request', (r) => {
    if (r.url().includes('/api/payments/')) chamadas.push(r.method() + ' ' + r.url().replace(API, ''));
  });

  const resultado = { pix: null, boleto: null, cartao: null };

  for (const metodo of ['pix', 'boleto', 'card']) {
    await page.goto(`${BASE}/checkout.html?plan=pro`, { waitUntil: 'commit', timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    await page.evaluate((t) => { localStorage.setItem('auxf_api_token', t); }, token).catch(() => {});
    await page.reload({ waitUntil: 'commit' }).catch(() => {});
    await page.waitForTimeout(2000);

    await page.fill('#inputName', 'Teste Pagamento');
    await page.fill('#inputEmail', 'teste@exemplo.com');
    await page.click(`.pm-option[data-method="${metodo}"]`, { force: true }).catch(() => {});
    await page.waitForTimeout(400);

    // o frontend deve estar Asking for card data?
    const coletaCartao = await page.evaluate(() => {
      const f = document.getElementById('cardForm');
      const visivel = f && getComputedStyle(f).display !== 'none' && !f.hidden;
      const temCampos = !!document.getElementById('inputCard');
      return { formVisivel: visivel, camposCartaoPresentes: temCampos };
    });

    chamadas.length = 0;
    await page.click('#btnPay');
    await page.waitForTimeout(4500);

    const r = await page.evaluate(() => {
      const box = document.getElementById('pixBox');
      const ta = document.getElementById('pixCode');
      return {
        pixBoxVisivel: !!box && getComputedStyle(box).display !== 'none',
        codigoPix: ta && ta.value ? ta.value.slice(0, 24) + '...' : null,
        temBotaoVerificar: !!document.getElementById('btnCheckPix'),
        linkBoleto: !!document.querySelector('#pixBox a[href*="boleto"], #pixBox a[href*="pdf"]'),
        alert: (document.getElementById('alertBox') || {}).innerText ? document.getElementById('alertBox').innerText.slice(0, 80) : '',
        gerouChaveNoCliente: (localStorage.getItem('pedb_pending_key') || null) !== null,
      };
    }).catch((e) => ({ redirecionou: true, nota: 'pagina navegou (gateway hospedado)' }));

    resultado[metodo] = { ...r, coletaCartao, chamadasAPI: chamadas.slice() };
    console.log(`\n--- ${metodo.toUpperCase()} ---`);
    console.log(JSON.stringify(resultado[metodo], null, 1));
  }

  // ---- activateLicense no backend ----
  await page.goto(`${BASE}/dashboard-auxfarmacia.html`, { waitUntil: 'commit', timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(5000);
  const lic = await page.evaluate(async () => {
    const demo = await window.activateLicense('AUXFARMA-DEMO1-DEMO2-DEMO3-DEMO4');
    localStorage.removeItem('auxf_license');
    const falsa = await window.activateLicense('AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX');
    return {
      demo: { success: demo.success, error: demo.error, msg: demo.message },
      falsa: { success: falsa.success, error: falsa.error, msg: falsa.message },
    };
  });
  console.log('\n--- activateLicense ---');
  console.log(JSON.stringify(lic, null, 1));

  console.log('\nerros de runtime:', erros.length ? erros.slice(0, 3) : 'NENHUM');
  await b.close();
})();
