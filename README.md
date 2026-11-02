# Butts Studios

> **You are here:** org root, Butts Studios · **Up:** the latarence head, `~/latarence/docs/ORG_STRUCTURE.md` ·
> **Down:** the projects below · **CoS seat:** [`Organization/Chief-of-Staff/README.md`](Organization/Chief-of-Staff/README.md) ·
> **HQ channel:** [`coordination/COS_CHANNEL.md`](coordination/COS_CHANNEL.md) · **Live state:** [`STATUS.md`](STATUS.md) (dated; live/built/retired kept distinct) ·
> **Direction (verbatim, dated):** `~/latarence/docs/DECISIONS.md` (2026-10-28 URL rule; 2026-11-02 nav, shop naming, no subdomains); earlier `~/latarence/coordination/dispatch/2026-10-07_STUDIOS_new_site.md` · **Agent rules:** `CLAUDE.md` → `AGENTS.md`

## Projects (local folder → public destination)

**buttsstudios.com is one path-based site; Butts Studios has no subdomains** (DECISIONS 2026-10-28, 2026-11-02; the
leftover `novels.`/`cards.`/`puzzle.`/`glb.`/`games.`/`portal.` hosts were removed 2026-11-02, no forwarding).

| Folder | What | Public destination |
|---|---|---|
| [`site/`](site/) | buttsstudios.com: About (`/`), Releases (`/releases`, `/books`, `/video`, `/channels`, `/titles/*`), Work (`/work`, `/how-we-work`), Shop (`/shop`), `/contact`, legal (`/terms`, `/privacy`, `/refunds`). URL map: `scripts/url_map.py`; deploy: `scripts/deploy_new_site.sh` (CLI deploy to the Vercel project `butts-studios-website`) | buttsstudios.com |
| [`website/`](website/) | The old site, kept untouched (history) | none |
| [`games/`](games/) | Games, each its own Vercel project, served under the site by proxy: Glowgrid (`games/glb/`, the canvas game; renamed from "GLB" 2026-10-16, unrelated to the apparel brand), Card Battle (`cards`), Sliding Numbers (`puzzle`), Brace (`games/brace/`, not public) | buttsstudios.com/games/glowgrid · /games/cards · /games/sliding-numbers |
| [`publication/`](publication/) | Books: ToBe, The Signal, Talon | buttsstudios.com/books · /titles/* |
| [`youtube/`](youtube/) | "The Channels" (the YouTube channels) | youtube.com · buttsstudios.com/channels |
| `~/mdo3d/projects/external/runwae-apparel/` | **Runwae Apparel** (subsidiary brand) and the shared storefront (Runwae, **GLB**, Butts Studios `/shop`). Files live in the MDO3 repo (private files; never pushed to the public remote); this CoS owns them | runwaeapparel.com · girlslovebutts.com · buttsstudios.com/shop (all waitlist-only) |

- **GLB / Girls Love Butts** is the apparel brand at girlslovebutts.com and stays **off** the Studios site (DECISIONS
  2026-11-02). Runwae Apparel appears on `/work` as design work only.
- The Runwae **app** (runwae.com) is an MDO3 product, separate from Runwae Apparel.
- Socials: Instagram (`instagram.com/buttsstudios`) is the only live account.
