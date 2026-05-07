// ==UserScript==
// @name         Blomoplastics — Insights Dashboard Theme
// @namespace    blomoplastics.insights
// @version      2.0
// @description  Industrial Pro theme for all Frappe Insights v3 dashboards on blomoplastics
// @author       Russell / Claude
// @match        https://blomoplastics.jh.frappe.cloud/insights/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

/*
  HOW THIS WORKS
  --------------
  Frappe Insights v3 is a standalone Vue SPA — Frappe Client Scripts and
  Website Settings head_html do NOT reach it. Tampermonkey injects this
  script on every matching page load, which is the only reliable mechanism.

  LAYOUT ASSUMPTION (all 3 planned dashboards use this same layout):
    nth-child(1-4) : KPI cards
    nth-child(5)   : hero bar/line chart
    nth-child(6-7) : detail tables

  If a dashboard has a different layout, update the nth-child selectors
  in the relevant section below.

  TO ADAPT FOR A NEW SITE
  -----------------------
  Duplicate this file, change @match to the new site URL, done.
  The selectors are layout-positional, not dashboard-specific, so one
  script covers all dashboards on a site with the same card layout.
*/

(function () {
  'use strict';

  const CSS = `
    /* =====================================================
       BLOMOPLASTICS — INDUSTRIAL PRO THEME v2
       Verified selectors: 2026-05-06
       DOM structure: .vgl-layout > .vgl-item:nth-child(N)
       Card element: [class*="rounded"][class*="bg-white"][class*="shadow"]
       Table card  : [class*="divide-y"][class*="bg-white"][class*="shadow"]
       ===================================================== */

    /* === DASHBOARD CANVAS === */
    .vgl-layout {
      background: #eef1f7 !important;
      padding: 8px !important;
    }

    /* === KPI 1 — Indigo (Active / Operational) === */
    .vgl-item:nth-child(1) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      background: linear-gradient(140deg, #3f51b5 0%, #1a237e 100%) !important;
      box-shadow: 0 4px 20px rgba(63,81,181,0.45) !important;
      border-radius: 14px !important;
      transition: transform 0.2s ease !important;
    }
    .vgl-item:nth-child(1) [class*="rounded"][class*="bg-white"][class*="shadow"]:hover {
      transform: translateY(-2px) !important;
    }
    .vgl-item:nth-child(1) [class*="rounded"][class*="bg-white"][class*="shadow"] span,
    .vgl-item:nth-child(1) [class*="rounded"][class*="bg-white"][class*="shadow"] div {
      color: #ffffff !important;
    }

    /* === KPI 2 — Teal (Production / Progress) === */
    .vgl-item:nth-child(2) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      background: linear-gradient(140deg, #00897b 0%, #004d40 100%) !important;
      box-shadow: 0 4px 20px rgba(0,137,123,0.45) !important;
      border-radius: 14px !important;
      transition: transform 0.2s ease !important;
    }
    .vgl-item:nth-child(2) [class*="rounded"][class*="bg-white"][class*="shadow"]:hover {
      transform: translateY(-2px) !important;
    }
    .vgl-item:nth-child(2) [class*="rounded"][class*="bg-white"][class*="shadow"] span,
    .vgl-item:nth-child(2) [class*="rounded"][class*="bg-white"][class*="shadow"] div {
      color: #ffffff !important;
    }

    /* === KPI 3 — Amber/Orange (Caution / Pending) === */
    .vgl-item:nth-child(3) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      background: linear-gradient(140deg, #fb8c00 0%, #bf360c 100%) !important;
      box-shadow: 0 4px 20px rgba(251,140,0,0.45) !important;
      border-radius: 14px !important;
      transition: transform 0.2s ease !important;
    }
    .vgl-item:nth-child(3) [class*="rounded"][class*="bg-white"][class*="shadow"]:hover {
      transform: translateY(-2px) !important;
    }
    .vgl-item:nth-child(3) [class*="rounded"][class*="bg-white"][class*="shadow"] span,
    .vgl-item:nth-child(3) [class*="rounded"][class*="bg-white"][class*="shadow"] div {
      color: #ffffff !important;
    }

    /* === KPI 4 — Red (Critical / Alert) === */
    .vgl-item:nth-child(4) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      background: linear-gradient(140deg, #e53935 0%, #7f0000 100%) !important;
      box-shadow: 0 4px 20px rgba(229,57,53,0.45) !important;
      border-radius: 14px !important;
      transition: transform 0.2s ease !important;
    }
    .vgl-item:nth-child(4) [class*="rounded"][class*="bg-white"][class*="shadow"]:hover {
      transform: translateY(-2px) !important;
    }
    .vgl-item:nth-child(4) [class*="rounded"][class*="bg-white"][class*="shadow"] span,
    .vgl-item:nth-child(4) [class*="rounded"][class*="bg-white"][class*="shadow"] div {
      color: #ffffff !important;
    }

    /* === HERO CHART (position 5) — white card + indigo top border === */
    .vgl-item:nth-child(5) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      border-top: 5px solid #3f51b5 !important;
      box-shadow: 0 2px 10px rgba(63,81,181,0.15) !important;
      border-radius: 14px !important;
    }

    /* === TABLE 1 (position 6) — teal accent === */
    .vgl-item:nth-child(6) [class*="divide-y"][class*="bg-white"][class*="shadow"] {
      border-top: 5px solid #00897b !important;
      box-shadow: 0 2px 10px rgba(0,137,123,0.15) !important;
      border-radius: 14px !important;
      overflow: hidden !important;
    }

    /* === TABLE 2 (position 7) — indigo accent === */
    .vgl-item:nth-child(7) [class*="divide-y"][class*="bg-white"][class*="shadow"] {
      border-top: 5px solid #3f51b5 !important;
      box-shadow: 0 2px 10px rgba(63,81,181,0.15) !important;
      border-radius: 14px !important;
      overflow: hidden !important;
    }

    /* === TABLE HEADERS === */
    thead.sticky {
      background: linear-gradient(90deg, #f5f6fa, #eef1f7) !important;
    }
    thead.sticky td {
      font-weight: 700 !important;
      font-size: 11px !important;
      text-transform: uppercase !important;
      letter-spacing: 0.06em !important;
      color: #37474f !important;
    }

    /* === TABLE ROW HOVER === */
    tbody tr:hover td {
      background: #e8eeff !important;
    }
  `;

  function injectTheme() {
    if (document.getElementById('insights-industrial-pro')) return;
    const style = document.createElement('style');
    style.id = 'insights-industrial-pro';
    style.textContent = CSS;
    (document.head || document.documentElement).appendChild(style);
  }

  // Inject immediately (document-start) and after Vue renders
  injectTheme();
  document.addEventListener('DOMContentLoaded', injectTheme);

  // Re-inject on Vue route changes (SPA navigation reuses the DOM)
  const observer = new MutationObserver(injectTheme);
  document.addEventListener('DOMContentLoaded', () => {
    observer.observe(document.body, { childList: true, subtree: false });
  });

})();
