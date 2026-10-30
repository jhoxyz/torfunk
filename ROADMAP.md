# Roadmap — Torfunk

Ideas collected for later. Nothing here is started yet — only work on an item when the user asks for it.

## Planned features (proposed by Claude, confirmed by user)

1. **Bench / matchday squad** — split the squad into starters, named substitutes and not selected.
2. ~~**Player availability**~~ — **done (2026-10-30):** status per player (available / injured / suspended / unavailable) via the round button in the squad list.
3. **Preferred positions** — favourite positions per player; warn when someone plays out of position.
4. **Several saved lineups** — one per match/opponent, to compare plan A and plan B.
5. ~~**Sharing**~~ — **done (2026-10-30):** Share button → lineup image incl. substitutes (share sheet on phones → WhatsApp, or download), link via WhatsApp / copy link (read-only view with "Import into my planner").
    - Open: links and phone sharing need the file hosted on HTTPS (any static host, no server code). Not yet tested on a real phone.
6. **Captain and set-piece takers** — armband, penalties, corners, free kicks.
7. **Smaller youth formats** — 5-, 7- and 9-a-side pitches and formations.
8. **Playing-time tracker** — substitution times and minutes per player over a season (fair playing time in youth football).
9. **Tactics board mode** — draw arrows/runs on the pitch, notes per position.
10. **Backup / restore** — export/import all data as a file, also to move it to another device.

## Bigger ideas (from the user)

11. **fussball.de data** — import squads, fixtures, results from fussball.de.
    - To check first: fussball.de has no official public API that we know of; check what data access is allowed (terms of use) before building any import or scraping.
12. **Player pictures** — photo per player, shown on the pitch and in the squad list.
13. **Login + web deployment** — accounts so coaches can use it online and keep their data across devices.
    - **Deferred (2026-10-30):** user decided to skip the server/login part for now. Keep the app serverless; don't plan other items around a backend.
14. **Android / iOS app** — mobile app version.
15. **GitHub Pages hosting** — publish `index.html` on GitHub Pages (static, HTTPS, no server code). Needed for share links and for sharing images to WhatsApp on phones (see 5); also the base for the PWA (14).
    - Done (2026-10-30): git repo + public GitHub repo https://github.com/jhoxyz/torfunk.
    - Still to do: enable Pages (repo Settings → Pages → branch `main`, folder `/`) → https://jhoxyz.github.io/torfunk/
    - Note: a public Pages site is visible to anyone with the URL. Squad data stays in each browser, but a share link contains the whole squad.

16. ~~**Live ticker with WhatsApp sharing**~~ — **done (2026-10-30):** tab "Live-Ticker", German messages, one person runs it.
    - Built: team name + short name (kept), opponent + short name, home/away, half length; clock with minute correction; phase button (Anpfiff → Halbzeit → 2. Halbzeit → Abpfiff); events goal / goal against (opponent shirt number) / substitution (several at once) / card / chance / note; WhatsApp preview; event log (resend, edit, delete); kickoff message with lineup, final summary. Substitutions and red cards update the lineup. Screen stays on during the match (https only).
    - Decided: one ticker person only; German messages; opponents are identified by shirt number only.
    - Not yet tested with real WhatsApp on a phone.
    - Original notes:
    - **WhatsApp formatting available** (plain text with markers, no colours/headings/tables):
      `*bold*`, `_italic_`, `~strikethrough~`, ` ```monospace``` `, `` `inline code` ``,
      lists (`- item` / `* item`, `1. item`), quotes (`> text`), line breaks and emojis (⚽ 🟨 🟥 🔁 ⏱️ 🏁 🧤 🎯 …).
      Links get a preview. Markers only work when they touch the words (`*1:0*` works, `* 1:0 *` doesn't).
    - **Claude's input — how it could work:**
      - Ticker screen with a match clock (start, half-time, second half, end) and big buttons: goal, goal against, chance, yellow/red card, substitution, injury, free note.
      - Pick players from the lineup instead of typing; substitutions update the lineup on the pitch (and later feed the playing-time tracker, item 8).
      - Score and minute are filled in automatically; each event becomes a ready message, e.g.
        `⚽ *TOR! 1:0* (23')` / `_Anna_ trifft nach Vorlage von _Bea_`
        `🔁 *Wechsel* (60')` / `⬆️ Cleo` / `⬇️ Dana`
        `🏁 *Abpfiff: 2:1*` + short summary (goals, cards) as a list.
      - Kick-off message with the lineup (text version of the share image) and a final summary.
      - Sending: one tap opens WhatsApp with the text filled in (share menu, or a `wa.me` link — the link also works on plain http); the user picks the group once and presses send. The last chat is usually on top, so it's quick.
      - Keep a log of all events in the match, editable afterwards (wrong minute, wrong scorer).
    - **Limits to know:**
      - There is no official way for a normal WhatsApp group to receive messages automatically — every message needs one tap on "send" by the person ticking.
      - Two tickers at once: without a server their phones don't share score/events. Options: agree who ticks what, or hand over the ticker state with a link (like share links, item 5).
    - **To decide:** message language (German/English, or selectable) and team/opponent names for the score line.

17. **Photos and videos in the live ticker** (user idea, 2026-10-30) — take a photo or video during the match and send it to WhatsApp together with the ticker text.
    - **Claude's input — how it could work:**
      - Camera button in the ticker (and optionally in each event dialog, e.g. the goal): `<input type="file" accept="image/*,video/*" capture>` opens the phone camera directly; picking from the gallery also works.
      - Caption filled in automatically: minute, score, event (e.g. `⚽ *TOR für SVM!* (23.) *SVM 1:0 FCM*`).
      - Photos: optionally burn a small score banner into the picture (`SVM 1:0 FCM · 23.`), drawn on a canvas like the lineup image — no library needed. Not possible for videos without heavy processing.
      - Sending: share menu with the file (`navigator.share({ files })`), like the lineup image. Needs **https** (laptop: `serve-https.py`, later GitHub Pages); on plain http only "save to phone, then attach in WhatsApp".
      - Event log shows that a photo/video was sent (small thumbnail for photos).
    - **Limits to know:**
      - Some WhatsApp versions drop the caption when a file and text are shared together → test on real phones; fallback: send the photo, then the text as a second message.
      - Don't store videos in the app (browser storage is only a few MB). Photos at most as small thumbnails, or not at all.
      - Long videos are big over mobile data; short clips (≤ 30 s) work best. The browser can't compress videos easily.
    - **Privacy:** youth teams — photos/videos of children need the parents' consent (DSGVO). Worth a short reminder in the app before the first photo, and an agreement in the team.

## Architecture notes for the bigger ideas

- Items 11, 13 and 14 (and storing pictures across devices for 12) don't fully fit the current setup: one HTML file, no backend, works offline. They need a backend (auth + database + file storage). Decide on the stack with the user before starting and update `AGENTS.md` once decided.
- A possible first step towards 14: make the web app an installable PWA (offline, home-screen icon) before building native apps.
- With the server deferred: pictures (12) can be stored locally in the browser and included in backup/restore (10); the app (14) can start as a PWA; fussball.de (11) would have to work without our own server, so check what is possible.
