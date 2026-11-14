#!/usr/bin/env python3
"""
Correcao CIRURGICA: remove APENAS os objetos orfaos
(blocos que nao tem "id" como chave de abertura)
dentro do array MEDS_EXTRAS.

Estrategia: encontrar blocos que tem },  ou ],  como delimitador
e cuja linha anterior NAO tem "id" como chave.
"""
import re
from pathlib import Path

OUTPUT = Path("/workspace/output")
DASHBOARDS = [
    "dashboard-auxfarmacia.html",
    "dashboard-auxfarmacia-FREE.html",
    "dashboard-auxfarmacia-PRO.html",
    "dashboard-auxfarmacia-PREMIUM.html",
    "dashboard-auxfarmasia-ENTERPRISE.html",  # possivel typo
    "dashboard-auxfarmacia-ENTERPRISE.html",
    "dashboard-auxfarmacia-educativo.html",
]


def fix_orphaned_v2():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            print(f"  ❌ {fname} nao existe")
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content

        # Estrategia: encontrar o array MEDS_EXTRAS e processar item por item
        # Um item "valido" tem { id: "...", ...
        # Um item "orfao" tem { rotulo: "Meningite (alta dose)", ...  (sem id)

        # Encontra o inicio e fim do array
        m = re.search(r'(const\s+MEDS_EXTRAS\s*=\s*\[)', content)
        if not m:
            print(f"  ⚠️  {fname}: MEDS_EXTRAS nao encontrado")
            continue

        # Procura o ] correspondente
        start = m.end()
        # Encontra o ] de fechamento do array
        depth = 0
        end = start
        for i in range(start, min(start + 50000, len(content))):
            if content[i] == '[':
                depth += 1
            elif content[i] == ']':
                if depth == 0:
                    end = i
                    break
                depth -= 1
            elif content[i] == '{':
                depth += 1
            elif content[i] == '}':
                if depth > 0:
                    depth -= 1

        array_content = content[start:end+1]
        # Remove os delimitadores
        inner = array_content[1:-1]  # remove [ e ]

        # Quebra por objetos no nivel 0
        items = []
        depth = 0
        current_start = None

        for i, c in enumerate(inner):
            if c == '{':
                if depth == 0:
                    current_start = i
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0 and current_start is not None:
                    items.append(inner[current_start:i+1])
                    current_start = None

        # Filtra items que tem "id" como chave
        valid = []
        removed = 0
        for item_text in items:
            # Verifica se tem "id" como chave
            if re.search(r"['\"]id['\"]\s*:", item_text):
                valid.append(item_text)
            else:
                removed += 1
                # Nao remove ainda - mostra o que vai ser removido
                first_line = item_text.split('\n')[1] if '\n' in item_text else item_text[:80]
                print(f"    Removendo: {first_line.strip()[:70]}")

        print(f"  {fname}: {len(items)} -> {len(valid)} validos ({removed} orfaos)")

        # Reconstroi
        if valid:
            new_array = '[\n  ' + ',\n  '.join(item.strip() for item in valid) + '\n]'
        else:
            new_array = '[]'

        new_content = content[:start] + new_array + content[end+1:]

        if new_content != original:
            path.write_text(new_content, encoding='utf-8')
            print(f"  ✅ {fname}: {removed} orfaos removidos")
        else:
            print(f"  ⚠️  {fname}: nenhuma mudanca")


if __name__ == "__main__":
    print("🔧 Correcao CIRURGICA de orfaos no MEDS_EXTRAS...\n")
    fix_orphaned_v2()
    print("\n✅ Concluido!")