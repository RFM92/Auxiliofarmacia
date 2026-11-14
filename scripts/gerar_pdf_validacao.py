#!/usr/bin/env python3
"""
Gera PDF formatado com todos os textos dos modulos dos cursos
para o usuario validar o conteudo.
"""
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

# Cores
COR_PRIMARIA = HexColor('#0f766e')
COR_SECUNDARIA = HexColor('#14b8a6')
COR_DESTAQUE = HexColor('#dc2626')
COR_TEXTO = HexColor('#1e293b')

# Estilos
styles = getSampleStyleSheet()

titulo_principal = ParagraphStyle(
    'TituloPrincipal', parent=styles['Title'],
    fontSize=28, textColor=COR_PRIMARIA, alignment=TA_CENTER,
    spaceAfter=20, fontName='Helvetica-Bold'
)

titulo_modulo = ParagraphStyle(
    'TituloModulo', parent=styles['Heading1'],
    fontSize=22, textColor=COR_PRIMARIA, spaceBefore=30, spaceAfter=15,
    fontName='Helvetica-Bold', borderWidth=2, borderColor=COR_PRIMARIA,
    borderPadding=10
)

subtitulo = ParagraphStyle(
    'Subtitulo', parent=styles['Heading2'],
    fontSize=16, textColor=COR_SECUNDARIA, spaceBefore=15, spaceAfter=10,
    fontName='Helvetica-Bold'
)

subtitulo_h3 = ParagraphStyle(
    'SubtituloH3', parent=styles['Heading3'],
    fontSize=13, textColor=COR_TEXTO, spaceBefore=10, spaceAfter=5,
    fontName='Helvetica-Bold'
)

texto_normal = ParagraphStyle(
    'TextoNormal', parent=styles['Normal'],
    fontSize=10, textColor=COR_TEXTO, alignment=TA_JUSTIFY,
    spaceAfter=8, leading=14, fontName='Helvetica'
)

texto_destaque = ParagraphStyle(
    'TextoDestaque', parent=styles['Normal'],
    fontSize=10, textColor=COR_DESTAQUE, alignment=TA_JUSTIFY,
    spaceAfter=8, leading=14, fontName='Helvetica-Bold'
)

rodape = ParagraphStyle(
    'Rodape', parent=styles['Normal'],
    fontSize=8, textColor=HexColor('#94a3b8'), alignment=TA_CENTER,
    spaceAfter=4
)


def extrair_modulo(html, pattern):
    """Extrai e limpa texto de um modulo"""
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return None

    content = match.group(0)

    # Limpa mas mantem alguma estrutura
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<svg[^>]*>.*?</svg>', '[DIAGRAMA/SVG]', content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)

    return content


def html_to_parags(content):
    """Converte HTML em paragrafos formatados para o PDF"""
    parags = []

    # Extrai titulo do modulo
    title_match = re.search(r'<h3 class="bcc-title"[^>]*>(.*?)</h3>', content, re.DOTALL)
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        parags.append(Paragraph(title, subtitulo_h3))

    # Extrai subtitulo
    subtitle_match = re.search(r'<p class="bcc-subtitle"[^>]*>(.*?)</p>', content, re.DOTALL)
    if subtitle_match:
        subtitle = re.sub(r'<[^>]+>', '', subtitle_match.group(1)).strip()
        parags.append(Paragraph(f"<i>{subtitle}</i>", texto_normal))

    # Extrai intro
    intro_match = re.search(r'<div class="bcc-intro"[^>]*>(.*?)</div>\s*<', content, re.DOTALL)
    if intro_match:
        intro = re.sub(r'<[^>]+>', '', intro_match.group(1)).strip()
        intro = re.sub(r'\s+', ' ', intro)
        parags.append(Paragraph(intro, texto_normal))

    # Extrai tabelas
    tables = re.findall(r'<table[^>]*>(.*?)</table>', content, re.DOTALL)
    for table_html in tables:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        if not rows:
            continue

        data = []
        for row in rows[:30]:  # Limita para PDF
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            cells_clean = []
            for c in cells:
                c = re.sub(r'<[^>]+>', ' ', c)
                c = re.sub(r'\s+', ' ', c).strip()
                cells_clean.append(c[:100])
            if cells_clean:
                data.append(cells_clean)

        if len(data) > 1:
            try:
                t = Table(data, colWidths=[5*cm, 4*cm, 4*cm, 3*cm])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA),
                    ('TEXTCOLOR', (0,0), (-1,0), HexColor('#ffffff')),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 7),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, HexColor('#cbd5e1')),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#f8fafc'), HexColor('#ffffff')]),
                    ('LEFTPADDING', (0,0), (-1,-1), 4),
                    ('RIGHTPADDING', (0,0), (-1,-1), 4),
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ]))
                parags.append(t)
                parags.append(Spacer(1, 6))
            except:
                pass

    # Mnemonicos
    mnemonics = re.findall(r'<div class="mnemonic-card"[^>]*>(.*?)</div>\s*</div>', content, re.DOTALL)
    for m in mnemonics:
        m_text = re.sub(r'<[^>]+>', ' ', m)
        m_text = re.sub(r'\s+', ' ', m_text).strip()
        if len(m_text) > 20:
            parags.append(Paragraph(f"<b>🧠 {m_text[:400]}</b>", texto_destaque))

    # Resumo
    summary = re.findall(r'<div class="bcc-summary-item"[^>]*>(.*?)</div>\s*</div>', content, re.DOTALL)
    for s in summary[:6]:
        s_text = re.sub(r'<[^>]+>', ' ', s)
        s_text = re.sub(r'\s+', ' ', s_text).strip()
        if s_text:
            parags.append(Paragraph(f"✅ {s_text[:300]}", texto_normal))

    return parags


def main():
    with open("output/dashboard-auxfarmacia-FREE.html", "r", encoding="utf-8") as f:
        html = f.read()

    output_pdf = Path("output/atualizacoes/TEXTOS_CURSOS_VALIDACAO.pdf")
    doc = SimpleDocTemplate(
        str(output_pdf), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    story = []

    # Capa
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("AUXÍLIO FARMÁCIA", titulo_principal))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>TEXTOS DOS MÓDULOS DOS CURSOS</b>", titulo_modulo))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Documento de validação de conteúdo",
        ParagraphStyle('sub', parent=texto_normal, fontSize=14, alignment=TA_CENTER, textColor=COR_SECUNDARIA)
    ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "<b>Curso:</b> Anti-hipertensivos<br/>"
        "<b>Curso:</b> Antidiabéticos<br/>"
        "<b>Total de módulos:</b> 7<br/>"
        "<b>Idioma:</b> Português (PT-BR)<br/>"
        "<b>Público-alvo:</b> Profissionais de saúde",
        ParagraphStyle('capa_info', parent=texto_normal, fontSize=11, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "<b>Índice:</b><br/>"
        "1. BCCs - Comparativo Completo<br/>"
        "2. IECA vs BRA<br/>"
        "3. Diuréticos<br/>"
        "4. ARA II - Alisquireno<br/>"
        "5. Betabloqueadores<br/>"
        "6. Antiarritmicos<br/>"
        "7. Anticoagulantes",
        ParagraphStyle('idx', parent=texto_normal, fontSize=10, alignment=TA_CENTER, leftIndent=0)
    ))
    story.append(PageBreak())

    # Modulos
    modulos = [
        ("MÓDULO 1: BCCs - BLOQUEADORES DOS CANAIS DE CÁLCIO",
         r'<div class="bcc-module"[^>]*>[^<]*<div class="bcc-header">.*?BCCs.*?(?=<div class="bcc-module"|</body>)'),
        ("MÓDULO 2: IECA vs BRA",
         r'id="iecaBraModule".*?(?=<div class="bcc-module"|</body>)'),
        ("MÓDULO 3: DIURÉTICOS",
         r'id="diureticosModule".*?(?=<div class="bcc-module"|</body>)'),
        ("MÓDULO 4: ARA II - ALISQUIRENO",
         r'id="araIIModule".*?(?=<div class="bcc-module"|</body>)'),
        ("MÓDULO 5: BETABLOQUEADORES",
         r'id="betaBloqModule".*?(?=<div class="bcc-module"|</body>)'),
        ("MÓDULO 6: ANTIARRÍTMICOS",
         r'id="antiarrModule".*?(?=<div class="bcc-module"|</body>)'),
        ("MÓDULO 7: ANTICOAGULANTES",
         r'id="anticoagModule".*?(?=<div class="bcc-module"|</body>)'),
    ]

    for titulo, pattern in modulos:
        content = extrair_modulo(html, pattern)
        if content:
            story.append(Paragraph(titulo, titulo_modulo))
            story.append(Spacer(1, 0.3*cm))
            parags = html_to_parags(content)
            story.extend(parags)
            story.append(PageBreak())

    # Rodape final
    story.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", rodape))
    story.append(Paragraph("Auxílio Farmácia © 2026 - Documento para validação", rodape))
    story.append(Paragraph("Conteúdo educativo - NÃO substitui consulta médica", rodape))

    doc.build(story)
    print(f"✅ PDF gerado: {output_pdf}")
    print(f"📊 Tamanho: {output_pdf.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()