#!/usr/bin/env python3
"""
Adiciona Hub de Cursos Farmaceuticos ao site:
- 8 cursos completos por classe terapeutica
- Player de video/aula
- Quiz com certificado
- Compra avulsa + bundles
- Cross-sell: comprar curso da acesso ao dashboard
"""
import re
from pathlib import Path

# ===== CSS PARA CURSOS =====
COURSES_CSS = """
<style>
/* ========== HUB DE CURSOS ========== */
.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.course-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.2s;
  position: relative;
}
.course-card:hover {
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.course-thumb {
  height: 160px;
  background: linear-gradient(135deg, var(--course-color, #0d9488) 0%, var(--course-color-2, #06b6d4) 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 56px; color: white;
  position: relative;
}
.course-thumb-overlay {
  position: absolute; bottom: 8px; right: 8px;
  background: rgba(0,0,0,0.6); color: white;
  padding: 3px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 700;
}
.course-thumb-badge {
  position: absolute; top: 8px; left: 8px;
  background: rgba(255,255,255,0.95);
  padding: 4px 10px; border-radius: 12px;
  font-size: 10px; font-weight: 700;
  color: var(--course-color, #0d9488);
  text-transform: uppercase; letter-spacing: 0.5px;
}

.course-body { padding: 16px; }
.course-cat {
  font-size: 10px; font-weight: 700;
  color: var(--course-color, #0d9488);
  text-transform: uppercase; letter-spacing: 1px;
  margin-bottom: 6px;
}
.course-title {
  font-size: 16px; font-weight: 700; color: #0f172a;
  margin: 0 0 8px 0; line-height: 1.3;
}
.course-desc {
  font-size: 13px; color: #64748b;
  line-height: 1.5; margin-bottom: 12px;
}
.course-meta {
  display: flex; gap: 12px; flex-wrap: wrap;
  padding: 10px 0; border-top: 1px solid #f1f5f9;
  font-size: 11px; color: #64748b;
  margin-bottom: 12px;
}
.course-meta-item { display: flex; align-items: center; gap: 4px; }

.course-footer {
  display: flex; justify-content: space-between; align-items: center;
}
.course-price {
  font-size: 22px; font-weight: 800;
  color: var(--course-color, #0d9488);
}
.course-price-old {
  font-size: 13px; text-decoration: line-through;
  color: #94a3b8; font-weight: 400; margin-left: 4px;
}
.course-btn {
  padding: 8px 16px; border: none; border-radius: 8px;
  background: var(--course-color, #0d9488);
  color: white; font-weight: 600; font-size: 13px;
  cursor: pointer; font-family: inherit;
}
.course-btn:hover { opacity: 0.9; }
.course-btn-enrolled {
  background: #10b981;
}

/* PLAYER */
.course-player {
  background: #0f172a; border-radius: 12px; overflow: hidden;
  margin-bottom: 16px;
}
.course-video {
  width: 100%; aspect-ratio: 16/9;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 64px;
  position: relative;
}
.course-video-overlay {
  position: absolute; bottom: 16px; left: 16px; right: 16px;
  display: flex; gap: 8px;
}
.course-video-controls {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: rgba(0,0,0,0.7); padding: 12px 16px;
  display: flex; align-items: center; gap: 12px;
  color: white;
}
.progress-bar {
  flex: 1; height: 6px; background: rgba(255,255,255,0.2);
  border-radius: 3px; overflow: hidden; cursor: pointer;
}
.progress-fill {
  height: 100%; background: #14b8a6; width: 35%;
  transition: width 0.3s;
}

.course-player-body { padding: 20px; }
.course-player-title {
  font-size: 18px; font-weight: 700; color: white;
  margin-bottom: 8px;
}
.course-player-meta { color: #94a3b8; font-size: 13px; margin-bottom: 12px; }

.course-tabs {
  display: flex; gap: 4px; border-bottom: 1px solid #334155;
  margin-bottom: 16px;
}
.course-tab {
  padding: 10px 16px; color: #94a3b8; cursor: pointer;
  font-weight: 600; font-size: 13px;
  border-bottom: 2px solid transparent;
}
.course-tab.active { color: #14b8a6; border-bottom-color: #14b8a6; }

/* MODULES LIST */
.modules-list { list-style: none; padding: 0; margin: 0; }
.module-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; border-radius: 8px;
  cursor: pointer; transition: background 0.15s;
  color: white;
}
.module-item:hover { background: rgba(255,255,255,0.05); }
.module-item.active { background: rgba(20,184,166,0.2); }
.module-icon {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.module-icon.done { background: #10b981; }
.module-info { flex: 1; }
.module-title { font-weight: 600; font-size: 14px; }
.module-meta { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.module-status { font-size: 12px; color: #94a3b8; }

/* CERTIFICATE */
.certificate {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 4px double #d97706; border-radius: 16px;
  padding: 40px; text-align: center;
  position: relative;
}
.cert-title {
  font-family: 'Playfair Display', serif;
  font-size: 28px; color: #92400e; margin-bottom: 8px;
}
.cert-text { color: #78350f; font-size: 14px; line-height: 1.6; margin: 16px 0; }
.cert-seal {
  width: 100px; height: 100px;
  background: radial-gradient(circle, #fbbf24 0%, #d97706 100%);
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  color: white; font-size: 36px; margin-top: 16px;
  border: 3px solid #92400e;
}

/* BUNDLE CARDS */
.bundle-card {
  background: linear-gradient(135deg, #0d9488 0%, #06b6d4 100%);
  color: white; padding: 24px; border-radius: 16px;
  margin-bottom: 16px;
}
.bundle-title { font-size: 18px; font-weight: 700; margin-bottom: 8px; }
.bundle-desc { opacity: 0.9; font-size: 13px; margin-bottom: 16px; line-height: 1.5; }
.bundle-includes { margin: 16px 0; }
.bundle-includes li { padding: 4px 0; font-size: 13px; }
.bundle-price { font-size: 32px; font-weight: 800; }
.bundle-price-old { font-size: 16px; text-decoration: line-through; opacity: 0.6; }
.bundle-savings {
  display: inline-block; background: rgba(255,255,255,0.2);
  padding: 4px 10px; border-radius: 12px;
  font-size: 11px; font-weight: 700;
  margin-left: 8px;
}

/* QUIZ */
.quiz-question {
  background: rgba(255,255,255,0.05); padding: 20px;
  border-radius: 12px; margin-bottom: 16px;
}
.quiz-q { font-size: 16px; color: white; font-weight: 600; margin-bottom: 16px; }
.quiz-options { display: flex; flex-direction: column; gap: 8px; }
.quiz-option {
  padding: 12px 16px; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
  color: white; cursor: pointer; text-align: left;
  font-family: inherit; font-size: 14px;
  transition: all 0.15s;
}
.quiz-option:hover { background: rgba(20,184,166,0.2); border-color: #14b8a6; }
.quiz-option.correct { background: rgba(16,185,129,0.2); border-color: #10b981; }
.quiz-option.wrong { background: rgba(239,68,68,0.2); border-color: #ef4444; }

/* FILTERS BAR */
.courses-filter {
  display: flex; gap: 8px; flex-wrap: wrap;
  margin-bottom: 20px; padding: 12px;
  background: #f8fafc; border-radius: 12px;
}
.courses-filter-btn {
  padding: 6px 14px; background: white;
  border: 1px solid #e2e8f0; border-radius: 20px;
  font-size: 13px; font-weight: 500;
  color: #64748b; cursor: pointer;
  font-family: inherit; transition: all 0.15s;
}
.courses-filter-btn.active {
  background: #0d9488; color: white; border-color: #0d9488;
}

/* ENROLLED BADGE */
.enrolled-badge {
  position: absolute; top: 8px; right: 8px;
  background: #10b981; color: white;
  padding: 4px 10px; border-radius: 12px;
  font-size: 10px; font-weight: 700;
  display: flex; align-items: center; gap: 4px;
  z-index: 2;
}

@media (max-width: 768px) {
  .courses-grid { grid-template-columns: 1fr; }
}
</style>
"""

# ===== DADOS DOS CURSOS =====
COURSES_DATA = """
<script>
// ========== CURSOS DATA ==========
const CURSOS = [
  {
    id: 'antibioticos',
    title: 'Antibioticoterapia na Prática Clínica',
    cat: 'Classe Terapêutica',
    desc: 'Curso completo sobre uso racional de antibióticos. Da farmacologia básica aos esquemas avançados para infecções comunitárias e hospitalares.',
    color: '#dc2626',
    color2: '#f59e0b',
    badge: 'MAIS VENDIDO',
    thumb: '🦠',
    duration: '8h 30min',
    modules: 12,
    lessons: 48,
    price: 197.00,
    priceOld: 297.00,
    includes: ['Acesso ao Dashboard Pro', 'Calculadoras clínicas', 'Mapa mental de antibióticos'],
    modules_list: [
      { title: 'Introdução aos Antibióticos', duration: '45min', lessons: 4 },
      { title: 'Mecanismos de Ação', duration: '60min', lessons: 5 },
      { title: 'Betalactâmicos (Penicilinas e Cefalosporinas)', duration: '90min', lessons: 6 },
      { title: 'Macrolídeos e Lincosamidas', duration: '60min', lessons: 4 },
      { title: 'Quinolonas', duration: '50min', lessons: 4 },
      { title: 'Aminoglicosídeos', duration: '40min', lessons: 3 },
      { title: 'Tetraciclinas e Glicilciclinas', duration: '45min', lessons: 3 },
      { title: 'Antibióticos em Pediatria', duration: '60min', lessons: 4 },
      { title: 'Antibióticos em Gestantes', duration: '40min', lessons: 3 },
      { title: 'Resistência Bacteriana', duration: '50min', lessons: 3 },
      { title: 'Casos Clínicos Comentados', duration: '90min', lessons: 6 },
      { title: 'Quiz Final + Certificado', duration: '30min', lessons: 3 },
    ]
  },
  {
    id: 'aines',
    title: 'AINEs: Do Mecanismo à Escolha Clínica',
    cat: 'Classe Terapêutica',
    desc: 'Domine anti-inflamatórios não esteroidais. Farmacologia, indicações, contraindicações e como escolher o melhor AINE para cada cenário.',
    color: '#7c3aed',
    color2: '#a855f7',
    badge: 'ATUALIZADO',
    thumb: '💊',
    duration: '6h 15min',
    modules: 10,
    lessons: 36,
    price: 147.00,
    priceOld: 197.00,
    includes: ['Acesso ao Dashboard Pro', 'Tabela comparativa AINEs'],
    modules_list: [
      { title: 'Farmacologia dos AINEs', duration: '60min', lessons: 4 },
      { title: 'Ciclooxigenase (COX-1 e COX-2)', duration: '45min', lessons: 3 },
      { title: 'Ibuprofeno, Diclofenaco e Naproxeno', duration: '60min', lessons: 4 },
      { title: 'Inibidores Seletivos COX-2', duration: '40min', lessons: 3 },
      { title: 'AINEs Tópicos', duration: '30min', lessons: 2 },
      { title: 'Efeitos Adversos Gastrointestinais', duration: '45min', lessons: 3 },
      { title: 'AINEs em Cardiopatas', duration: '40min', lessons: 3 },
      { title: 'AINEs em Idosos', duration: '40min', lessons: 3 },
      { title: 'Interações Medicamentosas', duration: '35min', lessons: 3 },
      { title: 'Quiz + Certificado', duration: '20min', lessons: 2 },
    ]
  },
  {
    id: 'analgesicos',
    title: 'Analgésicos e Dor: Abordagem Farmacológica',
    cat: 'Classe Terapêutica',
    desc: 'Aprenda a manejar a dor com a farmacologia certa. Da escada analgésica da OMS aos opioides, com casos práticos.',
    color: '#0d9488',
    color2: '#06b6d4',
    badge: 'RECOMENDADO',
    thumb: '⚡',
    duration: '7h',
    modules: 11,
    lessons: 40,
    price: 167.00,
    priceOld: 247.00,
    includes: ['Acesso ao Dashboard Pro', 'Calculadora de dose analgésica'],
    modules_list: [
      { title: 'Fisiologia da Dor', duration: '50min', lessons: 4 },
      { title: 'Escada Analgésica da OMS', duration: '40min', lessons: 3 },
      { title: 'Paracetamol e Dipirona', duration: '50min', lessons: 4 },
      { title: 'Opioides Fracos (Codeína, Tramadol)', duration: '60min', lessons: 4 },
      { title: 'Opioides Fortes (Morfina, Fentanil)', duration: '70min', lessons: 5 },
      { title: 'Adjuvantes Analgésicos', duration: '45min', lessons: 3 },
      { title: 'Dor Neuropática', duration: '50min', lessons: 4 },
      { title: 'Dor em Pediatria', duration: '40min', lessons: 3 },
      { title: 'Rotação de Opioides', duration: '45min', lessons: 3 },
      { title: 'Casos Clínicos', duration: '60min', lessons: 4 },
      { title: 'Quiz + Certificado', duration: '20min', lessons: 3 },
    ]
  },
  {
    id: 'antihipertensivos',
    title: 'Anti-hipertensivos: Farmacologia e Prescrição',
    cat: 'Classe Terapêutica',
    desc: 'Curso definitivo sobre drogas anti-hipertensivas. Da escolha inicial até combinações complexas em hipertensão refratária.',
    color: '#dc2626',
    color2: '#ec4899',
    badge: 'COMPLETO',
    thumb: '❤️',
    duration: '9h',
    modules: 14,
    lessons: 52,
    price: 197.00,
    priceOld: 297.00,
    includes: ['Acesso ao Dashboard Pro', 'Tabela de combinações fixas'],
    modules_list: [
      { title: 'Fisiopatologia da Hipertensão', duration: '60min', lessons: 4 },
      { title: 'IECA e BRA', duration: '70min', lessons: 5 },
      { title: 'Bloqueadores de Cálcio', duration: '60min', lessons: 4 },
      { title: 'Diuréticos', duration: '50min', lessons: 4 },
      { title: 'Betabloqueadores', duration: '60min', lessons: 4 },
      { title: 'Alfabloqueadores', duration: '30min', lessons: 2 },
      { title: 'Vasodilatadores Diretos', duration: '30min', lessons: 2 },
      { title: 'Anti-hipertensivos em Gestantes', duration: '50min', lessons: 3 },
      { title: 'Crise Hipertensiva', duration: '45min', lessons: 3 },
      { title: 'Hipertensão em Idosos', duration: '40min', lessons: 3 },
      { title: 'Associação de Drogas', duration: '60min', lessons: 5 },
      { title: 'Casos Clínicos', duration: '80min', lessons: 6 },
      { title: 'Emergências Hipertensivas', duration: '40min', lessons: 3 },
      { title: 'Quiz + Certificado', duration: '20min', lessons: 3 },
    ]
  },
  {
    id: 'diabeticos',
    title: 'Antidiabéticos: Da Metformina à Insulina',
    cat: 'Classe Terapêutica',
    desc: 'Curso completo sobre manejo farmacológico do diabetes. Orais, injetáveis e insulinoterapia.',
    color: '#f59e0b',
    color2: '#eab308',
    badge: 'PRÁTICO',
    thumb: '🩸',
    duration: '7h 30min',
    modules: 12,
    lessons: 44,
    price: 177.00,
    priceOld: 247.00,
    includes: ['Acesso ao Dashboard Pro', 'Calculadora de insulina'],
    modules_list: [
      { title: 'Fisiologia da Insulina', duration: '50min', lessons: 4 },
      { title: 'Diabetes Tipo 2 - Fisiopatologia', duration: '45min', lessons: 3 },
      { title: 'Metformina', duration: '40min', lessons: 3 },
      { title: 'Sulfoniluréias', duration: '30min', lessons: 2 },
      { title: 'Inibidores DPP-4', duration: '40min', lessons: 3 },
      { title: 'GLP-1 Agonistas', duration: '50min', lessons: 4 },
      { title: 'SGLT2 Inibidores', duration: '50min', lessons: 4 },
      { title: 'Insulinas - Tipos e Farmacologia', duration: '60min', lessons: 4 },
      { title: 'Insulinoterapia Intensiva', duration: '70min', lessons: 5 },
      { title: 'Hipoglicemia', duration: '30min', lessons: 2 },
      { title: 'Casos Clínicos', duration: '60min', lessons: 4 },
      { title: 'Quiz + Certificado', duration: '20min', lessons: 3 },
    ]
  },
  {
    id: 'psicotropicos',
    title: 'Psicotrópicos: Prescrição Segura e Legal',
    cat: 'Classe Terapêutica',
    desc: 'Aprenda a prescrever psicotrópicos de forma segura. Antidepressivos, ansiolíticos, antipsicóticos e controle da receita.',
    color: '#6366f1',
    color2: '#8b5cf6',
    badge: 'LEGAL',
    thumb: '🧠',
    duration: '8h',
    modules: 12,
    lessons: 45,
    price: 197.00,
    priceOld: 297.00,
    includes: ['Acesso ao Dashboard Premium', 'Modelos de receita controlada'],
    modules_list: [
      { title: 'Legislação de Psicotrópicos', duration: '60min', lessons: 4 },
      { title: 'Receita A, B, B2 e C', duration: '50min', lessons: 4 },
      { title: 'Benzodiazepínicos', duration: '60min', lessons: 4 },
      { title: 'ISRS', duration: '50min', lessons: 3 },
      { title: 'IRSN', duration: '30min', lessons: 2 },
      { title: 'Antidepressivos Tricíclicos', duration: '40min', lessons: 3 },
      { title: 'Antipsicóticos Típicos', duration: '50min', lessons: 4 },
      { title: 'Antipsicóticos Atípicos', duration: '50min', lessons: 4 },
      { title: 'Estabilizadores de Humor', duration: '40min', lessons: 3 },
      { title: 'Síndrome Serotoninérgica', duration: '30min', lessons: 2 },
      { title: 'Casos Clínicos', duration: '70min', lessons: 5 },
      { title: 'Quiz + Certificado', duration: '20min', lessons: 3 },
    ]
  },
  {
    id: 'corticoides',
    title: 'Corticoides: Uso Clínico e Manejo de Efeitos',
    cat: 'Classe Terapêutica',
    desc: 'Tudo sobre corticosteroides. Da farmacologia ao manejo de pacientes em uso crônico e desmame correto.',
    color: '#0891b2',
    color2: '#06b6d4',
    badge: 'CLÁSSICO',
    thumb: '💉',
    duration: '5h 45min',
    modules: 9,
    lessons: 32,
    price: 127.00,
    priceOld: 197.00,
    includes: ['Acesso ao Dashboard Pro', 'Tabela equivalência corticoides'],
    modules_list: [
      { title: 'Eixo HPA e Cortisol', duration: '45min', lessons: 3 },
      { title: 'Tipos de Corticoides', duration: '40min', lessons: 3 },
      { title: 'Prednisona, Prednisolona e Dexametasona', duration: '50min', lessons: 4 },
      { title: 'Indicações Clínicas', duration: '60min', lessons: 4 },
      { title: 'Efeitos Adversos', duration: '50min', lessons: 4 },
      { title: 'Desmame Correto', duration: '40min', lessons: 3 },
      { title: 'Insuficiência Adrenal', duration: '40min', lessons: 3 },
      { title: 'Casos Clínicos', duration: '50min', lessons: 4 },
      { title: 'Quiz + Certificado', duration: '20min', lessons: 4 },
    ]
  },
  {
    id: 'anticoagulantes',
    title: 'Anticoagulantes e Antiagregantes',
    cat: 'Classe Terapêutica',
    desc: 'Curso avançado sobre terapia anticoagulante. Heparinas, DOACs, varfarina e manejo perioperatório.',
    color: '#be123c',
    color2: '#f43f5e',
    badge: 'AVANÇADO',
    thumb: '🩸',
    duration: '6h 30min',
    modules: 10,
    lessons: 38,
    price: 167.00,
    priceOld: 247.00,
    includes: ['Acesso ao Dashboard Pro', 'Calculadora CHA2DS2-VASc'],
    modules_list: [
      { title: 'Cascata de Coagulação', duration: '50min', lessons: 4 },
      { title: 'Heparina Não Fracionada', duration: '40min', lessons: 3 },
      { title: 'Heparinas de Baixo Peso Molecular', duration: '45min', lessons: 4 },
      { title: 'Varfarina e INR', duration: '60min', lessons: 5 },
      { title: 'DOACs (Rivaroxabana, Apixabana)', duration: '60min', lessons: 4 },
      { title: 'Antiagregantes (AAS, Clopidogrel)', duration: '45min', lessons: 3 },
      { title: 'Manejo Perioperatório', duration: '50min', lessons: 4 },
      { title: 'Sangramento e Reversão', duration: '40min', lessons: 3 },
      { title: 'Casos Clínicos', duration: '60min', lessons: 4 },
      { title: 'Quiz + Certificado', duration: '20min', lessons: 4 },
    ]
  }
];

// ===== BUNDLES =====
const BUNDLES = [
  {
    id: 'curso_pro',
    title: '🎯 Bundle Curso + Dashboard Pro',
    desc: 'Compre qualquer curso e ganhe acesso completo ao Dashboard Pro (89+ medicamentos, calculadoras, casos clínicos).',
    price: 297.00,
    priceIndividual: 374.90,  // 197 curso + 29.90 pro
    savings: 'Economize R$ 77,90',
    includes: ['1 curso à sua escolha', 'Dashboard Pro por 30 dias', 'Todas calculadoras clínicas', 'Materiais complementares']
  },
  {
    id: 'trilha_completa',
    title: '📚 Trilha Completa: Todas as Classes',
    desc: 'Acesso vitalício aos 8 cursos + Dashboard Premium. A formação completa para médicos e farmacêuticos.',
    price: 1297.00,
    priceIndividual: 2576.00,  // 8 cursos + premium
    savings: 'Economize R$ 1.279',
    includes: ['Todos os 8 cursos', 'Dashboard Premium por 12 meses', 'Certificados de cada curso', 'Suporte prioritário', 'Atualizações gratuitas']
  },
  {
    id: 'institucional_cursos',
    title: '🏥 Institucional + Cursos',
    desc: 'Para hospitais, clínicas e faculdades. Multi-usuário + cursos para toda a equipe.',
    price: 1997.00,
    priceIndividual: 4500.00,
    savings: 'Economize R$ 2.503',
    includes: ['Dashboard Institucional (até 50 users)', 'Todos os 8 cursos', 'Painel admin dedicado', 'Treinamento da equipe', 'Suporte 24/7']
  }
];
</script>
"""

# ===== HTML DA ABA CURSOS =====
COURSES_TAB_HTML = """
<!-- ========== TAB: CURSOS ========== -->
<div class="tab-content" data-tab-content="cursos" style="display:none;">

  <!-- HEADER DA ABA -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;flex-wrap:wrap;gap:12px;">
    <div>
      <h2 style="margin:0;font-family:'Playfair Display',serif;color:#0f172a;font-size:28px;">
        🎓 Cursos Farmacêuticos
      </h2>
      <p style="margin:4px 0 0 0;color:#64748b;font-size:14px;">
        Aprenda com especialistas. Cada curso dá acesso ao Dashboard Pro.
      </p>
    </div>
    <div style="display:flex;gap:8px;align-items:center;">
      <button onclick="showMyCourses()" class="course-btn" style="background:#0f172a;">
        📚 Meus Cursos (<span id="myCoursesCount">0</span>)
      </button>
    </div>
  </div>

  <!-- BUNDLES -->
  <div class="grid-3" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:24px;">
    <div class="bundle-card" onclick="buyBundle('curso_pro')" style="cursor:pointer;">
      <div class="bundle-title">🎯 Curso + Dashboard Pro</div>
      <div class="bundle-desc">Compre um curso e ganhe 30 dias do Dashboard Pro de bônus.</div>
      <ul class="bundle-includes">
        <li>✓ 1 curso à sua escolha</li>
        <li>✓ Dashboard Pro (30 dias)</li>
        <li>✓ Todas calculadoras clínicas</li>
      </ul>
      <div>
        <span class="bundle-price">R$ 297</span>
        <span class="bundle-price-old">R$ 374,90</span>
        <span class="bundle-savings">-21%</span>
      </div>
      <button class="course-btn" style="margin-top:12px;background:white;color:#0d9488;">
        Comprar Bundle →
      </button>
    </div>

    <div class="bundle-card" onclick="buyBundle('trilha_completa')" style="cursor:pointer;background:linear-gradient(135deg,#7c3aed 0%,#a855f7 100%);">
      <div class="bundle-title">📚 Trilha Completa</div>
      <div class="bundle-desc">Os 8 cursos + Premium 12 meses. Formação completa.</div>
      <ul class="bundle-includes">
        <li>✓ Todos os 8 cursos (vitalício)</li>
        <li>✓ Dashboard Premium (12 meses)</li>
        <li>✓ 8 certificados</li>
      </ul>
      <div>
        <span class="bundle-price">R$ 1.297</span>
        <span class="bundle-price-old">R$ 2.576</span>
        <span class="bundle-savings">-50%</span>
      </div>
      <button class="course-btn" style="margin-top:12px;background:white;color:#7c3aed;">
        Comprar Trilha →
      </button>
    </div>

    <div class="bundle-card" onclick="buyBundle('institucional_cursos')" style="cursor:pointer;background:linear-gradient(135deg,#dc2626 0%,#f59e0b 100%);">
      <div class="bundle-title">🏥 Institucional</div>
      <div class="bundle-desc">Para hospitais e clínicas. Até 50 usuários.</div>
      <ul class="bundle-includes">
        <li>✓ Até 50 usuários</li>
        <li>✓ Todos os cursos</li>
        <li>✓ Painel admin</li>
      </ul>
      <div>
        <span class="bundle-price">R$ 1.997</span>
        <span class="bundle-price-old">R$ 4.500</span>
        <span class="bundle-savings">-56%</span>
      </div>
      <button class="course-btn" style="margin-top:12px;background:white;color:#dc2626;">
        Falar com Vendas →
      </button>
    </div>
  </div>

  <!-- FILTROS -->
  <div class="courses-filter">
    <button class="courses-filter-btn active" onclick="filterCourses('all', this)">Todos</button>
    <button class="courses-filter-btn" onclick="filterCourses('antibioticos', this)">Antibióticos</button>
    <button class="courses-filter-btn" onclick="filterCourses('aines', this)">AINEs</button>
    <button class="courses-filter-btn" onclick="filterCourses('analgesicos', this)">Analgésicos</button>
    <button class="courses-filter-btn" onclick="filterCourses('antihipertensivos', this)">Anti-hipertensivos</button>
    <button class="courses-filter-btn" onclick="filterCourses('diabeticos', this)">Antidiabéticos</button>
    <button class="courses-filter-btn" onclick="filterCourses('psicotropicos', this)">Psicotrópicos</button>
    <button class="courses-filter-btn" onclick="filterCourses('corticoides', this)">Corticoides</button>
    <button class="courses-filter-btn" onclick="filterCourses('anticoagulantes', this)">Anticoagulantes</button>
  </div>

  <!-- LISTA DE CURSOS -->
  <div class="courses-grid" id="coursesGrid">
    <!-- Preenchido via JS -->
  </div>

</div>

<!-- ========== MODAL: PLAYER DO CURSO ========== -->
<div class="modal" id="coursePlayerModal" role="dialog" style="max-width:900px;">
  <button type="button" class="modal-close" onclick="closeCoursePlayer()">×</button>
  <div id="coursePlayerContent"></div>
</div>

<!-- ========== MODAL: MEUS CURSOS ========== -->
<div class="modal" id="myCoursesModal" role="dialog" style="max-width:700px;">
  <button type="button" class="modal-close" onclick="closeMyCourses()">×</button>
  <div id="myCoursesContent"></div>
</div>
"""

# ===== JAVASCRIPT COMPLETO =====
COURSES_JS = """
<script>
// ========== HUB DE CURSOS - LOGICA ==========

let cursoAtivo = null;
let moduleAtivoIdx = 0;
let enrolledCourses = JSON.parse(localStorage.getItem('auxf_enrolled_courses') || '[]');

function initCourses() {
  renderCoursesGrid();
  updateMyCoursesCount();
}

function renderCoursesGrid(filter = 'all') {
  const grid = document.getElementById('coursesGrid');
  if (!grid) return;

  const filtered = filter === 'all' ? CURSOS : CURSOS.filter(c => c.id === filter);

  grid.innerHTML = filtered.map(curso => {
    const isEnrolled = enrolledCourses.includes(curso.id);
    return `
      <div class="course-card" style="--course-color:${curso.color};--course-color-2:${curso.color2};">
        ${isEnrolled ? '<div class="enrolled-badge">✓ Matriculado</div>' : ''}
        <div class="course-thumb" style="background:linear-gradient(135deg,${curso.color} 0%,${curso.color2} 100%);">
          <span class="course-thumb-badge">${curso.badge}</span>
          ${curso.thumb}
          <span class="course-thumb-overlay">${curso.modules} módulos • ${curso.lessons} aulas</span>
        </div>
        <div class="course-body">
          <div class="course-cat">${curso.cat}</div>
          <h3 class="course-title">${curso.title}</h3>
          <p class="course-desc">${curso.desc}</p>
          <div class="course-meta">
            <span class="course-meta-item">⏱️ ${curso.duration}</span>
            <span class="course-meta-item">📚 ${curso.modules} módulos</span>
            <span class="course-meta-item">🎬 ${curso.lessons} aulas</span>
            <span class="course-meta-item">🎓 Certificado</span>
          </div>
          <div class="course-footer">
            <div>
              <span class="course-price">R$ ${curso.price.toFixed(2).replace('.', ',')}</span>
              <span class="course-price-old">R$ ${curso.priceOld.toFixed(2).replace('.', ',')}</span>
            </div>
            ${isEnrolled
              ? `<button class="course-btn course-btn-enrolled" onclick="openCourse('${curso.id}')">▶ Assistir</button>`
              : `<button class="course-btn" onclick="buyCourse('${curso.id}')">Comprar</button>`
            }
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function filterCourses(cat, btn) {
  document.querySelectorAll('.courses-filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderCoursesGrid(cat);
}

function buyCourse(cursoId) {
  const curso = CURSOS.find(c => c.id === cursoId);
  if (!curso) return;

  const message = `Comprar "${curso.title}"\\n\\nValor: R$ ${curso.price.toFixed(2).replace('.', ',')}\\n\\n🎁 BONUS: Inclui acesso ao Dashboard Pro por 30 dias!\\n\\nConfirmar compra?`;

  if (confirm(message)) {
    enrollStudent(cursoId);
    alert(`✅ Compra realizada!\\n\\nVocê foi matriculado em "${curso.title}"\\n\\n✓ Dashboard Pro ativado por 30 dias\\n\\nAcesse "Meus Cursos" para começar.`);
  }
}

function buyBundle(bundleId) {
  const bundle = BUNDLES.find(b => b.id === bundleId);
  if (!bundle) return;

  const message = `${bundle.title}\\n\\n${bundle.desc}\\n\\nValor: R$ ${bundle.price.toFixed(2).replace('.', ',')} (de R$ ${bundle.priceIndividual.toFixed(2).replace('.', ',')})\\n\\n${bundle.savings}\\n\\nConfirmar compra?`;

  if (bundleId === 'institucional_cursos') {
    window.location.href = 'mailto:vendas@auxfarmacia.com.br?subject=Interesse no bundle institucional';
    return;
  }

  if (confirm(message)) {
    // Matricula em todos os cursos do bundle
    if (bundleId === 'curso_pro') {
      enrollStudent('escolhido'); // placeholder
      alert('✅ Bundle comprado! Escolha seu curso no painel.');
    } else if (bundleId === 'trilha_completa') {
      CURSOS.forEach(c => enrollStudent(c.id));
      alert('✅ Trilha completa adquirida!\\n\\n✓ Todos os 8 cursos liberados\\n✓ Dashboard Premium ativado por 12 meses\\n\\nBoa jornada!');
    }
  }
}

function enrollStudent(cursoId) {
  if (!enrolledCourses.includes(cursoId)) {
    enrolledCourses.push(cursoId);
    localStorage.setItem('auxf_enrolled_courses', JSON.stringify(enrolledCourses));
    updateMyCoursesCount();
    renderCoursesGrid();
    grantDashboardAccess();
  }
}

function grantDashboardAccess() {
  // Cross-sell: comprar curso da acesso ao Dashboard Pro
  const currentLic = JSON.parse(localStorage.getItem('auxf_license') || '{}');
  if (currentLic.tier !== 'pro' && currentLic.tier !== 'premium' && currentLic.tier !== 'institutional') {
    const proLic = {
      tier: 'pro',
      key: 'AUXFARMA-COURSE-BONUS-2024',
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      activatedAt: new Date().toISOString(),
      source: 'course-purchase'
    };
    localStorage.setItem('auxf_license', JSON.stringify(proLic));
  }
}

function openCourse(cursoId) {
  if (!enrolledCourses.includes(cursoId)) {
    return buyCourse(cursoId);
  }

  cursoAtivo = CURSOS.find(c => c.id === cursoId);
  moduleAtivoIdx = 0;
  renderCoursePlayer();
  document.getElementById('coursePlayerModal').classList.add('open');
}

function renderCoursePlayer() {
  const content = document.getElementById('coursePlayerContent');
  if (!content || !cursoAtivo) return;

  const module = cursoAtivo.modules_list[moduleAtivoIdx];
  const progress = ((moduleAtivoIdx + 1) / cursoAtivo.modules_list.length) * 100;

  content.innerHTML = `
    <div class="course-player" style="background:#0f172a;border-radius:16px;overflow:hidden;">
      <div class="course-video" style="background:linear-gradient(135deg,${cursoAtivo.color} 0%,${cursoAtivo.color2} 100%);">
        <div style="font-size:80px;">${cursoAtivo.thumb}</div>
        <div style="position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,0.7);padding:16px;display:flex;align-items:center;gap:12px;color:white;">
          <button style="background:white;color:#0f172a;border:none;border-radius:50%;width:48px;height:48px;font-size:24px;cursor:pointer;">▶</button>
          <div style="flex:1;">
            <div style="font-weight:600;font-size:14px;margin-bottom:4px;">${module.title}</div>
            <div class="progress-bar"><div class="progress-fill" style="width:${progress}%;"></div></div>
          </div>
          <span style="font-size:12px;">${Math.round(progress)}% completo</span>
        </div>
      </div>

      <div class="course-player-body">
        <div class="course-player-title">${cursoAtivo.title}</div>
        <div class="course-player-meta">Módulo ${moduleAtivoIdx + 1} de ${cursoAtivo.modules_list.length} • ${module.duration} • ${module.lessons} aulas</div>

        <div class="course-tabs">
          <div class="course-tab active" onclick="switchCourseTab('aulas', this)">📚 Aulas</div>
          <div class="course-tab" onclick="switchCourseTab('materiais', this)">📄 Materiais</div>
          <div class="course-tab" onclick="switchCourseTab('quiz', this)">📝 Quiz</div>
          <div class="course-tab" onclick="switchCourseTab('certificado', this)">🎓 Certificado</div>
        </div>

        <div id="courseTabContent">
          <ul class="modules-list">
            ${cursoAtivo.modules_list.map((m, i) => `
              <li class="module-item ${i === moduleAtivoIdx ? 'active' : ''} ${i < moduleAtivoIdx ? 'module-done' : ''}"
                  onclick="goToModule(${i})">
                <div class="module-icon ${i < moduleAtivoIdx ? 'done' : ''}">
                  ${i < moduleAtivoIdx ? '✓' : i + 1}
                </div>
                <div class="module-info">
                  <div class="module-title">${m.title}</div>
                  <div class="module-meta">${m.duration} • ${m.lessons} aulas</div>
                </div>
                <div class="module-status">
                  ${i < moduleAtivoIdx ? '✓ Concluído' : i === moduleAtivoIdx ? '▶ Assistindo' : '○ Bloqueado'}
                </div>
              </li>
            `).join('')}
          </ul>
        </div>

        <div style="display:flex;gap:8px;margin-top:20px;">
          <button onclick="goToModule(${Math.max(0, moduleAtivoIdx - 1)})" class="course-btn" style="background:#475569;" ${moduleAtivoIdx === 0 ? 'disabled' : ''}>
            ← Anterior
          </button>
          <button onclick="goToModule(${Math.min(cursoAtivo.modules_list.length - 1, moduleAtivoIdx + 1)})" class="course-btn" style="flex:1;background:${cursoAtivo.color};" ${moduleAtivoIdx >= cursoAtivo.modules_list.length - 1 ? 'disabled' : ''}>
            ${moduleAtivoIdx >= cursoAtivo.modules_list.length - 1 ? 'Finalizar Curso →' : 'Próximo Módulo →'}
          </button>
        </div>
      </div>
    </div>
  `;
}

function goToModule(idx) {
  moduleAtivoIdx = idx;
  renderCoursePlayer();
}

function switchCourseTab(tab, btn) {
  document.querySelectorAll('.course-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const content = document.getElementById('courseTabContent');
  if (!content || !cursoAtivo) return;

  if (tab === 'aulas') {
    renderCoursePlayer();
  } else if (tab === 'materiais') {
    content.innerHTML = `
      <div style="background:rgba(255,255,255,0.05);padding:20px;border-radius:12px;color:white;">
        <h4 style="margin-top:0;">📄 Materiais Complementares</h4>
        <ul style="list-style:none;padding:0;">
          <li style="padding:8px 0;border-bottom:1px solid #334155;">📋 Tabela de medicamentos da classe (PDF, 24 páginas)</li>
          <li style="padding:8px 0;border-bottom:1px solid #334155;">📊 Mapa mental das interações (PNG alta resolução)</li>
          <li style="padding:8px 0;border-bottom:1px solid #334155;">📝 Resumo executivo (PDF, 8 páginas)</li>
          <li style="padding:8px 0;">🎯 Checklist de prescrição segura (PDF)</li>
        </ul>
        <button onclick="alert('Download iniciado')" class="course-btn" style="background:${cursoAtivo.color};margin-top:12px;">
          📥 Baixar Todos os Materiais
        </button>
      </div>
    `;
  } else if (tab === 'quiz') {
    content.innerHTML = `
      <div class="quiz-question">
        <div class="quiz-q">1. Qual o principal mecanismo de ação dos betalactâmicos?</div>
        <div class="quiz-options">
          <button class="quiz-option" onclick="checkAnswer(this, false)">A) Inibição da síntese proteica</button>
          <button class="quiz-option" onclick="checkAnswer(this, true)">B) Inibição da síntese da parede celular</button>
          <button class="quiz-option" onclick="checkAnswer(this, false)">C) Inibição da DNA girase</button>
          <button class="quiz-option" onclick="checkAnswer(this, false)">D) Bloqueio do folato</button>
        </div>
      </div>
      <div style="color:#94a3b8;font-size:13px;text-align:center;margin-top:12px;">
        ✓ 1 de 10 questões | Aprovação: 70%
      </div>
    `;
  } else if (tab === 'certificado') {
    content.innerHTML = `
      <div class="certificate">
        <div class="cert-seal">🎓</div>
        <h3 class="cert-title">Certificado Digital</h3>
        <p class="cert-text">
          Após concluir todos os módulos e obter 70% no quiz final,<br>
          você receberá um certificado digital de ${cursoAtivo.modules * 2}h carga horária,<br>
          válido em todo território nacional.
        </p>
        <div style="background:rgba(255,255,255,0.4);padding:16px;border-radius:8px;margin:16px 0;">
          <strong>Progresso:</strong> ${moduleAtivoIdx} / ${cursoAtivo.modules_list.length} módulos
        </div>
        <div style="background:#d1fae5;padding:12px;border-radius:8px;color:#065f46;font-size:13px;">
          📌 Complete todos os módulos para liberar o certificado.
        </div>
      </div>
    `;
  }
}

function checkAnswer(btn, correct) {
  const opts = btn.parentElement.querySelectorAll('.quiz-option');
  opts.forEach(o => o.style.pointerEvents = 'none');
  if (correct) {
    btn.classList.add('correct');
    setTimeout(() => alert('✅ Resposta correta! +10 XP'), 200);
  } else {
    btn.classList.add('wrong');
    opts.forEach(o => { if (o.onclick.toString().includes('true')) o.classList.add('correct'); });
  }
}

function closeCoursePlayer() {
  document.getElementById('coursePlayerModal').classList.remove('open');
  cursoAtivo = null;
}

function showMyCourses() {
  const modal = document.getElementById('myCoursesModal');
  const content = document.getElementById('myCoursesContent');

  if (enrolledCourses.length === 0) {
    content.innerHTML = `
      <h2 style="margin-top:0;color:#0f172a;">📚 Meus Cursos</h2>
      <div style="text-align:center;padding:40px 20px;color:#64748b;">
        <div style="font-size:64px;margin-bottom:12px;opacity:0.4;">🎓</div>
        <p>Você ainda não comprou nenhum curso.</p>
        <p style="font-size:13px;">Compre um curso individual ou um bundle.</p>
        <button onclick="closeMyCourses()" class="course-btn" style="background:#0d9488;margin-top:16px;">
          Ver Cursos Disponíveis
        </button>
      </div>
    `;
  } else {
    const cursos = enrolledCourses.map(id => CURSOS.find(c => c.id === id)).filter(Boolean);
    content.innerHTML = `
      <h2 style="margin-top:0;color:#0f172a;font-family:'Playfair Display',serif;">📚 Meus Cursos (${cursos.length})</h2>
      <div style="display:flex;flex-direction:column;gap:12px;margin-top:16px;">
        ${cursos.map(c => `
          <div style="display:flex;align-items:center;gap:12px;padding:16px;border:1px solid #e2e8f0;border-radius:12px;">
            <div style="width:60px;height:60px;border-radius:12px;background:linear-gradient(135deg,${c.color},${c.color2});display:flex;align-items:center;justify-content:center;font-size:32px;">
              ${c.thumb}
            </div>
            <div style="flex:1;">
              <div style="font-weight:600;color:#0f172a;">${c.title}</div>
              <div style="font-size:12px;color:#64748b;">${c.modules} módulos • ${c.duration}</div>
            </div>
            <button onclick="closeMyCourses(); openCourse('${c.id}')" class="course-btn" style="background:${c.color};">
              ▶ Continuar
            </button>
          </div>
        `).join('')}
      </div>
    `;
  }

  modal.classList.add('open');
}

function closeMyCourses() {
  document.getElementById('myCoursesModal').classList.remove('open');
}

function updateMyCoursesCount() {
  const el = document.getElementById('myCoursesCount');
  if (el) el.textContent = enrolledCourses.length;
}

// Hook na navegacao de tabs para inicializar
const origShowTab = window.showTabContent;
if (typeof origShowTab === 'function') {
  window.showTabContent = function(tab) {
    origShowTab(tab);
    if (tab === 'cursos') initCourses();
  };
} else {
  // Watch pra mudanca de tab
  document.addEventListener('click', e => {
    if (e.target.closest('[data-tab="cursos"]')) {
      setTimeout(initCourses, 100);
    }
  });
}

// Init
document.addEventListener('DOMContentLoaded', initCourses);
setTimeout(initCourses, 500);
</script>
"""

# Função para adicionar aba Cursos à navegação
TAB_NAV_HTML = """
<a href="#cursos" class="site-tab" data-tab="cursos" onclick="showTabContent('cursos')">
  <span class="site-tab-icon">🎓</span>
  Cursos
  <span class="site-tab-badge pro">NOVO</span>
</a>
"""


def adicionar_cursos(html: str) -> str:
    """Adiciona o hub de cursos"""

    # 1. Adiciona CSS
    if 'HUB DE CURSOS' not in html:
        html = html.replace('</style>', '</style>\n' + COURSES_CSS, 1)

    # 2. Adiciona dados dos cursos (antes do </body>)
    if 'const CURSOS =' not in html:
        html = html.replace('</body>', COURSES_DATA + '\n</body>', 1)

    # 3. Adiciona aba de cursos no nav (após as outras abas)
    if 'data-tab="cursos"' not in html:
        # Procura pela última aba
        html = re.sub(
            r'(<a[^>]*data-tab="prescricao"[^>]*>[^<]*</a>\s*</a>)',
            lambda m: m.group(1) + '\n' + TAB_NAV_HTML,
            html,
            count=1
        )

    # 4. Adiciona conteúdo da tab cursos (próximo do final do conteúdo das tabs)
    if 'tab-content" data-tab-content="cursos"' not in html:
        # Procura pela última tab-content
        html = re.sub(
            r'(<div class="tab-content" data-tab-content="prescricao")',
            lambda m: COURSES_TAB_HTML + '\n' + m.group(1),
            html,
            count=1
        )

    # 5. Adiciona o JS
    if 'HUB DE CURSOS - LOGICA' not in html:
        html = html.replace('</body>', COURSES_JS + '\n</body>', 1)

    return html


def processar_arquivo(arquivo: Path):
    print(f"🎓 Processando: {arquivo.name}")
    with open(arquivo, 'r', encoding='utf-8') as f:
        html = f.read()

    original = len(html)
    html = adicionar_cursos(html)

    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"   ✅ Adicionados {len(html) - original:,} caracteres")


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
    print("🎓 Adicionando Hub de Cursos Farmacêuticos")
    print("=" * 60)

    for arquivo in arquivos:
        path = output / arquivo
        if path.exists():
            processar_arquivo(path)

    print()
    print("✅ Hub de Cursos adicionado!")
    print()
    print("📚 8 cursos por classe:")
    print("  - Antibioticoterapia")
    print("  - AINEs")
    print("  - Analgésicos")
    print("  - Anti-hipertensivos")
    print("  - Antidiabéticos")
    print("  - Psicotrópicos")
    print("  - Corticoides")
    print("  - Anticoagulantes")
    print()
    print("🎁 3 bundles com cross-sell:")
    print("  - Curso + Dashboard Pro (R$ 297)")
    print("  - Trilha Completa + Premium (R$ 1.297)")
    print("  - Institucional + Cursos (R$ 1.997)")


if __name__ == "__main__":
    main()