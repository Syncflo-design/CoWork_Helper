# Ardmore UAT item set (2026-09-22)

100 SKUs, all with image + real retail price + range/colour/design/size data.
Each holds 20 in **POS Store - ACT** and 20 on hand in the **Sage TESTING company**
(`Sage Item Selection`, company = Ardmore Ceramics TEST). Till: **POS_Test2**.
Register of the surrounding blocks: `gotchas/2026-09-22-ardmore-uat-sage-test-lock-register.md`.

To add items later: enable Server Script `uat-push-items-to-sage-test`, call
`uat_push_items_to_sage_test` with `codes` (JSON list) and `qty`, add the same qty
in POS Store - ACT with a Stock Reconciliation, untick *Qty Added Locally (pending
Sage)* on the item, disable the script again.

## Ceramics (37)

NJM465JUL26, SKHU366AUG26, SPN396AUG26, TS492AUG26, YY693AUG25R, MBU542AUG25R,
MF783AUG26, MF784AUG26, NF967AUG26R, NJM470JUL26, NF917JUN26, ABE552JAN24,
AM658JUL25R, AM748AUG26, BN185AUG26, BN187JUL26, BN188JUL26, BN189JUL26,
BN686DEC22, BPN231AUG26, BPN232JUL26, BPN234AUG26, BPN235JUL26, FK179AUG26,
GM148AUG26R, KF407AUG26, KF507AUG26, LD772AUG26, LD774AUG26, MBU658JUL26,
MBU659JUL26, MBU660AUG26, MBU661AUG26, MF782AUG26, MF788AUG26, MF789AUG26R,
MH228AUG26

(The first eleven carry thrower/painter/sculptor names; the rest have type, design,
size and colour.)

## Home (33)

CARBOX7, CUSHCCA60V, CUSHCCB60V, CUSHCCD50, CUSHCCD60V, CUSHCCDE60V, CUSHCCDS,
CUSHCCM60V, CUSHCCS50, CUSHCCS60V, CUSHCCSS, CUSHCKFDS, CUSHCKFM50, CUSHCKFM60V,
CUSHCKFMS, CUSHCKFP50, CUSHCKFP60V, CUSHCKFT50, CUSHCKFTS, CUSHCKG60V, CUSHCKJ60V,
CUSHCKS60V, CUSHCKSN60V, CUSHDEMIS, CUSHDES50, CUSHDES60V, CUSHDESS, CUSHDETL50,
CUSHHGS50, CUSHHGSS, CUSHHGSV, CUSHLLM50, CUSHLLMS

## Fashion (30)

SCAAWC90, SCAAWS90, SCABMO70, SCABP90, SCAPPD90, SCAPPDB135, SCAPPDB90, SCAPPE90,
SCAPPFL90, SCAPPMA90, SCAPPMI135, SCAPPMI90, SCAPPP135, SCAPPP90, SCAPPPA135,
SCAPPPA90, SCAPPS90, SCASKFL70, STCWF165, STCWT165, STPPFL86, STPPJ165, STPPP165,
STPPPA86, STSF86, STST86, SWPPD135, SWPPFL135, SWPPMI135, SWPPS135

## Deliberately excluded

- FABCBBR / FABCBPI / FABCBPU / FABCBTU (Cheri's fabrics): no image; still 249/250 in
  Sage TEST, so flagged *Qty Added Locally* and zeroed in ERPNext.
- RT233JUN26R: already in Sage TEST with an unknown quantity.
- Anything named Test / Nozy / ABC / string / Itm1234TR.
