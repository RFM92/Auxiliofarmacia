#!/usr/bin/env python3
"""
Correcao de CONTRASTE (WCAG AA) com parsing real de regras CSS.

Para cada regra CSS { seletor { ... } }:
  - le a propriedade `color` e a `background`/`background-color` da MESMA regra
  - se o ratio < 4.5:1:
      * texto branco sobre fundo medio -> ESCURECE o fundo (mesmo matiz)
      * caso contrario -> ajusta a cor do TEXTO (mesmo matiz)
  - se a regra nao define `color`, herda: nao mexe (evita falso positivo)

Uso: python3 fix_contrast_css.py [--dry]
"""
import re
import glob
import os
import shutil
import colorsys
from pathlib import Path
from collections import Counter

OUT = Path('/workspace/output')
BACKUP = Path('/workspace/backup_pre_contrast')
TARGET = 4.5
DRY = '--dry' in __import__('sys').argv


def hex2rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6 or not re.match(r'^[0-9a-fA-F]{6}$', h):
        return None
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(rgb):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(round(v)))) for v in rgb)


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


def adjust(fg_hex, bg_hex, target=TARGET, escurecer_fundo=False):
    """Ajusta fg (ou bg) mantendo o matiz ate atingir o ratio alvo."""
    fg = hex2rgb(fg_hex)
    bg = hex2rgb(bg_hex)
    if not fg or not bg:
        return None, None
    base = bg if escurecer_fundo else fg
    r, g, b = [v / 255 for v in base]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    bg_lum = lum(bg)
    if escurecer_fundo:
        direcao = -1
    else:
        direcao = +1 if bg_lum < 0.35 else -1
    melhor = None
    for s2 in (s, s * 0.85, s * 0.6, s * 0.4, 0.0):
        for step in range(0, 101):
            nl = max(0.0, min(1.0, l + direcao * step * 0.01))
            nr, ng, nb = colorsys.hls_to_rgb(h, nl, s2)
            cand = (nr * 255, ng * 255, nb * 255)
            r2 = ratio(cand, bg) if escurecer_fundo else ratio(cand, bg)
            if r2 >= target:
                melhor = rgb2hex(cand)
                break
            melhor = rgb2hex(cand)
        if melhor and ratio(hex2rgb(melhor), bg) >= target:
            break
    if not melhor:
        return None, None
    if escurecer_fundo:
        return fg_hex, melhor
    return melhor, bg_hex


RULE = re.compile(r'([^{}]+)\{([^{}]*)\}', re.S)


def process(c, nome):
    """Processa todas as regras CSS e ajusta contraste."""
    stats = Counter()
    mudou = False

    def sub_regra(m):
        nonlocal mudou
        seletor, corpo = m.group(1), m.group(2)
        cm = re.search(r'(?i)(?:^|;|\s)color\s*:\s*(#[0-9a-fA-F]{3,6})\s*(?:;|!important)?', corpo)
        if not cm:
            return m.group(0)
        fg_hex = cm.group(1)
        fg = hex2rgb(fg_hex)
        if not fg:
            return m.group(0)
        bm = re.search(r'(?i)(?:^|;|\s)background(?:-color)?\s*:\s*([^;]+)', corpo)
        if not bm:
            return m.group(0)
        bg_hex = None
        for cand in re.findall(r'#[0-9a-fA-F]{3,6}', bm.group(1)):
            if hex2rgb(cand):
                bg_hex = cand
                break
        if not bg_hex:
            return m.group(0)
        bg = hex2rgb(bg_hex)
        if not bg:
            return m.group(0)
        if fg_hex.lower() == bg_hex.lower():
            return m.group(0)   # falso positivo do heuristico
        r = ratio(fg, bg)
        if r >= TARGET:
            return m.group(0)

        eh_branco = fg_hex.lower() in ('#fff', '#ffffff')
        # texto branco -> escurece o fundo; senao ajusta o texto
        novo_fg, novo_bg = adjust(fg_hex, bg_hex, TARGET, escurecer_fundo=eh_branco)
        if not novo_fg or not novo_bg:
            return m.group(0)
        if novo_fg.lower() == fg_hex.lower() and novo_bg.lower() == bg_hex.lower():
            return m.group(0)
        novo_corpo = corpo
        if novo_fg.lower() != fg_hex.lower():
            novo_corpo = novo_corpo.replace(fg_hex, novo_fg, 1)
            stats['texto_ajustado'] += 1
        if novo_bg.lower() != bg_hex.lower():
            # substitui apenas a 1a ocorrencia dentro do background
            def repb(mm):
                return mm.group(0).replace(bg_hex, novo_bg, 1)
            novo_corpo = re.sub(r'(?i)(background(?:-color)?\s*:\s*[^;{}]*)', repb, novo_corpo, count=1)
            stats['fundo_ajustado'] += 1
        mudou = True
        return seletor + '{' + novo_corpo + '}'

    novo_c = RULE.sub(sub_regra, c)
    return novo_c, stats, mudou


def main():
    files = [f for f in sorted(glob.glob(str(OUT / '*.html')))
             if not re.search(r'(debug|test-|diag-|check-|show-meds|force-meds|load\.html|dashboard-FREE|dashboard-free-v2|VISUALIZAR)', os.path.basename(f))]
    if not DRY:
        BACKUP.mkdir(parents=True, exist_ok=True)
    total = Counter()
    for p in files:
        nome = os.path.basename(p)
        c = Path(p).read_text(encoding='utf-8', errors='replace')
        if not DRY:
            shutil.copy(p, BACKUP / nome)
        novo, stats, mudou = process(c, nome)
        if mudou and not DRY:
            Path(p).write_text(novo, encoding='utf-8')
        total += stats
        print(f'{nome}: ' + (', '.join(f'{k}={v}' for k, v in stats.items()) if stats else 'sem mudanca'))
    print('\nTOTAIS: ' + ', '.join(f'{k}={v}' for k, v in total.items()))


if __name__ == '__main__':
    main()
