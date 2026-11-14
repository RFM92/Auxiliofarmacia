#!/usr/bin/env python3
"""
CORRECAO: o paywall deve aplicar o plano da SESSAO mesmo quando o usuario
existe apenas no backend (nao em auxf_users local).

Antes: `if (!user) return;` abortava antes de definir currentPlan ->
todo mundo ficava travado no plano 'free', mesmo apos login valido
no backend (caso do admin e de qualquer conta criada via API).

Agora: a sessao e a fonte de verdade do plano; auxf_users e so um complemento.
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
FILES = sorted(OUT.glob('dashboard-auxfarmacia*.html'))

# --- A) bloco loadSession (AuthSync) ---
A_VELHO = """      if (user) {
        // Define variáveis globais (compatível com dashboard)
        window.currentUser = user;
        window.currentUser.email = user.email || session.email;
        window.currentPlan = session.plano || user.plano || 'free';
        console.log('[AuthSync] Sessao carregada:', user.email);
      }"""
A_NOVO = """      // A SESSAO e a fonte de verdade do plano (usuario pode existir
      // apenas no backend, sem registro em auxf_users local).
      window.currentUser = user || { nome: session.email.split('@')[0], email: session.email };
      window.currentUser.email = (user && user.email) || session.email;
      window.currentPlan = session.plano || (user && user.plano) || 'free';
      console.log('[AuthSync] Sessao carregada:', session.email, '- Plano:', window.currentPlan);"""

# --- B) bloco loadSession (Dashboard) ---
B_VELHO = """      if (user) {
        window.currentUser = user;
        window.currentUser.email = user.email || session.email;
        window.currentPlan = session.plano || user.plano || 'free';
        console.log('[Dashboard] Sessao restaurada:', user.email, '- Plano:', window.currentPlan);
      } else {
        console.warn('[Dashboard] Sessao aponta para usuario inexistente:', session.email);"""
B_NOVO = """      // SESSAO manda no plano: conta pode estar so no backend
      window.currentUser = user || { nome: session.email.split('@')[0], email: session.email };
      window.currentUser.email = (user && user.email) || session.email;
      window.currentPlan = session.plano || (user && user.plano) || 'free';
      console.log('[Dashboard] Sessao restaurada:', session.email, '- Plano:', window.currentPlan);
      if (!user) {
        console.warn('[Dashboard] Sessao sem registro local (conta do backend):', session.email);"""

# --- C) bloco loadSession (AuxAuth / site) ---
C_VELHO = """      const users = JSON.parse(localStorage.getItem('auxf_users') || '{}');
      const user = users[session.email] || users[session.email.toLowerCase()];
      if (!user) return;
      
      // Define currentUser/currentPlan globais (dashboard espera isso)
      window.currentUser = user;
      window.currentUser.email = user.email || session.email;
      window.currentPlan = session.plano || user.plano || 'free';"""
C_NOVO = """      const users = JSON.parse(localStorage.getItem('auxf_users') || '{}');
      const user = users[session.email] || users[session.email.toLowerCase()];
      
      // Define currentUser/currentPlan globais (dashboard espera isso).
      // Nao aborta se nao houver registro local: a sessao ja traz o plano.
      window.currentUser = user || { nome: session.email.split('@')[0], email: session.email };
      window.currentUser.email = (user && user.email) || session.email;
      window.currentPlan = session.plano || (user && user.plano) || 'free';"""

SUBS = [(A_VELHO, A_NOVO), (B_VELHO, B_NOVO), (C_VELHO, C_NOVO)]

total = 0
for p in FILES:
    c = p.read_text(encoding='utf-8')
    orig = c
    n = 0
    for velho, novo in SUBS:
        if velho in c:
            c = c.replace(velho, novo)
            n += 1
    if c != orig:
        p.write_text(c, encoding='utf-8')
    total += n
    print(f'{p.name}: {n} ponto(s) de leitura de plano corrigido(s)')

print(f'\nTotal: {total} correcoes')
