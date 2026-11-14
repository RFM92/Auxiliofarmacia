#!/usr/bin/env python3
"""Preview da Biblioteca de Videos"""
import re
import subprocess
from pathlib import Path

OUTPUT = Path("/workspace/output/atualizacoes")

PREVIEW_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <defs>
    <linearGradient id="bgVL" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f0fdfa"/>
      <stop offset="100%" stop-color="#ccfbf1"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1400" fill="url(#bgVL)"/>

  <!-- Header -->
  <text x="600" y="80" font-size="36" font-weight="700" fill="#0f766e" text-anchor="middle" font-family="DejaVu-Serif">📺 Biblioteca de Videos</text>
  <text x="600" y="115" font-size="16" fill="#0d9488" text-anchor="middle">Aulas em portugues de canais medicos verificados</text>

  <!-- Grid de videos -->
  <!-- Card 1 -->
  <rect x="40" y="160" width="365" height="160" fill="white" rx="12" stroke="#dc2626" stroke-width="3"/>
  <rect x="40" y="160" width="6" height="160" fill="#dc2626"/>
  <rect x="60" y="180" width="50" height="50" fill="#fef2f2" rx="8"/>
  <text x="85" y="215" font-size="24" text-anchor="middle">🎬</text>
  <text x="125" y="195" font-size="16" font-weight="700" fill="#7f1d1d">Educacao Farmaceutica</text>
  <text x="125" y="215" font-size="14" font-weight="700" fill="#7f1d1d">- HAS</text>
  <text x="60" y="260" font-size="13" fill="#64748b">Medicao correta da pressao</text>
  <text x="60" y="278" font-size="13" fill="#64748b">+ classificacao</text>
  <rect x="60" y="290" width="60" height="22" fill="#dc2626" rx="4"/>
  <text x="90" y="305" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 10:24</text>

  <!-- Card 2 -->
  <rect x="425" y="160" width="365" height="160" fill="white" rx="12" stroke="#f59e0b" stroke-width="3"/>
  <rect x="425" y="160" width="6" height="160" fill="#f59e0b"/>
  <rect x="445" y="180" width="50" height="50" fill="#fff7ed" rx="8"/>
  <text x="470" y="215" font-size="24" text-anchor="middle">💊</text>
  <text x="510" y="195" font-size="16" font-weight="700" fill="#92400e">HAS - Tratamento</text>
  <text x="510" y="215" font-size="14" font-weight="700" fill="#92400e">Farmacologico</text>
  <text x="445" y="260" font-size="13" fill="#64748b">IECA, BRA, BCC, diureticos</text>
  <text x="445" y="278" font-size="13" fill="#64748b">em uma aula completa</text>
  <rect x="445" y="290" width="60" height="22" fill="#f59e0b" rx="4"/>
  <text x="475" y="305" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 20:15</text>

  <!-- Card 3 -->
  <rect x="810" y="160" width="365" height="160" fill="white" rx="12" stroke="#7c3aed" stroke-width="3"/>
  <rect x="810" y="160" width="6" height="160" fill="#7c3aed"/>
  <rect x="830" y="180" width="50" height="50" fill="#f3e8ff" rx="8"/>
  <text x="855" y="215" font-size="24" text-anchor="middle">⚡</text>
  <text x="895" y="195" font-size="16" font-weight="700" fill="#5b21b6">Antihipertensivos</text>
  <text x="895" y="215" font-size="14" font-weight="700" fill="#5b21b6">Resumo Flavonoid</text>
  <text x="830" y="260" font-size="13" fill="#64748b">Resumo rapido para revisao</text>
  <text x="830" y="278" font-size="13" fill="#64748b">de prova</text>
  <rect x="830" y="290" width="60" height="22" fill="#7c3aed" rx="4"/>
  <text x="860" y="305" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 15:30</text>

  <!-- Card 4 -->
  <rect x="40" y="345" width="365" height="160" fill="white" rx="12" stroke="#10b981" stroke-width="3"/>
  <rect x="40" y="345" width="6" height="160" fill="#10b981"/>
  <rect x="60" y="365" width="50" height="50" fill="#d1fae5" rx="8"/>
  <text x="85" y="400" font-size="24" text-anchor="middle">📚</text>
  <text x="125" y="380" font-size="16" font-weight="700" fill="#065f46">Resumao HAS -</text>
  <text x="125" y="400" font-size="14" font-weight="700" fill="#065f46">Farmacologia Facil</text>
  <text x="60" y="445" font-size="13" fill="#64748b">Todas as classes em</text>
  <text x="60" y="463" font-size="13" fill="#64748b">uma aula so</text>
  <rect x="60" y="475" width="60" height="22" fill="#10b981" rx="4"/>
  <text x="90" y="490" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 45:00</text>

  <!-- Card 5 -->
  <rect x="425" y="345" width="365" height="160" fill="white" rx="12" stroke="#0ea5e9" stroke-width="3"/>
  <rect x="425" y="345" width="6" height="160" fill="#0ea5e9"/>
  <rect x="445" y="365" width="50" height="50" fill="#dbeafe" rx="8"/>
  <text x="470" y="400" font-size="24" text-anchor="middle">🎓</text>
  <text x="510" y="380" font-size="16" font-weight="700" fill="#1e3a8a">Farmacologia</text>
  <text x="510" y="400" font-size="14" font-weight="700" fill="#1e3a8a">Clinica - USP</text>
  <text x="445" y="445" font-size="13" fill="#64748b">Aula USP completa -</text>
  <text x="445" y="463" font-size="13" fill="#64748b">algoritmo terapeutico</text>
  <rect x="445" y="475" width="60" height="22" fill="#0ea5e9" rx="4"/>
  <text x="475" y="490" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 60:00</text>

  <!-- Card 6 -->
  <rect x="810" y="345" width="365" height="160" fill="white" rx="12" stroke="#ec4899" stroke-width="3"/>
  <rect x="810" y="345" width="6" height="160" fill="#ec4899"/>
  <rect x="830" y="365" width="50" height="50" fill="#fce7f3" rx="8"/>
  <text x="855" y="400" font-size="24" text-anchor="middle">🏥</text>
  <text x="895" y="380" font-size="16" font-weight="700" fill="#831843">HAS - Reta Final</text>
  <text x="895" y="400" font-size="14" font-weight="700" fill="#831843">Revalida</text>
  <text x="830" y="445" font-size="13" fill="#64748b">Diagnostico e tratamento</text>
  <text x="830" y="463" font-size="13" fill="#64748b">para residencia</text>
  <rect x="830" y="475" width="60" height="22" fill="#ec4899" rx="4"/>
  <text x="860" y="490" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 60:00</text>

  <!-- Card 7 -->
  <rect x="40" y="530" width="365" height="160" fill="white" rx="12" stroke="#6366f1" stroke-width="3"/>
  <rect x="40" y="530" width="6" height="160" fill="#6366f1"/>
  <rect x="60" y="550" width="50" height="50" fill="#e0e7ff" rx="8"/>
  <text x="85" y="585" font-size="24" text-anchor="middle">⭐</text>
  <text x="125" y="565" font-size="16" font-weight="700" fill="#3730a3">HAS Sistematica -</text>
  <text x="125" y="585" font-size="14" font-weight="700" fill="#3730a3">Super Revisao</text>
  <text x="60" y="630" font-size="13" fill="#64748b">Revisao sistematica</text>
  <text x="60" y="648" font-size="13" fill="#64748b">para prova</text>
  <rect x="60" y="660" width="60" height="22" fill="#6366f1" rx="4"/>
  <text x="90" y="675" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 45:00</text>

  <!-- Card 8 -->
  <rect x="425" y="530" width="365" height="160" fill="white" rx="12" stroke="#f97316" stroke-width="3"/>
  <rect x="425" y="530" width="6" height="160" fill="#f97316"/>
  <rect x="445" y="550" width="50" height="50" fill="#fed7aa" rx="8"/>
  <text x="470" y="585" font-size="24" text-anchor="middle">👶</text>
  <text x="510" y="565" font-size="16" font-weight="700" fill="#7c2d12">HAS Pediatrica -</text>
  <text x="510" y="585" font-size="14" font-weight="700" fill="#7c2d12">CardioPedBrasil</text>
  <text x="445" y="630" font-size="13" fill="#64748b">Hipertensao em criancas</text>
  <text x="445" y="648" font-size="13" fill="#64748b">(curva P95)</text>
  <rect x="445" y="660" width="60" height="22" fill="#f97316" rx="4"/>
  <text x="475" y="675" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 30:45</text>

  <!-- Card 9 -->
  <rect x="810" y="530" width="365" height="160" fill="white" rx="12" stroke="#be185d" stroke-width="3"/>
  <rect x="810" y="530" width="6" height="160" fill="#be185d"/>
  <rect x="830" y="550" width="50" height="50" fill="#fce7f3" rx="8"/>
  <text x="855" y="585" font-size="24" text-anchor="middle">🔬</text>
  <text x="895" y="565" font-size="16" font-weight="700" fill="#831843">HAS Secundaria -</text>
  <text x="895" y="585" font-size="14" font-weight="700" fill="#831843">Episodio 77</text>
  <text x="830" y="630" font-size="13" fill="#64748b">Causas secundarias</text>
  <text x="830" y="648" font-size="13" fill="#64748b">de hipertensao</text>
  <rect x="830" y="660" width="60" height="22" fill="#be185d" rx="4"/>
  <text x="860" y="675" font-size="11" font-weight="700" fill="white" text-anchor="middle">⏱ 30:00</text>

  <!-- Player principal -->
  <text x="40" y="740" font-size="22" font-weight="700" fill="#0f766e">🎬 Player Principal do Curso</text>
  <text x="40" y="765" font-size="14" fill="#0d9488">Embed direto do YouTube com iframe</text>

  <rect x="40" y="785" width="1120" height="450" fill="#0f172a" rx="12"/>
  <text x="600" y="850" font-size="80" text-anchor="middle">▶</text>
  <text x="600" y="950" font-size="22" font-weight="700" fill="white" text-anchor="middle">YouTube Player (16:9)</text>
  <text x="600" y="985" font-size="14" fill="#cbd5e1" text-anchor="middle">Embed: https://www.youtube.com/embed/VIDEO_ID</text>
  <text x="600" y="1010" font-size="12" fill="#94a3b8" text-anchor="middle">Rotacao automatica entre 11 videos validados</text>

  <rect x="40" y="1235" width="1120" height="60" fill="#1e293b" rx="8"/>
  <rect x="60" y="1250" width="60" height="30" fill="#10b981" rx="6"/>
  <text x="90" y="1270" font-size="12" font-weight="700" fill="white" text-anchor="middle">✓ Marcar</text>
  <text x="60" y="1110" font-size="14" font-weight="600" fill="white" text-anchor="middle">📺 Aula atual: Tratamento Farmacologico</text>

  <!-- Dica -->
  <rect x="40" y="1300" width="1120" height="60" fill="white" rx="8" stroke="#14b8a6" stroke-width="2"/>
  <text x="600" y="1325" font-size="14" fill="#475569" text-anchor="middle">💡 <tspan font-weight="700">Dica:</tspan> Assista os videos para aprofundar o conteudo. <tspan font-weight="700">+20 XP</tspan> por video.</text>
  <text x="600" y="1345" font-size="12" fill="#64748b" text-anchor="middle">Use o botao "✓ Marcar como assistida" no player principal para ganhar XP.</text>

  <!-- Footer -->
  <text x="600" y="1390" font-size="11" fill="#94a3b8" text-anchor="middle">Player + Biblioteca de Videos | Auxilio Farmacia</text>
</svg>"""


def main():
    OUTPUT.mkdir(exist_ok=True, parents=True)

    svg = PREVIEW_SVG
    svg = svg.replace('Inter, sans-serif', 'DejaVu-Sans')
    svg = svg.replace("'Inter, sans-serif'", 'DejaVu-Sans')
    svg = svg.replace('Playfair Display, serif', 'DejaVu-Serif')

    svg_path = OUTPUT / "video_library.svg"
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg)

    png_path = OUTPUT / "video_library.png"
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                         output_width=1200, background_color='white')
        print(f"✅ video_library.png")
    except Exception as e:
        print(f"❌ {e}")


if __name__ == "__main__":
    main()