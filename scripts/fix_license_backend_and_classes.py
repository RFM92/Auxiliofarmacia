#!/usr/bin/env python3
"""
1) activateLicense valida no BACKEND (a chamada estava comentada)
2) As chaves demo expiravam em 2025-12-31 -> hoje NINGUEM conseguia ativar
   nenhuma licenca (nem demo). Validade estendida.
3) Numero de classes corrigido: 50 -> 10 (o real: 10 classes terapeuticas)
"""
import re
from pathlib import Path

OUT = Path('/workspace/output')
DASH = sorted(OUT.glob('dashboard-auxfarmacia*.html'))

# ---------- 1. activateLicense -> backend ----------
VELHO = """  // Em producao, tentaria validar online:
  // const response = await fetch(`${LICENSE_CONFIG.apiUrl}/license/activate`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ key: cleanKey, fingerprint: fp })
  // });

  return {
    success: false,
    error: 'invalid_key',
    message: '❌ Chave inválida ou não encontrada. Verifique se digitou corretamente.'
  };
}"""

NOVO = """  // 3) Valida no BACKEND (fonte de verdade das assinaturas)
  try {
    const base = (window.location.origin.indexOf('localhost') !== -1 || window.location.protocol === 'file:')
      ? 'http://localhost:8000'
      : window.location.origin;
    const token = localStorage.getItem('auxf_api_token') || '';
    const resp = await fetch(base + '/api/licenses/activate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': 'Bearer ' + token } : {})
      },
      body: JSON.stringify({
        key: cleanKey,
        fingerprint: fp,
        device_name: (navigator.userAgent || '').slice(0, 80)
      })
    });
    const data = await resp.json().catch(() => ({}));

    if (resp.ok && (data.success || data.tier || data.license)) {
      const lic = data.license || data;
      const tier = lic.tier || data.tier || 'pro';
      const license = {
        key: cleanKey,
        tier: tier,
        email: lic.email || data.email || null,
        expiresAt: lic.expires_at || lic.expiresAt || null,
        activatedAt: new Date().toISOString(),
        fingerprint: fp,
        tierInfo: TIERS[tier] || TIERS.pro
      };
      try {
        localStorage.setItem('auxf_license', JSON.stringify(license));
        localStorage.setItem('auxf_license_cache_at', Date.now().toString());
      } catch (e) { console.error('Erro ao salvar licença:', e); }

      currentLicense = license;
      currentTier = tier;
      isLicenseValid = true;
      try { applyPaywall(); } catch (e) {}

      trackEvent('license_activated', { tier: tier, email: license.email });

      return {
        success: true,
        message: `✅ Licença ${(TIERS[tier] || TIERS.pro).name} ativada com sucesso!`,
        license: license
      };
    }

    // Backend respondeu mas recusou -> motve real
    if (resp.status && resp.status !== 0 && resp.status < 500) {
      const motivo = data.detail || data.reason || data.error || 'Chave inválida ou não encontrada.';
      const erros = {
        not_found: '❌ Chave não encontrada no servidor.',
        expired: '❌ Esta chave expirou. Renove sua assinatura.',
        revoked: '❌ Esta chave foi revogada.',
        suspended: '❌ Esta chave está suspensa.',
        device_limit_reached: '❌ Limite de dispositivos atingido. Desative um dispositivo.',
        invalid_format: '❌ Formato de chave inválido.'
      };
      return {
        success: false,
        error: data.reason || data.error || 'invalid_key',
        message: erros[data.reason] || ('❌ ' + motivo)
      };
    }
  } catch (e) {
    console.warn('[License] Backend indisponível, usando validação local:', e);
  }

  // 4) Fallback: chaves DEMO locais (somente quando o backend nao responde)
  if (DEMO_LICENSES[cleanKey]) {
    const demo = DEMO_LICENSES[cleanKey];
    const license = {
      key: cleanKey,
      tier: demo.tier,
      email: demo.email,
      expiresAt: demo.expiresAt,
      activatedAt: new Date().toISOString(),
      fingerprint: fp,
      tierInfo: TIERS[demo.tier]
    };
    try {
      localStorage.setItem('auxf_license', JSON.stringify(license));
      localStorage.setItem('auxf_license_cache_at', Date.now().toString());
    } catch (e) { console.error('Erro ao salvar licença:', e); }
    currentLicense = license;
    currentTier = demo.tier;
    isLicenseValid = true;
    trackEvent('license_activated', { tier: demo.tier, email: demo.email });
    return {
      success: true,
      message: `✅ Licença ${TIERS[demo.tier].name} ativada com sucesso!`,
      license: license
    };
  }

  return {
    success: false,
    error: 'invalid_key',
    message: '❌ Chave inválida ou não encontrada. Verifique se digitou corretamente.'
  };
}"""

# ---------- 2. demo keys: validade ----------
EXPIRA_VELHO = "expiresAt: '2025-12-31T23:59:59Z'"
EXPIRA_NOVO = "expiresAt: '2027-12-31T23:59:59Z'"

total = 0
for p in DASH:
    c = p.read_text(encoding='utf-8')
    orig = c
    n = 0
    if VELHO in c:
        c = c.replace(EXPIRA_VELHO, EXPIRA_NOVO)
        n += c.count(EXPIRA_NOVO) and 1
    if 'Em producao, tentaria validar online' in c:
        c = c.replace(VELHO, NOVO)
        n += 1
    if c != orig:
        p.write_text(c, encoding='utf-8')
    total += n
    print(f'{p.name}: {n} correcao(oes)')

print(f'\nTotal: {total}')

# ---------- 3. numero de classes: 50 -> 10 ----------
subs = [
    (r'(>)\s*50\s*(<)', r'\g<1>10\g<2>'),
    (r'(>\s*)50(\s*<)', r'\g<1>10\g<2>'),
    (r'\b50\s+[Cc]lasses\b', '10 Classes'),
    (r'\b50\s+classes\s+terapêuticas\b', '10 classes terapêuticas'),
    (r'\b50\s+classes\b', '10 classes'),
    (r'\b50\s+grupos\b', '10 grupos'),
]
t2 = 0
for p in sorted(OUT.glob('*.html')):
    c = p.read_text(encoding='utf-8', errors='replace')
    orig = c
    n = 0
    for pat, rep in subs:
        c, k = re.subn(pat, rep, c)
        n += k
    if c != orig:
        p.write_text(c, encoding='utf-8')
    t2 += n
    if n:
        print(f'{p.name}: {n} numero(s) de classe corrigido(s)')
print(f'Total de numeros corrigidos: {t2}')
