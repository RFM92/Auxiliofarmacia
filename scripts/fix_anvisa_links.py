#!/usr/bin/env python3
"""
Substitui o link direto para gov.br/anvisa (que estava com 404)
pela pagina interna anvisa.html
"""
import re
from pathlib import Path

OUTPUT = Path("/workspace/output")
ALL_HTML = [
    "dashboard-auxfarmacia.html",
    "dashboard-auxfarmacia-FREE.html",
    "dashboard-auxfarmacia-PRO.html",
    "dashboard-auxfarmacia-PREMIUM.html",
    "dashboard-auxfarmacia-ENTERPRISE.html",
    "dashboard-auxfarmacia-educativo.html",
    "admin.html",
    "landing.html",
    "checkout.html",
    "index.html",
]

# URL antiga da ANVISA (que dava 404)
OLD_URL_404 = "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/bulas"
NEW_URL_INTERNAL = "anvisa.html"

# Outras URLs validas que devem permanecer
VALID_URLS = [
    "https://www.gov.br/anvisa/pt-br/sistemas/bulario-eletronico",
    "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/bulas-e-rotulos/como-acessar-o-bulario-eletronico",
    "https://consultas.anvisa.gov.br/",
    "https://bvsms.saude.gov.br/bvs/saudelegis/anvisa/2011/rdc0020_05_05_2011.html",
    "https://www.gov.br/anvisa/pt-br/assuntos/fiscalizacao-e-monitoramento/propaganda/propaganda",
    "https://www.gov.br/anvisa/pt-br/sistemas",
    "https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2020/ranitidina-entenda-o-recolhimento-voluntario",
    "https://antigo.anvisa.gov.br/",
    "https://bula-anvisa.s3.sa-east-1.amazonaws.com/",
]


def fix_anvisa_links():
    total_files = 0
    total_links = 0
    for fname in ALL_HTML:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        # 1. Substitui a URL 404 pela pagina interna
        # Em diferentes variacoes de formatacao
        variations = [
            (f'href="{OLD_URL_404}"', f'href="{NEW_URL_INTERNAL}"'),
            (f"href='{OLD_URL_404}'", f"href='{NEW_URL_INTERNAL}'"),
            (f'href="{OLD_URL_404}" target="_blank"', f'href="{NEW_URL_INTERNAL}" target="_blank"'),
        ]
        for old, new in variations:
            html = html.replace(old, new)

        # 2. Texto "Bulas ANVISA" agora aponta para anvisa.html
        html = html.replace(
            '>Bulas ANVISA</a>',
            '>Bulas ANVISA</a>'  # Mantem texto
        )

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            changes = original.count(OLD_URL_404) - html.count(OLD_URL_404)
            total_links += changes
            total_files += 1
            print(f"✅ {fname}: {changes} links corrigidos")

    print(f"\n📊 Total: {total_files} arquivos, {total_links} links corrigidos")
    return total_files, total_links


if __name__ == "__main__":
    fix_anvisa_links()