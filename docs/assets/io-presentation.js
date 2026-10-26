/**
 * Progressive enhancement for the opt-in presentation deck.
 * Native outline links remain usable without this script. No animation or
 * third-party presentation runtime is needed for navigation and progress.
 */
(() => {
  const slides = [...document.querySelectorAll(".io-presentation .slide")];
  const links = [...document.querySelectorAll(".io-presentation .deck-nav a")];
  const toolbar = document.querySelector(".io-presentation .deck-toolbar");
  const controls = document.querySelector(".deck-controls");
  const previous = document.querySelector("[data-deck-previous]");
  const next = document.querySelector("[data-deck-next]");
  const position = document.querySelector(".deck-position");
  const outline = document.querySelector(".deck-outline");
  if (!slides.length || links.length !== slides.length || !toolbar || !position ||
      !(controls instanceof HTMLElement) || !(previous instanceof HTMLButtonElement) ||
      !(next instanceof HTMLButtonElement) || !(outline instanceof HTMLDetailsElement)) return;

  const compact = window.matchMedia("(max-width: 1400px)");
  // A deck fragment is the navigation state. Do not restore an unrelated saved
  // scroll offset over it when reloading or traversing browser history.
  window.history.scrollRestoration = "manual";
  let current = -1;
  let scheduled = false;

  /** @param {number} index - Zero-based slide index. */
  const markCurrent = (index) => {
    if (index === current) return;
    current = index;
    links.forEach((link, linkIndex) => {
      if (linkIndex === index) link.setAttribute("aria-current", "step");
      else link.removeAttribute("aria-current");
    });
    position.textContent = `${String(index + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}`;
    previous.disabled = index === 0;
    next.disabled = index === slides.length - 1;
  };

  const update = () => {
    const top = toolbar.getBoundingClientRect().bottom;
    let bestIndex = 0;
    let mostVisible = 0;
    slides.forEach((slide, index) => {
      const rect = slide.getBoundingClientRect();
      const visible = Math.max(0, Math.min(rect.bottom, window.innerHeight) - Math.max(rect.top, top));
      if (visible > mostVisible) {
        mostVisible = visible;
        bestIndex = index;
      }
    });
    markCurrent(bestIndex);
    scheduled = false;
  };

  const scheduleUpdate = () => {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(update);
  };

  const alignFragment = () => {
    const target = slides.find((slide) => `#${slide.id}` === window.location.hash);
    // Keep a slide URL tied to its visible destination, including on reload
    // and history traversal. Ordinary reader scrolling does not change the URL.
    target?.scrollIntoView({ block: "start", behavior: "instant" });
    scheduleUpdate();
  };

  /** @param {number} index - Target slide; out-of-range navigation is ignored. */
  const goTo = (index) => {
    if (index < 0 || index >= slides.length) return;
    if (compact.matches) outline.open = false;
    // Use the same fragment navigation as native links, preserving back/forward.
    window.location.hash = slides[index].id;
    alignFragment();
  };

  previous.addEventListener("click", () => goTo(current - 1));
  next.addEventListener("click", () => goTo(current + 1));
  links.forEach((link) => {
    link.addEventListener("click", () => {
      // Native fragment navigation focuses the destination slide (tabindex=-1),
      // rather than leaving keyboard focus inside the now-hidden outline.
      if (compact.matches) outline.open = false;
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    // Preserve editing, native disclosure/link behavior, and local equation or
    // table scrolling. Up/down and Space remain ordinary browser scrolling.
    if (event.target instanceof Element && event.target.closest(
      "a, summary, input, select, textarea, [contenteditable], .equation-scroll, .table-scroll"
    )) return;
    /** @type {Record<string, number>} */
    const targets = {
      ArrowLeft: current - 1,
      ArrowRight: current + 1,
      PageUp: current - 1,
      PageDown: current + 1,
      Home: 0,
      End: slides.length - 1,
    };
    if (!Object.hasOwn(targets, event.key)) return;
    event.preventDefault();
    goTo(targets[event.key]);
  });

  const adaptOutline = () => {
    outline.open = !compact.matches;
    scheduleUpdate();
  };
  compact.addEventListener("change", adaptOutline);
  outline.addEventListener("toggle", scheduleUpdate);
  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate);
  window.addEventListener("hashchange", alignFragment);
  window.addEventListener("load", alignFragment);
  controls.hidden = false;
  adaptOutline();
  update();
})();
