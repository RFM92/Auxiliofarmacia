#!/usr/bin/env python3
"""
Reformula a tela inicial (index.html) para ACESSO UNICO:
  - Hero vira card de login (email + senha) em vez de botao para outra pagina
  - Se ja logado: saudacao + botao "Entrar no site" + plano atual
  - Botao "Entrar / Criar conta" da auth-bar aponta para o proprio card
  - Post-login: redireciona para o dashboard master (paywall por currentPlan)
"""
import re
from pathlib import Path

P = Path('/workspace/output/index.html')
c = P.read_text(encoding='utf-8')

# ---------------------------------------------------------------- 1. CSS
CSS_NOVO = """
/* ============================================================
   ACESSO UNICO - CARD DE LOGIN (v2026.11)
   ============================================================ */
.access-card {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 28px;
  max-width: 440px;
  margin: 28px auto 0;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.35);
  text-align: left;
}
.access-card h2 {
  font-size: 20px;
  color: var(--text);
  margin-bottom: 4px;
  font-family: var(--font-serif);
}
.access-card .access-sub {
  font-size: 13px;
  color: var(--text-dim);
  margin-bottom: 20px;
}
.access-field { margin-bottom: 14px; }
.access-field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-dim);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.access-field input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 9px;
  border: 1px solid var(--border-light);
  background: var(--bg);
  color: var(--text);
  font-size: 15px;
  font-family: inherit;
  box-sizing: border-box;
}
.access-field input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.16);
}
.access-field input::placeholder { color: var(--text-dim); opacity: 0.7; }
.access-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  flex-wrap: wrap;
}
.access-actions .btn { flex: 1 1 auto; justify-content: center; }
.access-msg {
  margin-top: 14px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  display: none;
}
.access-msg.erro {
  display: block;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}
.access-msg.ok {
  display: block;
  background: rgba(20, 184, 166, 0.12);
  border: 1px solid rgba(20, 184, 166, 0.4);
  color: var(--primary);
}
.access-links {
  margin-top: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--text-dim);
}
.access-links a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}
.access-links a:hover { text-decoration: underline; }
.access-hint {
  margin-top: 16px;
  padding: 12px;
  border-radius: 9px;
  background: rgba(20, 184, 166, 0.07);
  border: 1px dashed rgba(20, 184, 166, 0.3);
  font-size: 12.5px;
  color: var(--text-dim);
  line-height: 1.6;
}
.access-hint code {
  background: rgba(255, 255, 255, 0.07);
  padding: 1px 6px;
  border-radius: 4px;
  color: var(--primary);
  font-size: 12px;
}
.welcome-box {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 26px 28px;
  max-width: 480px;
  margin: 28px auto 0;
  text-align: center;
}
.welcome-box .wb-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 6px;
}
.welcome-box .wb-plan {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
  margin-bottom: 18px;
}
.welcome-box .wb-msg {
  font-size: 14px;
  color: var(--text-dim);
  margin-bottom: 20px;
  line-height: 1.6;
}
@media (max-width: 520px) {
  .access-card, .welcome-box { padding: 22px 18px; }
}
"""

# ---------------------------------------------------------------- 2. HERO
HERO_VELHO_INI = '<section class="hero">'
HERO_VELHO = """<section class="hero">
  <div class="hero-inner" id="conteudo-principal">>
    <div class="hero-badge">✨ v2026.08 — Atualizado em 23/07/2026</div>
    <h1>Guia Médico-Farmacêutico<br><span class="accent">Adulto e Pediátrico</span></h1>
    <p class="hero-sub">Plataforma educacional completa para profissionais de farmácia e drogarias. Calculadoras clínicas, bulas oficiais, mapas mentais, flashcards interativos e cursos.</p>
    <div class="hero-actions">
      <a href="dashboard-auxfarmacia-FREE.html" class="btn btn-primary">📊 Acessar Dashboard FREE</a>
      <a href="#planos" class="btn btn-ghost">💎 Ver Planos</a>
    </div>
    <div class="hero-stats">
      <div class="stat">
        <div class="stat-value">61</div>
        <div class="stat-label">Medicamentos</div>
      </div>
      <div class="stat">
        <div class="stat-value">50</div>
        <div class="stat-label">Classes</div>
      </div>
      <div class="stat">
        <div class="stat-value">9</div>
        <div class="stat-label">Calculadoras</div>
      </div>
      <div class="stat">
        <div class="stat-value">11</div>
        <div class="stat-label">Vídeos</div>
      </div>
    </div>
  </div>
</section>"""

HERO_NOVO = """<section class="hero">
  <div class="hero-inner" id="conteudo-principal">
    <div class="hero-badge">✨ v2026.08 — Atualizado em 23/07/2026</div>
    <h1>Guia Médico-Farmacêutico<br><span class="accent">Adulto e Pediátrico</span></h1>
    <p class="hero-sub">Plataforma educacional completa para profissionais de farmácia e drogarias. Calculadoras clínicas, bulas oficiais, mapas mentais, flashcards interativos e cursos.</p>

    <!-- ========== ACESSO UNICO ========== -->
    <div id="accessGuest">
      <form class="access-card" id="accessForm" onsubmit="event.preventDefault(); doAccessLogin();">
        <h2>Acessar a plataforma</h2>
        <p class="access-sub">Entre com sua conta para abrir os módulos liberados no seu plano.</p>

        <div class="access-field">
          <label for="accessEmail">E-mail</label>
          <input type="email" id="accessEmail" placeholder="seu.email@profissional.com" required autocomplete="email">
        </div>

        <div class="access-field">
          <label for="accessPassword">Senha</label>
          <input type="password" id="accessPassword" placeholder="Sua senha" required autocomplete="current-password">
        </div>

        <div class="access-msg" id="accessMsg" role="status" aria-live="polite"></div>

        <div class="access-actions">
          <button type="submit" class="btn btn-primary">🔓 Entrar</button>
          <a href="login.html#register" class="btn btn-ghost">✨ Criar conta</a>
        </div>

        <div class="access-links">
          <a href="login.html#forgot">Esqueci minha senha</a>
        </div>

        <div class="access-hint">
          <strong>Acesso de demonstração:</strong> use <code>admin@auxfarmacia.com.br</code> / <code>admin123</code>.<br>
          Novos registros entram no plano <strong>FREE</strong> e podem ser atualizados a qualquer momento.
        </div>
      </form>
    </div>

    <div id="accessLogged" style="display:none;">
      <div class="welcome-box">
        <div class="wb-name" id="wbName">Olá!</div>
        <div class="wb-plan" id="wbPlan">FREE</div>
        <div class="wb-msg" id="wbMsg">
          Sua sessão está ativa. Os módulos liberados para o seu plano já estão disponíveis.
        </div>
        <div class="access-actions">
          <a href="dashboard-auxfarmacia.html" class="btn btn-primary">📊 Entrar no site</a>
          <button type="button" class="btn btn-ghost" onclick="doAccessLogout()">🚪 Sair</button>
        </div>
      </div>
    </div>
    <!-- ========== FIM ACESSO UNICO ========== -->

    <div class="hero-stats">
      <div class="stat">
        <div class="stat-value">61</div>
        <div class="stat-label">Medicamentos</div>
      </div>
      <div class="stat">
        <div class="stat-value">50</div>
        <div class="stat-label">Classes</div>
      </div>
      <div class="stat">
        <div class="stat-value">9</div>
        <div class="stat-label">Calculadoras</div>
      </div>
      <div class="stat">
        <div class="stat-value">11</div>
        <div class="stat-label">Vídeos</div>
      </div>
    </div>
  </div>
</section>"""

# ---------------------------------------------------------------- 3. JS
JS_NOVO = """
/* ============================================================
   ACESSO UNICO - LOGIN / LOGOUT / SESSAO
   ============================================================ */
function accessHash(pwd) {
  if (!pwd) return '';
  if (pwd.startsWith('h_')) return pwd;
  let h = 0;
  for (let i = 0; i < pwd.length; i++) {
    h = ((h << 5) - h) + pwd.charCodeAt(i);
    h = h & h;
  }
  return 'h_' + Math.abs(h).toString(36);
}

function accessMsg(texto, tipo) {
  const el = document.getElementById('accessMsg');
  if (!el) return;
  el.textContent = texto;
  el.className = 'access-msg ' + (tipo || 'erro');
}

function accessGetUsers() {
  try {
    const raw = localStorage.getItem('auxf_users');
    const u = raw ? JSON.parse(raw) : null;
    return u && typeof u === 'object' ? u : {};
  } catch (e) { return {}; }
}

function accessSetUsers(u) {
  localStorage.setItem('auxf_users', JSON.stringify(u));
}

function accessGetSession() {
  try {
    const raw = localStorage.getItem('auxf_session');
    const s = raw ? JSON.parse(raw) : null;
    return s && s.email ? s : null;
  } catch (e) { return null; }
}

function doAccessLogin() {
  const emailEl = document.getElementById('accessEmail');
  const pwdEl = document.getElementById('accessPassword');
  const email = (emailEl ? emailEl.value : '').trim().toLowerCase();
  const pwd = pwdEl ? pwdEl.value : '';

  if (!email || !pwd) {
    accessMsg('Preencha e-mail e senha.', 'erro');
    return;
  }

  const users = accessGetUsers();
  const user = users[email];

  if (!user) {
    accessMsg('Conta não encontrada. Clique em "Criar conta" para se cadastrar.', 'erro');
    return;
  }
  if (user.senha && user.senha !== accessHash(pwd)) {
    accessMsg('Senha incorreta. Se não lembrar, use "Esqueci minha senha".', 'erro');
    return;
  }

  const plano = user.plano || 'free';
  localStorage.setItem('auxf_session', JSON.stringify({
    email: email,
    plano: plano,
    expira: user.expira || null
  }));
  if (typeof user.nome !== 'undefined') {
    localStorage.setItem('auxf_user_name', user.nome || email.split('@')[0]);
  }

  accessMsg('Login realizado! Abrindo a plataforma…', 'ok');
  setTimeout(function () {
    window.location.href = 'dashboard-auxfarmacia.html';
  }, 700);
}

function doAccessLogout() {
  localStorage.removeItem('auxf_session');
  localStorage.removeItem('auxf_user_name');
  refreshAccessState();
}

function refreshAccessState() {
  const guest = document.getElementById('accessGuest');
  const logged = document.getElementById('accessLogged');
  const barGuest = document.getElementById('userGuest');
  const barLogged = document.getElementById('userLogged');
  const s = accessGetSession();

  if (s) {
    if (guest) guest.style.display = 'none';
    if (logged) logged.style.display = 'block';
    if (barGuest) barGuest.style.display = 'none';
    if (barLogged) barLogged.style.display = 'flex';

    const users = accessGetUsers();
    const u = users[s.email] || {};
    const nome = u.nome || localStorage.getItem('auxf_user_name') || s.email.split('@')[0];
    const plano = (s.plano || 'free').toUpperCase();

    const wbName = document.getElementById('wbName');
    const wbPlan = document.getElementById('wbPlan');
    if (wbName) wbName.textContent = 'Olá, ' + nome.split(' ')[0] + '!';
    if (wbPlan) wbPlan.textContent = plano;

    const mini = document.getElementById('userNameMini');
    const planMini = document.getElementById('userPlanMini');
    const av = document.getElementById('userAvatarMini');
    if (mini) mini.textContent = nome;
    if (planMini) planMini.textContent = plano;
    if (av) av.textContent = nome.split(' ').map(function (p) { return p[0]; }).slice(0, 2).join('').toUpperCase();
  } else {
    if (guest) guest.style.display = 'block';
    if (logged) logged.style.display = 'none';
    if (barGuest) barGuest.style.display = 'block';
    if (barLogged) barLogged.style.display = 'none';
  }
}

document.addEventListener('DOMContentLoaded', refreshAccessState);
"""

# ---------------------------------------------------------------- aplicacao
if 'ACESSO UNICO - CARD DE LOGIN' not in c:
    idx = c.find('</style>')
    c = c[:idx] + CSS_NOVO + c[idx:]
    print('CSS do access-card inserido')

if 'ACESSO UNICO ==========' not in c:
    if HERO_VELHO in c:
        c = c.replace(HERO_VELHO, HERO_NOVO)
        print('hero substituído por card de acesso unico')
    else:
        # fallback: substitui so o bloco hero-actions
        antigo = """    <div class="hero-actions">
      <a href="dashboard-auxfarmacia-FREE.html" class="btn btn-primary">📊 Acessar Dashboard FREE</a>
      <a href="#planos" class="btn btn-ghost">💎 Ver Planos</a>
    </div>"""
        c = c.replace(antigo, HERO_NOVO[HERO_NOVO.index('    <!-- ========== ACESSO UNICO'):HERO_NOVO.index('    <!-- ========== FIM ACESSO UNICO')] + '    <!-- ========== FIM ACESSO UNICO ========== -->')
        print('hero-actions substituído (fallback)')

# botao da auth-bar -> rola para o card de login
c = c.replace(
    """<button class="btn btn-primary" onclick="window.location.href='login.html'">🔑 Entrar / Criar conta</button>""",
    """<button class="btn btn-primary" onclick="goAccessLogin()">🔑 Entrar / Criar conta</button>"""
)
if 'function goAccessLogin' not in c:
    c = c.replace('function refreshAccessState() {',
                  """function goAccessLogin() {
  const el = document.getElementById('accessEmail');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(function () { el.focus(); }, 350);
  } else {
    window.location.href = 'login.html';
  }
}

function refreshAccessState() {""")

# JS do acesso unico
if 'ACESSO UNICO - LOGIN / LOGOUT / SESSAO' not in c:
    idx = c.rfind('</script>')
    c = c[:idx] + JS_NOVO + '\n' + c[idx:]
    print('JS do acesso unico inserido')

# ensure o dashboard link correto no bloco logged da auth-bar
c = c.replace('<a href="dashboard-auxfarmacia-FREE.html" class="btn btn-ghost">📊 Dashboard</a>',
              '<a href="dashboard-auxfarmacia.html" class="btn btn-ghost">📊 Entrar no site</a>')

P.write_text(c, encoding='utf-8')
print(f'index.html reescrito: {len(c)} bytes')
