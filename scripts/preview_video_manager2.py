#!/usr/bin/env python3
"""Preview simplificado do Video Manager"""
from pathlib import Path
import cairosvg

OUTPUT = Path("/workspace/output/atualizacoes")

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
<defs>
<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0f172a"/><stop offset="100%" stop-color="#1e293b"/></linearGradient>
<linearGradient id="gradBtn" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#14b8a6"/><stop offset="100%" stop-color="#0d9488"/></linearGradient>
<linearGradient id="gradSave" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#dc2626"/><stop offset="100%" stop-color="#b91c1c"/></linearGradient>
</defs>
<rect width="1200" height="1400" fill="url(#bg)"/>

<!-- Modal -->
<rect x="60" y="40" width="1080" height="1320" rx="20" fill="white"/>

<!-- Header -->
<text x="600" y="100" font-size="32" font-weight="700" fill="#0f766e" text-anchor="middle" font-family="DejaVu-Serif">🎬 Gerenciador de Vídeos</text>
<text x="600" y="130" font-size="14" fill="#64748b" text-anchor="middle">Substitua os vídeos do YouTube pelos seus próprios</text>
<circle cx="1090" cy="100" r="20" fill="#fee2e2"/>
<text x="1090" y="107" font-size="22" font-weight="700" fill="#dc2626" text-anchor="middle">×</text>

<!-- Fonte -->
<rect x="100" y="170" width="1000" height="280" rx="12" fill="#f0fdfa"/>
<text x="130" y="205" font-size="16" font-weight="700" fill="#0f766e">📹 Fonte do Vídeo</text>

<!-- Botoes de fonte -->
<rect x="130" y="225" width="200" height="50" rx="8" fill="white" stroke="#14b8a6" stroke-width="3"/>
<text x="230" y="256" font-size="13" font-weight="700" fill="#0f766e" text-anchor="middle">▶ YouTube</text>

<rect x="350" y="225" width="160" height="50" rx="8" fill="white" stroke="#cbd5e1" stroke-width="2"/>
<text x="430" y="256" font-size="13" fill="#475569" text-anchor="middle">▶ Vimeo</text>

<rect x="530" y="225" width="260" height="50" rx="8" fill="white" stroke="#cbd5e1" stroke-width="2"/>
<text x="660" y="256" font-size="13" fill="#475569" text-anchor="middle">📤 Meu Arquivo MP4</text>

<!-- Input -->
<text x="130" y="310" font-size="13" font-weight="600" fill="#475569">Cole a URL ou ID do YouTube:</text>
<rect x="130" y="325" width="830" height="42" rx="8" fill="white" stroke="#cbd5e1"/>
<text x="150" y="352" font-size="13" fill="#94a3b8">https://www.youtube.com/watch?v=SEU_VIDEO_AQUI</text>
<rect x="970" y="325" width="110" height="42" rx="8" fill="#dc2626"/>
<text x="1025" y="352" font-size="13" font-weight="700" fill="white" text-anchor="middle">▶ Preview</text>

<text x="130" y="395" font-size="11" fill="#94a3b8">💡 Suporta URLs completas, encurtadas (youtu.be), ou apenas o ID de 11 caracteres</text>

<rect x="130" y="415" width="950" height="30" rx="8" fill="black"/>
<text x="605" y="435" font-size="14" fill="white" text-anchor="middle">[Preview do vídeo aqui]</text>

<!-- Lista modulos -->
<text x="100" y="490" font-size="16" font-weight="700" fill="#0f766e">📚 Atribuir Vídeo a Cada Módulo</text>

<!-- Curso 1 -->
<rect x="100" y="510" width="1000" height="320" rx="10" fill="#f8fafc"/>
<rect x="100" y="510" width="6" height="320" fill="#14b8a6"/>
<text x="130" y="540" font-size="14" font-weight="700" fill="#0f766e">📚 Anti-hipertensivos (7 módulos)</text>

<!-- 7 modulos com exemplos diferentes -->
<g transform="translate(0,560)">
<text x="140" y="20" font-size="11" fill="#94a3b8">Módulo 1</text>
<rect x="220" y="0" width="120" height="30" rx="6" fill="#fef3c7" stroke="#ca8a04"/>
<text x="280" y="20" font-size="11" font-weight="600" fill="#713f12" text-anchor="middle">▶ YouTube</text>
<rect x="350" y="0" width="730" height="30" rx="6" fill="white" stroke="#cbd5e1"/>
<text x="365" y="20" font-size="11" fill="#475569">_Ps_bAvH5PU</text>
</g>

<g transform="translate(0,600)">
<text x="140" y="20" font-size="11" fill="#94a3b8">Módulo 2</text>
<rect x="220" y="0" width="120" height="30" rx="6" fill="#fef3c7" stroke="#ca8a04"/>
<text x="280" y="20" font-size="11" font-weight="600" fill="#713f12" text-anchor="middle">▶ YouTube</text>
<rect x="350" y="0" width="730" height="30" rx="6" fill="white" stroke="#cbd5e1"/>
<text x="365" y="20" font-size="11" fill="#475569">eCS2tnZCbrs</text>
</g>

<g transform="translate(0,640)">
<text x="140" y="20" font-size="11" fill="#94a3b8">Módulo 3</text>
<rect x="220" y="0" width="120" height="30" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
<text x="280" y="20" font-size="11" font-weight="600" fill="#065f46" text-anchor="middle">📤 MP4 Próprio</text>
<rect x="350" y="0" width="730" height="30" rx="6" fill="white" stroke="#10b981" stroke-width="2"/>
<text x="365" y="20" font-size="11" font-weight="600" fill="#10b981">✓ minha_aula_bcc.mp4 (upload local)</text>
</g>

<g transform="translate(0,680)">
<text x="140" y="20" font-size="11" fill="#94a3b8">Módulo 4</text>
<rect x="220" y="0" width="120" height="30" rx="6" fill="#fef3c7" stroke="#ca8a04"/>
<text x="280" y="20" font-size="11" font-weight="600" fill="#713f12" text-anchor="middle">▶ YouTube</text>
<rect x="350" y="0" width="730" height="30" rx="6" fill="white" stroke="#cbd5e1"/>
<text x="365" y="20" font-size="11" fill="#475569">hCqUHvif2qI</text>
</g>

<g transform="translate(0,720)">
<text x="140" y="20" font-size="11" fill="#94a3b8">Módulo 5</text>
<rect x="220" y="0" width="120" height="30" rx="6" fill="#dbeafe" stroke="#2563eb"/>
<text x="280" y="20" font-size="11" font-weight="600" fill="#1e3a8a" text-anchor="middle">▶ Vimeo</text>
<rect x="350" y="0" width="730" height="30" rx="6" fill="white" stroke="#cbd5e1"/>
<text x="365" y="20" font-size="11" fill="#475569">https://vimeo.com/123456789</text>
</g>

<g transform="translate(0,760)">
<text x="140" y="20" font-size="11" fill="#94a3b8">Módulo 6</text>
<rect x="220" y="0" width="120" height="30" rx="6" fill="#fef3c7" stroke="#ca8a04"/>
<text x="280" y="20" font-size="11" font-weight="600" fill="#713f12" text-anchor="middle">▶ YouTube</text>
<rect x="350" y="0" width="730" height="30" rx="6" fill="white" stroke="#cbd5e1"/>
<text x="365" y="20" font-size="11" fill="#475569">2iH2hL07a7A</text>
</g>

<g transform="translate(0,800)">
<text x="140" y="20" font-size="11" fill="#94a3b8">Módulo 7</text>
<rect x="220" y="0" width="120" height="30" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
<text x="280" y="20" font-size="11" font-weight="600" fill="#065f46" text-anchor="middle">📤 MP4 Próprio</text>
<rect x="350" y="0" width="730" height="30" rx="6" fill="white" stroke="#10b981" stroke-width="2"/>
<text x="365" y="20" font-size="11" font-weight="600" fill="#10b981">✓ anticoagulantes_aula07.mp4 (upload local)</text>
</g>

<!-- Linha divisoria -->
<line x1="100" y1="870" x2="1100" y2="870" stroke="#e2e8f0" stroke-width="2"/>

<!-- Botoes -->
<rect x="120" y="900" width="340" height="50" rx="8" fill="#fee2e2"/>
<text x="290" y="931" font-size="13" font-weight="600" fill="#dc2626" text-anchor="middle">🔄 Resetar Tudo para YouTube</text>

<rect x="700" y="900" width="140" height="50" rx="8" fill="#cbd5e1"/>
<text x="770" y="931" font-size="13" font-weight="600" fill="#1e293b" text-anchor="middle">Cancelar</text>

<rect x="850" y="900" width="240" height="50" rx="8" fill="url(#gradSave)"/>
<text x="970" y="931" font-size="14" font-weight="700" fill="white" text-anchor="middle">💾 Salvar Alterações</text>

<!-- Info box -->
<rect x="100" y="1000" width="1000" height="320" rx="12" fill="#fef3c7" stroke="#ca8a04" stroke-width="2"/>
<text x="600" y="1040" font-size="18" font-weight="700" fill="#713f12" text-anchor="middle">💡 3 Formas de Usar Seus Próprios Vídeos</text>

<g transform="translate(150,1080)">
<rect x="0" y="0" width="280" height="180" rx="10" fill="white" stroke="#dc2626" stroke-width="2"/>
<text x="140" y="30" font-size="32" text-anchor="middle">▶</text>
<text x="140" y="65" font-size="15" font-weight="700" fill="#dc2626" text-anchor="middle">YOUTUBE</text>
<text x="20" y="95" font-size="11" fill="#475569">Faça upload do seu vídeo</text>
<text x="20" y="113" font-size="11" fill="#475569">para YouTube (pode ser</text>
<text x="20" y="131" font-size="11" fill="#475569">não-listado/privado).</text>
<text x="20" y="158" font-size="10" font-weight="600" fill="#10b981">✓ Grátis</text>
<text x="80" y="158" font-size="10" font-weight="600" fill="#10b981">✓ Sem limite de tamanho</text>
</g>

<g transform="translate(460,1080)">
<rect x="0" y="0" width="280" height="180" rx="10" fill="white" stroke="#2563eb" stroke-width="2"/>
<text x="140" y="30" font-size="32" text-anchor="middle">▶</text>
<text x="140" y="65" font-size="15" font-weight="700" fill="#2563eb" text-anchor="middle">VIMEO</text>
<text x="20" y="95" font-size="11" fill="#475569">Plano grátis até 500MB</text>
<text x="20" y="113" font-size="11" fill="#475569">por semana. Privacidade</text>
<text x="20" y="131" font-size="11" fill="#475569">total garantida.</text>
<text x="20" y="158" font-size="10" font-weight="600" fill="#10b981">✓ Profissional</text>
<text x="120" y="158" font-size="10" font-weight="600" fill="#10b981">✓ Sem ads</text>
</g>

<g transform="translate(770,1080)">
<rect x="0" y="0" width="280" height="180" rx="10" fill="white" stroke="#10b981" stroke-width="2"/>
<text x="140" y="30" font-size="32" text-anchor="middle">📤</text>
<text x="140" y="65" font-size="15" font-weight="700" fill="#10b981" text-anchor="middle">MEU MP4</text>
<text x="20" y="95" font-size="11" fill="#475569">Upload direto do arquivo.</text>
<text x="20" y="113" font-size="11" fill="#475569">Fica salvo no navegador</text>
<text x="20" y="131" font-size="11" fill="#475569">(localStorage Base64).</text>
<text x="20" y="158" font-size="10" font-weight="600" fill="#ca8a04">⚠ Limite 50MB</text>
</g>

<text x="600" y="1300" font-size="12" font-style="italic" fill="#92400e" text-anchor="middle">Após salvar, recarregue a página. O player principal usará seus vídeos automaticamente.</text>

<!-- Botao flutuante -->
<rect x="1050" y="1300" width="120" height="50" rx="25" fill="url(#gradSave)"/>
<text x="1110" y="1330" font-size="13" font-weight="700" fill="white" text-anchor="middle">🎬 Vídeos</text>

</svg>"""

svg_path = OUTPUT / "video_manager.svg"
svg_path.write_text(SVG, encoding='utf-8')

png_path = OUTPUT / "video_manager.png"
try:
    cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                     output_width=1200, background_color='white')
    print(f"✅ video_manager.png")
except Exception as e:
    print(f"❌ {e}")