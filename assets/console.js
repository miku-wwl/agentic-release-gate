/* UI navigation only. No network calls, approval handling or execution APIs. */
"use strict";
document.body.classList.add("js-navigation");

const menu = document.querySelector(".menu-button");
if (menu) {
  menu.addEventListener("click", () => {
    const expanded = menu.getAttribute("aria-expanded") === "true";
    menu.setAttribute("aria-expanded", String(!expanded));
    document.body.classList.toggle("navigation-open", !expanded);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      menu.setAttribute("aria-expanded", "false");
      document.body.classList.remove("navigation-open");
    }
  });
}

const caseLinks = Array.from(document.querySelectorAll("[data-case-link]"));
const panels = Array.from(document.querySelectorAll("[data-case-panel]"));
function showCase() {
  const selected = location.hash === "#negative" ? "negative" : "positive";
  for (const panel of panels) {
    panel.hidden = panel.dataset.casePanel !== selected;
  }
  for (const control of caseLinks) {
    if (control.dataset.caseLink === selected) {
      control.setAttribute("aria-current", "true");
    } else {
      control.removeAttribute("aria-current");
    }
  }
  const announcement = document.getElementById("case-announcement");
  if (announcement)
    announcement.textContent = `${selected} demo fixture selected`;
}
if (panels.length) {
  window.addEventListener("hashchange", showCase);
  window.addEventListener("popstate", showCase);
  for (const control of caseLinks) {
    control.addEventListener("click", (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)
        return;
      // Switch fixtures in place; keep the case navigation visible and preserve Back.
      event.preventDefault();
      if (location.hash !== control.hash)
        history.pushState(null, "", control.hash);
      showCase();
    });
  }
  showCase();
}
