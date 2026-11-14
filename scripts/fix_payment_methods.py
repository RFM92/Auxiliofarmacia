#!/usr/bin/env python3
"""
CORRECAO no backend: nenhum metodo de pagamento do schema funcionava.

O schema `PaymentCreate` aceita:
    stripe_card | stripe_pix | stripe_boleto | asaas_pix | asaas_boleto | asaas_card
Mas `PaymentService.create_payment` so reconhecia:
    stripe | pix | boleto | cartao
=> TODAS as chamadas retornavam "Metodo invalido: asaas_pix".

Correcao: normalizar os aliases do schema para os nomes do servico.

Tambem: a rota passava `data.credit_card`, campo que NAO existe no schema
-> AttributeError capturado pelo except genérico, que devolvia success:false.
Agora usa getattr seguro.

E: o checkout nao deve coletar numero de cartao no site (PCI-DSS).
A coleta passa a ocorrer no gateway hospedado (Stripe checkout).
"""
import re
from pathlib import Path

B = Path('/workspace/backend/api')

# ---------- 1. payment_real.py: normaliza os metodos ----------
p = B / 'services' / 'payment_real.py'
c = p.read_text(encoding='utf-8')

VELHO = """        if method == 'stripe':
            return await self.stripe.create_checkout_session(
                plan_id, user_email, success_url or '', cancel_url or ''
            )
        elif method == 'pix':
            return await self.asaas.create_pix_payment(
                plan_id, user_email, user_name, user_cpf
            )
        elif method == 'boleto':
            return await self.asaas.create_boleto_payment(
                plan_id, user_email, user_name, user_cpf
            )
        elif method == 'cartao':
            if not credit_card:
                raise ValueError("credit_card obrigatorio")
            return await self.asaas.create_credit_card_payment(
                plan_id, user_email, user_name, credit_card, user_cpf
            )
        else:
            raise ValueError(f"Metodo invalido: {method}")"""

NOVO = """        # Normaliza os aliases vindos do schema (PaymentCreate) para os
        # metodos implementados pelos provedores.
        #   stripe_card/stripe_pix/stripe_boleto -> stripe (checkout hospedado)
        #   asaas_pix -> pix | asaas_boleto -> boleto | asaas_card -> cartao
        method = (method or '').strip().lower()
        aliases = {
            'stripe': 'stripe',
            'stripe_card': 'stripe',
            'stripe_pix': 'stripe',
            'stripe_boleto': 'stripe',
            'pix': 'pix',
            'asaas_pix': 'pix',
            'boleto': 'boleto',
            'asaas_boleto': 'boleto',
            'cartao': 'cartao',
            'card': 'cartao',
            'asaas_card': 'cartao',
        }
        method = aliases.get(method, method)

        if method == 'stripe':
            return await self.stripe.create_checkout_session(
                plan_id, user_email, success_url or '', cancel_url or ''
            )
        elif method == 'pix':
            return await self.asaas.create_pix_payment(
                plan_id, user_email, user_name, user_cpf
            )
        elif method == 'boleto':
            return await self.asaas.create_boleto_payment(
                plan_id, user_email, user_name, user_cpf
            )
        elif method == 'cartao':
            # O cartao NAO deve trafegar pelo nosso servidor (PCI-DSS).
            # Sem gateway configurado, orienta usar o checkout hospedado.
            if not credit_card:
                raise ValueError(
                    "Pagamento com cartao deve ser feito no checkout hospedado do gateway."
                )
            return await self.asaas.create_credit_card_payment(
                plan_id, user_email, user_name, credit_card, user_cpf
            )
        else:
            raise ValueError(f"Metodo invalido: {method}")"""

if VELHO in c:
    c = c.replace(VELHO, NOVO)
    p.write_text(c, encoding='utf-8')
    print('payment_real.py: metodos normalizados')
else:
    print('payment_real.py: PADRAO NAO ENCONTRADO')

# ---------- 2. routes/payments.py: credit_card seguro + method na URL ----------
p = B / 'routes' / 'payments.py'
c = p.read_text(encoding='utf-8')
VELHO2 = """            user_cpf=data.cpf_cnpj,
            credit_card=data.credit_card,"""
NOVO2 = """            user_cpf=data.cpf_cnpj,
            credit_card=getattr(data, 'credit_card', None),"""
if VELHO2 in c:
    c = c.replace(VELHO2, NOVO2)
    p.write_text(c, encoding='utf-8')
    print('payments.py: credit_card com getattr seguro')
else:
    print('payments.py: PADRAO NAO ENCONTRADO')
