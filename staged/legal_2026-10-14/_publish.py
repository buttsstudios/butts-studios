#!/usr/bin/env python3
"""Publishable legal pages for buttsstudios.com, games. and glb. (P0 sprint XE-4, 2026-10-17).

Same text base as _generate.py, with the open items filled from DECISIONS:
  - seller = the project name (DECISIONS 2026-10-15), no entity name
  - inbox = buttsstudios@gmail.com (the only Studios address that receives mail; buttsstudios.com has no MX)
  - refund window = 14 days (DECISIONS 2026-10-15 drafts-store answer)
  - prices: "the price shown at checkout" (the live Payment Links still charge .99 amounts; the price
    change ships with games_go_2026-10-15.sh price, so the pages never state a figure that can drift)
Still open (JARVIS): governing-law state and mailing address. Fill-in mechanism: set LAW_STATE /
MAILING_ADDRESS below (or env) and re-run; until then the law clause names no state and the address
line is left out. Output: publish/<slug>/{privacy,terms,refunds}.html. The script fails if any
[CONFIRM ...] marker, "free", ".99" or AHL name survives.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _generate as g

LAW_STATE = os.environ.get("LAW_STATE", "")          # e.g. "Delaware", once the Principal answers JARVIS L1
MAILING_ADDRESS = os.environ.get("MAILING_ADDRESS", "")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publish")
ADDR = "@@ADDR@@"
INBOX_ADDR = "buttsstudios@gmail.com"

g.ADDRESS = MAILING_ADDRESS or ADDR
g.INBOX = f'<a href="mailto:{INBOX_ADDR}">{INBOX_ADDR}</a>'
g.LAW = LAW_STATE or "@@LAW@@"
g.DATE = "17 October 2026"
g.WINDOW = "14 days"

P = g.PROPS
P["buttsstudios.com"]["processors"] = [x for x in P["buttsstudios.com"]["processors"] if "CONFIRM" not in x]
P["buttsstudios.com"]["collect"][0] = ("<strong>Contact form.</strong> First name, last name, email, optional phone number and "
    "your message, if you submit the form on the Contact page. The form is being reconnected; until then, please email us directly.")

P["buttsstudios.com"]["retention"] = [r.replace("[CONFIRM: retention period, e.g. 24 months]", "24 months") for r in P["buttsstudios.com"]["retention"]]

P["games"].update(
    refund_rules=[f"Within {g.WINDOW} of purchase, for any reason: full refund on request.",
                  "Lost your unlock after clearing browser data or changing device: we restore it rather than refund, on request with your receipt."],
    offer="This page lists our browser games (GLB, Butts Cards and Butts Puzzle). Each game lets you try a limited amount of play before you buy, and sells a one-time unlock. Each game's own terms and privacy policy also apply when you play it.",
    purchase_terms="Each unlock is a one-time purchase for that game, at the price shown on this page and on the Stripe checkout page before you pay. There is no subscription and no recurring charge. Unlocks are tied to the browser where they are applied; email us with your receipt to restore one.",
    items_table=g.items([("GLB full unlock", "As shown at checkout, one-time", "Unlimited levels"),
                         ("Butts Cards full unlock", "As shown at checkout, one-time", "Unlimited daily games"),
                         ("Butts Puzzle full unlock", "As shown at checkout, one-time", "Unlimited daily games and 5x5 boards")]),
)
P["glb"].update(
    offer="GLB is a canvas browser game. Levels 1 to 5 are a trial; a one-time unlock opens the levels after that.",
    purchase_terms="The unlock is a one-time purchase at the price shown on the Stripe checkout page before you pay. There is no subscription and no recurring charge. Premium status is stored in the browser you used once the payment is confirmed; email us with your receipt to restore it.",
    items_table=g.items([("GLB full unlock", "As shown at checkout, one-time", "Unlimited levels beyond level 5")]),
    refund_rules=[f"Within {g.WINDOW} of purchase, for any reason: full refund on request. Your premium status is removed when the refund is issued.",
                  "Lost your unlock after clearing browser data or changing device: we restore it rather than refund, on request with your receipt."],
)

LAW_P = re.compile(r"<p>These terms are governed by the laws of the State of @@LAW@@.*?</p>", re.S)
LAW_NEUTRAL = ("<p>The governing law and venue for these terms will be stated here once confirmed. Nothing in these terms "
               "limits the protections that the law where you live gives you as a consumer. Please contact us first; most "
               "issues can be resolved quickly by email.</p>")

def finish(html):
    html = html.replace('<meta name="robots" content="noindex">\n', "")
    html = re.sub(r'<div class="draft">.*?</div>\n', "", html, flags=re.S)
    html = LAW_P.sub(LAW_NEUTRAL, html)
    html = html.replace(f", {ADDR}.", ".").replace(f"<br>{ADDR}", "").replace(ADDR, "")
    # clean URLs: pages are served at /privacy, /terms, /refunds (vercel.json cleanUrls)
    html = re.sub(r'href="(privacy|terms|refunds)\.html"', r'href="/\1"', html)
    return html

BAD = [r"\[CONFIRM", r"@@", r"\bfree\b", r"\.99\b", r"Anne Huntington", r"\bAHL\b", r"(Butts|Studios|GLB|Games)[A-Za-z ]*,? LLC"]

def main():
    slugs = sys.argv[1:] or ["buttsstudios.com", "games", "glb"]
    fails = 0
    for slug in slugs:
        p = P[slug]
        d = os.path.join(OUT, slug); os.makedirs(d, exist_ok=True)
        pages = {"privacy": g.privacy(p), "terms": g.terms(p)}
        if p["sells"]:
            pages["refunds"] = g.refunds(p)
        else:
            q = dict(p, sells=True)  # footer gets a Refunds link
            pages["refunds"] = g.page(q, "Refund Policy", """<h2>1. Purchases on this site</h2>
<p>Nothing is sold on buttsstudios.com itself. Project work for clients is covered by each client's written agreement.</p>
<h2>2. Purchases on our other sites</h2>
<p>Each site that sells something has its own refund policy, which applies to purchases made there:</p>
<ul>
<li>Games and game unlocks: <a href="https://games.buttsstudios.com/refunds">games.buttsstudios.com/refunds</a> and <a href="https://glb.buttsstudios.com/refunds">glb.buttsstudios.com/refunds</a></li>
</ul>
<h2>3. Contact</h2>
<p>Questions about any purchase: """ + g.INBOX + """. Please include your Stripe receipt or the email address you paid with.</p>""")
        for name, html in pages.items():
            html = finish(html)
            for b in BAD:
                for m in re.finditer(b, html, flags=re.I):
                    fails += 1; print(f"FAIL {slug}/{name}: {b} -> {html[max(0,m.start()-60):m.end()+60]!r}")
            open(os.path.join(d, name + ".html"), "w").write(html)
    print("FAILS", fails)
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
