#!/usr/bin/env python3
"""Insere o '];' faltando em `const PRO_CLASSES = [...]` (cirurgico)."""
import re
from pathlib import Path

OUT = Path('/workspace/output')

for p in sorted(OUT.glob('dashboard-auxfarmacia*.html')):
    c = p.read_text(encoding='utf-8')
    if 'const PRO_CLASSES' not in c:
        print(f'{p.name}: sem PRO_CLASSES')
        continue

    # localiza a declaracao e a linha 'Estimulantes' que fecha a lista
    m = re.search(r"(?m)^([ \t]*)const PRO_CLASSES = \[", c)
    if not m:
        print(f'{p.name}: PRO_CLASSES nao encontrado')
        continue
    ini = m.end()
    # procura 'Estimulantes' apos
    m2 = re.search(r"(?m)^[ \t]*'Estimulantes'[ \t]*$", c[ini:ini + 2000])
    if not m2:
        print(f'{p.name}: \'Estimulantes\' nao encontrado')
        continue
    pos = ini + m2.end()   # logo apos a linha
    # ja fecha?
    if re.match(r'\s*\];', c[pos:pos + 12]):
        print(f'{p.name}: PRO_CLASSES ja fechado')
        continue
    indent = m.group(1)
    c = c[:pos] + '\n' + indent + '];' + c[pos:]
    p.write_text(c, encoding='utf-8')
    print(f'{p.name}: PRO_CLASSES fechado com ];')
