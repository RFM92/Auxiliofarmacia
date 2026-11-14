#!/usr/bin/env python3
"""
Scanner linear de regras CSS + auditoria/fix de contraste WCAG AA.

Evita o backtracking catastrofico do regex ([^{}]+)\{([^{}]*)\}.
Processa apenas o conteudo dos blocos <style>.
"""
import re
import colorsys
from pathlib import Path

TARGET = 4.5


# ---------- cores ----------
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


def adjust(base_hex, bg_hex, target=TARGET, escurecer=False):
    """Ajusta base_hex (texto ou fundo) mantendo o matiz ate atingir o ratio."""
    base = hex2rgb(base_hex)
    bg = hex2rgb(bg_hex)
    if not base or not bg:
        return None
    r, g, b = [v / 255 for v in base]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    direcao = -1 if (escurecer or lum(bg) >= 0.35) else +1
    melhor = None
    for s2 in (s, s * 0.85, s * 0.6, s * 0.4, 0.0):
        achou = False
        for step in range(0, 101):
            nl = max(0.0, min(1.0, l + direcao * step * 0.01))
            nr, ng, nb = colorsys.hls_to_rgb(h, nl, s2)
            cand = (nr * 255, ng * 255, nb * 255)
            if ratio(cand, bg) >= target:
                melhor = rgb2hex(cand)
                achou = True
                break
            melhor = rgb2hex(cand)
        if achou:
            break
    return melhor


# ---------- scanner de regras ----------
def iter_style_blocks(c):
    """Retorna [(ini, fim)] do conteudo de cada <style>...</style>."""
    out = []
    for m in re.finditer(r'(?is)<style[^>]*>(.*?)</style>', c):
        out.append((m.start(1), m.end(1)))
    return out


def iter_css_rules(css, base=0):
    """Retorna [(sel_ini, sel_fim, body_ini, body_fim, inicio_regra)] linear."""
    n = len(css)
    i = 0
    while i < n:
        j = css.find('{', i)
        if j == -1:
            break
        k = css.find('}', j)
        if k == -1:
            break
        sel = css[i:j]
        body = css[j + 1:k]
        # ignora blocos que parecem JS (objeto literal / template)
        if 'function' in sel or '=>' in sel or ';' in sel.strip():
            i = k + 1
            continue
        yield (base + i, base + j, base + j + 1, base + k, base + i)
        i = k + 1


def analyze_contrast(c):
    """Retorna lista de problemas de contraste (sem alterar nada)."""
    probs = []
    for si, sf in iter_style_blocks(c):
        css = c[si:sf]
        for sel_i, sel_j, b_i, b_j, rule_i in iter_css_rules(css, si):
            body = c[b_i:b_j]
            cm = re.search(r'(?i)(?:^|;|\s)color\s*:\s*(#[0-9a-fA-F]{3,6})', body)
            if not cm:
                continue
            fg_hex = cm.group(1)
            fg = hex2rgb(fg_hex)
            if not fg:
                continue
            bm = re.search(r'(?i)(?:^|;|\s)background(?:-color)?\s*:\s*([^;]+)', body)
            if not bm:
                continue
            bg_hex = None
            for cand in re.findall(r'#[0-9a-fA-F]{3,6}', bm.group(1)):
                if hex2rgb(cand):
                    bg_hex = cand
                    break
            if not bg_hex:
                continue
            bg = hex2rgb(bg_hex)
            if not bg or fg_hex.lower() == bg_hex.lower():
                continue
            r = ratio(fg, bg)
            if r < TARGET:
                probs.append({
                    'ratio': round(r, 2), 'fg': fg_hex, 'bg': bg_hex,
                    'color_pos': b_i + cm.start(1),
                    'bg_pos': b_i + bm.start(1),
                    'line': c[:b_i + cm.start(1)].count('\n') + 1,
                })
    return probs


def fix_contrast(c):
    """Ajusta contraste. Retorna (c, n_ajustes, n_restantes)."""
    total = 0
    for _ in range(12):
        probs = analyze_contrast(c)
        if not probs:
            break
        # corrige o primeiro de cada vez (reposiciona offsets)
        p = probs[0]
        fg_branco = p['fg'].lower() in ('#fff', '#ffffff')
        if fg_branco:
            novo_bg = adjust(p['bg'], p['bg'], TARGET, escurecer=True)
            if not novo_bg or novo_bg.lower() == p['bg'].lower():
                # nao da para escurecer mais: marca para pular
                c = c[:p['color_pos']] + ('#__SKIP__') + c[p['color_pos'] + len(p['fg']):]
                continue
            c = c[:p['bg_pos']] + novo_bg + c[p['bg_pos'] + len(p['bg']):]
        else:
            novo_fg = adjust(p['fg'], p['bg'], TARGET, escurecer=False)
            if not novo_fg or novo_fg.lower() == p['fg'].lower():
                c = c[:p['color_pos']] + ('#__SKIP__') + c[p['color_pos'] + len(p['fg']):]
                continue
            c = c[:p['color_pos']] + novo_fg + c[p['color_pos'] + len(p['fg']):]
        total += 1
    # remove marcadores de skip
    c = c.replace('#__SKIP__', '#ffffff')
    return c, total, len(analyze_contrast(c))
