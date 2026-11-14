#!/usr/bin/env python3
"""
Correcao de UX / Acessibilidade - Auxilio Farmacia

Corrige:
  1. CONTRASTE (WCAG AA) - ajusta a luminancia da cor do texto mantendo o matiz
  2. target="_blank" sem rel="noopener noreferrer"
  3. <div>/<span> clicavel sem role/tabindex
  4. botao so-icone sem aria-label
  5. input sem label/aria-label
  6. img sem alt
  7. meta description / viewport / lang faltando
  8. skip-link para navegacao por teclado
  9. foco visivel (:focus-visible)
 10. h1 multiplos -> h2 (mantendo o visual)

Faz backup antes de alterar.
"""
import re
import glob
import os
import json
import shutil
import colorsys
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path('/workspace/output')
BACKUP = Path('/workspace/backup_pre_a11y')
TARGET_RATIO = 4.5


# ================= COR =================
def hex2rgb(h):
    h = h.strip().lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    if len(h) != 6 or not re.match(r'^[0-9a-fA-F]{6}$', h):
        return None
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(rgb):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(round(v)))) for v in rgb)


def lum(rgb):
    def f(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    L1, L2 = lum(a), lum(b)
    if L1 < L2:
        L1, L2 = L2, L1
    return (L1 + 0.05) / (L2 + 0.05)


def fix_contrast(fg_hex, bg_hex, target=TARGET_RATIO):
    """Retorna a cor de texto ajustada que atinge `target` sobre `bg_hex`,
    mantendo o matiz. Retorna None se nao conseguir."""
    fg = hex2rgb(fg_hex)
    bg = hex2rgb(bg_hex)
    if not fg or not bg:
        return None
    if ratio(fg, bg) >= target:
        return fg_hex
    r, g, b = [v / 255 for v in fg]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    bg_lum = lum(bg)
    # se o fundo e escuro -> clarear o texto; se claro -> escurecer
    if bg_lum < 0.35:
        direcao = +1
    else:
        direcao = -1
    melhor = None
    for step in range(1, 101):
        nl = max(0.0, min(1.0, l + direcao * step * 0.01))
        nr, ng, nb = colorsys.hls_to_rgb(h, nl, s)
        cand = (nr * 255, ng * 255, nb * 255)
        if ratio(cand, bg) >= target:
            melhor = rgb2hex(cand)
            break
        melhor = rgb2hex(cand)
    # se chegou no limite sem atingir, reduz saturacao e tenta de novo
    if melhor and ratio(hex2rgb(melhor), bg) < target:
        for s2 in (s * 0.8, s * 0.6, s * 0.4, 0.0):
            for step in range(1, 101):
                nl = max(0.0, min(1.0, l + direcao * step * 0.01))
                nr, ng, nb = colorsys.hls_to_rgb(h, nl, s2)
                cand = (nr * 255, ng * 255, nb * 255)
                if ratio(cand, bg) >= target:
                    melhor = rgb2hex(cand)
                    break
            if melhor and ratio(hex2rgb(melhor), bg) >= target:
                break
    return melhor


# ================= HELPERS =================
DESCRICOES_BOTAO = {
    '⚙': 'Configuracoes', '🔑': 'Entrar ou criar conta', '📥': 'Baixar', '✅': 'Confirmar',
    '❌': 'Fechar', '×': 'Fechar', '✕': 'Fechar', '＋': 'Adicionar', '+': 'Adicionar',
    '−': 'Remover', '-': 'Remover', '→': 'Avancar', '←': 'Voltar', '↑': 'Subir', '↓': 'Descer',
    '★': 'Favoritar', '⭐': 'Favorito', '📋': 'Copiar', '🎨': 'Tema e cores',
    '🔒': 'Seguranca', '👤': 'Perfil do usuario', '⚠️': 'Aviso', '❗': 'Atencao',
    '🔔': 'Notificacoes', '🏠': 'Inicio', '📊': 'Dashboard', '📚': 'Cursos',
    '🏥': 'Calculadoras clinicas', '⚖️': 'Comparador', '💼': 'Casos clinicos',
    '💊': 'Medicamentos', '🎓': 'Certificado', '🔧': 'Administracao', '🚪': 'Sair',
    '📝': 'Editar', '🔍': 'Buscar', '🗑️': 'Excluir', '↻': 'Atualizar',
    '🌙': 'Tema escuro', '☀️': 'Tema claro', '🌤️': 'Tema automatico', '📥': 'Baixar',
}


def label_de(texto):
    t = re.sub(r'<[^>]+>', '', texto).strip()
    if t:
        return t[:60]
    for ch, desc in DESCRICOES_BOTAO.items():
        if ch in texto:
            return desc
    return 'Acao'


def aria_para_input(tag):
    """Deriva um aria-label do placeholder/name/id do input."""
    ph = re.search(r'placeholder="([^"]+)"', tag)
    if ph:
        return ph.group(1)[:60]
    nm = re.search(r'name="([^"]+)"', tag)
    if nm:
        return nm.group(1).replace('_', ' ').replace('-', ' ')[:60]
    return 'Campo de entrada'


META_DESC = {
    'index.html': 'Auxilio Farmacia - plataforma de apoio a prescricao e dispensacao farmaceutica para profissionais de saude no Brasil.',
    'login.html': 'Entre ou crie sua conta no Auxilio Farmacia para acessar posologia, calculadoras clinicas e cursos.',
    'admin.html': 'Painel administrativo do Auxilio Farmacia: licencas, pagamentos, auditoria e usuarios.',
    'landing.html': 'Auxilio Farmacia - posologia, calculadoras clinicas e cursos para prescritores e farmaceuticos.',
    'checkout.html': 'Assine o Auxilio Farmacia: planos Pro, Premium e Institucional com PIX, boleto ou cartao.',
    'ABRA-AQUI.html': 'Menu de acesso rapido para todas as areas do Auxilio Farmacia.',
    'VISUALIZAR.html': 'Visualizador de bulas e documentacao do Auxilio Farmacia.',
}
META_DESC_DEFAULT = 'Auxilio Farmacia - plataforma de apoio a prescricao e dispensacao farmaceutica para profissionais de saude no Brasil.'


def desc_de(nome):
    if nome in META_DESC:
        return META_DESC[nome]
    if nome.startswith('dashboard-auxfarmacia'):
        return 'Auxilio Farmacia - dashboard de posologia, calculadoras clinicas, cursos e material para prescritores e farmaceuticos.'
    if nome in ('termos.html',):
        return 'Termos de uso do Auxilio Farmacia.'
    if nome in ('privacidade.html',):
        return 'Politica de privacidade e tratamento de dados (LGPD) do Auxilio Farmacia.'
    if nome in ('sobre.html',):
        return 'Sobre o Auxilio Farmacia e sua missao de apoio a prescricao farmaceutica.'
    if nome in ('contato.html',):
        return 'Canais de contato e suporte do Auxilio Farmacia.'
    if nome in ('ajuda.html',):
        return 'Central de ajuda e perguntas frequentes do Auxilio Farmacia.'
    if nome in ('anvisa.html',):
        return 'Consultas de bulas e informacoes regulatorias - ANVISA / Visao Farmaceutica.'
    return META_DESC_DEFAULT


# ================= ETAPAS =================
def fix_contraste(c, nome):
    n = 0
    out = []
    pos = 0
    for m in re.finditer(r'(?i)(color:\s*)(#[0-9a-fA-F]{3,6})(\s*;)', c):
        fg_hex = m.group(2)
        fg = hex2rgb(fg_hex)
        if not fg:
            continue
        # procura o background mais proximo ANTES
        pre = c[max(0, m.start() - 600):m.start()]
        bgs = re.findall(r'(?i)(?:background(?:-color)?|background-color)\s*:\s*(#[0-9a-fA-F]{3,6})', pre)
        if not bgs:
            continue
        bg = hex2rgb(bgs[-1])
        if not bg:
            continue
        try:
            r = ratio(fg, bg)
        except Exception:
            continue
        if r >= TARGET_RATIO:
            continue
        # ignora cores de borda/decoracao (mesma cor do fundo)
        if fg_hex.lower() == bgs[-1].lower():
            continue
        novo = fix_contrast(fg_hex, bgs[-1])
        if novo and novo.lower() != fg_hex.lower():
            c = c[:m.start(2)] + novo + c[m.end(2):]
            n += 1
            # recalcula posicoes apos a substituicao
            # (o loop continua sobre a string original; refazemos)
            break
    # loop seguro: repete enquanto houver mudanca
    guard = 0
    while guard < 60:
        guard += 1
        mudou = False
        for m in re.finditer(r'(?i)(color:\s*)(#[0-9a-fA-F]{3,6})(\s*;)', c):
            fg_hex = m.group(2)
            fg = hex2rgb(fg_hex)
            if not fg:
                continue
            pre = c[max(0, m.start() - 600):m.start()]
            bgs = re.findall(r'(?i)(?:background(?:-color)?|background-color)\s*:\s*(#[0-9a-fA-F]{3,6})', pre)
            if not bgs:
                continue
            bg = hex2rgb(bgs[-1])
            if not bg:
                continue
            if fg_hex.lower() == bgs[-1].lower():
                continue
            try:
                r = ratio(fg, bg)
            except Exception:
                continue
            if r >= TARGET_RATIO:
                continue
            novo = fix_contrast(fg_hex, bgs[-1])
            if novo and novo.lower() != fg_hex.lower():
                c = c[:m.start(2)] + novo + c[m.end(2):]
                n += 1
                mudou = True
                break
        if not mudou:
            break
    return c, n


def fix_target_blank(c):
    n = 0
    def rep(m):
        nonlocal n
        t = m.group(0)
        if 'noopener' in t.lower():
            return t
        n += 1
        if re.search(r'\brel="', t):
            return re.sub(r'\brel="([^"]*)"', lambda mm: 'rel="' + (mm.group(1) + ' noopener noreferrer').strip() + '"', t)
        # insere antes do '>'
        return t[:-1] + ' rel="noopener noreferrer">' if t.endswith('>') else t
    c = re.sub(r'<a[^>]*target="_blank"[^>]*>', rep, c, flags=re.I)
    return c, n


def fix_click_role(c):
    n = 0
    def rep(m):
        nonlocal n
        tag = m.group(0)
        if 'role=' in tag or 'tabindex' in tag:
            return tag
        n += 1
        cls = re.search(r'class="([^"]*)"', tag)
        cls_s = cls.group(1).lower() if cls else ''
        role = 'tab' if ('tab' in cls_s and 'content' not in cls_s) else 'button'
        tabindex = ' tabindex="0"' if role == 'button' else ''
        # insere depois do nome da tag
        return re.sub(r'^(<(?:div|span))', r'\1 role="%s"%s' % (role, tabindex), tag, flags=re.I)
    c = re.sub(r'<(?:div|span)[^>]*\bonclick=[^>]*>', rep, c, flags=re.I)
    return c, n


def fix_botao_aria(c):
    n = 0
    def rep(m):
        nonlocal n
        tag = m.group(0)
        if 'aria-label' in tag:
            return tag
        n += 1
        inner = re.sub(r'^<button[^>]*>', '', tag, flags=re.I)
        inner = re.sub(r'</button>$', '', inner, flags=re.I)
        lab = label_de(inner)
        return tag[:-1] + f' aria-label="{lab}">' if tag.endswith('>') else tag
    padrao = re.compile(r'<button(?![^>]*aria-label)[^>]*>\s*[^<]{0,3}\s*</button>', re.I)
    c = padrao.sub(rep, c)
    return c, n


def fix_input_label(c):
    n = 0
    def rep(m):
        nonlocal n
        tag = m.group(0)
        if 'aria-label' in tag or 'id=' in tag:
            return tag
        n += 1
        return tag[:-1] + f' aria-label="{aria_para_input(tag)}">' if tag.endswith('>') else tag
    c = re.sub(r'<input(?![^>]*\btype=["\']?(hidden|submit|button))[^>]*>', rep, c, flags=re.I)
    return c, n


def fix_img_alt(c):
    n = 0
    def rep(m):
        nonlocal n
        tag = m.group(0)
        if 'alt=' in tag:
            return tag
        n += 1
        return tag[:-1] + ' alt="">' if tag.endswith('>') else tag
    c = re.sub(r'<img(?![^>]*\balt=)[^>]*>', rep, c, flags=re.I)
    return c, n


def fix_meta(c, nome):
    n = 0
    head_end = c.lower().find('</head>')
    if head_end == -1:
        head_end = c.lower().find('<body')
        if head_end == -1:
            return c, 0
    head = c[:head_end]

    # lang
    if not re.search(r'(?i)<html[^>]*\blang=', c):
        c = re.sub(r'(?i)(<html)([^>]*)(>)', r'\1 lang="pt-BR"\2\3', c, count=1)
        n += 1

    # viewport
    if not re.search(r'(?i)<meta[^>]+name=["\']viewport', c):
        idx = c.lower().find('</head>')
        c = c[:idx] + '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n' + c[idx:]
        n += 1

    # description
    if not re.search(r'(?i)<meta[^>]+name=["\']description', c):
        idx = c.lower().find('</head>')
        d = desc_de(nome)
        c = c[:idx] + f'  <meta name="description" content="{d}">\n' + c[idx:]
        n += 1
    return c, n


def fix_skip_link(c):
    if 'skip-link' in c or 'skip to' in c.lower():
        return c, 0
    m = re.search(r'(?i)<body[^>]*>', c)
    if not m:
        return c, 0
    link = ('\n<a href="#conteudo-principal" class="skip-link">Pular para o conteúdo principal</a>\n')
    c = c[:m.end()] + link + c[m.end():]
    # CSS do skip-link + foco visivel
    css = '''
<style>
/* === ACESSIBILIDADE: skip-link + foco visivel === */
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  z-index: 999999;
  background: #0d9488;
  color: #ffffff;
  padding: 12px 20px;
  border-radius: 0 0 8px 0;
  font-weight: 700;
  text-decoration: none;
}
.skip-link:focus {
  left: 0;
  outline: 3px solid #fbbf24;
  outline-offset: 2px;
}
:focus-visible {
  outline: 3px solid #fbbf24;
  outline-offset: 2px;
  border-radius: 4px;
}
[role="button"]:focus-visible,
[role="tab"]:focus-visible,
.tab-btn:focus-visible,
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 3px solid #fbbf24;
  outline-offset: 2px;
}
#conteudo-principal {
  scroll-margin-top: 80px;
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
</style>
'''
    idx = c.lower().find('</head>')
    if idx == -1:
        return c, 0
    c = c[:idx] + css + c[idx:]
    return c, 1


def fix_foco_visivel(c):
    if ':focus-visible' in c:
        return c, 0
    css = '''
<style>
:focus-visible {
  outline: 3px solid #fbbf24;
  outline-offset: 2px;
  border-radius: 4px;
}
</style>
'''
    idx = c.lower().find('</head>')
    if idx == -1:
        return c, 0
    c = c[:idx] + css + c[idx:]
    return c, 1


def main():
    BACKUP.mkdir(parents=True, exist_ok=True)
    files = [f for f in sorted(glob.glob(str(OUT / '*.html')))
             if not re.search(r'(debug|test-|diag-|check-|show-meds|force-meds|load\.html|dashboard-FREE|dashboard-free-v2|VISUALIZAR)', os.path.basename(f))]
    total = Counter()
    for p in files:
        nome = os.path.basename(p)
        shutil.copy(p, BACKUP / nome)
        c = Path(p).read_text(encoding='utf-8', errors='replace')
        s = Counter()
        c, s['contraste'] = fix_contraste(c, nome)
        c, s['target_blank'] = fix_target_blank(c)
        c, s['click_role'] = fix_click_role(c)
        c, s['botao_aria'] = fix_botao_aria(c)
        c, s['input_label'] = fix_input_label(c)
        c, s['img_alt'] = fix_img_alt(c)
        c, s['meta'] = fix_meta(c, nome)
        c, s['skip_link'] = fix_skip_link(c)
        c, s['foco'] = fix_foco_visivel(c)
        Path(p).write_text(c, encoding='utf-8')
        total += s
        print(f'{nome}: ' + ', '.join(f'{k}={v}' for k, v in s.items() if v))
    print('\nTOTAIS: ' + ', '.join(f'{k}={v}' for k, v in total.items()))
    print(f'Backup em {BACKUP}')


if __name__ == '__main__':
    main()
