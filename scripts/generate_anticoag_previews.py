#!/usr/bin/env python3
"""Gera previews SVG para Antiarritmicos e Anticoagulantes"""
import re
import subprocess
from pathlib import Path

OUTPUT = Path("/workspace/output/atualizacoes")

# ========== PREVIEW ANTIARRIITMICOS ==========
ANTIARR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <defs>
    <linearGradient id="bgArr" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fce7f3"/>
      <stop offset="100%" stop-color="#fbcfe8"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1400" fill="url(#bgArr)"/>

  <!-- Header -->
  <rect x="40" y="40" width="80" height="80" fill="#ec4899" rx="16"/>
  <text x="80" y="98" font-size="40" text-anchor="middle">⚡</text>
  <text x="140" y="75" font-size="30" font-weight="700" fill="#831843" font-family="DejaVu-Serif">Antiarritmicos - Vaughan-Williams</text>
  <text x="140" y="105" font-size="14" fill="#9d174d">Classes I, II, III e IV - Onde cada uma age</text>

  <!-- Diagrama do Potencial de Acao -->
  <rect x="40" y="140" width="1120" height="280" fill="white" rx="12"/>
  <text x="60" y="170" font-size="16" font-weight="700" fill="#831843">🧬 Potencial de Acao do Cardiomiocito</text>

  <!-- Eixos -->
  <line x1="100" y1="380" x2="1140" y2="380" stroke="#475569" stroke-width="2"/>
  <line x1="100" y1="200" x2="100" y2="380" stroke="#475569" stroke-width="2"/>
  <text x="620" y="405" font-size="11" fill="#475569" text-anchor="middle">Tempo (ms)</text>
  <text x="60" y="290" font-size="11" fill="#475569" text-anchor="middle" transform="rotate(-90 60 290)">mV</text>

  <!-- Curva do potencial -->
  <path d="M 110 360 L 130 360 L 150 220 L 180 210 L 280 230 L 500 320 L 800 350 L 1100 360" fill="none" stroke="#1e293b" stroke-width="3"/>

  <!-- Fases -->
  <rect x="120" y="200" width="80" height="180" fill="#fef3c7" opacity="0.4"/>
  <text x="160" y="195" font-size="11" font-weight="700" fill="#92400e" text-anchor="middle">FASE 0</text>
  <text x="160" y="385" font-size="9" fill="#92400e" text-anchor="middle">Na+</text>

  <rect x="200" y="200" width="40" height="180" fill="#fde68a" opacity="0.4"/>
  <text x="220" y="195" font-size="11" font-weight="700" fill="#92400e" text-anchor="middle">FASE 1</text>

  <rect x="240" y="200" width="260" height="180" fill="#fbcfe8" opacity="0.4"/>
  <text x="370" y="195" font-size="11" font-weight="700" fill="#831843" text-anchor="middle">FASE 2 - Plateau (Ca2+)</text>

  <rect x="500" y="200" width="320" height="180" fill="#e9d5ff" opacity="0.4"/>
  <text x="660" y="195" font-size="11" font-weight="700" fill="#581c87" text-anchor="middle">FASE 3 - Repolarizacao (K+)</text>

  <rect x="820" y="200" width="280" height="180" fill="#dbeafe" opacity="0.4"/>
  <text x="960" y="195" font-size="11" font-weight="700" fill="#1e3a8a" text-anchor="middle">FASE 4 - Repouso</text>

  <!-- Locais de acao -->
  <rect x="140" y="245" width="60" height="20" fill="#dc2626" rx="3"/>
  <text x="170" y="260" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE I</text>

  <rect x="320" y="280" width="60" height="20" fill="#f59e0b" rx="3"/>
  <text x="350" y="295" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE IV</text>

  <rect x="600" y="310" width="60" height="20" fill="#7c3aed" rx="3"/>
  <text x="630" y="325" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE III</text>

  <rect x="900" y="340" width="60" height="20" fill="#0ea5e9" rx="3"/>
  <text x="930" y="355" font-size="10" font-weight="700" fill="white" text-anchor="middle">CLASSE II</text>

  <!-- Tabela -->
  <text x="40" y="460" font-size="20" font-weight="700" fill="#831843">📋 Classes de Vaughan-Williams</text>

  <rect x="40" y="480" width="1120" height="320" fill="white" rx="12"/>

  <rect x="40" y="480" width="1120" height="36" fill="#ec4899" rx="12 12 0 0"/>
  <text x="80" y="503" font-size="12" font-weight="700" fill="white">Classe</text>
  <text x="220" y="503" font-size="12" font-weight="700" fill="white">Mecanismo</text>
  <text x="500" y="503" font-size="12" font-weight="700" fill="white">Drogas</text>
  <text x="800" y="503" font-size="12" font-weight="700" fill="white">Indicacao</text>
  <text x="1000" y="503" font-size="12" font-weight="700" fill="white">Efeitos Adv</text>

  <text x="60" y="540" font-size="11" font-weight="700" fill="#dc2626">IA</text>
  <text x="220" y="540" font-size="10" fill="#475569">Bloqueio moderado Na+</text>
  <text x="500" y="540" font-size="10" fill="#475569">Quinidina, Procainamida</text>
  <text x="800" y="540" font-size="10" fill="#475569">TV, FA</text>

  <line x1="40" y1="555" x2="1160" y2="555" stroke="#e2e8f0"/>
  <text x="60" y="580" font-size="11" font-weight="700" fill="#ca8a04">IB</text>
  <text x="220" y="580" font-size="10" fill="#475569">Bloqueio fraco Na+</text>
  <text x="500" y="580" font-size="10" fill="#475569">Lidocaina, Mexiletina</text>
  <text x="800" y="580" font-size="10" fill="#475569">TV pos-IAM, intox. digit.</text>

  <line x1="40" y1="595" x2="1160" y2="595" stroke="#e2e8f0"/>
  <text x="60" y="620" font-size="11" font-weight="700" fill="#be185d">IC</text>
  <text x="220" y="620" font-size="10" fill="#475569">Bloqueio forte Na+</text>
  <text x="500" y="620" font-size="10" fill="#475569">Flecainida, Propafenona</text>
  <text x="800" y="620" font-size="10" fill="#475569">TPSV, FA s/ cardiopatia</text>
  <text x="1000" y="620" font-size="10" fill="#dc2626" font-weight="700">⚠️ NUNCA pos-IAM!</text>

  <line x1="40" y1="635" x2="1160" y2="635" stroke="#e2e8f0"/>
  <text x="60" y="660" font-size="11" font-weight="700" fill="#0ea5e9">II</text>
  <text x="220" y="660" font-size="10" fill="#475569">Reduz automaticidade</text>
  <text x="500" y="660" font-size="10" fill="#475569">Propranolol, Metoprolol</text>
  <text x="800" y="660" font-size="10" fill="#475569">Taquic. sinusal, FA</text>

  <line x1="40" y1="675" x2="1160" y2="675" stroke="#e2e8f0"/>
  <text x="60" y="700" font-size="11" font-weight="700" fill="#7c3aed">III</text>
  <text x="220" y="700" font-size="10" fill="#475569">Prolonga repolarizacao (K+)</text>
  <text x="500" y="700" font-size="10" fill="#475569">Amiodarona, Sotalol</text>
  <text x="800" y="700" font-size="10" fill="#475569">FA, TV (DROGA TOTAL)</text>

  <line x1="40" y1="715" x2="1160" y2="715" stroke="#e2e8f0"/>
  <text x="60" y="740" font-size="11" font-weight="700" fill="#f97316">IV</text>
  <text x="220" y="740" font-size="10" fill="#475569">Bloqueia Ca2+</text>
  <text x="500" y="740" font-size="10" fill="#475569">Verapamil, Diltiazem</text>
  <text x="800" y="740" font-size="10" fill="#475569">TPSV, controle FC em FA</text>

  <line x1="40" y1="755" x2="1160" y2="755" stroke="#e2e8f0"/>
  <text x="60" y="780" font-size="11" font-weight="700" fill="#1e3a8a">Outros</text>
  <text x="220" y="780" font-size="10" fill="#475569">Digitais, Adenosina, Mg</text>
  <text x="500" y="780" font-size="10" fill="#475569">Digoxina, Adenosina IV</text>
  <text x="800" y="780" font-size="10" fill="#475569">TPSV, IC + FA</text>

  <!-- Mnemonicos -->
  <text x="40" y="840" font-size="20" font-weight="700" fill="#831843">🧠 Mnemonicos</text>

  <rect x="40" y="860" width="540" height="110" fill="white" rx="12" stroke="#dc2626" stroke-width="2"/>
  <rect x="50" y="875" width="80" height="22" fill="#dc2626" rx="4"/>
  <text x="90" y="890" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 1</text>
  <text x="140" y="890" font-size="14" font-weight="700">DICA das subclasses</text>
  <text x="60" y="920" font-size="11" fill="#475569">IA = Quinidina/Procainamida (2 drogas)</text>
  <text x="60" y="938" font-size="11" fill="#475569">IB = Lidocaina/Mexiletina (2 drogas)</text>
  <text x="60" y="956" font-size="11" fill="#475569">IC = Flecainida/Propafenona (2 drogas)</text>

  <rect x="620" y="860" width="540" height="110" fill="white" rx="12" stroke="#7c3aed" stroke-width="2"/>
  <rect x="630" y="875" width="80" height="22" fill="#7c3aed" rx="4"/>
  <text x="670" y="890" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 2</text>
  <text x="720" y="890" font-size="14" font-weight="700">AMIODARONA = amiga de todos</text>
  <text x="640" y="920" font-size="11" fill="#475569">Amiodarona tem propriedades das 4 classes</text>
  <text x="640" y="938" font-size="11" fill="#475569">(predominio classe III). "Droga total"!</text>
  <text x="640" y="956" font-size="11" fill="#dc2626">⚠️ Efeitos: tireoide, pulmao, figado</text>

  <!-- Desafio -->
  <rect x="40" y="990" width="1120" height="200" fill="white" rx="12" stroke="#7c3aed" stroke-width="2"/>
  <text x="60" y="1020" font-size="16" font-weight="700" fill="#7c3aed">💡 Desafio Clinico</text>
  <rect x="60" y="1035" width="1080" height="35" fill="#f0fdfa" rx="6"/>
  <text x="80" y="1058" font-size="12" fill="#1e293b"><tspan font-weight="700">Caso:</tspan> Homem 70a, pos-IAM 15d, TV sustentada, hemodinamicamente estavel. Qual antiarritmico?</text>

  <rect x="60" y="1085" width="1080" height="90" fill="#fef3c7" rx="6"/>
  <text x="80" y="1108" font-size="13" font-weight="700" fill="#10b981">✅ RESPOSTA: AMIODARONA (Classe III)</text>
  <text x="100" y="1130" font-size="11" fill="#1e293b">- Exclui IC (CAST study!), IB (TV nao e melhor indicacao)</text>
  <text x="100" y="1148" font-size="11" fill="#1e293b">- Amiodarona = 1a escolha em arritmias ventriculares</text>
  <text x="100" y="1166" font-size="11" fill="#1e293b">- Alternativas: Lidocaina (IB) ou Procainamida (IA)</text>

  <!-- Resumo -->
  <text x="40" y="1220" font-size="20" font-weight="700" fill="#831843">🎯 Resumo das Classes</text>

  <rect x="40" y="1240" width="180" height="100" fill="#fee2e2" rx="12"/>
  <rect x="40" y="1240" width="6" height="100" fill="#dc2626"/>
  <text x="60" y="1265" font-size="13" font-weight="700" fill="#dc2626">Classe I</text>
  <text x="60" y="1290" font-size="10">Bloqueia Na+</text>
  <text x="60" y="1310" font-size="10" fill="#475569">Fase 0</text>

  <rect x="240" y="1240" width="180" height="100" fill="#dbeafe" rx="12"/>
  <rect x="240" y="1240" width="6" height="100" fill="#0ea5e9"/>
  <text x="260" y="1265" font-size="13" font-weight="700" fill="#0ea5e9">Classe II</text>
  <text x="260" y="1290" font-size="10">Betabloqueador</text>
  <text x="260" y="1310" font-size="10" fill="#475569">Fase 4</text>

  <rect x="440" y="1240" width="180" height="100" fill="#f3e8ff" rx="12"/>
  <rect x="440" y="1240" width="6" height="100" fill="#7c3aed"/>
  <text x="460" y="1265" font-size="13" font-weight="700" fill="#7c3aed">Classe III</text>
  <text x="460" y="1290" font-size="10">Bloqueia K+</text>
  <text x="460" y="1310" font-size="10" fill="#475569">Fase 3</text>

  <rect x="640" y="1240" width="180" height="100" fill="#fed7aa" rx="12"/>
  <rect x="640" y="1240" width="6" height="100" fill="#f97316"/>
  <text x="660" y="1265" font-size="13" font-weight="700" fill="#f97316">Classe IV</text>
  <text x="660" y="1290" font-size="10">Bloqueia Ca2+</text>
  <text x="660" y="1310" font-size="10" fill="#475569">Fase 2</text>

  <rect x="840" y="1240" width="320" height="100" fill="#fef3c7" rx="12"/>
  <rect x="840" y="1240" width="6" height="100" fill="#ca8a04"/>
  <text x="860" y="1265" font-size="13" font-weight="700" fill="#92400e">Outros (nao-VW)</text>
  <text x="860" y="1290" font-size="10">Digoxina (Na/K-ATPase)</text>
  <text x="860" y="1310" font-size="10">Adenosina IV, MgSO4</text>

  <!-- Footer -->
  <text x="600" y="1370" font-size="12" fill="#94a3b8" text-anchor="middle">Modulo Antiarritmicos | Auxilio Farmacia</text>
</svg>"""

# ========== PREVIEW ANTICOAGULANTES ==========
ANTICOAG_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 1400" font-family="DejaVu-Sans">
  <defs>
    <linearGradient id="bgAnti" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#dbeafe"/>
      <stop offset="100%" stop-color="#bfdbfe"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="1400" fill="url(#bgAnti)"/>

  <!-- Header -->
  <rect x="40" y="40" width="80" height="80" fill="#3b82f6" rx="16"/>
  <text x="80" y="98" font-size="40" text-anchor="middle">🩸</text>
  <text x="140" y="75" font-size="30" font-weight="700" fill="#1e3a8a" font-family="DejaVu-Serif">Anticoagulantes - Warfarina, DOACs, Heparina</text>
  <text x="140" y="105" font-size="14" fill="#1e40af">Cascata de coagulacao e onde cada droga age</text>

  <!-- Diagrama da Cascata -->
  <rect x="40" y="140" width="1120" height="280" fill="white" rx="12"/>
  <text x="60" y="170" font-size="16" font-weight="700" fill="#1e3a8a">🧬 Cascata de Coagulacao - Onde cada anticoagulante age</text>

  <!-- Via intrinseca label -->
  <text x="100" y="200" font-size="11" font-weight="700" fill="#1e3a8a">VIA INTRINSECA (Heparinas)</text>

  <!-- XII -->
  <rect x="50" y="215" width="50" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6"/>
  <text x="75" y="237" font-size="11" font-weight="700" fill="#1e3a8a" text-anchor="middle">XII</text>

  <!-- XI -->
  <rect x="130" y="215" width="50" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6"/>
  <text x="155" y="237" font-size="11" font-weight="700" fill="#1e3a8a" text-anchor="middle">XI</text>

  <!-- IX -->
  <rect x="210" y="215" width="50" height="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="2" rx="6"/>
  <text x="235" y="237" font-size="11" font-weight="700" fill="#1e3a8a" text-anchor="middle">IX</text>

  <!-- X -->
  <rect x="290" y="285" width="50" height="35" fill="#fbcfe8" stroke="#be185c" stroke-width="2" rx="6"/>
  <text x="315" y="307" font-size="11" font-weight="700" fill="#831843" text-anchor="middle">X</text>

  <!-- II -->
  <rect x="370" y="285" width="50" height="35" fill="#fbcfe8" stroke="#be185c" stroke-width="2" rx="6"/>
  <text x="395" y="307" font-size="11" font-weight="700" fill="#831843" text-anchor="middle">II</text>

  <!-- Trombina -->
  <rect x="450" y="285" width="80" height="35" fill="#7f1d1d" stroke="#450a0a" stroke-width="2" rx="6"/>
  <text x="490" y="307" font-size="11" font-weight="700" fill="white" text-anchor="middle">TROMBINA</text>

  <!-- Fibrina -->
  <rect x="560" y="285" width="100" height="35" fill="#7f1d1d" stroke="#450a0a" stroke-width="2" rx="6"/>
  <text x="610" y="307" font-size="11" font-weight="700" fill="white" text-anchor="middle">FIBRINA</text>

  <!-- Via extrinseca -->
  <text x="800" y="200" font-size="11" font-weight="700" fill="#1e3a8a">VIA EXTRINSECA (Warfarina)</text>

  <!-- Fator tecidual + VII -->
  <rect x="850" y="215" width="100" height="35" fill="#fef3c7" stroke="#ca8a04" stroke-width="2" rx="6"/>
  <text x="900" y="237" font-size="11" font-weight="700" fill="#713f12" text-anchor="middle">Fator Tecidual + VII</text>

  <!-- Setas -->
  <line x1="100" y1="232" x2="130" y2="232" stroke="#3b82f6" stroke-width="2"/>
  <line x1="180" y1="232" x2="210" y2="232" stroke="#3b82f6" stroke-width="2"/>
  <path d="M 235 250 Q 235 270 290 290" fill="none" stroke="#3b82f6" stroke-width="2"/>
  <line x1="340" y1="302" x2="370" y2="302" stroke="#be185c" stroke-width="2"/>
  <line x1="420" y1="302" x2="450" y2="302" stroke="#be185c" stroke-width="2"/>
  <line x1="530" y1="302" x2="560" y2="302" stroke="#be185c" stroke-width="2"/>
  <path d="M 900 250 Q 700 240 320 280" fill="none" stroke="#ca8a04" stroke-width="2"/>

  <!-- Locais de acao -->
  <!-- Heparina -->
  <rect x="280" y="350" width="180" height="20" fill="#10b981" rx="3"/>
  <text x="370" y="365" font-size="9" font-weight="700" fill="white" text-anchor="middle">HEPARINA (anti-Xa + IIa)</text>

  <!-- DOACs -->
  <rect x="480" y="350" width="240" height="20" fill="#0ea5e9" rx="3"/>
  <text x="600" y="365" font-size="9" font-weight="700" fill="white" text-anchor="middle">DOACs (Rivaroxabana=anti-Xa, Dabigatrana=anti-IIa)</text>

  <!-- Warfarina -->
  <rect x="60" y="350" width="200" height="20" fill="#dc2626" rx="3"/>
  <text x="160" y="365" font-size="9" font-weight="700" fill="white" text-anchor="middle">WARFARINA (II, VII, IX, X)</text>

  <!-- Tabela -->
  <text x="40" y="430" font-size="20" font-weight="700" fill="#1e3a8a">📋 Anticoagulantes por Classe</text>

  <rect x="40" y="450" width="1120" height="380" fill="white" rx="12"/>

  <rect x="40" y="450" width="1120" height="36" fill="#3b82f6" rx="12 12 0 0"/>
  <text x="120" y="473" font-size="12" font-weight="700" fill="white">Droga</text>
  <text x="280" y="473" font-size="12" font-weight="700" fill="white">Mecanismo</text>
  <text x="620" y="473" font-size="12" font-weight="700" fill="white">Indicacao</text>
  <text x="880" y="473" font-size="12" font-weight="700" fill="white">Monitor.</text>
  <text x="1060" y="473" font-size="12" font-weight="700" fill="white">Antidoto</text>

  <!-- Warfarina -->
  <text x="60" y="510" font-size="11" font-weight="700">Warfarina</text>
  <text x="280" y="510" font-size="10" fill="#475569">Antagonista vit K (fatores II, VII, IX, X)</text>
  <text x="620" y="510" font-size="10" fill="#475569">FA, TEV cronico, valv. mecanica</text>
  <text x="880" y="510" font-size="10" fill="#475569">INR 2-3 (mec 2.5-3.5)</text>
  <text x="1060" y="510" font-size="10" fill="#475569">Vit K + CCP</text>

  <line x1="40" y1="525" x2="1160" y2="525" stroke="#e2e8f0"/>
  <!-- Rivaroxabana -->
  <text x="60" y="550" font-size="11" font-weight="700">Rivaroxabana</text>
  <text x="280" y="550" font-size="10" fill="#475569">Anti-Xa direto oral</text>
  <text x="620" y="550" font-size="10" fill="#475569">FA, TEV, SCA</text>
  <text x="880" y="550" font-size="10" fill="#10b981" font-weight="700">NAO precisa INR</text>
  <text x="1060" y="550" font-size="10" fill="#475569">Andexanet alfa</text>

  <line x1="40" y1="565" x2="1160" y2="565" stroke="#e2e8f0"/>
  <!-- Apixabana -->
  <text x="60" y="590" font-size="11" font-weight="700">Apixabana</text>
  <text x="280" y="590" font-size="10" fill="#475569">Anti-Xa direto oral</text>
  <text x="620" y="590" font-size="10" fill="#475569">FA, TEV</text>
  <text x="880" y="590" font-size="10" fill="#10b981" font-weight="700">NAO precisa</text>
  <text x="1060" y="590" font-size="10" fill="#475569">Andexanet alfa</text>

  <line x1="40" y1="605" x2="1160" y2="605" stroke="#e2e8f0"/>
  <!-- Dabigatrana -->
  <text x="60" y="630" font-size="11" font-weight="700">Dabigatrana</text>
  <text x="280" y="630" font-size="10" fill="#475569">Anti-IIa (trombina) direto oral</text>
  <text x="620" y="630" font-size="10" fill="#475569">FA, TEV</text>
  <text x="880" y="630" font-size="10" fill="#10b981" font-weight="700">NAO precisa</text>
  <text x="1060" y="630" font-size="10" fill="#10b981" font-weight="700">Idarucizumabe</text>

  <line x1="40" y1="645" x2="1160" y2="645" stroke="#e2e8f0"/>
  <!-- HNF -->
  <text x="60" y="670" font-size="11" font-weight="700">HNF</text>
  <text x="280" y="670" font-size="10" fill="#475569">Anti-IIa + anti-Xa, IV</text>
  <text x="620" y="670" font-size="10" fill="#475569">TEV agudo, SCA, dialise</text>
  <text x="880" y="670" font-size="10" fill="#475569">TTPa 1.5-2.5x</text>
  <text x="1060" y="670" font-size="10" fill="#475569">Protamina 100%</text>

  <line x1="40" y1="685" x2="1160" y2="685" stroke="#e2e8f0"/>
  <!-- HBPM -->
  <text x="60" y="710" font-size="11" font-weight="700">HBPM (Enoxaparina)</text>
  <text x="280" y="710" font-size="10" fill="#475569">Mais anti-Xa, SC 1-2x/dia</text>
  <text x="620" y="710" font-size="10" fill="#475569">TEV, SCA, profilaxia</text>
  <text x="880" y="710" font-size="10" fill="#10b981" font-weight="700">NAO precisa</text>
  <text x="1060" y="710" font-size="10" fill="#475569">Protamina 60-80%</text>

  <line x1="40" y1="725" x2="1160" y2="725" stroke="#e2e8f0"/>
  <!-- Fondaparinux -->
  <text x="60" y="750" font-size="11" font-weight="700">Fondaparinux</text>
  <text x="280" y="750" font-size="10" fill="#475569">Anti-Xa puro sintetico</text>
  <text x="620" y="750" font-size="10" fill="#475569">TEV, alergia heparina</text>
  <text x="880" y="750" font-size="10" fill="#10b981" font-weight="700">NAO precisa</text>
  <text x="1060" y="750" font-size="10" fill="#dc2626">NAO TEM!</text>

  <line x1="40" y1="765" x2="1160" y2="765" stroke="#e2e8f0"/>
  <!-- Observacao -->
  <rect x="60" y="780" width="1080" height="40" fill="#fef3c7" rx="6"/>
  <text x="80" y="805" font-size="12" font-weight="700" fill="#dc2626">⚠️ DOACs CONTRAINDICADOS em valvula mecanica ou estenose mitral reumatica (estudo RE-ALIGN)!</text>

  <!-- Mnemonicos -->
  <text x="40" y="870" font-size="20" font-weight="700" fill="#1e3a8a">🧠 5 Regras Mnemonicas</text>

  <rect x="40" y="890" width="540" height="100" fill="white" rx="12" stroke="#3b82f6" stroke-width="2"/>
  <rect x="50" y="905" width="80" height="22" fill="#3b82f6" rx="4"/>
  <text x="90" y="920" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 1</text>
  <text x="140" y="920" font-size="14" font-weight="700">DOAC = Direto OAnticoagulante COagulante</text>
  <text x="60" y="950" font-size="11" fill="#475569">Sufixo: "-xabana" (anti-Xa), "-gatrana" (anti-IIa)</text>
  <text x="60" y="970" font-size="11" fill="#475569">NAO precisa INR, inicio rapido, menos interacoes</text>

  <rect x="620" y="890" width="540" height="100" fill="white" rx="12" stroke="#dc2626" stroke-width="2"/>
  <rect x="630" y="905" width="80" height="22" fill="#dc2626" rx="4"/>
  <text x="670" y="920" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 2</text>
  <text x="720" y="920" font-size="14" font-weight="700">Warfarina = 4 fatores (II-VII-IX-X)</text>
  <text x="640" y="950" font-size="11" fill="#475569">Bloqueia fatores vitamina K-dependentes</text>
  <text x="640" y="970" font-size="11" fill="#dc2626">⚠️ TERATOGENICA - evitar gestante!</text>

  <rect x="40" y="1010" width="540" height="100" fill="white" rx="12" stroke="#10b981" stroke-width="2"/>
  <rect x="50" y="1025" width="80" height="22" fill="#10b981" rx="4"/>
  <text x="90" y="1040" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 3</text>
  <text x="140" y="1040" font-size="14" font-weight="700">HNF (hospitalar IV) vs HBPM (SC ambulatorio)</text>
  <text x="60" y="1070" font-size="11" fill="#475569">HNF: monitora TTPa. HBPM: NAO monitora.</text>
  <text x="60" y="1090" font-size="11" fill="#475569">Enoxaparina 1mg/kg 2x/dia (em IR: 1x/dia)</text>

  <rect x="620" y="1010" width="540" height="100" fill="white" rx="12" stroke="#7c3aed" stroke-width="2"/>
  <rect x="630" y="1025" width="80" height="22" fill="#7c3aed" rx="4"/>
  <text x="670" y="1040" font-size="11" font-weight="700" fill="white" text-anchor="middle">REGRA 4</text>
  <text x="720" y="1040" font-size="14" font-weight="700">Antidotos especificos</text>
  <text x="640" y="1070" font-size="11" fill="#475569">Warfarina = Vit K + CCP</text>
  <text x="640" y="1090" font-size="11" fill="#10b981" font-weight="700">Dabigatrana = Idarucizumabe (especifico!)</text>

  <!-- Desafio -->
  <rect x="40" y="1130" width="1120" height="190" fill="white" rx="12" stroke="#3b82f6" stroke-width="2"/>
  <text x="60" y="1160" font-size="16" font-weight="700" fill="#3b82f6">💡 Desafio: Sangramento + Anticoagulante</text>

  <rect x="60" y="1175" width="1080" height="35" fill="#f0fdfa" rx="6"/>
  <text x="80" y="1198" font-size="12" fill="#1e293b"><tspan font-weight="700">Caso:</tspan> Idosa 78a, FA, Dabigatrana 150mg 2x/dia. Hematoma subdural no TC. Qual manejo?</text>

  <rect x="60" y="1225" width="1080" height="90" fill="#fef3c7" rx="6"/>
  <text x="80" y="1248" font-size="13" font-weight="700" fill="#10b981">✅ IDARUCIZUMABE 5g IV (2 frascos de 2,5g)</text>
  <text x="100" y="1270" font-size="11" fill="#1e293b">- Antidoto ESPECIFICO da dabigatrana (350x mais forte)</text>
  <text x="100" y="1288" font-size="11" fill="#1e293b">- Efeito em minutos, reversao completa em 4h media</text>
  <text x="100" y="1306" font-size="11" fill="#1e293b">- Hemodialise: dabigatrana E dialisavel (baixa ligacao proteica)</text>

  <!-- Footer -->
  <text x="600" y="1370" font-size="12" fill="#94a3b8" text-anchor="middle">Modulo Anticoagulantes | Auxilio Farmacia</text>
</svg>"""


def main():
    OUTPUT.mkdir(exist_ok=True, parents=True)

    previews = [
        (ANTIARR_SVG, "antiarritmicos.png"),
        (ANTICOAG_SVG, "anticoagulantes.png"),
    ]

    print("=" * 60)
    print("📸 Gerando previews SVG...")
    print("=" * 60)

    for svg, fname in previews:
        # Substitui fontes
        svg = svg.replace('Inter, sans-serif', 'DejaVu-Sans')
        svg = svg.replace("'Inter, sans-serif'", 'DejaVu-Sans')
        svg = svg.replace('Playfair Display, serif', 'DejaVu-Serif')

        # Remove duplicatas de font-weight
        import re as _re
        svg = _re.sub(r'font-weight="700"\s*font-weight="700"', 'font-weight="700"', svg)

        svg_path = OUTPUT / fname.replace(".png", ".svg")
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg)

        png_path = OUTPUT / fname
        try:
            import cairosvg
            cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                             output_width=1200, background_color='white')
            print(f"✅ {fname}")
        except Exception as e:
            print(f"❌ {fname}: {e}")

    print()
    print("=" * 60)
    print("✅ Previews gerados!")
    print("=" * 60)


if __name__ == "__main__":
    main()