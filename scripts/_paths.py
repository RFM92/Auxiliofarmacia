#!/usr/bin/env python3
"""
Caminhos do repositorio, independentes do ambiente.

Resolves a raiz do repo a partir da localizacao do proprio script
(assim funciona no sandbox, no GitHub Actions e na maquina do usuario).

    scripts/_paths.py  ->  raiz = dirname(dirname(__file__))
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# site/ (frontend) e api/ (backend) --detection automatica
SITE = RAIZ / 'site'
API = RAIZ / 'api'
OUTPUT = SITE              # onde os HTML vivem no repo
BACKEND = API
DOCS = RAIZ / 'docs'
AUDITORIA = DOCS


def garantir_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def html_files():
    """Lista os HTML de producao (ignora debug/test)."""
    import re
    if not SITE.exists():
        return []
    ignorados = re.compile(
        r'^(debug|test-|diag-|check-|show-meds|force-meds|load\.html|'
        r'dashboard-FREE|dashboard-free-v2|VISUALIZAR)'
    )
    return sorted(
        f for f in SITE.glob('*.html')
        if not ignorados.match(f.name)
    )
