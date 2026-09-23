import json

def run_generate():
    with open('data.json', encoding='utf-8') as f:
        d = json.load(f)

    summary = d['summary']
    products = d['products']
    clients = d['clients']
    cities = d['cities']
    clients_lookup = d.get('clients_lookup', {})

    html_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>BUFFER · Painel Consolidado de Vendas | Light Report</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <style>
    /* ---- KIT: Light Report – tokens padronizados ---- */
    :root {{
      --bg: #f7f8fa;
      --plane: #ffffff;
      --plane-2: #f1f4f8;
      --stroke: #e2e8f0;
      --ink: #0f172a;
      --ink-2: #475569;
      --muted: #5f6b7a;
      --acc: #2563eb;
      --acc-2: #0369a1;
      --good: #15803d;
      --bad: #dc2626;
      --warn: #b45309;
      --good-bg: rgba(22, 163, 74, 0.08);
      --bad-bg: rgba(220, 38, 38, 0.08);
      --warn-bg: rgba(217, 119, 6, 0.1);
      --track: #e2e8f0;
      --grid: #eef2f7;
      --radius: 8px;
      --bw: 1px;
      --shadow: 0 1px 3px rgba(15, 23, 42, 0.04), 0 10px 24px -10px rgba(15, 23, 42, 0.07);
      --font: 'IBM Plex Sans';
      --display: 'IBM Plex Sans';
      --mono: 'IBM Plex Mono';
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background: var(--bg);
      color: var(--ink);
      font-family: var(--font), system-ui, -apple-system, sans-serif;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
      padding: 32px 24px;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 22px;
    }}

    /* Cabeçalho */
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .header-title h1 {{
      font-family: var(--display), sans-serif;
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.4px;
      color: var(--ink);
    }}

    .header-title p {{
      font-size: 13px;
      color: var(--muted);
      margin-top: 4px;
    }}

    .pill-session {{
      background: var(--plane);
      border: var(--bw) solid var(--stroke);
      padding: 8px 16px;
      border-radius: var(--radius);
      font-size: 12.5px;
      font-weight: 600;
      color: var(--ink-2);
      box-shadow: var(--shadow);
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}

    .pill-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--good);
      box-shadow: 0 0 6px rgba(21, 128, 61, 0.35);
    }}

    /* Botão Sincronizar Google Drive */
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .btn-sync {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      background: var(--plane);
      border: var(--bw) solid var(--stroke);
      color: var(--ink-2);
      padding: 8px 14px;
      border-radius: var(--radius);
      font-size: 12.5px;
      font-weight: 600;
      font-family: var(--font), sans-serif;
      cursor: pointer;
      box-shadow: var(--shadow);
      transition: all 0.15s ease;
    }}

    .btn-sync:hover:not(:disabled) {{
      background: var(--plane-2);
      color: var(--acc);
      border-color: rgba(37, 99, 235, 0.3);
    }}

    .btn-sync:disabled {{
      opacity: 0.65;
      cursor: not-allowed;
    }}

    .btn-sync.syncing .sync-icon {{
      animation: spin 1s linear infinite;
    }}

    @keyframes spin {{
      100% {{ transform: rotate(360deg); }}
    }}

    /* Toast Notification */
    .sync-toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--ink);
      color: #ffffff;
      padding: 12px 18px;
      border-radius: var(--radius);
      font-size: 13px;
      font-weight: 600;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.25);
      z-index: 9999;
      display: none;
      animation: slideUp 0.25s ease-out;
      max-width: 420px;
      line-height: 1.4;
    }}

    .sync-toast.toast-success {{
      background: #15803d;
    }}

    .sync-toast.toast-error {{
      background: #b91c1c;
    }}

    @keyframes slideUp {{
      from {{ transform: translateY(20px); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}

    /* Navegação por Abas */
    .nav-tabs-wrapper {{
      display: flex;
      justify-content: flex-start;
      margin-top: -6px;
    }}

    .nav-tabs {{
      display: inline-flex;
      background: var(--plane-2);
      border: var(--bw) solid var(--stroke);
      padding: 4px;
      border-radius: var(--radius);
      gap: 4px;
    }}

    .nav-tab {{
      display: inline-flex;
      align-items: center;
      padding: 8px 20px;
      border-radius: 6px;
      border: none;
      background: transparent;
      font-family: var(--font), sans-serif;
      font-size: 13px;
      font-weight: 600;
      color: var(--muted);
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .nav-tab:hover {{
      color: var(--ink);
    }}

    .nav-tab.active {{
      background: var(--plane);
      color: var(--acc);
      font-weight: 700;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }}

    /* Card Base */
    .glass-card {{
      background: var(--plane);
      border: var(--bw) solid var(--stroke);
      border-radius: var(--radius);
      padding: 24px;
      box-shadow: var(--shadow);
    }}

    .card-head {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 18px;
      gap: 14px;
    }}

    .card-head h3 {{
      font-size: 14px;
      font-weight: 700;
      color: var(--ink);
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    .card-head p {{
      font-size: 12px;
      color: var(--muted);
      margin-top: 3px;
    }}

    .meta-badge {{
      background: var(--plane-2);
      border: var(--bw) solid var(--stroke);
      color: var(--acc);
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: var(--radius);
      text-transform: uppercase;
      letter-spacing: 0.4px;
      white-space: nowrap;
    }}

    /* 1. Hero Block */
    .hero-card {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .hero-main {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .hero-label {{
      font-size: 12px;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }}

    .hero-number {{
      font-size: 46px;
      font-weight: 800;
      color: var(--ink);
      line-height: 1.1;
      letter-spacing: -1.2px;
      font-variant-numeric: tabular-nums;
      font-family: var(--display), sans-serif;
    }}

    .hero-number span {{
      font-size: 24px;
      font-weight: 700;
      color: var(--acc);
      margin-left: 6px;
      letter-spacing: normal;
    }}

    .badge-delta {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: var(--good-bg);
      border: var(--bw) solid rgba(21, 128, 61, 0.2);
      padding: 5px 12px;
      border-radius: var(--radius);
      font-size: 12px;
      font-weight: 700;
      color: var(--good);
      margin-top: 4px;
      width: fit-content;
    }}

    .badge-delta span {{
      font-weight: 500;
      color: var(--ink-2);
    }}

    /* 2. 6 KPIs Grid */
    .kpis-row {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 16px;
    }}

    .kpis-row-5 {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 16px;
    }}

    .kpi-item {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .kpi-title {{
      font-size: 11px;
      font-weight: 700;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .kpi-value {{
      font-size: 24px;
      font-weight: 800;
      color: var(--ink);
      font-variant-numeric: tabular-nums;
      font-family: var(--mono), monospace;
      margin: 2px 0;
    }}

    .kpi-delta {{
      font-size: 11.5px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }}

    .text-green {{ color: var(--good); }}
    .text-amber {{ color: var(--warn); }}
    .text-coral {{ color: var(--bad); }}
    .text-blue {{ color: var(--acc); }}
    .text-indigo {{ color: #4338ca; }}

    /* 3. Tabelas Estilizadas com Espaço Garantido */
    .table-container {{
      width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      max-height: 440px;
      overflow-y: auto;
      border-radius: var(--radius);
      border: var(--bw) solid var(--stroke);
      background: var(--plane);
    }}

    .table-container::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .table-container::-webkit-scrollbar-track {{
      background: var(--bg);
    }}
    .table-container::-webkit-scrollbar-thumb {{
      background: #cbd5e1;
      border-radius: 4px;
    }}
    .table-container::-webkit-scrollbar-thumb:hover {{
      background: var(--muted);
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      text-align: left;
    }}

    .data-table th {{
      padding: 12px 14px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 2px solid var(--stroke);
      position: sticky;
      top: 0;
      background: var(--plane-2);
      z-index: 2;
      white-space: nowrap;
    }}

    .data-table td {{
      padding: 11px 14px;
      border-bottom: var(--bw) solid var(--stroke);
      color: var(--ink);
      vertical-align: middle;
      font-size: 12.5px;
    }}

    .data-table tr:hover td {{
      background: #f8fafc;
    }}

    .ranking-badge {{
      background: var(--plane-2);
      border: var(--bw) solid var(--stroke);
      color: var(--ink-2);
      padding: 3px 8px;
      border-radius: var(--radius);
      font-size: 11px;
      font-weight: 700;
      font-family: var(--mono), monospace;
      display: inline-block;
      text-align: center;
      min-width: 26px;
    }}

    .num-col {{
      text-align: right;
      font-variant-numeric: tabular-nums;
      font-family: var(--mono), monospace;
      font-size: 12.5px;
      white-space: nowrap;
    }}

    .text-acc {{
      color: var(--acc);
      font-weight: 700;
    }}

    .bar-bg {{
      width: 100%;
      height: 5px;
      background: var(--track);
      border-radius: var(--radius);
      overflow: hidden;
      margin-top: 5px;
    }}

    .bar-fill {{
      height: 100%;
      background: var(--acc);
      border-radius: var(--radius);
    }}

    .table-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 2px solid var(--stroke);
      padding-top: 14px;
      margin-top: 12px;
      font-size: 12px;
      font-weight: 700;
      color: var(--ink);
      flex-wrap: wrap;
      gap: 10px;
    }}

    /* Grade de 2 Colunas para Produtos e Cidades */
    .two-col-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}

    /* Estilos da Aba "Análise por Cliente" */
    .search-box {{
      position: relative;
      width: 100%;
    }}

    .search-input-wrapper {{
      position: relative;
      display: flex;
      align-items: center;
    }}

    .search-input-wrapper input {{
      width: 100%;
      padding: 13px 44px 13px 42px;
      border-radius: var(--radius);
      border: 1.5px solid var(--stroke);
      background: var(--plane);
      font-size: 13.5px;
      font-family: var(--font), sans-serif;
      color: var(--ink);
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
      transition: border-color 0.15s, box-shadow 0.15s;
    }}

    .search-input-wrapper input:focus {{
      outline: none;
      border-color: var(--acc);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
    }}

    .search-icon {{
      position: absolute;
      left: 14px;
      color: var(--muted);
      pointer-events: none;
      display: flex;
      align-items: center;
    }}

    .btn-clear-search {{
      position: absolute;
      right: 12px;
      background: transparent;
      border: none;
      color: var(--muted);
      cursor: pointer;
      font-size: 14px;
      padding: 6px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .btn-clear-search:hover {{
      color: var(--ink);
      background: var(--plane-2);
    }}

    .search-dropdown {{
      position: absolute;
      top: calc(100% + 6px);
      left: 0;
      width: 100%;
      background: var(--plane);
      border: var(--bw) solid var(--stroke);
      border-radius: var(--radius);
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.12);
      max-height: 320px;
      overflow-y: auto;
      z-index: 100;
    }}

    .search-item {{
      padding: 11px 16px;
      border-bottom: var(--bw) solid var(--stroke);
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: background 0.15s;
      gap: 12px;
    }}

    .search-item:last-child {{
      border-bottom: none;
    }}

    .search-item:hover, .search-item.highlighted {{
      background: var(--plane-2);
    }}

    .search-item-main {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .search-item-nome {{
      font-weight: 700;
      font-size: 13px;
      color: var(--ink);
    }}

    .search-item-sub {{
      font-size: 11.5px;
      color: var(--muted);
    }}

    .search-item-badge {{
      background: var(--plane-2);
      border: var(--bw) solid var(--stroke);
      color: var(--acc);
      font-size: 11px;
      font-weight: 700;
      font-family: var(--mono), monospace;
      padding: 3px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }}

    .quick-chips {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 14px;
      font-size: 12px;
    }}

    .chip-btn {{
      background: var(--plane-2);
      border: var(--bw) solid var(--stroke);
      color: var(--ink-2);
      padding: 4px 10px;
      border-radius: 16px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .chip-btn:hover {{
      background: var(--plane);
      border-color: var(--acc);
      color: var(--acc);
    }}

    .empty-state-card {{
      text-align: center;
      padding: 48px 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }}

    .status-tag {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 10.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }}

    .status-atendido {{ background: var(--good-bg); color: var(--good); border: var(--bw) solid rgba(21, 128, 61, 0.2); }}
    .status-aguardando {{ background: var(--warn-bg); color: var(--warn); border: var(--bw) solid rgba(217, 119, 6, 0.25); }}
    .status-cancelado {{ background: var(--bad-bg); color: var(--bad); border: var(--bw) solid rgba(220, 38, 38, 0.2); }}

    /* Responsividade */
    @media (max-width: 1240px) {{
      .kpis-row {{ grid-template-columns: repeat(3, 1fr); }}
      .kpis-row-5 {{ grid-template-columns: repeat(3, 1fr); }}
      .two-col-grid {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 680px) {{
      body {{ padding: 18px 14px; }}
      .kpis-row {{ grid-template-columns: repeat(2, 1fr); }}
      .kpis-row-5 {{ grid-template-columns: repeat(2, 1fr); }}
      .hero-number {{ font-size: 36px; }}
    }}

    @media (max-width: 480px) {{
      .kpis-row {{ grid-template-columns: 1fr; }}
      .kpis-row-5 {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header>
      <div class="header-title">
        <h1>BUFFER · Painel Consolidado de Vendas</h1>
        <p>monitoramento integrado de faturamento, peso bruto (Kg) e capacidade de paletes | relatório real</p>
      </div>
      <div class="header-actions">
        <div class="pill-session">
          <span class="pill-dot"></span>
          <span id="session-tag">Data de Entrega: 24/09/2026</span>
        </div>
        <button type="button" id="btn-sync-drive" class="btn-sync" onclick="SPECS.syncDrive()" title="Puxar dados atualizados do Google Drive">
          <svg class="sync-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          <span id="sync-btn-text">Atualizar Dados</span>
        </button>
      </div>
    </header>

    <!-- Navegação das Abas -->
    <div class="nav-tabs-wrapper">
      <div class="nav-tabs">
        <button type="button" class="nav-tab active" id="tab-btn-geral" onclick="SPECS.switchTab('geral')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px;"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          Visão Geral
        </button>
        <button type="button" class="nav-tab" id="tab-btn-cliente" onclick="SPECS.switchTab('cliente')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          Análise por Cliente
        </button>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- ABA 1: VISÃO GERAL (MANTIDA 100% INTACTA)                     -->
    <!-- ============================================================ -->
    <div id="view-geral" class="tab-pane" style="display: flex; flex-direction: column; gap: 22px;">
      <!-- 1. HERO BLOCK -->
      <section class="glass-card hero-card">
        <div class="hero-main">
          <div class="hero-label">Volume Total Consolidado</div>
          <div class="hero-number" id="hero-val">0 <span>HL</span></div>
          <div class="badge-delta">
            <span id="hero-delta">▲ 100% ATENDIDO</span>
            <span id="hero-delta-sub">pedidos faturados e confirmados no buffer</span>
          </div>
        </div>
      </section>

      <!-- 2. 6 KPIS GRID -->
      <section class="kpis-row">
        <div class="glass-card kpi-item">
          <div class="kpi-title">Total de Entregas</div>
          <div class="kpi-value" id="kpi-entregas">0</div>
          <div class="kpi-delta text-green">
            <span id="kpi-entregas-delta">▲ {summary['total_pedidos']}</span>
            <span style="color:var(--muted);font-weight:400">pedidos únicos</span>
          </div>
        </div>

        <div class="glass-card kpi-item">
          <div class="kpi-title">Clientes Atendidos</div>
          <div class="kpi-value" id="kpi-clientes">0</div>
          <div class="kpi-delta text-blue">
            <span id="kpi-clientes-delta">▲ {summary['total_clientes']}</span>
            <span style="color:var(--muted);font-weight:400">pontos de venda</span>
          </div>
        </div>

        <div class="glass-card kpi-item">
          <div class="kpi-title">Cidades Atendidas</div>
          <div class="kpi-value" id="kpi-cidades">0</div>
          <div class="kpi-delta text-green">
            <span id="kpi-cidades-delta">▲ {summary['total_cidades']}</span>
            <span style="color:var(--muted);font-weight:400">municípios</span>
          </div>
        </div>

        <div class="glass-card kpi-item">
          <div class="kpi-title">Mix de Produtos</div>
          <div class="kpi-value" id="kpi-produtos">0</div>
          <div class="kpi-delta text-amber">
            <span id="kpi-produtos-delta">▲ {summary['total_produtos']}</span>
            <span style="color:var(--muted);font-weight:400">SKUs distintos</span>
          </div>
        </div>

        <div class="glass-card kpi-item">
          <div class="kpi-title">Peso Bruto Total</div>
          <div class="kpi-value" id="kpi-peso">0</div>
          <div class="kpi-delta text-indigo">
            <span id="kpi-peso-delta">▲ {summary['total_peso_ton']:,.1f} t</span>
            <span style="color:var(--muted);font-weight:400">{summary['total_peso_kg']:,.0f} kg</span>
          </div>
        </div>

        <div class="glass-card kpi-item">
          <div class="kpi-title">Carga em Paletes</div>
          <div class="kpi-value" id="kpi-pallets">0</div>
          <div class="kpi-delta text-green">
            <span id="kpi-pallets-delta">▲ {summary['total_pallets']:,.1f}</span>
            <span style="color:var(--muted);font-weight:400">pallets padrão</span>
          </div>
        </div>
      </section>

      <!-- 3. RANKING DE CLIENTES COM MAIORES PEDIDOS -->
      <section class="glass-card">
        <div class="card-head">
          <div>
            <h3>Ranking de Clientes com Maiores Pedidos</h3>
            <p>clientes líderes em volume faturado (HL), quantidade de pedidos, peso bruto e paletes</p>
          </div>
          <div class="meta-badge">{summary['total_clientes']} Clientes Atendidos</div>
        </div>

        <div class="table-container">
          <table class="data-table" style="min-width: 1040px;">
            <thead>
              <tr>
                <th style="width: 48px; text-align: center;">#</th>
                <th style="width: 75px; text-align: center;">Cód.</th>
                <th style="min-width: 250px;">Cliente (Nome Fantasia / Razão Social)</th>
                <th style="min-width: 120px;">Município</th>
                <th class="num-col" style="width: 85px;">Pedidos</th>
                <th class="num-col" style="width: 100px;">Qtd (Un./Cx)</th>
                <th class="num-col" style="width: 110px;">Peso (Kg)</th>
                <th class="num-col" style="width: 90px;">Paletes</th>
                <th class="num-col" style="width: 160px;">Volume Faturado</th>
              </tr>
            </thead>
            <tbody id="tbody-clientes">
              <!-- Injetado via SPECS -->
            </tbody>
          </table>
        </div>

        <div class="table-footer">
          <span style="color:var(--muted); text-transform:uppercase; font-size:11px;">Total Clientes Atendidos</span>
          <span id="footer-client-total">{summary['total_clientes']} clientes ({summary['total_pedidos']} pedidos · {summary['total_volume_hl']:,.2f} HL · {summary['total_peso_kg']:,.2f} kg · {summary['total_pallets']:,.2f} pallets)</span>
        </div>
      </section>

      <!-- 4. TABELAS DE RANKING DE PRODUTOS E CIDADES -->
      <div class="two-col-grid">
        <!-- Tabela Ranking Produtos -->
        <section class="glass-card">
          <div class="card-head">
            <div>
              <h3>Ranking de Produtos</h3>
              <p>itens faturados com detalhamento de peso bruto e paletes</p>
            </div>
            <div class="meta-badge">{summary['total_produtos']} SKUs</div>
          </div>

          <div class="table-container">
            <table class="data-table" style="min-width: 660px;">
              <thead>
                <tr>
                  <th style="width: 44px; text-align: center;">#</th>
                  <th style="min-width: 220px;">Produto</th>
                  <th class="num-col" style="width: 95px;">Quantidade</th>
                  <th class="num-col" style="width: 105px;">Peso (Kg)</th>
                  <th class="num-col" style="width: 85px;">Paletes</th>
                  <th class="num-col" style="width: 115px;">Volume (HL)</th>
                </tr>
              </thead>
              <tbody id="tbody-produtos">
                <!-- Injetado via SPECS -->
              </tbody>
            </table>
          </div>

          <div class="table-footer">
            <span style="color:var(--muted); text-transform:uppercase; font-size:11px;">Total Produtos</span>
            <span id="footer-prod-total">{summary['total_produtos']} SKUs ({summary['total_quantidade']:,} un. · {summary['total_volume_hl']:,.2f} HL · {summary['total_peso_kg']:,.2f} kg · {summary['total_pallets']:,.2f} pallets)</span>
          </div>
        </section>

        <!-- Tabela Ranking Cidades -->
        <section class="glass-card">
          <div class="card-head">
            <div>
              <h3>Ranking de Cidades</h3>
              <p>municípios com maior demanda em HL, peso e paletes</p>
            </div>
            <div class="meta-badge">{summary['total_cidades']} Cidades</div>
          </div>

          <div class="table-container">
            <table class="data-table" style="min-width: 660px;">
              <thead>
                <tr>
                  <th style="width: 44px; text-align: center;">#</th>
                  <th style="min-width: 150px;">Município</th>
                  <th class="num-col" style="width: 80px;">Entregas</th>
                  <th class="num-col" style="width: 90px;">Qtd (Un.)</th>
                  <th class="num-col" style="width: 105px;">Peso (Kg)</th>
                  <th class="num-col" style="width: 85px;">Paletes</th>
                  <th class="num-col" style="width: 115px;">Volume (HL)</th>
                </tr>
              </thead>
              <tbody id="tbody-cidades">
                <!-- Injetado via SPECS -->
              </tbody>
            </table>
          </div>

          <div class="table-footer">
            <span style="color:var(--muted); text-transform:uppercase; font-size:11px;">Total Cidades</span>
            <span id="footer-city-total">{summary['total_cidades']} cidades ({summary['total_pedidos']} entregas · {summary['total_volume_hl']:,.2f} HL · {summary['total_peso_kg']:,.2f} kg · {summary['total_pallets']:,.2f} pallets)</span>
          </div>
        </section>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- ABA 2: ANÁLISE POR CLIENTE (NOVA ADIÇÃO PURA)               -->
    <!-- ============================================================ -->
    <div id="view-cliente" class="tab-pane" style="display: none; flex-direction: column; gap: 22px;">
      <!-- Bloco de Pesquisa com Autocomplete -->
      <section class="glass-card">
        <div class="card-head">
          <div>
            <h3>Consulta e Detalhamento de Cliente</h3>
            <p>pesquise por código ou nome do cliente para analisar paletes, peso bruto, mix de produtos e pedidos</p>
          </div>
          <div class="meta-badge">{len(clients_lookup)} Clientes no Período</div>
        </div>

        <div class="search-box">
          <div class="search-input-wrapper">
            <span class="search-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            </span>
            <input type="text" id="client-search-input" placeholder="Digite o código ou nome do cliente (ex: 2743 ou TARCISIO)..." autocomplete="off" />
            <button type="button" class="btn-clear-search" id="btn-clear-search" onclick="SPECS.clearSearch()" style="display:none;" title="Limpar pesquisa">✕</button>
          </div>
          <div id="search-dropdown" class="search-dropdown" style="display:none;"></div>
        </div>

        <div class="quick-chips">
          <span style="color:var(--muted); font-weight:600;">Exemplos rápidos:</span>
          <button type="button" class="chip-btn" onclick="SPECS.selectClient(2743, DADOS)"><span style="font-family:var(--mono);">[2743]</span> LANC O TARCISIO AD</button>
          <button type="button" class="chip-btn" onclick="SPECS.selectClient(9025, DADOS)"><span style="font-family:var(--mono);">[9025]</span> S5 - COMERCIAL SUPER</button>
          <button type="button" class="chip-btn" onclick="SPECS.selectClient(24833, DADOS)"><span style="font-family:var(--mono);">[24833]</span> S5 - SUPER MAX FILIA</button>
          <button type="button" class="chip-btn" onclick="SPECS.selectClient(9878, DADOS)"><span style="font-family:var(--mono);">[9878]</span> MERCEARIA MULTIMARCA</button>
          <button type="button" class="chip-btn" onclick="SPECS.selectClient(9693, DADOS)"><span style="font-family:var(--mono);">[9693]</span> DEPOSITO ZERO GRAU</button>
        </div>
      </section>

      <!-- Estado Inicial Vazio -->
      <section class="glass-card empty-state-card" id="client-empty-state">
        <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.6;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <div style="font-size:15px; font-weight:700; color:var(--ink);">Nenhum cliente selecionado</div>
        <p style="font-size:12.5px; color:var(--muted); max-width:480px; line-height:1.5;">Digite o nome ou código de um cliente na busca acima ou clique em um dos exemplos rápidos para visualizar os totais de paletes, peso, produtos comprados e pedidos individuais.</p>
      </section>

      <!-- Detalhes do Cliente Selecionado -->
      <div id="client-detail-container" style="display: none; flex-direction: column; gap: 22px;">
        <!-- Card de Identificação do Cliente -->
        <section class="glass-card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
          <div>
            <div style="display:flex; align-items:center; gap:10px;">
              <h2 id="client-nome" style="font-size:19px; font-weight:800; color:var(--ink);">Cliente</h2>
              <span id="client-cod-badge" class="meta-badge" style="font-family:var(--mono);">Cód: 0</span>
            </div>
            <div id="client-sub" style="font-size:12.5px; color:var(--muted); margin-top:4px;">Razão Social · Município</div>
          </div>
          <div style="display:flex; gap:10px; align-items:center;">
            <div class="pill-session" style="box-shadow:none;">
              <span style="font-size:11.5px; color:var(--muted); font-weight:600; text-transform:uppercase;">Município:</span>
              <span id="client-cidade" style="font-size:12px; font-weight:700; color:var(--ink);">Cariús</span>
            </div>
          </div>
        </section>

        <!-- 5 Cards de KPIs Consolidados do Cliente -->
        <section class="kpis-row-5">
          <div class="glass-card kpi-item">
            <div class="kpi-title">Carga em Paletes</div>
            <div class="kpi-value text-acc" id="kpi-cli-pallets">0,00</div>
            <div class="kpi-delta text-green">
              <span>▲ Paletes</span>
              <span style="color:var(--muted);font-weight:400">calculados</span>
            </div>
          </div>

          <div class="glass-card kpi-item">
            <div class="kpi-title">Peso Bruto Total</div>
            <div class="kpi-value text-indigo" id="kpi-cli-peso">0 kg</div>
            <div class="kpi-delta text-indigo">
              <span id="kpi-cli-peso-sub">0,0 t</span>
              <span style="color:var(--muted);font-weight:400">peso total</span>
            </div>
          </div>

          <div class="glass-card kpi-item">
            <div class="kpi-title">Volume em HL</div>
            <div class="kpi-value" id="kpi-cli-hl">0,00</div>
            <div class="kpi-delta text-blue">
              <span>▲ HL</span>
              <span style="color:var(--muted);font-weight:400">faturado</span>
            </div>
          </div>

          <div class="glass-card kpi-item">
            <div class="kpi-title">Total de Pedidos</div>
            <div class="kpi-value" id="kpi-cli-pedidos">0</div>
            <div class="kpi-delta text-green">
              <span>▲ Ativos</span>
              <span style="color:var(--muted);font-weight:400">no período</span>
            </div>
          </div>

          <div class="glass-card kpi-item">
            <div class="kpi-title">Itens Distintos</div>
            <div class="kpi-value" id="kpi-cli-qtd">0</div>
            <div class="kpi-delta text-amber">
              <span>▲ Itens</span>
              <span style="color:var(--muted);font-weight:400">distintos</span>
            </div>
          </div>
        </section>

        <!-- 1. Tabela de Pedidos Individuais do Cliente -->
        <section class="glass-card">
          <div class="card-head">
            <div>
              <h3>Pedidos Individuais do Cliente</h3>
              <p>visão por pedido com número, data, operação, situações de atendimento, peso e paletes</p>
            </div>
            <div class="meta-badge" id="client-pedidos-count-badge">0 Pedidos</div>
          </div>

          <div class="table-container">
            <table class="data-table" style="min-width: 900px;">
              <thead>
                <tr>
                  <th style="width: 100px;">Nº Pedido</th>
                  <th style="width: 105px;">Data Entrega</th>
                  <th style="min-width: 170px;">Tipo Movimento / Operação</th>
                  <th style="min-width: 130px;">Situação Pedido</th>
                  <th style="min-width: 140px;">Situação Atend.</th>
                  <th class="num-col" style="width: 95px;">Qtd (Un.)</th>
                  <th class="num-col" style="width: 110px;">Peso (Kg)</th>
                  <th class="num-col" style="width: 85px;">Paletes</th>
                  <th class="num-col" style="width: 115px;">Volume (HL)</th>
                </tr>
              </thead>
              <tbody id="tbody-client-pedidos">
                <!-- Injetado via SPECS -->
              </tbody>
            </table>
          </div>

          <div class="table-footer">
            <span style="color:var(--muted); text-transform:uppercase; font-size:11px;">Resumo dos Pedidos Ativos</span>
            <span id="footer-client-pedidos">0 pedidos ativos</span>
          </div>
        </section>

        <!-- 2. Tabela de Produtos Comprados pelo Cliente -->
        <section class="glass-card">
          <div class="card-head">
            <div>
              <h3>Produtos Solicitados pelo Cliente</h3>
              <p>mix de SKUs com volume faturado, quantidade em caixas, peso bruto e paletes calculados</p>
            </div>
            <div class="meta-badge" id="client-prods-count-badge">0 SKUs</div>
          </div>

          <div class="table-container">
            <table class="data-table" style="min-width: 780px;">
              <thead>
                <tr>
                  <th style="width: 44px; text-align: center;">#</th>
                  <th style="min-width: 250px;">Produto</th>
                  <th class="num-col" style="width: 100px;">Quantidade</th>
                  <th class="num-col" style="width: 110px;">Peso (Kg)</th>
                  <th class="num-col" style="width: 90px;">Paletes</th>
                  <th class="num-col" style="width: 120px;">Volume (HL)</th>
                </tr>
              </thead>
              <tbody id="tbody-client-produtos">
                <!-- Injetado via SPECS -->
              </tbody>
            </table>
          </div>

          <div class="table-footer">
            <span style="color:var(--muted); text-transform:uppercase; font-size:11px;">Total de Produtos do Cliente</span>
            <span id="footer-client-produtos">0 SKUs</span>
          </div>
        </section>
      </div>
    </div>
  </div>

  <script>
    // ----------------------------------------------------
    // OBJETO DADOS: Valores reais do BUFFER.csv e 01.11.csv
    // ----------------------------------------------------
    const DADOS = {{
      summary: {json.dumps(summary, ensure_ascii=False)},
      daily: {json.dumps(d['daily'], ensure_ascii=False)},
      products: {json.dumps(products, ensure_ascii=False)},
      clients: {json.dumps(clients, ensure_ascii=False)},
      cities: {json.dumps(cities, ensure_ascii=False)},
      clients_lookup: {json.dumps(clients_lookup, ensure_ascii=False)}
    }};

    // ----------------------------------------------------
    // OBJETO SPECS: Funções de renderização do Light Report
    // ----------------------------------------------------
    const SPECS = {{
      currentTab: 'geral',
      selectedClientCod: null,

      formatBR(num, decimals = 2) {{
        return Number(num || 0).toLocaleString('pt-BR', {{
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals
        }});
      }},

      switchTab(tab) {{
        this.currentTab = tab;
        const btnGeral = document.getElementById('tab-btn-geral');
        const btnCliente = document.getElementById('tab-btn-cliente');
        const viewGeral = document.getElementById('view-geral');
        const viewCliente = document.getElementById('view-cliente');

        if (tab === 'geral') {{
          btnGeral.classList.add('active');
          btnCliente.classList.remove('active');
          viewGeral.style.display = 'flex';
          viewCliente.style.display = 'none';
        }} else {{
          btnCliente.classList.add('active');
          btnGeral.classList.remove('active');
          viewGeral.style.display = 'none';
          viewCliente.style.display = 'flex';
          const input = document.getElementById('client-search-input');
          if (input && !this.selectedClientCod) input.focus();
        }}
      }},

      renderHero(dados) {{
        const heroVal = document.getElementById('hero-val');
        if (heroVal) heroVal.innerHTML = `${{this.formatBR(dados.summary.total_volume_hl)}} <span>HL</span>`;
      }},

      renderKPIs(dados) {{
        const elEntregas = document.getElementById('kpi-entregas');
        const elClientes = document.getElementById('kpi-clientes');
        const elProdutos = document.getElementById('kpi-produtos');
        const elCidades = document.getElementById('kpi-cidades');
        const elPeso = document.getElementById('kpi-peso');
        const elPallets = document.getElementById('kpi-pallets');

        if (elEntregas) elEntregas.innerText = dados.summary.total_pedidos.toLocaleString('pt-BR');
        if (elClientes) elClientes.innerText = dados.summary.total_clientes.toLocaleString('pt-BR');
        if (elProdutos) elProdutos.innerText = dados.summary.total_produtos.toLocaleString('pt-BR');
        if (elCidades) elCidades.innerText = dados.summary.total_cidades.toLocaleString('pt-BR');
        if (elPeso) elPeso.innerText = `${{this.formatBR(dados.summary.total_peso_ton, 2)}} t`;
        if (elPallets) elPallets.innerText = this.formatBR(dados.summary.total_pallets, 2);
      }},

      renderTables(dados) {{
        // Tabela de Clientes com Maiores Pedidos
        const tbodyClientes = document.getElementById('tbody-clientes');
        if (tbodyClientes) {{
          const maxClientHl = dados.clients[0]?.hl || 1;
          tbodyClientes.innerHTML = dados.clients.map((c, idx) => {{
            const pct = Math.min(100, Math.round((c.hl / maxClientHl) * 100));
            return `
              <tr style="cursor: pointer;" onclick="SPECS.selectClientFromRanking(${{c.cod}})" title="Clique para abrir a análise deste cliente">
                <td style="text-align:center;"><span class="ranking-badge">${{idx + 1}}</span></td>
                <td style="text-align:center;">
                  <span style="font-family:var(--mono); font-weight:700; color:var(--acc); background:var(--plane-2); border:var(--bw) solid var(--stroke); padding:3px 8px; border-radius:4px; font-size:11.5px; display:inline-block;">${{c.cod}}</span>
                </td>
                <td>
                  <div style="font-weight:700; color:var(--ink); font-size:13px;" title="${{c.nome}}">${{c.nome}}</div>
                  ${{c.razao ? `<div style="font-size:11px; color:var(--muted); margin-top:2px;" title="${{c.razao}}">${{c.razao}}</div>` : ''}}
                </td>
                <td>
                  <span style="color:var(--ink-2); font-weight:600; font-size:12px;">${{c.cidade}}</span>
                </td>
                <td class="num-col" style="font-weight:700; color:var(--acc-2); font-size:13px;">${{c.pedidos.toLocaleString('pt-BR')}}</td>
                <td class="num-col">${{c.quantidade.toLocaleString('pt-BR')}}</td>
                <td class="num-col" style="font-weight:600; color:var(--ink-2); font-size:12px;">${{this.formatBR(c.peso_kg, 2)}} kg</td>
                <td class="num-col" style="font-weight:700; color:var(--acc); font-size:12.5px;">${{this.formatBR(c.pallets, 2)}}</td>
                <td class="num-col">
                  <div class="text-acc" style="font-size:13px;">${{this.formatBR(c.hl)}} HL</div>
                  <div class="bar-bg">
                    <div class="bar-fill" style="width: ${{pct}}%;"></div>
                  </div>
                </td>
              </tr>
            `;
          }}).join('');
        }}

        // Tabela de Produtos
        const tbodyProd = document.getElementById('tbody-produtos');
        if (tbodyProd) {{
          const maxProdHl = dados.products[0]?.hl || 1;
          tbodyProd.innerHTML = dados.products.map((p, idx) => {{
            const pct = Math.min(100, Math.round((p.hl / maxProdHl) * 100));
            const fatorInfo = p.cx_pallet > 0 ? `${{p.cx_pallet}} cx/pal · ${{this.formatBR(p.peso_unit_kg, 3)}} kg/un` : `${{this.formatBR(p.peso_unit_kg, 3)}} kg/un`;
            return `
              <tr>
                <td style="text-align:center;"><span class="ranking-badge">${{idx + 1}}</span></td>
                <td>
                  <div style="font-weight:700; color:var(--ink); font-size:12.5px;" title="${{p.produto}}">${{p.produto}}</div>
                  <div style="font-size:11px; color:var(--muted); font-family:var(--mono); margin-top:2px;">Cód: ${{p.cod}} · ${{fatorInfo}}</div>
                  <div class="bar-bg">
                    <div class="bar-fill" style="width: ${{pct}}%;"></div>
                  </div>
                </td>
                <td class="num-col">${{p.quantidade.toLocaleString('pt-BR')}}</td>
                <td class="num-col" style="font-weight:600; color:var(--ink-2); font-size:12px;">${{this.formatBR(p.peso_kg, 2)}} kg</td>
                <td class="num-col" style="font-weight:700; color:var(--acc); font-size:12.5px;">${{this.formatBR(p.pallets, 2)}}</td>
                <td class="num-col text-acc" style="font-size:13px;">${{this.formatBR(p.hl)}} HL</td>
              </tr>
            `;
          }}).join('');
        }}

        // Tabela de Cidades
        const tbodyCidades = document.getElementById('tbody-cidades');
        if (tbodyCidades) {{
          const maxCityHl = dados.cities[0]?.hl || 1;
          tbodyCidades.innerHTML = dados.cities.map((c, idx) => {{
            const pct = Math.min(100, Math.round((c.hl / maxCityHl) * 100));
            return `
              <tr>
                <td style="text-align:center;"><span class="ranking-badge">${{idx + 1}}</span></td>
                <td>
                  <div style="font-weight:700; color:var(--ink); font-size:13px;">${{c.cidade}}</div>
                  <div style="font-size:11px; color:var(--muted); margin-top:2px;">${{c.clientes}} clientes atendidos</div>
                  <div class="bar-bg">
                    <div class="bar-fill" style="width: ${{pct}}%;"></div>
                  </div>
                </td>
                <td class="num-col" style="font-weight:600; color:var(--acc-2);">${{c.pedidos.toLocaleString('pt-BR')}}</td>
                <td class="num-col">${{c.quantidade.toLocaleString('pt-BR')}}</td>
                <td class="num-col" style="font-weight:600; color:var(--ink-2); font-size:12px;">${{this.formatBR(c.peso_kg, 2)}} kg</td>
                <td class="num-col" style="font-weight:700; color:var(--acc); font-size:12.5px;">${{this.formatBR(c.pallets, 2)}}</td>
                <td class="num-col text-acc" style="font-size:13px;">${{this.formatBR(c.hl)}} HL</td>
              </tr>
            `;
          }}).join('');
        }}
      }},

      // ----------------------------------------------------
      // ABA 2: Métodos de Busca e Análise por Cliente
      // ----------------------------------------------------
      initClientSearch(dados) {{
        const input = document.getElementById('client-search-input');
        const dropdown = document.getElementById('search-dropdown');
        const btnClear = document.getElementById('btn-clear-search');
        if (!input || !dropdown) return;

        const clientsList = Object.values(dados.clients_lookup || {{}});

        const handleSearch = () => {{
          const q = input.value.trim().toLowerCase();
          if (!q) {{
            dropdown.style.display = 'none';
            if (btnClear) btnClear.style.display = 'none';
            return;
          }}

          if (btnClear) btnClear.style.display = 'flex';

          const matches = clientsList.filter(c => {{
            const codStr = String(c.cod);
            const nomeStr = (c.nome || '').toLowerCase();
            const razaoStr = (c.razao || '').toLowerCase();
            const cidStr = (c.cidade || '').toLowerCase();
            return codStr.includes(q) || nomeStr.includes(q) || razaoStr.includes(q) || cidStr.includes(q);
          }}).slice(0, 15);

          if (matches.length === 0) {{
            dropdown.innerHTML = `
              <div style="padding: 14px 16px; font-size: 12.5px; color: var(--muted); text-align: center;">
                Nenhum cliente encontrado para "<strong>${{q}}</strong>"
              </div>
            `;
          }} else {{
            dropdown.innerHTML = matches.map(c => `
              <div class="search-item" onclick="SPECS.selectClient(${{c.cod}}, DADOS)">
                <div class="search-item-main">
                  <div class="search-item-nome">${{c.nome}}</div>
                  <div class="search-item-sub">${{c.razao ? `${{c.razao}} · ` : ''}}${{c.cidade}}</div>
                </div>
                <div style="text-align:right;">
                  <span class="search-item-badge">Cód: ${{c.cod}}</span>
                  <div style="font-size:11px; color:var(--muted); font-family:var(--mono); margin-top:3px;">${{c.total_pedidos}} ped. · ${{this.formatBR(c.total_pallets, 2)}} pal.</div>
                </div>
              </div>
            `).join('');
          }}
          dropdown.style.display = 'block';
        }};

        input.addEventListener('input', handleSearch);
        input.addEventListener('focus', () => {{
          if (input.value.trim()) handleSearch();
        }});

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', (e) => {{
          if (!e.target.closest('.search-box')) {{
            dropdown.style.display = 'none';
          }}
        }});

        // Teclado
        input.addEventListener('keydown', (e) => {{
          if (e.key === 'Escape') {{
            dropdown.style.display = 'none';
          }} else if (e.key === 'Enter') {{
            const firstItem = dropdown.querySelector('.search-item');
            if (firstItem) firstItem.click();
          }}
        }});
      }},

      selectClient(cod, dados) {{
        const client = dados.clients_lookup?.[String(cod)];
        if (!client) return;

        this.selectedClientCod = cod;
        const dropdown = document.getElementById('search-dropdown');
        const input = document.getElementById('client-search-input');
        const btnClear = document.getElementById('btn-clear-search');
        const emptyState = document.getElementById('client-empty-state');
        const detailContainer = document.getElementById('client-detail-container');

        if (dropdown) dropdown.style.display = 'none';
        if (input) input.value = `${{client.nome}} (Cód: ${{client.cod}})`;
        if (btnClear) btnClear.style.display = 'flex';

        // Alternar containers
        if (emptyState) emptyState.style.display = 'none';
        if (detailContainer) detailContainer.style.display = 'flex';

        // Cabeçalho do Cliente
        document.getElementById('client-nome').innerText = client.nome;
        document.getElementById('client-cod-badge').innerText = `Cód: ${{client.cod}}`;
        document.getElementById('client-sub').innerText = `${{client.razao ? `${{client.razao}} · ` : ''}}${{client.cidade}}`;
        document.getElementById('client-cidade').innerText = client.cidade;

        // 5 KPIs Consolidados
        document.getElementById('kpi-cli-pallets').innerText = this.formatBR(client.total_pallets, 2);
        document.getElementById('kpi-cli-peso').innerText = `${{this.formatBR(client.total_peso_kg, 1)}} kg`;
        document.getElementById('kpi-cli-peso-sub').innerText = `${{this.formatBR(client.total_peso_kg / 1000, 2)}} t`;
        document.getElementById('kpi-cli-hl').innerText = this.formatBR(client.total_hl, 2);
        document.getElementById('kpi-cli-pedidos').innerText = client.total_pedidos.toLocaleString('pt-BR');
        document.getElementById('kpi-cli-qtd').innerText = (client.total_itens_distintos !== undefined ? client.total_itens_distintos : (client.produtos ? client.produtos.length : 0)).toLocaleString('pt-BR');

        // Tabela 1: Pedidos Individuais
        const tbodyPedidos = document.getElementById('tbody-client-pedidos');
        const badgeCount = document.getElementById('client-pedidos-count-badge');
        const footerPedidos = document.getElementById('footer-client-pedidos');

        if (badgeCount) badgeCount.innerText = `${{client.pedidos.length}} ${{client.pedidos.length === 1 ? 'Pedido' : 'Pedidos'}}`;

        if (tbodyPedidos) {{
          tbodyPedidos.innerHTML = client.pedidos.map(p => {{
            let statusTagClass = 'status-atendido';
            let statusTagText = p.situacao_atend;

            if (p.is_cancelled) {{
              statusTagClass = 'status-cancelado';
              statusTagText = 'CANCELADO';
            }} else if (p.situacao_atend === 'AGUARDANDO_ATENDIMENTO') {{
              statusTagClass = 'status-aguardando';
              statusTagText = 'AGUARDANDO';
            }}

            const rowStyle = p.is_cancelled ? 'opacity: 0.6; background: rgba(220, 38, 38, 0.03);' : '';
            return `
              <tr style="${{rowStyle}}">
                <td><strong style="font-family:var(--mono); color:var(--ink);">${{p.numero_pedido}}</strong></td>
                <td><span style="font-family:var(--mono); font-size:12px; color:var(--ink-2);">${{p.data_entrega}}</span></td>
                <td>
                  <div style="font-weight:700; color:var(--ink);">${{p.tipo_movimento}}</div>
                  <div style="font-size:11px; color:var(--muted);">${{p.operacao}}</div>
                </td>
                <td><span style="font-size:11.5px; color:var(--muted); font-family:var(--mono);">${{p.situacao_pedido}}</span></td>
                <td><span class="status-tag ${{statusTagClass}}">${{statusTagText}}</span></td>
                <td class="num-col">${{p.quantidade.toLocaleString('pt-BR')}}</td>
                <td class="num-col" style="font-weight:600; color:var(--ink-2);">${{this.formatBR(p.peso_kg, 2)}} kg</td>
                <td class="num-col" style="font-weight:700; color:var(--acc);">${{this.formatBR(p.pallets, 2)}}</td>
                <td class="num-col text-acc">${{this.formatBR(p.hl, 2)}} HL</td>
              </tr>
            `;
          }}).join('');
        }}

        if (footerPedidos) {{
          footerPedidos.innerHTML = `${{client.total_pedidos}} pedidos ativos somam <strong>${{this.formatBR(client.total_hl, 2)}} HL</strong> · <strong>${{this.formatBR(client.total_peso_kg, 2)}} kg</strong> · <strong>${{this.formatBR(client.total_pallets, 2)}} pallets</strong>`;
        }}

        // Tabela 2: Produtos Comprados
        const tbodyProdutos = document.getElementById('tbody-client-produtos');
        const prodsCountBadge = document.getElementById('client-prods-count-badge');
        const footerProdutos = document.getElementById('footer-client-produtos');

        if (prodsCountBadge) prodsCountBadge.innerText = `${{client.produtos.length}} SKUs`;

        if (tbodyProdutos) {{
          const maxProdHl = client.produtos[0]?.hl || 1;
          tbodyProdutos.innerHTML = client.produtos.map((p, idx) => {{
            const pct = Math.min(100, Math.round((p.hl / maxProdHl) * 100));
            return `
              <tr>
                <td style="text-align:center;"><span class="ranking-badge">${{idx + 1}}</span></td>
                <td>
                  <div style="font-weight:700; color:var(--ink); font-size:12.5px;" title="${{p.produto}}">${{p.produto}}</div>
                  <div style="font-size:11px; color:var(--muted); font-family:var(--mono); margin-top:2px;">Cód: ${{p.cod}}</div>
                  <div class="bar-bg">
                    <div class="bar-fill" style="width: ${{pct}}%;"></div>
                  </div>
                </td>
                <td class="num-col">${{p.quantidade.toLocaleString('pt-BR')}}</td>
                <td class="num-col" style="font-weight:600; color:var(--ink-2);">${{this.formatBR(p.peso_kg, 2)}} kg</td>
                <td class="num-col" style="font-weight:700; color:var(--acc);">${{this.formatBR(p.pallets, 2)}}</td>
                <td class="num-col text-acc">${{this.formatBR(p.hl, 2)}} HL</td>
              </tr>
            `;
          }}).join('');
        }}

        if (footerProdutos) {{
          footerProdutos.innerHTML = `${{client.produtos.length}} SKUs somam <strong>${{this.formatBR(client.total_hl, 2)}} HL</strong> · <strong>${{this.formatBR(client.total_peso_kg, 2)}} kg</strong> · <strong>${{this.formatBR(client.total_pallets, 2)}} pallets</strong>`;
        }}
      }},

      clearSearch() {{
        this.selectedClientCod = null;
        const input = document.getElementById('client-search-input');
        const dropdown = document.getElementById('search-dropdown');
        const btnClear = document.getElementById('btn-clear-search');
        const emptyState = document.getElementById('client-empty-state');
        const detailContainer = document.getElementById('client-detail-container');

        if (input) {{
          input.value = '';
          input.focus();
        }}
        if (dropdown) dropdown.style.display = 'none';
        if (btnClear) btnClear.style.display = 'none';
        if (emptyState) emptyState.style.display = 'flex';
        if (detailContainer) detailContainer.style.display = 'none';
      }},

      selectClientFromRanking(cod) {{
        this.switchTab('cliente');
        this.selectClient(cod, DADOS);
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }},

      async syncDrive() {{
        const btn = document.getElementById('btn-sync-drive');
        const text = document.getElementById('sync-btn-text');
        if (!btn || btn.disabled) return;

        btn.disabled = true;
        btn.classList.add('syncing');
        text.textContent = 'Puxando do Drive...';

        try {{
          const res = await fetch('/api/sync', {{ method: 'POST' }});
          const data = await res.json();
          if (data.success) {{
            this.showToast('✅ ' + (data.message || 'Dados atualizados com sucesso do Google Drive!'), 'success');
            setTimeout(() => window.location.reload(), 1200);
          }} else {{
            this.showToast('⚠️ ' + (data.error || 'Erro ao sincronizar do Google Drive.'), 'error');
            btn.disabled = false;
            btn.classList.remove('syncing');
            text.textContent = 'Atualizar Dados';
          }}
        }} catch (err) {{
          this.showToast('ℹ️ O botão de sincronização requer o servidor ativo (app.py). Dados locais preservados.', 'info');
          btn.disabled = false;
          btn.classList.remove('syncing');
          text.textContent = 'Atualizar Dados';
        }}
      }},

      showToast(msg, type = 'info') {{
        let toast = document.getElementById('sync-toast');
        if (!toast) {{
          toast = document.createElement('div');
          toast.id = 'sync-toast';
          document.body.appendChild(toast);
        }}
        toast.className = 'sync-toast toast-' + type;
        toast.innerHTML = msg;
        toast.style.display = 'block';
        setTimeout(() => {{
          if (toast) toast.style.display = 'none';
        }}, 5000);
      }},

      async checkSyncStatus() {{
        try {{
          const res = await fetch('/api/status');
          if (res.ok) {{
            const st = await res.json();
            if (st.last_sync && st.last_sync.timestamp) {{
              const btn = document.getElementById('btn-sync-drive');
              if (btn) btn.title = 'Última sincronização do Drive: ' + st.last_sync.timestamp;
            }}
          }}
        }} catch (e) {{}}
      }},

      init(dados) {{
        this.renderHero(dados);
        this.renderKPIs(dados);
        this.renderTables(dados);
        this.initClientSearch(dados);
        this.checkSyncStatus();
      }}
    }};

    window.addEventListener('DOMContentLoaded', () => {{
      SPECS.init(DADOS);
    }});
  </script>
</body>
</html>
'''

    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    with open('mesa-book-consolidado.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Dashboard files updated successfully with 'Visão Geral' and 'Análise por Cliente' tabs!")
    return html_content

if __name__ == '__main__':
    run_generate()
