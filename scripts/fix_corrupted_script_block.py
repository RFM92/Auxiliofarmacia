#!/usr/bin/env python3
"""
CORRECAO: Remove bloco <script> corrompido que contem:
  - array meds de 61 itens injetado no meio do codigo
  - <!DOCTYPE html>/<html>/<head> duplicados
  - copia parcial do AUTH SYNC

O bloco #5 e uma copia corrompida do bloco #6 (versao integra).
Remover o #5 restaura a integridade sintatica e elimina duplicatas.
"""
import re
import os
from pathlib import Path

FILES = [
    'dashboard-auxfarmacia.html',
    'dashboard-auxfarmacia-PRO.html',
    'dashboard-auxfarmacia-PREMIUM.html',
    'dashboard-auxfarmacia-ENTERPRISE.html',
    'dashboard-auxfarmacia-educativo.html',
]

OUT = Path('/workspace/output')
DOCTYPE_RE = re.compile(r'<script(?![^>]*\bsrc=)[^>]*>(?:(?!</script>).)*?<!DOCTYPE', re.S | re.I)


def find_corrupt_block(c):
    """Localiza o bloco script corrompido (contem DOCTYPE interno)."""
    for i, m in enumerate(re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', c, re.S | re.I)):
        if '<!DOCTYPE' in m.group(1):
            return i, m
    return None, None


def main():
    for name in FILES:
        p = OUT / name
        c = p.read_text(encoding='utf-8')
        if '<!DOCTYPE' not in c:
            print(f'{name}: ja limpo')
            continue

        idx, m = find_corrupt_block(c)
        if m is None:
            print(f'{name}: nao achei bloco corrompido')
            continue

        # remove do <script> ate o </script> correspondente (inclusive)
        start = m.start()
        end = m.end()
        removed = c[start:end]
        newc = c[:start] + c[end:]

        # remove linhas em branco duplicadas ao redor
        newc = re.sub(r'\n{4,}', '\n\n\n', newc)

        p.write_text(newc, encoding='utf-8')

        # verifica
        doctypes = len(re.findall(r'<!DOCTYPE', newc))
        scripts = list(re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', newc, re.S | re.I))
        internal = sum(1 for b in scripts if '<!DOCTYPE' in b.group(1))
        print(f'{name}:')
        print(f'   removido bloco #{idx} ({len(removed)}b)')
        print(f'   DOCTYPEs restantes: {doctypes} | blocos com DOCTYPE interno: {internal}')
        print(f'   tamanho: {len(c)} -> {len(newc)}')


if __name__ == '__main__':
    main()
