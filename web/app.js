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
  return '£' + Number(val).toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Helper: Format Numbers with commas
function formatNumber(val) {
  return Number(val).toLocaleString('en-GB');
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

  renderOverviewCharts();
  renderTrendsCharts();
  renderProductCharts();
  renderCustomerCharts();
  renderGeographyCharts();
}

// -------------------------------------------------------------
// TAB 1: EXECUTIVE OVERVIEW CHARTS
// -------------------------------------------------------------
function renderOverviewCharts() {
  const trends = appData.monthly_trends;
  const labels = trends.map(t => t.year_month);
  const revenues = trends.map(t => t.net_monthly_revenue_gbp);

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
          data: trends.map(t => t.order_count),
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
          data: trends.map(t => t.gross_sales_gbp),
          backgroundColor: '#3b82f6',
          borderRadius: 6
        },
        {
          label: 'Returns Deducted (£)',
          data: trends.map(t => Math.abs(t.return_refunds_gbp)),
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
    const row = document.createElement('tr');
    row.innerHTML = `
      <td class="mono"><strong>${t.year_month}</strong></td>
      <td>${formatNumber(t.order_count)}</td>
      <td class="mono positive">${formatGBP(t.gross_sales_gbp)}</td>
      <td class="mono negative">-${formatGBP(Math.abs(t.return_refunds_gbp))}</td>
      <td class="mono"><strong>${formatGBP(t.net_monthly_revenue_gbp)}</strong></td>
      <td>${t.refund_rate_pct.toFixed(2)}%</td>
      <td>${formatNumber(t.units_sold)}</td>
      <td class="mono">${formatGBP(t.average_order_value_gbp)}</td>
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
  function populateProductTable(list) {
    tbody.innerHTML = '';
    list.forEach((p, idx) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><span class="tag-pill cyan">#${idx + 1}</span></td>
        <td class="mono">${p.stock_code}</td>
        <td><strong>${p.description}</strong></td>
        <td>${formatNumber(p.units_sold)}</td>
        <td>${formatNumber(p.order_appearances || 'N/A')}</td>
        <td class="mono positive">${formatGBP(p.product_net_revenue)}</td>
        <td><strong>${p.pct_of_total_revenue.toFixed(2)}%</strong></td>
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

// Start application on DOM ready
document.addEventListener('DOMContentLoaded', initDashboard);
