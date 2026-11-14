#!/usr/bin/env python3
"""
Mantem APENAS os cursos:
- antihipertensivos
- diabeticos

Remove os outros 6 cursos:
- antibioticos
- aines
- analgesicos
- psicotropicos
- corticoides
- anticoagulantes
"""
import re
from pathlib import Path

CURSOS_PARA_REMOVER = [
    'antibioticos',
    'aines',
    'analgesicos',
    'psicotropicos',
    'corticoides',
    'anticoagulantes',
]


def remover_cursos(html: str) -> tuple[str, int]:
    """Remove cursos específicos. Retorna (html_modificado, qtd_removida)"""
    removidos = 0

    for curso_id in CURSOS_PARA_REMOVER:
        # 1. Remove objeto do array CURSOS
        # Padrão: "    id: 'XXX',\n    title: ...,\n    ...\n  },"
        pattern_obj = re.compile(
            r"    id: '" + re.escape(curso_id) + r"',\n"
            r"(?:.*?\n)*?"
            r"  \},\n",
            re.MULTILINE
        )
        match = pattern_obj.search(html)
        if match:
            html = pattern_obj.sub('', html, count=1)
            removidos += 1

        # 2. Remove do array modules_list (se existir)
        # O modules_list esta em PAYMENTS_JS, entao ja deve ter saido
        # Mas alguns HTMLs tem modules_list em outro lugar

    # 3. Remove dos botoes de filtro na aba cursos
    for curso_id in CURSOS_PARA_REMOVER:
        # Remove botoes do filtro
        pattern_btn = re.compile(
            r'<button class="courses-filter-btn"[^>]*onclick="filterCourses\(\''
            + re.escape(curso_id) + r'\'[^>]*>[^<]+</button>\n\s*',
            re.MULTILINE
        )
        html = pattern_btn.sub('', html)

    return html, removidos


def processar_arquivo(path: Path) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Conta cursos antes
    cursos_antes = len(re.findall(r"id: '(?:antibioticos|aines|analgesicos|antihipertensivos|diabeticos|psicotropicos|corticoides|anticoagulantes)'", html))

    html, qtd = remover_cursos(html)

    # Tambem remove referencias em comentarios/strings
    # E remove de places que possam ter ficado
    for curso_id in CURSOS_PARA_REMOVER:
        # Remove referencias em strings de comparacao ou comentarios
        html = re.sub(
            rf"//\s*{curso_id}.*\n",
            "",
            html
        )

    cursos_depois = len(re.findall(r"id: '(?:antibioticos|aines|analgesicos|antihipertensivos|diabeticos|psicotropicos|corticoides|anticoagulantes)'", html))

    if cursos_antes != cursos_depois:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


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
    print("🎓 Mantendo apenas 2 cursos: Antihipertensivos + Antidiabeticos")
    print("=" * 60)

    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        if processar_arquivo(path):
            print(f"✅ {fname}")
        else:
            print(f"⏭️  {fname} (sem mudancas)")

    print()
    print("=" * 60)
    print("✅ CONCLUIDO!")
    print("=" * 60)
    print()
    print("Cursos mantidos:")
    print("  ❤️  Anti-hipertensivos")
    print("  🩸 Antidiabeticos")
    print()
    print("Cursos removidos:")
    print("  - Antibioticos")
    print("  - AINEs")
    print("  - Analgesicos")
    print("  - Psicotropicos")
    print("  - Corticoides")
    print("  - Anticoagulantes")


if __name__ == "__main__":
    main()