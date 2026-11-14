#!/usr/bin/env python3
"""
CORRECAO: o paywall de medicamentos Pro nunca funcionou.

Causa: os cards reais sao `.med-card` (gerados em renderMedicamentosList) e
NAO tinham atributo `data-id` (o id estava so dentro do onclick). O paywall
procurava `.med-item[data-id]` -> nunca encontrava nenhum elemento ->
os 12 medicamentos Pro ficavam CLICAVEIS no plano FREE.

Correcao:
  1. Adiciona `data-id` no card gerado (fonte: onclick ja tinha o id)
  2. Amplia o seletor do paywall para `.med-card[data-id], .med-item[data-id]`
  3. Garante a classe de estilo `.med-list-item-locked` aplicada ao card
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
FILES = sorted(OUT.glob('dashboard-auxfarmacia*.html'))

# --- 1) gera o card com data-id ---
GERA_VELHO = """      html += '<div role="button" tabindex="0" class="med-card" data-class="' + cls + '" data-name="' + (m.nome || '').toLowerCase() + '" onclick="showMedDetails(\\'' + m.id + '\\')"'"""
GERA_NOVO = """      html += '<div role="button" tabindex="0" class="med-card" data-id="' + m.id + '" data-class="' + cls + '" data-name="' + (m.nome || '').toLowerCase() + '" onclick="showMedDetails(\\'' + m.id + '\\')"'"""

# --- 2) seletor do paywall ---
SEL_VELHO = "document.querySelectorAll('.med-item[data-id]')"
SEL_NOVO = "document.querySelectorAll('.med-card[data-id], .med-item[data-id]')"

total = 0
for p in FILES:
    c = p.read_text(encoding='utf-8')
    orig = c
    n = 0
    if GERA_VELHO in c:
        c = c.replace(GERA_VELHO, GERA_NOVO)
        n += 1
    # aplica o seletor novo em todos os lugares
    n += c.count(SEL_VELHO)
    c = c.replace(SEL_VELHO, SEL_NOVO)
    if c != orig:
        p.write_text(c, encoding='utf-8')
    total += n
    print(f'{p.name}: {n} correcao(oes)')

print(f'\nTotal: {total}')
