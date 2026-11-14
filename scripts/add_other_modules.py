#!/usr/bin/env python3
"""
Adiciona 4 modulos complementares:
1. IECA vs BRA (diferencas praticas)
2. Diureticos (tiazidicos vs alca vs poupadores)
3. ARA II (Alisquireno) - novo grupo
4. Betabloqueadores (cardiosseletivos vs nao-seletivos)
"""
import re
from pathlib import Path

# ===== MODULO IECA vs BRA =====
IECA_BRA_HTML = """
<!-- ========== MODULO IECA vs BRA ========== -->
<div class="bcc-module" id="iecaBraModule" style="background:linear-gradient(135deg,#fef2f2 0%,#fee2e2 100%);border-color:#dc2626;">
  <div class="bcc-header">
    <div class="bcc-icon" style="background:linear-gradient(135deg,#dc2626,#b91c1c);">💊</div>
    <div>
      <h3 class="bcc-title" style="color:#7f1d1d;">IECA vs BRA - Diferencas Praticas</h3>
      <p class="bcc-subtitle">Comparativo dos inibidores do sistema renina-angiotensina</p>
    </div>
  </div>

  <div class="bcc-intro">
    Os <strong>IECA</strong> (inibidores da ECA) e os <strong>BRA</strong> (bloqueadores do receptor AT1) agem no mesmo sistema (SRAA), mas em pontos diferentes. Ambos sao excelente primeira escolha para HAS, especialmente em diabeticos com proteinuria. Porem, diferem em <strong>tolerabilidade</strong>, <strong>eficacia</strong> e <strong>indicacoes especificas</strong>.
  </div>

  <!-- Tabela comparativa -->
  <div class="bcc-table-wrapper">
    <table class="bcc-table">
      <thead>
        <tr>
          <th style="width:20%;">Caracteristica</th>
          <th style="width:40%;">IECA (Captopril, Enalapril, Ramipril)</th>
          <th style="width:40%;">BRA (Losartana, Valsartana, Olmesartana)</th>
        </tr>
      </thead>
      <tbody>
        <tr class="bcc-group-header">
          <td colspan="3">⚙️ MECANISMO</td>
        </tr>
        <tr>
          <td><strong>Onde age</strong></td>
          <td>Inibe a enzima conversora de angiotensina (ECA), impedindo formacao de Angiotensina II.</td>
          <td>Bloqueia o receptor AT1 diretamente, impedindo a Angiotensina II de agir.</td>
        </tr>
        <tr>
          <td><strong>Bradicinina</strong></td>
          <td>Aumenta (causa tosse e angioedema)</td>
          <td>NAO afeta (sem tosse/angioedema)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="3">💊 EXEMPLOS</td>
        </tr>
        <tr>
          <td><strong>Principais</strong></td>
          <td>Captopril, Enalapril, Ramipril, Lisinopril, Perindopril</td>
          <td>Losartana, Valsartana, Candesartana, Olmesartana, Telmisartana</td>
        </tr>
        <tr>
          <td><strong>Sufixo</strong></td>
          <td>-pril</td>
          <td>-sartana</td>
        </tr>
        <tr>
          <td><strong>Posologia tipica</strong></td>
          <td>1-2x/dia (captopril 2-3x/dia)</td>
          <td>1x/dia (longa duracao)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="3">⚠️ EFEITOS ADVERSOS</td>
        </tr>
        <tr>
          <td><strong>Tosse seca</strong></td>
          <td><strong>10-20%</strong> (principal causa de abandono)</td>
          <td>Raro (&lt; 1%)</td>
        </tr>
        <tr>
          <td><strong>Angioedema</strong></td>
          <td><strong>0,1-0,7%</strong> (mais comum em negros)</td>
          <td>Raro, mas reportado</td>
        </tr>
        <tr>
          <td><strong>Hipercalemia</strong></td>
          <td>Sim (monitorar K+)</td>
        </tr>
        <tr>
          <td><strong>Insuficiencia renal aguda</strong></td>
          <td>Sim (especialmente em estenose bilateral de arteria renal)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="3">✅ INDICACOES PREFERENCIAIS</td>
        </tr>
        <tr>
          <td><strong>Pos-IAM</strong></td>
          <td>Captopril, Ramipril (reducao de mortalidade comprovada)</td>
          <td>Valsartana (alternativa)</td>
        </tr>
        <tr>
          <td><strong>IC com FEr reduzida</strong></td>
          <td>Enalapril, Ramipril</td>
          <td>Losartana, Valsartana, Candesartana</td>
        </tr>
        <tr>
          <td><strong>DM2 + proteinuria</strong></td>
          <td>Excelente (nefroprotetor)</td>
          <td>Excelente (nefroprotetor equivalente)</td>
        </tr>
        <tr>
          <td><strong>Prevencao de migranea</strong></td>
          <td>—</td>
          <td>Candesartana (unica com evidência forte)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mnemonicos -->
  <div class="bcc-mnemonics" style="background:linear-gradient(135deg,#fef9c3 0%,#fde68a 100%);border:2px dashed #ca8a04;">
    <h3 class="bcc-mnemonics-title">🧠 Dicas de Memorizacao</h3>

    <div class="mnemonic-card" style="border-color:#dc2626;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#dc2626;">SUFIXO</span>
        <h4 class="mnemonic-title">"PRIL" = PRIMEIRO / PRIORIDADE</h4>
      </div>
      <p class="mnemonic-content">
        IECA terminam em <strong>-pril</strong> (Capto<strong>pril</strong>, Enala<strong>pril</strong>). Foi o PRIMEIRO grupo a ser descoberto e tem mais evidencias de reducao de mortalidade.
      </p>
    </div>

    <div class="mnemonic-card" style="border-color:#f59e0b;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#f59e0b;">SUFIXO</span>
        <h4 class="mnemonic-title">"SARTANA" = SEM tosse / SEM angioedema</h4>
      </div>
      <p class="mnemonic-content">
        BRA terminam em <strong>-sartana</strong>. Como agem DEPOIS da formacao de angiotensina II, NAO acumulam bradicinina. Sao a <strong>alternativa para quem tem tosse com IECA</strong>.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Dica:</strong> Se paciente tosse com Captopril, troque para Losartana (mas espere 36h de "washout" para evitar angioedema).
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#7c3aed;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#7c3aed;">REGRA</span>
        <h4 class="mnemonic-title">NUNCA associar IECA + BRA</h4>
      </div>
      <p class="mnemonic-warning">
        <strong>⚠️ Contraindicacao absoluta:</strong> IECA + BRA juntos AUMENTAM risco de hipercalemia, insuficiencia renal e morte (estudo ONTARGET). Use APENAS um deles!
      </p>
    </div>
  </div>

  <div class="bcc-summary">
    <h4 class="bcc-summary-title" style="color:#7f1d1d;">🎯 Quando Escolher Cada Um</h4>
    <div class="bcc-summary-grid">
      <div class="bcc-summary-item" style="background:#fef2f2;border-left-color:#dc2626;">
        <strong style="color:#dc2626;">💊 IECA (1a escolha geral)</strong>
        DM2 + proteinuria, pos-IAM, IC FEr, nefroprotetor, mais barato.
      </div>
      <div class="bcc-summary-item" style="background:#fff7ed;border-left-color:#f59e0b;">
        <strong style="color:#f59e0b;">💊 BRA (1a alternativa)</strong>
        Tossiu com IECA, migranea profilatica (candesartana), pos-IAM alternativo.
      </div>
      <div class="bcc-summary-item" style="background:#fef3c7;border-left-color:#ca8a04;">
        <strong style="color:#92400e;">🚫 Evitar ambos</strong>
        Gestacao (teratogenicos!), estenose bilateral arteria renal, K+ &gt; 5,5.
      </div>
    </div>
  </div>
</div>
"""

# ===== MODULO DIURETICOS =====
DIURETICOS_HTML = """
<!-- ========== MODULO DIURETICOS ========== -->
<div class="bcc-module" id="diureticosModule" style="background:linear-gradient(135deg,#ecfeff 0%,#cffafe 100%);border-color:#06b6d4;">
  <div class="bcc-header">
    <div class="bcc-icon" style="background:linear-gradient(135deg,#06b6d4,#0891b2);">💧</div>
    <div>
      <h3 class="bcc-title" style="color:#0e7490;">Diureticos - Os 3 Grandes Grupos</h3>
      <p class="bcc-subtitle">Tiazidicos, Alca e Poupadores de Potassio</p>
    </div>
  </div>

  <div class="bcc-intro">
    Os <strong>diureticos</strong> sao fundamentais no tratamento da HAS, IC e edema. Dividem-se em <strong>3 grupos principais</strong> baseados no local de acao no nefron. A escolha depende da <strong>patologia</strong>, da <strong>funcao renal</strong> e dos <strong>efeitos colaterais desejados/indesejados</strong>.
  </div>

  <!-- Diagrama do Nefron -->
  <div class="bcc-diagram">
    <div class="bcc-diagram-title" style="color:#0e7490;">🧬 Local de Acao dos Diureticos no Nefron</div>
    <svg viewBox="0 0 700 350" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="nefronGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#fef3c7"/>
          <stop offset="100%" stop-color="#fde68a"/>
        </linearGradient>
      </defs>

      <!-- Tubulo Proximal -->
      <rect x="50" y="50" width="120" height="60" fill="url(#nefronGrad)" stroke="#ca8a04" stroke-width="2" rx="6"/>
      <text x="110" y="85" font-family="Arial" font-size="11" fill="#713f12" text-anchor="middle" font-weight="bold">TUBULO</text>
      <text x="110" y="100" font-family="Arial" font-size="11" fill="#713f12" text-anchor="middle" font-weight="bold">PROXIMAL</text>

      <text x="200" y="85" font-family="Arial" font-size="10" fill="#7c2d12" font-style="italic">Acetazolamida</text>
      <path d="M 180 90 L 220 90" stroke="#7c2d12" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Alca de Henle -->
      <path d="M 170 80 Q 250 30 350 80 Q 400 130 350 180 Q 300 230 200 180 Q 150 130 170 80 Z" fill="none" stroke="#7c3aed" stroke-width="3"/>
      <text x="275" y="120" font-family="Arial" font-size="11" fill="#5b21b6" text-anchor="middle" font-weight="bold">ALCA DE HENLE</text>
      <text x="275" y="220" font-family="Arial" font-size="10" fill="#7c3aed" text-anchor="middle">(porcao ascendente espessa)</text>

      <text x="430" y="140" font-family="Arial" font-size="10" fill="#5b21b6" font-style="italic">Furosemida,</text>
      <text x="430" y="155" font-family="Arial" font-size="10" fill="#5b21b6" font-style="italic">Bumetanida</text>
      <path d="M 410 145 L 370 130" stroke="#5b21b6" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Tubulo Distal -->
      <rect x="450" y="50" width="120" height="60" fill="url(#nefronGrad)" stroke="#ca8a04" stroke-width="2" rx="6"/>
      <text x="510" y="85" font-family="Arial" font-size="11" fill="#713f12" text-anchor="middle" font-weight="bold">TUBULO</text>
      <text x="510" y="100" font-family="Arial" font-size="11" fill="#713f12" text-anchor="middle" font-weight="bold">DISTAL</text>

      <text x="600" y="85" font-family="Arial" font-size="10" fill="#0c4a6e" font-style="italic">HCTZ,</text>
      <text x="600" y="100" font-family="Arial" font-size="10" fill="#0c4a6e" font-style="italic">Clortalidona</text>
      <path d="M 580 95 L 620 95" stroke="#0c4a6e" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Coletor -->
      <rect x="450" y="180" width="120" height="60" fill="url(#nefronGrad)" stroke="#dc2626" stroke-width="2" rx="6"/>
      <text x="510" y="215" font-family="Arial" font-size="11" fill="#7f1d1d" text-anchor="middle" font-weight="bold">DUTO</text>
      <text x="510" y="230" font-family="Arial" font-size="11" fill="#7f1d1d" text-anchor="middle" font-weight="bold">COLETOR</text>

      <text x="600" y="215" font-family="Arial" font-size="10" fill="#991b1b" font-style="italic">Espironolactona,</text>
      <text x="600" y="230" font-family="Arial" font-size="10" fill="#991b1b" font-style="italic">Eplerenona</text>
      <path d="M 580 220 L 620 220" stroke="#991b1b" stroke-width="1" marker-end="url(#arrow)"/>

      <!-- Seta fluxo -->
      <path d="M 50 290 L 650 290" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
      <text x="350" y="310" font-family="Arial" font-size="11" fill="#475569" text-anchor="middle" font-style="italic">Fluxo tubular (filtrado glomerular → urina)</text>

      <!-- Legenda -->
      <rect x="30" y="320" width="640" height="20" fill="#f0fdfa" stroke="#10b981" stroke-width="1" rx="4"/>
      <text x="50" y="335" font-family="Arial" font-size="10" fill="#065f46">💡 Os diureticos agem em pontos diferentes para impedir a reabsorcao de Na+ (e agua).</text>
    </svg>
  </div>

  <!-- Tabela -->
  <div class="bcc-table-wrapper">
    <table class="bcc-table">
      <thead>
        <tr>
          <th>Caracteristica</th>
          <th>🟦 Tiazidicos</th>
          <th>🟪 Alca (Alta potencia)</th>
          <th>🟥 Poupadores K+</th>
        </tr>
      </thead>
      <tbody>
        <tr class="bcc-group-header">
          <td colspan="4">💊 MEDICAMENTOS</td>
        </tr>
        <tr>
          <td><strong>Principais</strong></td>
          <td>HCTZ, Clortalidona, Indapamida</td>
          <td>Furosemida, Bumetanida, Torasemida</td>
          <td>Espironolactona, Eplerenona, Amilorida, Triamtereno</td>
        </tr>
        <tr>
          <td><strong>Potencia</strong></td>
          <td>Moderada</td>
          <td>Alta (a mais potente!)</td>
          <td>Fraca (poupa K+ mas pouco efeito)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">⚙️ MECANISMO</td>
        </tr>
        <tr>
          <td><strong>Onde age</strong></td>
          <td>Tubulo distal (inibe cotransportador Na+-Cl-)</td>
          <td>Alca de Henle (inibe cotransportador Na+-K+-2Cl-)</td>
          <td>Duto coletor (antagoniza aldosterona)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">✅ INDICACOES</td>
        </tr>
        <tr>
          <td><strong>HAS</strong></td>
          <td>1a linha (combinacao com IECA/BRA)</td>
          <td>Na emergencia hipertensiva</td>
          <td>NAO (fraco)</td>
        </tr>
        <tr>
          <td><strong>IC descompensada</strong></td>
          <td>Fraco (HCTZ pode ser usado em IC leve)</td>
          <td>1a escolha (Furosemida IV)</td>
          <td>Espironolactona (IC FEr, antagonista aldosterona)</td>
        </tr>
        <tr>
          <td><strong>Edema pulmonar</strong></td>
          <td>Ineficaz</td>
          <td>1a escolha absoluta!</td>
          <td>Ineficaz</td>
        </tr>
        <tr>
          <td><strong>DRC com TFG &lt; 30</strong></td>
          <td>Ineficaz (tiazidicos perdem efeito)</td>
          <td>Ainda funciona (1a escolha)</td>
          <td>Ineficaz</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">⚠️ EFEITOS ADVERSOS</td>
        </tr>
        <tr>
          <td><strong>K+ serico</strong></td>
          <td>↓ Hipopotassemia (cuidado arritmias!)</td>
          <td>↓ Hipopotassemia severa</td>
          <td>↑ Hipercalemia (risco de morte!)</td>
        </tr>
        <tr>
          <td><strong>Glicemia</strong></td>
          <td>↑ Hiperglicemia (piora DM)</td>
          <td>↓ Hipoglicemia leve</td>
          <td>Sem efeito direto</td>
        </tr>
        <tr>
          <td><strong>Acido urico</strong></td>
          <td>↑ Hiperuricemia (crise de gota!)</td>
          <td>↑ Hiperuricemia leve</td>
          <td>Sem efeito</td>
        </tr>
        <tr>
          <td><strong>Outros</strong></td>
          <td>Dislipidemia, impotencia</td>
          <td>Ototoxicidade (doses altas), caimbra</td>
          <td>Ginecomastia (espironolactona)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">💊 POSOLOGIA TIPICA</td>
        </tr>
        <tr>
          <td><strong>Dose habitual</strong></td>
          <td>HCTZ 25mg/dia ou Clortalidona 12,5-25mg/dia</td>
          <td>Furosemida 20-80mg/dia (max 600mg)</td>
          <td>Espironolactona 25-100mg/dia</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mnemonicos -->
  <div class="bcc-mnemonics" style="background:linear-gradient(135deg,#dbeafe 0%,#bfdbfe 100%);border:2px dashed #2563eb;">
    <h3 class="bcc-mnemonics-title" style="color:#1e3a8a;">🧠 Mnemonicos dos Diureticos</h3>

    <div class="mnemonic-card" style="border-color:#0891b2;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#0891b2;">REGRA 1</span>
        <h4 class="mnemonic-title">"OH DALT" - Local de acao (de cima para baixo no nefron)</h4>
      </div>
      <p class="mnemonic-content">
        <strong>O</strong>smosis (proxima) → <strong>H</strong>enle (Alca, mais potente) → <strong>D</strong>istal (Tiazidicos) → <strong>A</strong>ldosterona (Poupadores) → <strong>L</strong>i → <strong>T</strong>udo
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Quanto mais proximal, mais potente</strong> (ate Henle). Poupadores sao sempre fracos.
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#7c3aed;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#7c3aed;">REGRA 2</span>
        <h4 class="mnemonic-title">Tiazidicos = Tiazida + Top de linha para HAS</h4>
      </div>
      <p class="mnemonic-content">
        Para HAS, <strong>tiazidicos sao a 1a escolha</strong> (junto com IECA/BRA). Sao faceis de tomar (1x/dia), baratos e eficazes. Cuidado com hipopotassemia.
      </p>
    </div>

    <div class="mnemonic-card" style="border-color:#dc2626;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#dc2626;">REGRA 3</span>
        <h4 class="mnemonic-title">Espironolactona = Espirilo (que gira) o K+</h4>
      </div>
      <p class="mnemonic-content">
        Espirilo<strong>LACTONA</strong> &lt;-- Lactona = Loiro de K+ (poupa). Mas cuidado: se combinar com IECA/BRA, hipercalemia severa.
      </p>
      <div class="mnemonic-warning">
        <strong>⚠️ REGRA DE OURO:</strong> Espironolactona + IECA = HIPERCALEMIA GRAVE! Sempre monitorar K+ serico.
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#f59e0b;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#f59e0b;">REGRA 4</span>
        <h4 class="mnemonic-title">"Furosemida: Fun-osa" - A mais potente</h4>
      </div>
      <p class="mnemonic-content">
        <strong>Furosemida = FURO de agua</strong>. E a mais potente (ate 25% do Na+ filtrado). Reservar para <strong>edema agudo de pulmao, IC descompensada</strong>.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Tiazidicos perdem efeito com TFG &lt; 30 mL/min. Furosemida AINDA FUNCIONA.</strong> Por isso DRC avancada = sempre alca.
      </div>
    </div>
  </div>

  <div class="bcc-summary">
    <h4 class="bcc-summary-title" style="color:#0e7490;">🎯 Quando Escolher Cada Diuretico</h4>
    <div class="bcc-summary-grid">
      <div class="bcc-summary-item" style="background:#fef3c7;border-left-color:#ca8a04;">
        <strong>HAS 1a linha</strong>
        HCTZ 12,5-25mg + IECA/BRA. Barato, 1x/dia.
      </div>
      <div class="bcc-summary-item" style="background:#f3e8ff;border-left-color:#7c3aed;">
        <strong>IC descompensada</strong>
        Furosemida 40-80mg IV + Espironolactona 25-50mg.
      </div>
      <div class="bcc-summary-item" style="background:#fee2e2;border-left-color:#dc2626;">
        <strong>Edema pulmonar agudo</strong>
        Furosemida 40-80mg IV (ataque). Posologia agressiva.
      </div>
      <div class="bcc-summary-item" style="background:#fef2f2;border-left-color:#dc2626;">
        <strong>DRC avancada (TFG &lt; 30)</strong>
        SOMENTE Furosemida (tiazidicos nao funcionam mais).
      </div>
      <div class="bcc-summary-item" style="background:#fce7f3;border-left-color:#be185d;">
        <strong>Hiperaldosteronismo</strong>
        Espironolactona (bloqueia receptor de aldosterona).
      </div>
      <div class="bcc-summary-item" style="background:#d1fae5;border-left-color:#10b981;">
        <strong>Gota / hiperuricemia</strong>
        EVITAR tiazidicos e alca. Usar poupador (Losartan tbm ajuda).
      </div>
    </div>
  </div>
</div>
"""

# ===== MODULO ARA II (ALISQUIRENO) =====
ARA_II_HTML = """
<!-- ========== MODULO ARA II - ALISQUIRENO ========== -->
<div class="bcc-module" id="araIIModule" style="background:linear-gradient(135deg,#f3e8ff 0%,#e9d5ff 100%);border-color:#a855f7;">
  <div class="bcc-header">
    <div class="bcc-icon" style="background:linear-gradient(135deg,#a855f7,#7e22ce);">💎</div>
    <div>
      <h3 class="bcc-title" style="color:#581c87;">ARA II - O Novo Bloqueador Direto da Renina</h3>
      <p class="bcc-subtitle">Alisquireno: o primeiro inibidor direto da renina</p>
    </div>
  </div>

  <div class="bcc-intro">
    Os <strong>IECA</strong> bloqueiam a ECA, e os <strong>BRA</strong> bloqueiam o receptor AT1. Mas e se bloqueassemos a <strong>renina diretamente</strong>? O <strong>Alisquireno</strong> e o representante de uma nova classe: <strong>Inibidores Diretos da Renina (IDR)</strong>. Foi o primeiro anti-hipertensivo novo em uma decada, mas seu uso clinico e limitado.
  </div>

  <!-- Mecanismo -->
  <div class="bcc-diagram">
    <div class="bcc-diagram-title" style="color:#581c87;">🧬 Onde os ARA II Atuam no SRAA</div>
    <svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg">

      <!-- Renina -->
      <rect x="30" y="100" width="90" height="50" fill="#fef3c7" stroke="#ca8a04" stroke-width="2" rx="6"/>
      <text x="75" y="125" font-family="Arial" font-size="11" fill="#713f12" text-anchor="middle" font-weight="bold">RENINA</text>
      <text x="75" y="140" font-family="Arial" font-size="9" fill="#92400e" text-anchor="middle">(do rim)</text>

      <!-- Seta -->
      <line x1="125" y1="125" x2="180" y2="125" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

      <!-- Angiotensinogenio -->
      <rect x="180" y="100" width="100" height="50" fill="#fde68a" stroke="#ca8a04" stroke-width="2" rx="6"/>
      <text x="230" y="125" font-family="Arial" font-size="10" fill="#713f12" text-anchor="middle">Angiotensinogenio</text>
      <text x="230" y="140" font-family="Arial" font-size="9" fill="#92400e" text-anchor="middle">(do figado)</text>

      <!-- Seta -->
      <line x1="285" y1="125" x2="335" y2="125" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

      <!-- Angiotensina I -->
      <rect x="335" y="100" width="90" height="50" fill="#fbcfe8" stroke="#be185c" stroke-width="2" rx="6"/>
      <text x="380" y="130" font-family="Arial" font-size="10" fill="#831843" text-anchor="middle" font-weight="bold">ANGIOTENSINA I</text>

      <!-- ECA -->
      <rect x="430" y="100" width="60" height="50" fill="#dc2626" stroke="#7f1d1d" stroke-width="2" rx="6"/>
      <text x="460" y="130" font-family="Arial" font-size="11" fill="white" text-anchor="middle" font-weight="bold">ECA</text>

      <!-- Seta -->
      <line x1="495" y1="125" x2="530" y2="125" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>

      <!-- Angiotensina II -->
      <rect x="530" y="100" width="100" height="50" fill="#7f1d1d" stroke="#450a0a" stroke-width="2" rx="6"/>
      <text x="580" y="130" font-family="Arial" font-size="10" fill="white" text-anchor="middle" font-weight="bold">ANGIOTENSINA II</text>

      <!-- Receptor AT1 -->
      <rect x="640" y="100" width="60" height="50" fill="#fbbf24" stroke="#92400e" stroke-width="2" rx="6"/>
      <text x="670" y="125" font-family="Arial" font-size="11" fill="#7f1d1d" text-anchor="middle" font-weight="bold">AT1</text>
      <text x="670" y="140" font-family="Arial" font-size="8" fill="#7f1d1d" text-anchor="middle">(receptor)</text>

      <!-- Efeitos finais -->
      <rect x="250" y="200" width="400" height="35" fill="#fee2e2" stroke="#dc2626" stroke-width="2" rx="6"/>
      <text x="450" y="222" font-family="Arial" font-size="11" fill="#991b1b" text-anchor="middle" font-weight="bold">VASOCONSTRICAO + RETENCAO DE Na+ + ALDOSTERONA</text>

      <!-- Setas para efeitos -->
      <line x1="670" y1="150" x2="450" y2="195" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow)"/>

      <!-- Locais de acao das drogas -->
      <!-- IECA (bloqueia ECA) -->
      <rect x="455" y="155" width="40" height="20" fill="#dc2626" stroke="#7f1d1d" stroke-width="1" rx="2"/>
      <text x="475" y="168" font-family="Arial" font-size="9" fill="white" text-anchor="middle">IECA</text>

      <!-- BRA (bloqueia AT1) -->
      <rect x="660" y="155" width="40" height="20" fill="#dc2626" stroke="#7f1d1d" stroke-width="1" rx="2"/>
      <text x="680" y="168" font-family="Arial" font-size="9" fill="white" text-anchor="middle">BRA</text>

      <!-- ARA II / Alisquireno (bloqueia renina) -->
      <rect x="50" y="155" width="80" height="20" fill="#a855f7" stroke="#581c87" stroke-width="1" rx="2"/>
      <text x="90" y="168" font-family="Arial" font-size="9" fill="white" text-anchor="middle" font-weight="bold">ALISQUIRENO</text>

      <!-- Legenda -->
      <text x="350" y="40" font-family="Arial" font-size="13" fill="#581c87" text-anchor="middle" font-weight="bold">CASCATA DO SRAA - Onde cada droga age</text>
    </svg>
  </div>

  <!-- Tabela -->
  <div class="bcc-table-wrapper">
    <table class="bcc-table">
      <thead>
        <tr>
          <th>Caracteristica</th>
          <th>IECA</th>
          <th>BRA</th>
          <th>ARA II (Alisquireno)</th>
        </tr>
      </thead>
      <tbody>
        <tr class="bcc-group-header">
          <td colspan="4">⚙️ MECANISMO</td>
        </tr>
        <tr>
          <td><strong>Ponto de acao</strong></td>
          <td>Bloqueia ECA (enzima conversora)</td>
          <td>Bloqueia receptor AT1</td>
          <td>Bloqueia renina (etapa inicial)</td>
        </tr>
        <tr>
          <td><strong>Bradicinina</strong></td>
          <td>Aumenta (causa tosse)</td>
          <td>NAO afeta</td>
          <td>NAO afeta</td>
        </tr>
        <tr>
          <td><strong>Reducao de Angiotensina II</strong></td>
          <td>Sim (total)</td>
          <td>Sim (apenas efeito no AT1)</td>
          <td>Sim (total, na producao)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">✅ VANTAGENS TEORICAS</td>
        </tr>
        <tr>
          <td><strong>Sem tosse</strong></td>
          <td>NÃO (10-20% tem tosse)</td>
          <td>Sim</td>
          <td>Sim</td>
        </tr>
        <tr>
          <td><strong>Reducao de PRA</strong></td>
          <td>Aumenta PRA (reativa SRAA)</td>
          <td>Aumenta PRA</td>
          <td>REDUZ PRA (unico!)</td>
        </tr>
        <tr>
          <td><strong>Anti-fibrose</strong></td>
          <td>Alguma</td>
          <td>Alguma</td>
          <td>Teoricamente maior</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">⚠️ POR QUE NAO E POPULAR</td>
        </tr>
        <tr>
          <td><strong>Evidencias clinicas</strong></td>
          <td>FORTISSIMAS (muitos estudos)</td>
          <td>FORTISSIMAS</td>
          <td>FRACAS (estudos ALTITUDE e ASTRONAUT negativos)</td>
        </tr>
        <tr>
          <td><strong>Custo</strong></td>
          <td>Barato (genericos)</td>
          <td>Barato (genericos)</td>
          <td>CARO (R$ 200-400/mes)</td>
        </tr>
        <tr>
          <td><strong>Posologia</strong></td>
          <td>1-2x/dia</td>
          <td>1x/dia</td>
          <td>1x/dia</td>
        </tr>
        <tr>
          <td><strong>Combinacao IECA/BRA</strong></td>
          <td>Proibido (com outro)</td>
          <td>Proibido (com IECA)</td>
          <td>PROIBIDO com IECA/BRA (risco hipercalemia)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">📋 STATUS ATUAL</td>
        </tr>
        <tr>
          <td><strong>Recomendacao</strong></td>
          <td>1a escolha</td>
          <td>1a escolha</td>
          <td>NÃO recomendado como rotina</td>
        </tr>
        <tr>
          <td><strong>Uso atual</strong></td>
          <td>Muito comum</td>
          <td>Muito comum</td>
          <td>Raramente usado (reservado)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mnemonicos -->
  <div class="bcc-mnemonics" style="background:linear-gradient(135deg,#f3e8ff 0%,#e9d5ff 100%);border:2px dashed #a855f7;">
    <h3 class="bcc-mnemonics-title" style="color:#581c87;">🧠 Dicas de Memorizacao ARA II</h3>

    <div class="mnemonic-card" style="border-color:#a855f7;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#a855f7;">REGRA 1</span>
        <h4 class="mnemonic-title">"ALI = INICIO" - Age no comeco da cascata</h4>
      </div>
      <p class="mnemonic-content">
        <strong>Alisquireno</strong> bloqueia a <strong>renina</strong>, que e a PRIMEIRA enzima da cascata. Por isso, teoricamente e o mais "radical" - corta o problema pela raiz.
      </p>
    </div>

    <div class="mnemonic-card" style="border-color:#dc2626;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#dc2626;">REALIDADE</span>
        <h4 class="mnemonic-title">"ALI esqueceu o caminho" - Perdeu-se na pratica</h4>
      </div>
      <p class="mnemonic-warning">
        <strong>⚠️ Por que nao e usado:</strong> Estudo ALTITUDE (2012) mostrou AUMENTO de eventos adversos com Alisquireno + IECA/BRA em diabeticos. Estudo ASTRONAUT (2011) suspendeu por falta de eficacia. Por isso, NAO combine com IECA ou BRA!
      </p>
    </div>
  </div>

  <div class="bcc-summary">
    <h4 class="bcc-summary-title" style="color:#581c87;">🎯 Resumo dos Inibidores do SRAA</h4>
    <div class="bcc-summary-grid">
      <div class="bcc-summary-item" style="background:#fee2e2;border-left-color:#dc2626;">
        <strong style="color:#dc2626;">IECA (-pril)</strong>
        Primeira linha, pos-IAM, IC, DM proteinuria. Efeito adverso: tosse.
      </div>
      <div class="bcc-summary-item" style="background:#fef3c7;border-left-color:#ca8a04;">
        <strong style="color:#ca8a04;">BRA (-sartana)</strong>
        Primeira linha, alternativa a IECA se tosse. Mesma eficacia.
      </div>
      <div class="bcc-summary-item" style="background:#f3e8ff;border-left-color:#a855f7;">
        <strong style="color:#a855f7;">ARA II (-quireno)</strong>
        Uso raro. NUNCA combine com IECA/BRA. Caro, sem evidencias fortes.
      </div>
    </div>
  </div>
</div>
"""

# ===== MODULO BETABLOQUEADORES =====
BETA_BLOQUEADORES_HTML = """
<!-- ========== MODULO BETABLOQUEADORES ========== -->
<div class="bcc-module" id="betaBloqModule" style="background:linear-gradient(135deg,#fef3c7 0%,#fed7aa 100%);border-color:#f97316;">
  <div class="bcc-header">
    <div class="bcc-icon" style="background:linear-gradient(135deg,#f97316,#ea580c);">❤️</div>
    <div>
      <h3 class="bcc-title" style="color:#7c2d12;">Betabloqueadores - Cardio vs Nao-Cardio</h3>
      <p class="bcc-subtitle">Seletividade beta-1: a chave da diferenca</p>
    </div>
  </div>

  <div class="bcc-intro">
    Os <strong>Betabloqueadores (BB)</strong> sao amplos em cardiologia: HAS, IC, pos-IAM, arritmias, angina. Mas diferem muito em <strong>seletividade</strong> (beta-1 ou nao) e <strong>atividade simpatomimetica intrinseca (ASI)</strong>. A escolha depende das <strong>comorbidades</strong> do paciente.
  </div>

  <!-- Tabela -->
  <div class="bcc-table-wrapper">
    <table class="bcc-table">
      <thead>
        <tr>
          <th>Caracteristica</th>
          <th>🟢 Cardiosseletivos (beta-1)</th>
          <th>🟠 Nao-seletivos (beta-1 e beta-2)</th>
          <th>🟣 Com ASI</th>
        </tr>
      </thead>
      <tbody>
        <tr class="bcc-group-header">
          <td colspan="4">💊 MEDICAMENTOS</td>
        </tr>
        <tr>
          <td><strong>Principais</strong></td>
          <td>Atenolol, Metoprolol, Bisoprolol, Nebivolol, Esmolol</td>
          <td>Propranolol, Nadolol, Timolol, Carvedilol, Labetalol</td>
          <td>Pindolol, Acebutolol</td>
        </tr>
        <tr>
          <td><strong>Seletividade</strong></td>
          <td>APENAS beta-1 (coracao)</td>
          <td>beta-1 E beta-2 (pulmao + metabolismo)</td>
          <td>Varia</td>
        </tr>
        <tr>
          <td><strong>ASI</strong></td>
          <td>Geralmente NAO</td>
          <td>Geralmente NAO</td>
          <td>SIM (atividade simpatomimetica intrinseca)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">✅ INDICACOES ESPECIAIS</td>
        </tr>
        <tr>
          <td><strong>HAS</strong></td>
          <td>Sim (jovens, HAS + IC)</td>
          <td>Sim (HAS + enxaqueca, HAS + tremor)</td>
          <td>Sim (HAS em atletas, bradicardia basal)</td>
        </tr>
        <tr>
          <td><strong>IC FEr reduzida</strong></td>
          <td>Bisoprolol, Metoprolol succinato, Nebivolol (3 aprovados!)</td>
          <td>Carvedilol (tambem aprovado)</td>
          <td>NAO</td>
        </tr>
        <tr>
          <td><strong>Pos-IAM</strong></td>
          <td>Metoprolol, Atenolol</td>
          <td>Carvedilol, Propranolol</td>
          <td>NAO</td>
        </tr>
        <tr>
          <td><strong>Angina</strong></td>
          <td>Atenolol, Metoprolol</td>
          <td>Propranolol</td>
          <td>NAO</td>
        </tr>
        <tr>
          <td><strong>Enxaqueca (profilaxia)</strong></td>
          <td>Metoprolol</td>
          <td>Propranolol (mais eficaz!)</td>
          <td>—</td>
        </tr>
        <tr>
          <td><strong>Hipertireoidismo</strong></td>
          <td>Atenolol</td>
          <td>Propranolol (melhor!)</td>
          <td>—</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">⚠️ CONTRAINDICACOES ESPECIAIS</td>
        </tr>
        <tr>
          <td><strong>Asma / DPOC</strong></td>
          <td>Relativa (usar com cuidado)</td>
          <td>ABSOLUTA (broncoconstricao!)</td>
          <td>ABSOLUTA</td>
        </tr>
        <tr>
          <td><strong>DM insulinodependente</strong></td>
          <td>Relativa</td>
          <td>ABSOLUTA (mascara hipoglicemia!)</td>
          <td>ABSOLUTA</td>
        </tr>
        <tr>
          <td><strong>Doenca vascular periferica</strong></td>
          <td>Relativa</td>
          <td>ABSOLUTA (vasoconstricao!)</td>
          <td>ABSOLUTA</td>
        </tr>
        <tr>
          <td><strong>Bradicardia / BAV</strong></td>
          <td colspan="3" style="text-align:center;color:#dc2626;font-weight:700;">⚠️ ABSOLUTA - Todos os BB!</td>
        </tr>
        <tr>
          <td><strong>IC descompensada</strong></td>
          <td colspan="3" style="text-align:center;color:#dc2626;font-weight:700;">⚠️ ABSOLUTA - Iniciar so apos compensacao</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="4">💊 POSOLOGIA TIPICA</td>
        </tr>
        <tr>
          <td><strong>HAS / IC</strong></td>
          <td>Bisoprolol 2,5-10mg 1x/dia</td>
          <td>Carvedilol 6,25-25mg 2x/dia</td>
          <td>Pindolol 5-30mg/dia</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mnemonicos -->
  <div class="bcc-mnemonics" style="background:linear-gradient(135deg,#fed7aa 0%,#fb923c 100%);border:2px dashed #c2410c;">
    <h3 class="bcc-mnemonics-title" style="color:#7c2d12;">🧠 Mnemonicos dos Betabloqueadores</h3>

    <div class="mnemonic-card" style="border-color:#10b981;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#10b981;">REGRA 1</span>
        <h4 class="mnemonic-title">"Cardiosseletivo = CORacao SEGURO" (beta-1)</h4>
      </div>
      <p class="mnemonic-content">
        Cardiosseletivos agem APENAS no coracao. Sao mais seguros em <strong>asma leve, DPOC leve, DM</strong>. Mas em doses altas, perdem seletividade.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Dica:</strong> Suspender 48h antes de cirurgia eletiva? NAO e mais recomendado (estudo POISE). Mas suspender antes de ergometria? SIM (afeta FC).
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#f97316;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#f97316;">REGRA 2</span>
        <h4 class="mnemonic-title">"Nao-seletivo = Nao use em ASMA / DM"</h4>
      </div>
      <p class="mnemonic-content">
        Bloqueiam beta-2 (broncodilatacao). Em <strong>asma</strong>, causam broncoespasmo grave. Em <strong>DM insulinodependente</strong>, mascaram hipoglicemia (taquicardia, tremor).
      </p>
      <div class="mnemonic-warning">
        <strong>⚠️ DIABETICO tipo 1: NUNCA use propranolol!</strong> Se hipoglicemia, o paciente nao sente e pode ir a obito.
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#7c3aed;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#7c3aed;">REGRA 3</span>
        <h4 class="mnemonic-title">"Carvedilol = CarVEDilol = 3 acoes (alfa, beta-1, beta-2)"</h4>
      </div>
      <p class="mnemonic-content">
        O <strong>Carvedilol</strong> e o unico BB com <strong>acao alfa-1 bloqueadora adicional</strong>. Por isso, e vasodilatador tambem. Excelente para IC + HAS.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Os 4 BBs aprovados para IC:</strong> Bisoprolol, Carvedilol, Metoprolol succinato, Nebivolol. <strong>Nebivolol</strong> tambem libera oxido nitrico (vasodilatacao).
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#dc2626;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#dc2626;">REGRA 4</span>
        <h4 class="mnemonic-title">"ASI = nao tem taquicardia reflexa"</h4>
      </div>
      <p class="mnemonic-content">
        Betabloqueadores com <strong>ASI (Atividade Simpatomimetica Intrinseca)</strong> nao causam bradicardia severa em repouso. Sao bons para <strong>atletas</strong> (FC basal baixa) ou <strong>jovens ansiosos</strong> com taquicardia.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Porem:</strong> ASI NAO confere beneficio prognostico em pos-IAM ou IC. Por isso, em IC, use <strong>SEM ASI</strong> (bisoprolol, carvedilol, metoprolol succ).
      </div>
    </div>
  </div>

  <!-- Desafio -->
  <div class="bcc-challenge">
    <h3 class="bcc-challenge-title">💡 Desafio: Paciente Complexo</h3>

    <div class="bcc-challenge-text">
      <strong>Caso:</strong> Mulher 65 anos, HAS, IC com FEr 35%, DM2, DPOC leve (VEF1 70%). Vem com prescricao de <strong>Propranolol 40mg 3x/dia</strong> para HAS. Esta correto?
    </div>

    <div class="bcc-challenge-question">
      ❓ O que voce mudaria? Qual BB escolheria e por que?
    </div>

    <button class="bcc-challenge-btn" onclick="revealBetaChallenge()">
      💡 Ver Resposta
    </button>

    <div class="bcc-challenge-answer" id="betaChallengeAnswer">
      <strong>❌ PROPRANOLOL ESTA ERRADO neste paciente!</strong><br><br>

      <strong>Problemas:</strong><br>
      1. <strong>Nao-seletivo</strong> em paciente com DPOC: pode causar broncoespasmo<br>
      2. <strong>Nao-seletivo</strong> em DM2: mascara sintomas de hipoglicemia<br>
      3. <strong>Nao tem indicacao para IC</strong> (somente bisoprolol, carvedilol, metoprolol succ ou nebivolol)<br>
      4. <strong>3x/dia</strong> e inconveniente (BB modernos sao 1-2x/dia)<br><br>

      <strong>✅ MELHOR ESCOLHA: Bisoprolol 2,5-5mg 1x/dia</strong><br><br>

      <strong>Por que?</strong><br>
      - <strong>Cardiosseletivo (beta-1)</strong>: menor risco em DPOC leve e DM2<br>
      - <strong>Aprovado para IC FEr reduzida</strong>: reduz mortalidade (estudo CIBIS-II)<br>
      - <strong>1x/dia</strong>: melhor adesao<br>
      - Titulacao gradual (iniciar com 1,25mg, dobrar a cada 2 semanas)<br><br>

      <strong>Alternativa:</strong> Carvedilol 6,25mg 2x/dia (tambem aprovado, melhor perfil metabolico).
    </div>
  </div>

  <div class="bcc-summary">
    <h4 class="bcc-summary-title" style="color:#7c2d12;">🎯 Quando Escolher Cada Betabloqueador</h4>
    <div class="bcc-summary-grid">
      <div class="bcc-summary-item" style="background:#d1fae5;border-left-color:#10b981;">
        <strong style="color:#10b981;">Bisoprolol</strong>
        IC FEr, HAS + IC. 1x/dia. Cardiosseletivo.
      </div>
      <div class="bcc-summary-item" style="background:#fed7aa;border-left-color:#f97316;">
        <strong style="color:#f97316;">Carvedilol</strong>
        IC FEr, pos-IAM. 2x/dia. Alfa + beta. Vasodilatador.
      </div>
      <div class="bcc-summary-item" style="background:#dbeafe;border-left-color:#2563eb;">
        <strong style="color:#2563eb;">Metoprolol succinato</strong>
        IC FEr, pos-IAM, angina. 1x/dia. Cardiosseletivo.
      </div>
      <div class="bcc-summary-item" style="background:#f3e8ff;border-left-color:#7c3aed;">
        <strong style="color:#7c3aed;">Nebivolol</strong>
        IC FEr, HAS + dislipidemia. Libera oxido nitrico.
      </div>
      <div class="bcc-summary-item" style="background:#fee2e2;border-left-color:#dc2626;">
        <strong style="color:#dc2626;">Propranolol</strong>
        HAS + enxaqueca, HAS + tremor, hipertireoidismo. Evitar asma.
      </div>
      <div class="bcc-summary-item" style="background:#fce7f3;border-left-color:#be185d;">
        <strong style="color:#be185d;">Pindolol (ASI)</strong>
        Jovens atletas, ansiedade com taquicardia. NAO para IC.
      </div>
    </div>
  </div>
</div>

<script>
// ========== DESAFIO BETA ==========
function revealBetaChallenge() {
  const answer = document.getElementById('betaChallengeAnswer');
  if (answer) {
    answer.classList.add('show');
    answer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (typeof addXP === 'function') addXP(30);
  }
}

// Hook para mostrar modulos automaticamente
const _origOpenCourseMods = window.openCourse;
if (typeof _origOpenCourseMods === 'function') {
  window.openCourse = function(cursoId) {
    _origOpenCourseMods.apply(this, arguments);
    if (cursoId === 'antihipertensivos') {
      setTimeout(() => {
        // Mostra todos os 5 modulos
        ['bccModule', 'iecaBraModule', 'diureticosModule', 'araIIModule', 'betaBloqModule'].forEach((id, i) => {
          setTimeout(() => {
            const el = document.getElementById(id);
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, i * 500);
        });
      }, 1000);
    }
  };
}
</script>
"""


def main():
    output = Path("/workspace/output")

    arquivos = [
        "dashboard-auxfarmacia-FREE.html",
        "dashboard-auxfarmacia-PRO.html",
        "dashboard-auxfarmacia-PREMIUM.html",
        "dashboard-auxfarmacia-ENTERPRISE.html",
        "dashboard-auxfarmacia.html",
        "dashboard-auxfarmacia-educativo.html",
    ]

    print("=" * 60)
    print("💊 Adicionando 4 modulos complementares:")
    print("   1. IECA vs BRA")
    print("   2. Diureticos (3 grupos)")
    print("   3. ARA II (Alisquireno)")
    print("   4. Betabloqueadores")
    print("=" * 60)

    modulos = [
        ('id="iecaBraModule"', IECA_BRA_HTML),
        ('id="diureticosModule"', DIURETICOS_HTML),
        ('id="araIIModule"', ARA_II_HTML),
        ('id="betaBloqModule"', BETA_BLOQUEADORES_HTML),
    ]

    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        for marker, content in modulos:
            if marker not in html:
                html = html.replace('</body>', content + '\n</body>', 1)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ {fname}")

    print()
    print("=" * 60)
    print("✅ Todos os modulos adicionados!")
    print("=" * 60)


if __name__ == "__main__":
    main()