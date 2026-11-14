#!/usr/bin/env python3
"""
Corrige o bug critico: o botao "Entrar" do site-header tem onclick="return false;"
que faz nada acontecer. Substitui por onclick="showAuthModal('login')".
Tambem corrige o botao "Criar conta" do header (se existir com mesmo problema).
"""
import re
from pathlib import Path

OUTPUT = Path("/workspace/output")
DASHBOARDS = [
    "dashboard-auxfarmacia.html",
    "dashboard-auxfarmacia-FREE.html",
    "dashboard-auxfarmacia-PRO.html",
    "dashboard-auxfarmacia-PREMIUM.html",
    "dashboard-auxfarmacia-ENTERPRISE.html",
    "dashboard-auxfarmacia-educativo.html",
]


def fix_login_buttons():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content
        changes = 0

        # 1. Substitui o botao Entrar quebrado
        # <a href="#" class="site-btn site-btn-ghost" onclick="return false;">Entrar</a>
        # -> <button type="button" class="site-btn site-btn-ghost" onclick="showAuthModal('login')">Entrar</button>
        old_enter = '<a href="#" class="site-btn site-btn-ghost" onclick="return false;">Entrar</a>'
        new_enter = '<button type="button" class="site-btn site-btn-ghost" onclick="showAuthModal(\'login\')">Entrar</button>'
        if old_enter in content:
            content = content.replace(old_enter, new_enter)
            changes += 1
            print(f"  ✅ {fname}: botao Entrar corrigido")

        # 2. Se tiver "Criar conta" com mesmo problema
        old_register = '<a href="#" class="site-btn site-btn-primary" onclick="return false;">Criar conta</a>'
        new_register = '<button type="button" class="site-btn site-btn-primary" onclick="showAuthModal(\'register\')">Criar conta</button>'
        if old_register in content:
            content = content.replace(old_register, new_register)
            changes += 1
            print(f"  ✅ {fname}: botao Criar conta corrigido")

        # 3. Tambem procura por variantes com "Cadastrar"
        for variant in ['Cadastrar', 'Registrar', 'Sign in', 'Login']:
            old_any = f'<a href="#" class="site-btn" onclick="return false;">{variant}</a>'
            new_any = f'<button type="button" class="site-btn" onclick="showAuthModal(\'register\')">{variant}</button>'
            if old_any in content:
                content = content.replace(old_any, new_any)
                changes += 1
                print(f"  ✅ {fname}: botao {variant} corrigido")

        if content != original:
            path.write_text(content, encoding='utf-8')
            print(f"  📄 {fname}: {changes} botoes corrigidos\n")
        else:
            print(f"  ⚠️  {fname}: nenhuma mudanca necessaria\n")


if __name__ == "__main__":
    print("🔧 Corrigindo botoes de login/cadastro quebrados...\n")
    fix_login_buttons()
    print("✅ Concluido!")