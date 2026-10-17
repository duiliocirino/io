# IO HTML design system

A shared design system keeps long-form references and presentations visually related while giving each format the layout it needs. The direction is **quiet editorial**: engaging through clear hierarchy and useful visual structure rather than decoration.

## Visual foundations

- **Palette:** warm paper, warm charcoal ink, strong orange graphic accents (`#e65000`), and soft neutral surfaces. Small accent text uses a darker orange (`#b53c00`) for contrast; orange-tinted washes are reserved for selected navigation and callouts.
- **Typography:** serif display headings; sans-serif reading text; monospace code, metadata, and slide labels.
- **Layout:** generous but purposeful spacing, readable line lengths, fine rules, and restrained borders.
- **Accessibility:** semantic headings, visible keyboard focus, skip links in templates, responsive layouts, and print styles for reading pages.
- **No dependencies:** styles use system font stacks and local CSS; no external font or JavaScript library is required.

The shared tokens are defined at the top of [`assets/io-design-system.css`](assets/io-design-system.css). Adjust those variables to tune the visual identity once for both formats.

## Two formats, one identity

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
- **Navigation:** the ten-link outline stays expanded on wide screens and becomes a disclosure at 1400 px and below. Keep this CSS breakpoint in sync with the script’s media query. The script adds a current-slide marker/counter, bounded previous/next buttons, and Left/Right, Page Up/Down, Home, and End shortcuts. Editing fields, links, disclosures, and focus inside the equation region keep their native keyboard behavior. Native fragment navigation focuses each destination slide without adding extra Tab stops. Slide fragments are authoritative across reload and back/forward navigation rather than restoring an unrelated scroll offset. With no script, outline links and native scrolling still work; enhancement-only controls stay hidden.
- **Notation:** local MathML typesets constraints, decay, and half-life conversion. A wide equation scrolls in its own keyboard-focusable region on phones. Numerical activation examples and chosen half-lives are explicitly engineering choices, not measured or universal emotional parameters.
- **Print:** the opt-in stylesheet requests 16:9 landscape pages, with one slide per page and no toolbar. Use the browser's CSS page size when exporting; printer settings can override it.

When adding slides, update the outline and static footer counts together; keep each slide's `id` and `aria-labelledby` target unique. Check compact laptop sizes as well as phones, all navigation paths, and print output—not just a large desktop viewport.

## Using the shared stylesheet

Both templates link to `../assets/io-design-system.css`, which is correct for files inside `docs/templates/`. For a document stored elsewhere, update the relative path to the stylesheet.

Start from a template, keep the shared tokens as the source of truth, and add the opt-in research or presentation styles only when the document needs their extra navigation and layouts. Keep local assets alongside the HTML files when sharing the documents offline.
