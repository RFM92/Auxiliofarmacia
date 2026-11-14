#!/usr/bin/env python3
"""
Script de renomeação em massa: Auxílio Farmácia → Auxílio Farmácia
Troca em TODOS os arquivos do projeto
"""
import os
import re
from pathlib import Path
import sys

# Mapeamento de substituições
# Cuidado com a ordem: Auxílio Farmácia antes de auxfarmacia
SUBSTITUICOES = [
    # Marca principal (visível)
    ("Auxílio Farmácia", "Auxílio Farmácia"),
    ("AUXFARMA", "AUXFARMA"),
    ("auxfarmacia", "auxfarmacia"),

    # LocalStorage keys
    ("auxf_license", "auxf_license"),
    ("auxf_license_cache_at", "auxf_license_cache_at"),
    ("auxf_users", "auxf_users"),
    ("auxf_session", "auxf_session"),
    ("auxf_tema", "auxf_tema"),
    ("auxf_lang", "auxf_lang"),
    ("auxf_onboarding_done", "auxf_onboarding_done"),
    ("auxf_dark_mode", "auxf_dark_mode"),

    # Banco
    ("auxfarmacia.db", "auxfarmacia.db"),
    ("auxfarmacia_v1", "auxfarmacia_v1"),

    # URLs e domínios
    ("auxfarmacia.com.br", "auxfarmacia.com.br"),
    ("auxfarmacia.app", "auxfarmacia.app"),
    ("api.auxfarmacia.com.br", "api.auxfarmacia.com.br"),
    ("www.auxfarmacia.com.br", "www.auxfarmacia.com.br"),

    # Outras variantes
    ("dashboard-auxf", "dashboard-auxf"),
]

# Padrões de arquivos a processar
EXTENSOES = {
    ".html", ".py", ".md", ".yml", ".yaml",
    ".sh", ".css", ".js", ".json",
    ".txt", ".conf", ".env", ".example",
    "Dockerfile", "Makefile"
}

# Arquivos a ignorar
IGNORAR = {
    ".git", "__pycache__", "node_modules", "venv", ".venv",
    "auxfarmacia.db", ".pyc"
}

# Estatísticas
stats = {
    "arquivos_processados": 0,
    "arquivos_modificados": 0,
    "substituicoes_total": 0,
    "por_tipo": {}
}

def deve_processar(arquivo: Path) -> bool:
    """Verifica se o arquivo deve ser processado"""
    # Ignorar paths específicos
    partes = arquivo.parts
    for p in partes:
        if p in IGNORAR:
            return False

    # Verificar extensão
    if arquivo.suffix in EXTENSOES:
        return True
    if arquivo.name in EXTENSOES:
        return True
    return False

def processar_arquivo(arquivo: Path) -> int:
    """Processa um arquivo, retorna número de substituições"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except (UnicodeDecodeError, PermissionError, IsADirectoryError):
        return 0

    conteudo_original = conteudo
    total_subs = 0

    for antigo, novo in SUBSTITUICOES:
        count = conteudo.count(antigo)
        if count > 0:
            conteudo = conteudo.replace(antigo, novo)
            total_subs += count
            stats["por_tipo"][f"{antigo} → {novo}"] = stats["por_tipo"].get(f"{antigo} → {novo}", 0) + count

    if conteudo != conteudo_original:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        stats["arquivos_modificados"] += 1
        print(f"✅ {arquivo.relative_to(Path('/workspace'))} ({total_subs} substituições)")

    stats["arquivos_processados"] += 1
    stats["substituicoes_total"] += total_subs
    return total_subs

def main():
    """Processa todos os arquivos do projeto"""
    workspace = Path("/workspace")

    # Caminhos a processar
    paths_alvo = [
        workspace / "backend",
        workspace / "output",
        workspace / "build",
        workspace / "scripts",
    ]

    # Adiciona arquivos individuais
    for arquivo in [
        workspace / "README.md",
    ]:
        if arquivo.exists():
            stats["arquivos_processados"] += 1

    print("🚀 Iniciando renomeação: Auxílio Farmácia → Auxílio Farmácia")
    print("=" * 60)

    for path_alvo in paths_alvo:
        if not path_alvo.exists():
            continue

        for arquivo in path_alvo.rglob("*"):
            if arquivo.is_file() and deve_processar(arquivo):
                processar_arquivo(arquivo)

    # Relatório
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE RENOMEAÇÃO")
    print("=" * 60)
    print(f"📁 Arquivos processados: {stats['arquivos_processados']}")
    print(f"✏️  Arquivos modificados: {stats['arquivos_modificados']}")
    print(f"🔄 Total de substituições: {stats['substituicoes_total']}")
    print()
    print("Por tipo:")
    for tipo, count in sorted(stats["por_tipo"].items(), key=lambda x: -x[1]):
        print(f"  {tipo}: {count}")

    print("\n✅ Renomeação concluída!")

if __name__ == "__main__":
    main()
