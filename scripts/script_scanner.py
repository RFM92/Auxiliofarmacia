#!/usr/bin/env python3
"""
Scanner de tags <script> stateful.

Comportamento real do HTMLParser:
  - FORA de script: <script> abre, </script> e orfao (remover)
  - DENTRO de script: <script> e LITERAL no codigo JS (remover a tag E o
    </script> correspondente, senao o script fecha prematuramente)
"""
import re

TAG = re.compile(r'<script\b[^>]*>|</script>', re.I)


def scan(c):
    """Retorna (c_sanitizado, n_inline_removidos, n_orfaos_removidos)."""
    out = []
    i = 0
    dentro = False
    inline = 0
    orfaos = 0
    # quando True, o proximo </script> deve ser removido (fecha de um inline)
    pendente_remover = False
    while i < len(c):
        if not dentro:
            m = TAG.search(c, i)
            if not m:
                out.append(c[i:])
                break
            out.append(c[i:m.start()])
            t = m.group(0)
            if t.lower().startswith('</script'):
                orfaos += 1          # orfao: nao emite nada
            else:
                dentro = True
                out.append(t)
            i = m.end()
        else:
            m = TAG.search(c, i)
            if not m:
                out.append(c[i:])
                break
            out.append(c[i:m.start()])
            t = m.group(0)
            if t.lower().startswith('</script'):
                if pendente_remover:
                    pendente_remover = False   # fecha do inline: remove
                else:
                    dentro = False
                    out.append('</script>')
            else:
                # tag <script> literal dentro do codigo JS
                inline += 1
                pendente_remover = True
            i = m.end()
    return ''.join(out), inline, orfaos


def count_tags(c):
    """Conta tags de nivel de bloco (nao literais em JS)."""
    abre = fecha = 0
    dentro = False
    for m in TAG.finditer(c):
        if m.group(0).lower().startswith('<script'):
            if not dentro:
                abre += 1
                dentro = True
        else:
            if dentro:
                fecha += 1
                dentro = False
    return abre, fecha
