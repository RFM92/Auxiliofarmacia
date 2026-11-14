#!/usr/bin/env python3
"""
Adiciona IDs alias para que tanto #posologia quanto #tabPosologia funcionem.
Adiciona tambem #clinicas, #avancadas, #educacao (que faltam).
"""
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

# Mapeia: id_existente -> [aliases para adicionar via wrapper invisivel]
ALIASES = {
    "tabPosologia": ["posologia"],
    "tabAvancadas": ["avancadas"],
    "tabEducacao": ["educacao"],
    "tabClinicas": ["clinicas"],
    "tabVisual": ["visual"],
    "tabTabCursos": ["cursos", "educacional"],
    "tabTabPrescricao": ["prescricao-nova"],
    "tabComparacao": ["comparacao-nova"],
}


def add_aliases():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content
        added = 0

        for existing_id, aliases in ALIASES.items():
            for alias in aliases:
                if f'id="{alias}"' in content:
                    continue
                # Adiciona um span invisivel com id alias perto do elemento existente
                # Estrategia: adicionar id ao proprio elemento tab-content
                # Procura: id="tabPosologia"
                old = f'id="{existing_id}"'
                # Se ja tem id=, nao duplica
                if f'id="{existing_id}"' in content and 'id=' in content[content.find(old):content.find(old)+200].split('>')[0]:
                    # Adiciona um span com id alias antes do elemento
                    alias_span = f'<span id="{alias}" style="display:block;height:0;visibility:hidden;"></span>'
                    new = alias_span + old
                    if old in content and alias_span not in content:
                        content = content.replace(old, new, 1)
                        added += 1
                        print(f"  ✅ {fname}: alias '{alias}' para '{existing_id}'")
                else:
                    new = f'id="{existing_id}" id="{alias}"'  # HTML nao permite dois ids
                    # Melhor: adicionar via span
                    alias_span = f'<span id="{alias}" style="display:block;height:0;visibility:hidden;"></span>'
                    new = alias_span + old
                    if old in content and alias_span not in content:
                        content = content.replace(old, new, 1)
                        added += 1
                        print(f"  ✅ {fname}: alias '{alias}' para '{existing_id}'")

        if content != original:
            path.write_text(content, encoding='utf-8')
            print(f"  📄 {fname}: {added} aliases adicionados\n")
        else:
            print(f"  ⚠️  {fname}: nenhum alias adicionado\n")


if __name__ == "__main__":
    print("🔧 Adicionando aliases de ancoras...\n")
    add_aliases()
    print("✅ Concluido!")