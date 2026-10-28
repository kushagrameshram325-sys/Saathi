/* ==========================================================================
   SAATHI – Report page
   Connects to POST /api/v1/hazards on submit.
   Handles: category multi-select, photo upload (EXIF scrub),
            GPS location capture, time / urgency radio groups,
            draft save/restore, and backend submission.
   ========================================================================== */
(function () {
  "use strict";

  /* ---- API base (can be overridden by window.SAATHI_API_BASE) ---------- */
  const API_BASE =
    (window.SAATHI_API_BASE || "http://127.0.0.1:8080/api/v1").replace(/\/$/, "");

  const MAX_BYTES = 15 * 1024 * 1024;
  const ALLOWED   = ["image/jpeg", "image/png"];
  const DRAFT_KEY = "report-draft";

  const $  = (id) => document.getElementById(id);
  const form         = $("report-form");
  const categories   = Array.from(document.querySelectorAll(".category"));
  const timeButtons  = Array.from(document.querySelectorAll("#time-toggle [role=radio]"));
  const urgencyButtons = Array.from(document.querySelectorAll("#urgency-selector [role=radio]"));

  const state = { photoDataUrl: null, photoName: null, coords: null };

  /* ---------- Category multi-select ---------- */
  categories.forEach((btn) => {
    btn.addEventListener("click", () => {
      const on = btn.getAttribute("aria-pressed") === "true";
      btn.setAttribute("aria-pressed", String(!on));
      $("category-error").hidden = true;
    });
  });

  /* ---------- Radio-like groups ---------- */
  function radioGroup(buttons) {
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => select(btn));
      btn.addEventListener("keydown", (e) => {
        const i = buttons.indexOf(btn);
        if (e.key === "ArrowRight" || e.key === "ArrowDown") {
          e.preventDefault();
          const next = buttons[(i + 1) % buttons.length];
          select(next);
          next.focus();
        }
        if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
          e.preventDefault();
          const prev = buttons[(i - 1 + buttons.length) % buttons.length];
          select(prev);
          prev.focus();
        }
      });
    });
    function select(target) {
      buttons.forEach((b) => b.setAttribute("aria-checked", String(b === target)));
    }
  }
  radioGroup(timeButtons);
  radioGroup(urgencyButtons);

  const selected = (buttons) =>
    (buttons.find((b) => b.getAttribute("aria-checked") === "true") || {}).dataset?.value;

  /* ---------- Photo upload ---------- */
  const fileRow = $("file-row");
  $("btn-camera").addEventListener("click", () => $("file-camera").click());
  $("btn-gallery").addEventListener("click", () => $("file-gallery").click());
  ["file-camera", "file-gallery"].forEach((id) =>
    $(id).addEventListener("change", (e) => handleFile(e.target.files[0], e.target))
  );

  function handleFile(file, inputEl) {
    if (!file) return;
    if (!ALLOWED.includes(file.type)) {
      Saathi.toast("Please choose a PNG or JPG image.", "error");
      inputEl.value = "";
      return;
    }
    if (file.size > MAX_BYTES) {
      Saathi.toast("That photo is over 15 MB.", "error");
      inputEl.value = "";
      return;
    }
    scrubExif(file).then((dataUrl) => {
      if (!dataUrl) return;
      state.photoDataUrl = dataUrl;
      state.photoName = file.name;
      $("file-thumb").src = dataUrl;
      $("file-name").textContent = file.name;
      $("file-meta").textContent =
        (file.size / 1048576).toFixed(1) + " MB • Metadata removed";
      fileRow.hidden = false;
    });
  }

  /** Re-draw the image on a canvas: strips all EXIF / GPS metadata. */
  function scrubExif(file) {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        const scale = Math.min(1, 1600 / Math.max(img.width, img.height));
        const c = document.createElement("canvas");
        c.width  = Math.round(img.width  * scale);
        c.height = Math.round(img.height * scale);
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        resolve(c.toDataURL("image/jpeg", 0.85));
      };
      img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("bad image")); };
      img.src = url;
    }).catch(() => {
      Saathi.toast("Couldn't read that image.", "error");
      return null;
    });
  }

  $("file-remove").addEventListener("click", () => {
    state.photoDataUrl = null;
    state.photoName = null;
    $("file-camera").value = "";
    $("file-gallery").value = "";
    fileRow.hidden = true;
  });

  /* ---------- Location ---------- */
  $("btn-locate").addEventListener("click", () => {
    if (!navigator.geolocation) {
      Saathi.toast("Location isn't available on this device.", "location_off");
      return;
    }
    $("gps-text").textContent = "Locating…";
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        state.coords = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          accuracy: Math.round(pos.coords.accuracy),
        };
        $("loc-title").textContent =
          "Pin set at " +
          state.coords.lat.toFixed(4) + ", " +
          state.coords.lng.toFixed(4);
        $("loc-sub").textContent =
          "Accuracy ±" + state.coords.accuracy +
          "m • Coordinates stay on your device until you submit";
        $("map-label").textContent = "Current location";
        $("gps-text").textContent = "GPS Active";
      },
      () => {
        $("gps-text").textContent = "GPS Off";
        Saathi.toast(
          "Couldn't get your location. You can describe it in the landmark box.",
          "location_off"
        );
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  });

  /* ---------- Collect / restore ---------- */
  function collect() {
    return {
      categories: categories
        .filter((b) => b.getAttribute("aria-pressed") === "true")
        .map((b) => b.dataset.key),
      landmark:   $("landmark").value.trim(),
      when:       selected(timeButtons),
      urgency:    selected(urgencyButtons),
      anonymous:  $("opt-anon").checked,
      notify:     $("opt-notify").checked,
      coords:     state.coords,
      hasPhoto:   Boolean(state.photoDataUrl),
    };
  }

  function restoreDraft() {
    const d = Saathi.store.get(DRAFT_KEY);
    if (!d) return false;
    categories.forEach((b) =>
      b.setAttribute("aria-pressed", String(d.categories.includes(b.dataset.key)))
    );
    $("landmark").value = d.landmark || "";
    timeButtons.forEach((b) =>
      b.setAttribute("aria-checked", String(b.dataset.value === d.when))
    );
    urgencyButtons.forEach((b) =>
      b.setAttribute("aria-checked", String(b.dataset.value === d.urgency))
    );
    $("opt-anon").checked  = d.anonymous;
    $("opt-notify").checked = d.notify;
    Saathi.toast("Draft restored from your offline vault.", "archive");
    return true;
  }

  $("btn-draft").addEventListener("click", () => {
    if (Saathi.store.set(DRAFT_KEY, collect()))
      Saathi.toast("Draft saved to your offline vault (photo not stored).", "archive");
    else
      Saathi.toast("Couldn't save – private browsing may block storage.", "error");
  });

  /* ---------- Submit to backend API ---------- */
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = collect();

    if (!data.categories.length) {
      $("category-error").hidden = false;
      $("category-grid").scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    // Build description from landmark + categories (back-end requires ≥5 chars)
    const categoryLabel = data.categories.join(", ");
    const description =
      (data.landmark
        ? `${categoryLabel} — ${data.landmark}`
        : categoryLabel) +
      (data.when ? ` (observed: ${data.when})` : "") +
      (data.urgency ? ` [urgency: ${data.urgency}]` : "");

    // Use first selected category for the API's category field (≤60 chars)
    const primaryCategory = data.categories[0] || "other";

    const locationText = data.landmark || "Location not specified";

    const payload = {
      category:      primaryCategory,
      description:   description,
      location_text: locationText,
      latitude:  data.coords ? data.coords.lat : null,
      longitude: data.coords ? data.coords.lng : null,
    };

    const btn = $("btn-submit");
    btn.disabled = true;

    submitReport(payload)
      .then((result) => {
        Saathi.store.remove(DRAFT_KEY);
        const refMsg = result && result.reference_code
          ? ` Reference: ${result.reference_code}`
          : "";
        Saathi.toast(
          "Report submitted. Thank you for making your community safer." + refMsg,
          "check_circle"
        );
        // Reset form after a moment so the user can read the toast.
        setTimeout(() => {
          form.reset();
          categories.forEach((b) => b.setAttribute("aria-pressed", "false"));
          state.photoDataUrl = null;
          state.coords = null;
          fileRow.hidden = true;
          btn.disabled = false;
        }, 2000);
      })
      .catch((err) => {
        console.error("Hazard report error:", err);
        btn.disabled = false;
        Saathi.toast("Couldn't send right now. Save as a draft and retry later.", "wifi_off");
      });
  });

  /**
   * POST the hazard payload to the backend and return the parsed response.
   * @param {Object} payload
   * @returns {Promise<Object>}
   */
  function submitReport(payload) {
    return fetch(API_BASE + "/hazards", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "omit",
    }).then((res) => {
      if (!res.ok) {
        return res.json().then((data) => {
          throw new Error(data.detail || "Server error " + res.status);
        });
      }
      return res.json();
    });
  }

  restoreDraft();
})();
