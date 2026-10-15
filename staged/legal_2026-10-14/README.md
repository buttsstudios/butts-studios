# Legal pages, legacy Butts Studios properties (staged 2026-10-14)

Draft Privacy / Terms / Refund pages for the nine live legacy properties, written from a live audit
(curl of each site on 2026-10-14) plus a read of the source. Practical hygiene, not legal advice.
**Nothing here is deployed, pushed or committed.** Each repo's git remote may need a push login, which
is blocked from this seat, so placement and deploy are left to the owning lane.

Every page carries a yellow "Draft, not yet in effect" banner, `<meta name="robots" content="noindex">`,
and `Last updated: [CONFIRM: effective date]`. Before publishing: fill every `[CONFIRM: …]`, delete the
banner, remove the noindex tag. `_generate.py` rebuilds all pages from one shared text base
(`python3 _generate.py`); edit the constants at the top (address, inbox, state, window; the seller is each property's own project name, DECISIONS 2026-10-15) once
and regenerate rather than hand-editing nine folders.

## Audit summary (live, 2026-10-14)

All nine hosts return HTTP 200 (Vercel). **None has a privacy policy, terms or refund page**:
`/privacy`, `/privacy.html`, `/terms`, `/terms.html`, `/refunds`, `/refund`, `/returns`, `/legal`,
`/contact` all return 404 on every host. Only buttsstudios.com has `/contact.html` (200). No page has a
legal footer, and no page names a legal entity. No analytics, ad or tracking scripts were found on any host.

Dead contact inboxes:
- `butts-studios.com` (hyphenated) has **no DNS at all** (no A, no MX). It is used live for
  `film@`, `animation@`, `clients@`, `support@` and for the "Studios" footer link on novels/film/animation.
- `buttsstudios.com` has **no MX record** (`dig MX buttsstudios.com +short` is empty). The local,
  undeployed sources already swap the hyphenated addresses for `@buttsstudios.com` (e.g.
  `apps/butts-clients-next/index.html`, `clients@buttsstudios.com`), and the new `site/terms.html` uses
  `hello@buttsstudios.com`; **those will not receive mail either** until MX is set up.
- `buttsstudios@gmail.com` (main site) is the only working address found.

| Property | Sells | Data handled | Processors | Contact used | Key findings |
|---|---|---|---|---|---|
| buttsstudios.com | No | Contact form: first/last name, email, phone, message | Vercel, cdnjs, CloudFront (Webflow jQuery) | buttsstudios@gmail.com (works) | HIGH: data-collection form, no privacy policy. MED: form POSTs to `email.php`, which Vercel serves as a static file (POST returns 405), so submissions fail silently; PHP source is publicly downloadable (no secrets in it). LOW: Webflow template, no footer, no entity, no copyright line. |
| novels. | Yes, $9.99 pre-order (Stripe Payment Link, live) | Stripe checkout; "Stay Connected" email field | Vercel, Stripe, Google Fonts | none; footer links to dead butts-studios.com | HIGH: live payment, no privacy/terms/refund; pre-order of an "In Progress" book with no delivery date or pre-order refund terms. MED: newsletter form has no action/name and sends nothing, yet promises updates (honest-claims issue). |
| film. | No | mailto only | Vercel | film@butts-studios.com (DEAD, no DNS) | MED: dead inbox is the only contact path; no privacy/terms. LOW: dead "Studios" link. Portfolio items (e.g. 2026 titles) should be checked for accuracy. |
| animation. | No | mailto only | Vercel | animation@butts-studios.com (DEAD) | MED: dead inbox; no privacy/terms. LOW: placeholder portfolio names ("Project Alpha"). |
| games. | Yes, 3 Stripe links ($4.99/$2.99/$2.99, all live) | Stripe checkout | Vercel, Stripe | none | HIGH: live payment, no terms/refund/privacy. HIGH: GLB shown as $4.99 one-time here but $4.99/month in-game. MED: "Play Free" copy conflicts with lab paid-only policy (Principal call). LOW: links to unresolvable portal.buttsstudios.com (og-image) and *.vercel.app duplicates. |
| cards. | Yes, $2.99 one-time (Stripe link live) | Player name to public leaderboard + localStorage (name, daily tries, last played, premium flag) | Vercel, Firebase Firestore (Google), Stripe | none | HIGH: personal data (name) written to a public Firestore leaderboard and payments, no privacy policy. HIGH: "ad-free experience" (site has no ads) and "yours forever" while premium lives only in localStorage with no restore path. LOW: `?premium=true` URL unlocks premium without paying. |
| puzzle. | Yes, $2.99 one-time (Stripe link live) | Same as cards (Firestore leaderboard, localStorage) | Vercel, Firestore, Stripe | none | Same as cards (HIGH x2, LOW bypass). |
| glb. | Yes, "$4.99 /month" | localStorage `glb_premium` | Vercel, Stripe (Stripe.js live key + Checkout) | support@butts-studios.com (DEAD) | HIGH: payment, no legal pages. HIGH (false statements): paywall advertises "New Game Modes", "No Ads", "Leaderboards", none exist. HIGH: checkout broken: "Subscribe Now" opens `buy.stripe.com/glb-premium` (403) and `redirectToCheckout` uses placeholder `price_glb_premium` in one-time `payment` mode while copy says monthly. MED: "Restore Purchase" only shows an alert pointing at a dead inbox. LOW: `?premium=true` bypass. |
| clients. | No | Email + password form (not transmitted: submit handler only shows "coming soon") | Vercel | clients@butts-studios.com (DEAD) | MED: login UI with no privacy notice near the form (data not actually sent, so not High). MED: page advertises "real-time progress", "secure downloads", "one-click approvals" for a portal that does not exist (honest-claims). MED: dead inbox for "Request access". |

## What each folder contains and where it goes

Place files at the web root of each repo so they serve as `/privacy.html`, `/terms.html`, `/refunds.html`.
Several repos have uncommitted local changes and local copies that differ from live; pull/reconcile first.

| Folder | Files | Source path (repo, GitHub org `buttsstudios`) | Notes |
|---|---|---|---|
| `buttsstudios.com/` | privacy, terms | `~/buttsstudios/website/` (`butts-studios-website`, Vercel project `website`) | Local `index.html` and `contact.html` match live. Also fix the contact form handler. |
| `novels/` | privacy, terms, refunds | `~/buttsstudios/publication/the-signal/` (`the-signal-novel`) | Local index differs from live (74 diff lines, 10 dirty files). |
| `film/` | privacy, terms | `~/buttsstudios/production/film/` (`butts-film`) | Local differs from live (8 dirty). |
| `animation/` | privacy, terms | `~/buttsstudios/production/animation/` (`butts-animation`) | Local differs from live (7 dirty). |
| `games/` | privacy, terms, refunds | `~/buttsstudios/games/portal/` (`butts-games`, Vercel project `portal`) | Local differs from live (6 dirty). |
| `cards/` | privacy, terms, refunds | `~/buttsstudios/games/cards/public/` (create `public/`; Next.js app, `butts-cards`; `apps/butts-cards-next` is a second checkout of the same repo) | Link from the paywall modal and start screen. |
| `puzzle/` | privacy, terms, refunds | `~/buttsstudios/games/puzzle/public/` (create `public/`; `butts-puzzle`; also `apps/butts-puzzle-next`) | Same as cards. |
| `glb/` | privacy, terms, refunds | `~/buttsstudios/games/glb/` (`glb-game`) | Fix the paywall copy and checkout before publishing refunds. |
| `clients/` | privacy, terms, `login-notice-snippet.html` | `~/buttsstudios/apps/butts-clients-next/public/` or `~/buttsstudios/clients/portal/` (`butts-clients-next` vs `butts-clients`) | [CONFIRM which repo deploys clients.buttsstudios.com]; both differ from live. Paste the snippet directly under the Sign In button so the privacy notice sits next to the form. |

## Footer snippet (add to every page of each property)

```html
<footer class="legal-footer" style="font-size:.85rem;text-align:center;padding:1.5rem 1rem;color:#888">
  &copy; 2026 [CONFIRM: entity] &middot;
  <a href="/privacy.html">Privacy</a> &middot;
  <a href="/terms.html">Terms</a> &middot;
  <a href="/refunds.html">Refunds</a> &middot;   <!-- only on novels, games, cards, puzzle, glb -->
  <a href="mailto:[CONFIRM: working inbox]">Contact</a>
</footer>
```

In cards/puzzle (Next.js) add it to `app/layout.tsx`; also add a "By purchasing you agree to the Terms
and Refund Policy" line under each Stripe "Unlock" button on games, cards, puzzle, glb and novels.

## Sites with no legal pages at all

All nine: buttsstudios.com, novels, film, animation, games, cards, puzzle, glb, clients.

## Confirmations needed (Principal)

1. Selling/operating entity on all pages: Butts Studios vs Huntington Applied LLC (and which Stripe account the live Payment Links belong to).
2. Mailing address.
3. Governing-law state.
4. Privacy/support inbox: keep buttsstudios@gmail.com, or set up MX for buttsstudios.com; either way replace every @butts-studios.com address.
5. Refund window for digital unlocks (draft suggests 14 days) and pre-order delivery date / latest-delivery auto-refund date for The Signal.
6. GLB pricing model: $4.99 one-time or $4.99/month (and remove the nonexistent paywall features or build them).
7. "Play Free" / limited-play-without-purchase model on the games vs the lab's paid-only policy.
8. Novels email provider (or remove the sign-up form); clients portal: remove the login UI until live, or confirm the auth provider.
9. Effective date for all pages.
