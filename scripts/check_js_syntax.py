#!/usr/bin/env python3
"""Valida a sintaxe JS de todos os <script> inline dos HTMLs."""
import re, os, glob, sys
from pathlib import Path
import subprocess

OUT = Path('/workspace/output')
TMP = Path('/tmp/jschk'); TMP.mkdir(exist_ok=True)
total = 0; err = 0
for f in sorted(glob.glob(str(OUT / '*.html'))):
    c = Path(f).read_text(encoding='utf-8', errors='replace')
    for i, m in enumerate(re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', c, re.S | re.I)):
        code = m.group(1)
        if len(code.strip()) < 10:
            continue
        p = TMP / (Path(f).stem + '_' + str(i) + '.js')
        p.write_text(code, encoding='utf-8')
        r = subprocess.run(['node', '--check', str(p)], capture_output=True, text=True)
        total += 1
        if r.returncode != 0:
            err += 1
            first = [l for l in r.stderr.split('\n') if 'Error' in l]
            print('  ERRO', Path(f).name, (first[0][:110] if first else r.stderr[:110]))
print(f'blocos: {total} | com erro: {err} | arquivos OK: {len(glob.glob(str(OUT/"*.html"))) - (1 if err else 0)}')
