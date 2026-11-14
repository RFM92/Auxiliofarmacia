# 🔐 Guia: Ativar PIX e Cartão (Asaas) — passo a passo

O código **já está pronto**. Falta só a credencial da API. Sem ela, os pagamentos
rodam em **modo demo** (nenhuma cobrança real).

---

## Passo 1 — Crie a conta

| Ambiente | Para quê | URL |
|---|---|---|
| **Sandbox** (recomendo começar aqui) | Testes com dados fictícios, **não cobra** | https://sandbox.asaas.com |
| **Produção** | Cobrança real | https://www.asaas.com |

> ⚠️ As contas são **independentes**: chave do Sandbox não funciona em Produção e vice-versa.

---

## Passo 2 — Gere a chave de API

1. Entre na sua conta Asaas
2. Menu **Minha Conta → Integração → Gerar API Key**
   (ou direto: https://www.asaas.com/customerApiAccessToken/index)
3. Dê um nome (ex: `Auxilio Farmacia`) e defina uma data de expiração
4. **Copie a chave imediatamente** — ela aparece **só uma vez** e não pode ser recuperada

**Como identificar:**
| Prefixo | Ambiente |
|---|---|
| `$aact_prod_…` | Produção |
| `$aact_hmlg_…` | Sandbox |

> Só usuários **administradores** da conta podem gerar chaves.
> Máximo de 10 chaves por conta.

---

## Passo 3 — Grave a chave no projeto

```bash
# Sandbox (para testar)
python3 scripts/setup_payments.py --asaas $aact_hmlg_SUA_CHAVE

# Produção (para cobrar de verdade)
python3 scripts/setup_payments.py --asaas $aact_prod_SUA_CHAVE --prod
```

Isso grava em `/workspace/backend/.env` com permissão `600` e **nunca** entra no
código-fonte nem nos ZIPs.

### Verificar se ficou certo

```bash
python3 scripts/setup_payments.py --check
```

Saída esperada:
```
ASAAS_API_KEY        : CONFIGURADA
ASAAS_ENVIRONMENT    : production
Teste de conexao com o Asaas: OK - API respondeu 200
PIX e CARTAO prontos para producao (Asaas).
```

---

## Passo 4 — Configure o webhook (obrigatório)

O Asaas avisa nosso backend quando o pagamento é confirmado. Sem isso, a
licença **nunca é ativada** mesmo com o PIX pago.

**No painel Asaas:**
1. **Minha Conta → Integração → Webhooks**
2. Em *Eventos*, adicione:
   - `PAYMENT_RECEIVED`
   - `PAYMENT_CONFIRMED`
   - `PAYMENT_OVERDUE`
   - `PAYMENT_REFUNDED`
3. **Tipo:** `AUTOMATIC` (o Asaas envia o `access_token` da sua conta)
4. **URL:**
   ```
   https://SEU-DOMINIO/api/payments/webhook/asaas
   ```

> 🔗 **A URL precisa ser fixa e pública.** O tunnel `*.trycloudflare.com`
> muda a cada reinício → o webhook para de funcionar.
> Solução: use um **deploy permanente** (Netlify/Vercel/Cloudflare Pages para o
> frontend + um domínio/serveiro fixo para a API), ou um túnel **nomeado** do
> Cloudflare (URL fixa tipo `api.seudominio.com.br`).

### Token do webhook
Já existe no `.env`:
```
ASAAS_WEBHOOK_TOKEN=<valor>
```
O backend compara esse valor com o header `asaas-access-token` que o Asaas
envia. Se não bater, retorna **401** e o pagamento **não** ativa a licença.

---

## Passo 5 — Teste o fluxo completo

```bash
# 1. login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@auxfarmacia.com.br","password":"admin123"}'

# 2. criar um PIX (pegue o TOKEN do passo 1)
curl -X POST http://localhost:8000/api/payments/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"plan":"pro","method":"asaas_pix","cpf_cnpj":"12345678901","installments":1}'

# 3. consultar o status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/payments/check/PAYMENT_ID
```

No Sandbox, o Asaas permite **simular o pagamento** pelo painel
(*Cobranças → clicar na cobrança → "Simular pagamento"*), o que dispara o
webhook e ativa a licença de verdade. É a melhor forma de validar o fluxo
completo sem cobrar ninguém.

---

## Como fica para o usuário final

| Método | O que acontece |
|---|---|
| **PIX** | Tela mostra **QR Code** + **código copia-e-cola**, botão "Já paguei — verificar" e link para abrir no app do banco. Confirmação em segundos. |
| **Cartão** | Redireciona para o **checkout hospedado do Asaas** (o cartão é digitado no Asaas, **nunca passa pelo nosso servidor** — conformidade PCI-DSS). |
| **Boleto** | Link para o boleto em PDF + botão de verificação. |
| **NF** | Invoice — ainda não implementado no gateway (aparece como opção mas não gera cobrança). |

---

## Checklist de produção

- [ ] `ASAAS_API_KEY` configurada (`--check` retorna OK)
- [ ] `ASAAS_ENVIRONMENT=production` (só quando for cobrar de verdade)
- [ ] Webhook `PAYMENT_RECEIVED` / `PAYMENT_CONFIRMED` cadastrado
- [ ] `ASAAS_WEBHOOK_TOKEN` igual ao que o Asaas envia
- [ ] URL do webhook **fixa** (deploy permanente, não tunnel temporário)
- [ ] Conta Asaas com **CNPJ** e análise de crédito aprovada (a Asaas exige documentos da empresa para receber)
- [ ] Valor mínimo/limite configurado no painel se necessário

---

## ⚠️ Observações importantes

1. **A Asaas exige CNPJ** para conta de produção. Conta de pessoa física
   não recebe PIX de clientes.
2. **Sandbox não cobra nada** — é para validar a integração.
3. A chave tem **todos os privilégios** da conta. Nunca exponha em frontend,
   logs, repositório ou print.
4. O `.env` está fora dos ZIPs e do pacote de código — confirme com:
   ```bash
   unzip -l output/AuxilioFarmacia_CODIGO_COMPLETO_AVALIACAO.zip | grep -c "\.env"
   ```
   Deve retornar **0**.
