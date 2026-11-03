# Butts Studios — Status (rolling snapshot, kept true by the Butts Studios CoS)

*Last updated: 2026-11-03 (Bridge, after the Studios surge deploys; earlier: studios-surge-1 FS-50 / FS-54 / FS-59 reconciliation; every claim below was checked
with a curl or a git/file check at that time unless marked "unverified"). Direction (verbatim, dated):
`~/latarence/docs/DECISIONS.md` (2026-10-28 URL rule and subdomain cleanup; 2026-11-02 nav, shop naming, no subdomains).
Older direction: `~/latarence/coordination/dispatch/2026-10-07_STUDIOS_new_site.md`. Seat: `Organization/Chief-of-Staff/README.md`.*

## Three states, kept distinct
- **Live** = answers on buttsstudios.com right now (curl 200). **Built** = committed on a pushed branch, not deployed.
  **Retired** = removed on purpose (404 by design, no forwarding; DECISIONS 2026-10-28).

## Source and deployment (updated 2026-11-03)
- **Live revision:** `origin/main` @ `fa91d41` (About / Releases / Work / Shop plus the Studios surge fixes). Deployed in two steps on
  2026-11-02 with `scripts/deploy_new_site.sh --go` (first `6494694`: a11y, SEO, legal-text and subdomain-reference fixes; then `fa91d41`:
  security headers and the `/releases` layout-shift fix). Both printed VERIFIED LIVE and were re-checked by hand. **main now equals live**
  (earlier it lagged the live revision `460352d` by two commits).
- **Rollback:** `vercel rollback https://butts-studios-website-3ojtpyt3q-buttsstudios-projects.vercel.app --scope team_WMhVBeGTHA1CgDK9llwAmQd9`
  (the deployment before the headers deploy; the one before that is `butts-studios-website-icgongrbb-buttsstudios-projects.vercel.app`).
- **Deploy path:** CLI-deployed, not git-deployed. The Vercel project is `butts-studios-website`; it is linked to the repo
  `buttsstudios/butts-studios-website` (not `butts-studios`), so pushing to this repo's main deploys nothing. The CLI upload stages
  the site folder, runs the pre-flight checks (url_map, site_links, cohesion, launch_ready) and moves pages to clean paths.
- **Subdomains:** none. novels, cards, puzzle, glb, games and portal were removed from Cloudflare DNS and from Vercel on 2026-11-02 (records
  backed up in `~/latarence/coordination/evidence/2026-11-02/studios-subdomains/`); the mail records (`send`, `rsend`), `www` and `_domainconnect` stay.
- **Backends behind the paths** (from `site/vercel.json`): `/games/glowgrid` -> `glb-game`, `/games/cards` -> `butts-cards`,
  `/games/sliding-numbers` -> `butts-puzzle`, `/shop` -> `shop-buttsstudios`. They are live, not orphans. Real orphans: `butts-games`, `portal`,
  `the-signal-novel` (still serves the old pre-order page at its `*.vercel.app` address; JARVIS STUDIOS-INFRA D3).
- **Game repos:** `glb-game` main `ddacc32` is live (stylesheet path, Glowgrid naming, hello@ contact, working legal links). Branches
  `fix/subdomain-refs-20261102` on `butts-cards`, `butts-puzzle`, `butts-games` are built with static checks only; they need a Next build and a
  browser smoke on xps before they go to main (those repos auto-deploy and the games sell a paid unlock).
- **Shops** (GLB, Runwae Apparel, `/shop`; one storefront in the MDO3 repo, local only by guard): the Studios shop shows no planning wording;
  GLB and Runwae still do until `~/shipshops.sh` is run (Principal's line, JARVIS STUDIOS-SURGE item 8).
- **Checks that gate a deploy:** `scripts/check_cohesion.py`, `check_site_links.py`, `check_url_map.py`, `check_removed_hosts.py`,
  `check_a11y_seo.py`, `check_security_headers.py`, `check_browser_a11y.py` (Playwright; xps only). Run them on xps, not on the laptop.
- **Open for the Principal:** JARVIS `STUDIOS-SURGE` (legal defaults, "nothing is on sale" vs the paid games, Glowgrid How to play, infra, palette, storefront guard);
  SETUP_TODO `[CF-STUDIOS-EDIT]`, `[STUDIOS-SHOP-MAIL]`, `[STUDIOS-FIREBASE-KEY]`. Detail: `~/latarence/coordination/studios_surge_2026-11-02/README.md`.

## URL map (live, path-based; no subdomains)
| Path | State | Checked |
|---|---|---|
| `/` (About), `/releases`, `/work`, `/how-we-work`, `/shop`, `/contact` | Live 200 | curl 2026-11-02 |
| `/books`, `/video`, `/games`, `/channels` | Live 200 | curl 2026-11-02 |
| `/titles/the-signal`, `/titles/talon` | Live 200 | curl 2026-11-02 |
| `/titles/the-little-things`, `/titles/us-against-the-world`, `/video/film`, `/video/animation` | In `scripts/url_map.py` at 460352d; live status **unverified** | — |
| `/games/glowgrid`, `/games/cards`, `/games/sliding-numbers` | Live 200 (proxied from their own Vercel projects, `url_map.py` GAMES) | curl 2026-11-02 |
| `/refunds`, `/terms`, `/privacy` | Live 200 | curl 2026-11-02 |
| `/slate`, `/portfolio`, `/partnerships`, `/services`, `/about`, `/titles/tobe`, `/games/brace` | 404 (retired or never published; `/about` is `/`) | curl 2026-11-02 |
| `novels.`, `film.`, `animation.`, `shop.`, `games.`, `glb.`, `cards.`, `puzzle.`, `portal.` `.buttsstudios.com` | **Removed**: do not resolve (DNS CNAMEs deleted, Vercel domains detached 2026-11-02; backups `~/latarence/coordination/evidence/2026-11-02/studios-subdomains/*.json`) | curl 2026-11-02 (novels, film, animation, shop, games: no resolve) |

Rules: parts of the brand are **paths** (DECISIONS 2026-10-28); **Butts Studios has no subdomains** (DECISIONS 2026-11-02,
"if any subdomain exists for butts studios it hsould be removed"). Kept on purpose because they are not sites: `www`
(apex alias), `send`/`rsend` (Resend mail CNAMEs), `_domainconnect`. Open conflict to settle before it is created:
`sega.buttsstudios.com` (DECISIONS 2026-10-26) vs the no-subdomain rule.

## Now
| Area | State | Next | Gate |
|---|---|---|---|
| buttsstudios.com nav | **Live:** About (= `/`) · Releases (own titles: books, comics, video, games) · Work (made for others) · Shop. Footer columns Releases / Studio / Shop. "Client"/"internal" are not labels (DECISIONS 2026-11-02). Hero stats strip removed. | Fast-forward `origin/main` to `460352d` | Bridge push to main |
| Shops (Butts Studios `/shop`, Runwae Apparel `runwaeapparel.com`, GLB `girlslovebutts.com`) | **Live, waitlist-only:** every product shows Reserve / Waitlist / Pre-order; nothing purchasable (DECISIONS 2026-10-28 "Applies to every shop"). All three answer 200. **Copy gap on live `/shop`:** the `Collection 2027` heading is still live (3 hits) and the word `planned` appears 6–9× in each shop's HTML (visible or not: unverified). The rename to Shop → Apparel · Accessories · Objects with no "planned" labels is committed **local only**: mdo3d worktree `~/.wt/studios-shop-naming`, branch `fix/studios-shop-naming-20261102` @ `d261709` (112 tests pass on xps). | Ship via the shop deploy lane | mdo3d pre-push guard refuses the push (storefront is private, public repo; see ledger SHOP-OBJECTS-NAMING-20261102). The Principal decides how the private storefront moves (see the 2026-11-02 surge report) |
| Shop code location | Runwae Apparel + the shared storefront (Runwae, GLB, Studios store): `~/mdo3d/projects/external/runwae-apparel/` (private files in a public repo; never pushed to origin by rule). | — | — |
| Games | Live at `/games/glowgrid` (the canvas game, formerly "GLB game"; renamed 2026-10-16), `/games/cards`, `/games/sliding-numbers`. Stripe Payment-Link return URLs use `buttsstudios.com/games/*` (read-only Stripe check by the latarence seat, DECISIONS 2026-11-02; not re-run here). Premium prices $5 / $3 / $3 (no .99). Brace: not public (`/games/brace` 404; repo `games/brace/`). | Premium checkout stays gated | Live Payment Links + Principal GO |
| GLB on the Studios site | **Off the site entirely** (DECISIONS 2026-11-02 "GLB stays off"). GLB = the apparel brand at `girlslovebutts.com` only. If ever shown it belongs under Releases, not Work. Runwae Apparel stays on `/work` as design work, with no subsidiary statement. | — | Principal |
| Books / titles | `/books` + `/titles/*` carry no payment link; the old `novels.` pre-order page is unreachable (domain removed; stale Vercel project `the-signal-novel` still exists without a public address). | Delete or archive the orphan Vercel project (optional) | Vercel token |
| Legal | `/terms`, `/privacy`, `/refunds` live 200. Fill-in state (governing law, address): **unverified** this pass; see JARVIS L1. | — | Principal (JARVIS L1) |
| Contact | `/contact` live 200 (form; footer shows a Contact link, not an address, DECISIONS 2026-10-28). | — | — |
| Socials | **Instagram is the only live social**: the live home footer links `instagram.com/buttsstudios` and no other network (curl 2026-11-02). Facebook Page approved to create under the latarencejbutts login (DECISIONS 2026-11-01); Etsy shops on the latarencejbutts Etsy account (DECISIONS 2026-10-31); Tumblr dropped; Sketchfab deferred. | Add footer links only as each account becomes real | Principal accounts; posting needs per-batch OK |
| Email | hello@/support@ routing state: **unverified** this pass (last recorded 2026-10-16: bouncing; Resend CNAMEs `send`/`rsend` now exist on the zone). | Check MX/routing | Setup sheet row "buttsstudios.com email" |

## Open ledger rows (studios) — `python3 ~/latarence/coordination/fixledger/fixledger.py show <ID>`
- `SHOP-OBJECTS-NAMING-20261102` blocked: private storefront cannot be pushed from the public mdo3d repo (guard).
- Fast-forward of `origin/main` to the live `460352d` (recorded above; not a ledger row yet, Bridge action).

## Open Principal decisions (JARVIS ids, `~/jarvis/JARVIS QUESTIONS.md`)
- **L1** governing law + address · **BR1–BR3** Brace name / platforms / classroom · **AP1** apparel identity pick ·
  shop naming word "Objects" and nav word "Services"/"Work" are Bridge picks he may change (DECISIONS 2026-11-02).

## Recent (newest first)
- 2026-11-02: nav About / Releases / Work / Shop shipped from `fix/studios-work-organize-20261102@460352d` (CLI deploy);
  all six leftover subdomains (novels, cards, puzzle, glb, games, portal) removed from DNS and Vercel; hero strip removed;
  shop naming (Apparel · Accessories · Objects, no "planned") committed local-only in mdo3d; docs reconciled (FS-50/54/59).
- 2026-10-28: URL rule (paths, not subdomains); `/contact` page; Studio · Work · Shop header on main (`3aa4821`);
  Runwae Apparel redesign direction (luxury, no ancient motif); waitlist-only rule for every shop.
- 2026-10-16/17: legal pages live; Glowgrid rename; Brace chosen; sections style staged (now superseded by the path-based site).

## Archive: snapshot of 2026-10-17 (superseded; kept for history)
Rows: `~/latarence/coordination/P0_SPRINT_2026-10-16.md` (XE-*); ships: `~/latarence/coordination/MANUAL_SHIP_QUEUE.md`.
That snapshot described the sections/subdomain style branches (`style/studios-sections-2026-10-16`), the 8 live subdomains,
`portfolio`/`partnerships`/`slate` pages and site revision `3629c2b`. All of that is superseded by the path-based site above:
the subdomains are removed, those pages are retired (404 by design), and the live revision is `460352d`.
Still-true items from it: Brace report `staged/new_game_2026-10-16/`; product-shot library
`~/latarence/coordination/product_shots/manifest.json`; messaging rule "never combine good design with made of story"
(`design/MESSAGING.md`); apparel playbook `~/mdo3d/projects/external/runwae-apparel/APPAREL_PLAYBOOK.md`.
