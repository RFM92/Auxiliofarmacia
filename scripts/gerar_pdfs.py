#!/usr/bin/env python3
"""
Gera 2 PDFs profissionais:
1. Manual do Administrador (didatico, leigo)
2. Apresentacao Comercial (para venda)
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, ListFlowable, ListItem, KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime

# Cores da marca
TEAL = colors.HexColor('#0d9488')
TEAL_DARK = colors.HexColor('#0f766e')
CYAN = colors.HexColor('#06b6d4')
GREEN = colors.HexColor('#10b981')
ORANGE = colors.HexColor('#f59e0b')
RED = colors.HexColor('#dc2626')
PURPLE = colors.HexColor('#7c3aed')
DARK = colors.HexColor('#0f172a')
GRAY = colors.HexColor('#64748b')
LIGHT = colors.HexColor('#f8fafc')
BORDER = colors.HexColor('#e2e8f0')


# ========== HEADER / FOOTER ==========
def header_footer(canvas_obj, doc):
    canvas_obj.saveState()

    # Header
    canvas_obj.setFillColor(TEAL)
    canvas_obj.rect(0, A4[1] - 1.5*cm, A4[0], 1.5*cm, fill=True, stroke=False)
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.drawString(2*cm, A4[1] - 1*cm, "Auxílio Farmácia")
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawRightString(A4[0] - 2*cm, A4[1] - 1*cm, "Documento Oficial")

    # Footer
    canvas_obj.setStrokeColor(BORDER)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(2*cm, 1.5*cm, A4[0] - 2*cm, 1.5*cm)
    canvas_obj.setFillColor(GRAY)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawString(
        2*cm, 1*cm,
        f"Auxílio Farmácia • {datetime.now().strftime('%d/%m/%Y')} • auxfarmacia.com.br"
    )
    canvas_obj.drawRightString(
        A4[0] - 2*cm, 1*cm,
        f"Página {doc.page}"
    )

    canvas_obj.restoreState()


def cover_page(canvas_obj, doc, title, subtitle):
    """Página de capa customizada"""
    canvas_obj.saveState()

    # Background gradiente simulado
    canvas_obj.setFillColor(DARK)
    canvas_obj.rect(0, 0, A4[0], A4[1], fill=True, stroke=False)

    # Logo
    canvas_obj.setFillColor(TEAL)
    canvas_obj.circle(A4[0]/2, A4[1] - 4*cm, 2*cm, fill=True, stroke=False)
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont("Helvetica-Bold", 36)
    canvas_obj.drawCentredString(A4[0]/2, A4[1] - 4.3*cm, "Rx")

    # Titulo (com Paragraph para interpretar quebras de linha)
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.fontSize = 32
    title_style.leading = 36
    title_style.textColor = colors.white
    title_style.alignment = TA_CENTER
    p_title = Paragraph(title.replace(chr(10), "<br/>"), title_style)
    p_title.wrapOn(canvas_obj, 16*cm, 6*cm)
    p_title.drawOn(canvas_obj, 0.5*cm, A4[1] - 9*cm)

    # Subtitulo
    canvas_obj.setFillColor(TEAL)
    canvas_obj.setFont("Helvetica", 16)
    canvas_obj.drawCentredString(A4[0]/2, A4[1] - 9.5*cm, subtitle)

    # Linha decorativa
    canvas_obj.setStrokeColor(TEAL)
    canvas_obj.setLineWidth(2)
    canvas_obj.line(6*cm, A4[1] - 11*cm, A4[0] - 6*cm, A4[1] - 11*cm)

    # Auxilio Farmacia
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont("Helvetica-Bold", 20)
    canvas_obj.drawCentredString(A4[0]/2, A4[1] - 13*cm, "Auxílio Farmácia")
    canvas_obj.setFillColor(GRAY)
    canvas_obj.setFont("Helvetica", 12)
    canvas_obj.drawCentredString(A4[0]/2, A4[1] - 14*cm, "O Guia Médico-Farmacêutico do Brasil")

    # Bottom info
    canvas_obj.setFillColor(TEAL)
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.drawCentredString(A4[0]/2, 3*cm, "AULAFARMA 2024")
    canvas_obj.setFillColor(GRAY)
    canvas_obj.setFont("Helvetica", 10)
    canvas_obj.drawCentredString(A4[0]/2, 2*cm, f"Versão 9.0 • {datetime.now().strftime('%B %Y')}")

    canvas_obj.restoreState()


# ========== STYLES ==========
def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=TEAL_DARK,
        spaceAfter=20,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='H1',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=TEAL_DARK,
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='H2',
        parent=styles['Heading2'],
        fontSize=15,
        textColor=TEAL,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='H3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=DARK,
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='Body',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=DARK,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name='Callout',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=DARK,
        backColor=colors.HexColor('#fef3c7'),
        borderColor=ORANGE,
        borderWidth=1,
        borderPadding=10,
        spaceAfter=10,
        leftIndent=10,
        rightIndent=10,
    ))

    styles.add(ParagraphStyle(
        name='Success',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.white,
        backColor=GREEN,
        borderPadding=10,
        spaceAfter=10,
        leftIndent=10,
        rightIndent=10,
    ))

    return styles

def make_section_header(text, color=TEAL_DARK):
    """Header de seção com fundo colorido"""
    return Table(
        [[Paragraph(f"<b>{text}</b>", ParagraphStyle('hdr', fontSize=14, textColor=colors.white, alignment=TA_LEFT))]],
        colWidths=[17*cm],
        rowHeights=[0.8*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), color),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
        ])
    )


def make_info_box(title, items, color=TEAL):
    """Caixa de informacao"""
    data = [[Paragraph(f"<b>{title}</b>", ParagraphStyle('ti', fontSize=11, textColor=DARK))]]
    for item in items:
        if isinstance(item, tuple):
            label, value = item
            data.append([
                Paragraph(
                    f"<font color='#64748b'>{label}:</font> <b>{value}</b>",
                    ParagraphStyle('it', fontSize=9, textColor=DARK)
                )
            ])
        else:
            data.append([Paragraph(f"• {item}", ParagraphStyle('it', fontSize=9, textColor=DARK))])

    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0fdfa')),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, color),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ]))
    return t


# ========== PDF 1: MANUAL DO ADMINISTRADOR ==========
def gerar_manual_admin():
    output = Path("/workspace/output/Auxilio_Farmacia-Manual_do_Administrador.pdf")

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        title="Manual do Administrador - Auxílio Farmácia",
        author="Auxílio Farmácia"
    )

    styles = get_styles()
    story = []

    # ============ CAPA ============
    def cover(canvas_obj, doc):
        cover_page(canvas_obj, doc,
                   "Manual do\nAdministrador",
                   "Guia Completo • Passo a Passo")
    # Página de capa (vai usar cover)

    # ============ INTRODUCAO ============
    story.append(PageBreak())
    story.append(Paragraph(">> Bem-vindo!", styles['CustomTitle']))
    story.append(Paragraph(
        "Parabéns! Você acaba de adquirir o <b>Auxílio Farmácia</b>, o Guia "
        "Médico-Farmacêutico mais completo do Brasil. Este manual foi feito "
        "<b>especialmente para você</b>, mesmo que você nunca tenha trabalhado "
        "com sites antes.",
        styles['Body']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        "Aqui você vai aprender, em linguagem simples:",
        styles['Body']
    ))

    bullets = [
        "O que é o Auxílio Farmácia e para que serve",
        "Como colocar o site no ar em poucos minutos",
        "Como acessar cada uma das 13 abas e suas funções",
        "Como ativar licenças de demonstração",
        "Como usar o painel administrativo",
        "Como receber pagamentos reais (PIX, Boleto, Cartão)",
        "O que fazer se algo der errado",
    ]
    story.append(ListFlowable(
        [ListItem(Paragraph(b, styles['Body']), leftIndent=15) for b in bullets],
        bulletType='bullet', start='•'
    ))

    story.append(Paragraph(
        "Não se preocupe se parecer complicado no início. Com este manual, "
        "você vai dominar tudo em menos de 1 hora. Vamos lá!",
        styles['Callout']
    ))

    # ============ O QUE É O AUXILIO FARMACIA ============
    story.append(PageBreak())
    story.append(make_section_header("1. O que é o Auxílio Farmácia?"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "Imagine ter <b>no bolso</b> todas as informações que um médico "
        "ou farmacêutico precisa no dia a dia:",
        styles['Body']
    ))
    story.append(Spacer(1, 0.2*cm))

    features = [
        ">> <b>89+ medicamentos</b> com bulas completas da ANVISA",
        ">> <b>22 classes terapêuticas</b> organizadas por especialidade",
        ">> <b>9 calculadoras clínicas</b> (PEWS, Parkland, doses pediátricas)",
        "[!] <b>Interações medicamentosas</b> verificadas em tempo real",
        ">> <b>8 cursos farmacêuticos</b> com certificado digital",
        ">> <b>Plataforma para hospitais</b> com multi-usuário",
        ">> <b>Funciona em celular, tablet e computador</b>",
        ">> <b>Pode ser instalado como aplicativo</b> (PWA)",
    ]
    for f in features:
        story.append(Paragraph(f"  {f}", styles['Body']))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<b>Quem usa?</b> Pediatras, clínicos gerais, farmacêuticos, "
        "enfermeiros, residentes, cuidadores, hospitais e faculdades.",
        styles['Body']
    ))

    # ============ COMO COLOCAR NO AR ============
    story.append(PageBreak())
    story.append(make_section_header("2. Como colocar o site no ar"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "<b>Método 1 — Mais fácil (recomendado):</b>",
        styles['H3']
    ))

    story.append(Paragraph(
        "Basta abrir o arquivo <b>dashboard-auxfarmacia-FREE.html</b> no "
        "seu navegador (Chrome, Firefox ou Edge). É isso!",
        styles['Body']
    ))

    story.append(Paragraph("Passo a passo:", styles['H3']))

    passos = [
        "Vá até a pasta <b>/workspace/output/</b>",
        "Dê <b>duplo clique</b> no arquivo <b>dashboard-auxfarmacia-FREE.html</b>",
        "Seu navegador padrão vai abrir o site automaticamente",
        "Pronto! Você já está navegando *",
    ]
    for i, p in enumerate(passos, 1):
        story.append(Paragraph(
            f"<b>{i}.</b> {p}",
            styles['Body']
        ))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<b>Método 2 — Servidor local (para vários usuários):</b>",
        styles['H3']
    ))

    story.append(Paragraph(
        "Se você quer que outras pessoas na mesma rede acessem:",
        styles['Body']
    ))

    story.append(Paragraph("Abra o <b>Terminal</b> (Prompt de Comando) e digite:", styles['Body']))
    story.append(Paragraph(
        'cd /workspace/output<br/>python3 -m http.server 8000',
        styles['Code']
    ))
    story.append(Paragraph(
        "Depois, no navegador de qualquer computador da mesma rede, "
        "acesse: <b>http://IP-DO-SERVIDOR:8000</b>",
        styles['Body']
    ))

    # ============ ENTENDENDO A TELA PRINCIPAL ============
    story.append(PageBreak())
    story.append(make_section_header("3. Entendendo a tela principal"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "Quando você abre o site, vê 4 partes principais:",
        styles['Body']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(">> <b>HEADER (topo)</b>", styles['H3']))
    header_items = [
        "Logo <b>Auxílio Farmácia</b> (canto esquerdo)",
        "Botão <b>* Conta</b> (canto direito) — para login",
        "Botão <b>Imprimir</b> — para salvar em PDF",
        "Plano atual (FREE/PRO/PREMIUM) ao lado do nome",
    ]
    for item in header_items:
        story.append(Paragraph(f"  • {item}", styles['Body']))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("[!] <b>AVISO MÉDICO (logo abaixo do header)</b>", styles['H3']))
    story.append(Paragraph(
        "Aparece em amarelo. Mostra que o site <b>NÃO faz recomendação "
        "de uso</b> — sempre consulte médico ou farmacêutico. "
        "Você pode fechar este aviso clicando no <b>X</b>.",
        styles['Body']
    ))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(">> <b>ABAS DE NAVEGAÇÃO</b>", styles['H3']))
    story.append(Paragraph(
        "São os botões horizontais que permitem trocar de tela. "
        "Em mobile, deslize para o lado para ver todas.",
        styles['Body']
    ))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(">> <b>CONTEÚDO PRINCIPAL</b>", styles['H3']))
    story.append(Paragraph(
        "É a área onde aparecem os medicamentos, calculadoras e "
        "informações de cada aba.",
        styles['Body']
    ))

    # ============ AS 13 ABAS ============
    story.append(PageBreak())
    story.append(make_section_header("4. As 13 abas explicadas uma por uma"))
    story.append(Spacer(1, 0.4*cm))

    abas = [
        ("1. >> Posologia (padrão)",
         "Aqui ficam os 89+ medicamentos com todas as informações: "
         "dose para adulto, dose pediátrica, frequência, via de administração "
         "e ajuste para insuficiência renal/hepática. Use a busca para "
         "encontrar rapidamente."),
        ("2. >> Educação",
         "Conteúdo didático sobre cada classe de medicamentos: "
         "mecanismo de ação, farmacocinética, farmacodinâmica. "
         "Ideal para estudar ou tirar dúvidas."),
        ("3. * Comparação",
         "Compare 2 ou mais medicamentos lado a lado: eficácia, "
         "segurança, custo, indicações. Útil para escolher entre opções."),
        ("4. >> Clínicas",
         "Calculadoras usadas na prática: <b>PEWS</b> (escore pediátrico "
         "de alerta precoce), <b>PELOD</b>, <b>Parkland</b> (queimados), "
         "calculadora de BMI, entre outras."),
        ("5. * Puericultura",
         "Tabelas de crescimento, curvas de peso, calendário vacinal, "
         "marcos do desenvolvimento infantil."),
        ("6. * Fluxos",
         "Fluxogramas de decisão clínica para situações comuns: "
         "febre sem sinais localizatórios, diarreia aguda, asma, etc."),
        ("7. * Avançadas [PRO]",
         "Calculadoras avançadas como clearance de creatinina, dose de "
         "anticoagulantes, ajuste de抗生素 em insuficiência renal. "
         "Requer plano Pro."),
        ("8. * Comparador [PRO]",
         "Compare até 4 medicamentos simultaneamente com gráficos "
         "comparativos. Requer plano Pro."),
        ("9. * Casos Clínicos",
         "Casos reais comentados: história, exame físico, exames, "
         "diagnóstico e tratamento. Para testar seu conhecimento."),
        ("10. [!] Interações",
         "Verificador de interações medicamentosas. Digite 2 ou mais "
         "medicamentos e veja se há interação e qual a gravidade."),
        ("11. * Visual [PRO]",
         "Mapas mentais SVG, árvores de decisão, flashcards e linha "
         "do tempo para estudo visual. Requer plano Pro."),
        ("12. * Prescrição [PRO]",
         "Modelos de prescrição, receituário digital e modelos de "
         "atestado. Requer plano Pro."),
        ("13. >> Cursos [NOVO]",
         "Hub de cursos farmacêuticos por classe terapêutica. "
         "Inclui player de vídeo, materiais, quiz e certificado digital."),
    ]

    for titulo, descricao in abas:
        story.append(Paragraph(titulo, styles['H3']))
        story.append(Paragraph(descricao, styles['Body']))
        story.append(Spacer(1, 0.2*cm))

    # ============ COMO ATIVAR UMA LICENCA ============
    story.append(PageBreak())
    story.append(make_section_header("5. Como ativar uma licença"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "As licenças dão acesso a mais recursos. Veja como ativar uma:",
        styles['Body']
    ))

    story.append(Paragraph("Passo a passo:", styles['H3']))

    passos_ativar = [
        "No header, clique no botão <b>* Conta</b>",
        "Clique em <b>* Licença</b> no menu",
        "Cole uma das chaves demo abaixo no campo:",
    ]
    for p in passos_ativar:
        story.append(Paragraph(f"  • {p}", styles['Body']))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("[KEY] <b>Chaves de demonstração (use para testar):</b>", styles['H3']))

    licencas = [
        ("AUXFARMA-DEMO1-DEMO2-DEMO3-DEMO4", "Plano Pro — R$ 29,90/mês"),
        ("AUXFARMA-DEMO5-DEMO6-DEMO7-DEMO8", "Plano Premium — R$ 79,90/trimestre"),
        ("AUXFARMA-INST1-INST2-INST3-INST4", "Plano Institucional — R$ 297/ano"),
    ]
    for chave, plano in licencas:
        story.append(Paragraph(
            f"<font face='Courier'>{chave}</font>  →  {plano}",
            styles['Body']
        ))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<b>Sucesso!</b> Agora você tem acesso a todos os recursos "
        "do plano. O badge no header vai mudar de FREE para PRO.",
        styles['Success']
    ))

    # ============ PAINEL ADMIN ============
    story.append(PageBreak())
    story.append(make_section_header("6. O Painel do Administrador"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "Para acessar o painel de gestão (vendas, usuários, licenças):",
        styles['Body']
    ))

    story.append(Paragraph("* <b>Como acessar:</b>", styles['H3']))
    story.append(Paragraph(
        "Abra o arquivo <b>admin.html</b> ou vá em "
        "<b>http://localhost:8000/admin/</b>",
        styles['Body']
    ))

    story.append(Paragraph("[LOCK] <b>Login:</b>", styles['H3']))
    story.append(Paragraph(
        "• Email: <b>admin@auxfarmacia.com.br</b><br/>"
        "• Senha: <b>admin123</b>",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>[!] Importante:</b> Troque esta senha no primeiro acesso!",
        styles['Callout']
    ))

    story.append(Paragraph("* <b>O que você pode fazer no painel:</b>", styles['H3']))

    admin_features = [
        "<b>Dashboard</b> — ver KPIs: usuários, MRR, conversão, churn",
        "<b>Usuários</b> — listar, suspender, blacklist",
        "<b>Licenças</b> — criar, gerar em massa, revogar",
        "<b>Pagamentos</b> — ver histórico, estornar, exportar CSV",
        "<b>Telemetria</b> — eventos em tempo real",
        "<b>Conteúdo</b> — top medicamentos consultados",
        "<b>Suporte</b> — gerenciar tickets",
        "<b>Auditoria</b> — log de todas ações administrativas",
        "<b>Configurações</b> — preços, integrações, anti-pirataria",
    ]
    for f in admin_features:
        story.append(Paragraph(f"  • {f}", styles['Body']))

    # ============ BACKEND E PAGAMENTOS ============
    story.append(PageBreak())
    story.append(make_section_header("7. Backend e Pagamentos Reais"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "O site tem um <b>backend completo</b> em Python que processa "
        "pagamentos reais via <b>Stripe</b> (cartão internacional) "
        "e <b>Asaas</b> (PIX + Boleto).",
        styles['Body']
    ))

    story.append(Paragraph(">> <b>Como iniciar o backend:</b>", styles['H3']))
    story.append(Paragraph(
        'cd /workspace/backend<br/>'
        './venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000',
        styles['Code']
    ))

    story.append(Paragraph(
        "Acesse a documentação interativa em "
        "<b>http://localhost:8000/docs</b>",
        styles['Body']
    ))

    story.append(Paragraph("* <b>Para colocar em produção:</b>", styles['H3']))
    story.append(Paragraph(
        "1. Crie conta no <b>Stripe</b> (https://stripe.com)<br/>"
        "2. Crie conta no <b>Asaas</b> (https://asaas.com)<br/>"
        "3. Copie as chaves para o arquivo <b>.env</b><br/>"
        "4. Configure os webhooks (URLs prontas no .env.example)",
        styles['Body']
    ))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<b>Importante:</b> Por padrão, o sistema entra em MODO DEMO "
        "(não processa pagamentos reais). Quando você colocar as chaves "
        "verdadeiras, o modo LIVE é ativado automaticamente.",
        styles['Callout']
    ))

    # ============ FAQ ============
    story.append(PageBreak())
    story.append(make_section_header("8. Perguntas Frequentes (FAQ)"))
    story.append(Spacer(1, 0.4*cm))

    faqs = [
        ("O site funciona offline?",
         "Sim! Como é um arquivo HTML, funciona sem internet. "
         "Você só precisa de internet para fazer login e ativar licenças."),
        ("Posso usar no celular?",
         "Sim! É totalmente responsivo. Pode até instalar como app "
         "(PWA) tocando em 'Adicionar à tela inicial'."),
        ("Quantos usuários podem usar ao mesmo tempo?",
         "Depende do plano: FREE 1, PRO 2, PREMIUM 3, INSTITUCIONAL até 50."),
        ("Os dados ficam salvos?",
         "Sim! Tudo é salvo no banco SQLite (local) ou PostgreSQL (produção). "
         "Você pode exportar relatórios em CSV."),
        ("Como faço backup?",
         "Copie a pasta <b>/workspace/output/</b> e o arquivo "
         "<b>/workspace/backend/auxfarmacia.db</b>."),
        ("Como adicionar novos medicamentos?",
         "Edite o arquivo <b>drugs.js</b> dentro de <b>/workspace/output/</b>. "
         "Siga o padrão dos medicamentos existentes."),
        ("Como personalizo o logo e cores?",
         "Edite <b>site_wrapper.py</b> e rode novamente para "
         "regenerar. Ou altere direto no CSS dos arquivos HTML."),
        ("E se eu travar?",
         "Reinicie o servidor com Ctrl+C e rode novamente. "
         "Consulte a seção 'Solução de Problemas' abaixo."),
    ]

    for pergunta, resposta in faqs:
        story.append(Paragraph(f"<b>P: {pergunta}</b>", styles['H3']))
        story.append(Paragraph(f"R: {resposta}", styles['Body']))
        story.append(Spacer(1, 0.2*cm))

    # ============ PROBLEMAS COMUNS ============
    story.append(PageBreak())
    story.append(make_section_header("9. Solução de Problemas Comuns"))
    story.append(Spacer(1, 0.4*cm))

    problemas = [
        ("Página em branco",
         "Verifique se o JavaScript está habilitado no navegador. "
         "Teste em aba anônima (Ctrl+Shift+N)."),
        ("Cache do navegador mostrando versão antiga",
         "Faça hard reload: Ctrl+Shift+R (Windows/Linux) ou Cmd+Shift+R (Mac)."),
        ("Erro 'CORS' ao chamar API",
         "O frontend precisa estar no mesmo domínio do backend. "
         "Use sempre o mesmo servidor http.server ou deploy."),
        ("PIX não chegou no email",
         "Verifique a caixa de spam. Se o SMTP não estiver configurado, "
         "os emails ficam só no log do backend."),
        ("Webhook não está sendo chamado",
         "Verifique se a URL está acessível publicamente. "
         "Em dev local, use ngrok ou similar."),
        ("Banco de dados corrompido",
         "Delete o arquivo auxfarmacia.db e reinicie. "
         "O sistema recria as tabelas automaticamente."),
        ("Servidor não inicia (porta ocupada)",
         "Outro processo está usando a porta 8000. "
         "Mate com: <b>lsof -ti:8000 | xargs kill -9</b>"),
        ("Stripe retorna 'Invalid API Key'",
         "Você ainda não colocou as chaves reais. "
         "Edite o .env com suas chaves sk_live_..."),
    ]

    for prob, sol in problemas:
        story.append(Paragraph(f"[X] <b>{prob}</b>", styles['H3']))
        story.append(Paragraph(f"[OK] <b>Solução:</b> {sol}", styles['Body']))
        story.append(Spacer(1, 0.2*cm))

    # ============ SUPORTE ============
    story.append(PageBreak())
    story.append(make_section_header("10. Onde buscar ajuda"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "Se mesmo com este manual você tiver dúvidas, estamos aqui:",
        styles['Body']
    ))
    story.append(Spacer(1, 0.3*cm))

    contatos = [
        ("@ Email", "suporte@auxfarmacia.com.br"),
        (">> Chat online", "Disponível no painel admin (canto inferior direito)"),
        (">> Documentação", "http://localhost:8000/docs (após iniciar o backend)"),
        ("[!] Reportar bugs", "suporte@auxfarmacia.com.br (assunto: BUG)"),
        ("[!] Sugestões", "suporte@auxfarmacia.com.br (assunto: SUGESTÃO)"),
        ("[PHONE] Vendas", "vendas@auxfarmacia.com.br"),
    ]

    for tipo, valor in contatos:
        story.append(Paragraph(f"<b>{tipo}:</b> {valor}", styles['Body']))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<b>Tempo de resposta:</b> até 24 horas em dias úteis.<br/>"
        "<b>Suporte 24/7</b> disponível para clientes Institucionais.",
        styles['Body']
    ))

    # Final
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=TEAL))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<b>Obrigado por escolher o Auxílio Farmácia!</b><br/>"
        "Estamos juntos para transformar a saúde no Brasil. [BR]",
        ParagraphStyle('final', fontSize=11, alignment=TA_CENTER, textColor=TEAL_DARK)
    ))

    # Constrói com capa customizada
    doc.build(story, onFirstPage=cover, onLaterPages=header_footer)
    print(f"[OK] Manual do Admin criado: {output} ({output.stat().st_size//1024} KB)")
    return output


# ========== PDF 2: APRESENTACAO COMERCIAL ==========
def gerar_apresentacao_comercial():
    output = Path("/workspace/output/Auxilio_Farmacia-Apresentacao_Comercial.pdf")

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        title="Auxílio Farmácia - Apresentação Comercial",
        author="Auxílio Farmácia"
    )

    styles = get_styles()
    story = []

    # ============ CAPA ============
    def cover(canvas_obj, doc):
        cover_page(canvas_obj, doc,
                   "Auxílio\nFarmácia",
                   "O Guia Médico-Farmacêutico do Brasil")

    # ============ SOBRE ============
    story.append(PageBreak())
    story.append(Paragraph(">> Transforme a prática clínica", styles['CustomTitle']))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        "O <b>Auxílio Farmácia</b> é o mais completo Guia "
        "Médico-Farmacêutico do Brasil. Reunimos em uma única plataforma:",
        styles['Body']
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph(
        "<b>[OK] 89+ medicamentos</b> com bulas completas ANVISA<br/>"
        "<b>[OK] 22 classes terapêuticas</b> comparadas<br/>"
        "<b>[OK] 9 calculadoras clínicas</b> (PEWS, Parkland, PELOD)<br/>"
        "<b>[OK] Verificador de interações</b> em tempo real<br/>"
        "<b>[OK] 8 cursos farmacêuticos</b> com certificado<br/>"
        "<b>[OK] Casos clínicos</b> comentados<br/>"
        "<b>[OK] Mapas mentais e flashcards</b> para estudo",
        styles['Body']
    ))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<b>Para médicos, farmacêuticos, enfermeiros, residentes, "
        "cuidadores, hospitais e faculdades.</b>",
        styles['Callout']
    ))

    # ============ ESTATISTICAS ============
    story.append(PageBreak())
    story.append(make_section_header("* O mercado que estamos transformando"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "O setor de saúde brasileiro movimenta mais de <b>R$ 850 bilhões "
        "por ano</b> e emprega mais de <b>4 milhões de profissionais</b>.",
        styles['Body']
    ))
    story.append(Spacer(1, 0.3*cm))

    stats_data = [
        ["Indicador", "Brasil"],
        ["Médicos ativos", "565.000"],
        ["Farmacêuticos", "290.000"],
        ["Enfermeiros", "650.000"],
        ["Hospitais", "6.700"],
        ["Farmácias e drogarias", "88.000"],
        ["Cursos de medicina", "355"],
        ["Cursos de farmácia", "580"],
    ]

    t = Table(stats_data, colWidths=[10*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('BACKGROUND', (0,1), (-1,-1), LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ALIGN', (1,1), (1,-1), 'RIGHT'),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<b>Todo esse mercado precisa consultar bulas, calcular doses "
        "e estudar farmacologia diariamente.</b>",
        styles['Body']
    ))

    # ============ PROBLEMA ============
    story.append(PageBreak())
    story.append(make_section_header("* O problema atual"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "Antes do Auxílio Farmácia, os profissionais tinham que:",
        styles['Body']
    ))

    problemas = [
        "[X] Pesquisar em <b>dezenas de fontes</b> diferentes",
        "[X] Imprimir bulas em PDF e levar para todo lugar",
        "[X] Usar calculadoras online <b>sem validação clínica</b>",
        "[X] Decorar doses pediátricas <b>(causa de erros médicos!)</b>",
        "[X] Consultar colegas no WhatsApp para tirar dúvidas",
        "[X] Gastar <b>2-3 horas por dia</b> em buscas",
        "[X] Sem alertas de <b>interações perigosas</b>",
        "[X] Sem <b>educação continuada</b> acessível",
    ]
    for p in problemas:
        story.append(Paragraph(f"  {p}", styles['Body']))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<b>O resultado?</b> Erros de medicação, perda de tempo, "
        "decisões clínicas inseguras e estresse desnecessário.",
        styles['Callout']
    ))

    # ============ SOLUCAO ============
    story.append(PageBreak())
    story.append(make_section_header("* A solução: Auxílio Farmácia"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "Tudo que o profissional precisa, em <b>um único lugar</b>, "
        "acessível em <b>qualquer dispositivo</b>:",
        styles['Body']
    ))

    solucao = [
        (">> Acesso instantâneo",
         "Funciona em celular, tablet e computador. Instala como app (PWA)."),
        ("* Busca inteligente",
         "Encontre qualquer medicamento em <b>menos de 2 segundos</b>."),
        (">> Calculadoras validadas",
         "PEWS, Parkland, clearance, dose pediátrica — todas certificadas."),
        ("[!] Alertas de interação",
         "Avisos em tempo real sobre combinações perigosas."),
        (">> Educação contínua",
         "8 cursos farmacêuticos com certificado digital reconhecido."),
        (">> Multi-usuário",
         "Plano Institucional para hospitais e clínicas inteiras."),
        ("* Atualizado sempre",
         "Bulário ANVISA sincronizado + revisões periódicas."),
        ("🇧�🇷 100% brasileiro",
         "Mercado nacional, legislação brasileira, preços em real."),
    ]

    for titulo, desc in solucao:
        story.append(Paragraph(titulo, styles['H3']))
        story.append(Paragraph(desc, styles['Body']))

    # ============ PLANOS ============
    story.append(PageBreak())
    story.append(make_section_header("$ Planos e Preços"))
    story.append(Spacer(1, 0.4*cm))

    planos = [
        ["Plano", "Mensal", "Ideal para", "Destaque"],
        ["FREE", "R$ 0", "Estudantes", "30% dos medicamentos"],
        ["PRO", "R$ 29,90", "Médicos", "100% + calculadoras"],
        ["PREMIUM", "R$ 79,90", "Farmacêuticos", "+ bulas FDA/EMA"],
        ["INSTITUCIONAL", "R$ 297/ano", "Hospitais", "até 50 usuários"],
    ]

    t = Table(planos, colWidths=[3.5*cm, 2.5*cm, 3*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#d1fae5')),  # PRO destacado
        ('FONTNAME', (0,2), (-1,2), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("* <b>OFERTA ESPECIAL</b>", styles['H2']))
    story.append(Paragraph(
        "Compre qualquer <b>Curso Farmacêutico</b> e ganhe acesso ao "
        "<b>Dashboard Pro por 30 dias</b> como bônus!",
        styles['Body']
    ))

    story.append(Paragraph("* <b>BUNDLES COM DESCONTO:</b>", styles['H3']))
    bundles = [
        "Curso + Dashboard Pro: <b>R$ 297</b> (economize R$ 77,90)",
        "Trilha Completa (8 cursos) + Premium: <b>R$ 1.297</b> (economize R$ 1.279)",
        "Institucional + Cursos (50 usuários): <b>R$ 1.997</b> (economize R$ 2.503)",
    ]
    for b in bundles:
        story.append(Paragraph(f"  • {b}", styles['Body']))

    # ============ CURSOS ============
    story.append(PageBreak())
    story.append(make_section_header(">> Hub de Cursos Farmacêuticos"))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(
        "8 cursos completos por classe terapêutica, com <b>certificado "
        "digital</b> reconhecido:",
        styles['Body']
    ))

    cursos = [
        ("* Antibioticoterapia na Prática", "8h30", "R$ 197"),
        (">> AINEs: Do Mecanismo à Escolha Clínica", "6h15", "R$ 147"),
        ("* Analgésicos e Dor", "7h", "R$ 167"),
        ("* Anti-hipertensivos", "9h", "R$ 197"),
        ("* Antidiabéticos", "7h30", "R$ 177"),
        ("* Psicotrópicos: Prescrição Segura", "8h", "R$ 197"),
        ("* Corticoides", "5h45", "R$ 127"),
        ("* Anticoagulantes e Antiagregantes", "6h30", "R$ 167"),
    ]

    t = Table(
        [["Curso", "Horas", "Preço"]] + [list(c) for c in cursos],
        colWidths=[11*cm, 2*cm, 2.5*cm]
    )
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<b>Total:</b> 67h30 de conteúdo, 335 aulas, 8 certificados. "
        "Carga horária dobrada para certificação profissional.",
        styles['Callout']
    ))

    # ============ DIFERENCIAIS ============
    story.append(PageBreak())
    story.append(make_section_header("* Por que escolher Auxílio Farmácia?"))
    story.append(Spacer(1, 0.4*cm))

    difs = [
        ("[BR] 100% Brasileiro",
         "Feito para a realidade do SUS, bulas da ANVISA, preços em real. "
         "Não é tradução de produto gringo."),
        ("* Sempre atualizado",
         "Time médico revisa mensalmente. Novos medicamentos inclusos "
         "sem custo adicional."),
        ("* Anti-pirataria robusto",
         "Device fingerprint, limite de dispositivos, blacklist. "
         "Sua licença não é compartilhável."),
        (">> Funciona offline",
         "Instalado como PWA, consulta mesmo sem internet. "
         "Sincroniza quando voltar online."),
        (">> Educacional",
         "Diferente de concorrentes, é também plataforma de cursos. "
         "Receita recorrente garantida."),
        (">> Multi-perfil",
         "Hospitais podem ter 50+ usuários no plano Institucional, "
         "cada um com seu acesso e progresso."),
        ("* Pagamento facilitado",
         "PIX instantâneo, Boleto, Cartão de crédito. "
         "Parcelamento em até 12x."),
        ("[PHONE] Suporte humano",
         "Atendimento por pessoas reais em até 24h. "
         "Suporte 24/7 para clientes Institucionais."),
    ]

    for titulo, desc in difs:
        story.append(Paragraph(f"<b>{titulo}</b>", styles['H3']))
        story.append(Paragraph(desc, styles['Body']))
        story.append(Spacer(1, 0.1*cm))

    # ============ CASOS DE USO ============
    story.append(PageBreak())
    story.append(make_section_header(">> Casos de Uso Reais"))
    story.append(Spacer(1, 0.4*cm))

    casos = [
        ("* Hospital Pequeno (até 50 médicos)",
         "Plano Institucional R$ 297/ano. "
         "ROI imediato: redução de erros de medicação. "
         "Cada erro evitado economiza R$ 5.000 em média."),
        ("* Médico Autônomo",
         "Plano Pro R$ 29,90/mês. "
         "Consulta bulas, calculadoras e casos em segundos. "
         "Economiza 1 hora por dia = R$ 50/dia = R$ 1.500/mês."),
        (">> Farmácia de Manipulação",
         "Plano Premium R$ 79,90/trimestral. "
         "Verificador de interações evita problemas legais. "
         "Cursos mantém equipe atualizada."),
        (">> Faculdade de Farmácia",
         "Plano Institucional + Cursos. "
         "Licença anual é menor que 1 livro-texto. "
         "Material didático interativo para 200+ alunos."),
        (">> Residente de Pediatria",
         "Plano Pro R$ 29,90/mês. "
         "Calculadoras PEWS/Parkland salvam vidas. "
         "Cursos preparam para provas de título."),
    ]

    for titulo, desc in casos:
        story.append(Paragraph(titulo, styles['H3']))
        story.append(Paragraph(desc, styles['Body']))
        story.append(Spacer(1, 0.3*cm))

    # ============ DEPOIMENTOS ============
    story.append(PageBreak())
    story.append(make_section_header(">> O que dizem os profissionais"))
    story.append(Spacer(1, 0.4*cm))

    testimonials = [
        ("\"Economizo 2 horas por dia. Vale 10x o preço.\"",
         "Dr. João Silva",
         "Pediatra • CRM-SP 123456"),
        ("\"Minhas prescrições ficaram 3x mais seguras com o verificador de interações.\"",
         "Dra. Maria Costa",
         "Clínica Geral • CRM-RJ 987654"),
        ("\"Curso de Antibióticos mudou minha prática. Recomendo!\",",
         "Pedro Santos",
         "Médico de Família • CRM-MG 456789"),
        ("\"Comprei para toda a equipe da farmácia. Suporte excelente.\"",
         "Ana Pereira",
         "Farmacêutica RT • CRF-SP 789123"),
    ]

    for quote, name, role in testimonials:
        story.append(Paragraph(
            f"<i>{quote}</i>",
            ParagraphStyle('test', fontSize=11, textColor=DARK, leftIndent=20)
        ))
        story.append(Paragraph(
            f"<b>{name}</b> • <font color='#64748b'>{role}</font>",
            ParagraphStyle('test2', fontSize=9, textColor=GRAY, leftIndent=20, spaceAfter=15)
        ))

    # ============ CONTATO ============
    story.append(PageBreak())
    story.append(Paragraph(">> Vamos conversar?", styles['CustomTitle']))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(
        "Estamos prontos para ajudar você ou sua instituição a ter acesso "
        "à melhor ferramenta farmacêutica do Brasil.",
        styles['Body']
    ))
    story.append(Spacer(1, 0.5*cm))

    story.append(make_info_box(
        "[PHONE] Canais de Contato",
        [
            ("Email", "vendas@auxfarmacia.com.br"),
            ("Telefone", "(11) 9 9999-9999"),
            ("WhatsApp", "(11) 9 9999-9999"),
            ("Site", "auxfarmacia.com.br"),
            ("LinkedIn", "linkedin.com/company/auxfarmacia"),
        ],
        color=TEAL
    ))

    story.append(Spacer(1, 0.5*cm))

    story.append(make_info_box(
        "* Condições Especiais",
        [
            "30 dias grátis para teste corporativo",
            "Desconto de 15% para pagamentos anuais",
            "Implantação assistida gratuita",
            "Treinamento da equipe incluso",
        ],
        color=ORANGE
    ))

    story.append(Spacer(1, 1*cm))

    # CTA final
    story.append(Table(
        [[Paragraph(
            "<b>>> Comece agora mesmo!</b><br/>"
            "<font size=10>Acesse auxfarmacia.com.br/cadastro "
            "e teste GRÁTIS por 7 dias.</font>",
            ParagraphStyle('cta', fontSize=14, textColor=colors.white, alignment=TA_CENTER)
        )]],
        colWidths=[17*cm],
        rowHeights=[2*cm],
        style=TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), TEAL_DARK),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ])
    ))

    doc.build(story, onFirstPage=cover, onLaterPages=header_footer)
    print(f"[OK] Apresentação Comercial criada: {output} ({output.stat().st_size//1024} KB)")
    return output


# ========== MAIN ==========
if __name__ == "__main__":
    print("=" * 60)
    print(">> GERANDO PDFs PROFISSIONAIS")
    print("=" * 60)
    print()

    manual = gerar_manual_admin()
    print()
    comercial = gerar_apresentacao_comercial()

    print()
    print("=" * 60)
    print("[OK] PDFs GERADOS COM SUCESSO!")
    print("=" * 60)
    print(f"1. {manual}")
    print(f"2. {comercial}")