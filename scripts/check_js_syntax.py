#!/usr/bin/env python3
"""
Valida a sintaxe JS de todos os <script> inline dos HTMLs do site.

    python3 scripts/check_js_syntax.py
"""
import re
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import SITE, RAIZ, html_files  # noqa: E402

TMP = Path(os.environ.get('TMPDIR', '/tmp')) / 'jschk_auxfarmacia'
TMP.mkdir(parents=True, exist_ok=True)


def main():
    alvos = html_files()
    if not alvos:
        print('Nenhum HTML encontrado em', SITE)
        return 0

    total = 0
    erros = 0
    for f in alvos:
        c = f.read_text(encoding='utf-8', errors='replace')
        for i, m in enumerate(re.finditer(
                r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', c, re.S | re.I)):
            code = m.group(1)
            if len(code.strip()) < 10:
                continue
            p = TMP / f'{f.stem}_{i}.js'
            p.write_text(code, encoding='utf-8')
            r = subprocess.run(['node', '--check', str(p)],
                               capture_output=True, text=True)
            total += 1
            if r.returncode != 0:
                erros += 1
                linha = c[:m.start()].count('\n') + 1
                print(f'  ERRO {f.name}:{linha}')
                for l in r.stderr.split('\n')[:4]:
                    if l.strip():
                        print('     ', l[:150])

    print(f'blocos: {total} | com erro: {erros} | arquivos OK: {len(alvos)}')
    return 1 if erros else 0


if __name__ == '__main__':
    sys.exit(main())
