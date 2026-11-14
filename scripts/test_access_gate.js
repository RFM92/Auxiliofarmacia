#!/usr/bin/env node
/**
 * Testa o fluxo de ACESSO UNICO no index.html:
 *  1. visitanteve o card de login (nao o menu de acessos)
 *  2. login com credencial errada -> mostra erro
 *  3. login correto -> cria sessao e vai para o dashboard
 *  4. no dashboard, verifica o paywall (FREE bloqueia Pro, PRO desbloqueia)
 *
 * Uso: NODE_PATH=$(npm root -g) node scripts/test_access_gate.js
 */
const { chromium } = require('playwright');
const BASE = process.env.BASE || 'http://localhost:9090';

(async () => {
  const b = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const ALLOW = [BASE, 'http://localhost:8000', 'http://127.0.0.1:8000'];
  await ctx.route('**/*', (r) =>
    ALLOW.some((u) => r.request().url().startsWith(u)) ? r.continue() : r.abort()
  );
  const page = await ctx.newPage();
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message.slice(0, 100)));

  // ---------- 1. visitante ----------
  await page.goto(`${BASE}/index.html`, { waitUntil: 'commit', timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(2500);
  const t1 = await page.evaluate(() => ({
    cardLogin: !!document.querySelector('.access-card'),
    email: !!document.getElementById('accessEmail'),
    senha: !!document.getElementById('accessPassword'),
    botaoEntrar: !!(document.querySelector('.access-card button[type=submit]')),
    // nao deve haver menu de multiplos acessos no topo
    linksDiretosDashboard: document.querySelectorAll('.hero-actions a[href*="dashboard"]').length,
    temLinkAdminNoHero: document.querySelectorAll('a[href*="admin.html"]').length,
  }));
  console.log('1) VISITANTE:', JSON.stringify(t1));

  // ---------- 2. senha errada ----------
  await page.fill('#accessEmail', 'admin@auxfarmacia.com.br');
  await page.fill('#accessPassword', 'senhaerrada');
  await page.click('.access-card button[type=submit]');
  await page.waitForTimeout(900);
  const t2 = await page.evaluate(() => {
    const m = document.getElementById('accessMsg');
    return { visivel: m && getComputedStyle(m).display !== 'none', texto: m ? m.textContent.slice(0, 60) : '', url: location.pathname };
  });
  console.log('2) SENHA ERRADA:', JSON.stringify(t2));

  // ---------- 3. login correto ----------
  await page.fill('#accessPassword', 'admin123');
  await page.click('.access-card button[type=submit]');
  await page.waitForTimeout(2200);
  const t3 = await page.evaluate(() => ({
    url: location.pathname,
    sessao: (() => { try { return JSON.parse(localStorage.getItem('auxf_session') || 'null'); } catch (e) { return null; } })(),
  }));
  console.log('3) LOGIN OK:', JSON.stringify(t3));

  // ---------- 4. paywall no dashboard ----------
  await page.waitForTimeout(3000);
  const t4 = await page.evaluate(() => ({
    url: location.pathname,
    meds: Array.isArray(window.meds) ? window.meds.length : 'UNDEFINED',
    currentPlan: window.currentPlan,
    sessao: (() => { try { return JSON.parse(localStorage.getItem('auxf_session') || 'null'); } catch (e) { return null; } })(),
    bloqueados: document.querySelectorAll('.med-list-item-locked').length,
    badgesPro: document.querySelectorAll('.med-pro-badge').length,
  }));
  console.log('4) DASHBOARD (admin/enterprise):', JSON.stringify(t4));

  // ---------- 5. usuario FREE ----------
  await page.evaluate(() => {
    localStorage.setItem('auxf_users', JSON.stringify({
      'teste@free.com': { nome: 'Teste Free', email: 'teste@free.com', senha: 'h_1x2y3z', plano: 'free' }
    }));
    localStorage.setItem('auxf_session', JSON.stringify({ email: 'teste@free.com', plano: 'free', expira: null }));
  });
  await page.reload({ waitUntil: 'commit' }).catch(() => {});
  await page.waitForTimeout(5000);
  const t5 = await page.evaluate(() => ({
    currentPlan: window.currentPlan,
    sessaoPlano: (() => { try { return (JSON.parse(localStorage.getItem('auxf_session') || '{}')).plano; } catch (e) { return null; } })(),
    bloqueados: document.querySelectorAll('.med-list-item-locked').length,
    badgesPro: document.querySelectorAll('.med-pro-badge').length,
    aviso: document.body.innerText.includes('Sem licença ativa') || document.body.innerText.includes('plano Free'),
  }));
  console.log('5) DASHBOARD (free):', JSON.stringify(t5));

  console.log('\nerros de runtime:', erros.length ? erros.slice(0, 3) : 'NENHUM');
  await b.close();
})();
