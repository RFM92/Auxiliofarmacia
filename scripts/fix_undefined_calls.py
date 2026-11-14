#!/usr/bin/env python3
"""
CORRECAO: Protege chamadas de funcoes que podem nao existir.

Impacto: bootstrapPremiumV6() chama initTema()/initRipple()/init3DTilt()/
initThemeSelector() que NAO existem. Sem try/catch, o ReferenceError aborta o
handler DOMContentLoaded inteiro -> applyPaywall, renderAll, initLicense,
initComparador, initTelemetry NUNCA executam.

Correcao: envolver cada chamada em `typeof X === 'function' ? X() : null`,
padrao ja usado em todo o restante do codigo.
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')

# funcoes chamadas diretamente (sem guarda) que nao existem no arquivo
TARGETS = [
    'initTema', 'initRipple', 'init3DTilt', 'initThemeSelector',
    'createSparkle', 'showLoginModal', 'markVideoWatched',
    'checkFirstVisit', 'addProBadgeToHeader',
]

FILES = sorted(p.name for p in OUT.glob('*.html'))


def main():
    total = 0
    for name in FILES:
        p = OUT / name
        c = p.read_text(encoding='utf-8', errors='replace')
        orig = c
        applied = []

        for fn in TARGETS:
            # so protege se a funcao realmente NAO existir no arquivo
            if re.search(r'function\s+\*?\s*' + re.escape(fn) + r'\s*\(', c):
                continue
            if re.search(r'window\.' + re.escape(fn) + r'\s*=', c):
                continue

            # 1. chamada simples:  fn();   ->  if (typeof fn === 'function') fn();
            pat1 = re.compile(r'(?<![\w.$])' + re.escape(fn) + r'\(\s*\)\s*;')
            c, n1 = pat1.subn(lambda m: "if (typeof %s === 'function') %s();" % (fn, fn), c)

            # 2. setTimeout(fn, N)  ->  setTimeout(() => { if (typeof fn === 'function') fn(); }, N)
            pat2 = re.compile(r'setTimeout\(\s*' + re.escape(fn) + r'\s*,\s*')
            c, n2 = pat2.subn('setTimeout(() => { if (typeof %s === \'function\') %s(); }, ' % (fn, fn), c)

            # 3. handler inline: onclick="fn()"  ->  onclick="if (typeof fn === 'function') fn()"
            pat3 = re.compile(r'(on(?:click|change|input|submit)=")' + re.escape(fn) + r'\(\)')
            c, n3 = pat3.subn(r'\1if (typeof %s === \'function\') %s()' % (fn, fn), c)

            if n1 or n2 or n3:
                applied.append(f'{fn}({n1+n2+n3})')
                total += n1 + n2 + n3

        if c != orig:
            p.write_text(c, encoding='utf-8')
            print(f'{name}: ' + ', '.join(applied))
    print(f'\nTotal de chamadas protegidas: {total}')


if __name__ == '__main__':
    main()
