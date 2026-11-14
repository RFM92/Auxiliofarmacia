#!/usr/bin/env python3
"""
Correcao GENERICA: transforma todos os blocos de classes que estao
como "{  objeto1 }  {  objeto2 }" em "[{ objeto1 },{ objeto2 }]"

Identifica padroes:
  // ========== NOMECLASSE ==========
  {
    id: '...',
    ...
  }
  {
    id: '...',
    ...
  }
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

# Classes problematicas (com o mesmo bug do AINEs)
CLASSES = [
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
    # Mais classes que possam ter o mesmo padrao
]


def fix_classes():
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue

        content = path.read_text(encoding='utf-8', errors='ignore')
        original = content
        total_changes = 0

        for classe in CLASSES:
            # Encontra o inicio: // ========== NOME ========== \n {
            pattern_inicio = f"// ========== {classe} ==========\n  {{"
            replacement_inicio = f"// ========== {classe} ==========\n  [{{"

            if pattern_inicio in content:
                content = content.replace(pattern_inicio, replacement_inicio, 1)

                # Agora preciso adicionar virgulas entre os objetos
                # e adicionar ] no final
                idx = content.find(replacement_inicio)
                if idx == -1:
                    continue

                # Encontra a proxima secao
                next_match = re.search(r'\n\n\s*//\s*={3,}\s*[A-Z]', content[idx+10:])
                if not next_match:
                    # Final do script - vou pegar ate o final
                    end_pos = len(content)
                else:
                    end_pos = idx + 10 + next_match.start()

                aines_block = content[idx:end_pos]

                # Processa linha por linha
                lines = aines_block.split('\n')
                new_lines = []
                in_object = False

                for line in lines:
                    new_lines.append(line)
                    if re.match(r'^\s*\{\s*$', line) and not in_object:
                        in_object = True
                    elif re.match(r'^\s*\}\s*$', line) and in_object:
                        # Adiciona virgula se nao tiver
                        if not new_lines[-1].rstrip().endswith(','):
                            new_lines[-1] = new_lines[-1].rstrip() + ','
                        in_object = False

                # Adiciona ] no final
                new_lines.append('  ]')

                new_block = '\n'.join(new_lines)
                content = content[:idx] + new_block + content[end_pos:]
                total_changes += 1
                print(f"  ✅ {fname}: classe {classe} corrigida")

        if content != original:
            path.write_text(content, encoding='utf-8')
            print(f"  📄 {fname}: {total_changes} classes corrigidas\n")
        else:
            print(f"  ⚠️  {fname}: nenhuma mudanca\n")


if __name__ == "__main__":
    print("🔧 Transformando classes em arrays...\n")
    fix_classes()
    print("\n✅ Concluido!")