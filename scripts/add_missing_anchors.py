#!/usr/bin/env python3
"""
Adiciona os IDs faltantes para que as ancoras #posologia, #educacao, etc funcionem.
Detecta secoes que ja existem no HTML.
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

# Mapa de ancora -> lista de textos (com e sem acentos)
ANCHOR_SECTIONS = {
    "clinicas": ["Calculadoras Cl\u00ednicas", "Calculadoras Cl&iacute;nicas", "Calculadoras Clinicas"],
    "puericultura": ["Puericultura"],
    "avancadas": ["Calculadoras Avan\u00e7adas", "Calculadoras Avan&ccedil;adas"],
    "interacoes": ["Intera\u00e7\u00f5es", "Intera&ccedil;&otilde;es"],
    "fluxos": ["Fluxogramas", "Decis\u00e3o Cl\u00ednica", "Arvores de Decisao", "\u00c1rvores de Decis\u00e3o"],
    "visual": ["Mapas Mentais"],
    "comparador": ["Comparador de Classes", "Comparador"],
    "casos": ["Casos Cl\u00ednicos", "Casos Cl&iacute;nicos"],
    "comparacao": ["Compara\u00e7\u00e3o", "Compara&ccedil;&atilde;o", "Comparativo"],
    "educacao": ["Educa\u00e7\u00e3o", "Educa&ccedil;&atilde;o", "Educacao"],
    "posologia": ["Posologia"],
    "prescricao": ["Prescri\u00e7\u00e3o", "Prescri&ccedil;&atilde;o", "Prescricao"],
}


def add_anchors():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content
        added = 0

        for anchor, text_variants in ANCHOR_SECTIONS.items():
            # Se ja tem, pula
            if f'id="{anchor}"' in content:
                continue

            for text in text_variants:
                # Procura qualquer h2/h3/h4 que contenha o texto
                # Captura tanto o formato <h3>text</h3> quanto com classes
                pattern = rf'(<h[234]\b[^>]*?)(>)([^<]*?{re.escape(text)}[^<]*?)(</h[234]>)'

                def replacer(m):
                    tag_open = m.group(1)
                    content_inside = m.group(3)
                    if 'id=' in tag_open:
                        return m.group(0)
                    return f'{tag_open} id="{anchor}"{m.group(2)}{content_inside}{m.group(4)}'

                new_content = re.sub(pattern, replacer, content, count=1, flags=re.DOTALL)
                if new_content != content:
                    content = new_content
                    added += 1
                    print(f"  ✅ {fname}: id='{anchor}' para '{text}'")
                    break

        if content != original:
            path.write_text(content, encoding='utf-8')
            print(f"  📄 {fname}: {added} IDs adicionados\n")
        else:
            print(f"  ⚠️  {fname}: nenhum ID adicionado\n")


if __name__ == "__main__":
    print("🔧 Adicionando IDs faltantes para ancoras...\n")
    add_anchors()
    print("✅ Concluido!")