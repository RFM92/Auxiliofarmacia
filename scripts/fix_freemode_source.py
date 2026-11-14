#!/usr/bin/env python3
"""
CORRECAO: o paywall so olhava `auxf_license` para decidir o modo.
Quem loga pela tela de acesso (sessao) ficava SEMPRE em modo Free ->
as 12 classes Pro ficavam bloqueadas mesmo para quem contratou Pro/Premium.

Agora isFreeMode considera, em ordem:
  1) auxf_license  (licenca ativada por chave)
  2) auxf_session  (plano contratado no login)
  3) window.currentPlan (plano global em memoria)
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
FILES = sorted(OUT.glob('dashboard-auxfarmacia*.html'))

VELHO = """    const isFreeMode = (() => {
      try {
        const lic = localStorage.getItem('auxf_license');
        if (lic) {
          const parsed = JSON.parse(lic);
          return parsed.tier === 'free' || !parsed.tier;
        }
      } catch(e) {}
      return true;
    })();"""

NOVO = """    const isFreeMode = (() => {
      // 1) Licenca ativada por chave AUXFARMA-...
      try {
        const lic = localStorage.getItem('auxf_license');
        if (lic) {
          const parsed = JSON.parse(lic);
          if (parsed.tier && parsed.tier !== 'free') return false;
        }
      } catch(e) {}

      // 2) Plano contratado no login (tela de acesso unico)
      try {
        const sess = JSON.parse(localStorage.getItem('auxf_session') || 'null');
        if (sess && sess.plano && sess.plano !== 'free') return false;
      } catch(e) {}

      // 3) Plano global em memoria
      try {
        const p = (typeof window.currentPlan !== 'undefined') ? window.currentPlan : null;
        if (p && p !== 'free') return false;
      } catch(e) {}

      return true;
    })();"""

total = 0
for p in FILES:
    c = p.read_text(encoding='utf-8')
    if VELHO in c:
        c = c.replace(VELHO, NOVO)
        p.write_text(c, encoding='utf-8')
        total += 1
        print(f'{p.name}: isFreeMode corrigido')
    else:
        print(f'{p.name}: padrao nao encontrado (ja corrigido ou variante)')
print(f'\nTotal: {total}')
