#!/usr/bin/env python3
"""
Ajusta o aviso medico obrigatorio para ser menos intrusivo:
- Nao fica sticky (nao "corta" o conteudo)
- Dismissable (ja tem botao X)
- Auto-fecha depois de 8s
- Versao menor
"""
import re
from pathlib import Path

OUTPUT = Path("/workspace/output")
ALL_HTML = [
    "dashboard-auxfarmacia.html",
    "dashboard-auxfarmacia-FREE.html",
    "dashboard-auxfarmacia-PRO.html",
    "dashboard-auxfarmacia-PREMIUM.html",
    "dashboard-auxfarmacia-ENTERPRISE.html",
    "dashboard-auxfarmacia-educativo.html",
]

OLD_CSS = """  .medical-warning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-top: 3px solid #f59e0b;
    border-bottom: 1px solid #fbbf24;
    padding: 12px 24px;
    position: sticky;
    top: 64px;
    z-index: 9997;
    font-size: 13px;
    color: #78350f;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    text-align: center;
    font-weight: 500;"""

NEW_CSS = """  .medical-warning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-top: 3px solid #f59e0b;
    border-bottom: 1px solid #fbbf24;
    padding: 8px 24px;
    position: relative;
    z-index: 100;
    font-size: 12px;
    color: #78350f;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    text-align: center;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.3s, max-height 0.3s;
    max-height: 60px;
    overflow: hidden;"""

OLD_HTML = """<!-- ========== AVISO MÉDICO OBRIGATÓRIO ========== -->
<div class="medical-warning" id="medicalWarning">
  <span class="medical-warning-icon">⚠️</span>
  <span class="medical-warning-text">
    <strong>AVISO IMPORTANTE:</strong> Este site é apenas educativo e <strong>NÃO faz recomendação de uso de medicamentos</strong>.
    Sempre consulte um <strong>médico</strong> ou <strong>farmacêutico</strong> antes de usar qualquer medicação em crianças.
    Antibióticos e medicamentos controlados requerem prescrição médica.
  </span>
  <button class="medical-warning-close" onclick="document.getElementById('medicalWarning').style.display='none'" aria-label="Fechar aviso">×</button>
</div>"""

NEW_HTML = """<!-- ========== AVISO MÉDICO (COMPACTO + AUTO-DISMISS) ========== -->
<div class="medical-warning" id="medicalWarning" role="alert">
  <span class="medical-warning-icon">⚠️</span>
  <span class="medical-warning-text">
    <strong>Educativo:</strong> NÃO fazemos recomendação de uso. Sempre consulte <strong>médico</strong> ou <strong>farmacêutico</strong>.
  </span>
  <button class="medical-warning-close" onclick="document.getElementById('medicalWarning').style.display='none'" aria-label="Fechar aviso">×</button>
</div>

<script>
// Auto-fecha o aviso apos 8 segundos
setTimeout(function() {
  const w = document.getElementById('medicalWarning');
  if (w && w.style.display !== 'none') {
    w.style.transition = 'opacity 0.5s, max-height 0.5s';
    w.style.opacity = '0';
    w.style.maxHeight = '0';
    setTimeout(() => w.style.display = 'none', 500);
  }
}, 8000);
</script>"""


def fix_warning():
    total = 0
    for fname in ALL_HTML:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        # Substitui CSS para tornar nao-sticky e menor
        html = html.replace(OLD_CSS, NEW_CSS)

        # Substitui HTML para versao compacta
        html = html.replace(OLD_HTML, NEW_HTML)

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
            print(f"✅ {fname}")
    print(f"\nTotal: {total} arquivos ajustados")
    return total


if __name__ == "__main__":
    fix_warning()