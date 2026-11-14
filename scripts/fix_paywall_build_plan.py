#!/usr/bin/env python3
"""
Corrige o paywall por build de plano.

Problema: os dashboards PRO / PREMIUM / ENTERPRISE / educativo / master
aplicavam o bloqueio como se fossem o plano FREE, porque o `isFreeMode`
so olhava licenca, sessao e `window.currentPlan` (que, sem sessao, vale
'free'). Resultado: o plano pago continuava bloqueando 12 medicamentos Pro.

Correcao: cada dashboard declara o plano do proprio build em
`window.AUXF_BUILD_PLAN`, e o `isFreeMode` passa a consultar essa
fonte antes de cair em 'free'.

    python3 scripts/fix_paywall_build_plan.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = RAIZ / 'site'

PLANOS = {
    'dashboard-auxfarmacia.html': 'master',
    'dashboard-auxfarmacia-FREE.html': 'free',
    'dashboard-auxfarmacia-PRO.html': 'pro',
    'dashboard-auxfarmacia-PREMIUM.html': 'premium',
    'dashboard-auxfarmacia-ENTERPRISE.html': 'enterprise',
    'dashboard-auxfarmacia-educativo.html': 'educativo',
}

# planos que NUNCA sao free -> build pago liberando tudo
PAGOS = {'master', 'pro', 'premium', 'enterprise', 'institucional', 'educativo'}

DECL = """<script>
// ============================================================
// PLANO DESTE BUILD
// ============================================================
// Este arquivo e o build do plano "{plano}". O build pago libera
// o conteudo por si so, mesmo sem sessao (visitante / build avulso).
window.AUXF_BUILD_PLAN = '{plano}';
</script>
"""


def main() -> int:
    alterados = 0
    for arquivo, plano in PLANOS.items():
        p = SITE / arquivo
        if not p.exists():
            print(f'  ⚠️  {arquivo} nao encontrado')
            continue
        c = p.read_text(encoding='utf-8')
        antes = c

        # 1) declara o plano do build logo no inicio do <head>
        if 'window.AUXF_BUILD_PLAN' not in c:
            m = re.search(r'<head[^>]*>', c, re.I)
            if not m:
                print(f'  ❌ {arquivo}: sem <head>')
                continue
            c = c[:m.end()] + '\n' + DECL.format(plano=plano) + c[m.end():]

        # 2) isFreeMode: consulta o plano do build (fonte 4)
        if 'AUXF_BUILD_PLAN' not in c.split('isFreeMode')[-1][:1500]:
            antigo = """      // 3) Plano global em memoria
      try {
        const p = (typeof window.currentPlan !== 'undefined') ? window.currentPlan : null;
        if (p && p !== 'free') return false;
      } catch(e) {}

      return true;"""
            novo = """      // 3) Plano global em memoria
      try {
        const p = (typeof window.currentPlan !== 'undefined') ? window.currentPlan : null;
        if (p && p !== 'free') return false;
      } catch(e) {}

      // 4) PLANO DESTE BUILD (fonte mais forte): um build PRO/PREMIUM/
      //    ENTERPRISE/educativo/master libera o conteudo por si so,
      //    mesmo sem sessao (visita avulsa do build).
      try {
        const bp = (typeof window.AUXF_BUILD_PLAN !== 'undefined') ? window.AUXF_BUILD_PLAN : null;
        if (bp && bp !== 'free') return false;
      } catch(e) {}

      return true;"""
            if antigo in c:
                c = c.replace(antigo, novo)
            else:
                # fallback: insere antes do "return true;" do isFreeMode
                idx = c.find('const isFreeMode = (() => {')
                if idx != -1:
                    fim = c.find('return true;', idx)
                    if fim != -1:
                        bloco = """      // 4) PLANO DESTE BUILD (fonte mais forte)
      try {
        const bp = (typeof window.AUXF_BUILD_PLAN !== 'undefined') ? window.AUXF_BUILD_PLAN : null;
        if (bp && bp !== 'free') return false;
      } catch(e) {}

      """
                        c = c[:fim] + bloco + c[fim:]

        # 3) currentPlan: usa o plano do build como fallback (nao 'free')
        c = c.replace(
            "if (typeof window.currentPlan === 'undefined') window.currentPlan = 'free';",
            "if (typeof window.currentPlan === 'undefined') "
            "window.currentPlan = (typeof window.AUXF_BUILD_PLAN !== 'undefined') "
            "? window.AUXF_BUILD_PLAN : 'free';")
        c = c.replace(
            "window.currentPlan = session.plano || (user && user.plano) || 'free';",
            "window.currentPlan = session.plano || (user && user.plano) "
            "|| (typeof window.AUXF_BUILD_PLAN !== 'undefined' ? window.AUXF_BUILD_PLAN : 'free');")

        if c != antes:
            p.write_text(c, encoding='utf-8')
            alterados += 1
            print(f'  ✅ {arquivo}  (build={plano})')

    print(f'\n{alterados} dashboard(s) corrigido(s).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
