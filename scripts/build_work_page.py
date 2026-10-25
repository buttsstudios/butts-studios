#!/usr/bin/env python3
"""Build site/work.html: one filterable index of everything the studio makes (Principal 2026-10-25).

Current work = the slate titles (slate.html), Client work = partnership sites (partnerships.html),
Design = the portfolio item pages (portfolio/*.html). The source pages stay the detail views; re-run this
after editing any of them. Also rewrites the top nav on every page to: Work · How we work.

    python3 ~/buttsstudios/scripts/build_work_page.py
"""
import html
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "site"


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def esc(s):
    return html.escape(s, quote=True)


def slate_items():
    src = (SITE / "slate.html").read_text()
    out = []
    for row in re.findall(r'(?s)<a class="title-row" href="([^"]+)">(.*?)</a>\s*(?=<a class="title-row"|</div>)', src):
        href, body = row
        title = text(re.search(r"(?s)<h3[^>]*>(.*?)</h3>", body).group(1))
        kind = text(re.search(r'(?s)class="kind">(.*?)</div>', body).group(1))
        stage = text(re.search(r'(?s)class="stage-label">(.*?)</span>', body).group(1))
        bar = re.search(r'(?s)<span class="stage-bar">(.*?)</span>', body).group(1)
        note = re.search(r'(?s)class="stage-note">(.*?)</span>', body)
        out.append(dict(cat="current", href=href, title=title, kind=kind, stage=stage, bar=bar,
                        note=text(note.group(1)) if note else ""))
    return out


def client_items():
    src = (SITE / "partnerships.html").read_text()
    out = []
    for art in re.findall(r'(?s)<article(?: id="[^"]*")? class="work[^"]*">(.*?)</article>', src):
        title = text(re.search(r"(?s)<h3[^>]*>(.*?)</h3>", art).group(1))
        img = re.search(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', art)
        href = re.search(r'class="open-site" href="([^"]+)"', art)
        kind = re.search(r'(?s)</h3>\s*<p[^>]*>(.*?)</p>', art)
        out.append(dict(cat="client", href="partnerships.html#" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-"),
                        title=title, kind=text(kind.group(1)) if kind else "Website",
                        img=img.group(1) if img else "", alt=img.group(2) if img else title))
    return out


def design_items():
    order = re.findall(r'href="portfolio/([a-z0-9-]+)\.html"', (SITE / "portfolio.html").read_text())
    seen, slugs = set(), []
    for s in order + sorted(p.stem for p in (SITE / "portfolio").glob("*.html")):
        if s not in seen and (SITE / "portfolio" / f"{s}.html").exists():
            seen.add(s)
            slugs.append(s)
    out = []
    for s in slugs:
        src = (SITE / "portfolio" / f"{s}.html").read_text()
        title = text(re.search(r'(?s)<h1[^>]*>(.*?)</h1>', src).group(1))
        kind = re.search(r'(?s)<p class="kind">(.*?)</p>', src)
        img = re.search(r'<img src="\.\./([^"]+\.(?:webp|png|jpg|svg))"[^>]*alt="([^"]*)"', src)
        out.append(dict(cat="design", href=f"portfolio/{s}.html", title=title,
                        kind=text(kind.group(1)) if kind else "Design",
                        img=img.group(1) if img else "", alt=img.group(2) if img else title))
    return out


LABEL = {"current": "Current work", "client": "Client work", "design": "Design"}


def card(i):
    tag = f'<span class="wk-cat">{LABEL[i["cat"]]}</span>'
    if i["cat"] == "current":
        media = (f'<div class="wk-media wk-type"><span class="wk-type-title">{esc(i["title"])}</span>'
                 f'<span class="wk-type-stage"><span class="stage-bar">{i["bar"]}</span>{esc(i["stage"])}</span></div>')
    elif i["img"]:
        media = f'<div class="wk-media"><img src="{esc(i["img"])}" alt="{esc(i["alt"])}" loading="lazy"></div>'
    else:
        media = f'<div class="wk-media wk-type"><span class="wk-type-title">{esc(i["title"])}</span></div>'
    return (f'      <a class="wk-card" href="{esc(i["href"])}" data-cat="{i["cat"]}">\n        {media}\n'
            f'        <div class="wk-meta"><h3>{esc(i["title"])}</h3>{tag}</div>\n'
            f'        <p class="wk-kind">{esc(i["kind"])}</p>\n      </a>')


def build():
    items = slate_items() + client_items() + design_items()
    counts = {c: sum(1 for i in items if i["cat"] == c) for c in LABEL}
    filters = [f'<button type="button" data-filter="all" aria-pressed="true">All <small>{len(items)}</small></button>']
    filters += [f'<button type="button" data-filter="{c}" aria-pressed="false">{LABEL[c]} <small>{counts[c]}</small></button>'
                for c in LABEL]
    main = f'''<main>
  <section class="wrap hero">
    <p class="eyebrow">Work</p>
    <h1 class="display">Everything<br>we <span class="gold">make</span>.</h1>
    <div class="hero-row">
      <p class="lede">Our own titles in progress, sites for clients, and identity and product design.</p>
    </div>
  </section>

  <section class="wrap section wk">
    <div class="wk-filters" role="group" aria-label="Filter work">
      {"".join(filters)}
    </div>
    <div class="wk-grid">
{chr(10).join(card(i) for i in items)}
    </div>
    <p class="wk-more">Full views: <a href="slate.html">the slate</a> · <a href="partnerships.html">client sites</a> · <a href="portfolio.html">design portfolio</a></p>
  </section>
</main>'''
    shell = (SITE / "slate.html").read_text()
    page = re.sub(r"(?s)<main>.*?</main>", lambda _: main, shell)
    page = re.sub(r"<title>.*?</title>", "<title>Work · Butts Studios</title>", page)
    desc = "Everything Butts Studios makes: titles in progress, client sites, and identity and product design."
    page = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"',
                  lambda m: m.group(1) + desc + '"', page)
    page = re.sub(r'(<meta property="og:title" content=")[^"]*"', r'\1Work · Butts Studios"', page)
    page = page.replace("https://buttsstudios.com/slate.html", "https://buttsstudios.com/work.html")
    page = page.replace("</body>", '<script src="work.js" defer></script>\n</body>', 1)
    (SITE / "work.html").write_text(page)
    return len(items), counts


NAV_LINK = re.compile(r'\s*<a href="((?:\.\./)?)(slate|partnerships|portfolio|work)\.html"(?: aria-current="page")?>[A-Za-z ]+</a>')


def rewrite_nav():
    n = 0
    for f in list(SITE.glob("*.html")) + list(SITE.glob("*/*.html")):
        if "/work/" in str(f.relative_to(SITE).parent.as_posix() + "/") and f.parent.name != "titles":
            pass
        s = f.read_text()
        m = re.search(r"(?s)(<header[^>]*>.*?<nav>)(.*?)(</nav>)", s)
        if not m or "how-we-work.html" not in m.group(2):
            continue
        nav = m.group(2)
        pre = "../" if f.parent != SITE else ""
        on_work = f.parent.name in ("portfolio", "titles") or f.stem in ("slate", "partnerships", "portfolio", "work")
        cur = ' aria-current="page"' if on_work else ""
        nav2 = NAV_LINK.sub("", nav)
        hww = re.search(r'\s*<a href="(?:\.\./)?how-we-work\.html"', nav2)
        nav2 = nav2[:hww.start()] + f'\n    <a href="{pre}work.html"{cur}>Work</a>' + nav2[hww.start():]
        if nav2 != nav:
            s = s[:m.start(2)] + nav2 + s[m.end(2):]
            f.write_text(s)
            n += 1
    return n


if __name__ == "__main__":
    total, counts = build()
    print(f"work.html: {total} items {counts}")
    print(f"nav rewritten on {rewrite_nav()} pages")
