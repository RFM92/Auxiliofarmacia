#!/usr/bin/env python3
"""
Detecta e corrige CSS que ficou FORA de qualquer <style> (renderizado como texto).

Sintoma: no HTML aparece texto como ".site-header-center { flex: 1; ... }" na pagina.

Causa: um <style> de abertura foi removido/duplicado em algum passo de build.

Deteccao: segmenta o HTML em blocos (script/style/texto). Se um bloco de TEXTO
contem >= 8 seletores CSS ("algo {"), esse trecho e CSS orfao.
Correcao: envolve o trecho em <style>...</style>.
"""
import re
import glob
import os
from pathlib import Path

OUT = Path('/workspace/output')

SPLIT = re.compile(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)', re.S | re.I)
CSS_SEL = re.compile(r'(?m)^[ \t]*[.#a-zA-Z\[][^{}\n]{0,80}\{[ \t]*$')


def find_orphan_css(c):
    """Retorna [(ini, fim)] de trechos de CSS orfao no texto."""
    out = []
    pos = 0
    for m in SPLIT.finditer(c):
        seg = c[pos:m.start()]
        if seg.strip():
            # conta seletores CSS no trecho
            hits = [x for x in CSS_SEL.finditer(seg)]
            if len(hits) >= 8:
                ini = pos + hits[0].start()
                # encontra o fim: ultimo '}' antes do proximo marcador
                fim_bloco = pos + hits[-1].start()
                k = c.find('}', fim_bloco)
                if k != -1:
                    out.append((ini, k + 1))
        pos = m.end()
    # trecho final (apos o ultimo marcador)
    seg = c[pos:]
    if seg.strip():
        hits = list(CSs := CSS_SEL.finditer(seg))
        if len(hits) >= 8:
            ini = pos + hits[0].start()
            k = c.find('}', pos + hits[-1].start())
            if k != -1:
                out.append((ini, k + 1))
    return out


def main():
    total = 0
    for p in sorted(OUT.glob('*.html')):
        c = p.read_text(encoding='utf-8', errors='replace')
        regions = find_orphan_css(c)
        if not regions:
            continue
        for ini, fim in reversed(regions):
            bloco = c[ini:fim]
            if '<style' in bloco or '</style' in bloco:
                continue
            c = c[:ini] + '<style>\n' + bloco + '\n</style>' + c[fim:]
        p.write_text(c, encoding='utf-8')
        total += len(regions)
        print(f'{p.name}: {len(regions)} bloco(s) de CSS orfao(s) envolvido(s) em <style>')
    print(f'\nTotal: {total}')


if __name__ == '__main__':
    main()
