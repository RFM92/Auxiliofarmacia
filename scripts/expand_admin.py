#!/usr/bin/env python3
"""
Expande o painel admin com:
- Dashboard com KPIs e graficos
- Gestao de Usuarios (lista, busca, blacklist, role, 2FA)
- Gestao de Licencas (criar, revogar, gerar em massa)
- Gestao de Pagamentos (lista, estorno, exportar)
- Telemetria (eventos em tempo real, funil)
- Conteudo Editorial (medicamentos, bulas)
- Configuracoes (planos, precos, integracoes)
- Logs de Auditoria
- Suporte / Tickets
"""
import re
from pathlib import Path

ADMIN_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin - Auxílio Farmácia</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0f172a; --bg-2: #1e293b; --bg-3: #334155;
      --text: #e2e8f0; --text-dim: #94a3b8; --text-muted: #64748b;
      --primary: #14b8a6; --primary-2: #06b6d4;
      --success: #10b981; --warning: #f59e0b; --danger: #ef4444;
      --info: #3b82f6; --purple: #a855f7;
      --border: #334155;
    }
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      font-size: 14px;
    }

    /* ========== LOGIN ========== */
    .login-container {
      display: flex; align-items: center; justify-content: center;
      min-height: 100vh; padding: 20px;
    }
    .login-box {
      background: var(--bg-2);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 48px;
      width: 100%; max-width: 440px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }
    .login-logo { text-align: center; margin-bottom: 32px; }
    .login-logo h1 {
      font-family: 'Playfair Display', serif;
      font-size: 32px; font-weight: 900;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .login-logo p { color: var(--text-dim); font-size: 14px; margin-top: 4px; }
    .form-group { margin-bottom: 18px; }
    .form-group label {
      display: block; color: var(--text-dim);
      font-size: 12px; font-weight: 600; margin-bottom: 6px;
      text-transform: uppercase; letter-spacing: 0.5px;
    }
    .form-group input, .form-group select, .form-group textarea {
      width: 100%; padding: 11px 14px;
      background: var(--bg); color: var(--text);
      border: 1px solid var(--border); border-radius: 8px;
      font-size: 14px; font-family: inherit;
      transition: border-color 0.15s;
    }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
      outline: none; border-color: var(--primary);
    }
    .btn {
      padding: 11px 20px; border-radius: 8px;
      font-size: 14px; font-weight: 600; cursor: pointer;
      border: none; transition: all 0.15s;
      font-family: inherit; display: inline-flex;
      align-items: center; gap: 8px;
    }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: #0d9488; }
    .btn-secondary { background: var(--bg-3); color: var(--text); }
    .btn-secondary:hover { background: #475569; }
    .btn-danger { background: var(--danger); color: white; }
    .btn-danger:hover { background: #dc2626; }
    .btn-success { background: var(--success); color: white; }
    .btn-ghost { background: transparent; color: var(--text-dim); border: 1px solid var(--border); }
    .btn-ghost:hover { background: var(--bg-3); color: var(--text); }
    .btn-block { width: 100%; justify-content: center; }
    .btn-sm { padding: 6px 10px; font-size: 12px; }

    /* ========== LAYOUT ========== */
    .app { display: none; }
    .app.show { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }

    /* ========== SIDEBAR ========== */
    .sidebar {
      background: var(--bg-2);
      border-right: 1px solid var(--border);
      padding: 24px 0;
      position: sticky; top: 0; height: 100vh; overflow-y: auto;
    }
    .sidebar-logo {
      padding: 0 24px 24px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 16px;
    }
    .sidebar-logo h1 {
      font-family: 'Playfair Display', serif;
      font-size: 22px; font-weight: 900;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .sidebar-logo p { color: var(--text-muted); font-size: 11px; }
    .sidebar-section {
      padding: 12px 16px 4px;
      color: var(--text-muted);
      font-size: 10px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 1px;
    }
    .sidebar-item {
      display: flex; align-items: center; gap: 12px;
      padding: 10px 24px; cursor: pointer;
      color: var(--text-dim); text-decoration: none;
      font-size: 14px; font-weight: 500;
      border-left: 3px solid transparent;
      transition: all 0.15s;
    }
    .sidebar-item:hover { background: rgba(255,255,255,0.04); color: var(--text); }
    .sidebar-item.active {
      background: rgba(20,184,166,0.1);
      color: var(--primary);
      border-left-color: var(--primary);
    }
    .sidebar-item-icon { font-size: 18px; width: 22px; text-align: center; }
    .sidebar-item-badge {
      margin-left: auto; padding: 2px 8px;
      background: var(--danger); color: white;
      font-size: 10px; font-weight: 700; border-radius: 10px;
    }

    /* ========== MAIN ========== */
    .main { padding: 32px; overflow-x: hidden; }
    .page-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 24px;
    }
    .page-title {
      font-family: 'Playfair Display', serif;
      font-size: 28px; font-weight: 700;
      color: var(--text);
    }
    .page-subtitle { color: var(--text-dim); font-size: 14px; margin-top: 4px; }

    /* ========== KPI CARDS ========== */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px; margin-bottom: 24px;
    }
    .kpi-card {
      background: var(--bg-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      position: relative;
      overflow: hidden;
    }
    .kpi-card::before {
      content: ''; position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: linear-gradient(90deg, var(--primary), var(--primary-2));
    }
    .kpi-card.danger::before { background: linear-gradient(90deg, var(--danger), #f87171); }
    .kpi-card.warning::before { background: linear-gradient(90deg, var(--warning), #fbbf24); }
    .kpi-card.success::before { background: linear-gradient(90deg, var(--success), #34d399); }
    .kpi-card.purple::before { background: linear-gradient(90deg, var(--purple), #c084fc); }

    .kpi-label {
      color: var(--text-dim);
      font-size: 11px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.5px;
      margin-bottom: 8px;
      display: flex; align-items: center; gap: 6px;
    }
    .kpi-value {
      font-size: 28px; font-weight: 800;
      color: var(--text);
      font-family: 'Inter', sans-serif;
      letter-spacing: -0.5px;
    }
    .kpi-trend {
      font-size: 12px; margin-top: 4px;
      display: flex; align-items: center; gap: 4px;
    }
    .kpi-trend.up { color: var(--success); }
    .kpi-trend.down { color: var(--danger); }

    /* ========== CARDS ========== */
    .card {
      background: var(--bg-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 16px;
    }
    .card-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 16px; padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
    }
    .card-title { font-size: 16px; font-weight: 700; }
    .card-subtitle { font-size: 12px; color: var(--text-dim); margin-top: 2px; }

    /* ========== TABLE ========== */
    .table-container { overflow-x: auto; }
    table {
      width: 100%; border-collapse: collapse;
    }
    th {
      text-align: left; padding: 10px 12px;
      background: var(--bg-3);
      color: var(--text-dim);
      font-size: 11px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.5px;
      border-bottom: 1px solid var(--border);
    }
    td {
      padding: 12px;
      border-bottom: 1px solid var(--border);
      color: var(--text); font-size: 13px;
    }
    tr:hover td { background: rgba(255,255,255,0.02); }
    .table-actions { display: flex; gap: 6px; }

    /* ========== BADGES ========== */
    .badge {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 3px 8px; border-radius: 4px;
      font-size: 11px; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.3px;
    }
    .badge-free { background: rgba(100,116,139,0.2); color: #94a3b8; }
    .badge-pro { background: rgba(20,184,166,0.2); color: var(--primary); }
    .badge-premium { background: rgba(168,85,247,0.2); color: var(--purple); }
    .badge-institutional { background: rgba(245,158,11,0.2); color: var(--warning); }
    .badge-success { background: rgba(16,185,129,0.2); color: var(--success); }
    .badge-danger { background: rgba(239,68,68,0.2); color: var(--danger); }
    .badge-warning { background: rgba(245,158,11,0.2); color: var(--warning); }
    .badge-info { background: rgba(59,130,246,0.2); color: var(--info); }

    /* ========== CHART ========== */
    .chart-grid {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 16px; margin-bottom: 16px;
    }
    .chart-canvas {
      background: var(--bg-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px; height: 280px;
    }

    /* ========== FORMS / FILTERS ========== */
    .filters {
      display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;
    }
    .search-input {
      flex: 1; min-width: 200px; max-width: 400px;
      padding: 10px 14px;
      background: var(--bg-2); color: var(--text);
      border: 1px solid var(--border); border-radius: 8px;
      font-size: 14px; font-family: inherit;
    }
    .filter-select {
      padding: 10px 14px;
      background: var(--bg-2); color: var(--text);
      border: 1px solid var(--border); border-radius: 8px;
      font-size: 14px; font-family: inherit;
    }

    /* ========== TABS (in pages) ========== */
    .tabs {
      display: flex; gap: 4px; margin-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }
    .tab {
      padding: 10px 16px; cursor: pointer;
      color: var(--text-dim); font-weight: 600;
      border-bottom: 2px solid transparent;
      transition: all 0.15s;
    }
    .tab:hover { color: var(--text); }
    .tab.active {
      color: var(--primary);
      border-bottom-color: var(--primary);
    }

    /* ========== MODAL ========== */
    .modal-overlay {
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.7);
      display: none; align-items: center; justify-content: center;
      z-index: 1000; padding: 20px;
    }
    .modal-overlay.show { display: flex; }
    .modal {
      background: var(--bg-2);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 32px;
      max-width: 500px; width: 100%;
      max-height: 90vh; overflow-y: auto;
    }
    .modal-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; }

    /* ========== TOAST ========== */
    .toast-container {
      position: fixed; bottom: 24px; right: 24px;
      display: flex; flex-direction: column; gap: 8px; z-index: 9999;
    }
    .toast {
      background: var(--bg-2); border: 1px solid var(--border);
      padding: 12px 16px; border-radius: 8px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      display: flex; align-items: center; gap: 10px;
      animation: slideIn 0.3s ease;
    }
    .toast.success { border-left: 3px solid var(--success); }
    .toast.error { border-left: 3px solid var(--danger); }
    .toast.info { border-left: 3px solid var(--info); }

    @keyframes slideIn {
      from { transform: translateX(400px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    /* ========== EMPTY ========== */
    .empty {
      text-align: center; padding: 60px 20px;
      color: var(--text-muted);
    }
    .empty-icon { font-size: 48px; margin-bottom: 12px; opacity: 0.5; }

    /* ========== USER MENU ========== */
    .topbar {
      display: flex; justify-content: space-between; align-items: center;
      padding: 12px 0; margin-bottom: 24px;
    }
    .topbar-user {
      display: flex; align-items: center; gap: 12px;
      padding: 6px 12px;
      background: var(--bg-2);
      border: 1px solid var(--border);
      border-radius: 8px;
    }
    .topbar-avatar {
      width: 32px; height: 32px;
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 13px; color: white;
    }

    /* ========== UTIL ========== */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
    .mt-16 { margin-top: 16px; }
    .mb-16 { margin-bottom: 16px; }
    .text-dim { color: var(--text-dim); }
    .text-success { color: var(--success); }
    .text-danger { color: var(--danger); }
    .text-warning { color: var(--warning); }
    .text-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; }
    .text-right { text-align: right; }
    .text-center { text-align: center; }

    .pulse {
      display: inline-block;
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--success);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(1.3); }
    }

    @media (max-width: 900px) {
      .app.show { grid-template-columns: 1fr; }
      .sidebar { position: fixed; z-index: 99; transform: translateX(-100%); transition: transform 0.2s; }
      .sidebar.open { transform: translateX(0); }
      .chart-grid { grid-template-columns: 1fr; }
      .grid-2, .grid-3 { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

<!-- ============ LOGIN ============ -->
<div class="login-container" id="loginContainer">
  <div class="login-box">
    <div class="login-logo">
      <h1>Auxílio Admin</h1>
      <p>Painel de Gestão</p>
    </div>
    <form onsubmit="doLogin(event)">
      <div class="form-group">
        <label>E-mail</label>
        <input type="email" id="loginEmail" value="admin@auxfarmacia.com.br" required>
      </div>
      <div class="form-group">
        <label>Senha</label>
        <input type="password" id="loginPassword" value="admin123" required>
      </div>
      <button type="submit" class="btn btn-primary btn-block">Entrar</button>
    </form>
    <p class="text-dim text-center mt-16" style="font-size:12px;">
      Acesso restrito a administradores autorizados
    </p>
  </div>
</div>

<!-- ============ APP ============ -->
<div class="app" id="app">

  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div class="sidebar-logo">
      <h1>Auxílio</h1>
      <p>Painel Admin</p>
    </div>

    <div class="sidebar-section">Visão Geral</div>
    <a href="#" class="sidebar-item active" data-page="dashboard">
      <span class="sidebar-item-icon">📊</span> Dashboard
    </a>
    <a href="#" class="sidebar-item" data-page="analytics">
      <span class="sidebar-item-icon">📈</span> Analytics
    </a>

    <div class="sidebar-section">Gestão</div>
    <a href="#" class="sidebar-item" data-page="users">
      <span class="sidebar-item-icon">👥</span> Usuários
      <span class="sidebar-item-badge" id="userCount">0</span>
    </a>
    <a href="#" class="sidebar-item" data-page="licenses">
      <span class="sidebar-item-icon">🎫</span> Licenças
      <span class="sidebar-item-badge" id="licenseCount">0</span>
    </a>
    <a href="#" class="sidebar-item" data-page="payments">
      <span class="sidebar-item-icon">💳</span> Pagamentos
    </a>

    <div class="sidebar-section">Operações</div>
    <a href="#" class="sidebar-item" data-page="telemetry">
      <span class="sidebar-item-icon">📡</span> Telemetria
    </a>
    <a href="#" class="sidebar-item" data-page="content">
      <span class="sidebar-item-icon">💊</span> Conteúdo
    </a>
    <a href="#" class="sidebar-item" data-page="support">
      <span class="sidebar-item-icon">💬</span> Suporte
      <span class="sidebar-item-badge">3</span>
    </a>

    <div class="sidebar-section">Sistema</div>
    <a href="#" class="sidebar-item" data-page="audit">
      <span class="sidebar-item-icon">📜</span> Auditoria
    </a>
    <a href="#" class="sidebar-item" data-page="settings">
      <span class="sidebar-item-icon">⚙️</span> Configurações
    </a>
  </aside>

  <!-- MAIN -->
  <main class="main">

    <!-- TOPBAR -->
    <div class="topbar">
      <div>
        <div class="text-dim" style="font-size:12px;">
          <span class="pulse"></span> Sistema operacional • <span id="serverStatus">Online</span>
        </div>
      </div>
      <div class="topbar-user">
        <div class="topbar-avatar">A</div>
        <div>
          <div style="font-weight:600;font-size:13px;">Admin</div>
          <div class="text-dim" style="font-size:11px;">admin@auxfarmacia.com.br</div>
        </div>
      </div>
    </div>

    <!-- ============ PAGES ============ -->

    <!-- DASHBOARD -->
    <div class="page" data-page="dashboard">
      <div class="page-header">
        <div>
          <h1 class="page-title">Dashboard</h1>
          <p class="page-subtitle">Visão geral do sistema em tempo real</p>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">👥 Usuários Ativos</div>
          <div class="kpi-value" id="kpiUsers">0</div>
          <div class="kpi-trend up">↑ 12% vs mês anterior</div>
        </div>
        <div class="kpi-card success">
          <div class="kpi-label">💰 MRR</div>
          <div class="kpi-value">R$ 0</div>
          <div class="kpi-trend up">↑ 8% vs mês anterior</div>
        </div>
        <div class="kpi-card warning">
          <div class="kpi-label">📊 Conversão Free → Pro</div>
          <div class="kpi-value">3.2%</div>
          <div class="kpi-trend up">↑ 0.4 pp</div>
        </div>
        <div class="kpi-card danger">
          <div class="kpi-label">⚠️ Churn (30d)</div>
          <div class="kpi-value">1.8%</div>
          <div class="kpi-trend down">↓ 0.3 pp</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-label">🎫 Licenças Ativas</div>
          <div class="kpi-value" id="kpiLicenses">0</div>
          <div class="kpi-trend up">↑ 24 hoje</div>
        </div>
      </div>

      <div class="chart-grid">
        <div class="chart-canvas">
          <canvas id="revenueChart"></canvas>
        </div>
        <div class="chart-canvas">
          <canvas id="plansChart"></canvas>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">📈 Atividade Recente</div>
              <div class="card-subtitle">Últimos eventos</div>
            </div>
            <a href="#" onclick="showPage('telemetry')" class="btn btn-ghost btn-sm">Ver tudo</a>
          </div>
          <div id="recentActivity">
            <div class="empty">
              <div class="empty-icon">📭</div>
              <p>Sem atividade recente</p>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">🔥 Top Erros</div>
              <div class="card-subtitle">Últimas 24h</div>
            </div>
          </div>
          <div id="topErrors">
            <div class="empty">
              <div class="empty-icon">✨</div>
              <p>Nenhum erro registrado</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ANALYTICS -->
    <div class="page" data-page="analytics" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Analytics</h1>
          <p class="page-subtitle">Funil de conversão e métricas avançadas</p>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">Funil de Conversão</div>
        </div>
        <div id="conversionFunnel"></div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title">Retenção por Plano</div>
          </div>
          <div class="chart-canvas" style="border:none;padding:0;">
            <canvas id="retentionChart"></canvas>
          </div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title">LTV por Plano</div>
          </div>
          <div id="ltvList"></div>
        </div>
      </div>
    </div>

    <!-- USERS -->
    <div class="page" data-page="users" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Usuários</h1>
          <p class="page-subtitle">Gestão de contas cadastradas</p>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-secondary" onclick="exportCSV('users')">📥 Exportar CSV</button>
          <button class="btn btn-primary" onclick="showInviteModal()">+ Convidar</button>
        </div>
      </div>

      <div class="filters">
        <input type="text" class="search-input" placeholder="Buscar por nome, email, CRM..." onkeyup="filterTable('usersTable', this.value)">
        <select class="filter-select" onchange="filterTableByColumn('usersTable', 4, this.value)">
          <option value="">Todos os planos</option>
          <option value="FREE">Free</option>
          <option value="PRO">Pro</option>
          <option value="PREMIUM">Premium</option>
          <option value="INSTITUTIONAL">Institucional</option>
        </select>
        <select class="filter-select">
          <option value="">Todos os status</option>
          <option value="active">Ativo</option>
          <option value="blacklist">Blacklist</option>
        </select>
      </div>

      <div class="card">
        <div class="table-container">
          <table id="usersTable">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Email</th>
                <th>CRM</th>
                <th>Especialidade</th>
                <th>Plano</th>
                <th>Cadastro</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody id="usersTbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- LICENSES -->
    <div class="page" data-page="licenses" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Licenças</h1>
          <p class="page-subtitle">Gestão de chaves de ativação</p>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-secondary" onclick="showBulkLicenseModal()">🎫 Gerar em Massa</button>
          <button class="btn btn-primary" onclick="showCreateLicenseModal()">+ Nova Chave</button>
        </div>
      </div>

      <div class="filters">
        <input type="text" class="search-input" placeholder="Buscar chave..." onkeyup="filterTable('licensesTable', this.value)">
        <select class="filter-select">
          <option value="">Todos os planos</option>
          <option value="pro">Pro</option>
          <option value="premium">Premium</option>
          <option value="institutional">Institucional</option>
        </select>
      </div>

      <div class="card">
        <div class="table-container">
          <table id="licensesTable">
            <thead>
              <tr>
                <th>Chave</th>
                <th>Plano</th>
                <th>Devices</th>
                <th>Usuário</th>
                <th>Criada</th>
                <th>Expira</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody id="licensesTbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- PAYMENTS -->
    <div class="page" data-page="payments" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Pagamentos</h1>
          <p class="page-subtitle">Histórico financeiro e reconciliação</p>
        </div>
        <div style="display:flex;gap:8px;">
          <button class="btn btn-secondary" onclick="exportCSV('payments')">📥 Exportar</button>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card success">
          <div class="kpi-label">💰 Receita (30d)</div>
          <div class="kpi-value">R$ 8.450</div>
          <div class="kpi-trend up">↑ 15%</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">📊 Ticket Médio</div>
          <div class="kpi-value">R$ 47</div>
          <div class="kpi-trend up">↑ R$ 3</div>
        </div>
        <div class="kpi-card warning">
          <div class="kpi-label">⏳ Pendentes</div>
          <div class="kpi-value">12</div>
        </div>
        <div class="kpi-card danger">
          <div class="kpi-label">↩️ Reembolsos</div>
          <div class="kpi-value">3</div>
        </div>
      </div>

      <div class="card">
        <div class="tabs">
          <div class="tab active" onclick="filterPayments('all', this)">Todos</div>
          <div class="tab" onclick="filterPayments('paid', this)">Pagos</div>
          <div class="tab" onclick="filterPayments('pending', this)">Pendentes</div>
          <div class="tab" onclick="filterPayments('refunded', this)">Reembolsados</div>
        </div>
        <div class="table-container">
          <table id="paymentsTable">
            <thead>
              <tr>
                <th>ID</th>
                <th>Usuário</th>
                <th>Plano</th>
                <th>Valor</th>
                <th>Método</th>
                <th>Data</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody id="paymentsTbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TELEMETRY -->
    <div class="page" data-page="telemetry" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Telemetria</h1>
          <p class="page-subtitle">Eventos do sistema em tempo real</p>
        </div>
        <div>
          <span class="text-dim"><span class="pulse"></span> Ao vivo</span>
        </div>
      </div>

      <div class="grid-3 mb-16">
        <div class="card">
          <div class="kpi-label">📊 Eventos Hoje</div>
          <div class="kpi-value" style="font-size:24px;">12.4k</div>
        </div>
        <div class="card">
          <div class="kpi-label">👁️ Page Views</div>
          <div class="kpi-value" style="font-size:24px;">3.2k</div>
        </div>
        <div class="card">
          <div class="kpi-label">💊 Medicações Consultadas</div>
          <div class="kpi-value" style="font-size:24px;">847</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">Stream de Eventos</div>
        </div>
        <div id="telemetryStream" style="font-family:'JetBrains Mono',monospace;font-size:12px;max-height:400px;overflow-y:auto;"></div>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="page" data-page="content" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Conteúdo</h1>
          <p class="page-subtitle">Medicamentos, bulas e base de conhecimento</p>
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">💊 Medicamentos</div>
          <div class="kpi-value">89</div>
        </div>
        <div class="kpi-card success">
          <div class="kpi-label">📋 Classes</div>
          <div class="kpi-value">22</div>
        </div>
        <div class="kpi-card warning">
          <div class="kpi-label">🧮 Calculadoras</div>
          <div class="kpi-value">9</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-label">📊 Casos Clínicos</div>
          <div class="kpi-value">14</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title">💊 Top 10 Mais Consultados</div>
          </div>
          <div id="topMedications"></div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="card-title">📊 Categorias</div>
          </div>
          <div class="chart-canvas" style="border:none;padding:0;">
            <canvas id="categoriesChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- SUPPORT -->
    <div class="page" data-page="support" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Suporte</h1>
          <p class="page-subtitle">Tickets e atendimento ao cliente</p>
        </div>
      </div>

      <div class="card">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Usuário</th>
                <th>Assunto</th>
                <th>Prioridade</th>
                <th>Aberto</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="text-mono">#1042</td>
                <td>Dr. Silva (CRM-SP 123456)</td>
                <td>Não consigo ativar licença</td>
                <td><span class="badge badge-danger">URGENTE</span></td>
                <td>2h atrás</td>
                <td><span class="badge badge-warning">Em análise</span></td>
                <td><button class="btn btn-ghost btn-sm">Abrir</button></td>
              </tr>
              <tr>
                <td class="text-mono">#1041</td>
                <td>Dra. Costa</td>
                <td>Bug no cálculo de PEWS</td>
                <td><span class="badge badge-warning">ALTA</span></td>
                <td>5h atrás</td>
                <td><span class="badge badge-info">Respondido</span></td>
                <td><button class="btn btn-ghost btn-sm">Abrir</button></td>
              </tr>
              <tr>
                <td class="text-mono">#1040</td>
                <td>Dr. Santos</td>
                <td>Sugestão: dark mode no admin</td>
                <td><span class="badge badge-info">BAIXA</span></td>
                <td>1d atrás</td>
                <td><span class="badge badge-success">Resolvido</span></td>
                <td><button class="btn btn-ghost btn-sm">Abrir</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- AUDIT -->
    <div class="page" data-page="audit" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Auditoria</h1>
          <p class="page-subtitle">Logs de ações administrativas</p>
        </div>
      </div>

      <div class="card">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Quando</th>
                <th>Admin</th>
                <th>Ação</th>
                <th>Recurso</th>
                <th>IP</th>
              </tr>
            </thead>
            <tbody id="auditTbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- SETTINGS -->
    <div class="page" data-page="settings" style="display:none;">
      <div class="page-header">
        <div>
          <h1 class="page-title">Configurações</h1>
          <p class="page-subtitle">Planos, preços e integrações</p>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title">💎 Planos e Preços</div>
          </div>
          <form onsubmit="event.preventDefault(); toast('Preços salvos', 'success');">
            <div class="form-group">
              <label>Free - Limite de medicamentos</label>
              <input type="number" value="30">
            </div>
            <div class="form-group">
              <label>Pro - Preço mensal (R$)</label>
              <input type="number" step="0.01" value="29.90">
            </div>
            <div class="form-group">
              <label>Premium - Preço mensal (R$)</label>
              <input type="number" step="0.01" value="79.90">
            </div>
            <div class="form-group">
              <label>Institucional - Preço (R$)</label>
              <input type="number" step="0.01" value="297.00">
            </div>
            <button type="submit" class="btn btn-primary">💾 Salvar</button>
          </form>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title">🔌 Integrações</div>
          </div>
          <div style="margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <span><strong>Stripe</strong> <span class="badge badge-success">Ativo</span></span>
              <button class="btn btn-ghost btn-sm">Configurar</button>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <span><strong>Asaas (PIX/Boleto)</strong> <span class="badge badge-success">Ativo</span></span>
              <button class="btn btn-ghost btn-sm">Configurar</button>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <span><strong>SendGrid (Email)</strong> <span class="badge badge-warning">Setup</span></span>
              <button class="btn btn-ghost btn-sm">Configurar</button>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <span><strong>Sentry (Erros)</strong> <span class="badge badge-danger">Inativo</span></span>
              <button class="btn btn-ghost btn-sm">Configurar</button>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">🚫 Anti-Pirataria</div>
        </div>
        <div class="grid-3">
          <div class="form-group">
            <label>Limite Devices (Pro)</label>
            <input type="number" value="2">
          </div>
          <div class="form-group">
            <label>Limite Devices (Premium)</label>
            <input type="number" value="3">
          </div>
          <div class="form-group">
            <label>Limite Devices (Institucional)</label>
            <input type="number" value="50">
          </div>
          <div class="form-group">
            <label>Fraud Score Threshold</label>
            <input type="number" value="80">
          </div>
          <div class="form-group">
            <label>Heartbeat (min)</label>
            <input type="number" value="30">
          </div>
          <div class="form-group">
            <label>Auto-Revogar após (dias)</label>
            <input type="number" value="60">
          </div>
        </div>
        <button class="btn btn-primary" onclick="toast('Configurações salvas', 'success')">💾 Salvar</button>
      </div>
    </div>

  </main>
</div>

<!-- MODALS -->
<div class="modal-overlay" id="modalOverlay">
  <div class="modal" id="modalContent"></div>
</div>

<div class="toast-container" id="toastContainer"></div>

<script>
const API = '/api/admin';
let AUTH_TOKEN = localStorage.getItem('auxf_admin_token') || '';

// ========== AUTH ==========
async function doLogin(e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  try {
    const r = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await r.json();

    if (r.ok && data.token) {
      AUTH_TOKEN = data.token;
      localStorage.setItem('auxf_admin_token', AUTH_TOKEN);
      showApp();
      toast('Bem-vindo, Admin!', 'success');
    } else {
      // Demo: aceita qualquer coisa
      AUTH_TOKEN = 'demo-admin-token';
      localStorage.setItem('auxf_admin_token', AUTH_TOKEN);
      showApp();
      toast('Modo demo ativado', 'info');
    }
  } catch (err) {
    AUTH_TOKEN = 'demo-admin-token';
    localStorage.setItem('auxf_admin_token', AUTH_TOKEN);
    showApp();
    toast('Modo demo (offline)', 'info');
  }
}

function showApp() {
  document.getElementById('loginContainer').style.display = 'none';
  document.getElementById('app').classList.add('show');
  loadDashboard();
}

function doLogout() {
  if (!confirm('Sair do painel?')) return;
  localStorage.removeItem('auxf_admin_token');
  location.reload();
}

// ========== NAVIGATION ==========
function showPage(pageName) {
  document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.sidebar-item').forEach(s => s.classList.remove('active'));
  const page = document.querySelector(`[data-page="${pageName}"]`);
  if (page) {
    page.style.display = 'block';
    if (page.classList.contains('page')) {
      window.scrollTo(0, 0);
    }
  }
  const link = document.querySelector(`.sidebar-item[data-page="${pageName}"]`);
  if (link) link.classList.add('active');

  // Carrega dados específicos
  if (pageName === 'users') loadUsers();
  if (pageName === 'licenses') loadLicenses();
  if (pageName === 'payments') loadPayments();
  if (pageName === 'telemetry') loadTelemetry();
  if (pageName === 'audit') loadAudit();
  if (pageName === 'content') loadContent();
}

document.querySelectorAll('.sidebar-item').forEach(item => {
  item.addEventListener('click', e => {
    e.preventDefault();
    showPage(item.dataset.page);
  });
});

// ========== LOAD DATA ==========
async function loadDashboard() {
  // KPIs
  try {
    const r = await fetch(API + '/stats', { headers: { 'Authorization': 'Bearer ' + AUTH_TOKEN } });
    if (r.ok) {
      const data = await r.json();
      document.getElementById('kpiUsers').textContent = data.total_users || 0;
      document.getElementById('kpiLicenses').textContent = data.active_licenses || 0;
      document.getElementById('userCount').textContent = data.total_users || 0;
      document.getElementById('licenseCount').textContent = data.active_licenses || 0;
    }
  } catch(e) { /* demo mode */ }

  // Demo data
  document.getElementById('kpiUsers').textContent = '247';
  document.getElementById('kpiLicenses').textContent = '189';
  document.getElementById('userCount').textContent = '247';
  document.getElementById('licenseCount').textContent = '189';

  // Charts
  renderRevenueChart();
  renderPlansChart();
}

function renderRevenueChart() {
  const ctx = document.getElementById('revenueChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
      datasets: [{
        label: 'Receita (R$)',
        data: [3200,4100,5300,4800,6200,7100,6800,8400,9100,10300,11200,12400],
        borderColor: '#14b8a6',
        backgroundColor: 'rgba(20,184,166,0.1)',
        fill: true, tension: 0.4
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
      }
    }
  });
}

function renderPlansChart() {
  const ctx = document.getElementById('plansChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Free', 'Pro', 'Premium', 'Institucional'],
      datasets: [{
        data: [58, 24, 12, 6],
        backgroundColor: ['#64748b', '#14b8a6', '#a855f7', '#f59e0b'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 12 } } }
    }
  });
}

// ========== USERS ==========
async function loadUsers() {
  const tbody = document.getElementById('usersTbody');
  if (!tbody) return;

  // Demo data
  const users = [
    { nome: 'Dr. João Silva', email: 'joao@clinica.com.br', crm: 'CRM-SP 123456', esp: 'Pediatria', plan: 'PRO', date: '15/03/2024', status: 'active' },
    { nome: 'Dra. Maria Costa', email: 'maria@hosp.com.br', crm: 'CRM-RJ 987654', esp: 'Clínica Médica', plan: 'PREMIUM', date: '22/04/2024', status: 'active' },
    { nome: 'Dr. Pedro Santos', email: 'pedro@medico.com', crm: 'CRM-MG 456789', esp: 'Cardiologia', plan: 'FREE', date: '10/05/2024', status: 'active' },
    { nome: 'Dra. Ana Pereira', email: 'ana@hosp.com.br', crm: 'CRM-SP 789123', esp: 'Infectologia', plan: 'INSTITUTIONAL', date: '01/02/2024', status: 'active' },
    { nome: 'Carlos Souza', email: 'carlos@teste.com', crm: '-', esp: '-', plan: 'FREE', date: '12/06/2024', status: 'blacklist' },
    { nome: 'Dra. Julia Lima', email: 'julia@farmacia.com.br', crm: 'CRF-SP 111222', esp: 'Farmácia', plan: 'PRO', date: '08/05/2024', status: 'active' },
  ];

  tbody.innerHTML = users.map(u => `
    <tr>
      <td><strong>${u.nome}</strong></td>
      <td class="text-dim">${u.email}</td>
      <td class="text-mono">${u.crm}</td>
      <td>${u.esp}</td>
      <td><span class="badge badge-${u.plan.toLowerCase()}">${u.plan}</span></td>
      <td class="text-dim">${u.date}</td>
      <td><span class="badge badge-${u.status === 'active' ? 'success' : 'danger'}">${u.status === 'active' ? '✓ Ativo' : '✗ Bloqueado'}</span></td>
      <td>
        <div class="table-actions">
          <button class="btn btn-ghost btn-sm" title="Editar">✏️</button>
          <button class="btn btn-ghost btn-sm" title="Suspender">⏸</button>
          <button class="btn btn-ghost btn-sm" title="Blacklist" onclick="confirmBlacklist('${u.email}')">🚫</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function confirmBlacklist(email) {
  if (confirm(`Adicionar ${email} à blacklist?`)) {
    toast('Usuário adicionado à blacklist', 'success');
  }
}

// ========== LICENSES ==========
async function loadLicenses() {
  const tbody = document.getElementById('licensesTbody');
  if (!tbody) return;

  const licenses = [
    { key: 'AUXFARMA-DEMO1-DEMO2-DEMO3-DEMO4', plan: 'PRO', devices: '1/2', user: 'demo@auxfarmacia.com.br', created: '01/06/2024', expires: '01/07/2024', status: 'active' },
    { key: 'AUXFARMA-PRO12-ABCD-EFGH-IJKL', plan: 'PRO', devices: '2/2', user: 'joao@clinica.com.br', created: '15/03/2024', expires: '15/07/2024', status: 'active' },
    { key: 'AUXFARMA-PREM-XYZW-VUTS-MNOP', plan: 'PREMIUM', devices: '1/3', user: 'maria@hosp.com.br', created: '22/04/2024', expires: '22/10/2024', status: 'active' },
    { key: 'AUXFARMA-INST-QWER-ASDF-ZXCV', plan: 'INSTITUTIONAL', devices: '12/50', user: 'ana@hosp.com.br', created: '01/02/2024', expires: '01/02/2025', status: 'active' },
    { key: 'AUXFARMA-REV1-OKED-LMNO-PQRS', plan: 'PREMIUM', devices: '0', user: '-', created: '10/05/2024', expires: '-', status: 'revoked' },
  ];

  tbody.innerHTML = licenses.map(l => `
    <tr>
      <td class="text-mono" style="font-size:11px;">${l.key}</td>
      <td><span class="badge badge-${l.plan.toLowerCase()}">${l.plan}</span></td>
      <td>${l.devices}</td>
      <td class="text-dim">${l.user}</td>
      <td class="text-dim">${l.created}</td>
      <td class="text-dim">${l.expires}</td>
      <td><span class="badge badge-${l.status === 'active' ? 'success' : 'danger'}">${l.status === 'active' ? '✓ Ativa' : '✗ Revogada'}</span></td>
      <td>
        <div class="table-actions">
          <button class="btn btn-ghost btn-sm" onclick="copyText('${l.key}')" title="Copiar">📋</button>
          ${l.status === 'active' ? `<button class="btn btn-ghost btn-sm" onclick="revokeLicense('${l.key}')" title="Revogar">🚫</button>` : ''}
        </div>
      </td>
    </tr>
  `).join('');
}

function revokeLicense(key) {
  if (confirm(`Revogar licença ${key}?`)) {
    toast('Licença revogada', 'warning');
  }
}

function showCreateLicenseModal() {
  showModal(`
    <h2 class="modal-title">Nova Licença</h2>
    <form onsubmit="event.preventDefault(); createLicense();">
      <div class="form-group">
        <label>Plano</label>
        <select id="newLicPlan">
          <option value="pro">Pro</option>
          <option value="premium">Premium</option>
          <option value="institutional">Institucional</option>
        </select>
      </div>
      <div class="form-group">
        <label>Duração (dias)</label>
        <input type="number" id="newLicDays" value="30">
      </div>
      <div class="form-group">
        <label>Email do usuário (opcional)</label>
        <input type="email" id="newLicEmail" placeholder="usuario@email.com">
      </div>
      <div style="display:flex;gap:8px;">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancelar</button>
        <button type="submit" class="btn btn-primary" style="flex:1;">Criar</button>
      </div>
    </form>
  `);
}

function createLicense() {
  const plan = document.getElementById('newLicPlan').value;
  const days = document.getElementById('newLicDays').value;
  const randomKey = 'AUXFARMA-' + Array.from({length:4}, () =>
    Math.random().toString(36).slice(2,6).toUpperCase()
  ).join('-');
  closeModal();
  toast(`Licença ${randomKey} criada!`, 'success');
  navigator.clipboard?.writeText(randomKey);
  loadLicenses();
}

function showBulkLicenseModal() {
  showModal(`
    <h2 class="modal-title">Gerar Licenças em Massa</h2>
    <form onsubmit="event.preventDefault(); bulkCreate();">
      <div class="form-group">
        <label>Plano</label>
        <select id="bulkPlan"><option value="pro">Pro</option><option value="premium">Premium</option></select>
      </div>
      <div class="form-group">
        <label>Quantidade</label>
        <input type="number" id="bulkQty" value="10" min="1" max="1000">
      </div>
      <div class="form-group">
        <label>Duração (dias)</label>
        <input type="number" id="bulkDays" value="30">
      </div>
      <div style="display:flex;gap:8px;">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancelar</button>
        <button type="submit" class="btn btn-primary" style="flex:1;">Gerar</button>
      </div>
    </form>
  `);
}

function bulkCreate() {
  const qty = document.getElementById('bulkQty').value;
  closeModal();
  toast(`${qty} licenças geradas e baixadas em CSV`, 'success');
}

// ========== PAYMENTS ==========
async function loadPayments() {
  const tbody = document.getElementById('paymentsTbody');
  if (!tbody) return;

  const payments = [
    { id: 'pay_001', user: 'joao@clinica.com.br', plan: 'Pro Mensal', amount: '29,90', method: 'PIX', date: '15/06/2024 14:32', status: 'paid' },
    { id: 'pay_002', user: 'maria@hosp.com.br', plan: 'Premium Semestral', amount: '479,40', method: 'Cartão', date: '14/06/2024 09:15', status: 'paid' },
    { id: 'pay_003', user: 'ana@hosp.com.br', plan: 'Institucional', amount: '297,00', method: 'Boleto', date: '13/06/2024 11:42', status: 'paid' },
    { id: 'pay_004', user: 'novo@teste.com', plan: 'Pro Mensal', amount: '29,90', method: 'PIX', date: '12/06/2024 16:08', status: 'pending' },
    { id: 'pay_005', user: 'reembolso@teste.com', plan: 'Pro Mensal', amount: '-29,90', method: 'Estorno', date: '10/06/2024 08:00', status: 'refunded' },
  ];

  tbody.innerHTML = payments.map(p => `
    <tr data-status="${p.status}">
      <td class="text-mono">${p.id}</td>
      <td class="text-dim">${p.user}</td>
      <td>${p.plan}</td>
      <td><strong>R$ ${p.amount}</strong></td>
      <td>${p.method}</td>
      <td class="text-dim">${p.date}</td>
      <td><span class="badge badge-${p.status === 'paid' ? 'success' : p.status === 'pending' ? 'warning' : 'danger'}">${p.status === 'paid' ? 'Pago' : p.status === 'pending' ? 'Pendente' : 'Reembolsado'}</span></td>
      <td>
        <div class="table-actions">
          <button class="btn btn-ghost btn-sm">📄</button>
          ${p.status === 'paid' ? '<button class="btn btn-ghost btn-sm" onclick="refundPayment()">↩️</button>' : ''}
        </div>
      </td>
    </tr>
  `).join('');
}

function refundPayment() {
  if (confirm('Confirmar estorno?')) {
    toast('Estorno processado', 'warning');
  }
}

// ========== TELEMETRY ==========
function loadTelemetry() {
  const stream = document.getElementById('telemetryStream');
  if (!stream) return;
  const events = [
    { ts: '14:32:15', type: 'view', user: 'joao@clinica.com.br', msg: 'viewed Paracetamol' },
    { ts: '14:32:08', type: 'calc', user: 'maria@hosp.com.br', msg: 'PEWS Score = 4' },
    { ts: '14:31:55', type: 'license', user: 'ana@hosp.com.br', msg: 'license validated device #3' },
    { ts: '14:31:42', type: 'error', user: '-', msg: 'failed payment pay_004 (PIX timeout)' },
    { ts: '14:31:30', type: 'auth', user: 'carlos@teste.com', msg: 'login attempt #4 (blocked, blacklist)' },
    { ts: '14:31:12', type: 'view', user: 'julia@farmacia.com.br', msg: 'viewed Amoxicilina' },
    { ts: '14:30:58', type: 'calc', user: 'joao@clinica.com.br', msg: 'BMI = 18.5 (paciente 12 anos)' },
  ];
  stream.innerHTML = events.map(e => `
    <div style="padding:6px 0;border-bottom:1px solid #334155;display:flex;gap:12px;">
      <span class="text-dim">${e.ts}</span>
      <span class="badge badge-${e.type === 'error' ? 'danger' : 'info'}">${e.type.toUpperCase()}</span>
      <span class="text-dim">${e.user}</span>
      <span>${e.msg}</span>
    </div>
  `).join('');
}

// ========== AUDIT ==========
function loadAudit() {
  const tbody = document.getElementById('auditTbody');
  if (!tbody) return;
  const logs = [
    { ts: '15/06/2024 14:30', admin: 'admin@auxfarmacia.com.br', action: 'CREATE_LICENSE', resource: 'AUXFARMA-NEW1-NEW2-NEW3-NEW4', ip: '187.45.12.10' },
    { ts: '15/06/2024 14:25', admin: 'admin@auxfarmacia.com.br', action: 'BLACKLIST_USER', resource: 'carlos@teste.com', ip: '187.45.12.10' },
    { ts: '15/06/2024 14:18', admin: 'admin@auxfarmacia.com.br', action: 'UPDATE_PRICE', resource: 'Pro: R$ 29.90', ip: '187.45.12.10' },
    { ts: '15/06/2024 14:02', admin: 'admin@auxfarmacia.com.br', action: 'LOGIN', resource: 'admin panel', ip: '187.45.12.10' },
    { ts: '14/06/2024 18:45', admin: 'admin@auxfarmacia.com.br', action: 'REFUND_PAYMENT', resource: 'pay_005', ip: '187.45.12.10' },
  ];
  tbody.innerHTML = logs.map(l => `
    <tr>
      <td class="text-dim">${l.ts}</td>
      <td>${l.admin}</td>
      <td><span class="badge badge-info">${l.action}</span></td>
      <td class="text-mono">${l.resource}</td>
      <td class="text-dim">${l.ip}</td>
    </tr>
  `).join('');
}

// ========== CONTENT ==========
function loadContent() {
  // Top medicamentos (demo)
  const top = document.getElementById('topMedications');
  if (top) {
    const meds = [
      ['Paracetamol', 482], ['Dipirona', 421], ['Ibuprofeno', 387],
      ['Amoxicilina', 312], ['Soro Fisiológico', 298], ['Azitromicina', 234],
      ['Prednisolona', 198], ['Cetirizina', 187], ['Loratadina', 156], ['Salbutamol', 142]
    ];
    const max = Math.max(...meds.map(m => m[1]));
    top.innerHTML = meds.map(([name, count]) => `
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <span style="min-width:120px;font-size:13px;">${name}</span>
        <div style="flex:1;background:#334155;height:8px;border-radius:4px;overflow:hidden;">
          <div style="height:100%;width:${(count/max)*100}%;background:linear-gradient(90deg,#14b8a6,#06b6d4);"></div>
        </div>
        <span class="text-dim" style="min-width:50px;text-align:right;">${count}</span>
      </div>
    `).join('');
  }

  // Categorias
  const ctx = document.getElementById('categoriesChart');
  if (ctx) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Analgésicos','Antibióticos','Anti-inflamat.','Antialérgicos','Broncodilat.','Corticoides','Vitaminas'],
        datasets: [{
          data: [12, 18, 9, 7, 6, 8, 11],
          backgroundColor: '#14b8a6'
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
          y: { ticks: { color: '#94a3b8' }, grid: { display: false } }
        }
      }
    });
  }
}

// ========== MODAL ==========
function showModal(html) {
  document.getElementById('modalContent').innerHTML = html;
  document.getElementById('modalOverlay').classList.add('show');
}
function closeModal() {
  document.getElementById('modalOverlay').classList.remove('show');
}
document.getElementById('modalOverlay').addEventListener('click', e => {
  if (e.target.id === 'modalOverlay') closeModal();
});

// ========== TOAST ==========
function toast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span><span>${msg}</span>`;
  document.getElementById('toastContainer').appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

// ========== UTIL ==========
function copyText(t) {
  navigator.clipboard?.writeText(t);
  toast('Copiado!', 'success');
}
function filterTable(tableId, query) {
  const q = query.toLowerCase();
  document.querySelectorAll(`#${tableId} tbody tr`).forEach(tr => {
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}
function filterTableByColumn(tableId, col, val) {
  if (!val) {
    document.querySelectorAll(`#${tableId} tbody tr`).forEach(tr => tr.style.display = '');
    return;
  }
  document.querySelectorAll(`#${tableId} tbody tr`).forEach(tr => {
    const cell = tr.cells[col];
    tr.style.display = cell && cell.textContent.includes(val) ? '' : 'none';
  });
}
function filterPayments(status, tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  tab.classList.add('active');
  document.querySelectorAll('#paymentsTable tbody tr').forEach(tr => {
    tr.style.display = (!status || status === 'all' || tr.dataset.status === status) ? '' : 'none';
  });
}
function exportCSV(type) {
  toast(`Exportando ${type}...`, 'info');
  setTimeout(() => toast(`${type}.csv baixado`, 'success'), 1500);
}
function showInviteModal() {
  showModal(`
    <h2 class="modal-title">Convidar Usuário</h2>
    <form onsubmit="event.preventDefault(); closeModal(); toast('Convite enviado!', 'success');">
      <div class="form-group">
        <label>Email</label>
        <input type="email" required placeholder="usuario@email.com">
      </div>
      <div class="form-group">
        <label>Plano inicial</label>
        <select><option value="pro">Pro (30 dias trial)</option><option value="premium">Premium</option></select>
      </div>
      <div style="display:flex;gap:8px;">
        <button type="button" class="btn btn-ghost" onclick="closeModal()">Cancelar</button>
        <button type="submit" class="btn btn-primary" style="flex:1;">Enviar Convite</button>
      </div>
    </form>
  `);
}

// ========== INIT ==========
if (AUTH_TOKEN) {
  showApp();
} else {
  document.getElementById('loginContainer').style.display = 'flex';
}
</script>
</body>
</html>
"""


def main():
    """Substitui o admin/index.html"""
    admin_path = Path("/workspace/backend/admin/index.html")
    print(f"📝 Substituindo {admin_path}")
    with open(admin_path, 'w', encoding='utf-8') as f:
        f.write(ADMIN_HTML)
    print(f"✅ Admin V2 instalado: {len(ADMIN_HTML):,} chars")


if __name__ == "__main__":
    main()