# Frappe 16.56: frappe.get_route() reads empty while a deep link loads

**Symptom:** after updating a bench to Frappe 16.56, every full page load of a desk link
(bookmark, email link, F5) landed on the nest_home landing page. Clicking around inside the
desk was fine. Seen on nesterp and Com-Struct, 2026-11-12.

**Cause:** nest_home_redirect.js treated "frappe.get_route() is empty" as "the user is on the
desk home" and redirected (router change event + 800/2000 ms timers). From 16.56 the route reads
empty for a moment while a deep link settles (16.56 also prefixes routes with the app, e.g.
/desk/projects/query-report/X, /desk/buying/purchase-order). frappe.route_history showed the
real route first, then the redirect. Proof: switching the landing off for one user made the same
link open normally.

**Fix (nest_home 0.0.37):** decide "home" from the address bar - only /desk or /app (trailing
slash stripped) counts. Bare /desk still goes to the landing; deep links are left alone.

**Rule:** never key a redirect off frappe.get_route() during page load; read location.pathname.
The redirect JS is a plain app_include asset (no hash), so browsers need one hard refresh.
