#!/usr/bin/env python3
"""
Remove tags <script>/</script> que estao DENTRO de codigo JS (inline).

Um bloco <script> inline tem o conteudo indentado (esta dentro de uma funcao).
Blocos legitimos de nivel de documento comecam na coluna 0.

Este script DEVE rodar DEPOIS do fix_loose_js (que pode reintroduzir inline).
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')

PAT = re.compile(
    r'(?m)^[ \t]*<script[^>]*>[ \t]*\n((?:[ \t]{2,}[^\n]*\n)+?)[ \t]*</script>[ \t]*\n'
)

for p in sorted(OUT.glob('dashboard-auxfarmacia*.html')):
    c = p.read_text(encoding='utf-8')
    novo, n = PAT.subn(r'\1', c)
    # tambem remove </script> inline sem <script> correspondente
    if n:
        p.write_text(novo, encoding='utf-8')
    print(f'{p.name}: {n} bloco(s) <script> inline removido(s)')
