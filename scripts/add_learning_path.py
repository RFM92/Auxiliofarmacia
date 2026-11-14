#!/usr/bin/env python3
"""
Adiciona trilha de aprendizado com estrategias de memorizacao
em cada curso (Anti-hipertensivos e Antidiabeticos):
- Nivel Basico
- Nivel Intermediario
- Nivel Avancado
- Estrategias de memorizacao (mnemonicos, mapas mentais, casos)
"""
import re
from pathlib import Path

# CSS para a trilha de aprendizado
LEARNING_PATH_CSS = """
<style>
/* ========== TRILHA DE APRENDIZADO ========== */
.learning-path-section {
  background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 100%);
  border: 1px solid #a7f3d0;
  border-radius: 16px;
  padding: 24px;
  margin: 24px 16px;
}
.learning-path-title {
  font-family: 'Playfair Display', serif;
  font-size: 22px;
  color: #0f766e;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.learning-path-subtitle {
  color: #64748b;
  font-size: 14px;
  margin: 0 0 20px 0;
}

.learning-level {
  background: white;
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 14px;
  border-left: 4px solid;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: relative;
}
.learning-level.basic { border-color: #10b981; }
.learning-level.intermediate { border-color: #f59e0b; }
.learning-level.advanced { border-color: #dc2626; }

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.level-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}
.level-badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 3px 10px;
  border-radius: 12px;
  text-transform: uppercase;
}
.level-badge.basic {
  background: #d1fae5;
  color: #065f46;
}
.level-badge.intermediate {
  background: #fef3c7;
  color: #92400e;
}
.level-badge.advanced {
  background: #fee2e2;
  color: #991b1b;
}

.level-objectives {
  font-size: 13px;
  color: #475569;
  margin-bottom: 12px;
  padding-left: 16px;
}
.level-objectives li {
  margin-bottom: 4px;
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 10px;
}
.strategy-card {
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.strategy-icon {
  font-size: 20px;
  margin-bottom: 6px;
}
.strategy-name {
  font-weight: 700;
  font-size: 12px;
  color: #0f172a;
  margin: 0 0 4px 0;
}
.strategy-desc {
  font-size: 11px;
  color: #64748b;
  line-height: 1.4;
  margin: 0;
}

.mnemonic-box {
  background: linear-gradient(135deg, #fef9c3 0%, #fef08a 100%);
  border: 2px dashed #ca8a04;
  border-radius: 8px;
  padding: 12px;
  margin-top: 10px;
}
.mnemonic-title {
  font-size: 11px;
  font-weight: 700;
  color: #713f12;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.mnemonic-content {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #422006;
  font-weight: 700;
  letter-spacing: 1px;
}

.flashcard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
  margin-top: 10px;
}
.flashcard {
  background: white;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 8px;
  font-size: 11px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.flashcard:hover {
  background: #f0fdfa;
  border-color: #14b8a6;
  transform: translateY(-2px);
}
.flashcard-q {
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 2px;
}
.flashcard-a {
  color: #64748b;
  font-size: 10px;
}

.timeline {
  position: relative;
  padding-left: 24px;
  margin: 16px 0;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 8px; top: 0; bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #10b981 0%, #f59e0b 50%, #dc2626 100%);
}
.timeline-item {
  position: relative;
  padding-bottom: 12px;
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: -20px; top: 4px;
  width: 12px; height: 12px;
  background: white;
  border: 3px solid #10b981;
  border-radius: 50%;
}
.timeline-item.basic::before { border-color: #10b981; }
.timeline-item.intermediate::before { border-color: #f59e0b; }
.timeline-item.advanced::before { border-color: #dc2626; }

.timeline-week {
  font-weight: 700;
  font-size: 11px;
  color: #0d9488;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.timeline-title {
  font-size: 13px;
  color: #1f2937;
  font-weight: 600;
  margin: 2px 0;
}
.timeline-desc {
  font-size: 11px;
  color: #64748b;
  margin: 0;
}

@media (max-width: 768px) {
  .strategy-grid {
    grid-template-columns: 1fr;
  }
}
</style>
"""

# Trilha de Antihipertensivos
ANTIHIPERTENSIVOS_PATH = """
<!-- TRILHA DE APRENDIZADO - ANTIHIPERTENSIVOS -->
<div class="learning-path-section" id="path-antihipertensivos" style="display:none;">
  <h3 class="learning-path-title">
    🧠 Trilha de Aprendizado: Anti-hipertensivos
  </h3>
  <p class="learning-path-subtitle">
    Estrategia progressiva do basico ao avancado, com tecnicas de memorizacao cientificamente comprovadas.
  </p>

  <!-- Timeline Semanal -->
  <div class="timeline">

    <div class="timeline-item basic">
      <div class="timeline-week">SEMANA 1-2 · BASICO</div>
      <div class="timeline-title">Fundamentos e Sistema Renina-Angiotensina-Aldosterona</div>
      <p class="timeline-desc">Compreender a fisiologia e os 5 grandes grupos farmacologicos.</p>
    </div>

    <div class="timeline-item basic">
      <div class="timeline-week">SEMANA 3-4 · BASICO</div>
      <div class="timeline-title">Monoterapia e escolha inicial</div>
      <p class="timeline-desc">Quando iniciar, qual droga escolher, metas por perfil de paciente.</p>
    </div>

    <div class="timeline-item intermediate">
      <div class="timeline-week">SEMANA 5-6 · INTERMEDIARIO</div>
      <div class="timeline-title">Combinacoes fixas e posologia</div>
      <p class="timeline-desc">Associacoes sinergeticas, ajuste de dose, adesao ao tratamento.</p>
    </div>

    <div class="timeline-item intermediate">
      <div class="timeline-week">SEMANA 7-8 · INTERMEDIARIO</div>
      <div class="timeline-title">Comorbidades e individualizacao</div>
      <p class="timeline-desc">HAS + Diabetes, HAS + DRC, HAS + Idoso, HAS + Gestante.</p>
    </div>

    <div class="timeline-item advanced">
      <div class="timeline-week">SEMANA 9-10 · AVANCADO</div>
      <div class="timeline-title">Hipertensao refrataria e secundaria</div>
      <p class="timeline-desc">Investigar causas, hiperaldosteronismo, feocromocitoma.</p>
    </div>

    <div class="timeline-item advanced">
      <div class="timeline-week">SEMANA 11-12 · AVANCADO</div>
      <div class="timeline-title">Emergencias e urgencias hipertensivas</div>
      <p class="timeline-desc">Crise hipertensiva, AVC, IAM, dissecção aortica, eclampsia.</p>
    </div>
  </div>

  <!-- Nivel Basico -->
  <div class="learning-level basic">
    <div class="level-header">
      <h4 class="level-title">🟢 Nivel Basico - Fundamentos</h4>
      <span class="level-badge basic">INICIANTE</span>
    </div>
    <p class="level-objectives">
      <strong>Objetivos:</strong>
    </p>
    <ul class="level-objectives">
      <li>Compreender a fisiopatologia da HAS</li>
      <li>Conhecer os 5 grupos principais (IECA, BRA, BCC, DIU, BB)</li>
      <li>Identificar quando iniciar tratamento farmacologico</li>
      <li>Memorizar doses iniciais e titulacao</li>
    </ul>

    <div class="mnemonic-box">
      <div class="mnemonic-title">💡 Mnemonico - Os 5 grupos:</div>
      <div class="mnemonic-content">"IECA BRAo CALCIO BETA DIUretico"</div>
    </div>

    <div class="mnemonic-box" style="margin-top:8px;">
      <div class="mnemonic-title">💡 Mnemonico - SRAA:</div>
      <div class="mnemonic-content">Renina → Angiotensinogenio → Angiotensina I → ECA → Angiotensina II → AT1</div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#065f46;">📌 Estrategias de Memorizacao:</h5>
    <div class="strategy-grid">
      <div class="strategy-card">
        <div class="strategy-icon">🧠</div>
        <div class="strategy-name">Mapa Mental</div>
        <p class="strategy-desc">Desenhe o SRAA com cores: vermelho=ativacao, azul=inibicao.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">🔄</div>
        <div class="strategy-name">Repeticao Espacada</div>
        <p class="strategy-desc">Revise as aulas em 1, 3, 7 e 14 dias. Use Anki para flashcards.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">📖</div>
        <div class="strategy-name">Historia Clinica</div>
        <p class="strategy-desc">Crie 1 paciente ficticio para cada classe. Ex: "Joao, 55a, HAS estadio 1".</p>
      </div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#065f46;">🃏 Flashcards Rapidos:</h5>
    <div class="flashcard-grid">
      <div class="flashcard"><div class="flashcard-q">Captopril</div><div class="flashcard-a">IECA • 25-50mg 2-3x/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Losartana</div><div class="flashcard-a">BRA • 50-100mg 1x/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Anlodipino</div><div class="flashcard-a">BCC • 5-10mg 1x/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Hidroclorotiazida</div><div class="flashcard-a">DIU tiazidico • 25mg 1x/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Propranolol</div><div class="flashcard-a">BB nao seletivo</div></div>
      <div class="flashcard"><div class="flashcard-q">Atenolol</div><div class="flashcard-a">BB cardiosseletivo</div></div>
    </div>
  </div>

  <!-- Nivel Intermediario -->
  <div class="learning-level intermediate">
    <div class="level-header">
      <h4 class="level-title">🟡 Nivel Intermediario - Pratica Clinica</h4>
      <span class="level-badge intermediate">PRATICO</span>
    </div>
    <p class="level-objectives">
      <strong>Objetivos:</strong>
    </p>
    <ul class="level-objectives">
      <li>Dominar combinacoes fixas e doses</li>
      <li>Individualizar por comorbidades</li>
      <li>Ajustar em DRC, diabetes, gestacao</li>
      <li>Manejar efeitos adversos especificos</li>
    </ul>

    <div class="mnemonic-box">
      <div class="mnemonic-title">💡 Combinacoes preferenciais (eficazes):</div>
      <div class="mnemonic-content">IECA/BRA + BCC  |  IECA/BRA + DIU  |  BCC + DIU</div>
    </div>

    <div class="mnemonic-box" style="margin-top:8px;">
      <div class="mnemonic-title">💡 Evitar em combinacao:</div>
      <div class="mnemonic-content">IECA + BRA  |  BB + BCC nao dihidropiridinico  |  DIU poupador + IECA</div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#92400e;">📌 Estrategias de Memorizacao:</h5>
    <div class="strategy-grid">
      <div class="strategy-card">
        <div class="strategy-icon">🎯</div>
        <div class="strategy-name">Casos Clinicos</div>
        <p class="strategy-desc">Resolva 5 casos por semana. Apos 1 mes, voce sabe prescrever.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">🗂️</div>
        <div class="strategy-name">Algoritmo Decisorio</div>
        <p class="strategy-desc">Crie fluxograma: Comorbidade → droga preferida → combinacao.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">💬</div>
        <div class="strategy-name">Ensine Alguem</div>
        <p class="strategy-desc">Explique para um colega em 5 min. Se travar, reveja.</p>
      </div>
    </div>
  </div>

  <!-- Nivel Avancado -->
  <div class="learning-level advanced">
    <div class="level-header">
      <h4 class="level-title">🔴 Nivel Avancado - Especialista</h4>
      <span class="level-badge advanced">EXPERT</span>
    </div>
    <p class="level-objectives">
      <strong>Objetivos:</strong>
    </p>
    <ul class="level-objectives">
      <li>Diagnosticar HAS secundaria</li>
      <li>Manejar HAS refrataria (3+ drogas em dose maxima)</li>
      <li>Conduzir emergencias hipertensivas</li>
      <li>Dominar interacoes complexas</li>
    </ul>

    <div class="mnemonic-box">
      <div class="mnemonic-title">💡 Mnemonico HAS secundaria - CHAPS:</div>
      <div class="mnemonic-content">C Cushing / H Hiperaldosteronismo / A Apneia / P Feocromocitoma / S Renal (estenose)</div>
    </div>

    <div class="mnemonic-box" style="margin-top:8px;">
      <div class="mnemonic-title">💡 Drogas para Emergencia:</div>
      <div class="mnemonic-content">Nitroprussiato • Nitroglicerina • Labetalol • Hidralazina • Fentolamina</div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#991b1b;">📌 Estrategias de Memorizacao:</h5>
    <div class="strategy-grid">
      <div class="strategy-card">
        <div class="strategy-icon">🧩</div>
        <div class="strategy-name">Aprendizado Baseado em Problemas</div>
        <p class="strategy-desc">Estude casos complexos reais. Pesquise em PubMed e diretrizes.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">🎓</div>
        <div class="strategy-name">Discussao em Grupo</div>
        <p class="strategy-desc">Participe de forums medicos (Medscape, SBN). Discuta casos.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">📊</div>
        <div class="strategy-name">Auto-avaliacao Continua</div>
        <p class="strategy-desc">A cada 30 dias, faca prova com casos reais. Meve evolucao.</p>
      </div>
    </div>
  </div>
</div>
"""

# Trilha de Antidiabeticos
ANTIDIABETICOS_PATH = """
<!-- TRILHA DE APRENDIZADO - ANTIDIABETICOS -->
<div class="learning-path-section" id="path-antidiabeticos" style="display:none;">
  <h3 class="learning-path-title">
    🧠 Trilha de Aprendizado: Antidiabeticos
  </h3>
  <p class="learning-path-subtitle">
    Do mecanismo molecular a pratica clinica, com casos e mnemonicos para consulta rapida.
  </p>

  <!-- Timeline Semanal -->
  <div class="timeline">

    <div class="timeline-item basic">
      <div class="timeline-week">SEMANA 1-2 · BASICO</div>
      <div class="timeline-title">Fisiologia da insulina e DM2</div>
      <p class="timeline-desc">Insulina, glucagon, resistencia periferica, falencia de celulas beta.</p>
    </div>

    <div class="timeline-item basic">
      <div class="timeline-week">SEMANA 3-4 · BASICO</div>
      <div class="timeline-title">Metformina e primeiros passos</div>
      <p class="timeline-desc">Primeira linha, dose, contraindicacoes, ajuste renal.</p>
    </div>

    <div class="timeline-item intermediate">
      <div class="timeline-week">SEMANA 5-6 · INTERMEDIARIO</div>
      <div class="timeline-title">Segundas linhas (DPP4, GLP1, SGLT2)</div>
      <p class="timeline-desc">Quando adicionar, beneficios cardio-renais, efeitos adversos.</p>
    </div>

    <div class="timeline-item intermediate">
      <div class="timeline-week">SEMANA 7-8 · INTERMEDIARIO</div>
      <div class="timeline-title">Complicacoes e individualizacao</div>
      <p class="timeline-desc">DM + DRC, DM + ICC, DM + Obesidade, DM + Idoso fragil.</p>
    </div>

    <div class="timeline-item advanced">
      <div class="timeline-week">SEMANA 9-10 · AVANCADO</div>
      <div class="timeline-title">Insulinoterapia basal-bolus</div>
      <p class="timeline-desc">Tipos de insulina, esquemas, ajuste por glicemia, contagem de carboidratos.</p>
    </div>

    <div class="timeline-item advanced">
      <div class="timeline-week">SEMANA 11-12 · AVANCADO</div>
      <div class="timeline-title">Cetoacidose e Estado Hiperglicemico</div>
      <p class="timeline-desc">CAD, EHH, protocolo de hidratacao, insulinoterapia IV.</p>
    </div>
  </div>

  <!-- Nivel Basico -->
  <div class="learning-level basic">
    <div class="level-header">
      <h4 class="level-title">🟢 Nivel Basico - Fundamentos</h4>
      <span class="level-badge basic">INICIANTE</span>
    </div>
    <p class="level-objectives">
      <strong>Objetivos:</strong>
    </p>
    <ul class="level-objectives">
      <li>Compreender a fisiologia da glicemia</li>
      <li>Conhecer Metformina (primeira linha)</li>
      <li>Saber diagnosticar DM2 (HbA1c, glicemia jejum, TOTG)</li>
      <li>Entender metas glicemicas por perfil</li>
    </ul>

    <div class="mnemonic-box">
      <div class="mnemonic-title">💡 Diagnostico DM2 - 4 testes:</div>
      <div class="mnemonic-content">HbA1c ≥6,5%  |  Glicemia jejum ≥126  |  TOTG 2h ≥200  |  Casual ≥200 + sintomas</div>
    </div>

    <div class="mnemonic-box" style="margin-top:8px;">
      <div class="mnemonic-title">💡 Mnemonico Metformina:</div>
      <div class="mnemonic-content">"METforma da METade" → comece com 500mg 1x/dia apos almoco</div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#065f46;">📌 Estrategias de Memorizacao:</h5>
    <div class="strategy-grid">
      <div class="strategy-card">
        <div class="strategy-icon">🧠</div>
        <div class="strategy-name">Visualizacao Mental</div>
        <p class="strategy-desc">Imagine celulas beta produzindo insulina (fabrica) e musculos absorvendo glicose (consumo).</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">🔄</div>
        <div class="strategy-name">Repeticao Espacada</div>
        <p class="strategy-desc">Use Anki com SRS. Revise 20 minutos por dia.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">📝</div>
        <div class="strategy-name">Resumo em 1 Pagina</div>
        <p class="strategy-desc">Crie uma "cola" pessoal com doses, contraindicacoes e ajustes.</p>
      </div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#065f46;">🃏 Flashcards Rapidos:</h5>
    <div class="flashcard-grid">
      <div class="flashcard"><div class="flashcard-q">Metformina</div><div class="flashcard-a">Biguanida • 500-2550mg/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Glibenclamida</div><div class="flashcard-a">Sulfonilureia • 2,5-20mg/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Sitagliptina</div><div class="flashcard-a">DPP-4 • 100mg 1x/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Liraglutida</div><div class="flashcard-a">GLP-1 • SC 1,8mg/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Empagliflozina</div><div class="flashcard-a">SGLT2 • 10-25mg/dia</div></div>
      <div class="flashcard"><div class="flashcard-q">Insulina NPH</div><div class="flashcard-a">Basal • 12-18h acao</div></div>
    </div>
  </div>

  <!-- Nivel Intermediario -->
  <div class="learning-level intermediate">
    <div class="level-header">
      <h4 class="level-title">🟡 Nivel Intermediario - Pratica Clinica</h4>
      <span class="level-badge intermediate">PRATICO</span>
    </div>
    <p class="level-objectives">
      <strong>Objetivos:</strong>
    </p>
    <ul class="level-objectives">
      <li>Escolher segunda linha baseado em comorbidades</li>
      <li>Conhecer beneficios cardio-renais (GLP-1, SGLT2)</li>
      <li>Manejar efeitos adversos especificos</li>
      <li>Iniciar insulinoterapia basal</li>
    </ul>

    <div class="mnemonic-box">
      <div class="mnemonic-title">💡 Beneficios CV - "Coracao Protegido":</div>
      <div class="mnemonic-content">GLP-1 (LEADER, REWIND)  |  SGLT2 (EMPA-REG, DAPA-HF)</div>
    </div>

    <div class="mnemonic-box" style="margin-top:8px;">
      <div class="mnemonic-title">💡 Mnemonico efeitos adversos - "GLP1 SGLT2 DPP4":</div>
      <div class="mnemonic-content">GLP1: nausea  |  SGLT2: genital  |  DPP4: pancreatite</div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#92400e;">📌 Estrategias de Memorizacao:</h5>
    <div class="strategy-grid">
      <div class="strategy-card">
        <div class="strategy-icon">🎯</div>
        <div class="strategy-name">Algoritmo Visual</div>
        <p class="strategy-desc">Desenhe fluxograma: DM2 → metformina → qual comorbidade define a proxima droga.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">📖</div>
        <div class="strategy-name">Casos Clinicos Reais</div>
        <p class="strategy-desc">Veja 10 prontuarios de DM2 do seu servico. Identifique as escolhas.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">🎤</div>
        <div class="strategy-name">Apresentar para Equipe</div>
        <p class="strategy-desc">Apresente 15 min sobre uma classe. Aprendizado ativo.</p>
      </div>
    </div>
  </div>

  <!-- Nivel Avancado -->
  <div class="learning-level advanced">
    <div class="level-header">
      <h4 class="level-title">🔴 Nivel Avancado - Especialista</h4>
      <span class="level-badge advanced">EXPERT</span>
    </div>
    <p class="level-objectives">
      <strong>Objetivos:</strong>
    </p>
    <ul class="level-objectives">
      <li>Dominar insulinoterapia intensiva</li>
      <li>Manejar CAD e EHH</li>
      <li>Ajustar insulina em cirurgia e internacao</li>
      <li>Indicar bomba de insulina</li>
    </ul>

    <div class="mnemonic-box">
      <div class="mnemonic-title">💡 Protocolo CAD - 5 passos:</div>
      <div class="mnemonic-content">1. SF 0,9% 15mL/kg/h  2. K+ se &lt;5,3  3. Insulina regular 0,1U/kg/h  4. Glicemia capilar/h  5. Bicarbonato se pH&lt;6,9</div>
    </div>

    <div class="mnemonic-box" style="margin-top:8px;">
      <div class="mnemonic-title">💡 Mnemonico Insulinas - RAPID FEIA DEMORA:</div>
      <div class="mnemonic-content">RApida (Regular, Lispro)  |  Intermediaria (NPH)  |  LEnta (Detemir)  |  Muito LEnta (Glargina)</div>
    </div>

    <h5 style="margin:16px 0 8px 0;font-size:13px;color:#991b1b;">📌 Estrategias de Memorizacao:</h5>
    <div class="strategy-grid">
      <div class="strategy-card">
        <div class="strategy-icon">🏥</div>
        <div class="strategy-name">Estagio Pratico</div>
        <p class="strategy-desc">Acompanhe endocrinologista por 1 semana. Veja manejo na pratica.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">📚</div>
        <div class="strategy-name">Diretrizes Nacionais</div>
        <p class="strategy-desc">Leia SBD 2024 + ADA Standards of Care. Salve highlights.</p>
      </div>
      <div class="strategy-card">
        <div class="strategy-icon">🎓</div>
        <div class="strategy-name">Journal Club</div>
        <p class="strategy-desc">Participe de discussao de artigos. Critique com o metodo PICO.</p>
      </div>
    </div>
  </div>
</div>
"""

# JavaScript para alternar entre cursos e mostrar trilha
LEARNING_PATH_JS = """
<script>
// ========== TRILHA DE APRENDIZADO ==========

function showLearningPath(cursoId) {
  // Esconde todas as trilhas
  document.querySelectorAll('.learning-path-section').forEach(el => {
    el.style.display = 'none';
  });
  
  // Mostra a trilha do curso selecionado
  const target = document.getElementById('path-' + cursoId);
  if (target) {
    target.style.display = 'block';
    // Scroll suave
    setTimeout(() => {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }
}

// Hook no openCourse para mostrar trilha
const origOpenCourse = window.openCourse;
if (typeof origOpenCourse === 'function') {
  window.openCourse = function(cursoId) {
    origOpenCourse.apply(this, arguments);
    // Mostra trilha depois de abrir
    setTimeout(() => showLearningPath(cursoId), 300);
  };
}

// Flashcards interativas
document.addEventListener('click', e => {
  const card = e.target.closest('.flashcard');
  if (!card) return;
  const answer = card.querySelector('.flashcard-a');
  if (answer) {
    answer.style.color = answer.style.color === 'rgb(13, 148, 136)' ? '#64748b' : '#0d9488';
    answer.style.fontWeight = answer.style.fontWeight === '700' ? '400' : '700';
  }
});
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
    print("🎓 Adicionando Trilha de Aprendizado + Estrategias")
    print("=" * 60)

    for fname in arquivos:
        path = output / fname
        if not path.exists():
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        modified = False

        # Adiciona CSS
        if 'TRILHA DE APRENDIZADO' not in html:
            html = html.replace('</style>', '</style>\n' + LEARNING_PATH_CSS, 1)
            modified = True

        # Adiciona trilha dos 2 cursos
        if 'path-antihipertensivos' not in html:
            html = html.replace('</body>', ANTIHIPERTENSIVOS_PATH + '\n</body>', 1)
            modified = True

        if 'path-antidiabeticos' not in html:
            html = html.replace('</body>', ANTIDIABETICOS_PATH + '\n</body>', 1)
            modified = True

        # Adiciona JS
        if 'showLearningPath' not in html:
            html = html.replace('</body>', LEARNING_PATH_JS + '\n</body>', 1)
            modified = True

        if modified:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ {fname}")
        else:
            print(f"⏭️  {fname}")

    print()
    print("=" * 60)
    print("✅ TRILHAS ADICIONADAS!")
    print("=" * 60)


if __name__ == "__main__":
    main()