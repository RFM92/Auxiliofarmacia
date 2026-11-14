#!/usr/bin/env python3
"""
Porta para o build FREE as funcoes de UI/Conta que existem no master mas
sumiram do FREE (o drawer chamava activateTabById/scrollToTabs que nao
existiam -> menu lateral nao funcionava).

Extrator: encontra a definicao de cada funcao (function NOME ou const NOME = ...)
e extrai o corpo balanceado.
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
MASTER = OUT / 'dashboard-auxfarmacia.html'
FREE = OUT / 'dashboard-auxfarmacia-FREE.html'

FUNCS = [
    'activateTabById', 'scrollToTabs', 'openSettingsModal', 'closeSettingsModal',
    'switchSettingsTab', 'changePassword', 'forgotPasswordFromAccount',
    'saveProfile', 'exportUserData', 'updateUserStats', 'getCurrentUser',
    'getInitials', 'getUserFromUsers', 'updateAccountDisplay', 'showToast',
]


def extract_function(src, name):
    """Extrai a definicao completa da funcao `name`."""
    # function NAME(...) { ... }
    m = re.search(r'(?:^|\n)\s*(?:async\s+)?function\s+' + re.escape(name) + r'\s*\(', src)
    if m:
        start = m.start() + (1 if src[m.start()] == '\n' else 0)
        i = src.index('{', m.end() - 1)
        depth = 0
        j = i
        in_s = None
        in_tpl = False
        while j < len(src):
            ch = src[j]
            if in_s:
                if ch == '\\':
                    j += 2
                    continue
                if ch == in_s:
                    in_s = None
                j += 1
                continue
            if in_tpl:
                if ch == '\\':
                    j += 2
                    continue
                if ch == '`':
                    in_tpl = False
                j += 1
                continue
            if ch in ('"', "'"):
                in_s = ch
                j += 1
                continue
            if ch == '`':
                in_tpl = True
                j += 1
                continue
            if src.startswith('//', j):
                nl = src.find('\n', j)
                j = len(src) if nl == -1 else nl
                continue
            if src.startswith('/*', j):
                e = src.find('*/', j + 2)
                j = len(src) if e == -1 else e + 2
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return src[start:j + 1]
            j += 1
        return None

    # const/let NAME = function(...) {...}  ou  NAME = (...) => {...}
    m = re.search(r'(?:const|let|var)\s+' + re.escape(name) + r'\s*=\s*(?:async\s*)?(?:function|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)', src)
    if m:
        i = src.index('{', m.end())
        depth = 0
        j = i
        while j < len(src):
            if src[j] == '{':
                depth += 1
            elif src[j] == '}':
                depth -= 1
                if depth == 0:
                    return src[m.start():j + 1]
            j += 1
    return None


def main():
    master = MASTER.read_text(encoding='utf-8')
    free = FREE.read_text(encoding='utf-8')

    extraidos = []
    faltando = []
    for fn in FUNCS:
        if re.search(r'function\s+\*?\s*' + re.escape(fn) + r'\s*\(', free):
            continue
        code = extract_function(master, fn)
        if code:
            # remove tags <script>/</script> que podem estar embutidas no master
            code = re.sub(r'</?script[^>]*>', '', code)
            extraidos.append((fn, code.strip()))
        else:
            faltando.append(fn)

    print(f'Funcoes extraidas do master: {len(extraidos)}')
    for fn, _ in extraidos:
        print(f'  + {fn}')
    if faltando:
        print(f'NAO encontradas no master: {faltando}')

    if not extraidos:
        print('Nada a fazer.')
        return

    bloco = (
        '<script>\n'
        '// ============================================================\n'
        '// PORTADO DO BUILD MASTER - FUNCOES DE UI / CONTA / DRAWER\n'
        '// (build FREE nao possuia estas definicoes)\n'
        '// ============================================================\n'
        + '\n\n'.join(c for _, c in extraidos)
        + '\n</script>\n'
    )

    # insere antes do </body>
    idx = free.rfind('</body>')
    if idx == -1:
        idx = len(free)
    free = free[:idx] + bloco + free[idx:]
    FREE.write_text(free, encoding='utf-8')
    print(f'\nInserido no FREE: {len(bloco)} bytes')


if __name__ == '__main__':
    main()
