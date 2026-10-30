# Project instructions — Torfunk

Shared instructions for any AI coding agent (Claude Code, Codex, Cursor, Gemini, etc.).
When the user gives a lasting instruction, process, tool, or package choice, record it here.

## What this is

**Torfunk** — a matchday app for amateur/youth football (German UI). For everyone at the sideline:
- **Coaches:** squad, availability, formations (preset + custom), drag-and-drop lineup (dropping on an occupied position substitutes the player there), sharing the lineup as image/link.
- **Ticker people:** live ticker with German WhatsApp messages (one person runs it).
- **Team, parents, fans:** receive lineup image and ticker messages in the WhatsApp group.

Name history: started as "formation-planner" / "Aufstellungsplaner", renamed to Torfunk (2026-10-30). Internal names stay on purpose: the storage key `formation-planner-v1` (keeps saved data) and the `serve-https.py` certificate folder/CA name (keeps phones trusting it). The local folder may still be called `formation-planner`.

## Stack & conventions

- **Single file**: everything lives in `index.html` — CSS in `<style>`, JS in `<script>`.
- **No build step, no frameworks, no npm/node dependencies in the app, no CDNs** — must work offline by opening the file.
- **Theming via CSS variables** in `:root`; don't hardcode colors/spacing elsewhere.
- **State** in one JS object (`state`, persisted to `localStorage` key `formation-planner-v1`); transient UI state in `ui`.
- Drag & drop uses **pointer events** (not HTML5 DnD) so it works on touch devices; tap-to-place is the fallback.
- Touch rules: on list chips a swipe must scroll and a **hold (~280 ms) starts the drag** (`touch-action: pan-y`/`pan-x`); never set `touch-action: none` on list items again — the user couldn't scroll the squad on a phone. Phones get a fixed bench bar at the bottom.
- Test touch changes with puppeteer device emulation + `page.touchscreen` (swipe, tap, hold-and-drag), not only mouse.
- Must be responsive / usable on phones and tablets (coaches use it pitch-side).
- Share links put the whole lineup in the URL hash (`#lineup=` + base64url JSON with `v: 1`). Links already sent around must keep working: bump `v` and keep decoding old versions when the format changes.
- **Live ticker** (tab "Live-Ticker"): UI and WhatsApp messages are **German**; one ticker person; opponents only by shirt number. Messages are built in `buildMessage()` from event data (never stored as text), so edits re-generate them. WhatsApp formatting: `*bold*`, `_italic_`, `~strike~`, lists `- `. Sending: share menu on phones over https, otherwise a `wa.me/?text=` link.
- **The whole app UI is German** (since 2026-10-30), informal "du". New text must be German too. Position abbreviations are German (TW, LV, IV, RV, DM, ZM, OM, LA, RA, ST …); `LABELS_DE` converts old English labels from saved data and old share links.
- The share image is drawn on a `<canvas>` by hand (`drawLineupImage`), no screenshot libraries. Keep it in sync when the pitch display changes.

## Tools & packages

- Testing: headless Chrome (`/usr/bin/google-chrome`) driven by `puppeteer-core`, installed only in a temp/scratch dir — never added to the project.

## Processes

- **Git / GitHub:** push only with the account and remote already configured in this repo (local git config). Never change the remote or the commit identity, and don't use another GitHub account. The private details (which account, SSH alias) are in `AGENTS.local.md` — read it if present.
- **Keep personal data out of the repo** (it is public): no real names, employer, account names, email addresses, club/team names, IPs or paths containing user names in files or commit messages. Use neutral examples (SV Musterdorf / SVM, FC Musterstadt / FCM). Private notes go in `AGENTS.local.md` (git-ignored).
- **Testing on a phone:** run `python3 serve-https.py` (port 8443) on the laptop, open the printed `https://<laptop-ip>:8443/` on the phone. Plain `python3 -m http.server` is not enough: phones block image sharing (Web Share / clipboard) on http pages.
  - The script makes a local CA once; its keys live in `~/.local/share/formation-planner/certs/` — never inside the project folder (it is served).
  - The phone needs the CA installed once, from `https://<laptop-ip>:8443/ca.crt`.
  - `serve-https.py` is a dev helper only (Python standard library + openssl); the app itself stays a single HTML file.
