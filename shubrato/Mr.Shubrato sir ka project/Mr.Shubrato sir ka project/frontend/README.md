# SAATHI – Women's Safety App (front end)

Plain HTML + CSS + JavaScript. No build step, no framework.

## Run
Open `index.html` in a browser, or serve the folder (needed for encryption + geolocation, which require https/localhost):

    python3 -m http.server 8000      # then visit http://localhost:8000

## Structure
    index.html      Assist (home): emergency dial, language chips, triage, nearby safe space
    services.html   Verified Services directory: search, filters, voice search
    report.html     Community hazard report form: categories, photo (EXIF scrubbed), location, urgency, drafts
    private.html    Private space: encrypted incident log (Web Crypto AES-GCM), emergency wipe
    decoy.html      Neutral calculator shown after Quick Exit
    css/styles.css  Design tokens ("Sanctuary Quietude") + all components
    js/app.js       Shared: Quick Exit (button or Esc x3), toasts, language switcher, wipe
    js/services.js | report.js | private.js   Page logic

## To connect to a real backend
- `js/report.js` -> `submitReport()` (POST the payload)
- `js/services.js` -> booking / silent chat actions
- `js/private.js` -> secure chat / schedule / advisor actions
- Have Hindi/Bengali/Tamil strings in `js/app.js` reviewed by native speakers.
