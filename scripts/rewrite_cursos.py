#!/usr/bin/env python3
"""
Reparo CIRURGICO do array `const CURSOS = [...]` (baseado em LINHAS).

1) Remove linhas '{' orfas: antes de cada `id: 'xxx',` deve haver exatamente
   UMA linha contendo apenas '{'.
2) Insere o '];' de fechamento apos o objeto do ultimo curso
   (id: 'institucional_cursos'), se faltar.

Nao substitui nenhum trecho do arquivo.
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
FILES = [
    'dashboard-auxfarmacia.html',
    'dashboard-auxfarmacia-FREE.html',
    'dashboard-auxfarmacia-PRO.html',
    'dashboard-auxfarmacia-PREMIUM.html',
    'dashboard-auxfarmacia-ENTERPRISE.html',
    'dashboard-auxfarmacia-educativo.html',
]
CURSOS_IDS = ['antihipertensivos', 'diabeticos', 'trilha_completa', 'institucional_cursos']


def so_chave(linha):
    s = linha.strip()
    return s == '{'


def remove_chaves_orfas(c):
    """Remove linhas '{' extras antes de cada id de curso."""
    removidas = 0
    linhas = c.split('\n')
    saida = []
    i = 0
    n = len(linhas)
    while i < n:
        l = linhas[i]
        # detecta inicio de curso: linha com id: 'xxx'
        m = re.match(r"^\s*id:\s*'(?:" + '|'.join(CURSOS_IDS) + r")',", l)
        if not m:
            saida.append(l)
            i += 1
            continue
        # conta linhas '{' imediatamente anteriores em `saida`
        k = len(saida) - 1
        while k >= 0 and so_chave(saida[k]):
            k -= 1
        braces = list(range(k + 1, len(saida)))
        # mantem apenas a ultima (a que abre o objeto)
        for b in braces[:-1]:
            saida[b] = None
            removidas += 1
        saida = [x for x in saida if x is not None]
        saida.append(l)
        i += 1
    return '\n'.join(saida), removidas


def scan_obj_end(src, pos):
    depth = 0
    i = pos
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
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def main():
    for name in FILES:
        p = OUT / name
        c = p.read_text(encoding='utf-8')
        if 'const CURSOS = [' not in c:
            print(f'{name}: sem CURSOS')
            continue

        c, removidas = remove_chaves_orfas(c)

        # insere '];' apos o objeto do ultimo curso
        i = c.index('const CURSOS = [')
        m = re.search(r"id:\s*'institucional_cursos'", c[i:])
        if not m:
            print(f'{name}: institucional_cursos nao encontrado')
            continue
        idpos = i + m.start()
        k = idpos
        while k > 0 and c[k] != '{':
            k -= 1
        fim_obj = scan_obj_end(c, k)
        if re.match(r'\s*\];', c[fim_obj:fim_obj + 12]):
            status = 'ja fechava'
        else:
            c = c[:fim_obj] + '\n];' + c[fim_obj:]
            status = ']; inserido'

        p.write_text(c, encoding='utf-8')
        print(f'{name}: {removidas} chave(s) orfa(s) removida(s), {status}')


if __name__ == '__main__':
    main()
