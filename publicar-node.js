#!/usr/bin/env node
/**
 * ===================================================================
 *  Publica o Auxílio Farmácia no GitHub via API de Conteúdo (Contents API).
 *  Compatível com Personal Access Token fine-grained (escopo: Contents).
 *
 *   GITHUB_TOKEN=xxx node publicar-node.js
 * ===================================================================
 */
const fs = require('fs');
const path = require('path');

const OWNER = process.env.GITHUB_OWNER || 'raphaelmenossi-maker';
const REPO = process.env.GITHUB_REPO || 'Auxiliofarmacia';
const BRANCH = process.env.GITHUB_BRANCH || 'main';
const API = 'https://api.github.com';
const TOKEN = process.env.GITHUB_TOKEN;

const IGNORAR_DIRS = new Set(['.git', 'node_modules', '__pycache__', '.venv', 'venv', '.idea', '.vscode']);
const IGNORAR_ARQUIVOS = new Set(['.env', '.DS_Store', 'Thumbs.db']);
// Arquivos restritos: nunca vao para o repo publico (saem via API autenticada)
const IGNORAR_CAMINHOS = new Set(['api/output']);

function coletar(raiz) {
  const out = [];
  (function walk(dir, prefixo) {
    for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
      if (item.isDirectory()) {
        if (IGNORAR_DIRS.has(item.name)) continue;
        walk(path.join(dir, item.name), prefixo ? `${prefixo}/${item.name}` : item.name);
      } else {
        if (IGNORAR_ARQUIVOS.has(item.name)) continue;
        if (/\.pyc$/.test(item.name)) continue;
        const caminhoRel = prefixo ? `${prefixo}/${item.name}` : item.name;
        if (IGNORAR_CAMINHOS.has(caminhoRel)) continue;
        out.push({ path: prefixo ? `${prefixo}/${item.name}` : item.name, abs: path.join(dir, item.name) });
      }
    }
  })(raiz, '');
  return out;
}

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
  try { d = t ? JSON.parse(t) : {}; } catch (e) { d = { raw: t.slice(0, 300) }; }
  if (!r.ok) throw new Error(`${method} ${url} -> ${d.message || d.raw || 'HTTP ' + r.status}`);
  return d;
}

async function shaDe(caminho) {
  try {
    const d = await gh('GET', `/repos/${OWNER}/${REPO}/contents/${caminho}?ref=${BRANCH}`);
    return d.sha || null;
  } catch (e) {
    if (/Not Found/i.test(e.message)) return null;
    throw e;
  }
}

(async () => {
  if (!TOKEN) { console.error('GITHUB_TOKEN nao definido'); process.exit(1); }
  const raiz = __dirname;
  const arquivos = coletar(raiz);
  console.log(`📁 ${arquivos.length} arquivos`);
  console.log(`   destino: https://github.com/${OWNER}/${REPO} (branch ${BRANCH})\n`);

  // ---- seguranca ----
  const perigosos = arquivos.filter(a => /(^|\/)\.env$|\.db$|\.key$|\.pem$|venv\//.test(a.path));
  if (perigosos.length) {
    console.error('❌ Arquivos sensiveis:', perigosos.map(a => a.path));
    process.exit(1);
  }
  for (const a of arquivos) {
    if (/\.(md|js|py|txt|html)$/.test(a.path)) {
      const t = fs.readFileSync(a.abs, 'utf8');
      if (/aact_(prod|hmlg)_[A-Za-z0-9]{15,}|sk_live_[A-Za-z0-9]{15,}/.test(t)) {
        console.error(`❌ Chave real em ${a.path}`); process.exit(1);
      }
    }
  }
  console.log('🛡️  Sem segredos\n');

  // -----branch ----
  let branchExiste = true;
  try {
    await gh('GET', `/repos/${OWNER}/${REPO}/git/ref/heads/${BRANCH}`);
  } catch (e) {
    if (/Not Found/i.test(e.message)) branchExiste = false;
    else throw e;
  }
  if (!branchExiste) {
    console.log('🌿 Branch não existe, será criada no primeiro arquivo.');
  }

  // ---- envia arquivo por arquivo ----
  let ok = 0; const erros = [];
  for (let i = 0; i < arquivos.length; i++) {
    const a = arquivos[i];
    const buf = fs.readFileSync(a.abs);
    const sha = await shaDe(a.path);
    const payload = {
      message: `feat: Auxilio Farmacia v2026.08.1 - ${a.path}`,
      content: buf.toString('base64'),
      branch: BRANCH,
    };
    if (sha) payload.sha = sha;
    try {
      await gh('PUT', `/repos/${OWNER}/${REPO}/contents/${a.path}`, payload);
      ok++;
    } catch (e) {
      erros.push(`${a.path}: ${e.message}`);
    }
    if ((i + 1) % 20 === 0) process.stdout.write(`   ${i + 1}/${arquivos.length}\n`);
  }

  console.log(`\n✅ ${ok}/${arquivos.length} arquivos enviados`);

  // ---- SINCRONIZA: apaga no GitHub o que nao existe mais localmente ----
  // (sem isso, arquivo removido local continua no repositorio -- foi o que
  //  deixou o package.json antigo na raiz e enganou o Cloudflare Pages)
  if (process.env.GITHUB_SYNC !== '0') {
    const locais = new Set(arquivos.map(a => a.path));
    const remotos = await gh('GET', `/repos/${OWNER}/${REPO}/git/trees/${BRANCH}?recursive=1`);
    const alvos = (remotos.tree || [])
      .filter(t => t.type === 'blob')
      .filter(t => !locais.has(t.path))
      .filter(t => !/^(docs\/)/.test(t.path));   // preserva docs/ manualmente
    if (alvos.length) {
      console.log(`\n🧹 Sincronizando: ${alvos.length} arquivo(s) remoto(s) orfao(s)...`);
      for (const t of alvos) {
        const d = await gh('DELETE', `/repos/${OWNER}/${REPO}/contents/${t.path}?sha=${t.sha}&message=sync%3A%20remove%20arquivo%20orfao`);
        console.log(`   ${d.ok ? '🗑️ ' : '⚠️  '} ${t.path}`);
      }
    } else {
      console.log('\n🧹 Sincronizacao: nada a remover.');
    }
  }
  if (erros.length) {
    console.log(`❌ ${erros.length} erro(s):`);
    erros.slice(0, 10).forEach(e => console.log('   ' + e));
  }

  // ---- confere ----
  const lista = await gh('GET', `/repos/${OWNER}/${REPO}/contents/?ref=${BRANCH}`);
  console.log(`\n📂 Repo agora tem ${lista.length} itens na raiz`);

  console.log('\n═══════════════════════════════════════════════');
  console.log('  ✅ REPOSITÓRIO PUBLICADO!');
  console.log('═══════════════════════════════════════════════');
  console.log(`  https://github.com/${OWNER}/${REPO}`);
  console.log('');
  console.log('  PRÓXIMO PASSO — Cloudflare Pages (frontend):');
  console.log('    https://dash.cloudflare.com/ → Workers & Pages → Create');
  console.log('    → Connect to Git → Auxiliofarmacia');
  console.log('    → Build command: (vazio)');
  console.log('    → Build output directory: site');
  console.log('    → Deploy → https://auxiliofarmacia.pages.dev');
  console.log('');
  console.log('  Depois: https://huggingface.co/new-space (Docker) para o backend.');
})().catch(e => { console.error('\n❌', e.message); process.exit(1); });
