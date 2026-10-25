/**
 * Template-only preview control: switches the page between design versions.
 * Finished pages declare one version (data-io-theme on <html>) and do not load
 * this script. The choice is not saved, so the version written in the template
 * remains the source of truth after a reload.
 */
(() => {
  const root = document.documentElement;
  const group = document.querySelector(".theme-switch");
  if (!(group instanceof HTMLElement)) return;
  const buttons = [...group.querySelectorAll("button[data-io-theme-option]")];

  /** @param {string} version - "v1" (no attribute, the default) or "v2". */
  const apply = (version) => {
    if (version === "v1") root.removeAttribute("data-io-theme");
    else root.setAttribute("data-io-theme", version);
    buttons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.ioThemeOption === version));
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => apply(button.dataset.ioThemeOption ?? "v1"));
  });
  apply(root.getAttribute("data-io-theme") ?? "v1");
  group.hidden = false;
})();
