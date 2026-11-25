# Sage costed opening stock at the selling price (Ardmore, 9 Nov 2026)

**What happened:** Friday 6 Nov's kiln sheet (KSI-00018, 85 items) created items in Sage Ceramics with a quantity on
the create and `LastCost` 0. Sage set the cost from the selling price (retail ex VAT), so average cost and GP% were wrong.

**Going forward:** `post-pending-items-to-sage` creates the item with quantity 0 and sends `LastCost` = Item Cost, then
adds the opening stock by item adjustment at the sheet's Item Cost.

**Correcting an existing item (no Pharoh change):** `post-item-adjustment-to-sage` twice, in this order:

1. OUT: `quantity` = minus Sage's full quantity, `averageCost` = Sage's current average cost.
2. IN: the same quantity as a positive, `averageCost` = the correct cost.

**Proven live on Sage Ceramics, 9 Nov 2026 (83 items):**

- A negative `Quantity` is accepted as a reduction. Sage's API docs don't say so.
- Average cost changes immediately on the IN. Russell confirmed the adjustment journals are correct.
- `LastCost` does not change and can't be set; Sage maintains it itself.
- An item sits at 0 for about 3 seconds. The 5-minute stock sync ran during the job and caught nothing.

**Running it:** a temporary API Server Script, 10 items per call (about 35 seconds). Adjustments carry the reason
"Kiln sheet cost correction - out" / "- in", so they can be found in Sage. Disabled scripts left on the site:
`tmp-cost-fix-test`, `tmp-cost-fix-sheet`.
