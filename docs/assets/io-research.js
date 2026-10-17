/**
 * Progressive enhancement for the research index. Native anchors and disclosure
 * controls work without JavaScript; this only marks the section being read.
 */
(() => {
  const links = [...document.querySelectorAll(".research-index a[href^='#']")];
  const sections = links.map((link) => document.getElementById(link.hash.slice(1)));
  if (!links.length || sections.some((section) => !section)) return;

  let scheduled = false;

  const updateIndex = () => {
    // Use section starts, not visibility ratios: a long grid should stay selected
    // until the reader reaches the next section, just like a short paragraph.
    let current = 0;
    sections.forEach((section, index) => {
      if (section.getBoundingClientRect().top <= 120) current = index;
    });
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
      current = sections.length - 1;
    }

    links.forEach((link, index) => {
      if (index === current) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
    scheduled = false;
  };

  const scheduleUpdate = () => {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(updateIndex);
  };

  window.addEventListener("scroll", scheduleUpdate, { passive: true });
  window.addEventListener("resize", scheduleUpdate);
  window.addEventListener("load", scheduleUpdate);
  // Expanding the schema changes section positions without necessarily scrolling.
  document.querySelectorAll("details").forEach((details) => {
    details.addEventListener("toggle", scheduleUpdate);
  });
  updateIndex();
})();
