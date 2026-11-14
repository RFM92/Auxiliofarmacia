#!/usr/bin/env python3
"""
CORRECAO v2: Reempacota blocos de JavaScript soltos usando scanner de
balanceamento de chaves (nao heuristicas de linha).
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
FILES = [
    'dashboard-auxfarmacia.html',
    'dashboard-auxfarmacia-FREE.html',
    'dashboard-auxfarmacia-PRO.html',
    'dashboard-auxfarmacia-PREMIUM.html',
    'dashboard-auxfarmacia-ENTERPRISE.html',
    'dashboard-auxfarmacia-educativo.html',
]

JS_START = re.compile(r'^\s*(?:function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=|var\s+\w+\s*=|window\.\w+\s*=|//\s*=+)')


def scan_end(src, start):
    """Retorna o fim do bloco JS balanceado que comeca em `start`."""
    depth = 0
    i = start
    n = len(src)
    in_s = None
    in_tpl = False
    started = False
    while i < n:
        ch = src[i]
        if in_s:
            if ch == '\\':
                i += 2
                continue
            if ch == in_s:
                in_s = None
            i += 1
            continue
        if in_tpl:
            if ch == '\\':
                i += 2
                continue
            if ch == '`':
                in_tpl = False
            i += 1
            continue
        if ch in ('"', "'"):
            in_s = ch
            i += 1
            continue
        if ch == '`':
            in_tpl = True
            i += 1
            continue
        if src.startswith('//', i):
            j = src.find('\n', i)
            i = n if j == -1 else j
            continue
        if src.startswith('/*', i):
            j = src.find('*/', i + 2)
            i = n if j == -1 else j + 2
            continue
        if ch == '{':
            depth += 1
            started = True
        elif ch == '}':
            depth -= 1
            if started and depth == 0:
                # consome ate o fim da linha
                j = src.find('\n', i)
                return (n if j == -1 else j + 1)
        elif ch == ';' and not started:
            # statement simples (ex: setTimeout(...);)
            j = src.find('\n', i)
            end = n if j == -1 else j + 1
            # verifica se a proxima linha ainda e JS
            nxt = src[end:end + 400]
            m = re.match(r'\s*(?:function\s|const\s|let\s|var\s|window\.|//\s*=)', nxt)
            if not m:
                return end
        i += 1
    return n


def find_loose_js(c):
    parts = re.split(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)', c, flags=re.S | re.I)
    regions = []
    offset = 0
    for seg in parts:
        if seg.lower().startswith('<script') or seg.lower().startswith('<style'):
            offset += len(seg)
            continue
        lines = seg.split('\n')
        idx = [i for i, l in enumerate(lines) if JS_START.match(l)]
        # agrupa indices consecutivos (com folga de 2 linhas)
        groups = []
        for i in idx:
            if groups and i - groups[-1][-1] <= 4:
                groups[-1].append(i)
            else:
                groups.append([i])
        for g in groups:
            if len(g) < 2:
                continue
            s_off = len('\n'.join(lines[:g[0]]))
            e_off = len('\n'.join(lines[:g[-1] + 1]))
            # recua ate o inicio do bloco de codigo (inclui comentario de cabecalho)
            start = s_off
            pre = lines[:g[0]]
            k = g[0] - 1
            while k >= 0 and (pre[k].strip().startswith('//') or pre[k].strip().startswith('/*') or pre[k].strip().startswith('*')):
                k -= 1
            start = len('\n'.join(lines[:k + 1]))
            # avanca ate o fim balanceado
            abs_start = offset + start
            end_abs = scan_end(c, abs_start)
            regions.append((abs_start, end_abs))
        offset += len(seg)
    return regions


def main():
    for name in FILES:
        p = OUT / name
        c = p.read_text(encoding='utf-8')
        regions = find_loose_js(c)
        if not regions:
            print(f'{name}: sem JS solto')
            continue
        # merge regioes sobrepostas/adjacentes
        regions.sort()
        merged = []
        for s, e in regions:
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        for start, end in reversed(merged):
            body = c[start:end].strip('\n')
            if not body.strip():
                continue
            c = c[:start] + '\n<script>\n' + body + '\n</script>\n' + c[end:]
        p.write_text(c, encoding='utf-8')
        print(f'{name}: {len(merged)} regiao(oes) reempacotada(s)')


if __name__ == '__main__':
    main()
