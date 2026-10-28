/* ==========================================================================
   SAATHI – Private page
   - Dismissible banner
   - AES-GCM encrypted local incident log (Web Crypto API)
   - Emergency wipe
   - Support-preference form: POSTs to POST /api/v1/support-requests
   ========================================================================== */
(function () {
  "use strict";

  /* ---- API base (can be overridden by window.SAATHI_API_BASE) ---------- */
  const API_BASE =
    (window.SAATHI_API_BASE || "http://127.0.0.1:8080/api/v1").replace(/\/$/, "");

  const $   = (id) => document.getElementById(id);
  const LOG_KEY = "incident-log";
  const enc = new TextEncoder();
  const dec = new TextDecoder();

  /* ---------- Banner ---------- */
  $("banner-close").addEventListener("click", () => { $("vault-banner").hidden = true; });

  /* ---------- Crypto helpers (AES-GCM + PBKDF2) ---------- */
  const b64 = {
    to:   (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))),
    from: (str) => Uint8Array.from(atob(str), (c) => c.charCodeAt(0)),
  };

  async function deriveKey(passphrase, salt) {
    const material = await crypto.subtle.importKey(
      "raw", enc.encode(passphrase), "PBKDF2", false, ["deriveKey"]
    );
    return crypto.subtle.deriveKey(
      { name: "PBKDF2", salt, iterations: 250000, hash: "SHA-256" },
      material,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    );
  }

  async function encryptText(text, passphrase) {
    const salt = crypto.getRandomValues(new Uint8Array(16));
    const iv   = crypto.getRandomValues(new Uint8Array(12));
    const key  = await deriveKey(passphrase, salt);
    const cipher = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv }, key, enc.encode(text)
    );
    return {
      salt: b64.to(salt),
      iv:   b64.to(iv),
      data: b64.to(cipher),
      at:   new Date().toISOString(),
    };
  }

  async function decryptEntry(entry, passphrase) {
    const key   = await deriveKey(passphrase, b64.from(entry.salt));
    const plain = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: b64.from(entry.iv) },
      key,
      b64.from(entry.data)
    );
    return dec.decode(plain);
  }

  /* ---------- Log state ---------- */
  const getLog = () => Saathi.store.get(LOG_KEY, []);

  function relativeTime(iso) {
    const mins = Math.round((Date.now() - new Date(iso)) / 60000);
    if (mins < 1)  return "just now";
    if (mins < 60) return mins + " min ago";
    const hrs = Math.round(mins / 60);
    if (hrs < 24)  return hrs + " hr ago";
    const days = Math.round(hrs / 24);
    return days + (days === 1 ? " day ago" : " days ago");
  }

  function renderSummary() {
    const log = getLog();
    $("log-count").textContent =
      log.length + (log.length === 1 ? " Item Stored" : " Items Stored");
    $("log-last").textContent = log.length
      ? "Last Entry: " + relativeTime(log[log.length - 1].at) + " (Encrypted)"
      : "No entries yet";
  }

  /* ---------- Dialogs – generic close ---------- */
  document.querySelectorAll("dialog [data-close]").forEach((b) =>
    b.addEventListener("click", () => b.closest("dialog").close())
  );

  /* ---------- Add log entry ---------- */
  const entryDialog = $("entry-dialog");
  $("btn-add-entry").addEventListener("click", () => {
    if (!window.crypto || !crypto.subtle) {
      Saathi.toast("Encryption needs a secure (https) connection.", "lock");
      return;
    }
    $("entry-form").reset();
    entryDialog.showModal();
  });

  $("entry-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = $("entry-text").value.trim();
    const pass = $("entry-pass").value;
    if (!text || pass.length < 6) return;
    try {
      const entry = await encryptText(text, pass);
      const log   = getLog();
      log.push(entry);
      Saathi.store.set(LOG_KEY, log);
      entryDialog.close();
      renderSummary();
      Saathi.toast("Entry encrypted and saved on this device.", "lock");
    } catch (_) {
      Saathi.toast("Couldn't save the entry.", "error");
    }
  });

  /* ---------- View / unlock entries ---------- */
  const logDialog = $("log-dialog");
  $("btn-open-log").addEventListener("click", () => {
    $("unlock-pass").value = "";
    $("entry-list").replaceChildren();
    logDialog.showModal();
  });

  $("btn-unlock").addEventListener("click", async () => {
    const pass = $("unlock-pass").value;
    const list = $("entry-list");
    list.replaceChildren();
    const log = getLog();
    if (!log.length) { Saathi.toast("No entries to unlock yet.", "info"); return; }
    let opened = 0;
    for (const entry of log) {
      try {
        const text = await decryptEntry(entry, pass);
        const li   = document.createElement("li");
        const when = document.createElement("div");
        when.className   = "t-caps muted";
        when.textContent = new Date(entry.at).toLocaleString();
        const body = document.createElement("div");
        body.className   = "t-body";
        body.textContent = text; // textContent keeps user text inert (no HTML injection)
        li.append(when, body);
        list.appendChild(li);
        opened += 1;
      } catch (_) { /* wrong passphrase for this entry – skip silently */ }
    }
    if (!opened) Saathi.toast("That passphrase didn't open any entries.", "key_off");
  });

  /* ---------- Export backup ---------- */
  $("btn-export").addEventListener("click", () => {
    const log = getLog();
    if (!log.length) { Saathi.toast("Nothing to export yet.", "info"); return; }
    const blob = new Blob([JSON.stringify(log)], { type: "application/json" });
    const a    = document.createElement("a");
    a.href     = URL.createObjectURL(blob);
    a.download = "saathi-encrypted-backup.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    Saathi.toast(
      "Encrypted backup downloaded. It is useless without your passphrase.",
      "download"
    );
  });

  /* ---------- Emergency wipe ---------- */
  const confirmDialog = $("confirm-dialog");
  $("wipe-button").addEventListener("click", () => confirmDialog.showModal());
  $("confirm-wipe").addEventListener("click", () => {
    const btn = $("wipe-button");
    btn.textContent = "Purging storage…";
    Saathi.emergencyWipe();
  });

  /* ---------- Support-preference form (wires to backend) ---------- */
  const supportForm = $("support-request-form");
  if (supportForm) {
    supportForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const supportType     = (supportForm.querySelector("[name=support_type]")?.value || "").trim();
      const preferredContact = (supportForm.querySelector("[name=preferred_contact]")?.value || "self-directed").trim();
      const message         = (supportForm.querySelector("[name=message]")?.value || "").trim();
      const consentEl       = supportForm.querySelector("[name=consent]");
      const consent         = consentEl ? consentEl.checked : false;

      if (!consent) {
        Saathi.toast("Please confirm your consent before submitting.", "error");
        return;
      }

      const btn = supportForm.querySelector("[type=submit]");
      if (btn) btn.disabled = true;

      fetch(API_BASE + "/support-requests", {
        method:      "POST",
        headers:     { "Content-Type": "application/json" },
        body:        JSON.stringify({ support_type: supportType, preferred_contact: preferredContact, message, consent }),
        credentials: "omit",
      })
        .then((res) => {
          if (!res.ok) return res.json().then((d) => { throw new Error(d.detail || "Error " + res.status); });
          return res.json();
        })
        .then((data) => {
          if (btn) btn.disabled = false;
          supportForm.reset();
          Saathi.toast(
            "Your preference has been noted. Reference: " + data.reference_code,
            "check_circle"
          );
        })
        .catch((err) => {
          if (btn) btn.disabled = false;
          console.error("Support request error:", err);
          Saathi.toast("Couldn't submit right now. Please try again.", "error");
        });
    });
  }

  /* ---------- Placeholder actions (secure-chat, schedule, advisor, guidelines) ---------- */
  const MESSAGES = {
    "secure-chat": ["Opening secure chat with your counsellor… (Connect your chat service here.)", "lock_clock"],
    schedule:      ["Choose a private time slot. (Connect your calendar API here.)", "calendar_today"],
    advisor:       ["Connecting you to an independent advisor… typical wait 2 minutes.", "forum"],
    guidelines:    ["Filing guidelines will open here. (Link your guidance content.)", "menu_book"],
  };
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn || !MESSAGES[btn.dataset.action]) return;
    Saathi.toast(...MESSAGES[btn.dataset.action]);
  });

  renderSummary();
})();
