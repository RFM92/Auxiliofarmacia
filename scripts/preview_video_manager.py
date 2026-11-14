#!/usr/bin/env python3
"""Preview do Video Manager"""
from pathlib import Path
import cairosvg

OUTPUT = Path("/workspace/output/atualizacoes")

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <rect width="1200" height="1400" fill="#0f172a"/>
  <rect x="60" y="40" width="1080" height="1320" rx="20" fill="white"/>

  <!-- Header -->
  <text x="600" y="100" font-size="32" font-weight="700" fill="#0f766e" text-anchor="middle" font-family="DejaVu-Serif">🎬 Gerenciador de Vídeos</text>
  <text x="600" y="135" font-size="14" fill="#64748b" text-anchor="middle">Substitua os vídeos do YouTube pelos seus próprios</text>
  <circle cx="1080" cy="100" r="18" fill="#fee2e2"/>
  <text x="1080" y="107" font-size="20" font-weight="700" fill="#dc2626" text-anchor="middle">×</text>

  <!-- Fonte do video -->
  <rect x="100" y="170" width="1000" height="320" rx="12" fill="#f0fdfa"/>
  <text x="130" y="205" font-size="16" font-weight="700" fill="#0f766e">📹 Fonte do Vídeo</text>

  <!-- 3 opcoes -->
  <rect x="130" y="225" width="180" height="50" rx="8" fill="white" stroke="#14b8a6" stroke-width="3"/>
  <text x="220" y="255" font-size="13" font-weight="700" fill="#0f766e" text-anchor="middle">▶ YouTube (selecionado)</text>

  <rect x="330" y="225" width="160" height="50" rx="8" fill="white" stroke="#cbd5e1" stroke-width="2"/>
  <text x="410" y="255" font-size="13" fill="#475569" text-anchor="middle">▶ Vimeo</text>

  <rect x="510" y="225" width="240" height="50" rx="8" fill="white" stroke="#cbd5e1" stroke-width="2"/>
  <text x="630" y="255" font-size="13" fill="#475569" text-anchor="middle">▶ Meu Arquivo MP4</text>

  <!-- Input -->
  <text x="130" y="310" font-size="13" font-weight="600" fill="#475569">Cole a URL ou ID do YouTube:</text>
  <rect x="130" y="325" width="830" height="42" rx="8" fill="white" stroke="#cbd5e1"/>
  <text x="150" y="352" font-size="13" fill="#94a3b8">https://www.youtube.com/watch?v=SEU_VIDEO_AQUI</text>
  <rect x="970" y="325" width="110" height="42" rx="8" fill="#dc2626"/>
  <text x="1025" y="352" font-size="13" font-weight="700" fill="white" text-anchor="middle">▶ Preview</text>

  <text x="130" y="395" font-size="11" fill="#94a3b8">💡 Suporta URLs completas, encurtadas (youtu.be), ou apenas o ID de 11 caracteres</text>

  <!-- Preview do video -->
  <rect x="130" y="415" width="950" height="60" rx="8" fill="black"/>
  <text x="605" y="450" font-size="16" fill="white" text-anchor="middle">[Preview do vídeo YouTube aparece aqui]</text>

  <!-- Lista de modulos -->
  <text x="100" y="530" font-size="16" font-weight="700" fill="#0f766e">📚 Atribuir Vídeo a Cada Módulo</text>

  <!-- Curso Anti-hipertensivos -->
  <rect x="100" y="555" width="1000" height="380" rx="10" fill="#f8fafc"/>
  <rect x="100" y="555" width="6" height="380" fill="#14b8a6"/>
  <text x="130" y="585" font-size="14" font-weight="700" fill="#0f766e">📚 Anti-hipertensivos (7 módulos)</text>

  modulos = [
      ("Módulo 1", "YouTube", "_Ps_bAvH5PU", "#fef3c7"),
      ("Módulo 2", "YouTube", "eCS2tnZCbrs", "#fff7ed"),
      ("Módulo 3", "MP4 Próprio", "minha_aula_03.mp4", "#d1fae5"),
      ("Módulo 4", "YouTube", "hCqUHvif2qI", "#fef3c7"),
      ("Módulo 5", "Vimeo", "https://vimeo.com/...", "#dbeafe"),
      ("Módulo 6", "YouTube", "2iH2hL07a7A", "#fef3c7"),
      ("Módulo 7", "MP4 Próprio", "minha_aula_07.mp4", "#d1fae5"),
  ]

  y = 610
  for (mod, source, val, color) in modulos:
    rect_y = y
    rect_h = 40
    # Modulo
    text x="140" y="{y+25}" font-size="11" fill="#94a3b8">{mod}</text>
    # Select source
    rect x="220" y="{y+5}" width="120" height="30" rx="6" fill="white" stroke="#cbd5e1"/>
    text x="280" y="{y+25}" font-size="11" fill="#475569" text-anchor="middle">{source}</text>
    # Input
    rect x="350" y="{y+5}" width="730" height="30" rx="6" fill="white" stroke="#cbd5e1"/>
    text x="370" y="{y+25}" font-size="11" fill={('#dc2626' if 'minha' in val else '#475569')}>{val}</text>
    y += 45

  <!-- Botoes de acao -->
  rect x="100" y="970" width="1000" height="120" rx="0" fill="none"
  line x1="100" y1="970" x2="1100" y2="970" stroke="#e2e8f0" stroke-width="2"

  # Botao resetar
  rect x="120" y="1000" width="320" height="50" rx="8" fill="#fee2e2"
  text x="280" y="1031" font-size="13" font-weight="600" fill="#dc2626" text-anchor="middle">🔄 Resetar Tudo para YouTube</text>

  # Botoes direita
  rect x="700" y="1000" width="140" height="50" rx="8" fill="#cbd5e1"
  text x="770" y="1031" font-size="13" font-weight="600" fill="#1e293b" text-anchor="middle">Cancelar</text>

  rect x="850" y="1000" width="240" height="50" rx="8" fill="url(#btnGrad)"
  defs>
    linearGradient id="btnGrad" x1="0%" y1="0%" x2="100%" y2="0%"
      stop offset="0%" stop-color="#14b8a6"
      stop offset="100%" stop-color="#0d9488"
    /linearGradient
  /defs
  text x="970" y="1031" font-size="13" font-weight="700" fill="white" text-anchor="middle">💾 Salvar Alterações</text>

  <!-- Info box -->
  rect x="100" y="1120" width="1000" height="220" rx="12" fill="#fef3c7" stroke="#ca8a04" stroke-width="2"
  text x="130" y="1155" font-size="14" font-weight="700" fill="#713f12">💡 3 Formas de Usar Seus Próprios Vídeos</text>

  text x="130" y="1190" font-size="12" fill="#713f12"
    tspan font-weight="700"1. YouTube:/tspan Faça upload do seu vídeo para YouTube (pode ser não-listado)
    tspan x="130" dy="20" font-weight="700"2. Vimeo:/tspan Faça upload para Vimeo (plano grátis até 500MB)
    tspan x="130" dy="20" font-weight="700"3. MP4 Próprio:/tspan Upload direto (até 50MB, fica salvo no navegador)
  /text

  text x="130" y="1305" font-size="11" font-style="italic" fill="#92400e"
    Após salvar, recarregue a página. O player principal usará seus vídeos automaticamente.

  <!-- Botao flutuante -->
  circle cx="1100" cy="1340" r="35" fill="url(#floatingBtn)"
  defs>
    linearGradient id="floatingBtn" x1="0%" y1="0%" x2="100%" y2="100%"
      stop offset="0%" stop-color="#dc2626"
      stop offset="100%" stop-color="#b91c1c"
    /linearGradient
  /defs
  text x="1100" y="1347" font-size="13" font-weight="700" fill="white" text-anchor="middle">🎬 Vídeos</text>

  text x="600" y="1380" font-size="11" fill="#94a3b8" text-anchor="middle"Video Manager | Auxílio Farmácia (acesso apenas admin)</text>
</svg>"""

# Substitui caracteres que devem ser <
svg = svg.replace("text x=", "TEXT_PLACEHOLDER")  # workaround
svg = SVG.replace("text x=", "<text x=")
svg = svg.replace("/text", "</text>")
svg = svg.replace("rect x=", "<rect x=")
svg = svg.replace("/rect", "</rect>")
svg = svg.replace("circle cx=", "<circle cx=")
svg = svg.replace("/circle", "</circle>")
svg = svg.replace("line x1=", "<line x1=")
svg = svg.replace("/line", "</line>")
svg = svg.replace("defs>", "<defs>")
svg = svg.replace("/defs", "</defs>")
svg = svg.replace("linearGradient id=", "<linearGradient id=")
svg = svg.replace("/linearGradient", "</linearGradient>")
svg = svg.replace("stop offset=", "<stop offset=")
svg = svg.replace("/stop", "</stop>")
svg = svg.replace("tspan ", "<tspan ")
svg = svg.replace("/tspan", "</tspan>")
svg = svg.replace("tspan x=", "<tspan x=")

# Remove caracteres especiais problematicos
import re
svg = re.sub(r'(?<!<)/tspan>', '</tspan>', svg)

svg_path = OUTPUT / "video_manager.svg"
svg_path.write_text(svg, encoding='utf-8')

png_path = OUTPUT / "video_manager.png"
cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                 output_width=1200, background_color='white')
print(f"✅ video_manager.png")