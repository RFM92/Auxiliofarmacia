#!/usr/bin/env python3
"""
Adiciona 2 novos modulos:
1. Antiarritmicos (Classes I-IV de Vaughan-Williams)
2. Anticoagulantes (Warfarina, DOACs, Heparina)
"""
import re
from pathlib import Path

# ===== MODULO ANTIARRIITMICOS =====
ANTIARRITMICOS_HTML = """
<!-- ========== MODULO ANTIARRIITMICOS ========== -->
<div class="bcc-module" id="antiarrModule" style="background:linear-gradient(135deg,#fce7f3 0%,#fbcfe8 100%);border-color:#ec4899;">
  <div class="bcc-header">
    <div class="bcc-icon" style="background:linear-gradient(135deg,#ec4899,#be185d);">⚡</div>
    <div>
      <h3 class="bcc-title" style="color:#831843;">Antiarritmicos - Classificacao de Vaughan-Williams</h3>
      <p class="bcc-subtitle">Classes I, II, III e IV - Onde cada uma age</p>
    </div>
  </div>

  <div class="bcc-intro">
    Os <strong>antiarritmicos</strong> sao classificados em <strong>4 classes (I-IV)</strong> baseadas no seu mecanismo de acao no potencial de acao cardiaco. A classe I e subdividida em <strong>IA, IB e IC</strong>. Cada classe age em uma fase especifica do potencial de acao, sendo essencial conhecer para escolher a droga certa para cada arritmia.
  </div>

  <!-- Diagrama do Potencial de Acao -->
  <div class="bcc-diagram">
    <div class="bcc-diagram-title" style="color:#831843;">🧬 Potencial de Acao do Cardiomiocito - Onde cada classe age</div>
    <svg viewBox="0 0 700 350" xmlns="http://www.w3.org/2000/svg">
      <!-- Eixos -->
      <line x1="50" y1="300" x2="650" y2="300" stroke="#475569" stroke-width="2"/>
      <line x1="50" y1="50" x2="50" y2="300" stroke="#475569" stroke-width="2"/>
      <text x="350" y="335" font-family="Arial" font-size="11" fill="#475569" text-anchor="middle">Tempo (ms)</text>
      <text x="20" y="175" font-family="Arial" font-size="11" fill="#475569" text-anchor="middle" transform="rotate(-90 20 175)">mV</text>

      <!-- Curva do potencial de acao -->
      <path d="M 60 280 L 80 280 L 100 100 L 130 90 L 200 110 L 350 230 L 500 270 L 600 280" fill="none" stroke="#1e293b" stroke-width="3"/>

      <!-- Fases -->
      <!-- Fase 0 (Despolarizacao rapida - Na+) -->
      <rect x="60" y="50" width="80" height="250" fill="#fef3c7" opacity="0.4"/>
      <text x="100" y="40" font-family="Arial" font-size="12" fill="#92400e" text-anchor="middle" font-weight="bold">FASE 0</text>
      <text x="100" y="55" font-family="Arial" font-size="9" fill="#92400e" text-anchor="middle">Despolarizacao (Na+)</text>

      <!-- Fase 1 (Repolarizacao inicial - K+) -->
      <rect x="140" y="50" width="40" height="250" fill="#fde68a" opacity="0.4"/>
      <text x="160" y="40" font-family="Arial" font-size="11" fill="#92400e" text-anchor="middle" font-weight="bold">FASE 1</text>

      <!-- Fase 2 (Plateau - Ca2+) -->
      <rect x="180" y="50" width="170" height="250" fill="#fbcfe8" opacity="0.4"/>
      <text x="265" y="40" font-family="Arial" font-size="11" fill="#831843" text-anchor="middle" font-weight="bold">FASE 2</text>
      <text x="265" y="55" font-family="Arial" font-size="9" fill="#831843" text-anchor="middle">Plateau (Ca2+)</text>

      <!-- Fase 3 (Repolarizacao - K+) -->
      <rect x="350" y="50" width="160" height="250" fill="#e9d5ff" opacity="0.4"/>
      <text x="430" y="40" font-family="Arial" font-size="11" fill="#581c87" text-anchor="middle" font-weight="bold">FASE 3</text>
      <text x="430" y="55" font-family="Arial" font-size="9" fill="#581c87" text-anchor="middle">Repolarizacao (K+)</text>

      <!-- Fase 4 (Repouso) -->
      <rect x="510" y="50" width="140" height="250" fill="#dbeafe" opacity="0.4"/>
      <text x="580" y="40" font-family="Arial" font-size="11" fill="#1e3a8a" text-anchor="middle" font-weight="bold">FASE 4</text>
      <text x="580" y="55" font-family="Arial" font-size="9" fill="#1e3a8a" text-anchor="middle">Repouso (automaticidade)</text>

      <!-- Setas indicando onde cada classe age -->
      <!-- Classe I (bloqueia Na+ - Fase 0) -->
      <rect x="80" y="120" width="60" height="20" fill="#dc2626" rx="3"/>
      <text x="110" y="135" font-family="Arial" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE I</text>

      <!-- Classe IV (bloqueia Ca2+ - Fase 2) -->
      <rect x="240" y="160" width="60" height="20" fill="#f59e0b" rx="3"/>
      <text x="270" y="175" font-family="Arial" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE IV</text>

      <!-- Classe III (bloqueia K+ - Fase 3) -->
      <rect x="400" y="200" width="60" height="20" fill="#7c3aed" rx="3"/>
      <text x="430" y="215" font-family="Arial" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE III</text>

      <!-- Classe II (beta-bloq - Fase 4) -->
      <rect x="540" y="240" width="60" height="20" fill="#0ea5e9" rx="3"/>
      <text x="570" y="255" font-family="Arial" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE II</text>

      <!-- Legenda -->
      <text x="350" y="320" font-family="Arial" font-size="9" fill="#64748b" text-anchor="middle">Classe I (Na+) | Classe II (beta) | Classe III (K+) | Classe IV (Ca2+)</text>
    </svg>
  </div>

  <!-- Tabela -->
  <div class="bcc-table-wrapper">
    <table class="bcc-table">
      <thead>
        <tr>
          <th>Classe</th>
          <th>Mecanismo</th>
          <th>Drogas</th>
          <th>Indicacao Principal</th>
          <th>Efeitos Adversos</th>
        </tr>
      </thead>
      <tbody>
        <tr class="bcc-group-header">
          <td colspan="5">🟥 CLASSE I - BLOQUEADORES DE SODIO (Na+)</td>
        </tr>
        <tr>
          <td><strong>IA</strong></td>
          <td>Bloqueio moderado de Na+, prolonga duracao do potencial de acao</td>
          <td>Quinidina, Procainamida, Disopiramida</td>
          <td>Taquicardia ventricular, FA</td>
          <td>Quinidina: cinchonismo, torsades<br>Procainamida: lupus induzido<br>Disopiramida: anticolinergico</td>
        </tr>
        <tr>
          <td><strong>IB</strong></td>
          <td>Bloqueio fraco de Na+, encurta potencial de acao</td>
          <td>Lidocaina, Mexiletina, Fenitoina</td>
          <td>Taquicardia ventricular (pos-IAM), intox. digitalica</td>
          <td>Neurotoxicidade (convulsoes), tontura</td>
        </tr>
        <tr>
          <td><strong>IC</strong></td>
          <td>Bloqueio forte de Na+, sem efeito na duracao</td>
          <td>Flecainida, Propafenona, Encainida</td>
          <td>TPSV, FA sem cardiopatia estrutural</td>
          <td>Pro-arritmico (estudo CAST), IC</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="5">🟦 CLASSE II - BETABLOQUEADORES (beta)</td>
        </tr>
        <tr>
          <td><strong>II</strong></td>
          <td>Reduz automaticidade do no sinusal, diminui conducao AV</td>
          <td>Propranolol, Metoprolol, Atenolol, Bisoprolol, Esmolol</td>
          <td>Taquicardia sinusal, FA, TPSV, pos-IAM</td>
          <td>Bradicardia, broncoespasmo, fadiga</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="5">🟪 CLASSE III - BLOQUEADORES DE POTASSIO (K+)</td>
        </tr>
        <tr>
          <td><strong>III</strong></td>
          <td>Prolonga repolarizacao e duracao do potencial de acao</td>
          <td>Amiodarona, Sotalol, Dofetilida, Ibutilida</td>
          <td>FA, Flutter, TV (amiodarona = "droga total")</td>
          <td>Amiodarona: tireoide, figado, pulmao<br>Torsades (sotalol)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="5">🟧 CLASSE IV - BLOQUEADORES DE CALCIO (Ca2+)</td>
        </tr>
        <tr>
          <td><strong>IV</strong></td>
          <td>Bloqueia canais de Ca2+ (fase 2), reduz conducao nodal AV</td>
          <td>Verapamil, Diltiazem</td>
          <td>TPSV, FA com resposta ventricular alta</td>
          <td>Bradicardia, constipacao (verapamil), IC</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mnemonicos -->
  <div class="bcc-mnemonics" style="background:linear-gradient(135deg,#fce7f3 0%,#fbcfe8 100%);border:2px dashed #ec4899;">
    <h3 class="bcc-mnemonics-title" style="color:#831843;">🧠 Mnemonicos dos Antiarritmicos</h3>

    <div class="mnemonic-card" style="border-color:#dc2626;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#dc2626;">REGRA 1</span>
        <h4 class="mnemonic-title">"DICA da Quinidina" - Subclasses IA, IB, IC</h4>
      </div>
      <p class="mnemonic-content">
        <strong>D</strong>isopiramida, <strong>I</strong>A = Quinidina/Procainamida (duas)<br>
        <strong>I</strong>B = Lidocaina/Mexiletina (duas)<br>
        <strong>C</strong> = Flecainida/Propafenona (duas)<br>
        Todas tem 2 membros principais!
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Memorize por SUBFIXO:</strong> "-caína/-caina" é IB (LidoCAINA, MexileTIINA tbem). "-fenona" é IC (PropafeNONA). "-namida" é IA (ProcaiNAMIDA, AmiNAMIDA não).
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#0ea5e9;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#0ea5e9;">REGRA 2</span>
        <h4 class="mnemonic-title">"2-3-4 Sao canais" - Quais bloqueiam canais ionicos</h4>
      </div>
      <p class="mnemonic-content">
        <strong>Classe II</strong> = Beta (no automatico, Fase 4)<br>
        <strong>Classe III</strong> = K+ (repolarizacao, Fase 3)<br>
        <strong>Classe IV</strong> = Ca2+ (plateau, Fase 2)<br>
        <strong>Classe I</strong> = Na+ (despolarizacao, Fase 0)
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Ordem na onda:</strong> 0 → 4 → 3 → 2 (Na+ → Beta → K+ → Ca2+)
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#7c3aed;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#7c3aed;">REGRA 3</span>
        <h4 class="mnemonic-title">"AMIODARONA = Amiga de todos"</h4>
      </div>
      <p class="mnemonic-content">
        A <strong>Amiodarona</strong> e a unica droga que tem propriedades de <strong>TODAS as 4 classes</strong> (predominio classe III). Por isso e chamada de <strong>"droga total"</strong> ou <strong>"amiga do cardiologista"</strong>.
      </p>
      <div class="mnemonic-warning">
        <strong>⚠️ EFEITOS ADVERSOS da Amiodarona (caixa-preta):</strong> tireotoxicose/tireoidite, fibrose pulmonar, hepatotoxicidade, neuropatia, deposito corneal (azul-acinzentado), fotossensibilidade.
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#f59e0b;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#f59e0b;">REGRA 4</span>
        <h4 class="mnemonic-title">"CAST Study" - Cuidado com IC</h4>
      </div>
      <p class="mnemonic-warning">
        <strong>⚠️ Estudo CAST (1989):</strong> Flecainida e Encainida em pos-IAM AUMENTARAM mortalidade. <strong>Evite Classe IC em pacientes com cardiopatia estrutural ou pos-IAM!</strong>
      </p>
    </div>
  </div>

  <!-- Desafio -->
  <div class="bcc-challenge">
    <h3 class="bcc-challenge-title">💡 Desafio: Arritmia no PS</h3>

    <div class="bcc-challenge-text">
      <strong>Caso:</strong> Homem 70 anos, pos-IAM recente (15 dias), admitido com TV sustentada. Hemodinamicamente estavel. Qual antiarritmico escolher?
    </div>

    <div class="bcc-challenge-question">
      ❓ Qual classe voce usaria e por que?
    </div>

    <button class="bcc-challenge-btn" onclick="revealArrChallenge()">
      💡 Ver Resposta
    </button>

    <div class="bcc-challenge-answer" id="arrChallengeAnswer">
      <strong>✅ RESPOSTA: AMIODARONA (Classe III)</strong><br><br>

      <strong>Por que?</strong><br>
      - <strong>Pos-IAM</strong>: Exclui Classe IC (CAST study!) e Classe IB (TV nao e melhor indicacao)<br>
      - <strong>TV sustentada</strong>: Amiodarona e a primeira escolha em arritmias ventriculares<br>
      - <strong>Hemodinamicamente estavel</strong>: Nao precisa cardioversao eletrica<br>
      - <strong>Cardiopatia estrutural</strong>: Betabloqueador ajuda, mas nao para TV aguda<br><br>

      <strong>Alternativas:</strong><br>
      - Lidocaina (Classe IB) se TV monomorfica sem IC<br>
      - Procainamida (Classe IA) em TV polimorfica<br>
      - Betabloqueador (Classe II) na fase cronica pos-IAM<br><br>

      <strong>Evitar:</strong><br>
      - Flecainida (CAST - aumenta mortalidade pos-IAM)<br>
      - Sotalol (torsades em cardiopata)<br>
      - Verapamil (piora em TV - pode causar colapso)
    </div>
  </div>

  <div class="bcc-summary">
    <h4 class="bcc-summary-title" style="color:#831843;">🎯 Resumo Clinico dos Antiarritmicos</h4>
    <div class="bcc-summary-grid">
      <div class="bcc-summary-item" style="background:#fee2e2;border-left-color:#dc2626;">
        <strong style="color:#dc2626;">💊 Classe IA</strong>
        Quinidina, Procainamida. Uso em TV, FA. Cuidado: torsades, lupus.
      </div>
      <div class="bcc-summary-item" style="background:#fef3c7;border-left-color:#ca8a04;">
        <strong style="color:#ca8a04;">💊 Classe IB</strong>
        Lidocaina (TV pos-IAM). Nao usar em FA. EV = rapido.
      </div>
      <div class="bcc-summary-item" style="background:#fce7f3;border-left-color:#be185d;">
        <strong style="color:#be185d;">💊 Classe IC</strong>
        Flecainida (TPSV, FA sem cardiopatia). <strong>NUNCA pos-IAM!</strong>
      </div>
      <div class="bcc-summary-item" style="background:#dbeafe;border-left-color:#0ea5e9;">
        <strong style="color:#0ea5e9;">💊 Classe II</strong>
        Betabloqueadores. Cronico: pos-IAM, FA. Seguro.
      </div>
      <div class="bcc-summary-item" style="background:#f3e8ff;border-left-color:#7c3aed;">
        <strong style="color:#7c3aed;">💊 Classe III</strong>
        Amiodarona (droga total). Sotalol. Cuidado tireoide/pulmao.
      </div>
      <div class="bcc-summary-item" style="background:#fed7aa;border-left-color:#f97316;">
        <strong style="color:#f97316;">💊 Classe IV</strong>
        Verapamil, Diltiazem. TPSV, controle de FC em FA. Evitar IC.
      </div>
    </div>
  </div>
</div>
"""

# ===== MODULO ANTICOAGULANTES =====
ANTICOAGULANTES_HTML = """
<!-- ========== MODULO ANTICOAGULANTES ========== -->
<div class="bcc-module" id="anticoagModule" style="background:linear-gradient(135deg,#dbeafe 0%,#bfdbfe 100%);border-color:#3b82f6;">
  <div class="bcc-header">
    <div class="bcc-icon" style="background:linear-gradient(135deg,#3b82f6,#1d4ed8);">🩸</div>
    <div>
      <h3 class="bcc-title" style="color:#1e3a8a;">Anticoagulantes - Warfarina, DOACs e Heparina</h3>
      <p class="bcc-subtitle">Cascata de coagulacao e onde cada droga age</p>
    </div>
  </div>

  <div class="bcc-intro">
    Os <strong>anticoagulantes</strong> sao essenciais na prevencao e tratamento de tromboses. Dividem-se em: <strong>Antagonistas da Vitamina K</strong> (warfarina), <strong>DOACs</strong> (anticoagulantes orais diretos) e <strong>Heparinas</strong> (HNF e HBPM). A escolha depende da <strong>indicacao</strong>, <strong>funcao renal</strong> e <strong>risco hemorragico</strong>.
  </div>

  <!-- Diagrama da Cascata -->
  <div class="bcc-diagram">
    <div class="bcc-diagram-title" style="color:#1e3a8a;">🧬 Cascata de Coagulacao - Onde cada anticoagulante age</div>
    <svg viewBox="0 0 700 350" xmlns="http://www.w3.org/2000/svg">
      <!-- Via intrinseca -->
      <text x="100" y="30" font-family="Arial" font-size="11" font-weight="700" fill="#1e3a8a">VIA INTRINSECA (Heparinas)</text>

      <!-- XII -->
      <rect x="40" y="60" width="50" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6"/>
      <text x="65" y="82" font-family="Arial" font-size="11" font-weight="700" fill="#1e3a8a" text-anchor="middle">XII</text>

      <!-- XI -->
      <rect x="120" y="60" width="50" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6"/>
      <text x="145" y="82" font-family="Arial" font-size="11" font-weight="700" fill="#1e3a8a" text-anchor="middle">XI</text>

      <!-- IX -->
      <rect x="200" y="60" width="50" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6"/>
      <text x="225" y="82" font-family="Arial" font-size="11" font-weight="700" fill="#1e3a8a" text-anchor="middle">IX</text>

      <!-- X -->
      <rect x="280" y="160" width="50" height="35" fill="#fbcfe8" stroke="#be185c" stroke-width="2" rx="6"/>
      <text x="305" y="182" font-family="Arial" font-size="11" font-weight="700" fill="#831843" text-anchor="middle">X</text>

      <!-- II -->
      <rect x="360" y="160" width="50" height="35" fill="#fbcfe8" stroke="#be185c" stroke-width="2" rx="6"/>
      <text x="385" y="182" font-family="Arial" font-size="11" font-weight="700" fill="#831843" text-anchor="middle">II</text>

      <!-- Trombina -->
      <rect x="440" y="160" width="80" height="35" fill="#7f1d1d" stroke="#450a0a" stroke-width="2" rx="6"/>
      <text x="480" y="182" font-family="Arial" font-size="11" font-weight="700" fill="white" text-anchor="middle">TROMBINA</text>

      <!-- Fibrinogenio -->
      <rect x="550" y="160" width="100" height="35" fill="#7f1d1d" stroke="#450a0a" stroke-width="2" rx="6"/>
      <text x="600" y="182" font-family="Arial" font-size="11" font-weight="700" fill="white" text-anchor="middle">FIBRINA</text>

      <!-- Via extrinseca -->
      <text x="100" y="240" font-family="Arial" font-size="11" font-weight="700" fill="#1e3a8a">VIA EXTRINSECA (Warfarina)</text>

      <!-- Fator tecidual + VII -->
      <rect x="200" y="270" width="80" height="35" fill="#fef3c7" stroke="#ca8a04" stroke-width="2" rx="6"/>
      <text x="240" y="292" font-family="Arial" font-size="11" font-weight="700" fill="#713f12" text-anchor="middle">FT + VII</text>

      <!-- Setas -->
      <line x1="90" y1="80" x2="120" y2="80" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrowAC)"/>
      <line x1="170" y1="80" x2="200" y2="80" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrowAC)"/>
      <path d="M 225 95 Q 225 130 280 165" fill="none" stroke="#3b82f6" stroke-width="2" marker-end="url(#arrowAC)"/>
      <line x1="330" y1="180" x2="360" y2="180" stroke="#be185c" stroke-width="2" marker-end="url(#arrowAC)"/>
      <line x1="410" y1="180" x2="440" y2="180" stroke="#be185c" stroke-width="2" marker-end="url(#arrowAC)"/>
      <line x1="520" y1="180" x2="550" y2="180" stroke="#be185c" stroke-width="2" marker-end="url(#arrowAC)"/>
      <path d="M 280 290 Q 320 250 320 195" fill="none" stroke="#ca8a04" stroke-width="2" marker-end="url(#arrowAC)"/>

      <!-- Locais de acao -->
      <!-- Heparina (anti-Xa e anti-IIa) -->
      <rect x="280" y="130" width="120" height="22" fill="#10b981" rx="3"/>
      <text x="340" y="146" font-family="Arial" font-size="10" font-weight="700" fill="white" text-anchor="middle">HEPARINA (anti-Xa + IIa)</text>

      <!-- DOACs (anti-Xa ou anti-IIa) -->
      <rect x="280" y="200" width="200" height="22" fill="#0ea5e9" rx="3"/>
      <text x="380" y="216" font-family="Arial" font-size="10" font-weight="700" fill="white" text-anchor="middle">DOACs (Rivaroxabana=anti-Xa, Dabigatrana=anti-IIa)</text>

      <!-- Warfarina (fatores II, VII, IX, X) -->
      <rect x="60" y="100" width="180" height="22" fill="#dc2626" rx="3"/>
      <text x="150" y="116" font-family="Arial" font-size="10" font-weight="700" fill="white" text-anchor="middle">WARFARINA (II, VII, IX, X)</text>

      <defs>
        <marker id="arrowAC" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
        </marker>
      </defs>

      <!-- Legenda -->
      <text x="350" y="335" font-family="Arial" font-size="9" fill="#64748b" text-anchor="middle">Warfarina bloqueia sintese de fatores II, VII, IX, X (vitamina K-dependentes)</text>
    </svg>
  </div>

  <!-- Tabela -->
  <div class="bcc-table-wrapper">
    <table class="bcc-table">
      <thead>
        <tr>
          <th>Droga</th>
          <th>Mecanismo</th>
          <th>Indicacao</th>
          <th>Monitoramento</th>
          <th>Antidoto</th>
        </tr>
      </thead>
      <tbody>
        <tr class="bcc-group-header">
          <td colspan="5">🟦 ANTAGONISTAS DA VITAMINA K</td>
        </tr>
        <tr>
          <td><strong>Warfarina</strong></td>
          <td>Inibe sintese de fatores II, VII, IX, X (vitamina K-dependentes)</td>
          <td>FA, TEV cronico, valvulas mecanicas, sindrome antifosfolipide</td>
          <td>INR (alvo 2-3, mecanicos 2.5-3.5)</td>
          <td>Vitamina K + CCP (4 fatores)</td>
        </tr>
        <tr>
          <td><strong>Fenprocumona</strong></td>
          <td>Mesma classe, menos usado no Brasil</td>
          <td>Similar a warfarina</td>
          <td>INR</td>
          <td>Vitamina K</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="5">🟪 DOACs (Anticoagulantes Orais Diretos)</td>
        </tr>
        <tr>
          <td><strong>Rivaroxabana</strong></td>
          <td>Inibidor direto do Fator Xa</td>
          <td>FA, TEV, SCA (combinada)</td>
          <td>NAO precisa (fx renal)</td>
          <td>Andexanet alfa (off-label)</td>
        </tr>
        <tr>
          <td><strong>Apixabana</strong></td>
          <td>Inibidor direto do Fator Xa</td>
          <td>FA, TEV</td>
          <td>NAO precisa</td>
          <td>Andexanet alfa</td>
        </tr>
        <tr>
          <td><strong>Edoxabana</strong></td>
          <td>Inibidor direto do Fator Xa</td>
          <td>FA, TEV</td>
          <td>NAO precisa</td>
          <td>Andexanet alfa</td>
        </tr>
        <tr>
          <td><strong>Dabigatrana</strong></td>
          <td>Inibidor direto da Trombina (IIa)</td>
          <td>FA, TEV</td>
          <td>NAO precisa</td>
          <td>Idarucizumabe (específico!)</td>
        </tr>

        <tr class="bcc-group-header">
          <td colspan="5">🟩 HEPARINAS</td>
        </tr>
        <tr>
          <td><strong>HNF</strong><br>(Nao-fracionada)</td>
          <td>Anti-IIa + anti-Xa (proporcao 1:1), via IV</td>
          <td>TEV agudo, SCA, CIV, dialise</td>
          <td>TTPa (1.5-2.5x controle)</td>
          <td>Protamina (1mg/100U HNF)</td>
        </tr>
        <tr>
          <td><strong>HBPM</strong><br>(Enoxaparina)</td>
          <td>Mais anti-Xa que anti-IIa, SC 1-2x/dia</td>
          <td>TEV, SCA, profilaxia</td>
          <td>NAO precisa (fx anti-Xa em IR/obesos)</td>
          <td>Protamina (parcial, 60-80%)</td>
        </tr>
        <tr>
          <td><strong>Fondaparinux</strong></td>
          <td>Anti-Xa puro sintetico</td>
          <td>TEV, SCA</td>
          <td>NAO precisa</td>
          <td>NAO tem (risco sangramento)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mnemonicos -->
  <div class="bcc-mnemonics" style="background:linear-gradient(135deg,#dbeafe 0%,#bfdbfe 100%);border:2px dashed #3b82f6;">
    <h3 class="bcc-mnemonics-title" style="color:#1e3a8a;">🧠 Mnemonicos dos Anticoagulantes</h3>

    <div class="mnemonic-card" style="border-color:#3b82f6;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#3b82f6;">REGRA 1</span>
        <h4 class="mnemonic-title">"DOAC = Direto OAnticoagulante COagulante"</h4>
      </div>
      <p class="mnemonic-content">
        <strong>DOACs</strong> sao <strong>D</strong>iretos, <strong>O</strong>rais, <strong>A</strong>cao <strong>C</strong>urta. Diferenca para warfarina: <strong>NAO precisam de INR</strong>, <strong>inicio rapido</strong>, <strong>menos interacoes</strong>.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Sufixo:</strong> "-xabana" = anti-Xa (Rivaroxabana, Apixabana, Edoxabana). "-gatrana" = anti-trombina (Dabigatrana).
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#dc2626;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#dc2626;">REGRA 2</span>
        <h4 class="mnemonic-title">"Warfarina 4 fatores (II-VII-IX-X)"</h4>
      </div>
      <p class="mnemonic-content">
        Warfarina bloqueia a sintese de <strong>4 fatores vitamina K-dependentes</strong>: <strong>II, VII, IX, X</strong>. Por isso demora 3-5 dias para efeito pleno (meia-vida longa do fator II = protrombina).
      </p>
      <div class="mnemonic-warning">
        <strong>⚠️ CUIDADO:</strong> Warfarina e teratogenica (categoria X). EVITAR em gestante! Usar HBPM (enoxaparina).
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#10b981;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#10b981;">REGRA 3</span>
        <h4 class="mnemonic-title">"HNF vs HBPM" - Hospitalar vs Ambulatorio</h4>
      </div>
      <p class="mnemonic-content">
        <strong>HNF</strong> = Hospitalar, IV, monitora TTPa. Reversivel com protamina.<br>
        <strong>HBPM</strong> = Ambulatorio, SC, NAO monitora. Mais cara. <strong>Enoxaparina 1mg/kg 2x/dia</strong>.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Dica pratica:</strong> HBPM em IR com ClCr &lt; 30: reduzir dose (enoxaparina 1mg/kg 1x/dia) ou trocar para HNF.
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#7c3aed;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#7c3aed;">REGRA 4</span>
        <h4 class="mnemonic-title">"Bridge" - HBPM na transicao warfarina</h4>
      </div>
      <p class="mnemonic-content">
        Como warfarina demora 3-5 dias para fazer efeito, use <strong>HBPM em ponte</strong> ate INR alvo (2-3). Suspenda HBPM quando INR estiver em faixa terapeutica por 2 dias consecutivos.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Antidotos:</strong> Warfarina = Vitamina K + CCP. Dabigatrana = Idarucizumabe (especifico!). Rivaroxabana = Andexanet alfa.
      </div>
    </div>

    <div class="mnemonic-card" style="border-color:#f59e0b;">
      <div class="mnemonic-header">
        <span class="mnemonic-tag" style="background:#f59e0b;">REGRA 5</span>
        <h4 class="mnemonic-title">"DOACs NAO em valvula mecanica"</h4>
      </div>
      <div class="mnemonic-warning">
        <strong>⚠️ REGRA DE OURO:</strong> DOACs estao <strong>CONTRAINDICADOS</strong> em pacientes com <strong>valvula mecanica</strong> ou <strong>estenose mitral reumatica</strong> (estudo RE-ALIGN). Apenas warfarina!
      </div>
    </div>
  </div>

  <!-- Desafio -->
  <div class="bcc-challenge">
    <h3 class="bcc-challenge-title">💡 Desafio: Sangramento + Anticoagulante</h3>

    <div class="bcc-challenge-text">
      <strong>Caso:</strong> Idosa 78 anos, FA cronica, usando Dabigatrana 150mg 2x/dia. Cai em casa, bate a cabeca, e apresenta sangramento intracraniano no TC. Qual manejo?
    </div>

    <div class="bcc-challenge-question">
      ❓ Qual antidoto voce usaria? E outras medidas?
    </div>

    <button class="bcc-challenge-btn" onclick="revealAnticoagChallenge()">
      💡 Ver Resposta
    </button>

    <div class="bcc-challenge-answer" id="anticoagChallengeAnswer">
      <strong>✅ RESPOSTA: IDARUCIZUMABE 5g IV (2 frascos de 2,5g)</strong><br><br>

      <strong>Por que?</strong><br>
      - <strong>Anticoagulante = Dabigatrana</strong> (anti-IIa, "-gatrana")<br>
      - <strong>Idarucizumabe</strong> e o <strong>ANTIDOTO ESPECIFICO</strong> da dabigatrana (fragmento de anticorpo monoclonal)<br>
      - Liga-se a dabigatrana 350x mais forte que a trombina<br>
      - <strong>Efeito em minutos</strong>: reversao completa em media de 4h<br><br>

      <strong>Outras medidas:</strong><br>
      - Suspender dabigatrana IMEDIATAMENTE<br>
      - Suporte hemodinamico (cristaloides, transfusao se necessario)<br>
      - <strong>CCP (complexo protrombinico) NAO funciona</strong> para dabigatrana (ela age diretamente na trombina)<br>
      - Hemodialise: dabigatrana e <strong>dialisavel</strong> (baixa ligacao proteica)<br>
      - <strong>Avaliacao neurocirurgica</strong> (hematoma pode precisar drenagem)<br><br>

      <strong>SE FOSSE RIVAROXABANA ou APIXABANA:</strong><br>
      - Andexanet alfa 400-800mg IV (antidoto especifico, mas pouco disponivel)<br>
      - Alternativa: CCP 4 fatores 50 UI/kg<br>
      - <strong>NAO sao dialisaveis</strong> (alta ligacao proteica)
    </div>
  </div>

  <div class="bcc-summary">
    <h4 class="bcc-summary-title" style="color:#1e3a8a;">🎯 Quando Escolher Cada Anticoagulante</h4>
    <div class="bcc-summary-grid">
      <div class="bcc-summary-item" style="background:#fee2e2;border-left-color:#dc2626;">
        <strong style="color:#dc2626;">💊 Warfarina</strong>
        Valvula mecanica, sindrome antifosfolipide, IR avancada. Barato. INR obrigatorio.
      </div>
      <div class="bcc-summary-item" style="background:#dbeafe;border-left-color:#3b82f6;">
        <strong style="color:#3b82f6;">💊 DOACs</strong>
        FA nao-valvular, TEV. NAO precisa INR. Caro, mas pratico.
      </div>
      <div class="bcc-summary-item" style="background:#d1fae5;border-left-color:#10b981;">
        <strong style="color:#10b981;">💊 HNF</strong>
        Hospitalar, agudo, IR avancada, gravidas (alternativa a HBPM). TTPa obrigatorio.
      </div>
      <div class="bcc-summary-item" style="background:#d1fae5;border-left-color:#10b981;">
        <strong style="color:#10b981;">💊 HBPM</strong>
        TEV ambulatorial, gravidas (1a escolha!), SCA. SC 1-2x/dia.
      </div>
      <div class="bcc-summary-item" style="background:#fef3c7;border-left-color:#ca8a04;">
        <strong style="color:#ca8a04;">💊 Fondaparinux</strong>
        SCA, TEV em alergia a heparina (HIT). Anti-Xa puro. NAO tem antidoto.
      </div>
      <div class="bcc-summary-item" style="background:#f3e8ff;border-left-color:#7c3aed;">
        <strong style="color:#7c3aed;">🤰 Gestante</strong>
        HBPM (enoxaparina) sempre. Warfarina = teratogenica. DOACs = sem dados.
      </div>
    </div>
  </div>
</div>

<script>
// ========== DESAFIO ANTIARRIITMICO ==========
function revealArrChallenge() {
  const answer = document.getElementById('arrChallengeAnswer');
  if (answer) {
    answer.classList.add('show');
    answer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (typeof addXP === 'function') addXP(30);
  }
}

// ========== DESAFIO ANTICOAGULANTE ==========
function revealAnticoagChallenge() {
  const answer = document.getElementById('anticoagChallengeAnswer');
  if (answer) {
    answer.classList.add('show');
    answer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (typeof addXP === 'function') addXP(30);
  }
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
    print("⚡ Adicionando 2 novos modulos:")
    print("   1. Antiarritmicos (Vaughan-Williams)")
    print("   2. Anticoagulantes (Warfarina, DOACs, Heparinas)")
    print("=" * 60)

    modulos = [
        ('id="antiarrModule"', ANTIARRITMICOS_HTML),
        ('id="anticoagModule"', ANTICOAGULANTES_HTML),
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
    print("✅ Modulos adicionados!")
    print("=" * 60)


if __name__ == "__main__":
    main()