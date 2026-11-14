#!/usr/bin/env python3
"""
Remove blocos <script> duplicados do API CLIENT.

Cada copia declara `const API_BASE` e `const API` no escopo global -> a 2a e 3a
lancam "Identifier 'API_BASE' has already been declared" e nunca executam.

Correcao: mantem a copia MAIOR (superset funcional, inclui PAYMENTS) e remove
as demais. Antes, corrige o payload divergente de activateLicense para o
formato do backend (LicenseActivate: key + fingerprint).
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
WRONG = "body: { license_key: key, device_fingerprint: deviceFingerprint },"
RIGHT = "body: { key, fingerprint: deviceFingerprint },"

for p in sorted(OUT.glob('dashboard-auxfarmacia*.html')):
    c = p.read_text(encoding='utf-8')
    n_fix = c.count(WRONG)
    if n_fix:
        c = c.replace(WRONG, RIGHT)

    blocks = list(re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', c, re.S | re.I))
    cands = [(i, b) for i, b in enumerate(blocks)
             if 'const API_BASE' in b.group(1)
             and re.search(r'(?m)^const API\s*=\s*\{', b.group(1))]
    if len(cands) < 2:
        p.write_text(c, encoding='utf-8')
        print(f'{p.name}: {len(cands)} bloco(s) API client (payload_corrigido={n_fix})')
        continue

    # mantem o MAIOR
    cands.sort(key=lambda t: len(t[1].group(1)))
    remover = [cands[0][1]]
    for i, b in cands[1:-1]:
        remover.append(b)
    for b in sorted(remover, key=lambda b: b.start(), reverse=True):
        c = c[:b.start()] + c[b.end():]
    c = re.sub(r'\n{4,}', '\n\n\n', c)
    p.write_text(c, encoding='utf-8')
    print(f'{p.name}: {len(remover)} copia(s) reduzida(s) do API client removida(s) '
          f'(mantido o com PAYMENTS, {len(cands[-1][1].group(1))}b) payload_corrigido={n_fix}')
