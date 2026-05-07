/**
 * Manufacturing Operations Dashboard - Modern Styling Injector
 *
 * Usage:
 * 1. Add this as a custom script to your Frappe site
 * 2. Or paste into browser console when viewing the dashboard
 * 3. The CSS will automatically apply when the dashboard loads
 */

(function() {
  'use strict';

  // Inject the CSS styles
  function injectDashboardCSS() {
    if (document.getElementById('manufacturing-ops-dashboard-styles')) {
      return; // Already injected
    }

    const css = `
      /* Manufacturing Operations Dashboard - Modern Styling */

      /* KPI Cards - Gradient backgrounds */
      [data-chart="3q9k2se8it"] {
        --kpi-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
      }

      [data-chart="4qc7781u5f"] {
        --kpi-bg: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
      }

      [data-chart="3qccii7sev"] {
        --kpi-bg: linear-gradient(135deg, #fa709a 0%, #fee140 100%) !important;
      }

      [data-chart="0qcl33potd"] {
        --kpi-bg: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%) !important;
      }

      /* Number card styling */
      .chart-container .number-card,
      .insight-number-card,
      .echart-container svg ~ div {
        background: white !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        padding: 24px !important;
      }

      .chart-container .number-value,
      .insight-number-card .value {
        font-size: 48px !important;
        font-weight: 700 !important;
        line-height: 1;
        margin-bottom: 8px;
      }

      .chart-container .number-label,
      .insight-number-card .label {
        font-size: 13px !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.8;
      }

      /* Grid item styling */
      .grid-item,
      .grid-stack-item {
        background: white !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        overflow: hidden !important;
      }

      .grid-item:hover,
      .grid-stack-item:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
      }

      /* Dashboard background */
      .dashboard-wrapper,
      .dashboard-container,
      .insights-dashboard {
        background: #f8f9fa !important;
        padding: 24px !important;
      }

      /* Table styling */
      .chart-container table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }

      .chart-container table thead {
        background: linear-gradient(to right, #f5f5f5, #fafafa) !important;
        border-bottom: 2px solid #e0e0e0 !important;
      }

      .chart-container table thead th {
        font-weight: 600 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        color: #666 !important;
        padding: 12px 8px !important;
      }

      .chart-container table tbody tr {
        border-bottom: 1px solid #f0f0f0 !important;
        transition: background-color 0.2s ease;
      }

      .chart-container table tbody tr:hover {
        background-color: #f9f9f9 !important;
      }

      .chart-container table tbody td {
        padding: 10px 8px !important;
      }

      /* Highlight negative values (red background) */
      .chart-container table tbody td[data-value*="-"] {
        background-color: #ffe5e5 !important;
        color: #d32f2f !important;
        font-weight: 600;
        border-radius: 4px;
        padding: 6px 8px !important;
      }

      /* Chart title styling */
      .chart-container .chart-title,
      .echart-title {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
        margin-bottom: 16px !important;
      }

      /* Typography */
      .chart-container,
      .grid-item,
      .dashboard-item {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
      }

      /* Bar chart improvements */
      .chart-container .recharts-bar {
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.05));
      }

      /* Subtle gridlines */
      .chart-container .recharts-cartesian-axis-line {
        stroke: #e8e8e8 !important;
        stroke-width: 1 !important;
        opacity: 0.6 !important;
      }

      /* Responsive */
      @media (max-width: 768px) {
        .dashboard-wrapper { padding: 12px !important; }
        .grid-item { padding: 16px !important; }
        .chart-container .number-value { font-size: 36px !important; }
      }
    `;

    const style = document.createElement('style');
    style.id = 'manufacturing-ops-dashboard-styles';
    style.textContent = css;
    document.head.appendChild(style);

    console.log('✓ Manufacturing Operations dashboard styling applied');
  }

  // Apply gradient backgrounds to KPI cards
  function applyKPIGradients() {
    const kpiConfig = {
      '3q9k2se8it': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      '4qc7781u5f': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      '3qccii7sev': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      '0qcl33potd': 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)'
    };

    Object.entries(kpiConfig).forEach(([chartId, gradient]) => {
      const elements = document.querySelectorAll(`[data-chart="${chartId}"]`);
      elements.forEach(el => {
        // Find the card container
        const cardContainer = el.querySelector('.chart-container') || el;
        if (cardContainer) {
          cardContainer.style.background = gradient;
          cardContainer.style.color = 'white';
          cardContainer.style.borderRadius = '12px';
          cardContainer.style.padding = '24px';
          cardContainer.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
        }
      });
    });
  }

  // Highlight negative projected_qty values in tables
  function highlightNegativeValues() {
    const tables = document.querySelectorAll('.chart-container table tbody');
    tables.forEach(table => {
      const rows = table.querySelectorAll('tr');
      rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
          const text = cell.textContent.trim();
          // Check if it's a negative number
          if (text.startsWith('-') || text.includes('−')) {
            cell.style.backgroundColor = '#ffe5e5';
            cell.style.color = '#d32f2f';
            cell.style.fontWeight = '600';
            cell.style.borderRadius = '4px';
            cell.style.padding = '6px 8px';
          }
        });
      });
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      injectDashboardCSS();
      applyKPIGradients();
      setTimeout(highlightNegativeValues, 500);
    });
  } else {
    injectDashboardCSS();
    applyKPIGradients();
    highlightNegativeValues();
  }

  // Watch for dynamic updates (Insights may reload charts)
  const observer = new MutationObserver(() => {
    highlightNegativeValues();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: false
  });

  console.log('✓ Dashboard styling system loaded');
})();
