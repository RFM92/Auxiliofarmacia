#!/usr/bin/env python3
"""
Fixes residuais aplicados DEPOIS do pipeline principal:
  1. Template literal do player de video: falta um ')' -> SyntaxError
  2. Array `cursos` (video manager) sem ']'
  3. `const meds = [...]` dentro de IIFE -> expor window.meds + garantir 61 meds
  4. `meds` sem prefixo window. no handler DOMContentLoaded
  5. `curso.priceOld.toFixed(2)` -> guarda para cursos sem priceOld
  6. `selectBillingCycle` inexistente (FREE)
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

EXTRAS = '/tmp/extras_meds.txt'


def main():
    extras = Path(EXTRAS).read_text(encoding='utf-8') if Path(EXTRAS).exists() else ''

    for name in FILES:
        p = OUT / name
        c = p.read_text(encoding='utf-8')
        n = {}

        # 1) template literal: ')' faltando
        old = "][moduleAtivoIdx % 11])}?rel=0"
        new = "][moduleAtivoIdx % 11]))}?rel=0"
        n['template_paren'] = c.count(old)
        c = c.replace(old, new)

        # 2) array `cursos` sem fechamento
        old2 = re.compile(r"(const cursos = \[\n(?:[^\n]*\n)*?)(\n\s*\];\n(?:\s*\];\n)?\s*let html = '';)")
        c, n2 = old2.subn(r"\1\2", c)
        n['cursos_array'] = n2
        # se ainda nao fecha, insere
        if 'const cursos = [' in c and not re.search(r"const cursos = \[[\s\S]{0,400}?\];\n\s*let html", c):
            c, n3 = re.subn(r"(const cursos = \[\n(?:[^\n]*\n)*?)(\n\s*let html = '';)", r"\1\n  ];\2", c)
            n['cursos_inserido'] = n3

        # 3) const meds dentro de IIFE -> const + window.meds = meds
        m = re.search(r'(?m)^(\s*)(?:const meds|window\.meds)\s*=\s*(\[[\s\S]*?\n\s*\])\s*;', c)
        if m and 'window.meds = meds;' not in c:
            arr = m.group(2)
            ids = re.findall(r'\bid:\s*"([^"]+)"', arr)
            faltam = []
            if 'cetoprofeno-20' not in ids and extras:
                faltam.append(extras)
            if faltam:
                ind = m.group(1) or '      '
                # normaliza os extras para a indentacao do array
                ex = []
                for l in extras.split('\n'):
                    ex.append((ind + '  ' + l.strip()) if l.strip() else l)
                extras_ok = '\n'.join(ex)
                corpo = arr.rstrip()
                corpo = corpo[:-1].rstrip().rstrip(',') + ',\n' + extras_ok + '\n' + ind + ']'
            else:
                corpo = arr
            subst = f'{m.group(1)}const meds = {corpo};\n\nwindow.meds = meds;'
            c = c[:m.start()] + subst + c[m.end():]
            n['meds_exposto'] = 1
            n['meds_total'] = len(re.findall(r'\bid:\s*"', corpo))
        elif m:
            n['meds_exposto'] = 0
            n['meds_total'] = len(re.findall(r'\bid:\s*"', m.group(2)))

        # 4) meds sem window. no DOMContentLoaded
        old4 = """  if (typeof MEDS_DROGARIA !== 'undefined' && Array.isArray(MEDS_DROGARIA)) {
    const existe = meds.find(m => m.id === 'sinvastatina');
    if (!existe) {
      meds.push(...MEDS_DROGARIA);
    }
  }"""
        new4 = """  if (typeof MEDS_DROGARIA !== 'undefined' && Array.isArray(MEDS_DROGARIA)) {
    const listaMeds = (typeof window.meds !== 'undefined' && Array.isArray(window.meds)) ? window.meds : [];
    const existe = listaMeds.find(m => m.id === 'sinvastatina');
    if (!existe) {
      listaMeds.push(...MEDS_DROGARIA);
      window.meds = listaMeds;
    }
  }"""
        n['meds_sem_window'] = c.count(old4)
        c = c.replace(old4, new4)

        # 5) priceOld guard
        old5 = "R$ ${curso.priceOld.toFixed(2).replace('.', ',')}"
        new5 = "R$ ${(curso.priceOld ?? curso.priceIndividual ?? curso.price ?? 0).toFixed(2).replace('.', ',')}"
        n['priceOld'] = c.count(old5)
        c = c.replace(old5, new5)

        # 5b) currentUser/currentPlan sem prefixo window.
        old5b = "  if (!currentUser || currentPlan === 'free') return;"
        new5b = "  if (!window.currentUser || window.currentPlan === 'free') return;"
        n['currentUser_guard'] = c.count(old5b)
        c = c.replace(old5b, new5b)
        c = c.replace("${currentPlan.toUpperCase()}", "${(window.currentPlan || 'free').toUpperCase()}")
        c = c.replace("badge.title = `Plano ${currentPlan} ativo",
                      "badge.title = `Plano ${window.currentPlan || 'free'} ativo")

        # 6) selectBillingCycle
        old6 = '        selectBillingCycle(btn.dataset.cycle);'
        new6 = "        if (typeof selectBillingCycle === 'function') selectBillingCycle(btn.dataset.cycle);"
        n['selectBillingCycle'] = c.count(old6)
        c = c.replace(old6, new6)

        p.write_text(c, encoding='utf-8')
        print(f'{name}: {n}')


if __name__ == '__main__':
    main()
