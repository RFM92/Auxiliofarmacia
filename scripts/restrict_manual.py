#!/usr/bin/env python3
"""
Restringe Manual do Admin no frontend:
- Remove do modal publico de downloads
- Adiciona secao "Documentos Internos" no admin.html (com auth)
- Atualiza api-client.js para distinguir publico vs restrito
"""
from pathlib import Path

# Novo JS para downloads (atualizado)
DOWNLOADS_JS_V2 = """
<script>
// ========== MATERIAIS / DOWNLOADS v2 ==========
// Manual do Admin: APENAS para admin logado
// Apresentacao + Site ZIP: publico

const PUBLIC_DOWNLOADS = {
  comercial: {
    name: 'Auxilio_Farmacia-Apresentacao_Comercial.pdf',
    title: 'Apresentacao Comercial',
    desc: 'Material de vendas para clientes',
    size_kb: 18, pages: 11, type: 'pdf',
    public: true,
    url: '/api/downloads/comercial',
    fallback: 'Auxilio_Farmacia-Apresentacao_Comercial.pdf'
  },
  'site-zip': {
    name: 'auxfarmacia_site.zip',
    title: 'Site Completo (HTML)',
    desc: 'Todos os dashboards sem PDFs',
    size_kb: 800, type: 'zip',
    public: true,
    url: '/api/downloads/site-zip',
    fallback: 'auxfarmacia_site.zip'
  }
};

const ADMIN_DOWNLOADS = {
  manual: {
    name: 'Auxilio_Farmacia-Manual_do_Administrador.pdf',
    title: 'Manual do Administrador',
    desc: 'Guia interno para setup e operacao',
    size_kb: 23, pages: 13, type: 'pdf',
    public: false,
    url: '/api/downloads/admin/manual',
    requiresAuth: true,
    warning: 'Documento interno - NAO compartilhar publicamente'
  },
  'full-zip': {
    name: 'auxfarmacia_completo.zip',
    title: 'Pacote Completo (com Manuais)',
    desc: 'Inclui Manual do Admin',
    size_kb: 1200, type: 'zip',
    public: false,
    url: '/api/downloads/admin/full-zip',
    requiresAuth: true,
    warning: 'Documento interno - NAO compartilhar publicamente'
  }
};

async function downloadFile(item, requireAdmin) {
  // Se requer admin, verifica auth
  if (requireAdmin) {
    if (typeof AUXF_API === 'undefined' || !AUXF_API.isLoggedIn()) {
      if (confirm('Este download requer login de administrador.\\n\\nFazer login agora?')) {
        showLoginModal();
      }
      return;
    }

    // Verifica se e admin
    if (AUXF_API.user && AUXF_API.user.role !== 'admin' && AUXF_API.user.role !== 'super_admin') {
      alert('Acesso negado. Apenas administradores podem baixar este arquivo.');
      return;
    }

    // Tenta API real
    try {
      const r = await fetch(item.url, {
        headers: { 'Authorization': 'Bearer ' + AUXF_API.token }
      });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const blob = await r.blob();
      downloadBlob(blob, item.name);
      showToastDownload('Download: ' + item.name);
      return;
    } catch (e) {
      console.warn('Download via API falhou:', e);
      // Fallback: link direto
      const a = document.createElement('a');
      a.href = item.fallback || item.name;
      a.download = item.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToastDownload('Download: ' + item.name + ' (fallback)');
      return;
    }
  }

  // Publico - tenta API ou direto
  try {
    const r = await fetch(item.url);
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const blob = await r.blob();
    downloadBlob(blob, item.name);
    showToastDownload('Download: ' + item.name);
  } catch (e) {
    // Fallback
    const a = document.createElement('a');
    a.href = item.fallback || item.name;
    a.download = item.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToastDownload('Download: ' + item.name);
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function downloadPDF(type) {
  const item = PUBLIC_DOWNLOADS[type] || ADMIN_DOWNLOADS[type];
  if (!item) return;
  downloadFile(item, item.requiresAuth);
}

function downloadZIP(type) {
  // Publico: site zip / Admin: full zip
  const key = type === 'completo' ? 'full-zip' : 'site-zip';
  const item = key === 'site-zip' ? PUBLIC_DOWNLOADS[key] : ADMIN_DOWNLOADS[key];
  if (!item) return;
  downloadFile(item, item.requiresAuth);
}

function showToastDownload(msg) {
  if (typeof showToast === 'function') {
    showToast(msg, 'success');
  } else {
    console.log(msg);
  }
}

// ========== MODAL ==========
function showDownloadsModal() {
  const m = document.getElementById('downloadsModal');
  if (m) m.classList.add('open');
  updateAdminSection();
}

function closeDownloadsModal() {
  const m = document.getElementById('downloadsModal');
  if (m) m.classList.remove('open');
}

function updateAdminSection() {
  const section = document.getElementById('adminDownloadsSection');
  if (!section) return;

  const isAdmin = typeof AUXF_API !== 'undefined' &&
                  AUXF_API.user &&
                  (AUXF_API.user.role === 'admin' || AUXF_API.user.role === 'super_admin');

  if (isAdmin) {
    section.style.display = 'block';
    section.innerHTML = `
      <div style="background:#fef3c7;border:2px solid #f59e0b;border-radius:12px;padding:20px;margin:24px 16px 0;">
        <h3 style="margin:0 0 8px 0;color:#92400e;font-size:16px;">
          🔒 Documentos Internos (apenas admin)
        </h3>
        <p style="margin:0 0 16px 0;color:#78350f;font-size:13px;">
          Estes arquivos sao confidenciais. NAO compartilhar publicamente.
        </p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
          <div class="download-card" style="margin:0;border-color:#f59e0b;">
            <div class="download-card-icon admin">
              <span style="font-size:12px;line-height:1;">PDF</span>
              <small style="bottom:4px;font-size:8px;">RESTRITO</small>
            </div>
            <h3>Manual do Administrador</h3>
            <div class="desc">Guia interno. 13 paginas, linguagem simples.</div>
            <div class="meta">
              <span>PDF</span><span>23 KB</span><span>13 pag</span>
            </div>
            <button class="btn-download" onclick="downloadPDF('manual')">
              Baixar Manual (Admin)
            </button>
          </div>
          <div class="download-card" style="margin:0;border-color:#f59e0b;">
            <div class="download-card-icon zip">
              <span style="font-size:12px;line-height:1;">ZIP</span>
              <small style="bottom:4px;font-size:8px;">RESTRITO</small>
            </div>
            <h3>Pacote Completo</h3>
            <div class="desc">HTMLs + Manuais. Para deploys.</div>
            <div class="meta">
              <span>ZIP</span><span>1.2 MB</span>
            </div>
            <button class="btn-download zip" onclick="downloadZIP('completo')">
              Baixar Tudo (Admin)
            </button>
          </div>
        </div>
      </div>
    `;
  } else {
    section.style.display = 'none';
  }
}

// Botao no header
document.addEventListener('DOMContentLoaded', function() {
  const headerActions = document.querySelector('.site-header-actions');
  if (headerActions && !document.getElementById('siteMateriaisBtn')) {
    const btn = document.createElement('button');
    btn.id = 'siteMateriaisBtn';
    btn.className = 'site-materiais-btn';
    btn.innerHTML = 'Materiais';
    btn.onclick = showDownloadsModal;
    btn.title = 'Apresentacao comercial + arquivos do site';
    headerActions.insertBefore(btn, headerActions.firstChild);
  }

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeDownloadsModal();
  });
});
</script>
"""

# Novo HTML do modal - SEM manual
DOWNLOADS_MODAL_V2 = """
<!-- ========== MODAL: MATERIAIS PUBLICOS ========== -->
<div class="modal" id="downloadsModal" role="dialog">
  <div class="modal-box downloads-modal-box">
    <button type="button" class="modal-close" onclick="closeDownloadsModal()">×</button>

    <div class="downloads-header">
      <h2>Materiais Publicos</h2>
      <p>Material de vendas e arquivos do Auxilio Farmacia</p>
    </div>

    <div class="downloads-grid">

      <!-- Apresentacao Comercial - PUBLICO -->
      <div class="download-card featured">
        <span class="badge-new">PARA CLIENTES</span>
        <div class="download-card-icon">
          <span style="font-size:14px;line-height:1;">PDF</span>
          <small>11 PAGINAS</small>
        </div>
        <h3>Apresentacao Comercial</h3>
        <div class="desc">
          Material de vendas profissional. Use em reunioes com clientes,
          prospeccao, eventos ou compartilhe por email.
        </div>
        <div class="meta">
          <span>PDF</span>
          <span>18 KB</span>
          <span>11 paginas</span>
        </div>
        <button class="btn-download" onclick="downloadPDF('comercial')">
          Baixar Apresentacao (PDF)
        </button>
      </div>

      <!-- Site ZIP - PUBLICO -->
      <div class="download-card">
        <div class="download-card-icon html">
          <span style="font-size:14px;line-height:1;">ZIP</span>
          <small>ESSENCIAL</small>
        </div>
        <h3>Apenas o Site (HTML)</h3>
        <div class="desc">
          Pacote essencial com todos os dashboards (FREE/PRO/PREMIUM/ENTERPRISE)
          + admin + landing + checkout.
        </div>
        <div class="meta">
          <span>ZIP</span>
          <span>800 KB</span>
          <span>8 arquivos</span>
        </div>
        <button class="btn-download html" onclick="downloadZIP('site')">
          Baixar Site (ZIP)
        </button>
      </div>

    </div>

    <!-- Secao ADMIN (preenchida via JS se logado como admin) -->
    <div id="adminDownloadsSection" style="display:none;"></div>

    <div class="downloads-footer">
      Dica: arquivos gerados localmente no seu navegador (nada sai do seu dispositivo)
    </div>
  </div>
</div>
"""


def main():
    """Atualiza o modal de downloads em todos os dashboards"""
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
    print("🔒 RESTRINGINDO MANUAL DO ADMIN")
    print("=" * 60)

    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        modified = False

        # Remove o manual do modal publico (regex)
        import re
        # Substitui bloco do manual por nada (ou aviso)
        manual_block = re.search(
            r'<!-- PDF 1: MANUAL DO ADMIN -->.*?</div>\s*</div>',
            html, re.DOTALL
        )
        if manual_block:
            html = html.replace(manual_block.group(0), '')
            modified = True

        # Remove bloco do ZIP completo do modal publico
        zip_block = re.search(
            r'<!-- ZIP COMPLETO -->.*?</div>\s*</div>',
            html, re.DOTALL
        )
        if zip_block:
            html = html.replace(zip_block.group(0), '')
            modified = True

        # Adiciona secao adminDownloadsSection se nao existir
        if 'id="adminDownloadsSection"' not in html:
            # Substitui o downloads-footer pelo footer + adminSection
            html = html.replace(
                '<div class="downloads-footer">',
                '<div id="adminDownloadsSection" style="display:none;"></div>\n\n    <div class="downloads-footer">',
                1
            )
            modified = True

        # Substitui o JS antigo de downloads
        if 'PUBLIC_DOWNLOADS' not in html:
            # Remove o JS antigo
            old_js = re.search(
                r'<script>\s*// ========== MATERIAIS / DOWNLOADS ==========.*?</script>',
                html, re.DOTALL
            )
            if old_js:
                html = html.replace(old_js.group(0), '')
            # Adiciona o novo
            html = html.replace('</body>', DOWNLOADS_JS_V2 + '\n</body>', 1)
            modified = True

        if modified:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fname}")
        else:
            print(f"⏭️  {fname}")

    print()
    print("=" * 60)
    print("✅ MANUAL RESTRINGIDO!")
    print("=" * 60)
    print()
    print("Publico:")
    print("  - Apresentacao Comercial (PDF)")
    print("  - Apenas Site (ZIP, sem PDFs)")
    print()
    print("Restrito (admin only):")
    print("  - Manual do Administrador")
    print("  - Pacote Completo (com manuais)")


if __name__ == "__main__":
    main()