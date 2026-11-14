#!/usr/bin/env python3
"""
Atualiza TUDO apos remocao dos medicamentos hospitalares:
1. Regenera ZIPs com dashboards novos
2. Regenera PDFs institucionais (atualizando texto)
3. Atualiza landing page (se menciona medicamentos)
4. Atualiza admin.html
5. Cria changelog
"""
import re
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

OUTPUT = Path("/workspace/output")

HOSPITAL_ONLY = {
    'meropenem', 'vancomicina', 'adrenalina', 'ceftriaxona'
}

# ========== 1. ATUALIZAR ADMIN.HTML ==========
def update_admin():
    admin = OUTPUT / "admin.html"
    if not admin.exists():
        return False

    with open(admin, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove referencias aos medicamentos hospitalares
    for med in HOSPITAL_ONLY:
        # Remove de qualquer lista/tabela
        content = re.sub(rf'<[^>]*{med}[^>]*>(?:[^<]|<(?!/tr))*</[^>]*>', '', content)
        # Remove mencoes em texto
        content = re.sub(rf'\b{med}\b[,\s]*', '', content)

    with open(admin, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ========== 2. ATUALIZAR LANDING.HTML ==========
def update_landing():
    landing = OUTPUT / "landing.html"
    if not landing.exists():
        return False

    with open(landing, "r", encoding="utf-8") as f:
        content = f.read()

    # Atualiza contadores de medicamentos (se houver)
    # Procura "122 medicamentos" ou similar e atualiza
    content = re.sub(r'(\d+)\s*medicamentos', '58 medicamentos', content, flags=re.IGNORECASE)

    with open(landing, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ========== 3. REGENERAR ZIPs ==========
def regenerate_zips():
    print("\n📦 Regenerando ZIPs...")

    # Arquivos para o ZIP completo (com Manual)
    complete_files = [
        "dashboard-auxfarmacia.html",
        "dashboard-auxfarmacia-FREE.html",
        "dashboard-auxfarmacia-PRO.html",
        "dashboard-auxfarmacia-PREMIUM.html",
        "dashboard-auxfarmacia-ENTERPRISE.html",
        "dashboard-auxfarmacia-educativo.html",
        "admin.html",
        "landing.html",
        "checkout.html",
        "api-client.js",
        "Auxilio_Farmacia-Manual_do_Administrador.pdf",
        "Auxilio_Farmacia-Apresentacao_Comercial.pdf",
        "atualizacoes/MEDICAMENTOS_HOSPITALARES_REMOVIDOS.md",
    ]

    # ZIP apenas do site (sem Manual - restrito)
    site_files = [
        "dashboard-auxfarmacia.html",
        "dashboard-auxfarmacia-FREE.html",
        "dashboard-auxfarmacia-PRO.html",
        "dashboard-auxfarmacia-PREMIUM.html",
        "dashboard-auxfarmacia-ENTERPRISE.html",
        "dashboard-auxfarmacia-educativo.html",
        "landing.html",
        "checkout.html",
        "api-client.js",
    ]

    # ZIP completo
    complete_zip = OUTPUT / "auxfarmacia_completo.zip"
    with zipfile.ZipFile(complete_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in complete_files:
            fpath = OUTPUT / fname
            if fpath.exists():
                zf.write(fpath, fname)

    # ZIP site
    site_zip = OUTPUT / "auxfarmacia_site.zip"
    with zipfile.ZipFile(site_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in site_files:
            fpath = OUTPUT / fname
            if fpath.exists():
                zf.write(fpath, fname)

    print(f"  ✅ {complete_zip.name}: {complete_zip.stat().st_size:,} bytes")
    print(f"  ✅ {site_zip.name}: {site_zip.stat().st_size:,} bytes")


# ========== 4. REGENERAR PDFs INSTITUCIONAIS ==========
def regenerate_pdfs():
    print("\n📄 Regenerando PDFs institucionais...")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

        COR_PRIMARIA = HexColor('#0f766e')
        COR_DESTAQUE = HexColor('#dc2626')
        COR_TEXTO = HexColor('#1e293b')

        styles = getSampleStyleSheet()
        titulo = ParagraphStyle('T', parent=styles['Title'], fontSize=24, textColor=COR_PRIMARIA, alignment=TA_CENTER, spaceAfter=20)
        subtitulo = ParagraphStyle('S', parent=styles['Heading2'], fontSize=14, textColor=COR_PRIMARIA, spaceAfter=10)
        corpo = ParagraphStyle('C', parent=styles['Normal'], fontSize=10, textColor=COR_TEXTO, alignment=TA_JUSTIFY, spaceAfter=8, leading=13)
        obs = ParagraphStyle('O', parent=corpo, fontSize=9, textColor=HexColor('#64748b'))

        # ========== PDF 1: MANUAL DO ADMINISTRADOR ==========
        manual_path = OUTPUT / "Auxilio_Farmacia-Manual_do_Administrador.pdf"
        doc = SimpleDocTemplate(str(manual_path), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

        story = []
        story.append(Spacer(1, 3*cm))
        story.append(Paragraph("AUXÍLIO FARMÁCIA", titulo))
        story.append(Paragraph("Manual do Administrador", subtitulo))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            "<b>Versão:</b> 2026.07<br/>"
            "<b>Última atualização:</b> 08/07/2026<br/>"
            "<b>Changelog:</b> Remoção de 4 medicamentos hospitalares<br/>"
            "  • Meropenem, Vancomicina IV, Adrenalina, Ceftriaxona<br/>"
            "<b>Total de medicamentos:</b> 58 (de 62 anteriormente)",
            ParagraphStyle('info', parent=corpo, fontSize=11, alignment=TA_CENTER)
        ))
        story.append(PageBreak())

        # Conteúdo do manual
        story.append(Paragraph("1. VISÃO GERAL DA PLATAFORMA", subtitulo))
        story.append(Paragraph(
            "O <b>Auxílio Farmácia</b> é uma plataforma educacional para profissionais de farmácia "
            "e drogaria, com foco em <b>uso ambulatorial</b> e <b>atenção primária à saúde</b>.",
            corpo
        ))
        story.append(Paragraph(
            "<b>Público-alvo:</b> Farmacêuticos, balconistas, técnicos em farmácia, estudantes.<br/>"
            "<b>Idioma:</b> Português (PT-BR)<br/>"
            "<b>Cobertura:</b> 58 medicamentos + 22 classes terapêuticas<br/>"
            "<b>Calculadoras:</b> 9 (pediátricas, clínicas, avançadas)<br/>"
            "<b>Cursos:</b> 2 trilhas completas (Anti-hipertensivos + Antidiabéticos)",
            corpo
        ))

        story.append(Paragraph("2. MEDICAMENTOS INCLUSOS", subtitulo))
        story.append(Paragraph(
            "A plataforma contém <b>58 medicamentos</b> organizados em 4 bases de dados:",
            corpo
        ))
        story.append(Paragraph(
            "• <b>MEDS_DROGARIA (33):</b> Estatinas, AINEs, IBPs, anti-hipertensivos, antidiabéticos orais, "
            "psiquiátricos, dermatológicos, anticoagulantes orais.<br/>"
            "• <b>MEDS_EXTRAS (22):</b> Antibióticos orais, antiparasitários, antivirais orais, "
            "anticonvulsivantes orais, antieméticos orais.<br/>"
            "• <b>MEDS_TOPICOS (2):</b> Colírios, anti-histamínicos.<br/>"
            "• <b>MEDS_DERMICOS (1):</b> Hidrocortisona creme.",
            corpo
        ))

        story.append(Paragraph("3. MEDICAMENTOS HOSPITALARES REMOVIDOS", subtitulo))
        story.append(Paragraph(
            "<b>Em 08/07/2026</b>, foram removidos 4 medicamentos de uso exclusivamente hospitalar:",
            corpo
        ))
        story.append(Paragraph(
            "❌ <b>Meropenem</b> — Antibiótico carbapenêmico (uso IV hospitalar)<br/>"
            "❌ <b>Vancomicina</b> — Glicopeptídeo (uso IV hospitalar)<br/>"
            "❌ <b>Adrenalina</b> — Vasopressor (uso IV/IM em emergência)<br/>"
            "❌ <b>Ceftriaxona</b> — Cefalosporina 3ª geração (uso IM/IV hospitalar)",
            ParagraphStyle('lista', parent=corpo, fontSize=10, textColor=COR_DESTAQUE)
        ))
        story.append(Paragraph(
            "<b>Razão:</b> Esses medicamentos não têm apresentação oral ou ambulatorial. "
            "São manipulados exclusivamente em ambiente hospitalar e <b>não fazem parte do escopo "
            "de drogarias</b>.",
            corpo
        ))

        story.append(Paragraph("4. SUBSTITUTOS AMBULATORIAIS", subtitulo))
        story.append(Paragraph(
            "Para os medicamentos removidos, quando relevante ambulatorial:",
            corpo
        ))
        story.append(Paragraph(
            "• <b>Vancomicina IV (MRSA):</b> → Linezolida oral ou sulfametoxazol-trimetoprim<br/>"
            "• <b>Ceftriaxona (gonorreia):</b> → Cefalexina oral + Azitromicina<br/>"
            "• <b>Ceftriaxona (pneumonia):</b> → Amoxicilina-clavulanato oral<br/>"
            "• <b>Meropenem:</b> → Encaminhar para internação (sem substituto oral)<br/>"
            "• <b>Adrenalina:</b> → SAMU 192 / emergência hospitalar",
            corpo
        ))

        story.append(Paragraph("5. PLANOS DE LICENCIAMENTO", subtitulo))
        story.append(Paragraph(
            "• <b>FREE:</b> Acesso a 30% dos medicamentos + calculadoras básicas<br/>"
            "• <b>PRO (R$ 29,90/mês):</b> Todos os 58 medicamentos + 70% das funcionalidades<br/>"
            "• <b>PREMIUM (R$ 79,90/mês):</b> Tudo do PRO + cursos + vídeos + downloads<br/>"
            "• <b>ENTERPRISE (R$ 297/mês):</b> Para instituições (múltiplos usuários)",
            corpo
        ))

        story.append(Paragraph("6. SEGURANÇA E ANTIPIRATARIA", subtitulo))
        story.append(Paragraph(
            "• Device fingerprint (SHA-256 do UA + screen + canvas)<br/>"
            "• Limite de devices: Pro=2, Premium=3, Enterprise=50<br/>"
            "• JWT tokens com auto-refresh<br/>"
            "• Logs de auditoria de todos os downloads<br/>"
            "• Manual do Admin restrito a admin logado (3 camadas de proteção)",
            corpo
        ))

        story.append(Spacer(1, 2*cm))
        story.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", obs))
        story.append(Paragraph("Auxílio Farmácia © 2026 - Versão 2026.07 - Manual atualizado em 08/07/2026", obs))
        story.append(Paragraph("Conteúdo educativo - NÃO substitui consulta médica", obs))

        doc.build(story)
        print(f"  ✅ Manual do Administrador: {manual_path.stat().st_size:,} bytes")

        # ========== PDF 2: APRESENTAÇÃO COMERCIAL ==========
        apresentacao_path = OUTPUT / "Auxilio_Farmacia-Apresentacao_Comercial.pdf"
        doc2 = SimpleDocTemplate(str(apresentacao_path), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

        story2 = []
        story2.append(Spacer(1, 3*cm))
        story2.append(Paragraph("AUXÍLIO FARMÁCIA", titulo))
        story2.append(Paragraph("Apresentação Comercial", subtitulo))
        story2.append(Spacer(1, 1*cm))
        story2.append(Paragraph(
            "<b>Versão 2026.07</b><br/>"
            "Plataforma educacional para farmácias e drogarias<br/>"
            "Foco em uso ambulatorial e atenção primária",
            ParagraphStyle('sub', parent=corpo, fontSize=11, alignment=TA_CENTER, textColor=COR_PRIMARIA)
        ))
        story2.append(PageBreak())

        # Capa de Vendas
        story2.append(Paragraph("PROPOSTA DE VALOR", subtitulo))
        story2.append(Paragraph(
            "O <b>Auxílio Farmácia</b> é uma plataforma que reúne em um só lugar:",
            corpo
        ))
        story2.append(Paragraph(
            "✅ <b>58 medicamentos</b> com bulas completas (Anvisa)<br/>"
            "✅ <b>22 classes terapêuticas</b> comparadas<br/>"
            "✅ <b>9 calculadoras</b> (pediátricas, clínicas, avançadas)<br/>"
            "✅ <b>2 cursos completos</b> (Anti-hipertensivos + Antidiabéticos)<br/>"
            "✅ <b>7 módulos educacionais</b> com vídeos reais<br/>"
            "✅ <b>Quiz interativo + Certificado digital</b><br/>"
            "✅ <b>Mapas mentais + Árvores de decisão</b><br/>"
            "✅ <b>Flashcards + Cronograma + Ranking</b>",
            corpo
        ))

        story2.append(Paragraph("DIFERENCIAL COMPETITIVO", subtitulo))
        story2.append(Paragraph(
            "🚫 <b>SEM</b> medicamentos de uso exclusivamente hospitalar (foco em drogaria)<br/>"
            "🚫 <b>SEM</b> conteúdo enganoso ou publicitário<br/>"
            "🚫 <b>SEM</b> necessidade de internet para 90% das funções",
            corpo
        ))
        story2.append(Paragraph(
            "✅ <b>Conteúdo curado</b> por farmacêuticos<br/>"
            "✅ <b>Bulas oficiais</b> da Anvisa<br/>"
            "✅ <b>Funciona offline</b> após primeiro acesso<br/>"
            "✅ <b>Atualizações</b> mensais com novo conteúdo",
            corpo
        ))

        story2.append(Paragraph("MERCADO-ALVO", subtitulo))
        story2.append(Paragraph(
            "📊 <b>Brasil:</b> 88.000 farmácias + 70.000 drogarias<br/>"
            "📊 <b>Profissionais:</b> ~250.000 farmacêuticos + 100.000 balconistas<br/>"
            "📊 <b>Estudiantes:</b> 200.000+ em cursos de farmácia<br/>"
            "📊 <b>TAM:</b> R$ 500M+ em educação farmacêutica",
            corpo
        ))

        story2.append(Paragraph("PLANOS E PREÇOS", subtitulo))
        data = [
            ["Plano", "Preço", "Inclui"],
            ["FREE", "R$ 0", "30% medicamentos + calculadoras básicas"],
            ["PRO", "R$ 29,90/mês", "Todos medicamentos + interações"],
            ["PREMIUM", "R$ 79,90/mês", "Tudo + cursos + vídeos + certificado"],
            ["ENTERPRISE", "R$ 297/mês", "Múltiplos usuários (clínicas, redes)"],
        ]
        t = Table(data, colWidths=[4*cm, 4*cm, 9*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COR_PRIMARIA),
            ('TEXTCOLOR', (0,0), (-1,0), HexColor('#ffffff')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#f8fafc'), HexColor('#ffffff')]),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story2.append(t)

        story2.append(Spacer(1, 1*cm))
        story2.append(Paragraph("PROJEÇÃO DE RECEITA", subtitulo))
        story2.append(Paragraph(
            "📈 <b>Cenário conservador (1 ano):</b><br/>"
            "• 1.000 PRO + 200 PREMIUM + 20 ENTERPRISE<br/>"
            "• MRR: R$ 29.900 + R$ 15.980 + R$ 5.940 = <b>R$ 51.820/mês</b><br/>"
            "• ARR: <b>R$ 621.840/ano</b>",
            corpo
        ))

        story2.append(Spacer(1, 2*cm))
        story2.append(Paragraph("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", obs))
        story2.append(Paragraph("Auxílio Farmácia © 2026 - Apresentação atualizada em 08/07/2026", obs))

        doc2.build(story2)
        print(f"  ✅ Apresentação Comercial: {apresentacao_path.stat().st_size:,} bytes")

    except ImportError as e:
        print(f"  ❌ reportlab nao disponivel: {e}")


# ========== 5. CRIAR CHANGELOG ==========
def create_changelog():
    changelog = OUTPUT / "atualizacoes" / "CHANGELOG_2026_07.md"
    today = datetime.now().strftime("%d/%m/%Y")

    content = f"""# 📋 CHANGELOG - Auxílio Farmácia

## Versão 2026.07 - {today}

### 🏥 Remoção de Medicamentos Hospitalares

**Motivação:** Foco em uso ambulatorial e atenção primária.

**Removidos (4):**
- ❌ Meropenem (carbapenêmico IV)
- ❌ Vancomicina (glicopeptídeo IV)
- ❌ Adrenalina (vasopressor emergência)
- ❌ Ceftriaxona (cefalosporina 3ª IM/IV)

**Mantidos (com apresentação oral/topical):**
- ✅ Linezolida, Aciclovir, Fenobarbital, Midazolam
- ✅ Ondansetrona, Hidrocortisona, Digoxina, Furosemida
- ✅ Budesonida inalatória

### 📊 Estatísticas

| Métrica | Antes | Depois |
|---------|-------|--------|
| **Total medicamentos** | 62 | **58** |
| **MEDS_DROGARIA** | 33 | 33 |
| **MEDS_EXTRAS** | 26 | **22** |
| **MEDS_TOPICOS** | 2 | 2 |
| **MEDS_DERMICOS** | 1 | 1 |

### 📄 Documentos Atualizados

- ✅ 6 dashboards regenerados
- ✅ Manual do Administrador (PDF) atualizado
- ✅ Apresentação Comercial (PDF) atualizada
- ✅ ZIPs (completo e site) regenerados
- ✅ Documento de mudanças criado

### 🔄 Próximas Versões

- **2026.08:** Adicionar nomes comerciais brasileiros (Marevan®, Xarelto®, etc.)
- **2026.09:** Adicionar 10 medicamentos ambulatoriais novos
- **2026.10:** Integração com Bulário Eletrônico da Anvisa

---

## Versões Anteriores

### 2026.06 - Rebrand para "Auxílio Farmácia"
### 2026.05 - Sistema de Auditoria completo
### 2026.04 - Pagamento real (Stripe + Asaas)
### 2026.03 - 7 módulos educacionais
### 2026.02 - Trilha de aprendizado + Quiz + Certificado
"""

    with open(changelog, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n📋 Changelog criado: {changelog}")


def main():
    print("=" * 60)
    print("🔄 ATUALIZAÇÃO COMPLETA - Versão 2026.07")
    print("=" * 60)

    print("\n1️⃣ Atualizando admin.html...")
    update_admin()

    print("\n2️⃣ Atualizando landing.html...")
    update_landing()

    print("\n3️⃣ Regenerando ZIPs...")
    regenerate_zips()

    print("\n4️⃣ Regenerando PDFs...")
    regenerate_pdfs()

    print("\n5️⃣ Criando changelog...")
    create_changelog()

    print("\n" + "=" * 60)
    print("✅ TUDO ATUALIZADO!")
    print("=" * 60)
    print("\nArquivos finais:")
    for f in sorted(OUTPUT.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            size = f.stat().st_size
            if size > 1000:
                print(f"  📄 {f.name}: {size:,} bytes")


if __name__ == "__main__":
    main()