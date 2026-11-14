#!/usr/bin/env python3
"""
PIPELINE DE REPARO DETERMINISTICO - Auxilio Farmacia

Restaura os 6 dashboards a partir de backups integros e aplica, na ordem
correta, todas as correcoes de bug. Cada etapa e validada.

Uso: python3 repair_pipeline.py
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

OUT = Path('/workspace/output')
SCRIPTS = Path('/workspace/scripts')

# backups integros (tags <script> balanceadas)
BACKUPS = {
    'dashboard-auxfarmacia.html': '/tmp/backup-master.html',
    'dashboard-auxfarmacia-PRO.html': '/tmp/backup-pro.html',
    'dashboard-auxfarmacia-FREE.html': '/tmp/bk-free2.html',
    'dashboard-auxfarmacia-PREMIUM.html': None,   # deriva do PRO
    'dashboard-auxfarmacia-ENTERPRISE.html': None,
    'dashboard-auxfarmacia-educativo.html': '/tmp/bk-e3.html',
}

log = []


def step(msg):
    print(f'  -> {msg}')
    log.append(msg)


def restore():
    """Restaura backups integros. PREMIUM/ENTERPRISE derivam do PRO."""
    for name, bk in BACKUPS.items():
        if bk:
            shutil.copy(bk, OUT / name)
            step(f'restore {name} <- {Path(bk).name}')
    # derivar PREMIUM e ENTERPRISE a partir do PRO (mesma base, features por flag)
    pro = (OUT / 'dashboard-auxfarmacia-PRO.html').read_text(encoding='utf-8')
    for name in ['dashboard-auxfarmacia-PREMIUM.html', 'dashboard-auxfarmacia-ENTERPRISE.html']:
        (OUT / name).write_text(pro, encoding='utf-8')
        step(f'derivou {name} a partir do PRO')


def sanitize_script_tags():
    """
    Sanitiza tags <script> com regras baseadas no padrao real do arquivo:
      A) <script> seguido de outro <script> (so whitespace entre) -> remove o 1o
      B) </script> seguido de outro </script> -> remove o 1o
      C) </script> precedido por outro </script> -> remove o 1o
    """
    import re as _re
    for p in sorted(OUT.glob('dashboard-auxfarmacia*.html')):
        c = p.read_text(encoding='utf-8')
        antes = c
        # A) <script> vazio/duplicado
        c = _re.sub(r'<script[^>]*>[ \t]*\n(?:[ \t]*\n)*(?=[ \t]*<script)', '', c)
        # B) </script> duplicado (o primeiro e orfao)
        c = _re.sub(r'</script>[ \t]*\n(?=[ \t]*</script>)', '', c)
        # B2) <script> inline: bloco <script>..</script> cujo CONTEUDO e indentado
        #     (dentro de uma funcao). Blocos legitimos comecam na coluna 0.
        c = _re.sub(r'(?m)^[ \t]*<script[^>]*>[ \t]*\n((?:[ \t]{2,}[^\n]*\n)+?)[ \t]*</script>[ \t]*\n', r'\1', c)

        # C) remove </script> orfaos (fechamento sem abertura correspondente)
        depth = 0
        orfaos = []
        for _m in _re.finditer(r'<script\b[^>]*>|</script>', c):
            if _m.group(0).lower().startswith('<script'):
                depth += 1
            else:
                depth -= 1
                if depth < 0:
                    orfaos.append(_m.start())
                    depth = 0
        for _o in sorted(orfaos, reverse=True):
            c = c[:_o] + c[_o + len('</script>'):]
        if c != antes:
            p.write_text(c, encoding='utf-8')
        a = len(_re.findall(r'<script', c)); f = len(_re.findall(r'</script>', c))
        step(f'{p.name}: tags <script>={a} </script>={f} {"OK" if a==f else "DESBALANCEADO"}')


def run(script, *args):
    r = subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                       capture_output=True, text=True)
    for line in (r.stdout or '').strip().split('\n')[:8]:
        if line.strip():
            print('     ' + line)
    if r.returncode != 0:
        print(f'     !! {script} retornou {r.returncode}: {(r.stderr or "")[:200]}')


def main():
    print('=== 1. RESTAURAR BACKUPS INTEGROS ===')
    restore()

    print('\n=== 2. BLOQUE CORROMPIDO ===')
    run('fix_corrupted_script_block.py')

    print('\n=== 3. SANITIZAR TAGS <script> ===')
    sanitize_script_tags()

    print('\n=== 4. JS SOLTO (reempacotar) ===')
    run('fix_loose_js.py')

    print('\n=== 4b. REMOVER <script> INLINE (pos fix_loose_js) ===')
    run('strip_inline_scripts.py')

    print('\n=== 5. REESCREVER ARRAY CURSOS ===')
    run('rewrite_cursos.py')

    print('\n=== 5b. PRO_CLASSES ([] faltando) ===')
    run('fix_pro_classes.py')

    print('\n=== 6. CHAMADAS DE FUNCOES INEXISTENTES ===')
    run('fix_undefined_calls.py')

    print('\n=== 7. SCRIPT DUPLICADO (API client) ===')
    run('remove_duplicate_scripts.py')

    print('\n=== 8. FIXES RESIDUAIS ===')
    run('fix_residual.py')

    print('\n=== 8b. INJETAR ARRAY MEDS INTEGRO ===')
    run('inject_meds_array.py')

    print('\n=== 9. PORTAR FUNCOES UI AUSENTES (FREE) ===')
    run('port_missing_ui_functions.py')

    print('\n=== 10. VALIDACAO JS ===')
    r = subprocess.run([sys.executable, '/tmp/jscheck_all.py'], capture_output=True, text=True)
    print('     ' + (r.stdout or '').strip().split('\n')[-1])


if __name__ == '__main__':
    main()
