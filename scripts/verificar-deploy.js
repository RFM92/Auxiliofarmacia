#!/usr/bin/env node
/**
 * Verificador de deploy — confere se o site publicado no Cloudflare
 * esta no ar e se os pontos criticos funcionam.
 *
 *   node scripts/verificar-deploy.js https://auxiliofarmacia.pages.dev
 */
const https = require('https');
const http = require('http');

const BASE = (process.argv[2] || 'https://auxiliofarmacia.pages.dev').replace(/\/$/, '');

const PAGINAS = [
  ['/', 'index'],
  ['/index.html', 'index (html)'],
  ['/login.html', 'login'],
  ['/checkout.html', 'checkout'],
  ['/success.html', 'sucesso'],
  ['/downloads.html', 'downloads'],
  ['/config.js', 'config'],
  ['/404.html', '404'],
  ['/dashboard-auxfarmacia.html', 'dashboard master'],
  ['/dashboard-auxfarmacia-FREE.html', 'dashboard FREE'],
  ['/dashboard-auxfarmacia-PRO.html', 'dashboard PRO'],
  ['/dashboard-auxfarmacia-PREMIUM.html', 'dashboard PREMIUM'],
  ['/dashboard-auxfarmacia-ENTERPRISE.html', 'dashboard ENTERPRISE'],
  ['/dashboard-auxfarmacia-educativo.html', 'dashboard educativo'],
];

function get(url, redirects = 0) {
  return new Promise((resolve) => {
    if (!/^https?:\/\//.test(url)) {
      return resolve({ status: 0, body: '', type: '', err: 'URL invalida: ' + url });
    }
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, { timeout: 20000 }, (res) => {
      if ([301, 302, 307, 308].includes(res.statusCode) && redirects < 5) {
        res.resume();
        let loc = res.headers.location || '';
        if (loc.startsWith('/')) loc = BASE + loc;   // redirect relativo
        if (!loc) return resolve({ status: res.statusCode, body: '', type: '' });
        return resolve(get(loc, redirects + 1));
      }
      let body = '';
      res.on('data', (d) => { body += d; });
      res.on('end', () => resolve({ status: res.statusCode, body, type: res.headers['content-type'] || '' }));
    });
    req.on('error', (e) => resolve({ status: 0, body: '', type: '', err: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, body: '', type: '', err: 'timeout' }); });
  });
}

(async () => {
  console.log(`\n=== VERIFICANDO DEPLOY: ${BASE} ===\n`);
  let ok = 0, fail = 0;
  for (const [path, nome] of PAGINAS) {
    const r = await get(BASE + path);
    const bom = r.status === 200;
    bom ? ok++ : fail++;
    console.log(`  ${bom ? '✅' : '❌'} ${String(r.status).padEnd(4)} ${path.padEnd(42)} ${nome}${r.err ? '  (' + r.err + ')' : ''}`);
  }

  console.log(`\n--- conteudo critico em /index.html ---`);
  const idx = await get(BASE + '/index.html');
  if (idx.status === 200) {
    const checks = [
      ['aviso medico visivel', /N[ÃA]O.{0,40}(recomenda|indic)[ÃA]?[ÇC][ÃA]O|Cuidado|aten[Çc][ÃA]o/i],
      ['acesso unico (login)', /type="password"/i],
      ['campo de e-mail', /type="email"/i],
      ['recuperar senha', /esqueci|recuperar/i],
      ['config.js carregado', /config\.js/i],
    ];
    for (const [nome, rx] of checks) {
      const passou = rx.test(idx.body);
      passou ? ok++ : fail++;
      console.log(`  ${passou ? '✅' : '❌'} ${nome}`);
    }
    const cat = idx.body.match(/61\s+medicamentos/i);
    console.log(`  ${cat ? '✅' : '⚠️ '} número honesto "61 medicamentos" ${cat ? 'presente' : 'não encontrado'}`);
  }

  console.log(`\n--- /config.js ---`);
  const cfg = await get(BASE + '/config.js');
  if (cfg.status === 200) {
    const m = cfg.body.match(/apiBase:\s*'([^']*)'/);
    console.log(`  apiBase = ${m ? m[1] : '(não encontrado)'}`);
    const api = m && m[1];
    if (api) {
      const h = await get(api + '/api/health');
      const live = h.status === 200 || h.status === 401 || h.status === 403;
      live ? ok++ : fail++;
      console.log(`  ${live ? '✅' : '⚠️ '} backend ${api} -> HTTP ${h.status} ${h.err || ''}`);
    }
  }

  console.log(`\n=== ${ok} ok / ${fail} problema(s) ===\n`);
  process.exit(fail ? 1 : 0);
})();
