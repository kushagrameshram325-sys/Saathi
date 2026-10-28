/* ==========================================================================
   SAATHI – auth.js
   Handles the login / register page interactions:
   - Tab switching (Login ↔ Register)
   - Client-side validation
   - API calls to POST /api/v1/auth/login and POST /api/v1/auth/register
   - Saves session token to localStorage on success
   - Redirects to index.html after successful auth
   ========================================================================== */
(function () {
  "use strict";

  /* ---- API base (can be overridden by window.SAATHI_API_BASE) ----------- */
  const API_BASE =
    (window.SAATHI_API_BASE || "http://127.0.0.1:8080/api/v1").replace(/\/$/, "");

  const SESSION_KEY = "saathi:session";   // key in localStorage
  const REDIRECT    = "index.html";

  /* ---- If already logged in, skip to main app --------------------------- */
  (function checkExistingSession() {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      if (!raw) return;
      const sess = JSON.parse(raw);
      if (sess && sess.token && new Date(sess.expires_at) > new Date()) {
        window.location.replace(REDIRECT);
      }
    } catch (_) { /* ignore malformed storage */ }
  })();

  /* ---- DOM refs --------------------------------------------------------- */
  const tabLogin    = document.getElementById("tab-login");
  const tabRegister = document.getElementById("tab-register");
  const panelLogin  = document.getElementById("panel-login");
  const panelReg    = document.getElementById("panel-register");

  /* ---- Tab switching ---------------------------------------------------- */
  function showLogin() {
    tabLogin.classList.add("is-active");
    tabRegister.classList.remove("is-active");
    tabLogin.setAttribute("aria-selected", "true");
    tabRegister.setAttribute("aria-selected", "false");
    panelLogin.hidden  = false;
    panelReg.hidden    = true;
    clearErrors();
  }

  function showRegister() {
    tabRegister.classList.add("is-active");
    tabLogin.classList.remove("is-active");
    tabRegister.setAttribute("aria-selected", "true");
    tabLogin.setAttribute("aria-selected", "false");
    panelReg.hidden   = false;
    panelLogin.hidden = true;
    clearErrors();
  }

  tabLogin.addEventListener("click", showLogin);
  tabRegister.addEventListener("click", showRegister);
  document.getElementById("go-register").addEventListener("click", showRegister);
  document.getElementById("go-login").addEventListener("click", showLogin);

  /* ---- Password visibility toggle --------------------------------------- */
  document.querySelectorAll(".pw-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const isText = input.type === "text";
      input.type = isText ? "password" : "text";
      btn.querySelector(".icon").textContent = isText ? "visibility" : "visibility_off";
    });
  });

  /* ---- Error helpers ---------------------------------------------------- */
  function showFieldErr(id, show) {
    const el = document.getElementById(id);
    if (el) el.classList.toggle("is-visible", show);
  }

  function showServerErr(bannerId, msgId, message) {
    const banner = document.getElementById(bannerId);
    const msg    = document.getElementById(msgId);
    if (banner) banner.hidden = false;
    if (msg)    msg.textContent = message;
  }

  function hideServerErr(bannerId) {
    const banner = document.getElementById(bannerId);
    if (banner) banner.hidden = true;
  }

  function clearErrors() {
    document.querySelectorAll(".field-error").forEach((el) => el.classList.remove("is-visible"));
    hideServerErr("login-server-err");
    hideServerErr("reg-server-err");
  }

  /* ---- Session storage helper ------------------------------------------ */
  function saveSession(tokenData) {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify(tokenData));
    } catch (_) { /* private mode */ }
  }

  /* ---- On success: save and redirect ------------------------------------ */
  function onAuthSuccess(tokenData) {
    saveSession(tokenData);
    if (typeof Saathi !== "undefined") {
      Saathi.toast("Welcome, " + (tokenData.user.name || "friend") + "! Redirecting…", "check_circle");
    }
    setTimeout(() => window.location.replace(REDIRECT), 900);
  }

  /* ---- LOGIN form ------------------------------------------------------- */
  document.getElementById("form-login").addEventListener("submit", (e) => {
    e.preventDefault();
    clearErrors();

    const phone    = document.getElementById("login-phone").value.trim();
    const password = document.getElementById("login-password").value;
    let valid = true;

    if (!phone || phone.length < 7) { showFieldErr("login-phone-err", true); valid = false; }
    if (!password)                  { showFieldErr("login-pw-err",    true); valid = false; }
    if (!valid) return;

    const btn = document.getElementById("btn-login");
    btn.disabled = true;

    fetch(API_BASE + "/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "omit",
      body: JSON.stringify({ phone, password }),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || "Login failed."); });
        return res.json();
      })
      .then(onAuthSuccess)
      .catch((err) => {
        showServerErr("login-server-err", "login-server-msg", err.message || "Login failed. Please try again.");
      })
      .finally(() => { btn.disabled = false; });
  });

  /* ---- REGISTER form ---------------------------------------------------- */
  document.getElementById("form-register").addEventListener("submit", (e) => {
    e.preventDefault();
    clearErrors();

    const name        = document.getElementById("reg-name").value.trim();
    const phone       = document.getElementById("reg-phone").value.trim();
    const parentPhone = document.getElementById("reg-parent-phone").value.trim();
    const password    = document.getElementById("reg-password").value;
    let valid = true;

    if (!name || name.length < 2)   { showFieldErr("reg-name-err",  true); valid = false; }
    if (!phone || phone.length < 7)  { showFieldErr("reg-phone-err", true); valid = false; }
    if (!password || password.length < 6) { showFieldErr("reg-pw-err", true); valid = false; }
    if (!valid) return;

    const btn = document.getElementById("btn-register");
    btn.disabled = true;

    const payload = {
      name,
      phone,
      password,
      ...(parentPhone ? { parent_phone: parentPhone } : {}),
    };

    fetch(API_BASE + "/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "omit",
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || "Registration failed."); });
        return res.json();
      })
      .then(onAuthSuccess)
      .catch((err) => {
        showServerErr("reg-server-err", "reg-server-msg", err.message || "Registration failed. Please try again.");
      })
      .finally(() => { btn.disabled = false; });
  });

})();
