/* ===================================================================
   AUXILIO FARMACIA - API CLIENT
   Conecta frontend ao backend FastAPI real
   =================================================================== */

const API_BASE = (function () {
  var cfg = (typeof window !== 'undefined' && window.AUXF_CONFIG) ? window.AUXF_CONFIG : {};
  var base = (cfg && cfg.apiBase) ? String(cfg.apiBase).replace(/\/+$/, '') : '';
  if (!base) {
    var local = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:');
    base = local ? 'http://localhost:8000' : window.location.origin;
  }
  return base;
})();

const API = {
  base: API_BASE,
  token: localStorage.getItem('auxf_api_token') || null,
  refreshToken: localStorage.getItem('auxf_refresh_token') || null,
  user: JSON.parse(localStorage.getItem('auxf_api_user') || 'null'),

  /* ========== HELPERS ========== */
  async _fetch(path, opts = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(opts.headers || {})
    };
    if (this.token && !opts.skipAuth) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    const res = await fetch(`${this.base}${path}`, {
      ...opts,
      headers,
      body: opts.body ? JSON.stringify(opts.body) : undefined
    });
    if (res.status === 401 && this.refreshToken) {
      await this._refreshToken();
      return this._fetch(path, opts);
    }
    return res;
  },

  _saveAuth(data) {
    this.token = data.access_token;
    this.refreshToken = data.refresh_token;
    this.user = data.user;
    localStorage.setItem('auxf_api_token', data.access_token);
    localStorage.setItem('auxf_refresh_token', data.refresh_token);
    localStorage.setItem('auxf_api_user', JSON.stringify(data.user));
  },

  _clearAuth() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    localStorage.removeItem('auxf_api_token');
    localStorage.removeItem('auxf_refresh_token');
    localStorage.removeItem('auxf_api_user');
  },

  async _refreshToken() {
    try {
      const r = await fetch(`${this.base}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken })
      });
      if (r.ok) {
        const data = await r.json();
        this.token = data.access_token;
        localStorage.setItem('auxf_api_token', data.access_token);
      } else {
        this._clearAuth();
      }
    } catch (e) {
      console.error('Refresh failed', e);
    }
  },

  isLoggedIn() {
    return !!this.token && !!this.user;
  },

  /* ========== AUTH ========== */
  async register({ email, password, name, crm, specialty }) {
    const r = await this._fetch('/api/auth/register', {
      method: 'POST',
      body: { email, password, name, crm, specialty },
      skipAuth: true
    });
    if (!r.ok) throw await this._error(r, 'Falha no cadastro');
    const data = await r.json();
    this._saveAuth(data);
    return data;
  },

  async login(email, password) {
    const r = await this._fetch('/api/auth/login', {
      method: 'POST',
      body: { email, password },
      skipAuth: true
    });
    if (!r.ok) throw await this._error(r, 'Email ou senha incorretos');
    const data = await r.json();
    this._saveAuth(data);
    return data;
  },

  async logout() {
    this._clearAuth();
    window.location.reload();
  },

  async getMe() {
    const r = await this._fetch('/api/auth/me');
    if (!r.ok) throw await this._error(r, 'Falha ao buscar perfil');
    return r.json();
  },

  async updateMe(data) {
    const r = await this._fetch('/api/auth/me', {
      method: 'PUT',
      body: data
    });
    if (!r.ok) throw await this._error(r, 'Falha ao atualizar perfil');
    return r.json();
  },

  async forgotPassword(email) {
    const r = await this._fetch('/api/auth/forgot-password', {
      method: 'POST',
      body: { email },
      skipAuth: true
    });
    return r.ok;
  },

  /* ========== LICENSES ========== */
  async getDemoKeys() {
    // O endpoint /api/licenses/demo-keys exige autenticacao de admin.
    // Em caso de falha, devolve as chaves de demonstracao locais do frontend
    // para o modo de demonstracao continuar funcionando.
    try {
      const r = await this._fetch('/api/licenses/demo-keys', { skipAuth: false });
      if (r.ok) return await r.json();
    } catch (e) { /* fallback abaixo */ }
    return {
      demo_keys: [
        { key: 'AUXFARMA-DEMO1-DEMO2-DEMO3-DEMO4', tier: 'pro', description: 'Pro - Recursos completos' },
        { key: 'AUXFARMA-DEMO5-DEMO6-DEMO7-DEMO8', tier: 'premium', description: 'Premium - Bulas FDA/EMA' },
        { key: 'AUXFARMA-INST1-INST2-INST3-INST4', tier: 'institutional', description: 'Institucional - Multi-usuario' }
      ]
    };
  },

  async activateLicense(key, deviceFingerprint) {
    const r = await this._fetch('/api/licenses/activate', {
      method: 'POST',
      body: { key, fingerprint: deviceFingerprint },
      skipAuth: !this.isLoggedIn()
    });
    if (!r.ok) throw await this._error(r, 'Chave invalida ou ja usada');
    return r.json();
  },

  async validateLicense(key) {
    const r = await this._fetch('/api/licenses/validate', {
      method: 'POST',
      body: { license_key: key },
      skipAuth: true
    });
    if (!r.ok) return null;
    return r.json();
  },

  async deactivateLicense(key) {
    const r = await this._fetch('/api/licenses/deactivate', {
      method: 'POST',
      body: { license_key: key }
    });
    return r.ok;
  },

  async getMyLicenses() {
    const r = await this._fetch('/api/licenses/my');
    if (!r.ok) return [];
    return r.json();
  },

  /* ========== PAYMENTS ========== */
  async createPayment({ tier, method }) {
    const r = await this._fetch('/api/payments/create', {
      method: 'POST',
      body: { tier, method }
    });
    if (!r.ok) throw await this._error(r, 'Falha ao criar pagamento');
    return r.json();
  },

  async getMyPayments() {
    const r = await this._fetch('/api/payments/my');
    if (!r.ok) return [];
    return r.json();
  },

  /* ========== COURSES ========== */
  async getCourses() {
    const r = await this._fetch('/api/courses', { skipAuth: true });
    if (!r.ok) return [];
    return r.json();
  },

  async getCourse(id) {
    const r = await this._fetch(`/api/courses/${id}`, { skipAuth: true });
    if (!r.ok) return null;
    return r.json();
  },

  async enrollCourse(courseId) {
    const r = await this._fetch(`/api/courses/${courseId}/enroll`, {
      method: 'POST'
    });
    if (!r.ok) throw await this._error(r, 'Falha na matricula');
    return r.json();
  },

  async getMyCourses() {
    const r = await this._fetch('/api/courses/my');
    if (!r.ok) return [];
    return r.json();
  },

  async saveCourseProgress(courseId, moduleIdx, completed) {
    const r = await this._fetch(`/api/courses/${courseId}/progress`, {
      method: 'POST',
      body: { module_index: moduleIdx, completed }
    });
    return r.ok;
  },

  async getCertificate(courseId) {
    const r = await this._fetch(`/api/courses/${courseId}/certificate`);
    if (!r.ok) throw await this._error(r, 'Curso nao concluido');
    return r.json();
  },

  async buyBundle(bundleId) {
    const r = await this._fetch(`/api/courses/bundles/${bundleId}/purchase`, {
      method: 'POST'
    });
    if (!r.ok) throw await this._error(r, 'Falha na compra do bundle');
    return r.json();
  },

  /* ========== TELEMETRY ========== */
  async trackEvent(eventType, eventData) {
    try {
      await this._fetch('/api/telemetry/track', {
        method: 'POST',
        body: {
          event_type: eventType,
          event_data: eventData || {}
        },
        skipAuth: true
      });
    } catch (e) {
      // Telemetria e non-critical
      console.debug('telemetry failed', e);
    }
  },

  async trackBatch(events) {
    try {
      await this._fetch('/api/telemetry/batch', {
        method: 'POST',
        body: { events }
      });
    } catch (e) {
      console.debug('telemetry batch failed', e);
    }
  },

  /* ========== ADMIN ========== */
  async adminGetStats() {
    const r = await this._fetch('/api/admin/stats');
    if (!r.ok) return null;
    return r.json();
  },

  async adminGetUsers() {
    const r = await this._fetch('/api/admin/users');
    if (!r.ok) return [];
    return r.json();
  },

  async adminGetLicenses() {
    const r = await this._fetch('/api/admin/licenses');
    if (!r.ok) return [];
    return r.json();
  },

  async adminGetPayments() {
    const r = await this._fetch('/api/admin/payments');
    if (!r.ok) return [];
    return r.json();
  },

  async adminCreateLicense({ tier, duration_days, user_email }) {
    const r = await this._fetch('/api/admin/licenses/create', {
      method: 'POST',
      body: { tier, duration_days, user_email }
    });
    if (!r.ok) throw await this._error(r, 'Falha ao criar licenca');
    return r.json();
  },

  async adminRevokeLicense(key) {
    const r = await this._fetch(`/api/admin/licenses/${key}/revoke`, {
      method: 'POST'
    });
    return r.ok;
  },

  async adminGetRecentTelemetry() {
    const r = await this._fetch('/api/admin/telemetry/recent');
    if (!r.ok) return [];
    return r.json();
  },


  /* ========== PAYMENTS (Stripe + Asaas) ========== */
  async getPlans() {
    const r = await this._fetch('/api/payments/plans', { skipAuth: true });
    if (!r.ok) return [];
    return r.json();
  },

  async getPlan(planId) {
    const r = await this._fetch(`/api/payments/plans/${planId}`, { skipAuth: true });
    if (!r.ok) return null;
    return r.json();
  },

  async createPixPayment(planId, cpfCnpj = null) {
    if (!this.isLoggedIn()) throw new Error('Faca login primeiro');
    const r = await this._fetch('/api/payments/create', {
      method: 'POST',
      body: { plan: planId, method: 'pix', cpf_cnpj: cpfCnpj }
    });
    if (!r.ok) throw await this._error(r, 'Falha ao gerar PIX');
    return r.json();
  },

  async createBoletoPayment(planId, cpfCnpj = null) {
    if (!this.isLoggedIn()) throw new Error('Faca login primeiro');
    const r = await this._fetch('/api/payments/create', {
      method: 'POST',
      body: { plan: planId, method: 'boleto', cpf_cnpj: cpfCnpj }
    });
    if (!r.ok) throw await this._error(r, 'Falha ao gerar boleto');
    return r.json();
  },

  async createCardPayment(planId, creditCard, cpfCnpj = null) {
    if (!this.isLoggedIn()) throw new Error('Faca login primeiro');
    const r = await this._fetch('/api/payments/create', {
      method: 'POST',
      body: {
        plan: planId,
        method: 'cartao',
        cpf_cnpj: cpfCnpj,
        credit_card: creditCard
      }
    });
    if (!r.ok) throw await this._error(r, 'Falha ao processar cartao');
    return r.json();
  },

  async createStripeCheckout(planId) {
    if (!this.isLoggedIn()) throw new Error('Faca login primeiro');
    const r = await this._fetch('/api/payments/create', {
      method: 'POST',
      body: { plan: planId, method: 'stripe' }
    });
    if (!r.ok) throw await this._error(r, 'Falha ao criar checkout Stripe');
    return r.json();
  },

  async checkPaymentStatus(paymentId) {
    const r = await this._fetch(`/api/payments/check/${paymentId}`);
    if (!r.ok) return null;
    return r.json();
  },

  async getMyPayments() {
    const r = await this._fetch('/api/payments/my');
    if (!r.ok) return [];
    return r.json();
  },

  // ========== POLLING DE PAGAMENTO PIX ==========
  async pollPayment(paymentId, onUpdate, timeout = 300000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      const status = await this.checkPaymentStatus(paymentId);
      if (onUpdate) onUpdate(status);
      if (status && (status.status === 'paid' || status.status === 'CONFIRMED' || status.status === 'RECEIVED')) {
        return status;
      }
      await new Promise(r => setTimeout(r, 3000)); // Poll a cada 3s
    }
    return null;
  },

  /* ========== UTILS ========== */
  async _error(res, defaultMsg) {
    try {
      const data = await res.json();
      return new Error(data.detail || data.message || defaultMsg);
    } catch {
      return new Error(defaultMsg);
    }
  },

  /* ========== DEVICE FINGERPRINT ========== */
  getDeviceFingerprint() {
    let fp = localStorage.getItem('auxf_device_fp');
    if (!fp) {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.fillText('AuxFarmacia-' + navigator.userAgent, 2, 15);
      const canvasHash = canvas.toDataURL();

      const components = [
        navigator.userAgent,
        navigator.language,
        screen.width + 'x' + screen.height,
        new Date().getTimezoneOffset(),
        canvasHash
      ].join('|');

      fp = this._hash(components);
      localStorage.setItem('auxf_device_fp', fp);
    }
    return fp;
  },

  _hash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const chr = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + chr;
      hash |= 0;
    }
    return Math.abs(hash).toString(16).padStart(16, '0');
  }
};

// ========== TELEMETRIA AUTOMATICA ==========
(function autoTrack() {
  if (typeof window === 'undefined') return;

  const sessionStart = Date.now();
  const events = [];

  // Track page view
  events.push({
    event_type: 'page_view',
    event_data: {
      url: window.location.pathname,
      referrer: document.referrer,
      ts: new Date().toISOString()
    }
  });

  // Flush a cada 30s ou 10 eventos
  let pending = [...events];
  events.length = 0;

  const flush = () => {
    if (pending.length === 0) return;
    API.trackBatch(pending).catch(() => {});
    pending = [];
  };

  setInterval(flush, 30000);
  window.addEventListener('beforeunload', flush);

  // Track cliques em medicamentos
  document.addEventListener('click', e => {
    const target = e.target.closest('[data-med-id], [data-calc-id]');
    if (target) {
      pending.push({
        event_type: 'interaction',
        event_data: {
          type: target.dataset.medId ? 'medication' : 'calculator',
          id: target.dataset.medId || target.dataset.calcId,
          ts: new Date().toISOString()
        }
      });
    }
  });

  // Flush periodico
  setInterval(() => {
    if (pending.length >= 10) flush();
  }, 5000);
})();

// ========== INTERCEPT FETCH PARA DEMO MODE ==========
const _origFetch = window.fetch;
window.fetch = async function(url, opts) {
  // Detecta URLs demo (no-op)
  if (typeof url === 'string' && url.startsWith('demo://')) {
    return new Response(JSON.stringify({ demo: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  return _origFetch(url, opts);
};

window.AUXF_API = API;
console.log('✅ Auxílio Farmácia API client loaded');