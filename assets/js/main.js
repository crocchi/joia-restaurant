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
  status.textContent = isOpen ? "● Aperto ora" : "● Chiuso ora";
  status.classList.add(isOpen ? "open" : "closed");
  status.hidden = false;

  // Modulo partner: niente backend, apre il client email con la richiesta precompilata.
  // TODO: indirizzo reale; in alternativa collegare un servizio form (Formspree, Netlify Forms…).
  const PARTNER_EMAIL = "partner@joiatenerife.com";
  const form = document.getElementById("partner-form");
  const msg = document.getElementById("form-msg");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const required = form.querySelectorAll("[required]");
    let firstInvalid = null;
    required.forEach((el) => {
      const ok = el.type === "checkbox" ? el.checked : el.checkValidity() && el.value.trim() !== "";
      el.classList.toggle("invalid", !ok);
      if (!ok && !firstInvalid) firstInvalid = el;
    });
    if (firstInvalid) {
      msg.textContent = "Compila i campi obbligatori e accetta il trattamento dei dati.";
      msg.className = "form-msg error";
      firstInvalid.focus();
      return;
    }

    const d = new FormData(form);
    const body = [
      "Nome: " + d.get("nome"),
      "Email: " + d.get("email"),
      "Telefono: " + (d.get("telefono") || "-"),
      "Profilo: " + d.get("profilo"),
      "Capitale: " + d.get("capitale"),
      "",
      d.get("messaggio") || "",
    ].join("\n");

    window.location.href = "mailto:" + PARTNER_EMAIL +
      "?subject=" + encodeURIComponent("Richiesta partnership JOIA Tenerife - " + d.get("nome")) +
      "&body=" + encodeURIComponent(body);

    msg.textContent = "Grazie! Si sta aprendo la tua app email: invia il messaggio per completare la richiesta.";
    msg.className = "form-msg ok";
  });

  // Anno nel footer
  document.getElementById("year").textContent = now.getFullYear();
})();
