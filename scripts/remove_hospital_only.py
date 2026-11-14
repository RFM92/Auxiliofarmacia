#!/usr/bin/env python3
"""
Remove medicamentos de uso exclusivamente hospitalar.
Mantem apenas medicamentos com pelo menos uma apresentacao
oral/topica/inalatoria (uso ambulatorial/drogaria).
"""
import re
from pathlib import Path

# Lista de IDs a REMOVER (uso exclusivamente hospitalar)
HOSPITAL_ONLY = {
    'meropenem',        # Apenas IV
    'vancomicina',      # Apenas IV (a forma oral era para C. difficile, retirado)
    'adrenalina',       # Apenas IV/IM (emergencia)
    'ceftriaxona',      # Apenas IM/IV
}

# IDs a MANTER mesmo tendo IV (tem via oral)
HOSPITAL_BUT_HAS_ORAL = {
    'linezolida',       # IV + comp 600mg (oral OK)
    'aciclovir',        # IV + comp 200mg (oral OK)
    'fenobarbital',     # IV + comp 100mg (oral OK)
    'midazolam',        # IV + nasal/oral (oral OK)
    'ondansetrona',     # IV + comp/ODT (oral OK)
    'hidrocortisona',   # IV + comp (oral OK)
    'digoxina',         # Elixir + comp (oral OK)
    'furosemida',       # IV + comp 40mg (oral OK)
}

# Justificativas para documentacao
JUSTIFICATIVAS = {
    'meropenem': 'Antibiotico carbapenemico de uso exclusivamente hospitalar (IV). Nao tem apresentacao oral. Pacientes em uso estao internados.',
    'vancomicina': 'Glicopeptideo de uso exclusivamente hospitalar (IV). A antiga forma oral para C. difficile foi descontinuada no Brasil.',
    'adrenalina': 'Vasopressor de uso exclusivamente hospitalar/emergencia (IV/IM). Nao ha indicacao ambulatorial ou de drogaria.',
    'ceftriaxona': 'Cefalosporina de 3a geracao de uso exclusivamente hospitalar (IM/IV). Nao tem apresentacao oral - existe cefalexina (1a geracao) para uso oral.',
}


def remove_med_from_block(content, med_id):
    """Remove um medicamento de um bloco JSON-like."""
    # Padrao: bloco completo do medicamento
    # Estrutura: { id: 'xxx', nome: '...', ... }
    # Procura pelo id e remove ate a chave fechadora

    pattern = rf"\{{\s*\n\s*id:\s*'{med_id}'.*?\n\s*\}}"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Remove tambem a virgula/separador anterior se houver
        text = match.group(0)
        start, end = match.span()

        # Se bloco anterior termina com virgula, remove a virgula
        if end < len(content) and content[end:end+1] == ',':
            content = content[:end] + content[end+1:]
        elif start > 0 and content[start-1] == ',':
            content = content[:start-1] + content[start:]

        content = content.replace(text, '', 1)
        return content, True
    return content, False


def main():
    output = Path("/workspace/output")

    arquivos = [
        "dashboard-auxfarmacia-FREE.html",
        "dashboard-auxfarmacia-PRO.html",
        "dashboard-auxfarmacia-PREMIUM.html",
        "dashboard-auxfarmacia-ENTERPRISE.html",
        "dashboard-auxfarmacia.html",
        "dashboard-auxfarmacia-educativo.html",
    ]

    print("=" * 60)
    print("🏥 Removendo medicamentos de uso exclusivamente hospitalar")
    print("=" * 60)
    print(f"\nMedicamentos a remover: {len(HOSPITAL_ONLY)}")
    for med, just in JUSTIFICATIVAS.items():
        print(f"  ❌ {med}: {just}")

    print(f"\nMedicamentos mantidos (tem forma oral): {len(HOSPITAL_BUT_HAS_ORAL)}")
    for med in HOSPITAL_BUT_HAS_ORAL:
        print(f"  ✅ {med}")

    print("\n" + "=" * 60)

    total_removed = 0
    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        removed_in_file = 0
        for med_id in HOSPITAL_ONLY:
            html, ok = remove_med_from_block(html, med_id)
            if ok:
                removed_in_file += 1

        if removed_in_file > 0:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fname}: {removed_in_file} removidos")
            total_removed += removed_in_file
        else:
            print(f"⚠️ {fname}: nenhum encontrado")

    print("\n" + "=" * 60)
    print(f"✅ Total: {total_removed // len(arquivos)} medicamentos removidos por arquivo")
    print(f"   ({total_removed} total em {len(arquivos)} arquivos)")
    print("=" * 60)


if __name__ == "__main__":
    main()