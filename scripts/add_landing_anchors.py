#!/usr/bin/env python3
"""
Adiciona o id='recursos' na landing.html para que o link funcione
"""
from pathlib import Path

OUTPUT = Path("/workspace/output")
LANDING = OUTPUT / "landing.html"

if not LANDING.exists():
    print(f"❌ {LANDING} nao encontrado")
    exit()

content = LANDING.read_text(encoding='utf-8')
original = content

# Procura a secao "Recursos" na landing
# O padrao deve ser algo como <h2>Recursos</h2> ou <section ...>Recursos</section>
import re

# Tenta adicionar id em diferentes pontos
patterns = [
    # Adiciona id no h2 que contem "Recursos"
    (r'(<h2[^>]*)(>\s*Recursos\s*</h2>)', r'\1 id="recursos"\2'),
    # Adiciona em section
    (r'(<section[^>]*)(>\s*<h2[^>]*>\s*Recursos)', r'\1 id="recursos"\2'),
    # Adiciona antes do <h2>Recursos
    (r'(<h2[^>]*>Recursos</h2>)', r'<section id="recursos"><h2>Recursos</h2>'),
    # Ultima opcao: cria um span invisivel
]

added = False
for old, new in patterns:
    if re.search(old, content):
        content = re.sub(old, new, content, count=1)
        added = True
        print(f"  ✅ Adicionado id='recursos' na landing")
        break

if not added:
    # Adiciona um span invisivel no inicio do body
    span = '<span id="recursos" style="display:block;height:0;visibility:hidden;"></span>'
    if span not in content:
        content = content.replace('<body>', f'<body>\n{span}', 1)
        print(f"  ✅ Span invisivel com id='recursos' adicionado no inicio do body")
        added = True

if content != original:
    LANDING.write_text(content, encoding='utf-8')
    print(f"  📄 landing.html atualizado")
else:
    print(f"  ⚠️  Nenhuma alteracao feita")