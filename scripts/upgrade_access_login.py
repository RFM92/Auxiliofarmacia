#!/usr/bin/env python3
"""
Login do ACESSO UNICO: hibrido (backend -> fallback local).

Backend: POST {API_BASE}/api/auth/login  -> devolve access_token + user
Fallback: localStorage (auxf_users) -> contas criadas na propria pagina

Alem disso, grava no localStorage o que o dashboard espera:
  auxf_session   { email, plano, expira }
  auxf_api_token  token do backend (para o AUXF_API)
  auxf_api_user   dados do usuario
"""
import re
from pathlib import Path

P = Path('/workspace/output/index.html')
c = P.read_text(encoding='utf-8')

VELHO = """function doAccessLogin() {
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
}"""

NOVO = """function accessApiBase() {
  return (window.location.origin.indexOf('localhost') !== -1 || window.location.protocol === 'file:')
    ? 'http://localhost:8000'
    : window.location.origin;
}

function accessSaveSession(email, plano, expira, token, user) {
  localStorage.setItem('auxf_session', JSON.stringify({
    email: email,
    plano: plano || 'free',
    expira: expira || null
  }));
  localStorage.setItem('auxf_user_name', (user && user.nome) || email.split('@')[0]);
  if (token) {
    localStorage.setItem('auxf_api_token', token);
    localStorage.setItem('auxf_refresh_token', user && user.refresh_token ? user.refresh_token : '');
  }
  if (user) {
    localStorage.setItem('auxf_api_user', JSON.stringify(user));
  }
}

function accessLoginLocal(email, pwd) {
  const users = accessGetUsers();
  const u = users[email];
  if (!u) return { ok: false, motivo: 'Conta não encontrada. Clique em "Criar conta" para se cadastrar.' };
  if (u.senha && u.senha !== accessHash(pwd)) {
    return { ok: false, motivo: 'Senha incorreta. Se não lembrar, use "Esqueci minha senha".' };
  }
  return { ok: true, email: email, plano: u.plano || 'free', expira: u.expira || null, user: u };
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

  accessMsg('Verificando…', 'ok');

  // 1) tenta o backend (fonte de verdade das contas)
  fetch(accessApiBase() + '/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email, password: pwd })
  })
    .then(function (r) {
      if (!r.ok) throw new Error('http_' + r.status);
      return r.json();
    })
    .then(function (data) {
      const u = data.user || {};
      const role = (u.role || '').toLowerCase();
      const plano = (u.plan && u.plan !== 'free') ? u.plan : (role.indexOf('admin') !== -1 ? 'enterprise' : 'free');
      accessSaveSession(email, plano, u.plan_expires_at || null, data.access_token, {
        nome: u.name || u.nome || email.split('@')[0],
        email: email,
        role: u.role || 'user'
      });
      accessMsg('Login realizado! Abrindo a plataforma…', 'ok');
      setTimeout(function () {
        window.location.href = (role.indexOf('admin') !== -1) ? 'admin.html' : 'dashboard-auxfarmacia.html';
      }, 700);
    })
    .catch(function () {
      // 2) fallback: contas locais (criadas nesta pagina)
      const r = accessLoginLocal(email, pwd);
      if (!r.ok) {
        accessMsg(r.motivo, 'erro');
        return;
      }
      accessSaveSession(r.email, r.plano, r.expira, null, { nome: r.user.nome, email: r.email });
      accessMsg('Login realizado! Abrindo a plataforma…', 'ok');
      setTimeout(function () {
        window.location.href = 'dashboard-auxfarmacia.html';
      }, 700);
    });
}"""

if VELHO in c:
    c = c.replace(VELHO, NOVO)
    P.write_text(c, encoding='utf-8')
    print('login do acesso unico -> hibrido (backend + local)')
else:
    print('ATENCAO: padrao do login nao encontrado')
