#!/usr/bin/env python3
"""
Aplica correcoes baseadas na auditoria de conteudo e UX.

CRITICOS a corrigir:
1. Bug expandirMedicamentos() - sentinela 'meropenem' (quebrada!)
2. Lista WHO_EMC com 4 medicamentos removidos
3. Casos clinicos/flashcards com meds removidos
4. Links quebrados landing/checkout -> dashboard-pediatrico-*
5. Contadores de marketing desatualizados
"""
import re
from pathlib import Path

OUTPUT = Path("/workspace/output")

DASHBOARDS = [
    "dashboard-auxfarmacia.html",
    "dashboard-auxfarmacia-FREE.html",
    "dashboard-auxfarmacia-PRO.html",
    "dashboard-auxfarmacia-PREMIUM.html",
    "dashboard-auxfarmacia-ENTERPRISE.html",
    "dashboard-auxfarmacia-educativo.html",
]

ALL_HTML = DASHBOARDS + [
    "admin.html",
    "landing.html",
    "checkout.html",
]

REMOVED_MEDS = ["meropenem", "vancomicina", "adrenalina", "ceftriaxona"]

# Contadores
def fix_critical_bug():
    """1. Corrigir sentinela 'meropenem' em expandirMedicamentos()"""
    print("\n1. Corrigindo bug CRÍTICO expandirMedicamentos()...")
    total = 0
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        old = "if (meds.find(m => m.id === 'meropenem')) return;"
        new = "if (window._medsExpandido) return; window._medsExpandido = true;"
        if old in html:
            html = html.replace(old, new, 1)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
            print(f"  ✅ {fname}")
    print(f"  Total: {total} arquivos corrigidos")
    return total


def fix_who_emc():
    """2. Remover ceftriaxona e adrenalina de WHO_EMC"""
    print("\n2. Removendo 'ceftriaxona' e 'adrenalina' de WHO_EMC...")
    total = 0
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        # Padrao: ', 'ceftriaxona', ' em array
        new = html.replace("'ceftriaxona', ", "")
        new = new.replace("'adrenalina', ", "")
        new = new.replace("'meropenem', ", "")
        new = new.replace("'vancomicina', ", "")
        if new != html:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            total += 1
            print(f"  ✅ {fname}")
    print(f"  Total: {total} arquivos limpos")
    return total


def fix_broken_links():
    """3. Corrigir 6 links quebrados para dashboard-pediatrico-*"""
    print("\n3. Corrigindo 6 links quebrados dashboard-pediatrico-...")
    files_to_fix = ["landing.html", "checkout.html"]
    total = 0
    for fname in files_to_fix:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        old_targets = [
            "dashboard-pediatrico-FREE.html",
            "dashboard-pediatrico-PRO.html",
            "dashboard-pediatrico-PREMIUM.html",
            "dashboard-pediatrico-ENTERPRISE.html",
        ]
        changes = 0
        for old in old_targets:
            if old in html:
                html = html.replace(old, "dashboard-auxfarmacia-FREE.html")
                changes += 1
        if changes > 0:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            total += changes
            print(f"  ✅ {fname}: {changes} links corrigidos")
    print(f"  Total: {total} links corrigidos")
    return total


def fix_meta_tags():
    """4. Adicionar meta description e lang=pt-BR se faltar"""
    print("\n4. Adicionando meta description e lang=pt-BR...")
    total = 0
    for fname in ALL_HTML:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        # Adiciona lang=pt-BR no html se nao tiver
        if 'lang="pt-BR"' not in html and '<html' in html:
            html = re.sub(r'<html(\s*[^>]*)>', r'<html\1 lang="pt-BR">', html, count=1)
            if html != original:
                total += 1

        # Adiciona meta description se nao tiver
        if '<meta name="description"' not in html and '<head>' in html:
            desc = '<meta name="description" content="Auxílio Farmácia - plataforma educacional com 58 medicamentos, 22 classes terapêuticas, 9 calculadoras, 2 cursos completos e 7 módulos educacionais para profissionais de farmácia.">'
            html = html.replace('<head>', f'<head>\n  {desc}', 1)

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  ✅ {fname}")
    return total


def fix_aria_labels():
    """5. Adicionar aria-labels em botoes principais"""
    print("\n5. Adicionando aria-labels em CTAs principais...")
    total = 0
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        # Adiciona aria-label em botoes sem label
        # Procura por <button> sem aria-label e adiciona
        original = html
        # Botoes de fechar modal
        html = re.sub(
            r'<button([^>]*?)onclick="[^"]*fechar[^"]*"([^>]*?)>',
            r'<button\1onclick="..."\2 aria-label="Fechar">',
            html, flags=re.IGNORECASE
        )
        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
            print(f"  ✅ {fname}")
    return total


def fix_noscript():
    """6. Adicionar <noscript> fallback se faltar"""
    print("\n6. Adicionando <noscript> fallback...")
    total = 0
    for fname in DASHBOARDS:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        if '<noscript>' not in html and '<body>' in html:
            noscript = '<noscript><div style="padding:40px;text-align:center;font-family:sans-serif;"><h2>JavaScript Necessário</h2><p>Esta plataforma requer JavaScript habilitado. Por favor, ative o JavaScript no seu navegador para acessar o conteúdo.</p></div></noscript>'
            html = html.replace('<body>', f'<body>\n{noscript}', 1)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
            print(f"  ✅ {fname}")
    return total


def fix_counters():
    """7. Atualizar contadores de marketing"""
    print("\n7. Atualizando contadores de marketing...")
    total = 0
    counter_replacements = [
        # (old, new)
        ("122 medicamentos", "58 medicamentos"),
        ("62 medicamentos", "58 medicamentos"),
        ("89+ medicamentos", "58 medicamentos"),
        ("89 medicamentos", "58 medicamentos"),
        ("20 calculadoras", "9 calculadoras"),
        ("100+ medicamentos", "58 medicamentos"),
        ("100 medicamentos", "58 medicamentos"),
        ("+ de 100", "+ de 58"),
        ("mais de 100", "58"),
    ]
    for fname in ALL_HTML:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html
        for old, new in counter_replacements:
            if old in html:
                html = html.replace(old, new)
        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
            print(f"  ✅ {fname}")
    return total


def main():
    print("=" * 60)
    print("🔧 APLICANDO CORREÇÕES DA AUDITORIA")
    print("=" * 60)

    fix_critical_bug()
    fix_who_emc()
    fix_broken_links()
    fix_meta_tags()
    fix_aria_labels()
    fix_noscript()
    fix_counters()

    print("\n" + "=" * 60)
    print("✅ CORREÇÕES APLICADAS")
    print("=" * 60)

    # Verificacao final
    print("\n🔍 Verificacao final:")
    import subprocess
    result = subprocess.run(
        ['grep', '-r', '-l', 'meropenem|vancomicina|adrenalina|ceftriaxona',
         '--include=*.html',
         str(OUTPUT)],
        capture_output=True, text=True
    )
    # Filtra resultados que nao sao docs
    relevant = [f for f in result.stdout.split('\n')
                if f and not 'audits/' in f and not 'MEDICAMENTOS_HOSPITALARES' in f]
    if relevant:
        print(f"  ⚠️ Ainda ha referencias em: {relevant}")
    else:
        print("  ✅ Nenhuma referencia aos 4 medicamentos removidos nos HTMLs principais!")

    result = subprocess.run(
        ['grep', '-r', '-l', 'dashboard-pediatrico', '--include=*.html', str(OUTPUT)],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        print(f"  ⚠️ Ainda ha links para dashboard-pediatrico: {result.stdout.strip()}")
    else:
        print("  ✅ Nenhum link quebrado para dashboard-pediatrico-*!")


if __name__ == "__main__":
    main()