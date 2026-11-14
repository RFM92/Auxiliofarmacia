#!/usr/bin/env python3
"""
Corrige o bug critico: registros orfaos de medicamentos hospitalares
(Meropenem, Vancomicina IV, Adrenalina, Ceftriaxona) que ficaram soltos
dentro do array MEDS_EXTRAS.

O script remove_hospital_only.py removeu a chave mas deixou o objeto,
causando erro de sintaxe JS.
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


def fix_orphaned_meds():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content

        # Estrategia: dentro de MEDS_EXTRAS, remover objetos orfaos
        # que NAO tem campo "id" no inicio
        # Padrao: array de objetos, cada um deve ter "id": "...":
        # Procura blocos que sao objetos sem "id"

        # Pattern: encontrar "const MEDS_EXTRAS = [" ate o final "];"
        meds_match = re.search(
            r'const\s+MEDS_EXTRAS\s*=\s*\[(.*?)\n\s*\];',
            content,
            re.DOTALL
        )

        if not meds_match:
            print(f"  ⚠️  {fname}: MEDS_EXTRAS nao encontrado")
            continue

        meds_content = meds_match.group(1)
        meds_start = meds_match.start(1)
        meds_end = meds_match.end(1)

        # Quebrar em items do array
        # Cada item comeca com { e termina com }
        # Vamos balancear chaves
        items = []
        depth = 0
        current_item_start = None

        for i, c in enumerate(meds_content):
            if c == '{':
                if depth == 0:
                    current_item_start = i
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0 and current_item_start is not None:
                    items.append({
                        'start': current_item_start,
                        'end': i + 1,
                        'text': meds_content[current_item_start:i+1]
                    })
                    current_item_start = None

        print(f"  {fname}: {len(items)} items encontrados no MEDS_EXTRAS")

        # Filtrar items que tem campo "id" (sao validos)
        # Os orfaos nao tem "id"
        valid_items = []
        removed_count = 0
        for item in items:
            text = item['text']
            # Verifica se tem "id" como chave
            if re.search(r'["\']id["\']\s*:', text):
                valid_items.append(item)
            else:
                removed_count += 1
                # Mostra o que esta sendo removido (primeira linha)
                first_line = text.split('\n')[1] if '\n' in text else text[:80]
                print(f"    ❌ Removendo orfao: {first_line.strip()[:70]}")

        if removed_count == 0:
            print(f"  ✅ {fname}: nenhum orfao encontrado")
            continue

        # Reconstruir o conteudo
        new_meds = '\n  ' + ',\n  '.join(item['text'] for item in valid_items) + '\n'
        new_meds_full = 'const MEDS_EXTRAS = [' + new_meds + '];'

        # Substituir no conteudo
        old_meds_full = meds_match.group(0)
        content = content.replace(old_meds_full, new_meds_full)

        if content != original:
            path.write_text(content, encoding='utf-8')
            print(f"  ✅ {fname}: {removed_count} orfaos removidos\n")
        else:
            print(f"  ⚠️  {fname}: nenhuma mudanca\n")


if __name__ == "__main__":
    print("🔧 Removendo registros orfaos de medicamentos hospitalares...\n")
    fix_orphaned_meds()
    print("\n✅ Concluido!")