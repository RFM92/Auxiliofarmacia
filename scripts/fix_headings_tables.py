#!/usr/bin/env python3
"""
Correcao semantica de headings e tabelas.

1. ADMIN: h1 dos logos (login/sidebar) -> div.brand-title (+ CSS equivalente)
   h1 class="page-title" -> h2 class="page-title" (visual mantido)
2. DASHBOARDS: 2o h1 (topbar) -> h2 (+ CSS .title-row h2 espelhando h1)
3. CHECKOUT: adiciona <h1> na pagina
4. PRIVACIDADE: adiciona <thead> nas 2 tabelas
"""
import re
import glob
import os
from pathlib import Path

OUT = Path('/workspace/output')


def admin_fix(c):
    n = 0
    # logos: h1 -> div.brand-title
    c2, k = re.subn(r'(<div class="login-logo">\s*)<h1>(.*?)</h1>',
                    r'\1<div class="brand-title">\2</div>', c, flags=re.S)
    n += k
    c2, k = re.subn(r'(<div class="sidebar-logo">\s*)<h1>(.*?)</h1>',
                    r'\1<div class="brand-title">\2</div>', c2, flags=re.S)
    n += k
    # CSS: replica .login-logo h1 e .sidebar-logo h1 para .brand-title
    css = '''
    .login-logo .brand-title, .sidebar-logo .brand-title {
      font-family: 'Playfair Display', serif;
      font-size: 28px;
      font-weight: 700;
      letter-spacing: -0.5px;
      margin: 0 0 4px 0;
      line-height: 1.1;
    }
    .sidebar-logo .brand-title { font-size: 22px; }
'''
    idx = c2.find('</style>')
    if idx != -1 and '.brand-title {' not in c2:
        c2 = c2[:idx] + css + c2[idx:]
    # titulos de pagina: h1 -> h2 (visual mantido via .page-title)
    c2, k = re.subn(r'<h1 class="page-title">', '<h2 class="page-title">', c2)
    # fecha os </h1> correspondentes
    c2 = re.sub(r'(<h2 class="page-title">[^<]*)</h1>', r'\1</h2>', c2)
    n += k
    return c2, n


def dashboard_fix(c):
    """Converte o 2o h1 (topbar) em h2 e espelha o CSS."""
    n = 0
    # localiza o 2o <h1>
    occ = list(re.finditer(r'<h1[^>]*>(.*?)</h1>', c, re.S))
    if len(occ) >= 2:
        m = occ[1]
        c = c[:m.start()] + '<h2 class="app-title">' + m.group(1) + '</h2>' + c[m.end():]
        n += 1
        # CSS: .title-row h2 espelha .title-row h1
        css = '''
.title-row h2 {
  margin: 0;
  position: relative;
  font-size: inherit;
  font-weight: inherit;
  font-family: inherit;
  color: inherit;
}
'''
        idx = c.find('</style>')
        if idx != -1 and '.title-row h2 {' not in c:
            c = c[:idx] + css + c[idx:]
    return c, n


def checkout_fix(c):
    if re.search(r'<h1\b', c):
        return c, 0
    # adiciona h1 no titulo da pagina
    m = re.search(r'(?i)(<h2[^>]*>\s*Pagamento\s*</h2>|<h2[^>]*>\s*Assinar[^<]*</h2>)', c)
    if m:
        return c[:m.start()] + m.group(0).replace('<h2', '<h1').replace('</h2>', '</h1>') + c[m.end():], 1
    # fallback: primeiro h2 vira h1
    m = re.search(r'(?i)<h2([^>]*)>(.*?)</h2>', c, re.S)
    if m:
        return c[:m.start()] + f'<h1{m.group(1)}>{m.group(2)}</h1>' + c[m.end():], 1
    return c, 0


def privacidade_fix(c):
    """Adiciona <thead> nas tabelas que tem <tr> direto no <tbody> ou sem tbody."""
    n = 0

    def rep(m):
        nonlocal n
        tabela = m.group(0)
        if '<thead' in tabela:
            return tabela
        # encontra a primeira linha com <th>
        th = re.search(r'(?is)<tr[^>]*>\s*((?:<th[^>]*>.*?</th>\s*)+)</tr>', tabela)
        if not th:
            return tabela
        n += 1
        thead = '<thead><tr>' + th.group(1) + '</tr></thead>'
        # remove a linha original do <th> e insere o thead
        rest = tabela.replace(th.group(0), '', 1)
        if '<tbody' in rest:
            return rest.replace('<tbody>', '<tbody>\n' + thead, 1)
        return rest.replace('<table', '<table', 1).replace('>', '>\n' + thead, 1)
    c = re.sub(r'(?is)<table[^>]*>.*?</table>', rep, c)
    return c, n


def main():
    for p in sorted(OUT.glob('*.html')):
        nome = p.name
        c = p.read_text(encoding='utf-8', errors='replace')
        orig = c
        n = 0
        if nome == 'admin.html':
            c, n = admin_fix(c)
        elif nome.startswith('dashboard-auxfarmacia'):
            c, n = dashboard_fix(c)
        elif nome == 'checkout.html':
            c, n = checkout_fix(c)
        elif nome == 'privacidade.html':
            c, n = privacidade_fix(c)
        if c != orig:
            p.write_text(c, encoding='utf-8')
        if n:
            print(f'{nome}: {n} ajuste(s)')


if __name__ == '__main__':
    main()
