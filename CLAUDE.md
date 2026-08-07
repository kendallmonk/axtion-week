Axtion Week — Claude Code Instructions
Also read `../SHARED-CONTEXT.md` for cross-project facts (entities, sibling repos, hard cross-project rules). This file covers what's specific to Axtion Week.
What this is
Axtion Week is Kendall's weekly operating rhythm — a single-page view of work blocks, domains, and principles for the week.
Stack

* Single static `index.html` file — no separate CSS/JS files, no package.json, no `src/` folder, no build step
* Only external dependency is a Google Fonts import (Inter)
* Deployed via GitHub → Vercel auto-deploy
* `index.html` must stay at repo root — Vercel 404s otherwise
* Primary edit workflow is often direct GitHub web edits (pencil icon), not local commits — be extra careful with whole-file pastes, a partial paste can silently corrupt the page since there's no build step to catch it

Visual identity
Navy/neutral palette (`--navy`, `--neutral`, `--text`), Inter throughout. Domains are color-coded via CSS custom properties: work (blue), health (green), family (orange), flex (purple), rest (teal), med (amber), elliot (gold), read (blue-teal), ba (teal), una (pink) — confirm with Kendall what each of these domains represents before assuming; don't rename or repurpose a color without checking.

Password gate & storage bridge
Same postMessage bridge contract as Mission Vitals and Free Money, implemented inline in `index.html`:

* Request: `pos-storage-get`
* Reply: `pos-storage-get-reply`, keyed by `requestId` (not `reqId`)
* Write: `pos-storage-set` — fire-and-forget, no reply

Falls back to direct `localStorage` when opened standalone (not embedded in POS), detected via `window.self !== window.top`. Password gate uses the shared SHA-256 hash, same pattern as the other apps.
If POS's bridge contract ever changes, this file's `bridgeGet`/`bridgeSet` functions need to be updated to match — check POS's `CLAUDE.md` or `script.js` as the source of truth, don't assume.
Working style
Preview before write, always. Flag assumptions explicitly. Direct, no preamble. Ask before proceeding on anything ambiguous. Australian English in user-facing copy.
Known recurring deployment gotchas

* No build step means no safety net for a bad paste — verify the file still renders after any manual edit, especially GitHub web edits.
* Downloaded files sometimes have dots converted to hyphens/underscores — check filenames after upload.
