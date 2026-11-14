#!/usr/bin/env python3
"""
Remove elementos sticky/fixed do dashboard para que a pagina inteira
faca scroll natural. Mantem apenas modais/toasts como fixed (esses
precisam ficar sobre o conteudo).
"""
import re
from pathlib import Path

OUTPUT = Path("/workspace/output")
ALL_HTML = [
    "dashboard-auxfarmacia.html",
    "dashboard-auxfarmacia-FREE.html",
    "dashboard-auxfarmacia-PRO.html",
    "dashboard-auxfarmacia-PREMIUM.html",
    "dashboard-auxfarmacia-ENTERPRISE.html",
    "dashboard-auxfarmacia-educativo.html",
]

# CSS para a topbar: relative em vez de sticky
OLD_TOPBAR = """/* ===== TOPBAR PREMIUM (GLASSMORPHISM) ===== */
.topbar {
  background: var(--panel-glass);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 18px clamp(16px, 3vw, 34px);
}"""

NEW_TOPBAR = """/* ===== TOPBAR PREMIUM (SCROLL NORMAL) ===== */
.topbar {
  background: var(--panel-glass);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: 50;
  padding: 18px clamp(16px, 3vw, 34px);
}"""

# Remove o sticky do aviso medico tambem
OLD_WARNING = """  .medical-warning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-top: 3px solid #f59e0b;
    border-bottom: 1px solid #fbbf24;
    padding: 8px 24px;
    position: relative;
    z-index: 100;
    font-size: 12px;"""

NEW_WARNING = """  .medical-warning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-top: 3px solid #f59e0b;
    border-bottom: 1px solid #fbbf24;
    padding: 8px 24px;
    position: relative;
    z-index: 40;
    font-size: 12px;"""


def fix_full_scroll():
    total = 0
    for fname in ALL_HTML:
        path = OUTPUT / fname
        if not path.exists():
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        original = html

        # 1. Topbar: sticky -> relative
        html = html.replace(OLD_TOPBAR, NEW_TOPBAR)

        # 2. Aviso medico: relative, z-index menor
        html = html.replace(OLD_WARNING, NEW_WARNING)

        # 3. Remove sticky do .controls (existem alguns)
        html = re.sub(
            r'\.controls\s*\{\s*position:\s*sticky[^}]*\}',
            '.controls { position: relative; display: grid; gap: 12px; padding: 14px; }',
            html
        )

        # 4. Remove sticky de outros elementos
        html = re.sub(
            r'position:\s*sticky[^;]*;',
            'position: relative;',
            html
        )

        # 5. Ajusta .app para nao travar altura
        html = html.replace(
            '.app { min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }',
            '.app { min-height: 100vh; display: flex; flex-direction: column; }'
        )

        # 6. Garante scroll natural do body
        html = html.replace(
            'html, body { height: 100%; }',
            'html, body { min-height: 100%; }'
        )

        # 7. Remove overflow:hidden do body se tiver
        html = re.sub(
            r'body\s*\{[^}]*overflow:\s*hidden[^}]*\}',
            lambda m: m.group(0).replace('overflow: hidden;', 'overflow: auto;'),
            html
        )

        if html != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
            print(f"✅ {fname}")
    print(f"\nTotal: {total} arquivos")
    return total


if __name__ == "__main__":
    fix_full_scroll()