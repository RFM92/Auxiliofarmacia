import re, os, sys
from pathlib import Path
f = sys.argv[1]
c = Path(f).read_text(encoding='utf-8', errors='replace')
for i, m in enumerate(re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', c, re.S|re.I)):
    code = m.group(1)
    if len(code.strip()) < 10: continue
    p = Path('/tmp/_one.js'); p.write_text(code, encoding='utf-8')
    r = os.popen(f'node --check {p} 2>&1').read().strip()
    if r:
        print(r[:350]); ls = code.split('\n')
        for k in range(0, min(len(ls), 10)): print(f'  {k+1}: {ls[k][:100]}')
        break
