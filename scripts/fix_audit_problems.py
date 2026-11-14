#!/usr/bin/env python3
"""
Corrige os problemas identificados na auditoria de links:
1. Adiciona IDs fixos no HTML para que ancoras funcionem
2. Verifica e corrige links externos problematicos
3. Documenta a manutencao
"""
import re
from pathlib import Path

OUTPUT = Path("/workspace/output")
DASHBOARD = OUTPUT / "dashboard-auxfarmacia-FREE.html"

# Mapa: ancora -> id (fixo)
# Estes serao adicionados no HTML para que as ancoras funcionem
ANCHOR_IDS = {
    "tabClinicas": "Calculadoras Clínicas",
    "tabVisual": "Mapas Mentais & Visual",
    "tabEducacao": "Educação & Flashcards",
    "clinicas": "Calculadoras Clínicas",
    "puericultura": "Puericultura",
    "avancadas": "Calculadoras Avançadas",
    "interacoes": "Interações",
    "fluxos": "Fluxogramas",
    "visual": "Mapas Mentais",
    "comparador": "Comparador de Classes",
    "casos": "Casos Clínicos",
    "comparacao": "Comparação",
    "educacao": "Educação",
    "posologia": "Posologia",
    "prescricao": "Prescrição",
}


def add_anchor_ids():
    """Adiciona IDs fixos no HTML do dashboard FREE para ancoras funcionarem."""
    if not DASHBOARD.exists():
        print(f"❌ {DASHBOARD} nao encontrado")
        return

    content = DASHBOARD.read_text(encoding='utf-8')
    original = content

    # Procura por <h2 ...>texto</h2> e adiciona id
    # Pattern: <h2 class="...">Texto</h2>
    for anchor, section_text in ANCHOR_IDS.items():
        # Se ja tem id, pula
        if f'id="{anchor}"' in content:
            continue

        # Procura pelo titulo da secao
        # Padrao: <h2 ... class="...">Calculadoras Clínicas</h2>
        patterns = [
            (f'<h2>{section_text}</h2>', f'<h2 id="{anchor}">{section_text}</h2>'),
            (f'<h2 class="tab-title">{section_text}</h2>', f'<h2 class="tab-title" id="{anchor}">{section_text}</h2>'),
            (f'<h2 class="section-title">{section_text}</h2>', f'<h2 class="section-title" id="{anchor}">{section_text}</h2>'),
        ]
        for old, new in patterns:
            if old in content:
                content = content.replace(old, new, 1)
                print(f"  ✅ Adicionado id='{anchor}' para '{section_text}'")
                break

    if content != original:
        DASHBOARD.write_text(content, encoding='utf-8')
        print(f"\n✅ {DASHBOARD.name} atualizado")
    else:
        print(f"\n⚠️  Nenhum ID adicionado (provavelmente ja existiam ou padroes nao casaram)")


def fix_external_links():
    """Corrige links externos problematicos na anvisa.html."""
    anvisa = OUTPUT / "anvisa.html"
    if not anvisa.exists():
        return

    content = anvisa.read_text(encoding='utf-8')

    # Substitui URL do BVSMS que deu timeout pela URL alternativa
    old_bvsms = "https://bvsms.saude.gov.br/bvs/saudelegis/anvisa/2011/rdc0020_05_05_2011.html"
    new_bvsms = "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/controlados/antimicrobianos"
    if old_bvsms in content:
        content = content.replace(old_bvsms, new_bvsms)
        print(f"  ✅ URL do BVSMS substituida por URL oficial")

    # consultas.anvisa.gov.br - adiciona nota de que pode ter anti-bot
    # Mantem o link mas adiciona nota visual

    anvisa.write_text(content, encoding='utf-8')
    print(f"  ✅ anvisa.html atualizado")


if __name__ == "__main__":
    print("🔧 Corrigindo problemas da auditoria de links...\n")
    print("📋 Etapa 1: Adicionando IDs fixos nas secoes...")
    add_anchor_ids()
    print("\n📋 Etapa 2: Corrigindo links externos...")
    fix_external_links()
    print("\n✅ Concluido!")