#!/usr/bin/env python3
"""
Substitui links href="#" por links reais para as paginas criadas:
- termos.html
- privacidade.html
- sobre.html
- contato.html
- ajuda.html
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

# Padroes a substituir
REPLACEMENTS = [
    # Termos
    (r'<a href="#"([^>]*?)>termos de uso</a>', r'<a href="termos.html"\1 target="_blank">termos de uso</a>'),
    (r'<a href="#"([^>]*?)>Termos de Uso</a>', r'<a href="termos.html"\1 target="_blank">Termos de Uso</a>'),
    (r'<a href="#"([^>]*?)>termos</a>', r'<a href="termos.html"\1 target="_blank">termos</a>'),
    (r'<a href="#"([^>]*?)>Termos</a>', r'<a href="termos.html"\1 target="_blank">Termos</a>'),

    # Privacidade
    (r'<a href="#"([^>]*?)>pol[íi]tica de privacidade</a>', r'<a href="privacidade.html"\1 target="_blank">política de privacidade</a>'),
    (r'<a href="#"([^>]*?)>Pol[íi]tica de Privacidade</a>', r'<a href="privacidade.html"\1 target="_blank">Política de Privacidade</a>'),
    (r'<a href="#"([^>]*?)>privacidade</a>', r'<a href="privacidade.html"\1 target="_blank">privacidade</a>'),

    # Sobre
    (r'<a href="#"([^>]*?)>Sobre</a>', r'<a href="sobre.html"\1 target="_blank">Sobre</a>'),
    (r'<a href="#"([^>]*?)>sobre n[óo]s</a>', r'<a href="sobre.html"\1 target="_blank">sobre nós</a>'),

    # Contato
    (r'<a href="#"([^>]*?)>Contato</a>', r'<a href="contato.html"\1 target="_blank">Contato</a>'),
    (r'<a href="#"([^>]*?)>contato</a>', r'<a href="contato.html"\1 target="_blank">contato</a>'),
    (r'<a href="#"([^>]*?)>Fale Conosco</a>', r'<a href="contato.html"\1 target="_blank">Fale Conosco</a>'),

    # Ajuda
    (r'<a href="#"([^>]*?)>Ajuda</a>', r'<a href="ajuda.html"\1 target="_blank">Ajuda</a>'),
    (r'<a href="#"([^>]*?)>ajuda</a>', r'<a href="ajuda.html"\1 target="_blank">ajuda</a>'),
    (r'<a href="#"([^>]*?)>FAQ</a>', r'<a href="ajuda.html"\1 target="_blank">FAQ</a>'),
    (r'<a href="#"([^>]*?)>Central de Ajuda</a>', r'<a href="ajuda.html"\1 target="_blank">Central de Ajuda</a>'),
]


def fix_broken_links():
    total_files = 0
    total_links = 0
    for fname in ALL_HTML:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        for pattern, replacement in REPLACEMENTS:
            html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            # Conta quantos links foram substituidos
            changes = html.count('target="_blank"') - original.count('target="_blank"')
            total_links += changes
            total_files += 1
            print(f"✅ {fname}: {changes} links corrigidos")

    print(f"\n📊 Total: {total_files} arquivos, {total_links} links corrigidos")
    return total_files, total_links


if __name__ == "__main__":
    fix_broken_links()