#!/usr/bin/env python3
"""
Faz o frontend consumir window.AUXF_CONFIG (config.js) em vez de hard-code.

Arquivos que resolvem a URL da API:
  - api-client.js  (const API_BASE = ...)
  - index.html     (function accessApiBase)
  - checkout.html  (function checkoutApiBase)
  - success.html   (function base)
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')

RESOLVER = '''(function () {
  var cfg = (typeof window !== 'undefined' && window.AUXF_CONFIG) ? window.AUXF_CONFIG : {};
  var base = (cfg && cfg.apiBase) ? String(cfg.apiBase).replace(/\\/+$/, '') : '';
  if (!base) {
    var local = (typeof window !== 'undefined' &&
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:'));
    base = local ? 'http://localhost:8000' : (typeof window !== 'undefined' ? window.location.origin : '');
  }
  return base;
})()'''

# ---------- api-client.js ----------
p = OUT / 'api-client.js'
c = p.read_text(encoding='utf-8')
VELHO = """const API_BASE = window.location.origin.includes('localhost') || window.location.protocol === 'file:'
  ? 'http://localhost:8000'
  : window.location.origin;"""
NOVO = """const API_BASE = (function () {
  var cfg = (typeof window !== 'undefined' && window.AUXF_CONFIG) ? window.AUXF_CONFIG : {};
  var base = (cfg && cfg.apiBase) ? String(cfg.apiBase).replace(/\\/+$/, '') : '';
  if (!base) {
    var local = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:');
    base = local ? 'http://localhost:8000' : window.location.origin;
  }
  return base;
})();"""
if VELHO in c:
    c = c.replace(VELHO, NOVO)
    p.write_text(c, encoding='utf-8')
    print('api-client.js: usa AUXF_CONFIG')
else:
    print('api-client.js: PADRAO NAO ENCONTRADO')

# ---------- index.html / checkout.html / success.html ----------
FUNCS = {
    'index.html': ('function accessApiBase() {', 'accessApiBase'),
    'checkout.html': ('function checkoutApiBase() {', 'checkoutApiBase'),
    'success.html': ('function base() {', 'base'),
}

for fname, (sig, _) in FUNCS.items():
    p = OUT / fname
    if not p.exists():
        continue
    c = p.read_text(encoding='utf-8')
    i = c.find(sig)
    if i == -1:
        print(f'{fname}: funcao nao encontrada')
        continue
    # encontra o fim da funcao (chave na mesma indentacao)
    j = c.find('\n  }', i)
    if j == -1:
        print(f'{fname}: fim da funcao nao encontrado')
        continue
    corpo = ('function ' + fname.replace('.html', '') + 'Base() {\n'
             '    var cfg = (typeof window !== \'undefined\' && window.AUXF_CONFIG) ? window.AUXF_CONFIG : {};\n'
             '    var b = (cfg && cfg.apiBase) ? String(cfg.apiBase).replace(/\\/+$/, \'\') : \'\';\n'
             '    if (!b) {\n'
             '      var local = (window.location.hostname === \'localhost\' || window.location.hostname === \'127.0.0.1\' || window.location.protocol === \'file:\');\n'
             '      b = local ? \'http://localhost:8000\' : window.location.origin;\n'
             '    }\n'
             '    return b;\n'
             '  }')
    # preserva o nome original da funcao
    nome_original = c[i:i + c[i:].find('(')].strip()
    corpo = corpo.replace('function ' + fname.replace('.html', '') + 'Base()',
                          nome_original)
    c = c[:i] + corpo + c[j + 4:]
    p.write_text(c, encoding='utf-8')
    print(f'{fname}: {nome_original} usa AUXF_CONFIG')

# ---------- inclui config.js antes de api-client.js ----------
for fname, after in [('index.html', '<head>'), ('checkout.html', '<head>'), ('success.html', '<head>')]:
    p = OUT / fname
    c = p.read_text(encoding='utf-8')
    if 'config.js' in c:
        continue
    i = c.find(after)
    if i == -1:
        continue
    fim = c.find('>', i) + 1
    c = c[:fim] + '\n<script src="config.js"></script>' + c[fim:]
    p.write_text(c, encoding='utf-8')
    print(f'{fname}: config.js incluido')
