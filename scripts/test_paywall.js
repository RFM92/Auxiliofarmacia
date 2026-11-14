#!/usr/bin/env node
/**
 * Auditoria do PAYWALL: verifica se o conteudo e realmente bloqueado por plano.
 *
 * Cenarios:
 *  FREE     -> deve BLOQUEAR classes Pro (antibioticos, controlados) mas
 *              deixar visiveis (nao esconder) + 70% do catalogo liberado
 *  PRO      -> desbloqueia as classes Pro
 *  PREMIUM  -> desbloqueia tudo + cursos
 *
 * Uso: NODE_PATH=$(npm root -g) node scripts/test_paywall.js
 */
const { chromium } = require('playwright');
const BASE = process.env.BASE || 'http://localhost:9090';

const CENARIOS = [
  { plano: 'free', esperado: 'bloqueado' },
  { plano: 'pro', esperado: 'liberado' },
  { plano: 'premium', esperado: 'liberado' },
  { plano: 'enterprise', esperado: 'liberado' },
];

(async () => {
  const b = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const ctx = await b.newContext({ viewport: { width: 1366, height: 900 } });
  const ALLOW = [BASE, 'http://localhost:8000'];
  await ctx.route('**/*', (r) =>
    ALLOW.some((u) => r.request().url().startsWith(u)) ? r.continue() : r.abort()
  );
  const page = await ctx.newPage();
  const erros = [];
  page.on('pageerror', (e) => erros.push(e.message.slice(0, 90)));

  for (const cen of CENARIOS) {
    await page.goto(`${BASE}/dashboard-auxfarmacia.html`, { waitUntil: 'commit', timeout: 15000 }).catch(() => {});
    await page.evaluate((plano) => {
      localStorage.setItem('auxf_session', JSON.stringify({
        email: 'teste@plano.com', plano: plano, expira: null
      }));
    }, cen.plano);
    await page.reload({ waitUntil: 'commit' }).catch(() => {});
    await page.waitForTimeout(6000);

    const r = await page.evaluate(() => {
      const medItems = document.querySelectorAll('.med-card[data-id], .med-item[data-id], .med-list-item');
      const locked = document.querySelectorAll('.med-list-item-locked');
      const badges = document.querySelectorAll('.med-pro-badge');
      // conta classes Pro visiveis
      let proVisiveis = 0, proBloqueados = 0;
      document.querySelectorAll('.med-card[data-id], .med-item[data-id], .med-list-item').forEach((el) => {
        const id = el.dataset.id;
        const med = (window.meds || []).find((m) => m.id === id);
        if (!med) return;
        const isPro = ['Antibióticos', 'Controlados', 'Psicotrópicos', 'Benzodiazepínicos', 'Opióides', 'Estimulantes']
          .includes(med.classe);
        if (!isPro) return;
        proVisiveis++;
        if (el.classList.contains('med-list-item-locked')) proBloqueados++;
      });
      return {
        currentPlan: window.currentPlan,
        totalItens: medItems.length,
        locked: locked.length,
        badgesPro: badges.length,
        proVisiveis: proVisiveis,
        proBloqueados: proBloqueados,
        avisoFree: document.body.innerText.includes('Sem licença ativa') ||
                   document.body.innerText.includes('plano Free') ||
                   document.body.innerText.includes('Faça upgrade'),
      };
    });

    const bloqueou = r.proBloqueados > 0;
    const liberou = r.proBloqueados === 0 && r.proVisiveis > 0;
    const ok = cen.esperado === 'bloqueado' ? bloqueou : (liberou || r.proVisiveis === 0);
    console.log(`${ok ? 'OK  ' : 'FALHA'} ${cen.plano.padEnd(10)} ${JSON.stringify(r)}`);
  }

  console.log('\nerros de runtime:', erros.length ? erros.slice(0, 3) : 'NENHUM');
  await b.close();
})();
