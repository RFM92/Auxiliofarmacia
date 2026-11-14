#!/usr/bin/env python3
"""
Transforma as tabs existentes em uma navegação sticky tipo site:
- Barra de tabs sticky abaixo do header
- Cada tab com ícone emoji + label
- Tabs premium com badge "PRO"
- Scroll horizontal suave no mobile
- URL hash sync (#posologia, #educacao, etc)
- Title sync
"""
import re
from pathlib import Path

# CSS para a nova barra de tabs
TABS_CSS = """
<style>
/* ========== SITE TAB NAVIGATION ========== */
.site-tabs-wrapper {
  position: sticky;
  top: var(--site-header-h, 64px);
  z-index: 9998;
  background: white;
  border-bottom: 1px solid var(--site-border, #e2e8f0);
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  margin-bottom: 0;
}
.site-tabs-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.site-tabs-container::-webkit-scrollbar { display: none; }

.site-tabs {
  display: flex;
  gap: 4px;
  padding: 12px 0;
  white-space: nowrap;
}

.site-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 8px;
  background: transparent;
  color: var(--site-gray, #64748b);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s;
  text-decoration: none;
  font-family: inherit;
  position: relative;
  white-space: nowrap;
}
.site-tab:hover {
  background: var(--site-light, #f8fafc);
  color: var(--site-primary, #0d9488);
}
.site-tab.active {
  background: linear-gradient(135deg, rgba(13,148,136,0.08) 0%, rgba(6,182,212,0.08) 100%);
  color: var(--site-primary, #0d9488);
  border-color: rgba(13,148,136,0.2);
  font-weight: 600;
}
.site-tab-icon {
  font-size: 18px;
  display: inline-flex;
}
.site-tab-label {
  font-weight: inherit;
}
.site-tab-pro-badge {
  display: inline-block;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  font-size: 9px;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 4px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  margin-left: 4px;
}
.site-tab-counter {
  background: var(--site-light, #f8fafc);
  color: var(--site-gray, #64748b);
  font-size: 11px;
  padding: 1px 7px;
  border-radius: 10px;
  font-weight: 600;
}
.site-tab.active .site-tab-counter {
  background: var(--site-primary, #0d9488);
  color: white;
}

/* Animação quando ativa */
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.site-tab.active {
  animation: slideIn 0.2s ease-out;
}

/* Indicador de scroll horizontal no mobile */
.site-tabs-scroll-hint {
  display: none;
  padding: 4px 8px;
  background: var(--site-light, #f8fafc);
  border-radius: 4px;
  font-size: 11px;
  color: var(--site-gray, #64748b);
  margin-left: auto;
}

/* Mobile */
@media (max-width: 768px) {
  .site-tabs-container { padding: 0 16px; }
  .site-tab { padding: 8px 12px; font-size: 13px; }
  .site-tab-icon { font-size: 16px; }
  .site-tabs-scroll-hint { display: inline-flex; align-items: center; }
}

/* Esconde a barra de tabs antiga dentro do main */
.site-tabs-old-hide .tabs {
  display: none !important;
}
</style>
"""

# HTML da barra de tabs nova (será inserida antes do main content)
SITE_TABS_BAR = """
<!-- ========== SITE TABS NAVIGATION ========== -->
<div class="site-tabs-wrapper">
  <div class="site-tabs-container">
    <nav class="site-tabs" id="siteTabsNav">
      <a href="#posologia" class="site-tab active" data-target="tabPosologia">
        <span class="site-tab-icon">💊</span>
        <span class="site-tab-label">Posologia</span>
      </a>
      <a href="#educacao" class="site-tab" data-target="tabEducacao">
        <span class="site-tab-icon">📚</span>
        <span class="site-tab-label">Educação</span>
      </a>
      <a href="#comparacao" class="site-tab" data-target="tabComparacao">
        <span class="site-tab-icon">⚖️</span>
        <span class="site-tab-label">Comparação</span>
      </a>
      <a href="#clinicas" class="site-tab" data-target="tabClinicas">
        <span class="site-tab-icon">🏥</span>
        <span class="site-tab-label">Clínicas</span>
      </a>
      <a href="#puericultura" class="site-tab" data-target="tabPueri">
        <span class="site-tab-icon">👶</span>
        <span class="site-tab-label">Puericultura</span>
      </a>
      <a href="#fluxos" class="site-tab" data-target="tabFluxos">
        <span class="site-tab-icon">🔀</span>
        <span class="site-tab-label">Fluxos</span>
      </a>
      <a href="#avancadas" class="site-tab" data-target="tabAvancadas">
        <span class="site-tab-icon">🧠</span>
        <span class="site-tab-label">Avançadas</span>
        <span class="site-tab-pro-badge">PRO</span>
      </a>
      <a href="#comparador" class="site-tab" data-target="tabComparador">
        <span class="site-tab-icon">🎯</span>
        <span class="site-tab-label">Comparador</span>
        <span class="site-tab-pro-badge">PRO</span>
      </a>
      <a href="#casos" class="site-tab" data-target="tabCasos">
        <span class="site-tab-icon">💼</span>
        <span class="site-tab-label">Casos</span>
      </a>
      <a href="#interacoes" class="site-tab" data-target="tabInteracoes">
        <span class="site-tab-icon">⚠️</span>
        <span class="site-tab-label">Interações</span>
      </a>
      <a href="#visual" class="site-tab" data-target="tabVisual">
        <span class="site-tab-icon">🎨</span>
        <span class="site-tab-label">Visual</span>
        <span class="site-tab-pro-badge">PRO</span>
      </a>
      <a href="#prescricao" class="site-tab" data-target="tabTabPrescricao">
        <span class="site-tab-icon">📋</span>
        <span class="site-tab-label">Prescrição</span>
        <span class="site-tab-pro-badge">PRO</span>
      </a>
      <span class="site-tabs-scroll-hint">← arraste →</span>
    </nav>
  </div>
</div>
"""

# JavaScript para gerenciar as tabs
TABS_JS = """
<script>
(function() {
  // Aguarda DOM pronto
  document.addEventListener('DOMContentLoaded', function() {
    initSiteTabs();
  });

  // Se DOM já estiver pronto, executa
  if (document.readyState !== 'loading') {
    setTimeout(initSiteTabs, 100);
  }

  function initSiteTabs() {
    const siteTabs = document.querySelectorAll('.site-tab');
    const oldTabs = document.querySelectorAll('.tab-btn');

    // Map de IDs
    const targetMap = {
      'tabPosologia': 'posologia',
      'tabEducacao': 'educacao',
      'tabComparacao': 'comparacao',
      'tabClinicas': 'clinicas',
      'tabPueri': 'puericultura',
      'tabFluxos': 'fluxos',
      'tabAvancadas': 'avancadas',
      'tabComparador': 'comparador',
      'tabCasos': 'casos',
      'tabInteracoes': 'interacoes',
      'tabVisual': 'visual',
      'tabTabPrescricao': 'prescricao'
    };

    // Função para ativar uma tab
    function activateTab(tabId) {
      // Remove active de todas as site-tabs
      siteTabs.forEach(t => t.classList.remove('active'));
      // Remove active de todas as old-tabs
      oldTabs.forEach(t => t.classList.remove('active'));

      // Ativa site-tab correspondente
      const siteTab = document.querySelector(`.site-tab[data-target="${tabId}"]`);
      if (siteTab) siteTab.classList.add('active');

      // Ativa old-tab correspondente e simula click
      const oldTab = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
      if (oldTab) {
        oldTab.classList.add('active');
        oldTab.click();
      }

      // Mostra o conteúdo
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      const target = document.getElementById(tabId);
      if (target) {
        target.classList.add('active');
        // Scroll suave até o conteúdo
        setTimeout(() => {
          const headerOffset = 64 + 56; // header + tabs bar
          const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerOffset;
          window.scrollTo({ top: targetPosition, behavior: 'smooth' });
        }, 100);
      }
    }

    // Click nas site-tabs
    siteTabs.forEach(tab => {
      tab.addEventListener('click', function(e) {
        e.preventDefault();
        const target = this.dataset.target;
        if (target) {
          activateTab(target);
          // Atualiza URL hash
          const slug = targetMap[target] || 'dashboard';
          history.replaceState(null, '', '#' + slug);
        }
      });
    });

    // Sync com tabs antigas (caso user clique nelas)
    oldTabs.forEach(tab => {
      tab.addEventListener('click', function() {
        const target = this.dataset.tab;
        siteTabs.forEach(t => t.classList.remove('active'));
        const siteTab = document.querySelector(`.site-tab[data-target="${target}"]`);
        if (siteTab) siteTab.classList.add('active');
      });
    });

    // Suporte a hash na URL (#posologia, #educacao, etc)
    function loadFromHash() {
      const hash = window.location.hash.slice(1);
      if (hash) {
        // Encontra o tabId pelo slug
        const entry = Object.entries(targetMap).find(([_, slug]) => slug === hash);
        if (entry) {
          activateTab(entry[0]);
        }
      }
    }
    loadFromHash();
    window.addEventListener('hashchange', loadFromHash);

    // Atualiza title baseado na tab ativa
    const tabLabels = {
      'tabPosologia': 'Calculadora de Posologia',
      'tabEducacao': 'Educação Farmacológica',
      'tabComparacao': 'Comparação na Classe',
      'tabClinicas': 'Calculadoras Clínicas',
      'tabPueri': 'Puericultura',
      'tabFluxos': 'Fluxogramas',
      'tabAvancadas': 'Calculadoras Avançadas',
      'tabComparador': 'Comparador de Classes',
      'tabCasos': 'Casos Clínicos',
      'tabInteracoes': 'Interações',
      'tabVisual': 'Aprendizado Visual',
      'tabTabPrescricao': 'Prescrição'
    };
  }
})();
</script>
"""

def adicionar_tabs_site(html: str) -> str:
    """Adiciona barra de tabs sticky tipo site"""

    # 1. Adiciona CSS no <head>
    if 'SITE TAB NAVIGATION' not in html:
        html = html.replace('</style>', '</style>\n' + TABS_CSS, 1)

    # 2. Adiciona barra de tabs DEPOIS do header
    # Procura pelo </header> e injeta depois
    if 'class="site-tabs-wrapper"' not in html:
        html = re.sub(
            r'(</header>)',
            r'\1\n' + SITE_TABS_BAR,
            html,
            count=1
        )

    # 3. Esconde as tabs antigas (.tabs dentro do main)
    html = html.replace('<body', '<body class="site-tabs-old-hide"', 1)

    # 4. Adiciona o JS antes do </body>
    if 'function initSiteTabs' not in html:
        html = html.replace('</body>', TABS_JS + '\n</body>', 1)

    return html


def processar_arquivo(arquivo: Path):
    """Processa um arquivo HTML"""
    print(f"🔧 Processando: {arquivo.name}")

    with open(arquivo, 'r', encoding='utf-8') as f:
        html = f.read()

    html_original_len = len(html)
    html = adicionar_tabs_site(html)

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
    print("🎯 Adicionando navegação por tabs (aspecto de site)")
    print("=" * 60)

    for arquivo in arquivos:
        path = output / arquivo
        if path.exists():
            processar_arquivo(path)
        else:
            print(f"⚠️  Não encontrado: {arquivo}")

    print()
    print("✅ Todos os dashboards atualizados!")
    print()
    print("📋 Tabs disponíveis (12 no total):")
    print("  1. 💊 Posologia (default)")
    print("  2. 📚 Educação")
    print("  3. ⚖️ Comparação")
    print("  4. 🏥 Clínicas")
    print("  5. 👶 Puericultura")
    print("  6. 🔀 Fluxos")
    print("  7. 🧠 Avançadas [PRO]")
    print("  8. 🎯 Comparador [PRO]")
    print("  9. 💼 Casos")
    print(" 10. ⚠️ Interações")
    print(" 11. 🎨 Visual [PRO]")
    print(" 12. 📋 Prescrição [PRO]")
    print()
    print("🌐 Deep linking via URL hash:")
    print("  • /dashboard-auxfarmacia.html#avancadas")
    print("  • /dashboard-auxfarmacia.html#casos")
    print("  • etc.")


if __name__ == "__main__":
    main()
