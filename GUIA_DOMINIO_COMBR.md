# 🌐 Guia: Transformar o site em `.com.br`

> Objetivo: `https://auxiliofarmacia.com.br` (ou `www.auxiliofarmacia.com.br`)
>
> Custo do domínio: **R$ 40/ano** (Registro.br) · SSL: **grátis** (Cloudflare) ·
> Email: **grátis** (Cloudflare Email Routing)

---

## Escolha o nome

Verifiquei a disponibilidade agora:

| Domínio | Status |
|---|---|
| `auxiliofarmacia.com.br` | ✅ **LIVRE** |
| `auxilio-farmacia.com.br` | ✅ livre |
| `auxfarmacia.com.br` | ✅ livre |
| `auxiliofarmacia.com` | ❌ já registrado por terceiros |

**Recomendação: `auxiliofarmacia.com.br`** — sem hífen (menos erro de digitação),
com o nome da marca escrito por extenso, e `.com.br` que é o que o cliente
brasileiro digita e reconhece.

> 💡 `auxiliofarmacia.com` já está registrado por outra pessoa. Se quiser
> **proteger a marca**, registre também `auxfarmacia.com` (livre) logo em
> seguida e só redirecione — evita alguém registrar depois.

---

## Passo 1 — Registrar o domínio (você faz, ~10 min)

### Onde registrar

| Onde | Preço | Observação |
|---|---|---|
| **Registro.br** (direto) | **R$ 40/ano** | Mais barato, mas o pagamento é no nome do titular e o processo é mais manual |
| Locaweb / .ar / Hostinger | R$ 65–90/ano | Mais simples, já tem painel com DNS, mas markup maior |

**Recomendação:** Registro.br direto se você já tem conta lá (ou criar —
grátis). Se quiser praticidade, um provedor BR resolve tudo numa tela.

### O que você vai precisar

- **CPF** (pessoa física) ou **CNPJ** (empresa) — titular legal do domínio
- Documento com o mesmo nome do titular
- E-mail e telefone **correspondentes** aos dados do documento

> ⚠️ **Registre no CNPJ da empresa, não no CPF de um sócio.** Se você tiver
> CNPJ (inclusive MEI), use-o — o titular é quem responde legalmente pelo
> domínio. Se registrar no seu CPF pessoal e depois a empresa crescer, a
> transferência exige sua autorização.
>
> Se for CNPJ, o Registro.br pode levar **alguns dias** para validar a
> documentação da empresa. Comece por essa etapa.

### Cadastro no Registro.br

1. https://registro.br → **Criar conta** (ou entre)
2. Preencha: CPF/CNPJ, nome, email, telefone
3. Valide o email e o telefone (código por email/SMS)
4. Se for CNPJ: *Meus dados → Validar documentos → enviar comprovante*
5. Vá em **Registrar domínio** → pesquise `auxiliofarmacia.com.br` → escolha o período (1 a 10 anos) → pague (Pix, cartão, boleto)

Ao pagar, você vai receber os **nameservers**. Guarde-os (ex: `ana.ns.cloudflare.com`).

---

## Passo 2 — Apontar para a Cloudflare (eu faço)

> ✅ **O custom domain já está adicionado ao Pages** (`auxilio-farmacia.com.br`,
> status `pending` → aguardando o CNAME). Falta criar a zona DNS.

Para eu criar a zona, o token precisa de mais 2 permissões:

| Account | Permission | Access |
|---|---|---|
| Account | **Zone** | **Edit** |
| Account | **DNS** | **Edit** |

Em https://dash.cloudflare.com/profile/api-tokens → seu token → **Edit** → *Permissions*
→ *Add Permission* → adicione as duas → **Save**.

Depois eu rodo:

```bash
node scripts/adicionar-dominio-cloudflare.js auxiliofarmacia.com.br
```

e ele devolve os 2 nameservers para você colocar no Registro.br.

**Alternativa sem editar o token:** crie a zona pela UI —
*Websites → Add a site* → `auxiliofarmacia.com.br` → plano **Free** →
ele mostra os 2 nameservers. Me passe esses 2 e eu sigo daqui.

---

## Passo 3 — Trocar os nameservers no Registro.br

Ainda no painel do Registro.br (ou do provedor):

1. Edite o domínio `auxiliofarmacia.com.br`
2. Em **DNS**, troque os nameservers pelos 2 que a Cloudflare mostrou
3. Salve

⏱️ **Propagação: de minutos a 24h.** O Registro.br costuma ser rápido
(minutos). A Cloudflare avisa por e-mail assim que a zona ativar.

---

## Passo 4 — Adicionar o custom domain no Pages (eu faço)

```bash
node scripts/adicionar-dominio-cloudflare.js --pages dominio.com.br
```

A Cloudflare Pages cria sozinho os registros CNAME. O SSL é emitido
automaticamente (**Universal SSL**, grátis) — leva de 15 min a algumas horas.

---

## Passo 5 — Atualizar o backend

No Hugging Face Space → **Settings → Variables and secrets**:

```
APP_CORS_ORIGINS = https://auxiliofarmacia.com.br,https://www.auxiliofarmacia.com.br
APP_URL          = https://auxiliofarmacia.com.br
```

E o `site/config.js` **não muda** (ele aponta para a API, não para o site).

---

## Passo 6 — E-mail no seu domínio (bônus, grátis)

Com o domínio ativo dá pra criar `suporte@auxiliofarmacia.com.br`:

| Opção | Custo | Serve para |
|---|---|---|
| **Cloudflare Email Routing** | **grátis** | Encaminhar `suporte@` pro seu Gmail. Sem caixa de entrada própria, mas resolve 90% dos casos |
| Zoho Mail | grátis até 5 usuários | Caixa de entrada real, webmail |
| Google Workspace | ~US$ 7/mês | Gmail corporativo completo |

Para começar, o **Email Routing** resolve e é zero custo.

---

## Passo 7 — Limpeza (opcional)

1. O Workers Pages faz redirect de `auxilio-farmacia.pages.dev` para o domínio custom
2. O Worker antigo (`auxiliofarmacia.raphaelmenossi.workers.dev`) pode ser
   deletado — não serve mais para nada
3. Se quiser, desative o `.workers.dev` no Worker (`workers_dev = false` no `wrangler.toml`)

---

## Checklist

- [ ] Escolhi o nome (`auxiliofarmacia.com.br`)
- [ ] Registrei no CPF/CNPJ correto
- [ ] Paguei (R$ 40/ano)
- [ ] Tenho os 2 nameservers da Cloudflare
- [ ] Troquei os nameservers no Registro.br
- [ ] Cloudflare criou a zona (aviso por e-mail)
- [ ] Pages tem o custom domain + SSL ativo
- [ ] `APP_CORS_ORIGINS` atualizado no Space
- [ ] E-mail `suporte@` configurado
- [ ] Worker antigo deletado

---

## Erros comuns

| Sintoma | Causa | Solução |
|---|---|---|
| "Nameservers already pointing to Cloudflare" | O domínio já usa a Cloudflare | Normal, é o que queremos |
| Site não abre após 1h | Propagação ainda em curso | Espere; confira em `https://www.nslookup.com/` |
| Erro 522/523 | O DNS aponta mas o Pages não tem o domínio ainda | Reordene: adicione o custom domain no Pages **antes** de trocar os nameservers |
| SSL pendurado | Emissão em andamento | Force HTTPS nas settings do Pages depois do certificado |
| `.com.br` recusado | CPF/CNPJ sem validação ou contato divergente | Valide os dados no Registro.br |
