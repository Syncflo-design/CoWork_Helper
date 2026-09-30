# Web Page has an unused `css` field — restyle an app without touching its HTML or JS

**Date:** 2026-08-26
**Domain:** Frappe v16 (comstruct — the five mobile Web Page apps)
**Severity:** useful (turns a risky rewrite into a one-field write)

## Situation

The five Com-Struct field apps (`/po-request`, `/po-approvals`, `/po-director`,
`/site-stock`, `/van-stock`) are each a single **Web Page** record with the whole app in
`main_section_html` + `javascript`. They used raw emoji as icons (`&#128666;` etc.),
injected as HTML strings from JS.

Swapping those for a real icon set looked like it meant rewriting ~60KB of `javascript`
across five records — the night before a client demo, with the known truncation risk
around pushing large field values (see `2026-05-17-cowork-write-tool-silent-truncation.md`).

## The lever

The **Web Page** doctype has two fields that are almost never used:

| field | type | note |
|---|---|---|
| `insert_style` | Check | gate |
| `css` | Code | `depends_on: insert_style` |

Set `insert_style = 1` and whatever is in `css` is injected into the page head. That is
enough to restyle a page **without touching `main_section_html` or `javascript` at all**.

## What we did

Because every icon was already wrapped in a stable hook — `<span class="ni">` for nav,
`<div class="ei">` for empty states, and nav buttons carry ids like `#nav-transfer` — the
whole icon swap became CSS:

```css
@import url('https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.1/src/regular/style.css');

.ni, .ei { font-size: 0 !important; }              /* hide the emoji text node */
.ni::before { font-family:"Phosphor"!important; font-size:22px }
#nav-transfer .ni::before { content: "\e4b4"; }    /* ph-truck */
#nav-stock    .ni::before { content: "\e1da"; }    /* ph-cube  */
```

`font-size: 0` collapses the emoji glyph; `::before` paints the icon-font glyph in its
place. Specificity note: the page's own `<style>` lives in the body and so normally beats
head CSS at equal specificity — `!important` on the `font-size: 0` is what makes it stick.

Reverting is deleting one field value. No app logic was ever at risk.

## Getting the codepoints right

Do **not** hand-write icon-font codepoints. Download the published stylesheet and parse
them:

```bash
curl -s https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.1/src/regular/style.css -o ph.css
grep -A2 '^\.ph\.ph-truck:before' ph.css
```

Same for verifying a class exists before you rely on it.

## When this does NOT work

CSS can only replace a glyph that sits **alone** in an element. Where the emoji is mixed
into label text — e.g. `<span>&#128193; PROJ-0002</span>` on a request card — hiding the
font-size hides the label too. Those still need a real source edit.

## Rule of thumb

Before rewriting a Frappe Web Page app to restyle it, check whether the change can be
expressed as CSS against existing classes/ids and pushed into `css` + `insert_style`.
Additive, reversible, and it leaves the JS untouched.
