#!/usr/bin/env python3
"""
Reverte a transformacao errada: ao inves de transformar em array,
adiciona virgulas entre os objetos (eles ja estao no mesmo bloco,
so falta virgula entre).
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


def revert_and_fix():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content
        changes = 0

        # 1. Remove o "[{" que adicionei errado
        # "  // ========== NOME ==========\n  [{"
        # Volta para "  // ========== NOME ==========\n  {"
        # Mas so para as classes que estavam como { (objeto solto)
        classes_to_revert = [
            "ESTATINAS",
            "IBP (Inibidores de Bomba de Pr\u00f3tons)",
            "ANTI-HIPERTENSIVOS",
            "ANTIDIAB\u00c9TICOS ORAIS",
            "ANTICOAGULANTES",
            "HORM\u00d4NIOS TIREOIDIANOS",
            "ANTIDEPRESSIVOS",
            "ANTIAL\u00c9RGICOS",
            "DERMATOL\u00d3GICOS T\u00d3PICOS",
            "ANTICONCEPCIONAIS",
            "AINEs",
        ]

        for classe in classes_to_revert:
            # Remove o [ adicionado
            pattern = f"// ========== {classe} ==========\n  [{{"
            replacement = f"// ========== {classe} ==========\n  {{"
            if pattern in content:
                content = content.replace(pattern, replacement, 1)
                changes += 1

        # 2. Remove o "  ]" que adicionei (linha solta)
        # AINEs termina com "  ]" - precisa remover
        # A estrutura final deveria ser "  }" normal
        # O script anterior adicionou "  ]" depois de cada classe

        # Vou procurar "  ]" sozinho (linha) e remover
        # Mas so os que vem depois de classes problematicas
        # Padrao: "...  }, \n  ]\n\n  // ========== OUTRA CLASSE"
        content = re.sub(
            r"\n  \]\n\n  //\s*={3,}\s*[A-Z]",
            r"\n\n  //\s*={3,}\s*[A-Z]",
            content
        )
        changes += 1

        if content != original:
            path.write_text(content, encoding='utf-8')
            print(f"  ✅ {fname}: {changes} correcoes")
        else:
            print(f"  ⚠️  {fname}: nenhuma mudanca")


if __name__ == "__main__":
    print("🔧 Revertendo transformacao errada...\n")
    revert_and_fix()
    print("\n✅ Concluido!")