# Butts Studios — Status (rolling snapshot, kept true by the Butts Studios CoS)

*Last updated: 2026-10-16 ~05:06 ET (sections + subdomains audit). Source of truth for direction:
`~/latarence/coordination/dispatch/2026-10-07_STUDIOS_new_site.md`. Seat: `Organization/Chief-of-Staff/README.md`.*

## Now
| Area | State | Next | Gate |
|---|---|---|---|
| New buttsstudios.com (`site/`) | Built locally: slate, how-we-work, partnerships, portfolio (25 item pages), Books / Video / Games section landings, full footer, OG/meta on all 41 pages, 375px fixes, no .99 prices. Logo C5. Latest `3629c2b`. **Not deployed.** | Fill the legal blanks; deploy | Principal: deploy go + Vercel token (setup sheet) + legal answers (governing-law state, mailing address, refund terms) |
| Sections + subdomains (Principal 10-16) | **Audit:** the front pages Books / Video / Games exist on the new site (local). All **8 live subdomains** (games, glb, cards, puzzle, novels, film, animation, clients) were the old magenta template, with no C5 mark, no link to their section front page and no legal links. **Staged:** one shared style (`site/shared/studios-section.css` + `bar.tmpl`/`foot.tmpl`, `scripts/apply_studios_sections.py`). It has a C5 bar ("Butts Studios / Section / product"), Books·Video·Games nav and a shared footer with Terms/Refunds/Privacy. Each section has one accent (Books gold, Video red, Games green, Partnerships brass). It is on branch `style/studios-sections-2026-10-16` in all 8 repos, and the front pages have a sections sub-nav. Preview: `staged/sections_preview/index.html`. **Not deployed.** | `staged/sections_go_2026-10-16.sh go` after the new site and the games GO are live. Content calls: film's invented works, animation's placeholders, the dead clients login and novels newsletter (STATUS issues list / channel 10-16 09:06Z) | Principal: deploy go + GitHub push login + Vercel token |
| Legal pages | Seller = the project's own name everywhere. Site: 29 fill-ins left; legacy subdomain drafts: 171 (same few blanks repeated). The 9 old live sites have no legal pages yet (drafts staged). | Fill once answers land; launch guards block deploy until then | Principal (JARVIS legal row) |
| Games (cards, puzzle, GLB, hub) | `?premium=true` bypass closed (unlock only after a verified paid Stripe session); false claims removed; GLB copy matches one-time charge. New prices $5 / $3 on `price/no-99-2026-10-15` branches. | Run `staged/games_go_2026-10-15.sh` | Principal: restricted read-only Stripe key + new $5/$3 Payment Links with session redirect (setup sheet rows) + deploy go |
| Shops (Runwae Apparel, GLB, Butts Studios store) | Shared cart → Stripe Checkout (TEST), order + checkout emails, real inventory, print placement rules enforced by tests. Local commits. | Test-mode order walk, then deploy | Stripe TEST keys, Resend key, Printful/Shippo keys, GoDaddy/DNS, Vercel (setup sheet rows) |
| runwaeapparel.com | Down (holding page built) | Deploy holding page | Vercel token + 2 GoDaddy records |
| Email | hello@ / support@ on buttsstudios.com, runwaeapparel.com, girlslovebutts.com bounce (no mail routing). GLB "Restore purchase" points at support@buttsstudios.com. | Cloudflare Email Routing catch-all | Setup sheet row "buttsstudios.com email" (in progress with the Principal) |
| Socials | Instagram is the only live account; TikTok / FB / Threads / X / Bluesky / Pinterest "to create" | Add to footer as each becomes real | Principal accounts; posting needs per-batch OK (Buffer) |
| Messaging | Principal 2026-10-15: never combine "good design" with "made of story" (the combined line is withdrawn). `design/MESSAGING.md` being corrected; home line still open | Rewrite messaging without the combination | Principal taste call |

## Open Principal decisions (JARVIS)
- Home page line; apps & games branding (naming, GLB game vs GLB apparel name clash); drafts-store terms (do v0.1 buyers get later drafts?); legal answers above; The Signal on the slate.

## Recent (newest first)
- 2026-10-16: sections + subdomains audit; the shared Studios section style is staged on all 8 subdomain repos plus the front pages (not deployed). Issues found: film lists invented works; animation has placeholders; the clients login and the novels newsletter are non-functional; the in-game "free games" copy is fixed on the branch.
- 2026-10-15/16: legal seller names = project names; games premium bypass + honest copy; no .99 prices; site polish; section landings; full footer; Runwae v5 storefront; merch = cart + Stripe only, Huntington Applied merch first.
