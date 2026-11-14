#!/usr/bin/env python3
"""
Corrige o z-index dos modais para que aparecam acima do header.
Problema: header tem z-index 9999, modal tinha 1000 -> modal escondido atras do header.
Solucao: aumentar z-index do modal para 99999 (maior que qualquer outro elemento).
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


def fix_modal_zindex():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content
        changes = 0

        # Padrao 1: .modal { z-index: 1000; }
        content, n1 = re.subn(
            r'(\.modal\s*\{[^}]*?z-index:\s*)1000(\s*;)',
            r'\g<1>99999\g<2>',
            content
        )
        changes += n1

        # Padrao 2: media query .modal { z-index: 10000; }
        content, n2 = re.subn(
            r'(\.modal\s*\{[^}]*?z-index:\s*)10000(\s*;)',
            r'\g<1>99999\g<2>',
            content
        )
        changes += n2

        # Garante que modal-box tbm tem z-index alto
        if '.modal-box' in content and 'z-index' not in content[content.find('.modal-box'):content.find('.modal-box')+200]:
            content = content.replace(
                '.modal-box {',
                '.modal-box { z-index: 100000;',
                1
            )
            changes += 1

        # Garante que o header fica abaixo do modal
        # Procura o seletor de header principal
        if '.topbar' in content and 'position: sticky' in content:
            content = content.replace(
                '.topbar {',
                '.topbar { z-index: 50;',
                1
            )
            changes += 1

        if content != original:
            path.write_text(content, encoding='utf-8')
            print(f"  ✅ {fname}: {changes} ajustes de z-index")
        else:
            print(f"  ⚠️  {fname}: nenhuma mudanca")


if __name__ == "__main__":
    print("🔧 Corrigindo z-index dos modais...\n")
    fix_modal_zindex()
    print("\n✅ Concluido!")