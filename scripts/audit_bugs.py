#!/usr/bin/env python3
"""
Auditor de bugs - Auxilio Farmacia
Analise estatica de HTML/JS: sintaxe, IDs duplicados, refs quebradas,
handlers sem funcao, chaves de storage inconsistentes.
"""
import re, os, json, glob, sys
from pathlib import Path
from collections import defaultdict

OUT = Path('/workspace/output')
BACKEND = Path('/workspace/backend')

BUGS = []


def add(sev, file, line, cat, msg):
    BUGS.append({'sev': sev, 'file': file, 'line': line, 'cat': cat, 'msg': msg})


def extract_scripts(html):
    """Retorna [(offset_line, codigo_js)] dos blocos <script> sem src=."""
    out = []
    for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S | re.I):
        code = m.group(1)
        line = html[:m.start()].count('\n') + 1
        out.append((line, code))
    return out


def strip_js_comments(code):
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)
    code = re.sub(r'(?m)^\s*//.*$', '', code)
    return code


def audit_html(path):
    name = os.path.basename(path)
    raw = Path(path).read_text(encoding='utf-8', errors='replace')
    html = raw

    # --- 1. IDs duplicados ---
    ids = re.findall(r'\bid="([^"]+)"', html)
    dup = {i: c for i, c in defaultdict(int, {k: ids.count(k) for k in ids}).items() if c > 1}
    for d, c in dup.items():
        add('MEDIA', name, 0, 'ID_DUPLICADO', f'id="{d}" aparece {c}x (getElementById pega o 1o)')

    # --- 2. Handlers inline sem funcao definida ---
    handlers = set()
    for m in re.finditer(r'on(?:click|submit|change|input|load|error|keyup|keydown|mouseover|focus|blur)="([^"]+)"', html):
        for call in re.findall(r'([A-Za-z_$][\w$]*)\s*\(', m.group(1)):
            handlers.add(call)
    all_js = '\n'.join(c for _, c in extract_scripts(html))
    all_js_clean = strip_js_comments(all_js)
    defined = set(re.findall(r'function\s+([A-Za-z_$][\w$]*)', all_js_clean))
    defined |= set(re.findall(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function|\()', all_js_clean))
    defined |= set(re.findall(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?[A-Za-z_$][\w$]*\s*=>', all_js_clean))
    defined |= set(re.findall(r'window\.([A-Za-z_$][\w$]*)\s*=', all_js_clean))
    for h in sorted(handlers):
        if h in ('event', 'this', 'return', 'if', 'for', 'while', 'function'):
            continue
        if h not in defined and h not in dir(__builtins__):
            if h not in ('alert', 'confirm', 'prompt', 'location', 'console', 'Math', 'JSON', 'Date', 'parseInt', 'parseFloat', 'String', 'Number', 'Boolean', 'Array', 'Object', 'setTimeout', 'setInterval', 'fetch', 'localStorage', 'sessionStorage', 'encodeURIComponent', 'decodeURIComponent', 'isNaN', 'scrollTo', 'open', 'close', 'print', 'Error', 'RegExp', 'Map', 'Set', 'URLSearchParams'):
                add('ALTA', name, 0, 'FUNCAO_NAO_DEFINIDA', f'handler inline chama {h}() que nao existe no arquivo')

    # --- 3. getElementById sem elemento ---
    refd = set(re.findall(r'getElementById\(\s*[\'"]([^\'"]+)[\'"]', all_js_clean))
    for r in refd:
        if f'id="{r}"' not in html:
            add('MEDIA', name, 0, 'ID_NAO_EXISTE', f'getElementById("{r}") -> elemento nao existe no HTML')

    # --- 4. querySelector com seletor de ID que nao existe ---
    for sel in set(re.findall(r'querySelector(?:All)?\(\s*[\'"]#([A-Za-z0-9_-]+)[\'"]', all_js_clean)):
        if f'id="{sel}"' not in html:
            add('MEDIA', name, 0, 'SELECTOR_ID_NAO_EXISTE', f'querySelector("#{sel}") -> nao existe')

    # --- 5. querySelector de classe (amostra) ---
    for sel in set(re.findall(r'querySelector(?:All)?\(\s*[\'"]\.([A-Za-z0-9_-]+)[\'"]', all_js_clean)):
        if f'class="{sel}' not in html and f' {sel}"' not in html and f'{sel} ' not in html:
            add('BAIXA', name, 0, 'CLASSE_NAO_EXISTE', f'querySelector(".{sel}") -> classe nao encontrada no HTML')

    # --- 6. Links internos ---
    for m in re.finditer(r'href="([^"]*)"', html):
        l = m.group(1)
        if not l or l.startswith(('http', 'mailto:', 'tel:', 'javascript:', 'data:', '#')):
            continue
        if '${' in l or l.startswith('/'):
            continue
        base = l.split('#')[0].split('?')[0]
        if base and not (OUT / base).exists():
            add('ALTA', name, html[:m.start()].count('\n') + 1, 'LINK_QUEBRADO', f'href="{l}" -> arquivo inexistente')

    # --- 7. Anchors ---
    for m in re.finditer(r'href="([^"]*#[^"]+)"', html):
        l = m.group(1)
        if l.startswith(('http', 'data:', 'javascript:')) or '${' in l:
            continue
        base, anc = l.split('#', 1)
        tgt = OUT / base if base else Path(path)
        if not tgt.exists():
            continue
        tc = tgt.read_text(encoding='utf-8', errors='replace')
        if f'id="{anc}"' not in tc and f"id='{anc}'" not in tc:
            add('MEDIA', name, html[:m.start()].count('\n') + 1, 'ANCHOR_QUEBRADO', f'href="{l}" -> id inexistente')

    # --- 8. img sem alt ---
    for m in re.finditer(r'<img(?![^>]*\balt=)[^>]*>', html, re.I):
        add('BAIXA', name, html[:m.start()].count('\n') + 1, 'IMG_SEM_ALT', m.group(0)[:90])

    # --- 9. buttons sem type dentro de form (submit acidental) ---
    for m in re.finditer(r'<form[^>]*>(.*?)</form>', html, re.S | re.I):
        form_txt = m.group(1)
        for b in re.finditer(r'<button(?![^>]*\btype=)[^>]*>', form_txt, re.I):
            add('BAIXA', name, 0, 'BUTTON_SEM_TYPE', 'button sem type dentro de form = submit acidental')

    # --- 10. Label sem for / input sem id ---
    labels = re.findall(r'<label(?![^>]*\bfor=)[^>]*>([^<]{0,40})</label>', html, re.I)
    if labels:
        add('BAIXA', name, 0, 'LABEL_SEM_FOR', f'{len(labels)} label(s) sem for=')

    # --- 11. comentario nao fechado / TODO ---
    for m in re.finditer(r'<!--(?!.*?-->).*', html, re.S):
        if m.group(0).count('<!--') > m.group(0).count('-->'):
            add('ALTA', name, html[:m.start()].count('\n') + 1, 'COMENTARIO_NAO_FECHADO', 'HTML comment nao fechado')

    # --- 12. TODO/FIXME/HACK ---
    for m in re.finditer(r'(TODO|FIXME|HACK|XXX|BUG:)', html, re.I):
        ln = html[:m.start()].count('\n') + 1
        ctx = html[max(0, m.start() - 40):m.start() + 60].replace('\n', ' ')
        add('BAIXA', name, ln, 'TODO_OURO', ctx[:100])

    # --- 13. localStorage keys usadas ---
    for m in re.finditer(r'localStorage\.(?:getItem|setItem|removeItem)\(\s*[\'"]([^\'"]+)[\'"]', all_js_clean):
        pass  # cross-file checked later

    return html, all_js_clean, ids


def cross_file_checks(files_data):
    """Verifica chaves de localStorage consistentes entre paginas."""
    keys_by_file = defaultdict(set)
    for name, js, _ in files_data:
        for m in re.finditer(r'localStorage\.(?:getItem|setItem|removeItem)\(\s*[\'"]([^\'"]+)[\'"]', js):
            keys_by_file[name].add(m.group(1))

    all_keys = set()
    for v in keys_by_file.values():
        all_keys |= v

    # chaves de sessao/autenticacao usadas por login.html
    login_keys = keys_by_file.get('login.html', set())
    for name, js, _ in files_data:
        if name == 'login.html':
            continue
        k = keys_by_file[name]
        # procura chaves de sessao no arquivo de login e compara
        for lk in login_keys:
            if any(s in lk for s in ('session', 'users', 'user')):
                if not any(s in ' '.join(k) for s in ('session', 'users', 'user')):
                    add('ALTA', name, 0, 'STORAGE_DIVERGENTE',
                        f'login.html usa "{lk}" mas {name} nao referencia nenhuma chave de sessao/usuario')

    # Finds: chaves escritas em um arquivo e nunca lidas em outro
    written = defaultdict(set)
    for name, js, _ in files_data:
        for m in re.finditer(r'localStorage\.setItem\(\s*[\'"]([^\'"]+)[\'"]', js):
            written[m.group(1)].add(name)

    for key, writers in written.items():
        readers = set()
        for name, js, _ in files_data:
            if re.search(r'localStorage\.getItem\(\s*[\'"]' + re.escape(key) + r'[\'"]', js):
                readers.add(name)
        if not readers and writers:
            add('BAIXA', name, 0, 'STORAGE_SEM_LEITOR', f'chave "{key}" escrita em {sorted(writers)} mas nunca lida')


def main():
    files = sorted(glob.glob(str(OUT / '*.html')))
    files_data = []
    for f in files:
        html, js, ids = audit_html(f)
        files_data.append((os.path.basename(f), js, ids))

    cross_file_checks(files_data)

    # ---- sintaxe JS via node ----
    js_errors = []
    tmp = Path('/tmp/jscheck')
    tmp.mkdir(exist_ok=True)
    for f in files:
        raw = Path(f).read_text(encoding='utf-8', errors='replace')
        for i, (line, code) in enumerate(extract_scripts(raw)):
            if len(code.strip()) < 10:
                continue
            p = tmp / f'{Path(f).stem}_{i}.js'
            p.write_text(code, encoding='utf-8')
            r = os.popen(f'node --check "{p}" 2>&1').read().strip()
            if r:
                js_errors.append((os.path.basename(f), line, r[:400]))
    for name, line, err in js_errors:
        add('CRITICA', name, line, 'ERRO_SINTAXE_JS', err.replace('\n', ' | ')[:300])

    # ---- dedupe ----
    seen = set()
    uniq = []
    for b in BUGS:
        k = (b['cat'], b['file'], b['msg'][:120])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(b)

    order = {'CRITICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAIXA': 3}
    uniq.sort(key=lambda b: (order[b['sev']], b['file'], b['cat']))

    by_cat = defaultdict(list)
    for b in uniq:
        by_cat[b['cat']].append(b)

    print('=' * 70)
    print('RELATORIO DE BUGS - ANALISE ESTATICA')
    print('=' * 70)
    print(f'Arquivos auditados: {len(files)}')
    print(f'Bugs encontrados: {len(uniq)}')
    print()
    sev_count = defaultdict(int)
    for b in uniq:
        sev_count[b['sev']] += 1
    for s in ['CRITICA', 'ALTA', 'MEDIA', 'BAIXA']:
        print(f'  {s:9s} {sev_count[s]}')
    print()

    for cat in sorted(by_cat, key=lambda c: -len(by_cat[c])):
        items = by_cat[cat]
        print('-' * 70)
        print(f'[{cat}] - {len(items)} ocorrencia(s)')
        for b in items[:60]:
            loc = f"{b['file']}:{b['line']}" if b['line'] else b['file']
            print(f"  {b['sev']:8s} {loc:52s} {b['msg'][:90]}")
        if len(items) > 60:
            print(f'  ... e mais {len(items)-60}')
        print()

    Path('/workspace/avaliacao/07-documentacao/BUGS_AUDITORIA_ESTATICA.json').write_text(
        json.dumps(uniq, ensure_ascii=False, indent=2), encoding='utf-8')
    print('JSON salvo em avaliacao/07-documentacao/BUGS_AUDITORIA_ESTATICA.json')


if __name__ == '__main__':
    main()
