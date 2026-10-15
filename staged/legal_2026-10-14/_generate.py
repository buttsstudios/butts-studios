#!/usr/bin/env python3
"""Generate draft legal pages for legacy Butts Studios properties from one shared text base."""
import os, html

OUT = os.path.expanduser("~/buttsstudios/staged/legal_2026-10-14")

ENTITY = "[CONFIRM: operating/selling entity, Butts Studios or Huntington Applied LLC]"
ADDRESS = "[CONFIRM: mailing address]"
INBOX = "[CONFIRM: privacy inbox; buttsstudios@gmail.com is the only address that receives mail today]"
LAW = "[CONFIRM: governing-law state]"
DATE = "[CONFIRM: effective date]"
WINDOW = "[CONFIRM: returns window, e.g. 14 days]"

CSS = """
:root{--bg:#ffffff;--fg:#1d1d1f;--muted:#5f5f66;--line:#d9d9de;--note:#fff6d6;--noteline:#e6cf7a;--link:#6a1b9a}
@media (prefers-color-scheme: dark){:root{--bg:#121214;--fg:#ececf0;--muted:#a3a3ad;--line:#33333a;--note:#2e2a17;--noteline:#6b5d24;--link:#ce93d8}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:760px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:1.9rem;line-height:1.2;margin:0 0 4px}
h2{font-size:1.15rem;margin:32px 0 8px}
p,li{color:var(--fg)}
.meta{color:var(--muted);margin:0 0 20px}
.draft{background:var(--note);border:1px solid var(--noteline);border-radius:8px;padding:12px 14px;margin:0 0 24px;font-size:.95rem}
a{color:var(--link)}
footer{margin-top:48px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
table{border-collapse:collapse;width:100%;font-size:.95rem}
td,th{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
"""

def renumber(body):
    import re, itertools
    c = itertools.count(1)
    return re.sub(r"<h2>\d+\. ", lambda m: f"<h2>{next(c)}. ", body)

def page(prop, title, body):
    body = renumber(body)
    links = " &middot; ".join(
        f'<a href="{f}.html">{t}</a>' for f, t in
        [("privacy", "Privacy"), ("terms", "Terms")] + ([("refunds", "Refunds")] if prop["sells"] else []))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{title} | {html.escape(prop['name'])}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<h1>{title}</h1>
<p class="meta">{html.escape(prop['name'])} ({prop['host']}) &middot; Last updated: {DATE}</p>
<div class="draft"><strong>Draft, not yet in effect.</strong> Prepared 2026-10-14 from a review of what this site actually does. Every item marked [CONFIRM: &hellip;] must be filled in before publishing, and the noindex tag removed. This draft is practical hygiene, not legal advice.</div>
{body}
<footer>{links} &middot; <a href="{prop['home']}">Back to {html.escape(prop['name'])}</a></footer>
</main>
</body>
</html>
"""

def ul(items):
    return "<ul>\n" + "\n".join(f"<li>{i}</li>" for i in items) + "\n</ul>"

def privacy(p):
    b = []
    b.append(f"""<h2>1. Who we are</h2>
<p>{html.escape(p['name'])} at <strong>{p['host']}</strong> is operated by {ENTITY} (&ldquo;we&rdquo;, &ldquo;us&rdquo;), {ADDRESS}. This policy explains what information this site handles, why, who processes it for us, and the choices you have. Questions go to {INBOX}.</p>""")
    b.append("<h2>2. Information we handle</h2>\n" + ul(p["collect"]))
    b.append("<h2>3. How we use it</h2>\n" + ul(p["use"] + [
        "To keep the site secure, prevent abuse and meet legal obligations."]))
    b.append("<h2>4. Service providers</h2>\n<p>We rely on the following providers, each of which processes data on our behalf or receives it directly when you use their part of the service:</p>\n" + ul(p["processors"]))
    b.append("<h2>5. Cookies and browser storage</h2>\n<p>" + p["storage"] + "</p>")
    b.append("<h2>6. Retention</h2>\n" + ul(p["retention"] + [
        "Hosting request logs are kept by our host for its standard log period (typically days to weeks).",
        "We delete or anonymise information when it is no longer needed for the purposes above, unless the law requires us to keep it."]))
    b.append("""<h2>7. Sharing</h2>
<p>We share information only with the service providers listed above, when the law requires it, to protect rights and safety, or as part of a merger or transfer of the business (with notice to you). We do not sell personal information, and we do not share it for cross-context behavioural advertising, as those terms are defined under California law.</p>""")
    b.append(f"""<h2>8. Your rights</h2>
<p>Depending on where you live, you may have the right to know what personal information we hold about you, to get a copy, to correct it, to delete it, to object to or restrict certain uses, and to withdraw consent. California residents have these rights under the CCPA/CPRA, including the right to opt out of sale or sharing (we do neither) and the right not to be discriminated against for exercising their rights. Residents of the EEA and UK have rights under the GDPR/UK GDPR and may complain to their local data-protection authority; our legal bases are performance of a contract (purchases, game features), legitimate interests (security, answering enquiries) and consent where we ask for it. Residents of other US states with privacy laws have comparable rights, including the right to appeal a decision we make about a request.</p>
<p>To make a request, email {INBOX} from the address connected to your request, or include enough detail (for example a Stripe receipt or the leaderboard name you used) for us to find the information. We respond within 45 days (one month under the GDPR) and may need to verify your identity. You may use an authorised agent.</p>""")
    b.append("""<h2>9. Do Not Track and Global Privacy Control</h2>
<p>This site runs no analytics, advertising or cross-site tracking scripts, so there is no tracking for a Do Not Track or Global Privacy Control signal to switch off. If we ever add such tools, we will honour Global Privacy Control as an opt-out and update this policy first.</p>""")
    b.append(f"""<h2>10. Children</h2>
<p>{p['children']} We do not knowingly collect personal information from children under 13. If you believe a child has given us personal information, contact {INBOX} and we will delete it.</p>""")
    b.append("""<h2>11. Security and international transfer</h2>
<p>Pages are served over HTTPS. Our providers are based in the United States, so information is processed there; where the law requires, transfers rely on the providers' standard contractual clauses. No method of transmission or storage is completely secure.</p>""")
    b.append(f"""<h2>12. Changes</h2>
<p>We will post any change on this page and update the date above. Material changes will be highlighted on the site before they take effect.</p>
<h2>13. Contact</h2>
<p>{ENTITY}<br>{ADDRESS}<br>Privacy requests: {INBOX}</p>""")
    if p.get("privacy_extra"):
        b.insert(2, p["privacy_extra"])
    return page(p, "Privacy Policy", "\n".join(b))

def terms(p):
    b = []
    b.append(f"""<h2>1. Agreement</h2>
<p>These terms govern your use of {html.escape(p['name'])} at <strong>{p['host']}</strong>, operated by {ENTITY} (&ldquo;we&rdquo;, &ldquo;us&rdquo;). By using the site you agree to them and to our <a href="privacy.html">Privacy Policy</a>. If you do not agree, please do not use the site.</p>
<h2>2. Eligibility</h2>
<p>You must be at least 13 years old to use this site. You must be 18 or older, or have a parent or guardian's permission and involvement, to make a purchase.</p>""")
    b.append("<h2>3. What the site offers</h2>\n<p>" + p["offer"] + "</p>")
    if p["sells"]:
        b.append(f"""<h2>4. Purchases</h2>
<p>Prices are shown in US dollars at the point of sale and may change before you buy. Payment is processed by Stripe; we never see or store your full card number. {p['purchase_terms']} Refunds are covered by our <a href="refunds.html">Refund Policy</a>. Taxes, where applicable, are added at checkout.</p>""")
    if p.get("user_content"):
        b.append("<h2>5. Names and content you submit</h2>\n<p>" + p["user_content"] + "</p>")
    b.append("""<h2>6. Acceptable use</h2>
<p>Do not misuse the site: no attempts to break, overload, scrape at scale or reverse-engineer it; no bypassing purchase checks or limits; no unlawful, infringing, hateful or harassing content; and no impersonation. We may suspend access or remove content that breaks these rules.</p>
<h2>7. Intellectual property</h2>
<p>The site, its stories, artwork, games, code, video and branding are owned by us or our licensors and protected by copyright and trademark law. A purchase gives you a personal, non-transferable, non-exclusive licence to use what you bought for your own non-commercial enjoyment. Everything else is reserved.</p>
<h2>8. Third-party services and links</h2>
<p>The site uses or links to services we do not control (such as Stripe Checkout and the other sites linked from our pages). Their own terms and privacy policies apply to your use of them.</p>
<h2>9. Disclaimers</h2>
<p>The site is provided &ldquo;as is&rdquo; and &ldquo;as available&rdquo;. To the fullest extent the law allows, we disclaim all warranties, express or implied, including merchantability, fitness for a particular purpose and non-infringement, and we do not promise the site will be uninterrupted or without errors.</p>
<h2>10. Limitation of liability</h2>
<p>To the fullest extent the law allows, we are not liable for indirect, incidental, special, consequential or punitive damages, or for lost profits, data or goodwill. Our total liability for any claim relating to the site is limited to the greater of the amount you paid us in the 12 months before the claim or US$50. Some jurisdictions do not allow these limits, so they may not apply to you; nothing here limits rights you have as a consumer that cannot be waived.</p>
<h2>11. Indemnity</h2>
<p>You agree to indemnify us against claims arising from your breach of these terms or your misuse of the site, to the extent the law allows.</p>""")
    b.append(f"""<h2>12. Governing law and disputes</h2>
<p>These terms are governed by the laws of the State of {LAW}, USA, without regard to conflict-of-law rules. Courts located in {LAW} have exclusive jurisdiction, except that either party may bring a qualifying claim in small-claims court, and consumers keep any right to sue in their home courts that local law guarantees. Please contact us first; most issues can be resolved quickly by email.</p>
<h2>13. Changes and termination</h2>
<p>We may update these terms by posting a new version here with a new date. Continued use after a change means you accept it. We may suspend or end the site or any feature; if we end a paid feature you bought, the Refund Policy explains what happens.</p>
<h2>14. Contact</h2>
<p>{ENTITY}<br>{ADDRESS}<br>{INBOX}</p>""")
    if p.get("terms_extra"):
        b.append(p["terms_extra"])
    return page(p, "Terms of Use", "\n".join(b))

def refunds(p):
    b = [f"""<h2>Summary</h2>
<p>Everything sold on {html.escape(p['name'])} is a digital product. Nothing physical ships, so there are no returns of goods; this page explains refunds instead. Payment is processed by Stripe, and approved refunds go back to the original payment method, usually within 5&ndash;10 business days of approval.</p>
<h2>What is sold here</h2>
{p['items_table']}"""]
    b.append("<h2>When you can get a refund</h2>\n" + ul(p["refund_rules"] + [
        "Charged twice, or charged for something that never unlocked or arrived: full refund, at any time, once confirmed.",
        "We stop offering a paid feature you bought: we will restore access another way or refund you.",
        "Where local consumer law gives you stronger rights (for example the EU/UK withdrawal right for digital content), those rights apply. For instant digital unlocks, you agree at checkout that delivery starts immediately, which ends the withdrawal period once the content is unlocked."]))
    b.append(f"""<h2>How to ask</h2>
<p>Email {INBOX} with your Stripe receipt (or the email address you paid with) and a sentence on what went wrong. We aim to reply within 3 business days. Please contact us before opening a card dispute; we resolve most problems faster directly.</p>""")
    if p.get("refund_extra"):
        b.append(p["refund_extra"])
    return page(p, "Refund Policy", "\n".join(b))

VERCEL = "Vercel Inc. (website hosting and delivery). Vercel receives standard request data such as your IP address, browser type and the page requested, and keeps short-lived request logs."
STRIPE = "Stripe, Inc. (payments). When you click a buy button you leave this site for a Stripe Checkout page; Stripe collects your name, email, card and billing details directly under its own privacy policy (stripe.com/privacy). We receive your name, email, the item, amount and payment status, never your full card number."
FIRESTORE = "Google LLC, Firebase Cloud Firestore (game leaderboard database). Stores the player name, score or time, and timestamp you submit."
GFONTS = "Google LLC, Google Fonts (typeface delivery). Your browser requests font files from Google, which sees your IP address and browser details."
CDNS = "cdnjs (Cloudflare, Inc.) and Amazon CloudFront (script libraries for the page layout). Your browser requests script files from these networks, which see your IP address and browser details."
GMAIL = "Google LLC, Gmail (email). Messages you send us are received and stored in our Google Workspace or Gmail mailbox."

REQ = "Technical request data that every visit creates: IP address, browser and device type, the page requested and the time, processed by our host to deliver the site."

def items(rows):
    return "<table><tr><th>Item</th><th>Price shown</th><th>What you get</th></tr>" + "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows) + "</table>"

GAME_CHILDREN = "Our games are designed for a general audience and are not directed to children under 13. Children under 13 should not enter a name for the leaderboard or make purchases."
GENERAL_CHILDREN = "This site is intended for a general adult audience and is not directed to children under 13."

def game_unlock(name, key, price, features):
    return dict(
        sells=True,
        collect=[
            "<strong>Player name.</strong> The name you type on the start screen. It is saved in your browser and, when you finish a game, sent with your score and a timestamp to our leaderboard database, where it is shown publicly to other players. Use a nickname, not your real name.",
            "<strong>Game progress in your browser.</strong> Your daily play count, last-played date and premium status are stored in your browser's local storage on your device; they are not sent to us.",
            "<strong>Purchase details.</strong> If you buy the premium unlock, Stripe collects your payment details and shares with us your name, email, the item, amount and payment status.",
            "<strong>Emails you send us.</strong> Your address and whatever you write.",
            REQ],
        use=["To run the game, show the public leaderboard and enforce daily play limits.",
             "To process and support purchases, including restoring a premium unlock.",
             "To answer messages you send."],
        processors=[VERCEL, FIRESTORE, STRIPE, GMAIL],
        storage=f"This site sets no cookies of its own and uses no analytics or advertising cookies. It uses your browser's local storage to remember your player name and game state under the keys <code>{key}_player_name</code>, <code>{key}_daily_tries</code>, <code>{key}_last_played</code> and <code>{key}_premium</code>. You can clear these at any time in your browser settings; doing so resets your progress and removes the premium flag on that device (see the Refund Policy for restoring a purchase). Stripe sets its own cookies on its checkout pages for fraud prevention.",
        retention=["Leaderboard entries (name, score, timestamp): kept while the leaderboard runs, or until you ask us to delete them. [CONFIRM: leaderboard retention or reset schedule]",
                   "Purchase records: kept for as long as tax and accounting law requires (typically 7 years).",
                   "Emails: kept as long as needed to resolve your request."],
        children=GAME_CHILDREN,
        offer=f"{name} is a browser game. You can play a limited number of games each day without a purchase. A one-time premium unlock ({price}) adds {features}. Leaderboards show player names and scores publicly.",
        purchase_terms="The premium unlock is a one-time purchase for this game. Premium status is currently stored in the browser you used; if you clear browser data or switch devices, email us with your receipt and we will restore it. [CONFIRM: confirm the Stripe Payment Link redirects back to the game with the unlock applied after payment]",
        user_content="The player name you enter is displayed publicly on the leaderboard. Do not use your real full name, other people's names, or offensive names; we may remove any name at our discretion. You can ask us to delete your leaderboard entries at any time.",
        items_table=items([(f"{name} premium unlock", price + " one-time", features)]),
        refund_rules=[f"Within {WINDOW} of purchase, for any reason: full refund on request. Your premium status is removed when the refund is issued.",
                      "Lost your unlock after clearing browser data or changing device: we restore it rather than refund, on request with your receipt."],
    )

PROPS = {
"buttsstudios.com": dict(
    name="Butts Studios", host="buttsstudios.com", home="https://buttsstudios.com/", sells=False,
    collect=["<strong>Contact form.</strong> First name, last name, email, optional phone number and your message, if you submit the form on the Contact page.",
             "<strong>Emails you send us.</strong> Your address and whatever you write.",
             REQ],
    use=["To reply to project enquiries and discuss work with you."],
    processors=[VERCEL, CDNS, GMAIL,
                "[CONFIRM: contact-form processor once the form is reconnected, e.g. Formspree or a serverless function; the current form handler does not run on the host]"],
    storage="This site sets no cookies of its own and uses no analytics or advertising cookies. The page layout scripts (Webflow, jQuery, fullPage.js) run in your browser and do not track you.",
    retention=["Contact enquiries and emails: kept as long as needed to respond and for the duration of any project that follows, then deleted within [CONFIRM: retention period, e.g. 24 months] of last contact."],
    children=GENERAL_CHILDREN,
    offer="This site presents the studio's design and development work and lets prospective clients contact us. Nothing is sold through this site; any project is covered by a separate written agreement.",
),
"novels": dict(
    name="The Signal (a novel series)", host="novels.buttsstudios.com", home="https://novels.buttsstudios.com/", sells=True,
    collect=["<strong>Pre-order purchase details.</strong> If you pre-order, Stripe collects your payment details and shares with us your name, email, the item, amount and payment status. We use your email to deliver the book.",
             "<strong>Update sign-ups.</strong> [CONFIRM: the &ldquo;Stay Connected&rdquo; form is not connected to any mailing service today and sends nothing; once wired up, name the provider here, e.g. Buttondown or Mailchimp.] When live, it will collect your email address to send release news, with an unsubscribe link in every message.",
             "<strong>Emails you send us.</strong> Your address and whatever you write.",
             REQ],
    use=["To process pre-orders and deliver the book when it is released.",
         "To send release updates if you sign up (you can unsubscribe at any time).",
         "To answer messages you send."],
    processors=[VERCEL, STRIPE, GFONTS, GMAIL, "[CONFIRM: email-list provider, once the sign-up form is connected]"],
    storage="This site sets no cookies of its own and uses no analytics or advertising cookies, and stores nothing in your browser's local storage. Stripe sets its own cookies on its checkout pages for fraud prevention.",
    retention=["Purchase records: kept for as long as tax and accounting law requires (typically 7 years).",
               "Mailing-list addresses: kept until you unsubscribe.",
               "Emails: kept as long as needed to resolve your request."],
    children=GENERAL_CHILDREN,
    offer="This site presents The Signal novel series by Latarence Butts and takes pre-orders for Book One. Books Two and Three are announced for future years and are not yet on sale.",
    purchase_terms="A pre-order reserves a copy of Book One, &ldquo;The Signal&rdquo;, which is still being written. You are charged when you pre-order. We will deliver the book by email in [CONFIRM: format, e.g. EPUB and PDF] when it is released, targeted for [CONFIRM: expected release date]. If the release date moves, we will email you with the new date and your option to cancel for a full refund.",
    items_table=items([("The Signal, Book One (pre-order)", "$9.99", "A digital copy delivered by email on release. [CONFIRM: format]")]),
    refund_rules=["Pre-orders: cancel for a full refund at any time before the book is delivered.",
                  "If the book is not delivered by [CONFIRM: latest delivery date], we refund you automatically.",
                  f"After delivery: full refund within {WINDOW} if the file is faulty or not what was described."],
),
"film": dict(
    name="Butts Film", host="film.buttsstudios.com", home="https://film.buttsstudios.com/", sells=False,
    collect=["<strong>Emails you send us.</strong> When you use &ldquo;Get in Touch&rdquo;, your email app opens a message to us; we receive your address and whatever you write.", REQ],
    use=["To reply to production enquiries and discuss work with you."],
    processors=[VERCEL, GMAIL],
    storage="This site sets no cookies, uses no analytics or advertising tools and stores nothing in your browser.",
    retention=["Enquiries: kept as long as needed to respond and for any project that follows, then deleted within [CONFIRM: retention period, e.g. 24 months] of last contact."],
    children=GENERAL_CHILDREN,
    offer="This site presents the film and video production work of Butts Film and lets prospective clients contact us. Nothing is sold through this site; any project is covered by a separate written agreement.",
),
"animation": dict(
    name="Butts Animation", host="animation.buttsstudios.com", home="https://animation.buttsstudios.com/", sells=False,
    collect=["<strong>Emails you send us.</strong> When you use &ldquo;Get in Touch&rdquo;, your email app opens a message to us; we receive your address and whatever you write.", REQ],
    use=["To reply to animation enquiries and discuss work with you."],
    processors=[VERCEL, GMAIL],
    storage="This site sets no cookies, uses no analytics or advertising tools and stores nothing in your browser.",
    retention=["Enquiries: kept as long as needed to respond and for any project that follows, then deleted within [CONFIRM: retention period, e.g. 24 months] of last contact."],
    children=GENERAL_CHILDREN,
    offer="This site presents the animation work of Butts Animation and lets prospective clients contact us. Nothing is sold through this site; any project is covered by a separate written agreement.",
),
"games": dict(
    name="Butts Games", host="games.buttsstudios.com", home="https://games.buttsstudios.com/", sells=True,
    collect=["<strong>Purchase details.</strong> If you buy a game unlock from this page, Stripe collects your payment details and shares with us your name, email, the item, amount and payment status.",
             "<strong>Emails you send us.</strong> Your address and whatever you write.",
             REQ],
    use=["To process and support game-unlock purchases.", "To answer messages you send."],
    processors=[VERCEL, STRIPE, GMAIL],
    storage="This hub page sets no cookies, uses no analytics or advertising tools and stores nothing in your browser. Each game has its own privacy policy, linked from that game, covering what the game stores. Stripe sets its own cookies on its checkout pages for fraud prevention.",
    retention=["Purchase records: kept for as long as tax and accounting law requires (typically 7 years).", "Emails: kept as long as needed to resolve your request."],
    children=GAME_CHILDREN,
    offer="This page lists our browser games (GLB, Butts Cards and Butts Puzzle). Each game offers limited play without a purchase and a paid unlock. Each game's own terms and privacy policy also apply when you play it.",
    purchase_terms="Unlock prices shown here: GLB $4.99, Butts Cards $2.99, Butts Puzzle $2.99, each a one-time purchase for that game. [CONFIRM: GLB is shown as $4.99 one-time here but $4.99/month inside the game; pick one and make both pages match.] Unlocks are tied to the browser where they are applied; email us with your receipt to restore one.",
    items_table=items([("GLB full unlock", "$4.99 [CONFIRM: one-time or monthly]", "Unlimited levels"),
                       ("Butts Cards full unlock", "$2.99 one-time", "Unlimited daily games"),
                       ("Butts Puzzle full unlock", "$2.99 one-time", "Unlimited daily games and 5x5 boards")]),
    refund_rules=[f"Within {WINDOW} of purchase, for any reason: full refund on request.",
                  "Lost your unlock after clearing browser data or changing device: we restore it rather than refund, on request with your receipt."],
),
"cards": dict(name="Butts Cards (Card Battle)", host="cards.buttsstudios.com", home="https://cards.buttsstudios.com/",
              **game_unlock("Card Battle", "butts_cards", "$2.99", "unlimited daily games")),
"puzzle": dict(name="Butts Puzzle (Sliding Numbers)", host="puzzle.buttsstudios.com", home="https://puzzle.buttsstudios.com/",
               **game_unlock("Sliding Numbers", "sliding_numbers", "$2.99", "unlimited daily games and 5x5 challenge boards")),
"glb": dict(
    name="GLB", host="glb.buttsstudios.com", home="https://glb.buttsstudios.com/", sells=True,
    collect=["<strong>Game progress in your browser.</strong> Your premium status is stored in your browser's local storage on your device; it is not sent to us. Score, lives and level exist only while you play.",
             "<strong>Purchase details.</strong> If you upgrade, Stripe collects your payment details and shares with us your name, email, the item, amount and payment status.",
             "<strong>Emails you send us.</strong> Your address and whatever you write.",
             REQ],
    use=["To run the game and apply your premium upgrade.", "To process and support purchases, including restoring an upgrade.", "To answer messages you send."],
    processors=[VERCEL, STRIPE + " The game page also loads Stripe.js from js.stripe.com to start checkout.", GMAIL],
    storage="This site sets no cookies of its own and uses no analytics or advertising cookies. It stores one value, <code>glb_premium</code>, in your browser's local storage to remember a premium upgrade. Clearing browser data removes it on that device (see the Refund Policy for restoring a purchase). Stripe.js and Stripe Checkout set Stripe's own cookies for fraud prevention.",
    retention=["Purchase records: kept for as long as tax and accounting law requires (typically 7 years).", "Emails: kept as long as needed to resolve your request."],
    children=GAME_CHILDREN,
    offer="GLB is a canvas browser game. Levels 1 to 5 can be played without a purchase; a premium upgrade unlocks further levels. [CONFIRM: the upgrade screen also lists &ldquo;New Game Modes&rdquo;, &ldquo;No Ads&rdquo; and &ldquo;Leaderboards&rdquo;; none of these exist in the game today, so remove them from the game or ship them before this page lists them.]",
    purchase_terms="The premium upgrade is priced at [CONFIRM: $4.99 one-time or $4.99/month; the game says per month, the games hub says one-time, and the checkout code is set up as a one-time payment]. If it is a subscription, it renews monthly until you cancel; you can cancel at any time by emailing us or through the Stripe customer portal [CONFIRM: portal link], and cancellation takes effect at the end of the current billing month. Premium status is stored in the browser you used; email us with your receipt to restore it.",
    items_table=items([("GLB premium", "$4.99 [CONFIRM: one-time or per month]", "Unlimited levels beyond level 5")]),
    refund_rules=[f"Within {WINDOW} of your first payment, for any reason: full refund on request.",
                  "If it is a subscription: cancel at any time to stop future charges; the current month is not pro-rated unless you were charged in error. [CONFIRM]",
                  "Lost your upgrade after clearing browser data or changing device: we restore it rather than refund, on request with your receipt."],
),
"clients": dict(
    name="Butts Studios Client Portal", host="clients.buttsstudios.com", home="https://clients.buttsstudios.com/", sells=False,
    collect=["<strong>Sign-in details.</strong> The sign-in form is not yet connected to an account system: the email and password you type stay in your browser and are not sent to us or stored anywhere. [CONFIRM: when the portal goes live, replace this with the account data collected (name, email, company, hashed password), the auth provider, and project files and messages stored in the portal.]",
             "<strong>Access requests.</strong> When you click &ldquo;Request access&rdquo;, your email app opens a message to us; we receive your address and whatever you write.",
             REQ],
    use=["To reply to access requests and to share project updates with clients.",
         "When the portal is live: to authenticate you, show your projects and deliverables, and keep the portal secure."],
    processors=[VERCEL, GMAIL, "[CONFIRM: authentication and file-storage providers once the portal is live]"],
    storage="This page sets no cookies, uses no analytics or advertising tools and stores nothing in your browser today. [CONFIRM: when sign-in is live, list the session cookie name and its lifetime here; strictly necessary session cookies do not require consent.]",
    retention=["Access-request emails: kept as long as needed to respond and for the duration of any client relationship.",
               "When live: account data kept for the life of the account plus [CONFIRM: period], project files per the client agreement."],
    children="The client portal is for business clients and is not intended for anyone under 18.",
    offer="This portal is for existing Butts Studios clients. The sign-in is not yet operational; until it is, clients receive project updates by email. Project work itself is governed by each client's separate written agreement, which takes priority over these terms where they differ.",
    terms_extra="""<h2>15. Accounts (when sign-in is live)</h2>
<p>Keep your password confidential and tell us promptly if you suspect unauthorised access. You are responsible for activity under your account. Access may be withdrawn when a client engagement ends, after reasonable notice to download your deliverables.</p>""",
),
}

def main():
    for slug, p in PROPS.items():
        d = os.path.join(OUT, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "privacy.html"), "w").write(privacy(p))
        open(os.path.join(d, "terms.html"), "w").write(terms(p))
        if p["sells"]:
            open(os.path.join(d, "refunds.html"), "w").write(refunds(p))
    # clients login notice snippet
    open(os.path.join(OUT, "clients", "login-notice-snippet.html"), "w").write(
        """<!-- Place directly under the Sign In button in clients.buttsstudios.com index.html -->
<p class="login-legal" style="font-size:.85rem;color:#888;margin-top:1rem;text-align:center">
  By signing in you agree to our <a href="/terms.html">Terms</a>. See our
  <a href="/privacy.html">Privacy Policy</a> for how sign-in details are handled.
</p>
""")

if __name__ == "__main__":
    main()
