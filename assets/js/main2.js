(function () {
  "use strict";
  const language = document.documentElement.lang;
  const labels = {
    en: { open: "Open menu", close: "Close menu", openNow: "● Open now", closedNow: "● Closed now" },
    it: { open: "Apri menu", close: "Chiudi menu", openNow: "● Aperto ora", closedNow: "● Chiuso ora" },
    es: { open: "Abrir menú", close: "Cerrar menú", openNow: "● Abierto ahora", closedNow: "● Cerrado ahora" }
  }[language] || { open: "Open menu", close: "Close menu", openNow: "● Open now", closedNow: "● Closed now" };
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("navigation");
  const closeMenu = () => {
    nav.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", labels.open);
  };
  toggle.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") !== "true";
    nav.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? labels.close : labels.open);
  });
  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
      closeMenu();
      toggle.focus();
    }
  });
  document.getElementById("year2").textContent = new Date().getFullYear();
})();
