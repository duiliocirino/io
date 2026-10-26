# IO HTML design system

A shared design system keeps long-form references and presentations visually related while giving each format the layout it needs. The direction is **quiet editorial**: engaging through clear hierarchy and useful visual structure rather than decoration.

## Visual foundations

- **Palette:** paper, ink, one structural accent, and soft neutral surfaces. Two [design versions](#design-versions) share everything else: orange (v1) and green with citron highlights (v2).
- **Typography:** serif display headings; sans-serif reading text; monospace code, metadata, and slide labels.
- **Layout:** generous but purposeful spacing, readable line lengths, fine rules, and restrained borders.
- **Accessibility:** semantic headings, visible keyboard focus, skip links in templates, responsive layouts, and print styles for reading pages.
- **No dependencies:** styles use system font stacks and local CSS; no external font or JavaScript library is required.

The shared tokens are defined at the top of [`assets/io-design-system.css`](assets/io-design-system.css). Adjust those variables to tune the visual identity once for every format. The base layer of that file (box sizing, body typography, links, highlights, focus, skip link) applies to all three: `.io-document`, `.io-deck`, and `.io-social`.

## Design versions

Both versions use the same layouts, typography, and token names. Each page chooses one version on its `<html>` element.

| Version | Look | Use |
|---|---|---|
| **v1** (default) | Warm paper, warm charcoal ink, orange accents (`#e65000`; `#b53c00` for small text). | No attribute needed. The io repository tags this state as `design-v1`. |
| **v2** | Cleaner off-white paper, green-black ink, green structure (`#3b8a2c`; `#2a6420` for small text), citron highlights (`#e8f2a2`), points as the signature element, and dark covers with bright yellow (`#fde047`). | Load [`assets/io-theme-v2.css`](assets/io-theme-v2.css) after every other `io-*` stylesheet and add `data-io-theme="v2"` to `<html>`. |

To return a page to v1, remove `data-io-theme="v2"`. The v2 stylesheet has no effect without that attribute.

**Color roles in v2.**

- **Green is structure:** links, labels, rules, bars, points, focus outlines, and key figures. Large figures use the deep green, without a stroke or fill.
- **Citron is the highlighter on light paper:** `<mark>`, the current section or slide, and, in a paler tone, callouts. It is always a background behind dark ink.
- **Bright yellow appears only on the dark cover,** where it is readable. On light paper it would have about 1.2:1 contrast.

Color is never the only carrier of meaning.

**Signature details:**

- **Highlights:** `<mark>` fills the line with a soft citron tone. Use a few per document and no more than one per slide or card; if everything is highlighted, nothing stands out.
- **Points:** a point on a line, like a data point on an axis. The mark at the top of each slide or card is a short line ending in a point. Column rules on slides and social cards start with a point. In documents, section labels and list markers use points. Points are decorative only.
- **Covers:** the slide or card that contains the `h1` is inverted to a dark green-black. The theme remaps tokens on that element, so components inside need no extra rules. Labels become light green, and the highlight and point become bright yellow.
- **Optional dot field:** add `dot-field` to a cover slide or card, for example `<section class="slide dot-field">`. Dots gather in the top-right corner and fade out before the title and footer. Use it for covers that need more presence; the social template uses it, while deck covers stay plain. It has no effect in v1.

**Templates** start in v2 and include a small v1/v2 switch ([`assets/io-theme-switch.js`](assets/io-theme-switch.js)) for comparison. The choice is not saved. Remove the switch markup and script from finished pages.

**Extending the system.** Keep every color a token, or derive it from one with `color-mix()`, so both versions update automatically. Put a v2-only adjustment in `io-theme-v2.css` as `[data-io-theme="v2"]` plus the v1 selector it adjusts. This wins by specificity and leaves v1 unchanged. Re-check contrast on paper, muted surfaces, callouts, and dark covers.

## Three formats, one identity

### Long-form documents

Start with [`templates/document.html`](templates/document.html). The **Guided Editorial** pattern uses:

- a clear title and short framing introduction;
- a table of contents for substantial documents;
- numbered or labeled sections with descriptive headings;
- callouts for genuinely important ideas;
- tables, cards, and code blocks only when they help explain the material.

Keep paragraphs focused and use headings to make the argument easy to scan. Avoid turning every content block into a card.

### Research-document refinements

[`research/emotions-research-document.html`](research/emotions-research-document.html) is the complete long-form research example. It loads [`assets/io-research.css`](assets/io-research.css) **after** the shared stylesheet and adds `io-research` to the body. The overrides are opt-in; other documents and slide decks are unchanged.

- **Index:** a sticky, ordered reading rail above 1100 px; an in-flow, collapsible contents panel on smaller screens. Native anchors and `details` work without JavaScript. The optional [`assets/io-research.js`](assets/io-research.js) marks the section currently being read with `aria-current="location"`.
- **Formulas:** native MathML renders subscripts, sums, exponents, and fractions offline in current Chrome, Firefox, and Safari. Write notation as `<math>` markup, not raw `$…$` LaTeX; there is no TeX renderer. Display equations use a numbered `figure`, a keyboard-scrollable `.equation-scroll` region, and an optional `.symbol-key` definition list.
- **Reference material:** captioned, keyboard-scrollable tables; a collapsible JSON schema (expanded initially); numbered bibliography entries with linked DOIs. Print styles remove the rail and show the complete schema in browsers supporting `::details-content`.

To review changes, open the document directly in a browser. Check the contents links, current-section marker, contents/schema disclosure controls, and formulas at desktop and narrow phone widths. Wide tables and equations should scroll within their own regions, never widen the page. Also check print preview. The selected-source expansion covers SST follow-ups, neural and cross-linguistic evidence, commercial expression measurement, and representation choices. Counts retain their task and sample context; the bibliography distinguishes academic sources from vendor documentation. This is not an exhaustive literature review or a claim that 27 controls form a universal biological standard.

### Hybrid slide presentations

Start with [`templates/slides.html`](templates/slides.html). The same style is adapted into widescreen slides on desktop and vertically scrollable sections on small screens. Native links provide slide navigation; browser scrolling and keyboard controls work without custom JavaScript.

Use one main idea per slide. Vary the layout when it helps explain the material, but keep the type, palette, and footer details consistent. Avoid automatic animation and decorative effects that compete with the content.

The enhanced ten-slide [`research/emotions-presentation-deck.html`](research/emotions-presentation-deck.html) opts into [`assets/io-presentation.css`](assets/io-presentation.css) and [`assets/io-presentation.js`](assets/io-presentation.js) with the `io-presentation` body class. These additions do not change the basic template or the research document.

- **Layout:** desktop slides prefer 16:9 and size against both viewport axes, with content allowed to grow rather than clip in unusually short windows. Typography and spacing scale with the slide's content width through container-query units; below 900 px, slides become naturally growing reading sections. Comparison columns, a category overview, and illustrative activation bars provide variety without decorative animation.
- **Navigation:** the outline stays expanded on wide screens and becomes a disclosure at 1400 px and below. Keep this CSS breakpoint in sync with the script’s media query. The script adds a current-slide marker/counter, bounded previous/next buttons, and Left/Right, Page Up/Down, Home, and End shortcuts. Editing fields, links, disclosures, and focus inside equation or table scrolling regions keep their native keyboard behavior. Native fragment navigation focuses each destination slide without adding extra Tab stops. Slide fragments are authoritative across reload and back/forward navigation rather than restoring an unrelated scroll offset. With no script, outline links and native scrolling still work; enhancement-only controls stay hidden.
- **Notation:** local MathML typesets constraints, decay, and half-life conversion. A wide equation scrolls in its own keyboard-focusable region on phones. Numerical activation examples and chosen half-lives are explicitly engineering choices, not measured or universal emotional parameters.
- **Print:** the opt-in stylesheet requests 16:9 landscape pages, with one slide per page and no toolbar. Use the browser's CSS page size when exporting; printer settings can override it.

When adding slides, update the outline and static footer counts together; keep each slide's `id` and `aria-labelledby` target unique. Check compact laptop sizes as well as phones, all navigation paths, and print output—not just a large desktop viewport.

### Data and verification primitives

Argument decks often need measured values and claim checks, which the base deck vocabulary does not cover. `assets/io-presentation.css` therefore adds a small set of primitives to the same vocabulary rather than a parallel one. They are scoped to `.io-presentation` and `.io-social`, so a deck and a carousel share one definition and only resize it per format.

- **Quiet statements:** `.point-list` is a left-ruled list for prose-sized claims, used instead of turning every block into a card.
- **Measured bars:** `.metric-layout` places two `.metric-panel` figures side by side; each figure has a `.metric-list` of `label + .metric-track + .metric-value` rows. Bars reuse the activation-bar recipe (`.channel-track` and `.metric-track` share one rule; the fill width comes from `--bar-width`), so a slide can mix designed channels and measured values without visual drift. Always name the scale in the `figcaption` and use the same scale for every bar in the panel; `.metric-benchmark` marks a reference value with the lighter accent line rather than a new colour.
- **Verification table:** `.claim-table` is the reading-document table recipe in the shape already used by wide equations — a figure with a label, a keyboard-focusable `.table-scroll` region, and a `.table-hint` that appears only at 600 px and below and never in print. Keep tables to the claims that change the argument; put the nuance in the cells, not in extra slides.
- **Verdicts:** `.verdict` (plus `.verdict-partial` and `.verdict-refuted`) are monospace chips. The wording always carries the meaning, and the three fills (accent wash, neutral, solid ink) only reinforce it, so the table survives greyscale printing.
- **Comparison columns:** `.contrast-grid` is the two-column `framework-grid` variant for side-by-side alternatives.

When checking these additions, verify the same things as for any deck: bars against their declared axis, the table reachable by keyboard and scrollable on a phone without widening the page, and verdict chips legible in a black-and-white print preview.

### Comparison diagrams

The routing research document and deck, and the memory research document, share the opt-in [`assets/io-diagrams.css`](assets/io-diagrams.css). Load it after the format stylesheet and before the theme. The memory document uses it for the fast/slow complementary-learning comparison. A `.io-diagram` figure contains a named `figcaption`, a `.diagram-comparison` grid, and `.diagram-route` rows made of `.diagram-node` labels and a `.diagram-connector`. Use `role="img"` with an explicit accessible label on a symbolic connector. The grid stacks on phones; print keeps the figure together.

State the relationship and evidence status in the caption: a double arrow might summarize functional coupling, not anatomical wiring, causal direction, or a measured connection strength. Keep labels meaningful without colour or CSS. This is a reusable comparison primitive, not a brain-diagram or simulation engine.

### Social carousels

Start with [`templates/social.html`](templates/social.html). A carousel post is a sequence of single images, so `assets/io-social.css` trades the deck's fluid slides for an **exact canvas**: each `.card` is 1080 × 1350 CSS px (4:5). Add `io-social` to the body and load the sheets in this order — `io-design-system.css`, `io-presentation.css`, `io-social.css` — because the presentation sheet now carries the shared data components, scoped with `:is(.io-presentation, .io-social)`.

- **Fixed canvas:** canvas-level metrics (padding, the graphic rule) are px, because an element cannot query itself; content inside a card uses container-query units against the card's constant 908 × 1116 content box. Nothing in a card may be smaller than 24 px, which is why mono labels start at 2.7cqw. If the text does not fit, cut the text.
- **One idea per card:** the number of cards follows the argument, not a template. Reference arc: hook → statements → evidence (facts or bars) → contrast → verification → summary/CTA. Each card must read on its own, since a reshared card arrives without its neighbours: no "this", "as we saw", no orphan pronouns.
- **Platform safety:** the bottom padding is the largest one (108 px) because the app overlays its progress marks on the lower edge; `body[data-safe-areas]` draws the dashed square that the profile crop applies to the cover card, so a hook survives being shown at 1:1.
- **Text outside the image:** links and sources cannot live in a card. Every card carries its own `data-alt`, and the post text, the source list and the ALT list sit in `.social-caption`, below the cards and excluded from every export. The caption stays under ~2.200 characters and each ALT under ~1.250.
- **Export:** set a 1080 × 1350 viewport, jump to `#card-N`, take a **viewport** screenshot. The format supports this by having a non-sticky toolbar, `scroll-margin-top: 0`, no inline padding around the cards, and hidden scrollbars (`html:has(body.io-social)`), so the frame is exactly one card — verified by pixel probes: identity rule at (100, 2) in v1, or the line of the v2 point mark at (100, 49), card rule colour on both side edges, paper above the bottom edge. Two traps found while verifying: screenshots of *elements* outside the viewport come out identical to each other (blank), and a cached stylesheet silently reverts the canvas to `scroll-margin-top: 5rem`, so bump a `?v=N` query when re-exporting.
- **Print:** one 4:5 page per card. Headless `printToPDF` here ignores `@page size`, so the screenshot route is the reliable export; a desktop browser print dialog that honours the CSS page size gives the same layout.

## Using the shared stylesheet

Templates link to `../assets/io-design-system.css`, which is correct for files inside `docs/templates/`. For a document stored elsewhere, update the relative path to the stylesheet. Load order is: shared stylesheet, format stylesheets (`io-research.css`, `io-presentation.css`, `io-social.css`), then `io-theme-v2.css` when the page uses v2.

Start from a template, keep the shared tokens as the source of truth, and add the opt-in research, presentation, or social styles only when the document needs their layouts. Keep local assets alongside the HTML files when sharing the documents offline.

## Structural checks

Run `python3 -m unittest discover -s tests -v` from the repository root. These dependency-free tests cover research-page markup, local links/assets, accessible label targets, outline/slide counts, and native MathML. They do not replace source checking or desktop/phone, keyboard, visual, and print review in a real browser.
