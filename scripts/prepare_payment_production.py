#!/usr/bin/env python3
"""
Deixa o gateway PRONTO PARA PRODUCAO em PIX + Cartao.

1) CARTAO (Asaas) sem PCI: em vez de enviar numero/validade/CVV pelo
   nosso servidor, cria a cobranca e devolve o `invoiceUrl` (checkout
   hospedado do Asaas). O cliente digita o cartao direto no gateway.
   Nenhum dado de cartao trafega pelo Auxilio Farmacia.

2) STRIPE: habilita PIX junto com cartao no checkout hospedado
   (`payment_method_types=['card', 'pix']`).

3) Metodo 'cartao' no PaymentService passa a usar o invoiceUrl.
"""
import re
from pathlib import Path

B = Path('/workspace/backend/api')
p = B / 'services' / 'payment_real.py'
c = p.read_text(encoding='utf-8')

# ---------- 1. create_credit_card_payment: sem dados de cartao no nosso servidor ----------
VELHO = """        try:
            customer = await self.create_customer(user_name, user_email, user_cpf)

            # Cria cobranca com cartao
            payment = await self._request('POST', '/payments', json={
                'customer': customer['id'],
                'billingType': 'CREDIT_CARD',
                'value': plan['prices']['brl'],
                'dueDate': datetime.now().strftime('%Y-%m-%d'),
                'description': f'{plan["name"]} - Auxílio Farmácia',
                'creditCard': {
                    'holderName': credit_card['holder_name'],
                    'number': credit_card['number'].replace(' ', ''),
                    'expiryMonth': credit_card['expiry_month'],
                    'expiryYear': credit_card['expiry_year'],
                    'ccv': credit_card['ccv'],
                },
                'creditCardHolderInfo': {
                    'name': user_name,
                    'email': user_email,
                    'cpfCnpj': user_cpf or '00000000000',
                },
            })

            return {
                'id': payment['id'],
                'status': payment['status'],
                'value': payment['value'],
                'billing_type': 'CREDIT_CARD',
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro Asaas Cartao: {e}")
            raise"""

NOVO = """        try:
            customer = await self.create_customer(user_name, user_email, user_cpf)

            # Cobranca de cartao SEM enviar dados do cartao para o nosso
            # servidor (PCI-DSS). O Asaas gera um checkout hospedado
            # (invoiceUrl) onde o proprio cliente digita o cartao.
            due = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
            payment = await self._request('POST', '/payments', json={
                'customer': customer['id'],
                'billingType': 'CREDIT_CARD',
                'value': plan['prices']['brl'],
                'dueDate': due,
                'description': f'{plan["name"]} - Auxilio Farmacia',
                'externalReference': plan_id,
            })

            return {
                'id': payment['id'],
                'status': payment['status'],
                'value': payment['value'],
                'due_date': payment.get('dueDate', due),
                'billing_type': 'CREDIT_CARD',
                'invoice_url': payment.get('invoiceUrl', ''),
                'mode': 'live'
            }
        except Exception as e:
            logger.error(f"Erro Asaas Cartao: {e}")
            raise"""

if VELHO in c:
    c = c.replace(VELHO, NOVO)
    print('payment_real.py: cartao usa checkout hospedado (sem PCI)')
else:
    print('payment_real.py: PADRAO DO CARTAO NAO ENCONTRADO')

# demo do cartao tambem deve devolver invoice_url
VELHO_DEMO = """        if not self.enabled:
            return {
                'id': f'pay_demo_{uuid.uuid4().hex[:16]}',
                'status': 'CONFIRMED',
                'value': plan['prices']['brl'],
                'billing_type': 'CREDIT_CARD',
                'mode': 'demo'
            }"""
NOVO_DEMO = """        if not self.enabled:
            return {
                'id': f'pay_demo_{uuid.uuid4().hex[:16]}',
                'status': 'PENDING',
                'value': plan['prices']['brl'],
                'billing_type': 'CREDIT_CARD',
                'invoice_url': f'https://demo.asaas.com/i/{uuid.uuid4().hex[:10]}',
                'mode': 'demo'
            }"""
if VELHO_DEMO in c:
    c = c.replace(VELHO_DEMO, NOVO_DEMO)
    print('payment_real.py: demo do cartao devolve invoice_url')

# ---------- 2. Stripe: habilita PIX + cartao ----------
c2 = c.replace("payment_method_types=['card'],", "payment_method_types=['card', 'pix'],")
if c2 != c:
    print('payment_real.py: Stripe com card + pix')
    c = c2

# ---------- 3. metodo 'cartao' do facade ----------
VELHO_F = """        elif method == 'cartao':
            # O cartao NAO deve trafegar pelo nosso servidor (PCI-DSS).
            # Sem gateway configurado, orienta usar o checkout hospedado.
            if not credit_card:
                raise ValueError(
                    "Pagamento com cartao deve ser feito no checkout hospedado do gateway."
                )
            return await self.asaas.create_credit_card_payment(
                plan_id, user_email, user_name, credit_card, user_cpf
            )"""
NOVO_F = """        elif method == 'cartao':
            # O cartao NAO trafega pelo nosso servidor (PCI-DSS): o Asaas
            # devolve um checkout hospedado (invoiceUrl) para o cliente digitar.
            return await self.asaas.create_credit_card_payment(
                plan_id, user_email, user_name, credit_card, user_cpf
            )"""
if VELHO_F in c:
    c = c.replace(VELHO_F, NOVO_F)
    print('payment_real.py: metodo cartao sem exigir dados no servidor')

p.write_text(c, encoding='utf-8')
print(f'payment_real.py: {len(c)} bytes')
