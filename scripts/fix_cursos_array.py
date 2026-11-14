#!/usr/bin/env python3
"""
CORRECAO v4 (deterministica): Repara `const CURSOS = [...]`.

Processa o array linha a linha:
  - Remove linhas `{` orfas (mantem exatamente 1 antes de cada `id:`)
  - Garante o fechamento `];`
"""
import re
from pathlib import Path

FILES = [
    'dashboard-auxfarmacia.html',
    'dashboard-auxfarmacia-FREE.html',
    'dashboard-auxfarmacia-PRO.html',
    'dashboard-auxfarmacia-PREMIUM.html',
    'dashboard-auxfarmacia-ENTERPRISE.html',
    'dashboard-auxfarmacia-educativo.html',
]

OUT = Path('/workspace/output')
KEY = 'const CURSOS = ['
RE_OBJ = re.compile(r"^[ \t]*\{[ \t]*$")
RE_ID = re.compile(r"^[ \t]*id:[ \t]*'")


def repair(path):
    p = OUT / path
    c = p.read_text(encoding='utf-8')
    if KEY not in c:
        return f'{path}: sem CURSOS'

    i = c.index(KEY)
    j = c.index('];', i) + 2
    arr = c[i:j]
    ls = arr.split('\n')

    drop = set()
    removed = 0
    added = 0
    for n, l in enumerate(ls):
        if not RE_ID.match(l):
            continue
        # linhas consecutivas so com '{' imediatamente antes
        k = n - 1
        braces = []
        while k >= 0 and RE_OBJ.match(ls[k]):
            braces.append(k)
            k -= 1
        if braces:
            # mantém a última (mais próxima do id), remove as demais
            for b in braces[:-1]:
                drop.add(b)
                removed += 1

    newls = [l for n, l in enumerate(ls) if n not in drop]
    newarr = '\n'.join(newls)
    # normaliza: garante `];` no fim
    newarr = re.sub(r'[\s\];]*$', '\n];', newarr)

    c = c[:i] + newarr + c[j:]
    p.write_text(c, encoding='utf-8')
    return f'{path}: {removed} chaves orfas removidas'


def main():
    for f in FILES:
        print(repair(f))

    print('\n--- validacao ---')
    for f in FILES:
        c = (OUT / f).read_text(encoding='utf-8')
        i = c.index(KEY)
        j = c.index('];', i) + 2
        arr = c[i:j]
        ls = arr.split('\n')
        ok = True
        info = []
        for n, l in enumerate(ls):
            if RE_ID.match(l):
                prev = ls[n - 1] if n > 0 else ''
                if not RE_OBJ.match(prev):
                    ok = False
                    info.append(f'linha {n} sem abertura')
        ids = re.findall(r"id:[ \t]*'([^']+)'", arr)
        opens = sum(1 for l in ls if RE_OBJ.match(l))
        print(f'{f}: abre={opens} fecha={sum(1 for l in ls if l.strip() in ("}", "},"))} '
              f'ids={len(ids)} estrutura_ok={ok} {info if info else ""}')


if __name__ == '__main__':
    main()
