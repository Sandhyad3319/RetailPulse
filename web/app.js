/**
 * RetailPulse — Interactive Executive Dashboard Application
 * Handles data fetching, Chart.js rendering, tab routing, and real-time search.
 */

// Global Chart defaults for dark theme
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.95)';
  Chart.defaults.plugins.tooltip.titleColor = '#f8fafc';
  Chart.defaults.plugins.tooltip.bodyColor = '#94a3b8';
  Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

let appData = null;
let charts = {};

// Helper: Format Currency GBP
function formatGBP(val) {
  if (val === null || val === undefined) return '£0.00';
  const num = Number(val);
  if (isNaN(num)) return '£0.00';
  return '£' + num.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Helper: Format Numbers with commas
function formatNumber(val) {
  if (val === null || val === undefined) return '0';
  const num = Number(val);
  if (isNaN(num)) return String(val);
  return num.toLocaleString('en-GB');
}

// Tab Switching Logic
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');

      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }

      // Trigger resize on charts in the newly active tab
      setTimeout(() => {
        Object.values(charts).forEach(chart => {
          if (chart) chart.resize();
        });
      }, 50);
    });
  });
}

// Bind Top KPI Cards dynamically from loaded JSON
function renderKPIs() {
  if (!appData || !appData.kpis) return;
  const kpis = appData.kpis;

  const elNetRev = document.getElementById('kpi-net-revenue');
  if (elNetRev) elNetRev.textContent = formatGBP(kpis.net_revenue_gbp);

  const elOrders = document.getElementById('kpi-total-orders');
  if (elOrders) elOrders.textContent = formatNumber(kpis.total_orders);

  const elAOV = document.getElementById('kpi-aov');
  if (elAOV) {
    const aov = kpis.total_orders > 0 ? (kpis.net_revenue_gbp / kpis.total_orders) : 0;
    elAOV.textContent = formatGBP(aov);
  }

  const elUnits = document.getElementById('kpi-units-sold');
  if (elUnits) elUnits.textContent = formatNumber(kpis.net_units_sold);

  const elReturnRate = document.getElementById('kpi-return-rate');
  if (elReturnRate) elReturnRate.textContent = kpis.refund_rate_pct.toFixed(2) + '%';
}

// Initialize and render all Dashboard charts
async function initDashboard() {
  initTabs();

  try {
    const res = await fetch('dashboard_data.json');
    appData = await res.json();
  } catch (err) {
    console.error('Failed to fetch dashboard_data.json:', err);
    return;
  }

  renderKPIs();
  renderOverviewCharts();
  renderTrendsCharts();
  renderProductCharts();
  renderCustomerCharts();
  renderGeographyCharts();
  initSqlStudio();
  initWhatIfSimulator();
  initExportButtons();
  initTableSorting();
}

// -------------------------------------------------------------
// TAB 1: EXECUTIVE OVERVIEW CHARTS
// -------------------------------------------------------------
function renderOverviewCharts() {
  const trends = appData.monthly_trends;
  const labels = trends.map(t => t.year_month);
  const revenues = trends.map(t => t.net_revenue_gbp ?? t.net_monthly_revenue_gbp);

  // 1. Monthly Overview Line & Bar Chart
  const ctxOverview = document.getElementById('chart-overview-monthly').getContext('2d');
  charts.overviewMonthly = new Chart(ctxOverview, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          type: 'line',
          label: 'Net Revenue (£)',
          data: revenues,
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.1)',
          borderWidth: 3,
          tension: 0.35,
          fill: true,
          pointBackgroundColor: '#06b6d4',
          pointRadius: 4,
          pointHoverRadius: 7,
          yAxisID: 'y'
        },
        {
          type: 'bar',
          label: 'Monthly Orders',
          data: trends.map(t => t.monthly_orders ?? t.order_count),
          backgroundColor: 'rgba(59, 130, 246, 0.35)',
          borderRadius: 6,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.03)' } },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            callback: val => '£' + (val / 1000) + 'k'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: {
            callback: val => val + ' orders'
          }
        }
      }
    }
  });

  // 2. Channel Split Donut
  const ctxDonut = document.getElementById('chart-overview-donuts').getContext('2d');
  charts.overviewDonut = new Chart(ctxDonut, {
    type: 'doughnut',
    data: {
      labels: ['Registered Loyalty Accounts', 'Guest Checkouts'],
      datasets: [{
        data: [8278519.42, 1469611.65],
        backgroundColor: ['#06b6d4', '#8b5cf6'],
        borderColor: '#0f172a',
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, padding: 16 } },
        tooltip: {
          callbacks: {
            label: item => ` ${item.label}: ${formatGBP(item.raw)} (${((item.raw / 9748131.07) * 100).toFixed(1)}%)`
          }
        }
      },
      cutout: '72%'
    }
  });
}

// -------------------------------------------------------------
// TAB 2: SALES TRENDS & SEASONALITY
// -------------------------------------------------------------
function renderTrendsCharts() {
  const trends = appData.monthly_trends;
  const labels = trends.map(t => t.year_month);

  // Gross vs Returns Bar Chart
  const ctxGross = document.getElementById('chart-gross-returns').getContext('2d');
  charts.grossReturns = new Chart(ctxGross, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Gross Sales (£)',
          data: trends.map(t => t.gross_revenue_gbp ?? t.gross_sales_gbp),
          backgroundColor: '#3b82f6',
          borderRadius: 6
        },
        {
          label: 'Returns Deducted (£)',
          data: trends.map(t => Math.abs(t.refund_value_gbp ?? t.return_refunds_gbp ?? 0)),
          backgroundColor: '#f43f5e',
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.03)' } },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { callback: v => '£' + (v / 1000) + 'k' }
        }
      }
    }
  });

  // Cumulative Growth Chart
  const cumData = appData.cumulative_revenue;
  const ctxCum = document.getElementById('chart-cumulative').getContext('2d');
  charts.cumulative = new Chart(ctxCum, {
    type: 'line',
    data: {
      labels: cumData.map(c => c.year_month),
      datasets: [{
        label: 'Cumulative Net Revenue (£)',
        data: cumData.map(c => c.cumulative_running_revenue_gbp),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
        pointBackgroundColor: '#10b981'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.03)' } },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { callback: v => '£' + (v / 1000000).toFixed(1) + 'M' }
        }
      }
    }
  });

  // Populate Monthly Table
  const tbody = document.querySelector('#table-monthly-trends tbody');
  tbody.innerHTML = '';
  trends.forEach(t => {
    const gross = t.gross_revenue_gbp ?? t.gross_sales_gbp ?? 0;
    const refund = t.refund_value_gbp ?? t.return_refunds_gbp ?? 0;
    const net = t.net_revenue_gbp ?? t.net_monthly_revenue_gbp ?? (gross + refund);
    const orders = t.monthly_orders ?? t.order_count ?? 0;
    const units = t.net_units_sold ?? t.units_sold ?? 0;
    const refundRate = t.refund_rate_pct !== undefined ? t.refund_rate_pct : (gross > 0 ? (Math.abs(refund) * 100 / gross) : 0);
    const aov = t.average_order_value_gbp !== undefined ? t.average_order_value_gbp : (orders > 0 ? (net / orders) : 0);

    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="mono"><strong>${t.year_month}</strong></td>
      <td>${formatNumber(orders)}</td>
      <td class="mono positive">${formatGBP(gross)}</td>
      <td class="mono negative">-${formatGBP(Math.abs(refund))}</td>
      <td class="mono"><strong>${formatGBP(net)}</strong></td>
      <td>${refundRate.toFixed(2)}%</td>
      <td>${formatNumber(units)}</td>
      <td class="mono">${formatGBP(aov)}</td>
    `;
    tbody.appendChild(row);
  });
}

// -------------------------------------------------------------
// TAB 3: PRODUCT PERFORMANCE
// -------------------------------------------------------------
function renderProductCharts() {
  const topRev = appData.top_products_revenue;
  const topVol = appData.top_products_units;

  // Top 10 by Revenue Horizontal Bar
  const ctxTopRev = document.getElementById('chart-top-products-rev').getContext('2d');
  charts.topProductsRev = new Chart(ctxTopRev, {
    type: 'bar',
    data: {
      labels: topRev.map(p => p.description.slice(0, 22) + '...'),
      datasets: [{
        label: 'Net Revenue (£)',
        data: topRev.map(p => p.product_net_revenue),
        backgroundColor: '#8b5cf6',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { callback: v => '£' + (v / 1000) + 'k' }
        },
        y: { grid: { display: false } }
      }
    }
  });

  // Top 10 by Volume Horizontal Bar
  const ctxTopVol = document.getElementById('chart-top-products-vol').getContext('2d');
  charts.topProductsVol = new Chart(ctxTopVol, {
    type: 'bar',
    data: {
      labels: topVol.map(p => p.description.slice(0, 22) + '...'),
      datasets: [{
        label: 'Units Sold',
        data: topVol.map(p => p.total_units_sold),
        backgroundColor: '#06b6d4',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { callback: v => (v / 1000) + 'k' }
        },
        y: { grid: { display: false } }
      }
    }
  });

  // Populate Product Table
  const tbody = document.querySelector('#table-top-products tbody');
  const countDisplay = document.getElementById('product-count-display');
  function populateProductTable(list) {
    tbody.innerHTML = '';
    if (countDisplay) {
      countDisplay.textContent = `Showing ${list.length} of ${topRev.length} items`;
    }
    list.forEach((p, idx) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><span class="tag-pill cyan">#${idx + 1}</span></td>
        <td class="mono">${p.stock_code}</td>
        <td><strong>${p.description}</strong></td>
        <td>${formatNumber(p.units_sold ?? p.total_units_sold ?? 0)}</td>
        <td>${p.order_appearances !== undefined ? formatNumber(p.order_appearances) : 'N/A'}</td>
        <td class="mono positive">${formatGBP(p.product_net_revenue ?? p.net_product_revenue_gbp)}</td>
        <td><strong>${Number(p.pct_of_total_revenue || 0).toFixed(2)}%</strong></td>
      `;
      tbody.appendChild(row);
    });
  }
  populateProductTable(topRev);

  // Search filter
  const searchInput = document.getElementById('product-search');
  searchInput.addEventListener('input', e => {
    const term = e.target.value.toLowerCase();
    const filtered = topRev.filter(p =>
      p.stock_code.toLowerCase().includes(term) ||
      p.description.toLowerCase().includes(term)
    );
    populateProductTable(filtered);
  });
}

// -------------------------------------------------------------
// TAB 4: CUSTOMER INTELLIGENCE & VIPs
// -------------------------------------------------------------
function renderCustomerCharts() {
  const tiers = appData.repeat_customer_dist;

  // Frequency Tiers Chart
  const ctxTiers = document.getElementById('chart-loyalty-tiers').getContext('2d');
  charts.loyaltyTiers = new Chart(ctxTiers, {
    type: 'bar',
    data: {
      labels: tiers.map(t => t.loyalty_tier),
      datasets: [
        {
          label: 'Customer Count',
          data: tiers.map(t => t.customer_count),
          backgroundColor: '#3b82f6',
          borderRadius: 6,
          yAxisID: 'y'
        },
        {
          label: 'Revenue Generated (£)',
          data: tiers.map(t => t.tier_revenue_gbp),
          backgroundColor: '#10b981',
          borderRadius: 6,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: 'rgba(255, 255, 255, 0.03)' } },
        y: {
          position: 'left',
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { callback: v => v + ' buyers' }
        },
        y1: {
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { callback: v => '£' + (v / 1000) + 'k' }
        }
      }
    }
  });

  // Guest vs Registered Chart
  const ctxGuest = document.getElementById('chart-guest-split').getContext('2d');
  charts.guestSplit = new Chart(ctxGuest, {
    type: 'doughnut',
    data: {
      labels: ['Registered Loyalty Spend', 'Guest Checkout Revenue'],
      datasets: [{
        data: [8278519.42, 1469611.65],
        backgroundColor: ['#06b6d4', '#f59e0b'],
        borderColor: '#0f172a',
        borderWidth: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } }
      },
      cutout: '70%'
    }
  });

  // Populate Top 10 Customers Table
  const tbody = document.querySelector('#table-top-customers tbody');
  tbody.innerHTML = '';
  appData.top_customers.forEach((c, idx) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><span class="tag-pill purple">#${idx + 1}</span></td>
      <td class="mono"><strong>${c.customer_id}</strong></td>
      <td>${c.country}</td>
      <td><span class="status-pill">${c.customer_type}</span></td>
      <td>${c.total_orders}</td>
      <td>${formatNumber(c.total_items_bought)}</td>
      <td>${c.first_order_date}</td>
      <td>${c.last_order_date}</td>
      <td class="mono positive"><strong>${formatGBP(c.lifetime_spend_gbp)}</strong></td>
    `;
    tbody.appendChild(row);
  });
}

// -------------------------------------------------------------
// TAB 5: GEOGRAPHIC MARKETS
// -------------------------------------------------------------
function renderGeographyCharts() {
  const aov = appData.aov_by_region;
  const returns = appData.returns_by_country.slice(0, 8); // Top friction countries

  // Region AOV
  const ctxAOV = document.getElementById('chart-region-aov').getContext('2d');
  charts.regionAOV = new Chart(ctxAOV, {
    type: 'bar',
    data: {
      labels: aov.map(r => r.market_region),
      datasets: [{
        label: 'Average Order Value (£)',
        data: aov.map(r => r.average_order_value_gbp),
        backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981'],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { callback: v => '£' + v }
        }
      }
    }
  });

  // Return Friction Bar
  const ctxFriction = document.getElementById('chart-return-friction').getContext('2d');
  charts.friction = new Chart(ctxFriction, {
    type: 'bar',
    data: {
      labels: returns.map(r => r.country),
      datasets: [{
        label: 'Refund Rate (%) by Value',
        data: returns.map(r => r.refund_value_rate_pct),
        backgroundColor: '#f43f5e',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { callback: v => v + '%' }
        }
      }
    }
  });

  // Populate Country Table
  const tbody = document.querySelector('#table-country-revenue tbody');
  tbody.innerHTML = '';
  appData.country_revenue.forEach(c => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><span class="tag-pill blue">${c.market_region}</span></td>
      <td><strong>${c.country}</strong></td>
      <td>${formatNumber(c.total_orders)}</td>
      <td>${formatNumber(c.active_customers)}</td>
      <td class="mono positive">${formatGBP(c.net_revenue_gbp)}</td>
      <td><strong>${c.pct_global_revenue.toFixed(2)}%</strong></td>
    `;
    tbody.appendChild(row);
  });
}

// -------------------------------------------------------------
// TAB 6: INTERACTIVE SQL QUERY STUDIO & DATA MODEL
// -------------------------------------------------------------
function initSqlStudio() {
  const select = document.getElementById('sql-query-select');
  if (!select || !appData || !appData.sql_queries_library) return;

  select.innerHTML = '';
  appData.sql_queries_library.forEach(q => {
    const opt = document.createElement('option');
    opt.value = q.num;
    opt.textContent = `Query ${String(q.num).padStart(2, '0')}: ${q.title}`;
    select.appendChild(opt);
  });

  function renderSelectedQuery(num) {
    const q = appData.sql_queries_library.find(item => item.num === Number(num));
    if (!q) return;

    // Business Question
    const bqEl = document.getElementById('sql-business-question');
    if (bqEl) bqEl.textContent = q.business_question || 'Analytical business query executed against data/processed/retailpulse.db';

    // Concept Tags
    const tagsEl = document.getElementById('sql-concept-tags');
    if (tagsEl) {
      tagsEl.innerHTML = '';
      const concepts = (q.concepts || 'SQL Aggregations').split(',').map(c => c.trim());
      concepts.forEach(c => {
        const span = document.createElement('span');
        span.className = 'concept-tag';
        span.textContent = c;
        tagsEl.appendChild(span);
      });
    }

    // Code
    const codeEl = document.getElementById('sql-code-display');
    if (codeEl) codeEl.textContent = q.sql;

    // Row Count
    const countEl = document.getElementById('sql-row-count');
    if (countEl) countEl.textContent = q.rows ? q.rows.length : 0;

    // Results Table
    const thead = document.getElementById('sql-results-thead');
    const tbody = document.getElementById('sql-results-tbody');
    if (thead && tbody) {
      thead.innerHTML = '';
      tbody.innerHTML = '';

      if (q.columns && q.columns.length > 0) {
        const trHead = document.createElement('tr');
        q.columns.forEach(col => {
          const th = document.createElement('th');
          th.textContent = col.replace(/_/g, ' ').toUpperCase();
          trHead.appendChild(th);
        });
        thead.appendChild(trHead);

        if (q.rows && q.rows.length > 0) {
          q.rows.forEach(row => {
            const tr = document.createElement('tr');
            q.columns.forEach(col => {
              const td = document.createElement('td');
              const val = row[col];
              if (typeof val === 'number') {
                if (col.includes('revenue') || col.includes('gbp') || col.includes('spend') || col.includes('price')) {
                  td.textContent = formatGBP(val);
                  td.className = 'mono positive';
                } else if (col.includes('pct') || col.includes('rate') || col.includes('share')) {
                  td.textContent = val.toFixed(2) + '%';
                  td.className = 'mono';
                } else {
                  td.textContent = formatNumber(val);
                  td.className = 'mono';
                }
              } else {
                td.textContent = val ?? 'N/A';
              }
              tr.appendChild(td);
            });
            tbody.appendChild(tr);
          });
        }
      }
    }
  }

  select.addEventListener('change', e => {
    renderSelectedQuery(e.target.value);
  });

  // Initial render with Query 1
  renderSelectedQuery(1);

  // Copy SQL button
  const copyBtn = document.getElementById('btn-copy-sql');
  const copyText = document.getElementById('copy-text');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const code = document.getElementById('sql-code-display').textContent;
      navigator.clipboard.writeText(code).then(() => {
        if (copyText) {
          const orig = copyText.textContent;
          copyText.textContent = '✓ Copied!';
          setTimeout(() => { copyText.textContent = orig; }, 1500);
        }
      });
    });
  }

  // Export Query CSV button
  const exportBtn = document.getElementById('btn-export-query-results');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const qNum = select.value;
      const q = appData.sql_queries_library.find(item => item.num === Number(qNum));
      const filename = `RetailPulse_Query_${String(qNum).padStart(2, '0')}_results.csv`;
      exportTableToCSV('table-sql-results', filename);
    });
  }
}

// -------------------------------------------------------------
// WHAT-IF STRATEGIC SCENARIO SIMULATOR
// -------------------------------------------------------------
function initWhatIfSimulator() {
  const sliderGuest = document.getElementById('slider-guest-conv');
  const displayGuest = document.getElementById('val-guest-conv');
  const resAccounts = document.getElementById('res-guest-accounts');
  const resRepeat = document.getElementById('res-guest-repeat');
  const resRevenue = document.getElementById('res-guest-revenue');

  function updateGuestSim() {
    if (!sliderGuest) return;
    const rate = Number(sliderGuest.value);
    if (displayGuest) displayGuest.textContent = rate + '%';

    // 1,610 guest orders, £1,469,611.65 revenue
    const newAccounts = Math.round(1610 * (rate / 100));
    // Repeat rate among registered is 69.98%
    const repeatOrders = Math.round(newAccounts * 0.6998 * 2.4);
    // Estimated average lifetime uplift per converted account
    const revUplift = Math.round(newAccounts * 686.60);

    if (resAccounts) resAccounts.textContent = `+${formatNumber(newAccounts)}`;
    if (resRepeat) resRepeat.textContent = `+${formatNumber(repeatOrders)} orders`;
    if (resRevenue) resRevenue.textContent = `+${formatGBP(revUplift)}`;
  }

  if (sliderGuest) {
    sliderGuest.addEventListener('input', updateGuestSim);
    updateGuestSim();
  }

  const sliderRefund = document.getElementById('slider-refund-reduct');
  const displayRefund = document.getElementById('val-refund-reduct');
  const resNewRate = document.getElementById('res-new-rate');
  const resSavedLines = document.getElementById('res-saved-lines');
  const resRefundSavings = document.getElementById('res-refund-savings');

  function updateRefundSim() {
    if (!sliderRefund) return;
    const reduction = Number(sliderRefund.value);
    if (displayRefund) displayRefund.textContent = `-${reduction.toFixed(1)}%`;

    const baselineRate = 8.40;
    const baselineGross = 10642110.80;
    const newRate = Math.max(0, baselineRate - reduction);
    const savings = Math.round(baselineGross * (reduction / 100));
    const savedLines = Math.round(9251 * (reduction / baselineRate));

    if (resNewRate) resNewRate.textContent = `${newRate.toFixed(2)}%`;
    if (resSavedLines) resSavedLines.textContent = `~${formatNumber(savedLines)} lines`;
    if (resRefundSavings) resRefundSavings.textContent = `+${formatGBP(savings)}`;
  }

  if (sliderRefund) {
    sliderRefund.addEventListener('input', updateRefundSim);
    updateRefundSim();
  }
}

// -------------------------------------------------------------
// UNIVERSAL CSV EXPORTER UTILITY
// -------------------------------------------------------------
function exportTableToCSV(tableId, filename) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const rows = [];
  const headerCells = table.querySelectorAll('thead th');
  if (headerCells.length > 0) {
    const headers = Array.from(headerCells).map(th => `"${th.textContent.trim().replace(/"/g, '""')}"`);
    rows.push(headers.join(','));
  }

  const bodyRows = table.querySelectorAll('tbody tr');
  bodyRows.forEach(tr => {
    const cells = tr.querySelectorAll('td');
    const rowData = Array.from(cells).map(td => {
      let text = td.textContent.trim();
      text = text.replace(/\s+/g, ' ');
      return `"${text.replace(/"/g, '""')}"`;
    });
    rows.push(rowData.join(','));
  });

  const csvContent = "\uFEFF" + rows.join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || 'retailpulse_export.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function initExportButtons() {
  const bindExport = (btnId, tableId, filename) => {
    const btn = document.getElementById(btnId);
    if (btn) {
      btn.addEventListener('click', () => exportTableToCSV(tableId, filename));
    }
  };

  bindExport('btn-export-monthly', 'table-monthly-trends', 'RetailPulse_Monthly_Financial_Statement.csv');
  bindExport('btn-export-products', 'table-top-products', 'RetailPulse_Product_Catalog_Leaderboard.csv');
  bindExport('btn-export-customers', 'table-top-customers', 'RetailPulse_Top_VIP_Customers.csv');
  bindExport('btn-export-geography', 'table-country-revenue', 'RetailPulse_Country_Market_Segmentation.csv');
}

// -------------------------------------------------------------
// DYNAMIC TABLE COLUMN SORTING
// -------------------------------------------------------------
function initTableSorting() {
  const tables = document.querySelectorAll('.data-table');
  tables.forEach(table => {
    const headers = table.querySelectorAll('thead th');
    headers.forEach((th, colIdx) => {
      th.classList.add('sortable');
      th.title = 'Click to sort ascending/descending';
      let asc = true;
      th.addEventListener('click', () => {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        const rows = Array.from(tbody.querySelectorAll('tr'));
        rows.sort((a, b) => {
          const aCell = a.children[colIdx];
          const bCell = b.children[colIdx];
          const aText = aCell ? aCell.textContent.trim() : '';
          const bText = bCell ? bCell.textContent.trim() : '';
          
          const aClean = aText.replace(/[^0-9.-]+/g, '');
          const bClean = bText.replace(/[^0-9.-]+/g, '');
          const aNum = parseFloat(aClean);
          const bNum = parseFloat(bClean);
          
          if (!isNaN(aNum) && !isNaN(bNum) && aClean.length > 0 && bClean.length > 0) {
            return asc ? aNum - bNum : bNum - aNum;
          }
          return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
        });
        asc = !asc;
        tbody.innerHTML = '';
        rows.forEach(r => tbody.appendChild(r));
      });
    });
  });
}

// Start application on DOM ready
document.addEventListener('DOMContentLoaded', initDashboard);
