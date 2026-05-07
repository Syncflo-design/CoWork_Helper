// ==UserScript==
// @name         Frappe Insights — Soft Professional Theme (All Sites) [FALLBACK]
// @namespace    frappe.insights.theme
// @version      4.0
// @description  [SUPERSEDED — kept as fallback] Applies a muted, professional colour theme
//               to all Frappe Insights v3 dashboards. As of 2026-05-06 the same theme is
//               deployed server-side on blomoplastics.jh.frappe.cloud via the custom
//               Insights fork (Syncflo-design/insights:syncflo-custom-theme). This userscript
//               should be DISABLED in Tampermonkey while the fork is live — its !important
//               rules layer on top of the server CSS and can mask future server-side tweaks.
//               Re-enable only if you need to test theme changes locally before pushing to
//               the fork, or if the fork is reverted. See playbooks/insights-fork-themeing.md.
// @author       Russell / Claude
// @match        https://*.jh.frappe.cloud/insights/*
// @match        https://*.frappe.cloud/insights/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

/*
  HOW TO ADD A NEW SITE
    1. Copy one of the existing SITE_THEMES entries below
    2. Change the key to the new site hostname
    3. Pick colours that suit that site
    4. Save the file — Tampermonkey picks up changes automatically

  HOW TO ADD A PER-DASHBOARD OVERRIDE
    Add a `dashboards` key inside a site entry. The key is the dashboard
    ID from the URL (e.g. "2uljes564g" from /insights/dashboards/2uljes564g).

  CSS SELECTORS (verified against live Insights v3 DOM)
    Grid container : .vgl-layout
    Each tile      : .vgl-item:nth-child(N)
    KPI card       : [class*="rounded"][class*="bg-white"][class*="shadow"]
    Table card     : [class*="divide-y"][class*="bg-white"][class*="shadow"]
    Table header   : thead.sticky td
*/

// ============================================================
//  SITE COLOUR CONFIG
// ============================================================
const SITE_THEMES = {

  // --- Blomoplastics: Manufacturing Ops — Soft Professional ---
  'blomoplastics.jh.frappe.cloud': {
    bg: '#f5f6f8',
    kpi: [
      { from: '#6b85a3', to: '#4a6580', shadow: 'rgba(107,133,163,0.30)' },
      { from: '#82a085', to: '#5d7a60', shadow: 'rgba(130,160,133,0.30)' },
      { from: '#c4a373', to: '#99794d', shadow: 'rgba(196,163,115,0.30)' },
      { from: '#b07e7e', to: '#855555', shadow: 'rgba(176,126,126,0.30)' },
    ],
    heroAccent:   '#6b85a3',
    tableAccents: ['#82a085', '#6b85a3'],
    dashboards: {
      // MD Overview — Soft Executive palette
      '2uljes564g': {
        bg: '#f4f5f9',
        kpi: [
          { from: '#5e85a8', to: '#3f6182', shadow: 'rgba(94,133,168,0.30)'  },
          { from: '#7a9c7d', to: '#557556', shadow: 'rgba(122,156,125,0.30)' },
          { from: '#8b7991', to: '#614f68', shadow: 'rgba(139,121,145,0.30)' },
          { from: '#b08c75', to: '#836552', shadow: 'rgba(176,140,117,0.30)' },
        ],
        heroAccent:   '#5e85a8',
        tableAccents: ['#7a9c7d', '#5e85a8'],
      },
    },
  },

  // --- Add other sites here ---

};

// ============================================================
//  CSS BUILDER
// ============================================================
function buildCSS(theme) {
  const { bg, kpi, heroAccent, tableAccents } = theme;

  const kpiBlocks = kpi.map((c, i) => {
    const n = i + 1;
    return `
    .vgl-item:nth-child(${n}) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      background: linear-gradient(140deg, ${c.from} 0%, ${c.to} 100%) !important;
      box-shadow: 0 4px 20px ${c.shadow} !important;
      border-radius: 14px !important;
      transition: transform 0.2s ease !important;
    }
    .vgl-item:nth-child(${n}) [class*="rounded"][class*="bg-white"][class*="shadow"]:hover {
      transform: translateY(-2px) !important;
    }
    .vgl-item:nth-child(${n}) [class*="rounded"][class*="bg-white"][class*="shadow"] span,
    .vgl-item:nth-child(${n}) [class*="rounded"][class*="bg-white"][class*="shadow"] div {
      color: #ffffff !important;
    }`;
  }).join('\n');

  const heroBlock = `
    .vgl-item:nth-child(${kpi.length + 1}) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      border-top: 5px solid ${heroAccent} !important;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important;
      border-radius: 14px !important;
    }`;

  const tableBlocks = tableAccents.map((colour, i) => {
    const n = kpi.length + 2 + i;
    return `
    .vgl-item:nth-child(${n}) [class*="divide-y"][class*="bg-white"][class*="shadow"],
    .vgl-item:nth-child(${n}) [class*="rounded"][class*="bg-white"][class*="shadow"] {
      border-top: 5px solid ${colour} !important;
      box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important;
      border-radius: 14px !important;
      overflow: hidden !important;
    }`;
  }).join('\n');

  return `
    /* === Insights Soft Professional Theme === */
    .vgl-layout { background: ${bg} !important; padding: 8px !important; }
    ${kpiBlocks}
    ${heroBlock}
    ${tableBlocks}
    thead.sticky { background: linear-gradient(90deg, #f5f6fa, #eef1f7) !important; }
    thead.sticky td {
      font-weight: 700 !important; font-size: 11px !important;
      text-transform: uppercase !important; letter-spacing: 0.06em !important;
      color: #37474f !important;
    }
    tbody tr:hover td { background: #eef2f6 !important; }
  `;
}

// ============================================================
//  THEME RESOLVER
// ============================================================
function getTheme() {
  const siteTheme = SITE_THEMES[window.location.hostname];
  if (!siteTheme) return null;
  if (siteTheme.dashboards) {
    const match = window.location.pathname.match(/dashboards\/([^\/]+)/);
    const dashId = match && match[1];
    if (dashId && siteTheme.dashboards[dashId]) {
      return Object.assign({}, siteTheme, siteTheme.dashboards[dashId]);
    }
  }
  return siteTheme;
}

// ============================================================
//  CHART PALETTE RECOLOURER
//  Walks SVG fills inside each .vgl-item and remaps the chart
//  library's default series colours to the site's soft palette.
//  Idempotent — fills already in the palette are skipped.
// ============================================================

const CHART_PALETTE_EXTRAS = [
  '#a08570', '#9a8588', '#7a9c7d', '#85a0a8', '#9a7878', '#aa9c80'
];

function getChartPalette(theme) {
  const kpi = (theme.kpi || []).map(c => c.from);
  return kpi.concat(CHART_PALETTE_EXTRAS);
}

function isNeutralFill(value) {
  if (!value || value === 'none' || value === 'transparent') return true;
  const v = String(value).toLowerCase().trim();
  if (v.indexOf('url(') === 0) return true;
  if (v === '#fff' || v === '#ffffff' || v === '#000' || v === '#000000') return true;
  let r, g, b;
  let m = v.match(/^#([a-f0-9]{6})$/);
  if (m) {
    r = parseInt(m[1].substr(0, 2), 16);
    g = parseInt(m[1].substr(2, 2), 16);
    b = parseInt(m[1].substr(4, 2), 16);
  } else {
    m = v.match(/^rgba?\(\s*(\d+)[,\s]+(\d+)[,\s]+(\d+)/);
    if (m) { r = +m[1]; g = +m[2]; b = +m[3]; }
    else return false;
  }
  if (Math.max(r, g, b) - Math.min(r, g, b) < 14) return true;
  if (r > 245 && g > 245 && b > 245) return true;
  return false;
}

let activeChartPalette = null;
let paletteSet = new Set();

function recolorChartTile(tile) {
  if (!activeChartPalette) return;
  const elements = tile.querySelectorAll('svg path[fill], svg rect[fill], svg circle[fill], svg polygon[fill]');
  if (elements.length === 0) return;
  const fillMap = new Map();

  elements.forEach(function (el) {
    const f = el.getAttribute('fill');
    if (isNeutralFill(f)) return;
    const key = f.toLowerCase();
    if (paletteSet.has(key)) return;
    if (!fillMap.has(key)) {
      fillMap.set(key, activeChartPalette[fillMap.size % activeChartPalette.length]);
    }
    el.setAttribute('fill', fillMap.get(key));
  });

  tile.querySelectorAll('svg path[stroke], svg line[stroke]').forEach(function (el) {
    const s = el.getAttribute('stroke');
    if (isNeutralFill(s)) return;
    const key = s.toLowerCase();
    if (paletteSet.has(key)) return;
    if (fillMap.has(key)) {
      el.setAttribute('stroke', fillMap.get(key));
    }
  });

  tile.querySelectorAll('[style*="background"]').forEach(function (el) {
    const style = el.getAttribute('style');
    if (!style) return;
    const m = style.match(/background(?:-color)?\s*:\s*(#[a-f0-9]{6}|rgba?\([^)]+\))/i);
    if (m) {
      const key = m[1].toLowerCase();
      if (fillMap.has(key)) {
        el.setAttribute('style', style.replace(m[1], fillMap.get(key)));
      }
    }
  });
}

function recolorAllCharts() {
  document.querySelectorAll('.vgl-item').forEach(recolorChartTile);
}

let recolorTimer = null;
function scheduleRecolor() {
  clearTimeout(recolorTimer);
  recolorTimer = setTimeout(recolorAllCharts, 120);
}

function startChartObserver() {
  const layout = document.querySelector('.vgl-layout');
  if (!layout) {
    setTimeout(startChartObserver, 250);
    return;
  }
  if (window.__insightsChartObserver) {
    window.__insightsChartObserver.disconnect();
  }
  const obs = new MutationObserver(scheduleRecolor);
  obs.observe(layout, { childList: true, subtree: true });
  window.__insightsChartObserver = obs;
  recolorAllCharts();
}

// ============================================================
//  INJECTION
// ============================================================
(function () {
  'use strict';

  let lastPath = null;

  function injectTheme() {
    const currentPath = window.location.pathname;
    if (currentPath === lastPath && document.getElementById('insights-soft-professional')) return;
    lastPath = currentPath;

    const theme = getTheme();
    if (!theme) return;

    const existing = document.getElementById('insights-soft-professional');
    if (existing) existing.remove();

    const css = buildCSS(theme);
    const style = document.createElement('style');
    style.id = 'insights-soft-professional';
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);

    activeChartPalette = getChartPalette(theme);
    paletteSet = new Set(activeChartPalette.map(function (c) { return c.toLowerCase(); }));
    startChartObserver();
  }

  injectTheme();
  document.addEventListener('DOMContentLoaded', injectTheme);

  const observer = new MutationObserver(injectTheme);
  document.addEventListener('DOMContentLoaded', function () {
    if (document.body) observer.observe(document.body, { childList: true, subtree: false });
  });
})();
