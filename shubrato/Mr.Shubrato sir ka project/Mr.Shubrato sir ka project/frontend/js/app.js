/* ==========================================================================
   SAATHI – shared behaviour (loaded on every page)
   - Quick Exit (button + press Escape 3x)
   - Toast helper
   - Language switcher (Assist page strings)
   - Emergency wipe helper
   ========================================================================== */
(function () {
  "use strict";

  const DECOY_URL = "decoy.html";
  const STORAGE_PREFIX = "saathi:";

  /* ---------- Safe storage helpers (storage can throw in private modes) ---------- */
  const store = {
    get(key, fallback = null) {
      try {
        const raw = localStorage.getItem(STORAGE_PREFIX + key);
        return raw === null ? fallback : JSON.parse(raw);
      } catch (_) { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem(STORAGE_PREFIX + key, JSON.stringify(value)); return true; }
      catch (_) { return false; }
    },
    remove(key) { try { localStorage.removeItem(STORAGE_PREFIX + key); } catch (_) {} },
  };

  /* ---------- Quick Exit / Wipe ---------- */
  function quickExit() {
    // location.replace() removes this page from history so Back cannot return to it.
    window.location.replace(DECOY_URL);
  }

  function wipeAllLocalData() {
    try { localStorage.clear(); } catch (_) {}
    try { sessionStorage.clear(); } catch (_) {}
  }

  function emergencyWipe() {
    wipeAllLocalData();
    quickExit();
  }

  document.querySelectorAll("[data-quick-exit]").forEach((btn) => btn.addEventListener("click", quickExit));

  // Keyboard shortcut: press Escape three times within 1.5 seconds.
  let escCount = 0, escTimer;
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    escCount += 1;
    clearTimeout(escTimer);
    escTimer = setTimeout(() => { escCount = 0; }, 1500);
    if (escCount >= 3) quickExit();
  });

  /* ---------- Toasts ---------- */
  function toast(message, icon = "check_circle") {
    let region = document.querySelector(".toast-region");
    if (!region) {
      region = document.createElement("div");
      region.className = "toast-region";
      region.setAttribute("role", "status");
      region.setAttribute("aria-live", "polite");
      document.body.appendChild(region);
    }
    const el = document.createElement("div");
    el.className = "toast t-label-lg";
    el.innerHTML = '<span class="icon icon--18 icon--fill" aria-hidden="true"></span><span></span>';
    el.firstChild.textContent = icon;
    el.lastChild.textContent = message;
    region.appendChild(el);
    setTimeout(() => {
      el.classList.add("is-leaving");
      setTimeout(() => el.remove(), 300);
    }, 3200);
  }

  /* ---------- Language switcher ---------- */
  const TRANSLATIONS = {
    en: {
      safe_title: "You are safe here",
      safe_body: "No browsing trace, search history, or personal identifiers are saved on this device. You can leave anytime using the Exit button.",
      dial_title: "Emergency Direct Dial",
      support_title: "How can SAATHI support you today?",
      support_sub: "Select a category below. Every step is guided gently and confidential.",
      nearby_title: "Nearby Safe Space",
      never_alone: "You are never alone. Confidential peer listening is always free.",
    },
    hi: {
      safe_title: "आप यहाँ सुरक्षित हैं",
      safe_body: "इस डिवाइस पर कोई ब्राउज़िंग ट्रेस, सर्च हिस्ट्री या व्यक्तिगत जानकारी सहेजी नहीं जाती। आप कभी भी Exit बटन से बाहर निकल सकती हैं।",
      dial_title: "आपातकालीन सीधा कॉल",
      support_title: "साथी आज आपकी कैसे मदद कर सकता है?",
      support_sub: "नीचे एक श्रेणी चुनें। हर कदम कोमलता और गोपनीयता के साथ निर्देशित है।",
      nearby_title: "पास का सुरक्षित स्थान",
      never_alone: "आप अकेली नहीं हैं। गोपनीय सहकर्मी सहायता हमेशा निःशुल्क है।",
    },
    bn: {
      safe_title: "আপনি এখানে নিরাপদ",
      safe_body: "এই ডিভাইসে কোনো ব্রাউজিং ট্রেস, সার্চ হিস্ট্রি বা ব্যক্তিগত তথ্য সংরক্ষিত হয় না। আপনি যেকোনো সময় Exit বোতাম দিয়ে বেরিয়ে যেতে পারেন।",
      dial_title: "জরুরি সরাসরি কল",
      support_title: "সাথী আজ আপনাকে কীভাবে সাহায্য করতে পারে?",
      support_sub: "নিচে একটি বিভাগ বেছে নিন। প্রতিটি ধাপ কোমলভাবে ও গোপনীয়তার সঙ্গে পরিচালিত।",
      nearby_title: "কাছের নিরাপদ স্থান",
      never_alone: "আপনি একা নন। গোপনীয় সহকর্মী সহায়তা সবসময় বিনামূল্যে।",
    },
    ta: {
      safe_title: "நீங்கள் இங்கே பாதுகாப்பாக இருக்கிறீர்கள்",
      safe_body: "இந்த சாதனத்தில் உலாவல் தடம், தேடல் வரலாறு அல்லது தனிப்பட்ட அடையாளங்கள் எதுவும் சேமிக்கப்படுவதில்லை. எப்போது வேண்டுமானாலும் Exit பொத்தானால் வெளியேறலாம்.",
      dial_title: "அவசர நேரடி அழைப்பு",
      support_title: "இன்று சாத்தி உங்களுக்கு எப்படி உதவலாம்?",
      support_sub: "கீழே ஒரு பிரிவைத் தேர்ந்தெடுக்கவும். ஒவ்வொரு படியும் மென்மையாகவும் ரகசியமாகவும் வழிநடத்தப்படும்.",
      nearby_title: "அருகிலுள்ள பாதுகாப்பான இடம்",
      never_alone: "நீங்கள் தனியாக இல்லை. ரகசிய தோழமை ஆதரவு எப்போதும் இலவசம்.",
    },
  };

  function applyLanguage(lang) {
    const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const text = dict[el.dataset.i18n];
      if (text) el.textContent = text;
    });
    document.querySelectorAll("[data-lang]").forEach((chip) => {
      chip.setAttribute("aria-pressed", String(chip.dataset.lang === lang));
    });
    try { sessionStorage.setItem(STORAGE_PREFIX + "lang", lang); } catch (_) {}
  }

  const langChips = document.querySelectorAll("[data-lang]");
  if (langChips.length) {
    langChips.forEach((chip) => chip.addEventListener("click", () => applyLanguage(chip.dataset.lang)));
    let saved = "en";
    try { saved = sessionStorage.getItem(STORAGE_PREFIX + "lang") || "en"; } catch (_) {}
    applyLanguage(saved);
  }

  /* ---------- Public API for page scripts ---------- */
  window.Saathi = { store, toast, quickExit, emergencyWipe, wipeAllLocalData };
})();
