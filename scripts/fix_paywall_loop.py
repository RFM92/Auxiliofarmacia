#!/usr/bin/env python3
"""
CORRECAO CRITICA: elimina loop infinito (100% CPU) no paywall de medicamentos Pro.

Causa:
  blockClicks() fazia `el.cloneNode(true)` + `el.parentNode.replaceChild(...)`
  a cada execucao. Como blockClicks() e chamado por um MutationObserver que
  observa `document.body { childList: true, subtree: true }`, cada replace
  dispara o observer -> blockClicks() -> replace ... = LOOP INFINITO.
  O renderer do navegador trava ("Unexpected renderer destruction").

Correcao:
  - Nao clonar/substituir mais. Marcar o elemento com data-paywall-blocked
    e registrar o listener uma unica vez.
  - Adicionar um guard no observer para nao reagir a mutacoes internas.
"""
import re
import glob
from pathlib import Path

OUT = Path('/workspace/output')

# corpo antigo (usa cloneNode + replaceChild)
VELHO = """        // Remove listeners antigos (se houver)
        const newEl = el.cloneNode(true);
        el.parentNode.replaceChild(newEl, el);

        // Adiciona novo listener
        newEl.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          showMedProPaywall(med);
        }, true);"""

NOVO = """        // Nao clonar/substituir: isso muta o DOM e dispara o MutationObserver
        // que chama esta funcao, causando loop infinito (renderer travado).
        // Em vez disso, marca o elemento e registra o listener uma unica vez.
        if (el.dataset.paywallBlocked === '1') return;
        el.dataset.paywallBlocked = '1';

        el.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          showMedProPaywall(med);
        }, true);"""

# guard no MutationObserver
VELHO_OBS = """      const obs = new MutationObserver(() => {
        applyLock();
        blockClicks();
      });"""
NOVO_OBS = """      let _paywallLockTimer = null;
      const obs = new MutationObserver(() => {
        // Debounce: evita reentrar em loop quando as proprias mudancas
        // (badge PRO, classe locked) dispararem o observer
        if (_paywallLockTimer) clearTimeout(_paywallLockTimer);
        _paywallLockTimer = setTimeout(() => {
          _paywallLockTimer = null;
          applyLock();
          blockClicks();
        }, 150);
      });"""


def main():
    total = 0
    for p in sorted(OUT.glob('dashboard-auxfarmacia*.html')):
        c = p.read_text(encoding='utf-8')
        orig = c
        n = 0
        c, k = re.subn(re.escape(VELHO), NOVO, c)
        n += k
        c, k = re.subn(re.escape(VELHO_OBS), NOVO_OBS, c)
        n += k
        if c != orig:
            p.write_text(c, encoding='utf-8')
            total += n
        print(f'{p.name}: {n} correcao(oes)')
    print(f'\nTotal: {total}')


if __name__ == '__main__':
    main()
