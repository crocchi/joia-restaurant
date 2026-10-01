(function () {
  "use strict";

  // Menu mobile
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");

  function setNav(open) {
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Chiudi menu" : "Apri menu");
    nav.classList.toggle("open", open);
  }

  toggle.addEventListener("click", () => setNav(toggle.getAttribute("aria-expanded") !== "true"));
  nav.addEventListener("click", (e) => { if (e.target.closest("a")) setNav(false); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setNav(false); });

  // Ombra header allo scroll
  const header = document.querySelector(".site-header");
  const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Reveal on scroll
  const items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    items.forEach((el) => io.observe(el));
  } else {
    items.forEach((el) => el.classList.add("in"));
  }

  // Orari: evidenzia oggi e mostra "Aperto ora / Chiuso ora".
  // Tenere allineato con la tabella in index.html.
  // Indici: 0 = domenica … 6 = sabato. Fasce in minuti dalla mezzanotte.
  const t = (h, m) => h * 60 + m;
  const SCHEDULE = {
    0: [[t(12, 0), t(22, 0)]],
    1: [],
    2: [[t(12, 0), t(15, 0)], [t(19, 0), t(23, 0)]],
    3: [[t(12, 0), t(15, 0)], [t(19, 0), t(23, 0)]],
    4: [[t(12, 0), t(15, 0)], [t(19, 0), t(23, 0)]],
    5: [[t(12, 0), t(15, 0)], [t(19, 0), t(23, 0)]],
    6: [[t(12, 0), t(23, 30)]],
  };
  // Riga della tabella corrispondente a ogni giorno
  const ROW_FOR_DAY = [3, 0, 1, 1, 1, 1, 2];

  const now = new Date();
  const day = now.getDay();
  const minutes = now.getHours() * 60 + now.getMinutes();

  const rows = document.querySelectorAll(".hours dl > div");
  if (rows[ROW_FOR_DAY[day]]) rows[ROW_FOR_DAY[day]].classList.add("is-today");

  const status = document.getElementById("today-status");
  const isOpen = SCHEDULE[day].some(([from, to]) => minutes >= from && minutes < to);
  if (status) {
    status.textContent = isOpen ? "● Aperto ora" : "● Chiuso ora";
    status.classList.add(isOpen ? "open" : "closed");
    status.hidden = false;
  }

  // Anno nel footer
  document.getElementById("year").textContent = now.getFullYear();
})();
