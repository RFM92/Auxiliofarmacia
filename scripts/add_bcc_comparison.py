#!/usr/bin/env python3
"""
Adiciona modulo comparativo dos BCCs (Bloqueadores dos Canais de Calcio)
no curso de Anti-hipertensivos com:
- Tabela comparativa completa
- Diagrama molecular do canal de calcio
- Mnemonicos de memorizacao
- Desafio interativo de 8h
"""
import re
from pathlib import Path

# CSS para o modulo BCC
BCC_CSS = """
<style>
/* ========== MODULO BCC ========== */
.bcc-module {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #0ea5e9;
  border-radius: 16px;
  padding: 24px;
  margin: 20px 16px;
}

.bcc-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #bae6fd;
}
.bcc-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
}
.bcc-title {
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  color: #0c4a6e;
  margin: 0;
}
.bcc-subtitle {
  font-size: 13px;
  color: #475569;
  margin: 4px 0 0 0;
}

.bcc-intro {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  font-size: 14px;
  line-height: 1.6;
  color: #1e293b;
  border-left: 4px solid #0ea5e9;
}

/* Diagrama molecular */
.bcc-diagram {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}
.bcc-diagram-title {
  font-weight: 700;
  color: #0c4a6e;
  margin-bottom: 12px;
  font-size: 15px;
}
.bcc-channel-svg {
  max-width: 100%;
  height: auto;
}

/* Tabela comparativa */
.bcc-table-wrapper {
  overflow-x: auto;
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.bcc-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 13px;
}
.bcc-table thead {
  background: linear-gradient(135deg, #0c4a6e 0%, #0ea5e9 100%);
  color: white;
}
.bcc-table th {
  padding: 14px 12px;
  text-align: left;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.bcc-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: top;
}
.bcc-table tbody tr:hover {
  background: #f0f9ff;
}
.bcc-group-header {
  background: linear-gradient(90deg, #dbeafe, #bfdbfe);
  font-weight: 700;
  color: #0c4a6e;
}
.bcc-group-vascular {
  background: linear-gradient(90deg, #fee2e2, #fecaca);
}
.bcc-group-cardiac {
  background: linear-gradient(90deg, #fef3c7, #fde68a);
}
.bcc-drug-name {
  font-weight: 700;
  color: #0c4a6e;
  font-size: 14px;
}
.bcc-suffix {
  display: inline-block;
  background: #1e293b;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 10px;
  margin-left: 6px;
  letter-spacing: 0.5px;
}
.bcc-target-vascular {
  background: #fee2e2;
  color: #991b1b;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}
.bcc-target-cardiac {
  background: #fef3c7;
  color: #92400e;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}
.bcc-target-mixed {
  background: #e0e7ff;
  color: #3730a3;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
}
.bcc-effect {
  font-size: 12px;
  color: #475569;
  line-height: 1.5;
}
.bcc-indication {
  background: #f0fdf4;
  border-left: 3px solid #10b981;
  padding: 8px 10px;
  font-size: 12px;
  color: #065f46;
  border-radius: 4px;
  line-height: 1.5;
}

/* Mnemonicos */
.bcc-mnemonics {
  background: linear-gradient(135deg, #fef9c3 0%, #fde68a 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 2px dashed #ca8a04;
}
.bcc-mnemonics-title {
  font-size: 18px;
  font-weight: 700;
  color: #713f12;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mnemonic-card {
  background: white;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 4px solid;
}
.mnemonic-card.dipino { border-color: #dc2626; }
.mnemonic-card.verapamil { border-color: #f59e0b; }
.mnemonic-card.diltiazem { border-color: #7c3aed; }

.mnemonic-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.mnemonic-tag {
  background: #0c4a6e;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.mnemonic-title {
  font-size: 14px;
  font-weight: 700;
  color: #0c4a6e;
  margin: 0;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.5px;
}
.mnemonic-content {
  font-size: 13px;
  color: #1f2937;
  line-height: 1.6;
  margin: 0;
}
.mnemonic-highlight {
  background: linear-gradient(135deg, #fef9c3, #fef08a);
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 8px;
  border-left: 3px solid #ca8a04;
  font-style: italic;
}
.mnemonic-warning {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 8px;
  border-left: 3px solid #dc2626;
  font-weight: 600;
  color: #991b1b;
}
.mnemonic-extra {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 8px;
  border-left: 3px solid #2563eb;
  color: #1e3a8a;
}

/* Desafio interativo */
.bcc-challenge {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 2px solid #f59e0b;
}
.bcc-challenge-title {
  font-size: 18px;
  font-weight: 700;
  color: #92400e;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.bcc-challenge-text {
  background: white;
  border-radius: 10px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
  color: #1f2937;
  margin-bottom: 12px;
}
.bcc-challenge-question {
  background: #fef9c3;
  border-left: 4px solid #ca8a04;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 700;
  color: #422006;
  margin-bottom: 12px;
}
.bcc-challenge-btn {
  padding: 10px 20px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
}
.bcc-challenge-btn:hover {
  background: #d97706;
}
.bcc-challenge-answer {
  background: #d1fae5;
  border-left: 4px solid #10b981;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 12px;
  display: none;
  font-size: 13px;
  color: #065f46;
  line-height: 1.6;
}
.bcc-challenge-answer.show { display: block; }

/* Resumo final */
.bcc-summary {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-top: 16px;
  border: 2px dashed #0ea5e9;
}
.bcc-summary-title {
  font-size: 16px;
  font-weight: 700;
  color: #0c4a6e;
  margin: 0 0 12px 0;
}
.bcc-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.bcc-summary-item {
  background: #f0f9ff;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 12px;
  color: #0c4a6e;
  border-left: 3px solid #0ea5e9;
}
.bcc-summary-item strong {
  display: block;
  margin-bottom: 2px;
  font-size: 13px;
}

@media (max-width: 768px) {
  .bcc-table { font-size: 11px; }
  .bcc-table th, .bcc-table td { padding: 8px 6px; }
}
</style>
"""

# HTML do modulo BCC
BCC_HTML = """
<!-- ========== MODULO BCC - BLOQUEADORES DOS CANAIS DE CALCIO ========== -->
<div class="bcc-module" id="bccModule">
  <div class="bcc-header">
    <div class="bcc-icon">🧬</div>
    <div>
      <h3 class="bcc-title">Bloqueadores dos Canais de Calcio (BCCs)</h3>
      <p class="bcc-subtitle">Modulo complementar ao curso de Anti-hipertensivos</p>
    </div>
  </div>

  <div class="bcc-intro">
    <strong>Os BCCs</strong> atuam diretamente na comporta ionica que revisamos no painel inferior esquerdo da nossa imagem molecular (<strong>Canal de Calcio Tipo L</strong>). Porem, essa classe se divide em <strong>dois grupos quimicos completamente diferentes</strong>, mudando totalmente o foco da acao (se agem mais nos <strong>vasos</strong> ou mais no <strong>coracao</strong>). Sao divididos entre <strong>Di-hidropiridinicos</strong> (foco vascular) e <strong>Nao Di-hidropiridinicos</strong> (foco cardiaco).
  </div>

  <!-- Diagrama molecular -->
  <div class="bcc-diagram">
    <div class="bcc-diagram-title">🧪 Canal de Calcio Tipo L - Onde os BCCs Atuam</div>
    <svg viewBox="0 0 600 280" class="bcc-channel-svg" xmlns="http://www.w3.org/2000/svg">
      <!-- Membrana celular -->
      <defs>
        <linearGradient id="memGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#1e293b"/>
          <stop offset="50%" stop-color="#475569"/>
          <stop offset="100%" stop-color="#1e293b"/>
        </linearGradient>
        <linearGradient id="chGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#0ea5e9"/>
          <stop offset="50%" stop-color="#0284c7"/>
          <stop offset="100%" stop-color="#0ea5e9"/>
        </linearGradient>
      </defs>

      <!-- Membrana -->
      <rect x="0" y="100" width="600" height="80" fill="url(#memGrad)"/>

      <!-- Citoplasma -->
      <text x="20" y="50" font-family="Arial" font-size="13" fill="#475569" font-weight="bold">CITOPLASMA (celula muscular lisa)</text>
      <rect x="50" y="60" width="100" height="30" fill="#fbbf24" opacity="0.3" rx="4"/>
      <text x="60" y="80" font-family="Arial" font-size="11" fill="#92400e">Ca²⁺ no interior</text>

      <!-- Extracelular -->
      <text x="20" y="240" font-family="Arial" font-size="13" fill="#475569" font-weight="bold">ESPACO EXTRACELULAR</text>
      <circle cx="80" cy="220" r="5" fill="#ef4444"/>
      <text x="90" y="225" font-family="Arial" font-size="11" fill="#dc2626">Ca²⁺</text>
      <circle cx="140" cy="225" r="5" fill="#ef4444"/>
      <circle cx="180" cy="220" r="5" fill="#ef4444"/>
      <circle cx="220" cy="225" r="5" fill="#ef4444"/>

      <!-- Canal de Calcio -->
      <rect x="280" y="80" width="120" height="120" fill="url(#chGrad)" rx="8"/>
      <text x="340" y="145" font-family="Arial" font-size="13" fill="white" text-anchor="middle" font-weight="bold">CANAL</text>
      <text x="340" y="160" font-family="Arial" font-size="13" fill="white" text-anchor="middle" font-weight="bold">TIPO L</text>

      <!-- Porta do canal (BCC bloqueia) -->
      <rect x="320" y="130" width="40" height="30" fill="#dc2626" stroke="#7f1d1d" stroke-width="2" rx="4"/>
      <text x="340" y="150" font-family="Arial" font-size="10" fill="white" text-anchor="middle" font-weight="bold">🔒</text>

      <!-- Seta indicando entrada de calcio -->
      <path d="M 240 180 L 280 175 L 280 185 Z" fill="#dc2626"/>
      <text x="240" y="195" font-family="Arial" font-size="10" fill="#dc2626" font-weight="bold">ENTRADA</text>
      <text x="240" y="208" font-family="Arial" font-size="10" fill="#dc2626" font-weight="bold">BLOQUEADA</text>

      <!-- Subunidades -->
      <circle cx="340" cy="80" r="12" fill="#fde68a" stroke="#ca8a04" stroke-width="2"/>
      <text x="340" y="85" font-family="Arial" font-size="10" fill="#713f12" text-anchor="middle" font-weight="bold">α1</text>

      <circle cx="280" cy="140" r="8" fill="#fecaca" stroke="#dc2626" stroke-width="1"/>
      <text x="280" y="143" font-family="Arial" font-size="8" fill="#7f1d1d" text-anchor="middle">α2</text>
      <circle cx="400" cy="140" r="8" fill="#fecaca" stroke="#dc2626" stroke-width="1"/>
      <text x="400" y="143" font-family="Arial" font-size="8" fill="#7f1d1d" text-anchor="middle">δ</text>

      <circle cx="340" cy="200" r="8" fill="#bfdbfe" stroke="#2563eb" stroke-width="1"/>
      <text x="340" y="203" font-family="Arial" font-size="8" fill="#1e3a8a" text-anchor="middle">β</text>

      <!-- Legenda -->
      <rect x="450" y="50" width="140" height="180" fill="white" stroke="#0ea5e9" stroke-width="1" rx="6"/>
      <text x="460" y="70" font-family="Arial" font-size="11" fill="#0c4a6e" font-weight="bold">LEGENDA:</text>
      <circle cx="465" cy="90" r="4" fill="#ef4444"/>
      <text x="475" y="94" font-family="Arial" font-size="10" fill="#475569">Calcio (Ca²⁺)</text>
      <rect x="460" y="105" width="14" height="14" fill="#fde68a" stroke="#ca8a04" stroke-width="1"/>
      <text x="480" y="116" font-family="Arial" font-size="10" fill="#475569">α1 (BCC liga)</text>
      <rect x="460" y="128" width="14" height="14" fill="#dc2626"/>
      <text x="480" y="139" font-family="Arial" font-size="10" fill="#475569">🔒 Bloqueado</text>
      <rect x="460" y="151" width="14" height="14" fill="url(#chGrad)"/>
      <text x="480" y="162" font-family="Arial" font-size="10" fill="#475569">Canal Tipo L</text>
      <text x="460" y="185" font-family="Arial" font-size="10" fill="#dc2626" font-weight="bold">⚠️ BCCs agem aqui</text>
    </svg>
  </div>

  <!-- Tabela Comparativa -->
  <h4 style="color:#0c4a6e;margin:20px 0 12px 0;font-size:16px;">📊 Tabela Comparativa Completa</h4>

  <div class="bcc-table-wrapper">
    <table class="bcc-table">
      <thead>
        <tr>
          <th style="width:22%;">Grupo Quimico</th>
          <th style="width:18%;">Medicamento</th>
          <th style="width:18%;">Alvo Principal</th>
          <th style="width:20%;">Efeito Farmacologico</th>
          <th style="width:22%;">Indicacao / Particularidade</th>
        </tr>
      </thead>
      <tbody>
        <tr class="bcc-group-header">
          <td colspan="5">🔴 Di-hidropiridinicos (Sufixo "DIPINO")</td>
        </tr>
        <tr>
          <td><span class="bcc-target-vascular">VASOS</span><br><small>Foco Vascular</small></td>
          <td class="bcc-drug-name">Anlodipino<span class="bcc-suffix">-DIPINO</span></td>
          <td><span class="bcc-target-vascular">Vasos Sanguineos (Musculo Liso)</span></td>
          <td class="bcc-effect"><strong>Potente Vasodilatacao Periferica</strong><br>Relaxa a musculatura lisa das arterias, reduzindo resistencia vascular.</td>
          <td class="bcc-indication">Acao longa (<strong>~36-50h</strong>). Muito usado na hipertensao pura. <strong>Causa edema maleolar</strong> (tornozelo inchado).</td>
        </tr>
        <tr>
          <td><span class="bcc-target-vascular">VASOS</span><br><small>Foco Vascular</small></td>
          <td class="bcc-drug-name">Nifedipino<span class="bcc-suffix">-DIPINO</span><br><small>(Retard/Oros)</small></td>
          <td><span class="bcc-target-vascular">Vasos Sanguineos (Musculo Liso)</span></td>
          <td class="bcc-effect"><strong>Vasodilatacao rapida/moderada</strong><br>Efeito mais rapido que anlodipino.</td>
          <td class="bcc-indication"><strong>Muito usado em gestantes com hipertensao</strong>. A versao de liberacao rapida foi banida por causar taquicardia reflexa grave.</td>
        </tr>
        <tr class="bcc-group-header">
          <td colspan="5">🟡 Nao Di-hidropiridinicos</td>
        </tr>
        <tr>
          <td><span class="bcc-target-cardiac">CORAÇÃO</span><br><small>Foco Cardiaco</small></td>
          <td class="bcc-drug-name">Verapamil</td>
          <td><span class="bcc-target-cardiac">Coracao (Miocitos e Nodulos)</span></td>
          <td class="bcc-effect"><strong>Inotropico (-) + Cronotropico (-)</strong><br>Diminui forca de batimento E a frequencia cardiaca.</td>
          <td class="bcc-indication">Altamente seletivo para o coracao. <strong>Usado em arritmias e angina</strong>. Causa muita <strong>constipacao intestinal</strong>.</td>
        </tr>
        <tr>
          <td><span class="bcc-target-mixed">MISTO</span><br><small>Cardiaco + Vascular</small></td>
          <td class="bcc-drug-name">Diltiazem</td>
          <td><span class="bcc-target-mixed">Misto (Coracao e Vasos)</span></td>
          <td class="bcc-effect"><strong>Efeito intermediario</strong> (Cardiaco e Vascular)<br>Equilibra os dois efeitos.</td>
          <td class="bcc-indication"><strong>Excelente para angina estavel</strong>. Dilata coronarias enquanto reduz FC de forma sutil. Queridinho dos cardiologistas.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mnemonicos -->
  <div class="bcc-mnemonics">
    <h3 class="bcc-mnemonics-title">🧠 Dicas de Memorizacao e Mnemonicos</h3>
    <p style="margin:0 0 16px 0;color:#713f12;font-size:14px;">
      Para separar esses mecanismos na sua mente de forma definitiva, use estas regras de associacao:
    </p>

    <!-- Mnemonico 1: DIPINO -->
    <div class="mnemonic-card dipino">
      <div class="mnemonic-header">
        <span class="mnemonic-tag">REGRA 1</span>
        <h4 class="mnemonic-title">DIPINO = DIreta no PIso (Vasos la embaixo)</h4>
      </div>
      <p class="mnemonic-content">
        <strong>A dica:</strong> Todos os medicamentos que terminam em <code>"dipino"</code> (Anlodipino, Nifedipino, Lercanidipino) pertencem ao grupo das Di-hidropiridinas.<br>
        <strong>O foco:</strong> Eles sao <strong>"vasosseletivos"</strong>. Eles preferem se ligar aos canais de calcio que estao nas arterias perifericas. Ao travarem esses canais, as arterias relaxam.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Efeito colateral classico:</strong> Como dilatam muito os vasos das pernas, o liquido "vaza" por gravidade e acumula no tornozelo. Falou em Anlodipino, lembra de <strong>edema de tornozelo</strong>.
      </div>
    </div>

    <!-- Mnemonico 2: VERAPAMIL -->
    <div class="mnemonic-card verapamil">
      <div class="mnemonic-header">
        <span class="mnemonic-tag">REGRA 2</span>
        <h4 class="mnemonic-title">VERAPAMIL = VERdadeiro PAra o MIocardio (Coracao)</h4>
      </div>
      <p class="mnemonic-content">
        <strong>A dica:</strong> O Verapamil e o oposto dos "dipinos". Ele ignora os vasos perifericos e vai direto para os canais de calcio Tipo L do musculo do coracao e do no sinusal.<br>
        <strong>O foco:</strong> Ele "decrocha" o coracao, diminuindo drasticamente a forca de batimento e o ritmo.
      </p>
      <div class="mnemonic-warning">
        <strong>⚠️ Contraindicacao de ouro:</strong> NUNCA de Verapamil para um paciente com <strong>Insuficiencia Cardiaca Congestiva (ICC) descompensada</strong>, pois se o coracao ja esta fraco, o Verapamil corta o calcio e faz o coracao parar de bombear de vez.
      </div>
      <div class="mnemonic-extra">
        <strong>🧠 Mnemonico extra:</strong> Verapa<strong>MIL</strong> causa <strong>MIL</strong> dias sem ir ao banheiro (Gera uma constipacao/prisao de ventre severa por relaxar o musculo liso do intestino).
      </div>
    </div>

    <!-- Mnemonico 3: DILTIAZEM -->
    <div class="mnemonic-card diltiazem">
      <div class="mnemonic-header">
        <span class="mnemonic-tag">REGRA 3</span>
        <h4 class="mnemonic-title">DILTIAZEM = DIfícil escolher (Fica no MEIO termo)</h4>
      </div>
      <p class="mnemonic-content">
        <strong>A dica:</strong> O Diltiazem e o cara do meio de campo. Ele nao e tao focado no vaso quanto o Anlodipino, e nao e tao focado no coracao quanto o Verapamil. Ele atua um pouco em cada um.<br>
        <strong>O foco:</strong> Ele e excelente para dilatar as arterias coronarias (que irrigam o proprio coracao) enquanto reduz a frequencia de forma sutil. E o <strong>queridinho para pacientes com angina estavel</strong>.
      </p>
      <div class="mnemonic-highlight">
        <strong>💡 Dica clinica:</strong> Em pacientes com angina + HAS, o Diltiazem e a primeira escolha entre os BCCs porque trata as duas condicoes sem causar bradicardia severa (como o Verapamil) nem edema (como os dipinos).
      </div>
    </div>
  </div>

  <!-- Desafio Interativo -->
  <div class="bcc-challenge">
    <h3 class="bcc-challenge-title">💡 Desafio Interativo de Revisao de 8 horas</h3>

    <div class="bcc-challenge-text">
      <strong>Cenario clinico real:</strong> Imagine que chega uma receita na farmacia de <strong>Anlodipino 5mg</strong> para um paciente que ja tem <strong>insuficiencia cardiaca grave</strong> com as <strong>pernas muito inchadas</strong>.
      <br><br>
      Olhando para a nossa tabela e lembrando do mecanismo do canal de calcio, esse "dipino" pode <strong>piorar o inchaço periferico</strong>, exigindo uma analise cuidadosa do clinico.
    </div>

    <div class="bcc-challenge-question">
      ❓ Pergunta: Este paciente deveria mesmo receber Anlodipino? O que o prescritor deveria ter considerado? Quais alternativas sao mais seguras neste caso?
    </div>

    <button class="bcc-challenge-btn" onclick="revealChallenge()">
      💡 Ver Resposta Comentada
    </button>

    <div class="bcc-challenge-answer" id="challengeAnswer">
      <strong>📋 Analise Farmacologica Completa:</strong><br><br>

      <strong>⚠️ Problemas com Anlodipino neste paciente:</strong><br>
      1. <strong>ICC grave</strong>: Embora di-hidropiridinicos de 2a geracao (anlodipino, felodipino) NAO piorem ICC em ensaios clinicos, em pacientes com ICC descompensada <strong>qualquer vasodilatador pode piorar o quadro</strong>.<br>
      2. <strong>Edema periferico pre-existente</strong>: Anlodipino causa edema maleolar em ate 10-30% dos pacientes. Se o paciente ja tem edema por ICC, vai piorar significativamente.<br>
      3. <strong>Mecanismo do edema</strong>: Efeito <strong>PRE-CAPILAR</strong> (vasodilatacao arteriolar sem dilatar venulas) → aumento da pressao hidrostatica → extravasamento liquido para o intersticio → AGRAVA edema.<br><br>

      <strong>✅ Alternativas mais seguras:</strong><br>
      • <strong>IECA ou BRA</strong> (ex: enalapril, losartana): primeira linha em ICC, REDUZ edema.<br>
      • <strong>Betabloqueador seletivo</strong> (ex: carvedilol, bisoprolol): melhora prognostico de ICC.<br>
      • <strong>Diuretico de alca</strong> (furosemida) para controle do edema.<br>
      • <strong>Espironolactona</strong>: em ICC com FEr reduzida.<br>
      • Se BCC for absolutamente necessario: <strong>Diltiazem</strong> em dose baixa e com cautela (ainda pode piorar).<br><br>

      <strong>🧠 Licao clinica:</strong> Antes de prescrever qualquer BCC, SEMPRE avalie:<br>
      1. Paciente tem ICC? (cuidado com verapamil e di-hidropiridinicos)<br>
      2. Paciente tem edema? (prefira outro grupo)<br>
      3. Paciente tem bloqueio AV ou usa BB? (evite verapamil/diltiazem)<br>
      4. Paciente tem angina + HAS? (diltiazem e otimo)<br>
      5. Paciente e gestante? (nifedipino e a escolha)
    </div>
  </div>

  <!-- Resumo Final -->
  <div class="bcc-summary">
    <h4 class="bcc-summary-title">🎯 Resumo Visual - Como Escolher o BCC Certo</h4>

    <div class="bcc-summary-grid">
      <div class="bcc-summary-item">
        <strong>🔴 Anlodipino</strong>
        HAS pura, idoso, posologia 1x/dia, edema maleolar OK.
      </div>
      <div class="bcc-summary-item">
        <strong>🔴 Nifedipino</strong>
        Gestante com HAS, emergencia hipertensiva, acao rapida.
      </div>
      <div class="bcc-summary-item">
        <strong>🟡 Verapamil</strong>
        Arritmias supraventriculares, angina, NUNCA com ICC.
      </div>
      <div class="bcc-summary-item">
        <strong>🟡 Diltiazem</strong>
        Angina estavel + HAS, melhor equilibrio vasos/coracao.
      </div>
      <div class="bcc-summary-item">
        <strong>🚫 Evitar BCCs</strong>
        ICC descompensada (todos), BAV (verapamil/diltiazem).
      </div>
      <div class="bcc-summary-item">
        <strong>✅ Prefira BCCs</strong>
        HAS + angina, HAS + gestante, HAS + doenca vascular.
      </div>
    </div>
  </div>

  <!-- Proxima Aula -->
  <div style="background:linear-gradient(135deg,#dbeafe,#bfdbfe);border-radius:12px;padding:16px;margin-top:16px;text-align:center;">
    <p style="margin:0;color:#1e3a8a;font-weight:700;">📚 Proxima Aula: Antidiabeticos - Diabeticos Tipo 2 e Metformina</p>
    <button onclick="goToModule('antidiabeticos', 0)" style="margin-top:8px;padding:8px 20px;background:#2563eb;color:white;border:none;border-radius:8px;cursor:pointer;font-family:inherit;font-weight:600;">
      Ir para Proxima Aula →
    </button>
  </div>
</div>

<script>
// ========== DESAFIO BCC ==========
function revealChallenge() {
  const answer = document.getElementById('challengeAnswer');
  if (answer) {
    answer.classList.add('show');
    answer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    if (typeof addXP === 'function') {
      addXP(30); // Bonus por completar desafio
    }
  }
}

// Hook no modulo: mostra o modulo BCC quando abrir o curso anti-hipertensivos
const origOpenCourseBCC = window.openCourse;
if (typeof origOpenCourseBCC === 'function') {
  window.openCourse = function(cursoId) {
    origOpenCourseBCC.apply(this, arguments);
    if (cursoId === 'antihipertensivos') {
      setTimeout(() => {
        const bccModule = document.getElementById('bccModule');
        if (bccModule) {
          bccModule.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 800);
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
    print("🧬 Adicionando Modulo Comparativo dos BCCs")
    print("=" * 60)

    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        modified = False

        # Adiciona CSS
        if 'MODULO BCC ==========' not in html:
            html = html.replace('</style>', '</style>\n' + BCC_CSS, 1)
            modified = True

        # Adiciona HTML do modulo (antes do </body>)
        if 'id="bccModule"' not in html:
            html = html.replace('</body>', BCC_HTML + '\n</body>', 1)
            modified = True

        if modified:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fname}")
        else:
            print(f"⏭️  {fname}")

    print()
    print("✅ Modulo BCC adicionado em todos os dashboards!")
    print()
    print("Conteudo:")
    print("  - Diagrama SVG do Canal de Calcio Tipo L")
    print("  - Tabela comparativa completa (4 BCCs)")
    print("  - 3 mnemonicos de memorizacao")
    print("  - Desafio interativo com resposta")
    print("  - Resumo visual de selecao clinica")


if __name__ == "__main__":
    main()