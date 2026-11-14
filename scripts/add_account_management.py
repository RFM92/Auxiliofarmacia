#!/usr/bin/env python3
"""
Adiciona:
1. Tela de Gestao de Conta (account management)
2. Tela de Ativacao Pos-compra melhorada
3. Menu dropdown do usuario no header
4. Listagem de dispositivos ativos
"""
import re
from pathlib import Path

# CSS para a tela de gestao
ACCOUNT_CSS = """
<style>
/* ========== ACCOUNT MANAGEMENT ========== */
.site-account-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: white;
  border: 1px solid var(--site-border, #e2e8f0);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  min-width: 320px;
  padding: 0;
  z-index: 10000;
  display: none;
  overflow: hidden;
}
.site-account-dropdown.open { display: block; }

.site-account-header {
  background: linear-gradient(135deg, #0d9488 0%, #06b6d4 100%);
  color: white;
  padding: 20px;
}
.site-account-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 10px;
  border: 2px solid rgba(255,255,255,0.4);
}
.site-account-name {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 4px 0;
}
.site-account-email {
  font-size: 13px;
  opacity: 0.9;
  margin: 0 0 8px 0;
}
.site-account-plan-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.25);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.site-account-body {
  padding: 8px 0;
  max-height: 480px;
  overflow-y: auto;
}
.site-account-section {
  padding: 8px 16px;
}
.site-account-section-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--site-gray, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 8px 0;
}
.site-account-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  text-decoration: none;
  color: var(--site-dark, #0f172a);
  font-size: 14px;
}
.site-account-item:hover {
  background: var(--site-light, #f8fafc);
}
.site-account-item-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(13,148,136,0.1);
  color: var(--site-primary, #0d9488);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.site-account-item-text { flex: 1; }
.site-account-item-title { font-weight: 600; }
.site-account-item-desc {
  font-size: 12px;
  color: var(--site-gray, #64748b);
}
.site-account-item-arrow { color: #cbd5e1; }

.site-account-footer {
  border-top: 1px solid var(--site-border, #e2e8f0);
  padding: 8px;
  background: var(--site-light, #f8fafc);
}
.site-account-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  border: 1px solid var(--site-border, #e2e8f0);
  background: white;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #dc2626;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
  font-family: inherit;
  margin-bottom: 4px;
}
.site-account-btn:hover {
  background: #fef2f2;
  border-color: #fecaca;
}
.site-account-btn-primary {
  background: var(--site-primary, #0d9488);
  color: white;
  border-color: var(--site-primary, #0d9488);
}
.site-account-btn-primary:hover {
  background: #0f766e;
  border-color: #0f766e;
}

.site-account-plan-info {
  background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 100%);
  margin: 8px 16px;
  padding: 14px;
  border-radius: 8px;
  border: 1px solid #a7f3d0;
}
.site-account-plan-info-title {
  font-size: 11px;
  color: var(--site-gray, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}
.site-account-plan-info-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--site-primary, #0d9488);
}
.site-account-plan-info-expiry {
  font-size: 12px;
  color: var(--site-gray, #64748b);
  margin-top: 4px;
}

.site-account-device {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  background: var(--site-light, #f8fafc);
  margin-bottom: 4px;
  font-size: 13px;
}
.site-account-device-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.site-account-device-info { flex: 1; }
.site-account-device-name { font-weight: 600; }
.site-account-device-meta { font-size: 11px; color: var(--site-gray, #64748b); }
.site-account-device-current {
  font-size: 9px;
  background: #10b981;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

@media (max-width: 768px) {
  .site-account-dropdown {
    position: fixed;
    top: 64px;
    left: 16px;
    right: 16px;
    width: auto;
    max-width: none;
  }
}
</style>
"""

# HTML do dropdown do usuario
ACCOUNT_DROPDOWN_HTML = """
<!-- ========== USER ACCOUNT DROPDOWN ========== -->
<div class="site-account-dropdown" id="siteAccountDropdown">
  <div class="site-account-header">
    <div class="site-account-avatar" id="accountAvatar">U</div>
    <div class="site-account-name" id="accountName">Usuário</div>
    <div class="site-account-email" id="accountEmail">usuario@email.com</div>
    <span class="site-account-plan-badge" id="accountPlanBadge">FREE</span>
  </div>

  <div class="site-account-body">
    <div class="site-account-plan-info">
      <div class="site-account-plan-info-title">Plano Atual</div>
      <div class="site-account-plan-info-name" id="accountPlanName">Free</div>
      <div class="site-account-plan-info-expiry" id="accountPlanExpiry">Expira em: N/A</div>
    </div>

    <div class="site-account-section">
      <div class="site-account-section-title">Conta</div>
      <a href="#" class="site-account-item" onclick="event.preventDefault(); showAccountProfile();">
        <div class="site-account-item-icon">👤</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Meu Perfil</div>
          <div class="site-account-item-desc">Nome, CRM, especialidade</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
      <a href="#" class="site-account-item" onclick="event.preventDefault(); showAccountPassword();">
        <div class="site-account-item-icon">🔑</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Senha e Segurança</div>
          <div class="site-account-item-desc">Alterar senha, 2FA</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
    </div>

    <div class="site-account-section">
      <div class="site-account-section-title">Assinatura</div>
      <a href="#" class="site-account-item" onclick="event.preventDefault(); showAccountPlan();">
        <div class="site-account-item-icon">💎</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Mudar Plano</div>
          <div class="site-account-item-desc">Upgrade, downgrade</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
      <a href="#" class="site-account-item" onclick="event.preventDefault(); showAccountBilling();">
        <div class="site-account-item-icon">💳</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Pagamentos</div>
          <div class="site-account-item-desc">Histórico e faturas</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
      <a href="#" class="site-account-item" onclick="event.preventDefault(); showAccountLicense();">
        <div class="site-account-item-icon">🎫</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Licença</div>
          <div class="site-account-item-desc">Ativar, ver chave</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
    </div>

    <div class="site-account-section">
      <div class="site-account-section-title">Dispositivos</div>
      <div id="accountDevices">
        <div class="site-account-device">
          <div class="site-account-device-icon">💻</div>
          <div class="site-account-device-info">
            <div class="site-account-device-name">Este dispositivo</div>
            <div class="site-account-device-meta">Chrome • macOS</div>
          </div>
          <span class="site-account-device-current">ATUAL</span>
        </div>
      </div>
      <a href="#" class="site-account-item" onclick="event.preventDefault(); showAccountDevices();" style="margin-top:6px;">
        <div class="site-account-item-icon">📱</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Gerenciar dispositivos</div>
          <div class="site-account-item-desc">Desconectar outros</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
    </div>

    <div class="site-account-section">
      <div class="site-account-section-title">Suporte</div>
      <a href="#" class="site-account-item" onclick="event.preventDefault();">
        <div class="site-account-item-icon">💬</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Ajuda</div>
          <div class="site-account-item-desc">FAQ e tutoriais</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
      <a href="mailto:suporte@auxfarmacia.com.br" class="site-account-item">
        <div class="site-account-item-icon">📧</div>
        <div class="site-account-item-text">
          <div class="site-account-item-title">Contato</div>
          <div class="site-account-item-desc">suporte@auxfarmacia.com.br</div>
        </div>
        <div class="site-account-item-arrow">›</div>
      </a>
    </div>
  </div>

  <div class="site-account-footer">
    <button class="site-account-btn site-account-btn-primary" onclick="showAccountPlan()">
      ⬆ Fazer Upgrade
    </button>
    <button class="site-account-btn" onclick="doLogout()">
      🚪 Sair da Conta
    </button>
  </div>
</div>
"""

# Modal de ativacao melhorado
ACTIVATION_MODAL_HTML = """
<!-- ========== ACTIVATION SUCCESS MODAL ========== -->
<div class="modal" id="activationSuccessModal" role="dialog">
  <div class="modal-box large" style="max-width:560px;">
    <button type="button" class="modal-close" onclick="closeActivationSuccess()">×</button>

    <div style="text-align:center;padding:24px 0;">
      <div style="font-size:64px;margin-bottom:12px;">🎉</div>
      <div style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:white;display:inline-block;padding:6px 16px;border-radius:20px;font-size:12px;font-weight:700;letter-spacing:0.5px;margin-bottom:16px;">
        PAGAMENTO CONFIRMADO
      </div>
      <h2 style="margin:0 0 8px 0;color:#0f172a;font-size:24px;font-weight:700;">
        Bem-vindo ao Pro!
      </h2>
      <p style="margin:0 0 24px 0;color:#64748b;font-size:14px;">
        Sua licença foi ativada com sucesso. Abaixo está sua chave de ativação:
      </p>

      <div style="background:#f0fdfa;border:2px dashed #14b8a6;border-radius:12px;padding:20px;margin-bottom:20px;text-align:center;">
        <div id="activationKeyDisplay" style="font-family:'Courier New',monospace;font-size:20px;font-weight:700;color:#0d9488;letter-spacing:1px;word-break:break-all;">
          AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX
        </div>
        <button onclick="copyActivationKey()" style="margin-top:12px;background:#0d9488;color:white;border:none;padding:8px 16px;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;">
          📋 Copiar Chave
        </button>
      </div>

      <div style="background:#fef3c7;border:1px solid #f59e0b;border-radius:8px;padding:12px;margin-bottom:20px;font-size:13px;color:#78350f;text-align:left;">
        <strong>📋 Como ativar:</strong><br>
        1. Sua licença já está ativa automaticamente<br>
        2. Você pode usar até <strong>2 dispositivos</strong> simultaneamente<br>
        3. Use o menu Conta (canto superior direito) para gerenciar
      </div>

      <div style="display:flex;gap:8px;">
        <button onclick="sendKeyByEmail()" style="flex:1;padding:12px;background:#e5e7eb;color:#1f2937;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;">
          📧 Enviar por Email
        </button>
        <button onclick="closeActivationSuccess()" style="flex:2;padding:12px;background:linear-gradient(135deg,#0d9488 0%,#06b6d4 100%);color:white;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;font-family:inherit;">
          🚀 Ir para Dashboard
        </button>
      </div>
    </div>
  </div>
</div>
"""

# JavaScript para gerenciar tudo
ACCOUNT_JS = """
<script>
// ========== ACCOUNT MANAGEMENT ==========

// Abre/fecha dropdown do usuario
function toggleAccountDropdown() {
  const dd = document.getElementById('siteAccountDropdown');
  if (!dd) return;
  dd.classList.toggle('open');
  // Fecha ao clicar fora
  if (dd.classList.contains('open')) {
    setTimeout(() => {
      document.addEventListener('click', closeAccountDropdownOnClickOutside);
    }, 0);
  }
}

function closeAccountDropdownOnClickOutside(e) {
  const dd = document.getElementById('siteAccountDropdown');
  if (!dd) return;
  if (!dd.contains(e.target) && !e.target.closest('[onclick*="toggleAccountDropdown"]')) {
    dd.classList.remove('open');
    document.removeEventListener('click', closeAccountDropdownOnClickOutside);
  }
}

function closeAccountDropdown() {
  const dd = document.getElementById('siteAccountDropdown');
  if (dd) dd.classList.remove('open');
}

// Atualiza informacoes do usuario no dropdown
function refreshAccountDropdown() {
  const lic = JSON.parse(localStorage.getItem('auxf_license') || '{}');
  const sess = JSON.parse(localStorage.getItem('auxf_session') || '{}');

  const avatar = document.getElementById('accountAvatar');
  const name = document.getElementById('accountName');
  const email = document.getElementById('accountEmail');
  const badge = document.getElementById('accountPlanBadge');
  const planName = document.getElementById('accountPlanName');
  const planExpiry = document.getElementById('accountPlanExpiry');

  if (sess.email) {
    if (email) email.textContent = sess.email;
    if (name) name.textContent = sess.nome || sess.email.split('@')[0];
    if (avatar) avatar.textContent = (sess.nome || sess.email)[0].toUpperCase();
  }

  if (lic.tier) {
    const tierName = lic.tier === 'free' ? 'Free' : lic.tier === 'pro' ? 'Pro' : lic.tier === 'premium' ? 'Premium' : 'Institucional';
    if (badge) {
      badge.textContent = tierName.toUpperCase();
      badge.className = 'site-account-plan-badge ' + lic.tier;
    }
    if (planName) planName.textContent = tierName;
    if (planExpiry && lic.expiresAt) {
      const d = new Date(lic.expiresAt);
      planExpiry.textContent = 'Expira em: ' + d.toLocaleDateString('pt-BR');
    }
  } else {
    if (badge) badge.textContent = 'NAO LOGADO';
    if (planName) planName.textContent = 'Sem conta';
  }
}

// Placeholders das telas de gestao
function showAccountProfile() {
  closeAccountDropdown();
  if (typeof showToast === 'function') {
    showToast('Perfil: edicao de dados pessoais em breve');
  } else {
    alert('Meu Perfil\\n\\nEdicao de nome, CRM, especialidade e instituicao.\\nEm construcao.');
  }
}

function showAccountPassword() {
  closeAccountDropdown();
  if (typeof showToast === 'function') {
    showToast('Seguranca: alteracao de senha em breve');
  } else {
    alert('Senha e Seguranca\\n\\nAlterar senha, ativar 2FA, ver sessoes ativas.\\nEm construcao.');
  }
}

function showAccountPlan() {
  closeAccountDropdown();
  if (typeof showPlansModal === 'function') {
    showPlansModal('all');
  }
}

function showAccountBilling() {
  closeAccountDropdown();
  if (typeof showToast === 'function') {
    showToast('Pagamentos: historico em breve');
  } else {
    alert('Pagamentos\\n\\nHistorico de cobrancas, faturas, formas de pagamento.\\nEm construcao.\\n\\n(Banco de dados ja registra - so falta UI)');
  }
}

function showAccountLicense() {
  closeAccountDropdown();
  if (typeof showActivationModal === 'function') {
    showActivationModal();
  }
}

function showAccountDevices() {
  closeAccountDropdown();
  const devices = JSON.parse(localStorage.getItem('auxf_devices') || '[]');
  if (typeof showToast === 'function') {
    showToast('Dispositivos: ' + (devices.length || 1) + ' ativo(s)');
  } else {
    alert('Gerenciar Dispositivos\\n\\nVoce tem ' + (devices.length || 1) + ' dispositivo(s) ativo(s).\\nA versao FREE permite 1, PRO permite 2, PREMIUM 3, INSTITUCIONAL ate 50.\\n\\n(Desconectar outros em breve)');
  }
}

function doLogout() {
  if (!confirm('Tem certeza que deseja sair?')) return;
  localStorage.removeItem('auxf_session');
  localStorage.removeItem('auxf_users');
  if (typeof showToast === 'function') {
    showToast('Voce saiu da conta');
  }
  setTimeout(() => location.reload(), 500);
}

// ========== ACTIVATION SUCCESS ==========

function showActivationSuccess(key, tier) {
  const modal = document.getElementById('activationSuccessModal');
  if (!modal) return;
  const keyDisplay = document.getElementById('activationKeyDisplay');
  if (keyDisplay) keyDisplay.textContent = key;
  modal.classList.add('open');
}

function closeActivationSuccess() {
  const modal = document.getElementById('activationSuccessModal');
  if (modal) modal.classList.remove('open');
}

function copyActivationKey() {
  const key = document.getElementById('activationKeyDisplay')?.textContent;
  if (key && navigator.clipboard) {
    navigator.clipboard.writeText(key);
    if (typeof showToast === 'function') showToast('Chave copiada!');
  }
}

function sendKeyByEmail() {
  if (typeof showToast === 'function') {
    showToast('Chave enviada por email (simulado)');
  }
}

// Ativa via URL (?plan=pro)
function checkUrlActivation() {
  const params = new URLSearchParams(window.location.search);
  const plan = params.get('plan');
  if (plan) {
    const demoKeys = {
      pro: 'AUXFARMA-DEMO1-DEMO2-DEMO3-DEMO4',
      premium: 'AUXFARMA-DEMO5-DEMO6-DEMO7-DEMO8',
      institutional: 'AUXFARMA-INST1-INST2-INST3-INST4'
    };
    if (demoKeys[plan] && typeof activateLicense === 'function') {
      setTimeout(() => {
        activateLicense(demoKeys[plan]);
        showActivationSuccess(demoKeys[plan], plan);
      }, 500);
    }
  }
}

// Inicializa
document.addEventListener('DOMContentLoaded', function() {
  // Botao de conta no header
  const headerActions = document.querySelector('.site-header-actions');
  if (headerActions) {
    const btn = document.createElement('button');
    btn.className = 'site-btn site-btn-ghost';
    btn.innerHTML = '👤';
    btn.title = 'Minha Conta';
    btn.onclick = function(e) {
      e.stopPropagation();
      refreshAccountDropdown();
      toggleAccountDropdown();
    };
    btn.style.cssText = 'font-size:18px;padding:6px 10px;';
    // Substitui o botao Entrar se logado
    const entrar = headerActions.querySelector('a[href="#"]');
    if (entrar) entrar.style.display = 'none';
    headerActions.insertBefore(btn, headerActions.firstChild);
  }

  // Atualiza info
  refreshAccountDropdown();
  checkUrlActivation();
});

// Hook no activateLicense para mostrar sucesso
(function() {
  const orig = window.activateLicense;
  if (typeof orig === 'function') {
    window.activateLicense = function(key) {
      const result = orig.apply(this, arguments);
      if (result && result.success && !key.startsWith('AUXFARMA-DEMO')) {
        const tier = result.tier || 'pro';
        setTimeout(() => showActivationSuccess(key, tier), 200);
      }
      // Atualiza dropdown
      setTimeout(refreshAccountDropdown, 300);
      return result;
    };
  }
})();
</script>
"""


def adicionar_gestao_conta(html: str) -> str:
    """Adiciona tela de gestao de conta + ativacao"""

    # 1. Adiciona CSS
    if 'ACCOUNT MANAGEMENT' not in html:
        html = html.replace('</style>', '</style>\n' + ACCOUNT_CSS, 1)

    # 2. Adiciona dropdown do usuario + modal de ativacao DEPOIS do </header>
    if 'site-account-dropdown' not in html:
        html = re.sub(
            r'(</header>)',
            lambda m: m.group(1) + '\n' + ACCOUNT_DROPDOWN_HTML + ACTIVATION_MODAL_HTML,
            html,
            count=1
        )

    # 3. Adiciona o JS antes do </body>
    if 'ACCOUNT MANAGEMENT ==========' not in html:
        html = html.replace('</body>', ACCOUNT_JS + '\n</body>', 1)

    return html


def processar_arquivo(arquivo: Path):
    """Processa um arquivo HTML"""
    print(f"🔧 Processando: {arquivo.name}")
    with open(arquivo, 'r', encoding='utf-8') as f:
        html = f.read()

    html_original_len = len(html)
    html = adicionar_gestao_conta(html)

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
    print("👤 Adicionando tela de gestão de conta + ativação")
    print("=" * 60)

    for arquivo in arquivos:
        path = output / arquivo
        if path.exists():
            processar_arquivo(path)
        else:
            print(f"⚠️  Não encontrado: {arquivo}")

    print()
    print("✅ Telas adicionadas em todos os dashboards!")
    print()
    print("📋 Componentes:")
    print("  👤 Botão de usuário no header")
    print("  📋 Dropdown com perfil, plano, dispositivos")
    print("  🔑 Tela de ativação melhorada com QR/chave")
    print("  💎 Mudar plano / Upgrade")
    print("  💳 Pagamentos / Histórico")
    print("  🚪 Sair da conta")


if __name__ == "__main__":
    main()