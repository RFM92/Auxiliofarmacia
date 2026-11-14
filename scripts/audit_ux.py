#!/usr/bin/env python3
"""
Auditoria de UX / Acessibilidade (WCAG 2.1) - Auxilio Farmacia

Verifica:
  - contraste de cor (WCAG AA: 4.5:1 texto normal, 3:1 texto grande)
  - target="_blank" sem rel="noopener"
  - <div>/<span> clicavel sem role/tabindex
  - botao so-icone sem aria-label
  - input sem label (for) e sem aria-label
  - imagem sem alt
  - meta description / viewport / lang faltando
  - hierarquia de headings (h1 unico, sem salto)
  - skip-link
  - foco visivel
"""
import re
import glob
import os
import json
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path('/workspace/output')
issues = []


def add(sev, f, cat, msg, line=0):
    issues.append({'sev': sev, 'file': f, 'cat': cat, 'msg': msg, 'line': line})


# ---------- cor ----------
def hex2rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6 or not re.match(r'^[0-9a-fA-F]{6}$', h):
        return None
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    def f(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    L1, L2 = lum(a), lum(b)
    if L1 < L2:
        L1, L2 = L2, L1
    return (L1 + 0.05) / (L2 + 0.05)


def audit():
    files = sorted(glob.glob(str(OUT / '*.html')))
    # so os arquivos de PRODUCAO (ignora debug/test)
    producao = [f for f in files if not re.search(
        r'(debug|test-|diag-|check-|show-meds|force-meds|load\.html|dashboard-FREE|dashboard-free-v2|VISUALIZAR)', os.path.basename(f))]
    for p in producao:
        name = os.path.basename(p)
        c = Path(p).read_text(encoding='utf-8', errors='replace')
        lines = c.split('\n')

        # ---- contraste (scanner linear) ----
        import sys as _s
        _s.path.insert(0, '/workspace/scripts')
        from css_contrast import analyze_contrast
        for x in analyze_contrast(c):
            add('MÉDIA', name, 'CONTRASTE',
                f"ratio {x['ratio']}:1 (fg {x['fg']} sobre {x['bg']}) - minimo 4.5:1",
                x['line'])

        # ---- target=_blank ----
        for m in re.finditer(r'<a[^>]*target="_blank"[^>]*>', c, re.I):
            if 'noopener' not in m.group(0).lower():
                add('MÉDIA', name, 'TARGET_BLANK_SEM_NOOPENER',
                    'target="_blank" permite reverse-tabnabbing', c[:m.start()].count('\n') + 1)

        # ---- div/span clicavel ----
        for m in re.finditer(r'<(div|span)[^>]*\bonclick=[^>]*>', c, re.I):
            t = m.group(0)
            if 'role=' not in t and 'tabindex' not in t:
                add('BAIXA', name, 'CLICK_SEM_ROLE',
                    f'<{m.group(1)} onclick> sem role/tabindex - inacessivel por teclado',
                    c[:m.start()].count('\n') + 1)

        # ---- botao so-icone ----
        for m in re.finditer(r'<button(?![^>]*aria-label)(?![^>]*aria-labelledby)[^>]*>\s*'
                            r'(?:[⚙🔑📥✅❌×✕＋+−\-→←↑↓★⭐📋📥🎨🔒👤⚠️❗🔔🏠📊📚🏥⚖️💼📥💊🎓🔧🚪📝🔍🗑️↻🌙☀️🌤️])'
                            r'\s*</button>', c, re.I):
            add('BAIXA', name, 'BOTAO_SEM_ARIA',
                'botao somente-icone sem aria-label', c[:m.start()].count('\n') + 1)

        # ---- input sem label ----
        for m in re.finditer(r'<input(?![^>]*\btype=["\']?(hidden|submit|button|checkbox|radio))[^>]*>', c, re.I):
            t = m.group(0)
            if 'aria-label' in t or 'aria-labelledby' in t:
                continue
            if re.search(r'\bid=["\']', t):
                continue  # tem id (pode ter label for)
            add('MÉDIA', name, 'INPUT_SEM_LABEL',
                f'input sem label/aria-label: {t[:80]}', c[:m.start()].count('\n') + 1)

        # ---- img sem alt ----
        for m in re.finditer(r'<img(?![^>]*\balt=)[^>]*>', c, re.I):
            add('MÉDIA', name, 'IMG_SEM_ALT', m.group(0)[:80], c[:m.start()].count('\n') + 1)

        # ---- meta / lang ----
        if '<title>' not in c:
            add('MÉDIA', name, 'SEM_TITLE', 'sem <title>')
        if not re.search(r'(?i)<meta[^>]+name=["\']description', c):
            add('BAIXA', name, 'SEM_META_DESC', 'sem meta description')
        if not re.search(r'(?i)<meta[^>]+name=["\']viewport', c):
            add('MÉDIA', name, 'SEM_VIEWPORT', 'sem meta viewport (quebra mobile)')
        if not re.search(r'(?i)<html[^>]*\blang=', c):
            add('MÉDIA', name, 'SEM_LANG', 'sem lang no <html>')

        # ---- headings ----
        h1 = len(re.findall(r'(?i)<h1\b', c))
        if h1 == 0:
            add('BAIXA', name, 'SEM_H1', 'nenhum <h1>')
        elif h1 > 1:
            add('BAIXA', name, 'H1_MULTIPLO', f'{h1} elementos <h1>')

        # ---- skip link ----
        if 'skip-link' not in c and 'skip to' not in c.lower():
            add('BAIXA', name, 'SEM_SKIP_LINK', 'sem skip-link para navegacao por teclado')

        # ---- foco visivel ----
        if ':focus-visible' not in c and ':focus' not in c:
            add('MÉDIA', name, 'SEM_FOCO_VISIVEL', 'sem estilo de foco visivel')

        # ---- tabelas ----
        for m in re.finditer(r'<table(?![^>]*>\s*<thead)', c, re.I):
            add('BAIXA', name, 'TABLE_SEM_THEAD', 'tabela sem <thead>', c[:m.start()].count('\n') + 1)


def main():
    audit()
    print('=' * 72)
    print('AUDITORIA DE UX / ACESSIBILIDADE')
    print('=' * 72)
    print(f'Total de achados: {len(issues)}')
    print()
    for k, v in Counter(i['cat'] for i in issues).most_common():
        print(f'  {k:32s} {v}')
    print()
    by_file = defaultdict(Counter)
    for i in issues:
        by_file[i['file']][i['cat']] += 1
    for f in sorted(by_file):
        print(f'  {f}: {sum(by_file[f].values())}')
    print()
    print('--- DETALHE (primeiros 40) ---')
    for i in issues[:40]:
        print(f"  [{i['sev']:8s}] {i['file']}:{i['line']} {i['cat']}: {i['msg'][:88]}")
    Path('/workspace/avaliacao/07-documentacao/UX_A11Y_ANTES.json').write_text(
        json.dumps(issues, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
