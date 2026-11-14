    // Desabilita botão
    const btn = document.getElementById('btnPay');
    btn.disabled = true;
    btn.innerHTML = '<span style="display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 0.8s linear infinite;"></span> Processando...';

    // Metodo da UI -> metodo da API
    const apiMethod = {
      card:   'stripe_card',
      pix:    'asaas_pix',
      boleto: 'asaas_boleto'
    }[method] || 'stripe_card';

    const cpf = (document.getElementById('inputCpf') ? document.getElementById('inputCpf').value : '').trim()
             || (document.getElementById('inputCnpj') ? document.getElementById('inputCnpj').value : '').trim() || null;
    const token = localStorage.getItem('auxf_api_token') || '';

    try {
      const resp = await fetch(checkoutApiBase() + '/api/payments/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': 'Bearer ' + token } : {})
        },
        body: JSON.stringify({
          plan: planKey,
          method: apiMethod,
          cpf_cnpj: cpf,
          installments: 1
        })
      });

      const data = await resp.json().catch(() => ({}));

      if (!resp.ok || data.success === false) {
        const msg = data.detail || data.error || 'Nao foi possivel iniciar o pagamento.';
        showAlert('error', msg);
        btn.disabled = false;
        btn.innerHTML = 'Pagar R$ ' + plan.price.toFixed(2).replace('.', ',');
        return;
      }

      // Stripe -> checkout hospedado
      const redirectUrl = data.checkout_url || data.invoice_url;
      if (redirectUrl) {
        showAlert('info', 'Redirecionando para o gateway de pagamento...');
        window.location.href = redirectUrl;
        return;
      }

      // Asaas -> PIX copia-e-cola / QR
      if (data.pix_code || data.pix_qr_code) {
        showPixPayment(data, planKey);
        btn.disabled = false;
        btn.innerHTML = 'Pagar R$ ' + plan.price.toFixed(2).replace('.', ',');
        return;
      }

      // Asaas -> boleto
      if (data.boleto_url) {
        showBoletoPayment(data, planKey);
        btn.disabled = false;
        btn.innerHTML = 'Pagar R$ ' + plan.price.toFixed(2).replace('.', ',');
        return;
      }

      // Modo demo do backend (sem credenciais de gateway)
      if (data.mode === 'demo') {
        showDemoPayment(data, planKey);
        return;
      }

      showAlert('error', 'O gateway nao retornou forma de pagamento. Tente outro metodo.');
      btn.disabled = false;
      btn.innerHTML = 'Pagar R$ ' + plan.price.toFixed(2).replace('.', ',');
    } catch (err) {
      // Backend fora do ar: NAO finge que o pagamento foi feito
      console.error('[Checkout] Falha ao chamar a API de pagamento:', err);
      showAlert('error', 'Nao foi possivel conectar ao servidor de pagamento. Verifique sua conexao e tente novamente.');
      btn.disabled = false;
      btn.innerHTML = 'Pagar R$ ' + plan.price.toFixed(2).replace('.', ',');
    }
  }

  function checkoutApiBase() {
    return (window.location.origin.indexOf('localhost') !== -1 || window.location.protocol === 'file:')
      ? 'http://localhost:8000'
      : window.location.origin;
  }

  // ===== PAGAMENTO VIA PIX (Asaas) =====
  function showPixPayment(data, planKey) {
    const box = document.getElementById('pixBox');
    if (!box) return;
    box.innerHTML = `
      <h3 style="color: var(--ink); margin-bottom: 6px;">Pague com PIX</h3>
      <p style="font-size: 0.85rem; color: var(--muted); margin-bottom: 12px;">
        Abra o app do seu banco, escolha PIX e use o codigo copia-e-cola:
      </p>
      ${data.pix_qr_code ? `<img src="${data.pix_qr_code}" alt="QR Code PIX do pagamento da assinatura Auxilio Farmacia" style="width: 220px; height: 220px; background: #fff; padding: 10px; border-radius: 10px; margin-bottom: 12px;">` : ''}
      <textarea id="pixCode" readonly aria-label="Codigo PIX copia e cola"
        style="width: 100%; min-height: 90px; font-family: monospace; font-size: 11px; padding: 10px; border-radius: 8px; border: 1px solid var(--line); background: var(--bg); color: var(--ink); word-break: break-all;">${data.pix_code || ''}</textarea>
      <div style="display: flex; gap: 8px; margin-top: 12px;">
        <button type="button" id="btnCopyPix" class="btn" style="background: var(--bg); color: var(--ink); border: 1px solid var(--line); flex: 1;">Copiar codigo</button>
        <button type="button" id="btnCheckPix" class="btn btn-primary" style="flex: 1;">Ja paguei - verificar</button>
      </div>
      <p id="pixStatus" role="status" aria-live="polite" style="font-size: 0.8rem; color: var(--muted); margin-top: 10px;"></p>
    `;
    box.classList.add('show');
    wirePaymentButtons(data.payment_id, planKey);
  }

  function copyPix() {
    const ta = document.getElementById('pixCode');
    if (!ta) return;
    ta.select();
    const done = () => showAlert('success', 'Codigo PIX copiado!');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(ta.value).then(done).catch(() => { document.execCommand('copy'); done(); });
    } else {
      document.execCommand('copy');
      done();
    }
  }

  // ===== PAGAMENTO VIA BOLETO =====
  function showBoletoPayment(data, planKey) {
    const box = document.getElementById('pixBox');
    if (!box) return;
    box.innerHTML = `
      <h3 style="color: var(--ink); margin-bottom: 6px;">Boleto bancario</h3>
      <p style="font-size: 0.85rem; color: var(--muted); margin-bottom: 12px;">
        Vence em ${data.due_date || '3 dias uteis'}.
      </p>
      <a href="${data.boleto_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary"
         style="display: block; text-align: center; text-decoration: none; margin-bottom: 10px;">Abrir boleto</a>
      <button type="button" id="btnCheckPix" class="btn" style="background: var(--bg); color: var(--ink); border: 1px solid var(--line); width: 100%;">Ja paguei - verificar</button>
      <p id="pixStatus" role="status" aria-live="polite" style="font-size: 0.8rem; color: var(--muted); margin-top: 10px;"></p>
    `;
    box.classList.add('show');
    wirePaymentButtons(data.payment_id, planKey);
  }

  function wirePaymentButtons(paymentId, planKey) {
    const bCopy = document.getElementById('btnCopyPix');
    if (bCopy) bCopy.addEventListener('click', copyPix);
    const bCheck = document.getElementById('btnCheckPix');
    if (bCheck) bCheck.addEventListener('click', function () { checkPaymentStatus(paymentId, planKey); });
  }

  // ===== VERIFICA STATUS DO PAGAMENTO =====
  async function checkPaymentStatus(paymentId, planKey) {
    const st = document.getElementById('pixStatus');
    if (st) st.textContent = 'Verificando pagamento...';
    try {
      const token = localStorage.getItem('auxf_api_token') || '';
      const r = await fetch(checkoutApiBase() + '/api/payments/check/' + paymentId, {
        headers: token ? { 'Authorization': 'Bearer ' + token } : {}
      });
      const d = await r.json().catch(() => ({}));
      const pago = d.status === 'paid' || d.status === 'confirmed' || d.paid_at || d.paid;
      if (pago) {
        if (st) st.innerHTML = '<strong>Pagamento confirmado!</strong> Abrindo a plataforma...';
        localStorage.setItem('auxf_pending_plan', planKey);
        setTimeout(function () { window.location.href = 'dashboard-auxfarmacia.html'; }, 1200);
      } else if (st) {
        st.textContent = 'Pagamento ainda nao confirmado. Se ja pagou, aguarde alguns minutos e clique em verificar novamente.';
      }
    } catch (e) {
      if (st) st.textContent = 'Nao foi possivel verificar agora. Tente novamente em instantes.';
    }
  }

  // ===== MODO DEMO (backend sem credenciais de gateway) =====
  function showDemoPayment(data, planKey) {
    const box = document.getElementById('pixBox');
    if (box) {
      box.innerHTML = `
        <h3 style="color: var(--ink); margin-bottom: 6px;">Modo demonstracao</h3>
        <p style="font-size: 0.85rem; color: var(--muted); margin-bottom: 12px;">
          As credenciais do gateway nao estao configuradas, portanto
          <strong>nenhuma cobranca real foi feita</strong> e nenhum plano foi ativado.
        </p>
        <button type="button" id="btnCheckPix" class="btn btn-primary" style="width: 100%;">Verificar status</button>
        <p id="pixStatus" role="status" aria-live="polite" style="font-size: 0.8rem; color: var(--muted); margin-top: 10px;"></p>
      `;
      box.classList.add('show');
      wirePaymentButtons(data.paymentId || data.payment_id, planKey);
    }
    showAlert('info', 'Modo demonstracao: nenhuma cobranca real foi realizada.');
  }

