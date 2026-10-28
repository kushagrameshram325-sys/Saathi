/* ==========================================================================
   SAATHI – Services page
   Loads the service directory from GET /api/v1/services, then applies
   client-side keyword search, synonym expansion, and category filtering.
   Falls back to showing any static HTML cards already in the DOM if the
   backend is unreachable.
   ========================================================================== */
(function () {
  "use strict";

  /* ---- API base (can be overridden by window.SAATHI_API_BASE) ---------- */
  const API_BASE =
    (window.SAATHI_API_BASE || "http://127.0.0.1:8080/api/v1").replace(/\/$/, "");

  const input      = document.getElementById("directory-search");
  const filterBtns = Array.from(document.querySelectorAll("[data-filter]"));
  const noResults  = document.getElementById("no-results");
  const statusEl   = document.getElementById("results-status");
  const listEl     = document.getElementById("service-list");

  let activeFilter = "all";
  let apiCards     = [];   // article elements rendered from API data
  let staticCards  = [];   // static HTML cards already in DOM (fallback)

  // Category → tag mapping for filter chips
  const CATEGORY_TAGS = {
    helpline:     "247 free",
    emergency:    "247",
    counselling:  "free",
    "legal-support": "free",
    shelter:      "free women",
  };

  // Keyword synonyms so plain-language queries still match
  const SYNONYMS = {
    legal:       ["legal", "lawyer", "advocate", "court", "law", "protection order"],
    shelter:     ["shelter", "stay", "beds", "safe house", "home"],
    counselling: ["counselling", "counseling", "counsellor", "therapy", "trauma", "mental", "talk"],
    helpline:    ["helpline", "hotline", "call", "dial", "phone", "emergency"],
    women:       ["women", "mahila", "stree", "female", "sakhi"],
  };

  function expandTerms(query) {
    const terms   = query.toLowerCase().split(/\s+/).filter(Boolean);
    const expanded = new Set(terms);
    terms.forEach((t) => {
      Object.values(SYNONYMS).forEach((group) => {
        if (group.some((g) => g.includes(t) || t.includes(g)))
          group.forEach((g) => expanded.add(g));
      });
    });
    return Array.from(expanded);
  }

  /* ---------- Render services fetched from the API ---------- */
  function buildCard(svc) {
    const tags = CATEGORY_TAGS[svc.category] || "";
    const phoneLink = svc.phone
      ? `<a class="btn btn--lg btn--container t-label-lg" href="tel:${svc.phone}">
           <span class="icon icon--18" aria-hidden="true">call</span>
           Call ${svc.phone}
         </a>`
      : "";
    const websiteLink = svc.website
      ? `<a class="btn btn--soft t-label-lg" href="${svc.website}" target="_blank" rel="noopener noreferrer">
           <span class="icon icon--18 accent" aria-hidden="true">open_in_new</span>
           Visit Website
         </a>`
      : "";
    const verifiedBadge = svc.verified
      ? `<span class="badge t-caps"><span class="icon icon--14 icon--fill" aria-hidden="true">verified</span>Verified</span>`
      : `<span class="badge t-caps">Demo listing – not verified</span>`;

    const article = document.createElement("article");
    article.className = "card service";
    article.dataset.tags   = tags;
    article.dataset.search = [svc.name, svc.description, svc.category, svc.city]
      .join(" ")
      .toLowerCase();

    article.innerHTML = `
      <div class="row row--between" style="align-items:flex-start">
        <div>
          <h2 class="t-title">${escHtml(svc.name)}</h2>
          <span class="t-small muted">${escHtml(svc.city)}</span>
        </div>
        ${verifiedBadge}
      </div>
      <p class="t-body muted">${escHtml(svc.description)}</p>
      ${svc.accessibility_notes
        ? `<p class="t-small subtle"><span class="icon icon--14" aria-hidden="true">accessibility</span> ${escHtml(svc.accessibility_notes)}</p>`
        : ""}
      <div class="stack-xs pt-xs">
        ${phoneLink}
        ${websiteLink}
      </div>`;
    return article;
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderApiServices(services) {
    // Remove previously rendered API cards
    apiCards.forEach((c) => c.remove());
    apiCards = [];

    services.forEach((svc) => {
      const card = buildCard(svc);
      listEl.appendChild(card);
      apiCards.push(card);
    });

    applyFilters();
  }

  /* ---------- Filter / search ---------- */
  function applyFilters() {
    const q     = input.value.trim();
    const terms = q ? expandTerms(q) : [];

    // Combine API-rendered cards and any static HTML fallback cards
    const allCards = [...apiCards, ...staticCards];
    let visible = 0;

    allCards.forEach((card) => {
      const cardTags = (card.dataset.tags || "").split(" ");
      const matchesFilter =
        activeFilter === "all" || cardTags.includes(activeFilter);
      const haystack = (card.dataset.search || "") + " " + card.textContent.toLowerCase();
      const matchesQuery = !terms.length || terms.some((t) => haystack.includes(t));
      const show = matchesFilter && matchesQuery;
      card.classList.toggle("is-hidden-by-filter", !show);
      if (show) visible += 1;
    });

    noResults.hidden = visible !== 0;
    statusEl.hidden  = !q && activeFilter === "all";
    statusEl.textContent =
      visible + (visible === 1 ? " service found" : " services found");
  }

  input.addEventListener("input", applyFilters);

  document.querySelectorAll("[data-query]").forEach((chip) => {
    chip.addEventListener("click", () => {
      input.value = chip.dataset.query;
      input.focus();
      applyFilters();
    });
  });

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      activeFilter = btn.dataset.filter;
      filterBtns.forEach((b) =>
        b.setAttribute("aria-pressed", String(b === btn))
      );
      applyFilters();
    });
  });

  // Deep link from home: services.html?need=emergency
  const need = new URLSearchParams(location.search).get("need");
  if (need === "emergency") {
    const btn = filterBtns.find((b) => b.dataset.filter === "247");
    if (btn) btn.click();
  }

  /* ---------- Voice search ---------- */
  const mic = document.getElementById("mic-btn");
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    if (mic) mic.hidden = true;
  } else {
    mic.addEventListener("click", () => {
      const rec = new SpeechRecognition();
      rec.lang =
        document.documentElement.lang === "en"
          ? "en-IN"
          : document.documentElement.lang;
      rec.interimResults = false;
      mic.classList.add("is-listening");
      rec.onresult = (e) => {
        input.value = e.results[0][0].transcript;
        applyFilters();
      };
      rec.onerror = () =>
        Saathi.toast("Couldn't hear that. Please try again.", "mic_off");
      rec.onend = () => mic.classList.remove("is-listening");
      rec.start();
    });
  }

  /* ---------- Card actions (route, book, chat) ---------- */
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    const name = btn.dataset.name || "this service";
    switch (btn.dataset.action) {
      case "route":
        window.open(
          "https://www.google.com/maps/dir/?api=1&travelmode=walking&destination=" +
            encodeURIComponent(name),
          "_blank",
          "noopener"
        );
        break;
      case "book":
        Saathi.toast(
          "Anonymous booking request ready for " +
            name +
            ". (Connect your booking API here.)",
          "calendar_month"
        );
        break;
      case "chat":
        Saathi.toast(
          "Opening silent web chat with " +
            name +
            "… (Connect your chat widget here.)",
          "forum"
        );
        break;
    }
  });

  /* ---------- Load from backend ---------- */
  function loadServices() {
    // Preserve static cards already in the DOM as fallback
    staticCards = Array.from(document.querySelectorAll(".service"));

    fetch(API_BASE + "/services", { credentials: "omit" })
      .then((res) => {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then((services) => {
        if (services.length) {
          // Hide static HTML cards – the API data takes precedence
          staticCards.forEach((c) => (c.hidden = true));
          staticCards = [];
          renderApiServices(services);
        } else {
          // No API data – fall back to static cards
          applyFilters();
        }
      })
      .catch((err) => {
        console.warn("Could not load services from API; using static cards.", err);
        // Just filter the static cards that are already in the DOM
        applyFilters();
      });
  }

  loadServices();
})();
