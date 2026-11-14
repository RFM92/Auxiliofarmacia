#!/usr/bin/env python3
"""
REPARO v2: reconstroi tags <script> de abertura removidas.

Padrao do dano: a tag <script> de abertura de cada bloco foi removida.
O bloco de codigo de cada segmento comeca logo apos o </script> anterior
(ignorando whitespace). Entao: segmenta por </script>; se o segmento nao
contem <script>, insere <script> no inicio do codigo (apos o whitespace).
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

TAG = re.compile(r'<script\b[^>]*>|</script>', re.I)
# tags <script> que aparecem DENTRO de strings JS (para nao contar)
IN_STRING = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"|`[^`]*`")


def main():
    for name in FILES:
        p = OUT / name
        c = p.read_text(encoding='utf-8')

        # 1) localiza os fechamentos e as aberturas REAIS (fora de strings JS)
        # Para simplicidade: um <script> so conta se estiver fora de literais.
        # Heuristica: tags <script> reais estao sempre no inicio de uma linha
        # ou precedidas de > ou whitespace no nivel do documento.
        # Vamos usar: <script no inicio da linha (com indentacao) OU precedido por >
        abre_real = [m.start() for m in re.finditer(r'(?m)^\s*<script\b[^>]*>', c)]
        # remove os que estao dentro de bloco de codigo (indentados + nao no topo do arquivo)
        fecha = [m.start() for m in re.finditer(r'(?m)^</script>', c)]

        if len(abre_real) >= len(fecha):
            print(f'{name}: ja balanceado ({len(abre_real)} / {len(fecha)})')
            continue

        # reconstroi: para cada fecha, encontra o </script> anterior
        segs = c.split('</script>')
        novo = segs[0]
        # a primeira parte pode ja ter <script>
        if not re.search(r'(?m)^\s*<script\b', segs[0]):
            novo = '<script>\n' + novo
        adicionados = 1 if novo != segs[0] else 0
        for s in segs[1:]:
            if not re.search(r'(?m)^\s*<script\b', s):
                # insere apos o whitespace inicial
                m = re.match(r'\s*', s)
                ini = m.end()
                s = s[:ini] + '<script>\n' + s[ini:]
                adicionados += 1
            novo += '</script>' + s

        p.write_text(novo, encoding='utf-8')
        a = len(re.findall(r'(?m)^\s*<script\b', novo))
        f = len(re.findall(r'(?m)^</script>', novo))
        print(f'{name}: {adicionados} tags inseridas -> abre={a} fecha={f}')


if __name__ == '__main__':
    main()
