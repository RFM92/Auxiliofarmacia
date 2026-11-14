#!/usr/bin/env python3
"""
Corrige os links do rodape e do menu de navegacao que estao com href="#"
Substitui por links reais para paginas existentes ou ancora (#secao).
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
]

# Mapa de substituicoes para links do footer/menu
# text -> href_real
FOOTER_LINKS = {
    # Footer dos dashboards
    "Bulas ANVISA": "https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/bulas",
    "Calculadoras": "dashboard-auxfarmacia-FREE.html#tabClinicas",
    "Mapas mentais": "dashboard-auxfarmacia-FREE.html#tabVisual",
    "Flashcards": "dashboard-auxfarmacia-FREE.html#tabEducacao",
    "Suporte": "ajuda.html",
    "LGPD": "privacidade.html",
    "Status": "sobre.html",
    "Termos": "termos.html",
    "Termos de Uso": "termos.html",
    "Politica de Privacidade": "privacidade.html",
    "Pol\u00edtica de Privacidade": "privacidade.html",
    "Contato": "contato.html",
    "Ajuda": "ajuda.html",
    "FAQ": "ajuda.html",
    "Blog": "sobre.html",
    "Carreiras": "contato.html",
    "Sobre": "sobre.html",
    "Sobre nos": "sobre.html",
    "Sobre n\u00f3s": "sobre.html",
}


def fix_footer_links():
    total_files = 0
    total_links = 0
    for fname in ALL_HTML:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        # Substitui cada link do rodape
        for text, href in FOOTER_LINKS.items():
            # Padrao: <a href="#">text</a>
            patterns = [
                (f'<a href="#">{text}</a>', f'<a href="{href}" target="_blank">{text}</a>'),
                (f'<a href="#" class="auth-link">{text}</a>', f'<a href="{href}" class="auth-link" target="_blank">{text}</a>'),
                (f'<a href="#" class="site-link">{text}</a>', f'<a href="{href}" class="site-link" target="_blank">{text}</a>'),
                (f'<a href="#" class="nav-link">{text}</a>', f'<a href="{href}" class="nav-link" target="_blank">{text}</a>'),
                (f'<a href="#">{text}</a>', f'<a href="{href}" target="_blank">{text}</a>'),
            ]
            for old, new in patterns:
                html = html.replace(old, new)

        # Padrao mais generico: <a href="#">text</a> -> usar mapa acima
        # Para links com texto exato
        for text, href in FOOTER_LINKS.items():
            # Se sobrou <a href="#">text</a> sem target, adiciona
            if f'<a href="#">{text}</a>' in html:
                html = html.replace(
                    f'<a href="#">{text}</a>',
                    f'<a href="{href}" target="_blank">{text}</a>'
                )

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            changes = original.count('href="#"') - html.count('href="#"')
            total_links += changes
            total_files += 1
            print(f"✅ {fname}: {changes} links corrigidos")

    print(f"\n📊 Total: {total_files} arquivos, {total_links} links corrigidos")
    return total_files, total_links


if __name__ == "__main__":
    fix_footer_links()