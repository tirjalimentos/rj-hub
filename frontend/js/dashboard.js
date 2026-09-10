/* ================================================================
   RJ HUB — dashboard.js
   Renderiza os indicadores (KPIs) e o gráfico de uso por
   especialista. Layout novo: kpi-grid sem ícones (mais limpo) e
   barras verticais em vez de barras horizontais — mesma lógica de
   dados de antes (uso por DEPARTAMENTO), só o visual mudou.
   ================================================================ */

function renderDashboardStats(){
  document.getElementById('dashStats').innerHTML = DASH_STATS.map(s => `
    <div class="card stat">
      <div class="stat-label">${s.lab}</div>
      <div class="stat-value">${s.num}</div>
    </div>
  `).join('');
}

function renderDashboardBars(){
  document.getElementById('dashBars').innerHTML = DASH_BARS.map(b => `
    <div class="bar-wrap">
      <div class="bar" style="height:${b.val}%" title="${b.nome}: ${b.val}%"></div>
      <div class="bar-label">${b.nome}</div>
    </div>
  `).join('');
}

function renderDashboard(){
  renderDashboardStats();
  renderDashboardBars();
}
