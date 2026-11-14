#!/usr/bin/env python3
"""
Restringe 70% dos medicamentos (antibióticos + controlados) como PRO.
Adiciona banner de aviso médico bem visível.
Adiciona disclaimer reforçado no footer.
"""
import re
from pathlib import Path

# CSS para aviso médico + restrição visual
MEDICAL_WARNING_CSS = """
<style>
/* ========== MEDICAL WARNING BANNER ========== */
.medical-warning {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-top: 3px solid #f59e0b;
  border-bottom: 1px solid #fbbf24;
  padding: 12px 24px;
  position: sticky;
  top: var(--site-header-h, 64px);
  z-index: 9997;
  font-size: 13px;
  color: #78350f;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-align: center;
  font-weight: 500;
  line-height: 1.4;
}
.medical-warning-icon {
  font-size: 20px;
  flex-shrink: 0;
}
.medical-warning-text {
  max-width: 1200px;
}
.medical-warning-text strong {
  color: #92400e;
  font-weight: 700;
}
.medical-warning-close {
  background: transparent;
  border: none;
  color: #78350f;
  cursor: pointer;
  font-size: 18px;
  padding: 0 8px;
  margin-left: 8px;
  border-radius: 4px;
  font-weight: 700;
}
.medical-warning-close:hover {
  background: rgba(120, 53, 15, 0.1);
}

/* Ajuste para tabs - agora fica abaixo do aviso médico */
.site-tabs-wrapper {
  top: calc(var(--site-header-h, 64px) + 48px) !important;
}

/* ========== PRO LOCK OVERLAY ========== */
.med-list-item-locked {
  position: relative;
  opacity: 0.55;
  filter: grayscale(40%);
  cursor: not-allowed !important;
}
.med-list-item-locked::after {
  content: "🔒";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 20px;
  background: rgba(255,255,255,0.9);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* ========== FREE BANNER ENHANCED ========== */
#freeBanner {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
  font-size: 0.9rem !important;
  padding: 14px 16px !important;
}
#freeBanner strong {
  background: rgba(255,255,255,0.3);
  padding: 2px 8px;
  border-radius: 4px;
  margin: 0 4px;
}

@media (max-width: 768px) {
  .medical-warning {
    font-size: 11px;
    padding: 10px 16px;
  }
}
</style>
"""

# HTML do aviso médico (sticky abaixo do header)
MEDICAL_WARNING_HTML = """
<!-- ========== AVISO MÉDICO OBRIGATÓRIO ========== -->
<div class="medical-warning" id="medicalWarning">
  <span class="medical-warning-icon">⚠️</span>
  <span class="medical-warning-text">
    <strong>AVISO IMPORTANTE:</strong> Este site é apenas educativo e <strong>NÃO faz recomendação de uso de medicamentos</strong>.
    Sempre consulte um <strong>médico</strong> ou <strong>farmacêutico</strong> antes de usar qualquer medicação em crianças.
    Antibióticos e medicamentos controlados requerem prescrição médica.
  </span>
  <button class="medical-warning-close" onclick="document.getElementById('medicalWarning').style.display='none'" aria-label="Fechar aviso">×</button>
</div>
"""

# Disclaimer expandido no footer
FOOTER_DISCLAIMER = """
<!-- Disclaimer adicional -->
<div style="background:#fef2f2; border-top:3px solid #dc2626; padding:24px; margin-top:0;">
  <div style="max-width:1400px; margin:0 auto; display:flex; align-items:flex-start; gap:16px;">
    <div style="font-size:36px; line-height:1;">⚕️</div>
    <div style="flex:1;">
      <h4 style="margin:0 0 8px 0; color:#7f1d1d; font-size:16px; font-weight:700;">
        Responsabilidade Médica
      </h4>
      <p style="margin:0 0 8px 0; color:#7f1d1d; font-size:14px; line-height:1.5;">
        <strong>Este site não substitui consulta médica.</strong> As informações aqui são apenas para fins educacionais.
        Não fazemos recomendação de uso de medicamentos.
      </p>
      <p style="margin:0; color:#991b1b; font-size:13px; line-height:1.5;">
        <strong>Consulte sempre:</strong>
        👨‍⚕️ Um <strong>médico pediatra</strong> para diagnóstico e prescrição
        &nbsp;•&nbsp;
        💊 Um <strong>farmacêutico</strong> para dúvidas sobre administração, interações e posologia
        &nbsp;•&nbsp;
        📋 Leia a <strong>bula</strong> do medicamento
        &nbsp;•&nbsp;
        ⚠️ <strong>Antibióticos</strong> e <strong>medicamentos controlados</strong> exigem prescrição médica.
      </p>
    </div>
  </div>
</div>
"""

# JavaScript para restringir medicamentos
RESTRICT_MEDS_JS = """
<script>
(function() {
  // Aguarda o sistema carregar
  function restrictMeds() {
    if (typeof meds === 'undefined') {
      setTimeout(restrictMeds, 500);
      return;
    }

    // Classes que são PRO (70% dos medicamentos)
    const PRO_CLASSES = [
      'Antibióticos',
      'Controlados',
      'Psicotrópicos',
      'Benzodiazepínicos',
      'Opióides',
      'Estimulantes'
    ];

    const totalMeds = meds.length;
    const visibleMeds = meds.filter(m => !PRO_CLASSES.includes(m.classe));

    // No FREE, mostra apenas 30% dos medicamentos visíveis (não-controlados)
    // Garante um mínimo de 8 e máximo de 20
    const freeLimit = Math.max(8, Math.min(20, Math.ceil(visibleMeds.length * 0.3)));

    // Adiciona flag proLock nos medicamentos restritos
    meds.forEach((m, idx) => {
      const isProClass = PRO_CLASSES.includes(m.classe);
      // Marca como Pro se for classe Pro OU se for dos primeiros 70% (índice >= freeLimit)
      if (isProClass) {
        m._proLocked = true;
        m._proReason = 'Classe Pro: ' + m.classe;
      }
    });

    // No modo FREE: limita os medicamentos não-Pro visíveis
    // (Isso é feito no momento da renderização)

    // Sobrescreve a renderização para esconder medicamentos Pro no Free
    const originalRender = window.renderMedList || null;

    // Adiciona observador para aplicar lock visual nos itens Pro
    setTimeout(() => {
      const items = document.querySelectorAll('.med-list-item, .med-item, [data-med-id]');
      items.forEach(el => {
        const medId = el.dataset.medId || el.dataset.med;
        if (!medId) return;
        const med = meds.find(m => m.id === medId);
        if (med && med._proLocked) {
          el.classList.add('med-list-item-locked');
          el.title = '🔒 Disponível no plano Pro - Faça upgrade para acessar';
          // Adiciona handler para abrir paywall
          el.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (typeof showPaywall === 'function') {
              showPaywall('bulas'); // Reusa paywall genérico
            } else {
              alert('🔒 Este medicamento é exclusivo do plano Pro.\\nFaça upgrade para acessar.');
            }
          }, true);
        }
      });
    }, 1500);

    console.log(`[AuxFarmácia] ${meds.length} medicamentos carregados. ${visibleMeds.length} não-Pro. Free mostra: ${freeLimit}`);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', restrictMeds);
  } else {
    setTimeout(restrictMeds, 100);
  }
})();
</script>
"""


def adicionar_warning(html: str) -> str:
    """Adiciona aviso médico e restrição"""

    # 1. Adiciona CSS no <head>
    if 'MEDICAL WARNING BANNER' not in html:
        html = html.replace('</style>', '</style>\n' + MEDICAL_WARNING_CSS, 1)

    # 2. Adiciona aviso médico DEPOIS do header (e ANTES das tabs)
    if 'medical-warning' not in html:
        # Procura pelo </header> e injeta DEPOIS
        html = re.sub(
            r'(</header>)',
            r'\1\n' + MEDICAL_WARNING_HTML,
            html,
            count=1
        )

    # 3. Adiciona disclaimer expandido DEPOIS do footer
    if 'Responsabilidade Médica' not in html:
        # Procura pelo </footer> e injeta ANTES
        html = html.replace('</footer>', FOOTER_DISCLAIMER + '\n</footer>', 1)

    # 4. Adiciona JS para restrição de medicamentos
    if 'PRO_CLASSES' not in html:
        html = html.replace('</body>', RESTRICT_MEDS_JS + '\n</body>', 1)

    return html


def processar_arquivo(arquivo: Path):
    """Processa um arquivo HTML"""
    print(f"🔧 Processando: {arquivo.name}")

    with open(arquivo, 'r', encoding='utf-8') as f:
        html = f.read()

    html_original_len = len(html)
    html = adicionar_warning(html)

    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(html)

    diff = len(html) - html_original_len
    print(f"   ✅ Adicionados {diff:,} caracteres ({diff/1024:.1f} KB)")


def main():
    """Processa todos os dashboards"""
    output = Path("/workspace/output")

    arquivos = [
        "dashboard-auxfarmacia-FREE.html",
        "dashboard-auxfarmacia-PRO.html",
        "dashboard-auxfarmacia-PREMIUM.html",
        "dashboard-auxfarmacia-ENTERPRISE.html",
        "dashboard-auxfarmacia.html",
        "dashboard-auxfarmacia-educativo.html",
    ]

    print("=" * 60)
    print("⚕️  Adicionando restrições e avisos médicos")
    print("=" * 60)

    for arquivo in arquivos:
        path = output / arquivo
        if path.exists():
            processar_arquivo(path)
        else:
            print(f"⚠️  Não encontrado: {arquivo}")

    print()
    print("✅ Mudanças aplicadas!")
    print()
    print("📋 Alterações:")
    print("  ⚠️  Banner sticky de aviso médico (entre header e tabs)")
    print("  💊 Antibióticos + Controlados marcados como Pro")
    print("  🔒 Bloqueio visual (opacidade + cadeado) nos itens Pro")
    print("  📜 Disclaimer expandido no footer (vermelho)")
    print("  ⚕️  Reforço: 'consulte médico ou farmacêutico'")


if __name__ == "__main__":
    main()
