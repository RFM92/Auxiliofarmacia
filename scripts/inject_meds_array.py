#!/usr/bin/env python3
"""
Injeta o array `meds` INTEGRO (61 medicamentos) nos builds que o perderam.

Fonte integra: /tmp/bk-free2.html (build FREE, array `const meds = [...]` com
61 itens corretamente fechados).

Destino: substitui o trecho `window.meds = [...]` / `const meds = [...]` pelo
array integro, expondo `window.meds = meds;` para o escopo global.
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
SOURCE = '/tmp/bk-free2.html'
FILES = [
    'dashboard-auxfarmacia.html',
    'dashboard-auxfarmacia-FREE.html',
    'dashboard-auxfarmacia-PRO.html',
    'dashboard-auxfarmacia-PREMIUM.html',
    'dashboard-auxfarmacia-ENTERPRISE.html',
    'dashboard-auxfarmacia-educativo.html',
]


def scan_array(src, start):
    """start = pos do '['; retorna pos apos o ']' correspondente."""
    depth = 0
    i = start
    n = len(src)
    in_s = None
    in_tpl = False
    while i < n:
        ch = src[i]
        if in_s:
            if ch == '\\':
                i += 2
                continue
            if ch == in_s:
                in_s = None
            i += 1
            continue
        if in_tpl:
            if ch == '\\':
                i += 2
                continue
            if ch == '`':
                in_tpl = False
            i += 1
            continue
        if ch in ('"', "'"):
            in_s = ch
            i += 1
            continue
        if ch == '`':
            in_tpl = True
            i += 1
            continue
        if src.startswith('//', i):
            j = src.find('\n', i)
            i = n if j == -1 else j
            continue
        if src.startswith('/*', i):
            j = src.find('*/', i + 2)
            i = n if j == -1 else j + 2
            continue
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def main():
    src = Path(SOURCE).read_text(encoding='utf-8')
    m = re.search(r'(?m)^(\s*)const meds\s*=\s*\[', src)
    if not m:
        print('FONTE: array meds nao encontrado'); return
    br = src.index('[', m.start())
    end = scan_array(src, br)
    arr = src[br:end]
    ids = re.findall(r'\bid:\s*"([^"]+)"', arr)
    print(f'FONTE: {len(ids)} medicamentos extraidos')
    if len(ids) != 61:
        print('ERRO: esperado 61'); return

    for name in FILES:
        p = OUT / name
        c = p.read_text(encoding='utf-8')
        mm = re.search(r'(?m)^([ \t]*)(?:const meds|window\.meds)\s*=\s*\[', c)
        if not mm:
            print(f'{name}: array meds nao encontrado'); continue
        br2 = c.index('[', mm.start())
        end2 = scan_array(c, br2)
        subst = (f'{mm.group(1)}const meds = {arr};\n\n'
                 f'{mm.group(1)}window.meds = meds;')
        c = c[:mm.start()] + subst + c[end2:]
        p.write_text(c, encoding='utf-8')
        print(f'{name}: array meds substituido ({len(ids)} meds) + window.meds = meds')


if __name__ == '__main__':
    main()
