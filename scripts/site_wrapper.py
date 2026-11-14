#!/usr/bin/env python3
"""
Adiciona "casca de site" ao dashboard:
- Header fixo com navegação
- Hero section
- Footer completo
- Mantém 100% das funcionalidades do dashboard
"""
import re
from pathlib import Path

# CSS para header, hero, footer
SITE_CSS = """
<style>
/* ========== SITE WRAPPER STYLES ========== */
/* Importa Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@700;900&display=swap');

:root {
  --site-header-h: 64px;
  --site-primary: #0d9488;
  --site-primary-light: #14b8a6;
  --site-dark: #0f172a;
  --site-gray: #64748b;
  --site-light: #f8fafc;
  --site-border: #e2e8f0;
  --site-shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
  --site-shadow-lg: 0 10px 25px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.05);
}

/* HEADER FIXO */
.site-header {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--site-header-h);
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--site-border);
  z-index: 9999;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: var(--site-shadow);
}
.site-header-inner {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.site-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
  font-size: 18px;
  color: var(--site-dark);
  text-decoration: none;
  font-family: 'Inter', sans-serif;
}
.site-logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--site-primary) 0%, var(--site-primary-light) 100%);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 800;
  font-size: 16px;
  box-shadow: 0 4px 10px rgba(20,184,166,0.3);
}
.site-nav {
  display: flex;
  gap: 4px;
  align-items: center;
}
.site-nav a {
  color: var(--site-dark);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 14px;
  border-radius: 6px;
  transition: all 0.15s;
}
.site-nav a:hover {
  background: var(--site-light);
  color: var(--site-primary);
}
.site-nav a.active {
  background: var(--site-light);
  color: var(--site-primary);
}
.site-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.site-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.site-btn-ghost {
  background: transparent;
  color: var(--site-dark);
}
.site-btn-ghost:hover {
  background: var(--site-light);
}
.site-btn-primary {
  background: var(--site-primary);
  color: white;
  box-shadow: 0 4px 10px rgba(13,148,136,0.25);
}
.site-btn-primary:hover {
  background: #0f766e;
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(13,148,136,0.35);
}
.site-plan-badge {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.site-plan-badge.pro { background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%); }
.site-plan-badge.premium { background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%); }
.site-plan-badge.institutional { background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); }

/* MAIN WRAPPER - dá espaço para o header */
.site-main {
  margin-top: var(--site-header-h);
  min-height: calc(100vh - var(--site-header-h));
}

/* HERO SECTION */
.site-hero {
  background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 50%, #f0f9ff 100%);
  padding: 60px 24px 50px;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--site-border);
}
.site-hero::before {
  content: '';
  position: absolute;
  top: -50%; right: -10%;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(20,184,166,0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.site-hero::after {
  content: '';
  position: absolute;
  bottom: -30%; left: -10%;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(6,182,212,0.08) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.site-hero-inner {
  max-width: 1400px;
  margin: 0 auto;
  text-align: center;
  position: relative;
  z-index: 1;
}
.site-hero h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(28px, 4vw, 44px);
  font-weight: 900;
  color: var(--site-dark);
  margin: 0 0 12px 0;
  line-height: 1.1;
}
.site-hero h1 .accent {
  background: linear-gradient(135deg, var(--site-primary) 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.site-hero p {
  font-size: clamp(15px, 1.5vw, 18px);
  color: var(--site-gray);
  max-width: 720px;
  margin: 0 auto 20px;
  line-height: 1.5;
}
.site-hero-badges {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  font-size: 13px;
  color: var(--site-gray);
}
.site-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: white;
  border: 1px solid var(--site-border);
  border-radius: 20px;
  font-weight: 500;
}
.site-hero-badge-icon {
  color: #10b981;
  font-weight: 700;
}

/* SITE BREADCRUMB */
.site-breadcrumb {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px 0;
  font-size: 13px;
  color: var(--site-gray);
}
.site-breadcrumb a {
  color: var(--site-gray);
  text-decoration: none;
}
.site-breadcrumb a:hover { color: var(--site-primary); }
.site-breadcrumb-sep {
  margin: 0 6px;
  color: #cbd5e1;
}

/* FOOTER */
.site-footer {
  background: var(--site-dark);
  color: #cbd5e1;
  padding: 60px 24px 24px;
  margin-top: 60px;
}
.site-footer-inner {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}
.site-footer-brand h3 {
  color: white;
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.site-footer-brand p {
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 16px;
}
.site-footer-col h4 {
  color: white;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.site-footer-col a {
  display: block;
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  margin-bottom: 10px;
  transition: color 0.15s;
}
.site-footer-col a:hover { color: white; }
.site-footer-bottom {
  max-width: 1400px;
  margin: 0 auto;
  padding-top: 24px;
  border-top: 1px solid #1e293b;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #64748b;
  flex-wrap: wrap;
  gap: 16px;
}
.site-footer-bottom-links {
  display: flex;
  gap: 24px;
}
.site-footer-bottom-links a {
  color: #94a3b8;
  text-decoration: none;
}
.site-footer-bottom-links a:hover { color: white; }

/* BADGE PRO flutuante (mobile) */
.site-plan-badge-mobile {
  display: none;
}
@media (max-width: 768px) {
  .site-nav { display: none; }
  .site-plan-badge { display: none; }
  .site-plan-badge-mobile { display: inline-block; }
  .site-footer-inner { grid-template-columns: 1fr; gap: 32px; }
}

/* Ajusta o banner do free que está embaixo */
#freeBanner {
  bottom: 0 !important;
}
body { padding-bottom: 60px; }
</style>
"""

# HTML do Header
SITE_HEADER = """
<!-- ========== SITE HEADER FIXO ========== -->
<header class="site-header">
  <div class="site-header-inner">
    <a href="landing.html" class="site-logo">
      <div class="site-logo-icon">Rx</div>
      <span>Auxílio Farmácia</span>
    </a>

    <nav class="site-nav">
      <a href="landing.html#recursos">Recursos</a>
      <a href="landing.html#planos">Planos</a>
      <a href="landing.html#faq">FAQ</a>
      <a href="dashboard-auxfarmacia.html" class="active">Dashboard</a>
      <span class="site-plan-badge" id="sitePlanBadge">FREE</span>
    </nav>

    <div class="site-header-actions">
      <a href="#" class="site-btn site-btn-ghost" onclick="return false;">Entrar</a>
      <a href="checkout.html" class="site-btn site-btn-primary">Assinar Pro</a>
    </div>
  </div>
</header>

<main class="site-main">
  <!-- ========== HERO SECTION ========== -->
  <section class="site-hero">
    <div class="site-hero-inner">
      <h1>O Guia Médico-<span class="accent">Farmacêutico</span> completo do Brasil</h1>
      <p>89+ medicamentos adultos e pediátricos com bulas ANVISA, 9 calculadoras clínicas avançadas (PEWS, PELOD, Parkland), mapas mentais interativos e flashcards. Para médicos, farmacêuticos e profissionais de saúde.</p>
      <div class="site-hero-badges">
        <span class="site-hero-badge"><span class="site-hero-badge-icon">✓</span> Bulas oficiais ANVISA</span>
        <span class="site-hero-badge"><span class="site-hero-badge-icon">✓</span> Calculadoras pediátricas</span>
        <span class="site-hero-badge"><span class="site-hero-badge-icon">✓</span> Mapas mentais SVG</span>
        <span class="site-hero-badge"><span class="site-hero-badge-icon">✓</span> Flashcards interativos</span>
      </div>
    </div>
  </section>

  <!-- ========== BREADCRUMB ========== -->
  <div class="site-breadcrumb">
    <a href="landing.html">Início</a>
    <span class="site-breadcrumb-sep">›</span>
    <a href="landing.html#planos">Dashboard</a>
    <span class="site-breadcrumb-sep">›</span>
    <span>Guia Médico-Farmacêutico</span>
  </div>
"""

# HTML do Footer
SITE_FOOTER = """
</main>
<!-- ========== SITE FOOTER ========== -->
<footer class="site-footer">
  <div class="site-footer-inner">
    <div class="site-footer-brand">
      <h3>
        <div class="site-logo-icon" style="width:32px;height:32px;font-size:14px;">Rx</div>
        Auxílio Farmácia
      </h3>
      <p>Dashboard pediátrico de posologia mais completo do Brasil. Feito com carinho por pediatras para pediatras.</p>
      <p style="font-size:12px;color:#64748b;margin-top:12px;">Para ensino de farmacologia. Não substitui bula, prescrição ou avaliação médica individualizada.</p>
    </div>

    <div class="site-footer-col">
      <h4>Produto</h4>
      <a href="landing.html#recursos">Recursos</a>
      <a href="landing.html#planos">Planos</a>
      <a href="landing.html#faq">FAQ</a>
      <a href="dashboard-auxfarmacia.html">Dashboard</a>
    </div>

    <div class="site-footer-col">
      <h4>Recursos</h4>
      <a href="#">Bulas ANVISA</a>
      <a href="#">Calculadoras</a>
      <a href="#">Mapas mentais</a>
      <a href="#">Flashcards</a>
    </div>

    <div class="site-footer-col">
      <h4>Contato</h4>
      <a href="mailto:contato@auxfarmacia.com.br">contato@auxfarmacia.com.br</a>
      <a href="#">Suporte</a>
      <a href="#">Política de Privacidade</a>
      <a href="#">Termos de Uso</a>
    </div>
  </div>

  <div class="site-footer-bottom">
    <div>© 2025 Auxílio Farmácia. Todos os direitos reservados.</div>
    <div class="site-footer-bottom-links">
      <a href="#">Privacidade</a>
      <a href="#">Termos</a>
      <a href="#">LGPD</a>
      <a href="#">Status</a>
    </div>
  </div>
</footer>

<script>
// Atualiza badge do plano no header
(function() {
  try {
    const lic = localStorage.getItem('auxf_license');
    if (lic) {
      const parsed = JSON.parse(lic);
      const tier = (parsed.tier || 'free').toUpperCase();
      const badge = document.getElementById('sitePlanBadge');
      if (badge) {
        badge.textContent = tier;
        badge.className = 'site-plan-badge ' + tier.toLowerCase();
      }
    }
  } catch(e) {}
})();
</script>
"""

def adicionar_site_wrapper(html: str) -> str:
    """Adiciona header/footer/hero ao HTML"""

    # 1. Adiciona CSS no <head> (após o </style> existente)
    if 'SITE WRAPPER STYLES' not in html:
        html = html.replace('</style>', '</style>\n' + SITE_CSS, 1)

    # 2. Substitui <body> por header + abertura do main
    if 'class="site-header"' not in html:
        # Encontra o <body ...> e injeta depois
        html = re.sub(
            r'(<body[^>]*>)',
            r'\1\n' + SITE_HEADER,
            html,
            count=1
        )

    # 3. Adiciona footer antes do </body>
    if 'class="site-footer"' not in html:
        html = html.replace('</body>', SITE_FOOTER + '\n</body>', 1)

    return html


def processar_arquivo(arquivo: Path):
    """Processa um arquivo HTML"""
    print(f"🔧 Processando: {arquivo.name}")

    with open(arquivo, 'r', encoding='utf-8') as f:
        html = f.read()

    html_original_len = len(html)
    html = adicionar_site_wrapper(html)

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
    print("🎨 Adicionando 'aspecto de site' aos dashboards")
    print("=" * 60)

    for arquivo in arquivos:
        path = output / arquivo
        if path.exists():
            processar_arquivo(path)
        else:
            print(f"⚠️  Não encontrado: {arquivo}")

    print()
    print("✅ Todos os dashboards atualizados com aspecto de site!")
    print()
    print("📋 Elementos adicionados:")
    print("  • Header fixo no topo com navegação")
    print("  • Logo + Plano badge (FREE/PRO/PREMIUM)")
    print("  • Hero section com headline + badges")
    print("  • Breadcrumb de navegação")
    print("  • Footer completo (4 colunas)")
    print("  • Copyright + links legais")


if __name__ == "__main__":
    main()
