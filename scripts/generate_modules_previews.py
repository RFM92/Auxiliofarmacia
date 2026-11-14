#!/usr/bin/env python3
"""
Gera previews SVG detalhados dos 4 modulos, ja que nao temos browser.
"""
import re
import subprocess
from pathlib import Path

OUTPUT = Path("/workspace/output/atualizacoes")

# ========== PREVIEW IECA vs BRA ==========
IECA_BRA_SVG_RAW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <defs>
    <linearGradient id="bgIECA" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef2f2"/>
      <stop offset="100%" stop-color="#fee2e2"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1400" fill="url(#bgIECA)"/>

  <!-- Header -->
  <rect x="40" y="40" width="80" height="80" fill="#dc2626" rx="16"/>
  <text x="80" y="98" font-size="40" text-anchor="middle">💊</text>
  <text x="140" y="75" font-size="32" font-weight="700" fill="#7f1d1d" font-family="Playfair Display">IECA vs BRA - Diferencas Praticas</text>
  <text x="140" y="105" font-size="14" fill="#991b1b">Comparativo dos inibidores do sistema renina-angiotensina</text>

  <!-- Intro -->
  <rect x="40" y="160" width="1120" height="100" fill="white" rx="12"/>
  <text x="60" y="195" font-size="14" fill="#475569">Os <tspan font-weight="700">IECA</tspan> (inibidores da ECA) e os <tspan font-weight="700">BRA</tspan> (bloqueadores do receptor AT1) agem no mesmo sistema (SRAA),</text>
  <text x="60" y="215" font-size="14" fill="#475569">mas em pontos diferentes. Ambos sao excelente primeira escolha para HAS, especialmente em diabeticos com proteinuria.</text>
  <text x="60" y="235" font-size="14" fill="#475569">Porem, diferem em <tspan font-weight="700">tolerabilidade</tspan>, <tspan font-weight="700">eficacia</tspan> e <tspan font-weight="700">indicacoes especificas</tspan>.</text>

  <!-- Tabela Comparativa -->
  <text x="40" y="295" font-size="20" font-weight="700" fill="#7f1d1d">📋 Tabela Comparativa</text>

  <rect x="40" y="310" width="1120" height="450" fill="white" rx="12"/>

  <!-- Header -->
  <rect x="40" y="310" width="1120" height="40" fill="#7f1d1d" rx="12 12 0 0"/>
  <text x="240" y="336" font-size="13" font-weight="700" fill="white">Caracteristica</text>
  <text x="600" y="336" font-size="13" font-weight="700" fill="white">IECA (Captopril, Enalapril...)</text>
  <text x="980" y="336" font-size="13" font-weight="700" fill="white">BRA (Losartana, Valsartana...)</text>

  <!-- Linha 1 -->
  <text x="60" y="375" font-size="12" font-weight="700" fill="#475569">Mecanismo</text>
  <text x="370" y="370" font-size="11" fill="#475569">Inibe a ECA (enzima conversora),</text>
  <text x="370" y="385" font-size="11" fill="#475569">impedindo formacao de Angiotensina II</text>
  <text x="370" y="400" font-size="11" fill="#dc2626" font-weight="700">↑ Bradicinina (causa tosse)</text>
  <text x="800" y="370" font-size="11" fill="#475569">Bloqueia o receptor AT1 diretamente,</text>
  <text x="800" y="385" font-size="11" fill="#475569">impedindo a Angiotensina II de agir</text>
  <text x="800" y="400" font-size="11" fill="#10b981" font-weight="700">✓ Sem tosse/angioedema</text>

  <!-- Linha 2 -->
  <line x1="40" y1="420" x2="1160" y2="420" stroke="#e2e8f0"/>
  <text x="60" y="445" font-size="12" font-weight="700" fill="#475569">Sufixo</text>
  <text x="370" y="440" font-size="11" fill="#475569">-pril (CaptoPRIL, EnalaPRIL, RamiPRIL)</text>
  <text x="800" y="440" font-size="11" fill="#475569">-sartana (Losartana, Valsartana)</text>

  <line x1="40" y1="465" x2="1160" y2="465" stroke="#e2e8f0"/>
  <text x="60" y="490" font-size="12" font-weight="700" fill="#475569">Tosse seca</text>
  <text x="370" y="490" font-size="14" fill="#dc2626" font-weight="700">10-20% (principal causa de abandono!)</text>
  <text x="800" y="490" font-size="14" fill="#10b981" font-weight="700">Raro (&lt; 1%)</text>

  <line x1="40" y1="510" x2="1160" y2="510" stroke="#e2e8f0"/>
  <text x="60" y="535" font-size="12" font-weight="700" fill="#475569">Pos-IAM</text>
  <text x="370" y="530" font-size="11" fill="#475569">Captopril, Ramipril (reducao de mortalidade)</text>
  <text x="800" y="530" font-size="11" fill="#475569">Valsartana (alternativa)</text>

  <line x1="40" y1="555" x2="1160" y2="555" stroke="#e2e8f0"/>
  <text x="60" y="580" font-size="12" font-weight="700" fill="#475569">DM2 + proteinuria</text>
  <text x="370" y="580" font-size="11" fill="#10b981" font-weight="700">✓ Nefroprotetor</text>
  <text x="800" y="580" font-size="11" fill="#10b981" font-weight="700">✓ Nefroprotetor equivalente</text>

  <line x1="40" y1="605" x2="1160" y2="605" stroke="#e2e8f0"/>
  <text x="60" y="630" font-size="12" font-weight="700" fill="#475569">Migranea (profilaxia)</text>
  <text x="370" y="630" font-size="11" fill="#94a3b8">—</text>
  <text x="800" y="625" font-size="11" fill="#475569">Candesartana (unica com evidencia forte)</text>

  <line x1="40" y1="655" x2="1160" y2="655" stroke="#e2e8f0"/>
  <text x="60" y="680" font-size="12" font-weight="700" fill="#475569">Posologia</text>
  <text x="370" y="680" font-size="11" fill="#475569">1-2x/dia (captopril 2-3x/dia)</text>
  <text x="800" y="680" font-size="11" fill="#475569">1x/dia (longa duracao)</text>

  <line x1="40" y1="705" x2="1160" y2="705" stroke="#e2e8f0"/>
  <text x="60" y="730" font-size="12" font-weight="700" fill="#dc2626">⚠️ Combinacao</text>
  <text x="370" y="730" font-size="11" fill="#dc2626" font-weight="700">NUNCA associar IECA + BRA (risco morte)</text>

  <!-- Mnemonicos -->
  <text x="40" y="800" font-size="20" font-weight="700" fill="#7f1d1d">🧠 Mnemonicos</text>

  <!-- Mnemonic 1 -->
  <rect x="40" y="820" width="540" height="130" fill="white" rx="12" stroke="#dc2626" stroke-width="2"/>
  <rect x="50" y="835" width="80" height="22" fill="#dc2626" rx="4"/>
  <text x="90" y="850" font-size="11" font-weight="700" fill="white" text-anchor="middle">SUFIXO</text>
  <text x="140" y="850" font-size="14" font-weight="700" fill="#1e293b">"PRIL" = PRIMEIRO</text>
  <text x="60" y="890" font-size="12" fill="#475569">IECA terminam em -pril (CaptoPRIL).</text>
  <text x="60" y="908" font-size="12" fill="#475569">Foi o PRIMEIRO grupo descoberto e tem mais</text>
  <text x="60" y="926" font-size="12" fill="#475569">evidencias de reducao de mortalidade.</text>

  <!-- Mnemonic 2 -->
  <rect x="620" y="820" width="540" height="130" fill="white" rx="12" stroke="#f59e0b" stroke-width="2"/>
  <rect x="630" y="835" width="80" height="22" fill="#f59e0b" rx="4"/>
  <text x="670" y="850" font-size="11" font-weight="700" fill="white" text-anchor="middle">SUFIXO</text>
  <text x="720" y="850" font-size="14" font-weight="700" fill="#1e293b">"SARTANA" = SEM tosse</text>
  <text x="640" y="890" font-size="12" fill="#475569">BRA terminam em -sartana. Como agem</text>
  <text x="640" y="908" font-size="12" fill="#475569">DEPOIS da formacao de angiotensina II,</text>
  <text x="640" y="926" font-size="12" fill="#475569">NAO acumulam bradicinina.</text>

  <!-- Mnemonic 3 -->
  <rect x="40" y="970" width="1120" height="100" fill="white" rx="12" stroke="#7c3aed" stroke-width="2"/>
  <rect x="50" y="985" width="80" height="22" fill="#7c3aed" rx="4"/>
  <text x="90" y="1000" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA</text>
  <text x="140" y="1000" font-size="14" font-weight="700" fill="#1e293b">NUNCA associar IECA + BRA</text>
  <text x="60" y="1030" font-size="12" fill="#dc2626" font-weight="700">⚠️ Contraindicacao absoluta: IECA + BRA juntos AUMENTAM risco de hipercalemia, IR e morte (ONTARGET).</text>
  <text x="60" y="1050" font-size="12" fill="#475569">Use APENAS um deles! Se tosse com IECA → troque para BRA (espere 36h de washout).</text>

  <!-- Resumo -->
  <text x="40" y="1110" font-size="20" font-weight="700" fill="#7f1d1d">🎯 Quando Escolher</text>

  <rect x="40" y="1130" width="370" height="200" fill="#fee2e2" rx="12"/>
  <rect x="40" y="1130" width="6" height="200" fill="#dc2626"/>
  <text x="60" y="1160" font-size="16" font-weight="700" fill="#dc2626">💊 IECA (1a escolha)</text>
  <text x="60" y="1190" font-size="12" fill="#1e293b">✓ DM2 + proteinuria</text>
  <text x="60" y="1210" font-size="12" fill="#1e293b">✓ Pos-IAM</text>
  <text x="60" y="1230" font-size="12" fill="#1e293b">✓ IC FEr</text>
  <text x="60" y="1250" font-size="12" fill="#1e293b">✓ Nefroprotetor</text>
  <text x="60" y="1270" font-size="12" fill="#1e293b">✓ Mais barato</text>

  <rect x="430" y="1130" width="370" height="200" fill="#fff7ed" rx="12"/>
  <rect x="430" y="1130" width="6" height="200" fill="#f59e0b"/>
  <text x="450" y="1160" font-size="16" font-weight="700" fill="#f59e0b">💊 BRA (1a alternativa)</text>
  <text x="450" y="1190" font-size="12" fill="#1e293b">✓ Tossiu com IECA</text>
  <text x="450" y="1210" font-size="12" fill="#1e293b">✓ Migranea (candesartana)</text>
  <text x="450" y="1230" font-size="12" fill="#1e293b">✓ Pos-IAM alternativo</text>

  <rect x="820" y="1130" width="340" height="200" fill="#fef3c7" rx="12"/>
  <rect x="820" y="1130" width="6" height="200" fill="#ca8a04"/>
  <text x="840" y="1160" font-size="16" font-weight="700" fill="#92400e">🚫 Evitar Ambos</text>
  <text x="840" y="1190" font-size="12" fill="#1e293b">✗ Gestacao (teratogenico!)</text>
  <text x="840" y="1210" font-size="12" fill="#1e293b">✗ Estenose bilateral</text>
  <text x="840" y="1230" font-size="12" fill="#1e293b">✗ K+ &gt; 5,5</text>

  <!-- Footer -->
  <text x="600" y="1370" font-size="12" fill="#94a3b8" text-anchor="middle">Modulo IECA vs BRA | Auxilio Farmacia</text>
</svg>"""

# ========== PREVIEW DIURETICOS ==========
DIURETICOS_SVG_RAW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <defs>
    <linearGradient id="bgDiur" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ecfeff"/>
      <stop offset="100%" stop-color="#cffafe"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1400" fill="url(#bgDiur)"/>

  <!-- Header -->
  <rect x="40" y="40" width="80" height="80" fill="#06b6d4" rx="16"/>
  <text x="80" y="98" font-size="40" text-anchor="middle">💧</text>
  <text x="140" y="75" font-size="32" font-weight="700" fill="#0e7490" font-family="Playfair Display">Diureticos - Os 3 Grandes Grupos</text>
  <text x="140" y="105" font-size="14" fill="#155e75">Tiazidicos, Alca e Poupadores de Potassio</text>

  <!-- Diagrama do Nefron -->
  <rect x="40" y="160" width="1120" height="280" fill="white" rx="12"/>
  <text x="60" y="190" font-size="18" font-weight="700" fill="#0e7490">🧬 Local de Acao dos Diureticos no Nefron</text>

  <!-- Tubulo Proximal -->
  <rect x="100" y="220" width="140" height="60" fill="#fef3c7" stroke="#ca8a04" stroke-width="2" rx="6"/>
  <text x="170" y="245" font-size="11" font-weight="700" fill="#713f12" text-anchor="middle">TUBULO</text>
  <text x="170" y="265" font-size="11" font-weight="700" fill="#713f12" text-anchor="middle">PROXIMAL</text>

  <!-- Alca de Henle -->
  <path d="M 250 250 Q 320 200 410 250 Q 460 300 410 360 Q 350 410 280 360 Q 230 300 250 250 Z" fill="none" stroke="#7c3aed" stroke-width="3"/>
  <text x="335" y="305" font-size="11" font-weight="700" fill="#5b21b6" text-anchor="middle">ALCA DE HENLE</text>
  <text x="335" y="385" font-size="10" fill="#7c3aed" text-anchor="middle" font-style="italic">porcao ascendente espessa</text>

  <!-- Tubulo Distal -->
  <rect x="490" y="220" width="140" height="60" fill="#fef3c7" stroke="#ca8a04" stroke-width="2" rx="6"/>
  <text x="560" y="245" font-size="11" font-weight="700" fill="#713f12" text-anchor="middle">TUBULO</text>
  <text x="560" y="265" font-size="11" font-weight="700" fill="#713f12" text-anchor="middle">DISTAL</text>

  <!-- Duto Coletor -->
  <rect x="490" y="340" width="140" height="60" fill="#fef3c7" stroke="#dc2626" stroke-width="2" rx="6"/>
  <text x="560" y="365" font-size="11" font-weight="700" fill="#7f1d1d" text-anchor="middle">DUTO</text>
  <text x="560" y="385" font-size="11" font-weight="700" fill="#7f1d1d" text-anchor="middle">COLETOR</text>

  <!-- Labels com medicamentos -->
  <rect x="640" y="240" width="180" height="50" fill="#fef3c7" rx="6" stroke="#ca8a04"/>
  <text x="730" y="262" font-size="11" font-weight="700" fill="#0c4a6e" text-anchor="middle">HCTZ, Clortalidona,</text>
  <text x="730" y="278" font-size="11" font-weight="700" fill="#0c4a6e" text-anchor="middle">Indapamida</text>

  <rect x="640" y="100" width="180" height="50" fill="#f3e8ff" rx="6" stroke="#7c3aed"/>
  <text x="730" y="122" font-size="11" font-weight="700" fill="#5b21b6" text-anchor="middle">Furosemida, Bumetanida,</text>
  <text x="730" y="138" font-size="11" font-weight="700" fill="#5b21b6" text-anchor="middle">Torasemida</text>

  <rect x="640" y="360" width="180" height="50" fill="#fee2e2" rx="6" stroke="#dc2626"/>
  <text x="730" y="382" font-size="11" font-weight="700" fill="#991b1b" text-anchor="middle">Espironolactona,</text>
  <text x="730" y="398" font-size="11" font-weight="700" fill="#991b1b" text-anchor="middle">Eplerenona, Amilorida</text>

  <!-- Linhas conectando -->
  <line x1="630" y1="265" x2="640" y2="265" stroke="#0c4a6e" stroke-width="2" marker-end="url(#arrowCyan)"/>
  <line x1="410" y1="290" x2="640" y2="125" stroke="#5b21b6" stroke-width="2" stroke-dasharray="3,2"/>
  <line x1="630" y1="385" x2="640" y2="385" stroke="#991b1b" stroke-width="2" marker-end="url(#arrowRed)"/>

  <defs>
    <marker id="arrowCyan" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#0c4a6e"/>
    </marker>
    <marker id="arrowRed" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#991b1b"/>
    </marker>
  </defs>

  <!-- Tabela -->
  <text x="40" y="480" font-size="20" font-weight="700" fill="#0e7490">📋 Tabela dos 3 Grupos</text>

  <rect x="40" y="500" width="1120" height="280" fill="white" rx="12"/>

  <!-- Header -->
  <rect x="40" y="500" width="1120" height="36" fill="#06b6d4" rx="12 12 0 0"/>
  <text x="240" y="523" font-size="12" font-weight="700" fill="white">Caracteristica</text>
  <text x="510" y="523" font-size="12" font-weight="700" fill="white">🟦 Tiazidicos</text>
  <text x="770" y="523" font-size="12" font-weight="700" fill="white">🟪 Alca</text>
  <text x="1010" y="523" font-size="12" font-weight="700" fill="white">🟥 Poupadores K+</text>

  <!-- Linha potencia -->
  <text x="60" y="560" font-size="11" font-weight="700">Potencia</text>
  <text x="430" y="560" font-size="11" fill="#475569">Moderada</text>
  <text x="700" y="560" font-size="11" fill="#475569">ALTA (mais potente!)</text>
  <text x="950" y="560" font-size="11" fill="#475569">Fraca</text>

  <line x1="40" y1="575" x2="1160" y2="575" stroke="#e2e8f0"/>
  <text x="60" y="600" font-size="11" font-weight="700">HAS</text>
  <text x="430" y="600" font-size="11" fill="#10b981" font-weight="700">✓ 1a linha</text>
  <text x="700" y="600" font-size="11" fill="#475569">Emergencia</text>
  <text x="950" y="600" font-size="11" fill="#94a3b8">✗ Fraco</text>

  <line x1="40" y1="615" x2="1160" y2="615" stroke="#e2e8f0"/>
  <text x="60" y="640" font-size="11" font-weight="700">IC desc.</text>
  <text x="430" y="640" font-size="11" fill="#475569">Fraco</text>
  <text x="700" y="640" font-size="11" fill="#10b981" font-weight="700">✓ 1a escolha</text>
  <text x="950" y="640" font-size="11" fill="#475569">Espironolactona</text>

  <line x1="40" y1="655" x2="1160" y2="655" stroke="#e2e8f0"/>
  <text x="60" y="680" font-size="11" font-weight="700">Edema pulmao</text>
  <text x="430" y="680" font-size="11" fill="#94a3b8">Ineficaz</text>
  <text x="700" y="680" font-size="11" fill="#10b981" font-weight="700">✓ ABSOLUTA</text>
  <text x="950" y="680" font-size="11" fill="#94a3b8">Ineficaz</text>

  <line x1="40" y1="695" x2="1160" y2="695" stroke="#e2e8f0"/>
  <text x="60" y="720" font-size="11" font-weight="700">TFG &lt; 30</text>
  <text x="430" y="720" font-size="11" fill="#94a3b8">✗ Perde efeito</text>
  <text x="700" y="720" font-size="11" fill="#10b981" font-weight="700">✓ Ainda funciona</text>

  <line x1="40" y1="735" x2="1160" y2="735" stroke="#e2e8f0"/>
  <text x="60" y="760" font-size="11" font-weight="700">K+ serico</text>
  <text x="430" y="760" font-size="11" fill="#dc2626">↓ Hipopotassemia</text>
  <text x="700" y="760" font-size="11" fill="#dc2626">↓ Severa</text>
  <text x="950" y="760" font-size="11" fill="#dc2626">↑ HIPERCALEMIA!</text>

  <!-- Mnemonicos -->
  <text x="40" y="820" font-size="20" font-weight="700" fill="#0e7490">🧠 Mnemonicos</text>

  <rect x="40" y="840" width="540" height="110" fill="white" rx="12" stroke="#0891b2" stroke-width="2"/>
  <rect x="50" y="855" width="80" height="22" fill="#0891b2" rx="4"/>
  <text x="90" y="870" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 1</text>
  <text x="140" y="870" font-size="13" font-weight="700">"OH DALT" - Proximal → Alca → Distal → Aldosterona</text>
  <text x="60" y="900" font-size="11" fill="#475569">Quanto mais proximal, mais potente (ate Henle).</text>
  <text x="60" y="918" font-size="11" fill="#475569">Poupadores sao sempre fracos.</text>
  <text x="60" y="936" font-size="11" font-weight="700" fill="#0891b2">💡 Furosemida = FURO de agua (mais potente)</text>

  <rect x="620" y="840" width="540" height="110" fill="white" rx="12" stroke="#7c3aed" stroke-width="2"/>
  <rect x="630" y="855" width="80" height="22" fill="#7c3aed" rx="4"/>
  <text x="670" y="870" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 2</text>
  <text x="720" y="870" font-size="13" font-weight="700">DRC avancada = SEMPRE alca</text>
  <text x="640" y="900" font-size="11" fill="#475569">Tiazidicos perdem efeito com TFG &lt; 30 mL/min.</text>
  <text x="640" y="918" font-size="11" fill="#475569">Furosemida AINDA FUNCIONA.</text>
  <text x="640" y="936" font-size="11" font-weight="700" fill="#7c3aed">💡 DRC avancada = furosemida sempre</text>

  <rect x="40" y="970" width="1120" height="100" fill="white" rx="12" stroke="#dc2626" stroke-width="2"/>
  <rect x="50" y="985" width="80" height="22" fill="#dc2626" rx="4"/>
  <text x="90" y="1000" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 3</text>
  <text x="140" y="1000" font-size="14" font-weight="700">"EspironoLACTONA" = Loiro de K+ (poupa)</text>
  <text x="60" y="1030" font-size="12" fill="#dc2626" font-weight="700">⚠️ Espironolactona + IECA/BRA = HIPERCALEMIA GRAVE! Monitorar K+!</text>
  <text x="60" y="1050" font-size="12" fill="#475569">Espirilo = Lactona que gira o K+. Em IC FEr, sempre considerar (estudo RALES).</text>

  <!-- Resumo -->
  <text x="40" y="1110" font-size="20" font-weight="700" fill="#0e7490">🎯 Quando Escolher</text>

  <rect x="40" y="1130" width="370" height="200" fill="#fef3c7" rx="12"/>
  <rect x="40" y="1130" width="6" height="200" fill="#ca8a04"/>
  <text x="60" y="1160" font-size="16" font-weight="700" fill="#92400e">HAS 1a linha</text>
  <text x="60" y="1185" font-size="12">HCTZ 12,5-25mg</text>
  <text x="60" y="1205" font-size="12">+ IECA/BRA</text>
  <text x="60" y="1225" font-size="12" fill="#475569">Barato, 1x/dia</text>

  <rect x="430" y="1130" width="370" height="200" fill="#f3e8ff" rx="12"/>
  <rect x="430" y="1130" width="6" height="200" fill="#7c3aed"/>
  <text x="450" y="1160" font-size="16" font-weight="700" fill="#7c3aed">IC descompensada</text>
  <text x="450" y="1185" font-size="12">Furosemida 40-80mg IV</text>
  <text x="450" y="1205" font-size="12">+ Espironolactona 25-50mg</text>

  <rect x="820" y="1130" width="340" height="200" fill="#fee2e2" rx="12"/>
  <rect x="820" y="1130" width="6" height="200" fill="#dc2626"/>
  <text x="840" y="1160" font-size="16" font-weight="700" fill="#dc2626">Edema agudo pulmao</text>
  <text x="840" y="1185" font-size="12">Furosemida 40-80mg IV</text>
  <text x="840" y="1205" font-size="12">Posologia agressiva</text>
  <text x="840" y="1225" font-size="12" fill="#475569">(emergencia!)</text>

  <!-- Footer -->
  <text x="600" y="1370" font-size="12" fill="#94a3b8" text-anchor="middle">Modulo Diureticos | Auxilio Farmacia</text>
</svg>"""

# ========== PREVIEW ARA II ==========
ARA_II_SVG_RAW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <defs>
    <linearGradient id="bgARA" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f3e8ff"/>
      <stop offset="100%" stop-color="#e9d5ff"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1400" fill="url(#bgARA)"/>

  <!-- Header -->
  <rect x="40" y="40" width="80" height="80" fill="#a855f7" rx="16"/>
  <text x="80" y="98" font-size="40" text-anchor="middle">💎</text>
  <text x="140" y="75" font-size="32" font-weight="700" fill="#581c87" font-family="Playfair Display">ARA II - Alisquireno</text>
  <text x="140" y="105" font-size="14" fill="#7e22ce">O primeiro inibidor direto da renina</text>

  <!-- Diagrama SRAA -->
  <rect x="40" y="160" width="1120" height="240" fill="white" rx="12"/>
  <text x="60" y="190" font-size="18" font-weight="700" fill="#581c87">🧬 Cascata do SRAA - Onde Cada Droga Age</text>

  <!-- Renina -->
  <rect x="60" y="240" width="100" height="50" fill="#fef3c7" stroke="#ca8a04" stroke-width="2" rx="6"/>
  <text x="110" y="265" font-size="11" font-weight="700" fill="#713f12" text-anchor="middle">RENINA</text>
  <text x="110" y="280" font-size="9" fill="#92400e" text-anchor="middle">(do rim)</text>

  <!-- Seta -->
  <line x1="165" y1="265" x2="195" y2="265" stroke="#475569" stroke-width="2" marker-end="url(#arrowA)"/>

  <!-- Angiotensinogenio -->
  <rect x="200" y="240" width="120" height="50" fill="#fde68a" stroke="#ca8a04" stroke-width="2" rx="6"/>
  <text x="260" y="265" font-size="10" fill="#713f12" text-anchor="middle">Angiotensinogenio</text>
  <text x="260" y="280" font-size="9" fill="#92400e" text-anchor="middle">(do figado)</text>

  <line x1="325" y1="265" x2="355" y2="265" stroke="#475569" stroke-width="2" marker-end="url(#arrowA)"/>

  <!-- Angiotensina I -->
  <rect x="360" y="240" width="120" height="50" fill="#fbcfe8" stroke="#be185c" stroke-width="2" rx="6"/>
  <text x="420" y="270" font-size="10" font-weight="700" fill="#831843" text-anchor="middle">ANGIOTENSINA I</text>

  <line x1="485" y1="265" x2="515" y2="265" stroke="#475569" stroke-width="2" marker-end="url(#arrowA)"/>

  <!-- ECA -->
  <rect x="520" y="240" width="60" height="50" fill="#dc2626" stroke="#7f1d1d" stroke-width="2" rx="6"/>
  <text x="550" y="270" font-size="11" font-weight="700" fill="white" text-anchor="middle">ECA</text>

  <line x1="585" y1="265" x2="615" y2="265" stroke="#475569" stroke-width="2" marker-end="url(#arrowA)"/>

  <!-- Angiotensina II -->
  <rect x="620" y="240" width="120" height="50" fill="#7f1d1d" stroke="#450a0a" stroke-width="2" rx="6"/>
  <text x="680" y="270" font-size="10" font-weight="700" fill="white" text-anchor="middle">ANGIOTENSINA II</text>

  <line x1="745" y1="265" x2="775" y2="265" stroke="#475569" stroke-width="2" marker-end="url(#arrowA)"/>

  <!-- AT1 -->
  <rect x="780" y="240" width="80" height="50" fill="#fbbf24" stroke="#92400e" stroke-width="2" rx="6"/>
  <text x="820" y="265" font-size="11" font-weight="700" fill="#7f1d1d" text-anchor="middle">AT1</text>
  <text x="820" y="280" font-size="9" fill="#7f1d1d" text-anchor="middle">(receptor)</text>

  <!-- Efeito final -->
  <rect x="280" y="340" width="500" height="40" fill="#fee2e2" stroke="#dc2626" stroke-width="2" rx="6"/>
  <text x="530" y="365" font-size="12" font-weight="700" fill="#991b1b" text-anchor="middle">VASOCONSTRICAO + RETENCAO DE Na+ + ALDOSTERONA</text>

  <line x1="820" y1="290" x2="530" y2="335" stroke="#dc2626" stroke-width="2" marker-end="url(#arrowA)"/>

  <!-- Locais de acao -->
  <rect x="540" y="305" width="40" height="20" fill="#dc2626" rx="2"/>
  <text x="560" y="320" font-size="9" font-weight="700" fill="white" text-anchor="middle">IECA</text>

  <rect x="810" y="305" width="40" height="20" fill="#dc2626" rx="2"/>
  <text x="830" y="320" font-size="9" font-weight="700" fill="white" text-anchor="middle">BRA</text>

  <rect x="80" y="305" width="100" height="20" fill="#a855f7" rx="2"/>
  <text x="130" y="320" font-size="9" font-weight="700" fill="white" text-anchor="middle" font-weight="700">ALISQUIRENO</text>

  <defs>
    <marker id="arrowA" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
    </marker>
  </defs>

  <!-- Tabela -->
  <text x="40" y="450" font-size="20" font-weight="700" fill="#581c87">📋 Tabela Comparativa</text>

  <rect x="40" y="470" width="1120" height="280" fill="white" rx="12"/>

  <rect x="40" y="470" width="1120" height="36" fill="#a855f7" rx="12 12 0 0"/>
  <text x="220" y="493" font-size="12" font-weight="700" fill="white">Caracteristica</text>
  <text x="540" y="493" font-size="12" font-weight="700" fill="white">IECA</text>
  <text x="790" y="493" font-size="12" font-weight="700" fill="white">BRA</text>
  <text x="1020" y="493" font-size="12" font-weight="700" fill="white">ARA II</text>

  <text x="60" y="530" font-size="11" font-weight="700">Ponto de acao</text>
  <text x="450" y="530" font-size="11" fill="#475569">Bloqueia ECA</text>
  <text x="700" y="530" font-size="11" fill="#475569">Bloqueia AT1</text>
  <text x="940" y="530" font-size="11" fill="#a855f7" font-weight="700">Bloqueia renina</text>

  <line x1="40" y1="545" x2="1160" y2="545" stroke="#e2e8f0"/>
  <text x="60" y="570" font-size="11" font-weight="700">Bradicinina</text>
  <text x="450" y="570" font-size="11" fill="#dc2626">↑ Aumenta (causa tosse)</text>
  <text x="700" y="570" font-size="11" fill="#10b981">NAO afeta</text>
  <text x="940" y="570" font-size="11" fill="#10b981">NAO afeta</text>

  <line x1="40" y1="585" x2="1160" y2="585" stroke="#e2e8f0"/>
  <text x="60" y="610" font-size="11" font-weight="700">Reducao PRA</text>
  <text x="450" y="610" font-size="11" fill="#dc2626">↑ Aumenta (reativa SRAA)</text>
  <text x="700" y="610" font-size="11" fill="#dc2626">↑ Aumenta</text>
  <text x="940" y="610" font-size="11" fill="#10b981" font-weight="700">✓ UNICO que REDUZ</text>

  <line x1="40" y1="625" x2="1160" y2="625" stroke="#e2e8f0"/>
  <text x="60" y="650" font-size="11" font-weight="700">Evidencias</text>
  <text x="450" y="650" font-size="11" fill="#10b981" font-weight="700">✓ FORTISSIMAS</text>
  <text x="700" y="650" font-size="11" fill="#10b981" font-weight="700">✓ FORTISSIMAS</text>
  <text x="940" y="650" font-size="11" fill="#dc2626">✗ FRACAS (estudos negativos)</text>

  <line x1="40" y1="665" x2="1160" y2="665" stroke="#e2e8f0"/>
  <text x="60" y="690" font-size="11" font-weight="700">Custo</text>
  <text x="450" y="690" font-size="11" fill="#10b981">Barato (genericos)</text>
  <text x="700" y="690" font-size="11" fill="#10b981">Barato (genericos)</text>
  <text x="940" y="690" font-size="11" fill="#dc2626">CARO (R$ 200-400/mes)</text>

  <line x1="40" y1="705" x2="1160" y2="705" stroke="#e2e8f0"/>
  <text x="60" y="730" font-size="11" font-weight="700">Status</text>
  <text x="450" y="730" font-size="11" fill="#10b981" font-weight="700">1a escolha</text>
  <text x="700" y="730" font-size="11" fill="#10b981" font-weight="700">1a escolha</text>
  <text x="940" y="730" font-size="11" fill="#dc2626" font-weight="700">NAO recomendado</text>

  <!-- Mnemonicos -->
  <text x="40" y="790" font-size="20" font-weight="700" fill="#581c87">🧠 Mnemonicos</text>

  <rect x="40" y="810" width="540" height="130" fill="white" rx="12" stroke="#a855f7" stroke-width="2"/>
  <rect x="50" y="825" width="80" height="22" fill="#a855f7" rx="4"/>
  <text x="90" y="840" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 1</text>
  <text x="140" y="840" font-size="14" font-weight="700">"ALI = INICIO" (bloqueia renina)</text>
  <text x="60" y="880" font-size="12" fill="#475569">Alisquireno bloqueia a renina, que e a</text>
  <text x="60" y="898" font-size="12" fill="#475569">PRIMEIRA enzima da cascata.</text>
  <text x="60" y="916" font-size="12" fill="#a855f7" font-weight="700">💡 Teoricamente o mais "radical"</text>

  <rect x="620" y="810" width="540" height="130" fill="white" rx="12" stroke="#dc2626" stroke-width="2"/>
  <rect x="630" y="825" width="100" height="22" fill="#dc2626" rx="4"/>
  <text x="680" y="840" font-size="11" font-weight="700" fill="white" text-anchor="middle">REALIDADE</text>
  <text x="740" y="840" font-size="14" font-weight="700">"ALI esqueceu o caminho"</text>
  <text x="640" y="880" font-size="11" fill="#475569">Estudo ALTITUDE (2012): aumento de eventos</text>
  <text x="640" y="898" font-size="11" fill="#475569">adversos. ASTRONAUT (2011): suspensa por</text>
  <text x="640" y="916" font-size="11" fill="#475569">falta de eficacia.</text>

  <rect x="40" y="960" width="1120" height="100" fill="white" rx="12" stroke="#dc2626" stroke-width="2"/>
  <text x="60" y="990" font-size="14" font-weight="700" fill="#dc2626">⚠️ REGRA DE OURO: NUNCA combine Alisquireno com IECA ou BRA!</text>
  <text x="60" y="1015" font-size="12" fill="#475569">Combinacao aumenta risco de hipercalemia, hipotensao e lesao renal aguda.</text>
  <text x="60" y="1035" font-size="12" fill="#475569">Por isso, o uso clinico e raro. Reservado apenas para casos selecionados.</text>

  <!-- Resumo -->
  <text x="40" y="1110" font-size="20" font-weight="700" fill="#581c87">🎯 Resumo dos Inibidores SRAA</text>

  <rect x="40" y="1130" width="370" height="200" fill="#fee2e2" rx="12"/>
  <rect x="40" y="1130" width="6" height="200" fill="#dc2626"/>
  <text x="60" y="1160" font-size="16" font-weight="700" fill="#dc2626">IECA (-pril)</text>
  <text x="60" y="1190" font-size="12">✓ 1a linha</text>
  <text x="60" y="1210" font-size="12">✓ Pos-IAM, IC</text>
  <text x="60" y="1230" font-size="12">✓ DM proteinuria</text>
  <text x="60" y="1250" font-size="12" fill="#dc2626">⚠️ 10-20% tosse</text>

  <rect x="430" y="1130" width="370" height="200" fill="#fef3c7" rx="12"/>
  <rect x="430" y="1130" width="6" height="200" fill="#ca8a04"/>
  <text x="450" y="1160" font-size="16" font-weight="700" fill="#92400e">BRA (-sartana)</text>
  <text x="450" y="1190" font-size="12">✓ 1a linha</text>
  <text x="450" y="1210" font-size="12">✓ Alternativa a IECA</text>
  <text x="450" y="1230" font-size="12">✓ Mesma eficacia</text>
  <text x="450" y="1250" font-size="12" fill="#10b981">✓ Sem tosse</text>

  <rect x="820" y="1130" width="340" height="200" fill="#f3e8ff" rx="12"/>
  <rect x="820" y="1130" width="6" height="200" fill="#a855f7"/>
  <text x="840" y="1160" font-size="16" font-weight="700" fill="#a855f7">ARA II (-quireno)</text>
  <text x="840" y="1190" font-size="12">✗ Uso raro</text>
  <text x="840" y="1210" font-size="12">✗ Caro</text>
  <text x="840" y="1230" font-size="12">✗ Sem evidencias</text>
  <text x="840" y="1250" font-size="12" fill="#dc2626">⚠️ NAO com IECA/BRA</text>

  <!-- Footer -->
  <text x="600" y="1370" font-size="12" fill="#94a3b8" text-anchor="middle">Modulo ARA II - Alisquireno | Auxilio Farmacia</text>
</svg>"""

# ========== PREVIEW BETABLOQUEADORES ==========
BETABLOQ_SVG_RAW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <defs>
    <linearGradient id="bgBeta" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef3c7"/>
      <stop offset="100%" stop-color="#fed7aa"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1400" fill="url(#bgBeta)"/>

  <!-- Header -->
  <rect x="40" y="40" width="80" height="80" fill="#f97316" rx="16"/>
  <text x="80" y="98" font-size="40" text-anchor="middle">❤️</text>
  <text x="140" y="75" font-size="32" font-weight="700" fill="#7c2d12" font-family="Playfair Display">Betabloqueadores - Cardio vs Nao-Cardio</text>
  <text x="140" y="105" font-size="14" fill="#9a3412">Seletividade beta-1: a chave da diferenca</text>

  <!-- Tabela -->
  <text x="40" y="170" font-size="20" font-weight="700" fill="#7c2d12">📋 Tabela Comparativa dos Betabloqueadores</text>

  <rect x="40" y="190" width="1120" height="280" fill="white" rx="12"/>

  <rect x="40" y="190" width="1120" height="36" fill="#f97316" rx="12 12 0 0"/>
  <text x="220" y="213" font-size="12" font-weight="700" fill="white">Caracteristica</text>
  <text x="500" y="213" font-size="12" font-weight="700" fill="white">🟢 Cardiosseletivos (beta-1)</text>
  <text x="780" y="213" font-size="12" font-weight="700" fill="white">🟠 Nao-seletivos (beta-1 e beta-2)</text>
  <text x="1060" y="213" font-size="12" font-weight="700" fill="white">🟣 Com ASI</text>

  <text x="60" y="250" font-size="11" font-weight="700">Principais</text>
  <text x="350" y="250" font-size="10" fill="#475569">Atenolol, Metoprolol, Bisoprolol,</text>
  <text x="350" y="265" font-size="10" fill="#475569">Nebivolol, Esmolol</text>
  <text x="700" y="250" font-size="10" fill="#475569">Propranolol, Nadolol, Timolol,</text>
  <text x="700" y="265" font-size="10" fill="#475569">Carvedilol, Labetalol</text>
  <text x="1010" y="250" font-size="10" fill="#475569">Pindolol, Acebutolol</text>

  <line x1="40" y1="280" x2="1160" y2="280" stroke="#e2e8f0"/>
  <text x="60" y="305" font-size="11" font-weight="700">IC FEr</text>
  <text x="350" y="305" font-size="10" fill="#10b981" font-weight="700">✓ Bisoprolol, Metoprolol succ,</text>
  <text x="350" y="320" font-size="10" fill="#10b981" font-weight="700">  Nebivolol (3 aprovados!)</text>
  <text x="700" y="305" font-size="10" fill="#10b981" font-weight="700">✓ Carvedilol</text>
  <text x="1010" y="305" font-size="10" fill="#dc2626">✗ NAO</text>

  <line x1="40" y1="335" x2="1160" y2="335" stroke="#e2e8f0"/>
  <text x="60" y="360" font-size="11" font-weight="700">Enxaqueca</text>
  <text x="350" y="360" font-size="10" fill="#475569">Metoprolol</text>
  <text x="700" y="360" font-size="10" fill="#10b981" font-weight="700">✓ Propranolol (melhor!)</text>

  <line x1="40" y1="380" x2="1160" y2="380" stroke="#e2e8f0"/>
  <text x="60" y="405" font-size="11" font-weight="700">Asma/DPOC</text>
  <text x="350" y="405" font-size="10" fill="#ca8a04">Relativa</text>
  <text x="700" y="405" font-size="10" fill="#dc2626" font-weight="700">⚠️ ABSOLUTA</text>
  <text x="1010" y="405" font-size="10" fill="#dc2626" font-weight="700">⚠️ ABSOLUTA</text>

  <line x1="40" y1="425" x2="1160" y2="425" stroke="#e2e8f0"/>
  <text x="60" y="450" font-size="11" font-weight="700">DM insulinodep.</text>
  <text x="350" y="450" font-size="10" fill="#ca8a04">Relativa</text>
  <text x="700" y="450" font-size="10" fill="#dc2626" font-weight="700">⚠️ Mascara hipoglicemia</text>

  <!-- Mnemonicos -->
  <text x="40" y="510" font-size="20" font-weight="700" fill="#7c2d12">🧠 4 Mnemonicos</text>

  <rect x="40" y="530" width="540" height="100" fill="white" rx="12" stroke="#10b981" stroke-width="2"/>
  <rect x="50" y="545" width="80" height="22" fill="#10b981" rx="4"/>
  <text x="90" y="560" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 1</text>
  <text x="140" y="560" font-size="14" font-weight="700">"Cardio = CORacao SEGURO"</text>
  <text x="60" y="595" font-size="11" fill="#475569">Cardiosseletivos agem APENAS no coracao. Mais seguros em asma leve, DPOC leve, DM.</text>

  <rect x="620" y="530" width="540" height="100" fill="white" rx="12" stroke="#f97316" stroke-width="2"/>
  <rect x="630" y="545" width="80" height="22" fill="#f97316" rx="4"/>
  <text x="670" y="560" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 2</text>
  <text x="720" y="560" font-size="14" font-weight="700">"Nao-seletivo = NAO em asma/DM"</text>
  <text x="640" y="595" font-size="11" fill="#475569">Bloqueiam beta-2: broncoespasmo (asma), mascaram hipoglicemia (DM).</text>

  <rect x="40" y="650" width="540" height="100" fill="white" rx="12" stroke="#7c3aed" stroke-width="2"/>
  <rect x="50" y="665" width="80" height="22" fill="#7c3aed" rx="4"/>
  <text x="90" y="680" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 3</text>
  <text x="140" y="680" font-size="14" font-weight="700">"Carvedilol = 3 em 1 (alfa+beta-1+beta-2)"</text>
  <text x="60" y="715" font-size="11" fill="#475569">Unico com alfa-1 tambem. Vasodilatador. Excelente IC + HAS.</text>

  <rect x="620" y="650" width="540" height="100" fill="white" rx="12" stroke="#dc2626" stroke-width="2"/>
  <rect x="630" y="665" width="80" height="22" fill="#dc2626" rx="4"/>
  <text x="670" y="680" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 4</text>
  <text x="720" y="680" font-size="14" font-weight="700">"ASI = sem taquicardia reflexa"</text>
  <text x="640" y="715" font-size="11" fill="#475569">Atletas/jovens com FC baixa. NAO para IC (sem beneficio prognostico).</text>

  <!-- Desafio -->
  <text x="40" y="780" font-size="20" font-weight="700" fill="#7c2d12">💡 Desafio Clinico</text>

  <rect x="40" y="800" width="1120" height="280" fill="white" rx="12"/>

  <rect x="60" y="820" width="1080" height="40" fill="#f0fdfa" rx="6"/>
  <text x="80" y="845" font-size="12" fill="#1e293b"><tspan font-weight="700">Caso:</tspan> Mulher 65 anos, HAS, IC com FEr 35%, DM2, DPOC leve (VEF1 70%). Prescricao: Propranolol 40mg 3x/dia.</text>

  <text x="60" y="890" font-size="14" fill="#475569"><tspan font-weight="700">❓ O que voce mudaria? Qual BB escolheria e por que?</tspan></text>

  <rect x="60" y="910" width="1080" height="160" fill="#fef3c7" rx="6"/>
  <text x="80" y="935" font-size="13" font-weight="700" fill="#dc2626">❌ PROPRANOLOL ESTA ERRADO neste paciente!</text>

  <text x="80" y="965" font-size="11" fill="#1e293b" font-weight="700">Problemas:</text>
  <text x="100" y="985" font-size="11" fill="#1e293b">1. Nao-seletivo em DPOC: broncoespasmo</text>
  <text x="100" y="1003" font-size="11" fill="#1e293b">2. Nao-seletivo em DM2: mascara hipoglicemia</text>
  <text x="100" y="1021" font-size="11" fill="#1e293b">3. Nao tem indicacao para IC (so Bisoprolol/Carvedilol/Metoprolol succ/Nebivolol)</text>

  <text x="80" y="1045" font-size="13" font-weight="700" fill="#10b981">✅ MELHOR ESCOLHA: Bisoprolol 2,5-5mg 1x/dia</text>
  <text x="100" y="1063" font-size="11" fill="#1e293b">Cardiosseletivo (menor risco), aprovado para IC, 1x/dia, titulacao gradual</text>

  <!-- Resumo -->
  <text x="40" y="1110" font-size="20" font-weight="700" fill="#7c2d12">🎯 Quando Escolher</text>

  <rect x="40" y="1130" width="270" height="200" fill="#d1fae5" rx="12"/>
  <rect x="40" y="1130" width="6" height="200" fill="#10b981"/>
  <text x="60" y="1160" font-size="15" font-weight="700" fill="#10b981">Bisoprolol</text>
  <text x="60" y="1190" font-size="11">IC FEr</text>
  <text x="60" y="1210" font-size="11">HAS + IC</text>
  <text x="60" y="1230" font-size="11">1x/dia</text>
  <text x="60" y="1250" font-size="11" fill="#475569">Cardiosseletivo</text>

  <rect x="330" y="1130" width="270" height="200" fill="#fed7aa" rx="12"/>
  <rect x="330" y="1130" width="6" height="200" fill="#f97316"/>
  <text x="350" y="1160" font-size="15" font-weight="700" fill="#f97316">Carvedilol</text>
  <text x="350" y="1190" font-size="11">IC FEr</text>
  <text x="350" y="1210" font-size="11">Pos-IAM</text>
  <text x="350" y="1230" font-size="11">2x/dia</text>
  <text x="350" y="1250" font-size="11" fill="#475569">Alfa + Beta</text>

  <rect x="620" y="1130" width="270" height="200" fill="#dbeafe" rx="12"/>
  <rect x="620" y="1130" width="6" height="200" fill="#2563eb"/>
  <text x="640" y="1160" font-size="15" font-weight="700" fill="#2563eb">Metoprolol succ</text>
  <text x="640" y="1190" font-size="11">IC FEr</text>
  <text x="640" y="1210" font-size="11">Pos-IAM</text>
  <text x="640" y="1230" font-size="11">Angina</text>

  <rect x="910" y="1130" width="250" height="200" fill="#fee2e2" rx="12"/>
  <rect x="910" y="1130" width="6" height="200" fill="#dc2626"/>
  <text x="930" y="1160" font-size="15" font-weight="700" fill="#dc2626">Propranolol</text>
  <text x="930" y="1190" font-size="11">HAS + enxaqueca</text>
  <text x="930" y="1210" font-size="11">HAS + tremor</text>
  <text x="930" y="1230" font-size="11">Hipertireoidismo</text>
  <text x="930" y="1250" font-size="11" fill="#dc2626">⚠️ Evitar asma</text>

  <!-- Footer -->
  <text x="600" y="1370" font-size="12" fill="#94a3b8" text-anchor="middle">Modulo Betabloqueadores | Auxilio Farmacia</text>
</svg>"""


def main():
    OUTPUT.mkdir(exist_ok=True, parents=True)

    previews = [
        (IECA_BRA_SVG_RAW, "ieca_bra.png"),
        (DIURETICOS_SVG_RAW, "diureticos.png"),
        (ARA_II_SVG_RAW, "ara_ii.png"),
        (BETABLOQ_SVG_RAW, "betabloqueadores.png"),
    ]

    print("=" * 60)
    print("📸 Gerando previews SVG dos 4 modulos...")
    print("=" * 60)

    for svg, fname in previews:
        # Salva SVG
        svg_path = OUTPUT / fname.replace(".png", ".svg")
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg)

        # Converte para PNG
        png_path = OUTPUT / fname
        # Substitui fontes para DejaVu (disponivel no sistema)
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        svg_content = svg_content.replace('Inter, sans-serif', 'DejaVu-Sans')
        svg_content = svg_content.replace("'Inter, sans-serif'", 'DejaVu-Sans')
        svg_content = svg_content.replace('Playfair Display, serif', 'DejaVu-Serif')
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        try:
            result = subprocess.run(
                ['convert', '-density', '90', '-background', 'white',
                 f'svg:{svg_path}', f'png24:{png_path}'],
                check=True, timeout=120, capture_output=True
            )
            print(f"✅ {fname}")
        except subprocess.CalledProcessError as e:
            print(f"❌ {fname}: {e.stderr.decode()[:200]}")

    print()
    print("=" * 60)
    print("✅ Previews gerados!")
    print("=" * 60)


if __name__ == "__main__":
    main()