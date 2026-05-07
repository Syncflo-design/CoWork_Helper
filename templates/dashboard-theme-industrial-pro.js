/* =========================================================
   INDUSTRIAL PRO — Client Script wrapper
   Frappe Insights v3 | Paste into Client Script
   dt: "Insights Dashboard v3"

   HOW TO ADAPT FOR A NEW DASHBOARD
   -----------------------------------
   1. frappe_list "Insights Chart v3" to find chart names
   2. Replace each placeholder below:
        KPI_CHART_1   → first KPI (Indigo — active/operational)
        KPI_CHART_2   → second KPI (Teal — production/progress)
        KPI_CHART_3   → third KPI (Amber — caution/pending)
        KPI_CHART_4   → fourth KPI (Red — critical/alert)
        HERO_CHART    → hero bar or line chart name
        TABLE_1       → first table chart name
        TABLE_2       → second table chart name
   3. Adjust border-top accent colors for tables if desired
   4. Create a new Client Script for the target dashboard
   ========================================================= */

function injectDashboardStyling() {
  const existing = document.getElementById('insights-dashboard-custom-style');
  if (existing) existing.remove();

  const style = document.createElement('style');
  style.id = 'insights-dashboard-custom-style';
  style.textContent = `

    /* === DASHBOARD CANVAS === */
    .insights-dashboard,
    .dashboard-container,
    [class*="dashboard"] > .vue-grid-layout {
      background: #eef1f7 !important;
      padding: 8px !important;
    }

    /* === BASE CARD === */
    .vue-grid-item {
      padding: 6px !important;
    }

    .insights-chart-container,
    .chart-container {
      border-radius: 14px !important;
      background: #ffffff !important;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.07) !important;
      overflow: hidden !important;
      transition: box-shadow 0.25s ease, transform 0.25s ease !important;
    }

    .insights-chart-container:hover,
    .chart-container:hover {
      box-shadow: 0 4px 12px rgba(0,0,0,0.10), 0 8px 28px rgba(0,0,0,0.09) !important;
      transform: translateY(-2px) !important;
    }

    /* === KPI CARD 1 — Indigo === */
    [data-docname="KPI_CHART_1"] .insights-chart-container,
    [data-docname="KPI_CHART_1"] .chart-container {
      background: linear-gradient(140deg, #3f51b5 0%, #1a237e 100%) !important;
      border: none !important;
      box-shadow: 0 4px 20px rgba(63,81,181,0.40) !important;
    }
    [data-docname="KPI_CHART_1"],
    [data-docname="KPI_CHART_1"] span,
    [data-docname="KPI_CHART_1"] div,
    [data-docname="KPI_CHART_1"] p { color: #ffffff !important; }

    /* === KPI CARD 2 — Teal === */
    [data-docname="KPI_CHART_2"] .insights-chart-container,
    [data-docname="KPI_CHART_2"] .chart-container {
      background: linear-gradient(140deg, #00897b 0%, #004d40 100%) !important;
      border: none !important;
      box-shadow: 0 4px 20px rgba(0,137,123,0.40) !important;
    }
    [data-docname="KPI_CHART_2"],
    [data-docname="KPI_CHART_2"] span,
    [data-docname="KPI_CHART_2"] div,
    [data-docname="KPI_CHART_2"] p { color: #ffffff !important; }

    /* === KPI CARD 3 — Amber/Orange === */
    [data-docname="KPI_CHART_3"] .insights-chart-container,
    [data-docname="KPI_CHART_3"] .chart-container {
      background: linear-gradient(140deg, #fb8c00 0%, #bf360c 100%) !important;
      border: none !important;
      box-shadow: 0 4px 20px rgba(251,140,0,0.40) !important;
    }
    [data-docname="KPI_CHART_3"],
    [data-docname="KPI_CHART_3"] span,
    [data-docname="KPI_CHART_3"] div,
    [data-docname="KPI_CHART_3"] p { color: #ffffff !important; }

    /* === KPI CARD 4 — Red === */
    [data-docname="KPI_CHART_4"] .insights-chart-container,
    [data-docname="KPI_CHART_4"] .chart-container {
      background: linear-gradient(140deg, #e53935 0%, #7f0000 100%) !important;
      border: none !important;
      box-shadow: 0 4px 20px rgba(229,57,53,0.40) !important;
    }
    [data-docname="KPI_CHART_4"],
    [data-docname="KPI_CHART_4"] span,
    [data-docname="KPI_CHART_4"] div,
    [data-docname="KPI_CHART_4"] p { color: #ffffff !important; }

    /* === HERO CHART === */
    [data-docname="HERO_CHART"] .insights-chart-container,
    [data-docname="HERO_CHART"] .chart-container {
      background: #ffffff !important;
      border-radius: 16px !important;
      border-top: 5px solid #3f51b5 !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 6px 24px rgba(63,81,181,0.10) !important;
    }

    /* === TABLE 1 — Teal accent === */
    [data-docname="TABLE_1"] .insights-chart-container,
    [data-docname="TABLE_1"] .chart-container {
      background: #ffffff !important;
      border-radius: 14px !important;
      border-top: 5px solid #00897b !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 6px 24px rgba(0,137,123,0.10) !important;
    }

    /* === TABLE 2 — Indigo accent === */
    [data-docname="TABLE_2"] .insights-chart-container,
    [data-docname="TABLE_2"] .chart-container {
      background: #ffffff !important;
      border-radius: 14px !important;
      border-top: 5px solid #3f51b5 !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 6px 24px rgba(63,81,181,0.10) !important;
    }

    /* === TABLE HEADERS === */
    .insights-table thead tr,
    .datatable thead tr,
    table thead tr {
      background: linear-gradient(90deg, #f5f6fa 0%, #eef1f7 100%) !important;
    }
    .insights-table thead th,
    .datatable thead th,
    table thead th {
      color: #37474f !important;
      font-weight: 700 !important;
      font-size: 11px !important;
      text-transform: uppercase !important;
      letter-spacing: 0.07em !important;
      border-bottom: 2px solid #e3e6ef !important;
      padding: 10px 14px !important;
    }

    /* === TABLE ROWS === */
    .insights-table tbody tr:nth-child(even),
    .datatable tbody tr:nth-child(even),
    table tbody tr:nth-child(even) {
      background: #f9fafb !important;
    }
    .insights-table tbody tr:hover,
    .datatable tbody tr:hover,
    table tbody tr:hover {
      background: #e8eeff !important;
    }
    .insights-table tbody td,
    .datatable tbody td,
    table tbody td {
      border-bottom: 1px solid #f0f2f7 !important;
      padding: 8px 14px !important;
      font-size: 13px !important;
      color: #2c3e50 !important;
    }

    /* === NEGATIVE VALUE HIGHLIGHT (applied by JS below) === */
    td.negative-value {
      background: #fff0f0 !important;
      color: #c62828 !important;
      font-weight: 600 !important;
    }

  `;

  document.head.appendChild(style);

  // Auto-highlight negative numeric cells in tables
  function highlightNegatives() {
    document.querySelectorAll('table tbody td').forEach(function(td) {
      const val = parseFloat(td.textContent.trim().replace(/,/g, ''));
      if (!isNaN(val) && val < 0) {
        td.classList.add('negative-value');
      }
    });
  }

  setTimeout(highlightNegatives, 800);
  setTimeout(highlightNegatives, 2000);
}

// Fire on load + after chart render delays
injectDashboardStyling();
setTimeout(injectDashboardStyling, 100);
setTimeout(injectDashboardStyling, 500);
setTimeout(injectDashboardStyling, 1500);

// Debounced re-apply on dynamic DOM changes
if (typeof MutationObserver !== 'undefined') {
  const observer = new MutationObserver(function() {
    clearTimeout(window._insightStyleTimer);
    window._insightStyleTimer = setTimeout(injectDashboardStyling, 200);
  });
  observer.observe(document.body, { childList: true, subtree: true });
}
