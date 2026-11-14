#!/usr/bin/env python3
"""
Setup do gateway de pagamento (PIX + Cartao) para producao.

Uso:
  python3 scripts/setup_payments.py --check          # verifica o estado
  python3 scripts/setup_payments.py --asaas KEY      # grava a chave do Asaas
  python3 scripts/setup_payments.env --stripe KEY SECRET [PRICE_PRO] [PRICE_PREM]

Variaveis de ambiente suportadas pelo backend:
  ASAAS_API_KEY         chave de producao/sandbox do Asaas (PIX, Boleto, Cartao)
  ASAAS_ENVIRONMENT     'sandbox' | 'production'
  ASAAS_WEBHOOK_TOKEN   token do webhook (ja vem preenchido no .env)
  STRIPE_SECRET_KEY     chave secreta do Stripe
  STRIPE_WEBHOOK_SECRET segredo do webhook do Stripe
"""
import argparse
import os
import re
import sys
import urllib.request
import json
from pathlib import Path

ENV_PATH = Path('/workspace/backend/.env')
EXAMPLE = Path('/workspace/backend/.env.example')


def ler_env():
    dados = {}
    if ENV_PATH.exists():
        for linha in ENV_PATH.read_text(encoding='utf-8').split('\n'):
            if '=' in linha and not linha.strip().startswith('#'):
                k, v = linha.split('=', 1)
                dados[k.strip()] = v.strip()
    return dados


def gravar(chaves):
    """Atualiza o .env preservando as demais linhas."""
    if not ENV_PATH.exists():
        ENV_PATH.write_text('', encoding='utf-8')
    texto = ENV_PATH.read_text(encoding='utf-8')
    for k, v in chaves.items():
        linha = f'{k}={v}'
        padrao = re.compile(rf'^{re.escape(k)}=.*$', re.M)
        if padrao.search(texto):
            texto = padrao.sub(linha, texto)
        else:
            texto = texto.rstrip('\n') + f'\n{linha}\n'
    ENV_PATH.write_text(texto, encoding='utf-8')
    try:
        os.chmod(ENV_PATH, 0o600)
    except Exception:
        pass


def testar_asaas(chave, ambiente='production'):
    """Chama a API do Asaas para validar a chave."""
    base = 'https://api.asaas.com/v3' if ambiente == 'production' else 'https://api-sandbox.asaas.com/v3'
    req = urllib.request.Request(f'{base}/payments?limit=1')
    req.add_header('access_token', chave)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return True, f'API respondeu {r.status}'
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return False, f'chave rejeitada (HTTP {e.code})'
        return False, f'HTTP {e.code}: {e.read()[:120].decode("utf-8", "ignore")}'
    except Exception as e:
        return False, f'erro de rede: {e}'


def testar_stripe(chave):
    if not chave:
        return False, 'vazio'
    try:
        import stripe
        stripe.api_key = chave
        stripe.PaymentIntent.list(limit=1)
        return True, 'API respondeu'
    except Exception as e:
        msg = str(e)
        if 'Invalid API Key' in msg or 'api_key_invalid' in msg:
            return False, 'chave invalida'
        return False, msg[:140]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--asaas', metavar='CHAVE')
    ap.add_argument('--stripe', metavar='CHAVE')
    ap.add_argument('--stripe-secret', metavar='SEGREDO')
    ap.add_argument('--prod', action='store_true', help='usar ambiente de producao do Asaas')
    args = ap.parse_args()

    dados = ler_env()

    if args.asaas:
        gravar({'ASAAS_API_KEY': args.asaas,
                'ASAAS_ENVIRONMENT': 'production' if args.prod else 'sandbox'})
        print(f'✅ ASAAS_API_KEY gravada no .env (modo {dados.get("ASAAS_ENVIRONMENT", "sandbox")})')
        return

    if args.stripe:
        chaves = {'STRIPE_SECRET_KEY': args.stripe}
        if args.stripe_secret:
            chaves['STRIPE_WEBHOOK_SECRET'] = args.stripe_secret
        gravar(chaves)
        print('✅ STRIPE_SECRET_KEY gravada no .env')
        return

    # ---- --check ----
    print('=' * 66)
    print('ESTADO DO GATEWAY DE PAGAMENTO (PIX + CARTAO)')
    print('=' * 66)

    asaas_key = dados.get('ASAAS_API_KEY', '')
    asaas_ok = bool(asaas_key) and 'REPLACE' not in asaas_key.upper() and 'invalid' not in asaas_key.lower()
    stripe_key = dados.get('STRIPE_SECRET_KEY', '')
    stripe_ok = bool(stripe_key) and 'REPLACE' not in stripe_key.upper() and 'invalid' not in stripe_key.lower()
    env = dados.get('ASAAS_ENVIRONMENT', 'sandbox')
    webhook_asaas = bool(dados.get('ASAAS_WEBHOOK_TOKEN', ''))
    webhook_stripe = bool(dados.get('STRIPE_WEBHOOK_SECRET', ''))

    print(f'\nASAAS  (PIX + Boleto + Cartao)')
    print(f'  ASAAS_API_KEY        : {"CONFIGURADA" if asaas_ok else "VAZIA"}')
    print(f'  ASAAS_ENVIRONMENT    : {env}')
    print(f'  ASAAS_WEBHOOK_TOKEN  : {"OK" if webhook_asaas else "VAZIO"}')
    print(f'  Stripe  (PIX + Cartao)')
    print(f'  STRIPE_SECRET_KEY    : {"CONFIGURADA" if stripe_ok else "VAZIA"}')
    print(f'  STRIPE_WEBHOOK_SECRET: {"OK" if webhook_stripe else "VAZIO"}')

    if asaas_ok:
        ok, msg = testar_asaas(asaas_key, env)
        print(f'\n  Teste de conexao com o Asaas: {"OK - " if ok else "FALHOU - "}{msg}')
    if stripe_ok:
        ok, msg = testar_stripe(stripe_key)
        print(f'  Teste de conexao com o Stripe: {"OK - " if ok else "FALHOU - "}{msg}')

    print('\n' + '-' * 66)
    conexao_ok = False
    if asaas_ok:
        ok, msg = testar_asaas(asaas_key, env)
        conexao_ok = ok
        if not ok:
            print(f'  CHAVE ASAAS INVALIDA: {msg}')
            print('  Os pagamentos continuam em MODO DEMO (sem cobranca real).')
    if stripe_ok:
        ok, msg = testar_stripe(stripe_key)
        conexao_ok = conexao_ok or ok
        if not ok:
            print(f'  CHAVE STRIPE INVALIDA: {msg}')

    if conexao_ok:
        print('  PIX e CARTAO prontos para producao.')
        print('  Falta apenas: cadastrar o WEBHOOK no painel Asaas')
        print('  (PAYMENT_RECEIVED / PAYMENT_CONFIRMED) apontando para')
        print('  https://SEU-DOMINIO/api/payments/webhook/asaas')
    else:
        print('  Nenhum gateway valido: os pagamentos rodam em MODO DEMO')
        print('  (sem cobranca real). Configure com:')
        print('    python3 scripts/setup_payments.py --asaas SUA_CHAVE [--prod]')
        print('    python3 scripts/setup_payments.py --stripe SUA_CHAVE --stripe-secret SEGREDO')
    print('-' * 66)


if __name__ == '__main__':
    main()
