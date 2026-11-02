#!/usr/bin/env python3
"""Build site/releases.html (the studio's own titles) and site/work.html (what we make with others).

Principal 2026-11-02: nav is About, Releases (internal: our own titles), Work (clients), Shop ("or we could do releases
(internal) and work (clients)"). He disliked "client" and "internal" as labels and a home slate that showed 3 titles with a
"see all 4" button, so:
- /releases shows ALL of the studio's own titles at once (books, video, games; each card shows its stage), with a kind
  filter (Books / Video / Games) and the "Read our books early" section (scripts/sources/how-it-works.html).
- /work shows ALL projects made for others (client archives and the portfolio item pages), then how a project runs
  (copy from /how-we-work). No filter, no "see more".
Old links: /work#books|video|games|current|originals now live on /releases (an inline redirect on /work); #client,
#commissions, #design, #web mean /work. Without JS everything shows.

Sources (the retired slate/partnerships/portfolio pages live on as data in scripts/sources/, never served):
- Releases: the four slate titles (scripts/sources/slate.html, minus Runwae Apparel and GLB, DECISIONS #56), the index rows
  of site/books.html and site/video.html, and the plates on site/games.html (thumbnails in assets/work/).
- Work: scripts/sources/partnerships.html (each opens its archived site under /work/<name>/) and the portfolio item pages
  (site/portfolio/*.html) in scripts/sources/portfolio.html order.

    python3 ~/buttsstudios/scripts/build_work_page.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SOURCES = ROOT / "scripts" / "sources"

TYPES = [("books", "Books"), ("video", "Video"), ("games", "Games")]
TYPE_LABEL = dict(TYPES, web="Web & design")
NOT_STUDIO_TITLES = ("runwae-and-glb",)  # apparel labels are not studio titles (DECISIONS #56)
TITLE_TYPE = {"/titles/us-against-the-world": "books", "/titles/talon": "books",
              "/channels": "video", "/titles/the-little-things": "video"}
GAME_ALT = {"glowgrid": "Glowgrid start screen: Ready., with Today's run and Endless on a dark grid of lights",
            "cards": "Card Battle start screen: three playing cards around a prize card, with Play the first match",
            "sliding-numbers": "Sliding Numbers: a 3x3 board of numbered tiles with moves, time and par above it"}


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def esc(s):
    return html.escape(s, quote=True)


def rows(src):
    """Title rows of an index page: href, title, kind, stage, bar (may be empty)."""
    out = []
    for href, body in re.findall(r'(?s)<a class="title-row" href="([^"]+)">(.*?)</a>', src):
        title = text(re.search(r"(?s)<h3[^>]*>(.*?)</h3>", body).group(1))
        kind = re.search(r'(?s)class="kind">(.*?)</div>', body)
        stage = re.search(r'(?s)class="stage-label">(.*?)</span>', body)
        bar = re.search(r'(?s)<span class="stage-bar">(.*?)</span>', body)
        out.append(dict(href=href, title=title, kind=text(kind.group(1)) if kind else "",
                        stage=text(stage.group(1)) if stage else "", bar=bar.group(1) if bar else ""))
    return out


def current_items():
    out = []
    for r in rows((SOURCES / "slate.html").read_text()):
        if any(x in r["href"] for x in NOT_STUDIO_TITLES):
            continue
        out.append(dict(r, type=TITLE_TYPE.get(r["href"], "books"), img=""))
    return out


def section_items(page, cat, have):
    out = []
    for r in rows((SITE / page).read_text()):
        if r["href"] in have or not r["href"].startswith("/"):
            continue
        out.append(dict(r, type=cat, img=""))
    return out


def game_items():
    src = (SITE / "games.html").read_text()
    out = []
    for href, slug, body in re.findall(r'(?s)<a class="plate-card" href="(/games/([a-z0-9-]+))">(.*?)</a>', src):
        img = f"assets/work/game-{slug}-720.webp"
        if not (SITE / img).exists():
            raise SystemExit(f"missing game thumbnail {img}")
        out.append(dict(href=href, title=text(re.search(r'(?s)class="plate-name">(.*?)</span>', body).group(1)),
                        kind=text(re.search(r'(?s)class="plate-kind">(.*?)</span>', body).group(1)),
                        type="games", img=img, alt=GAME_ALT.get(slug, slug)))
    return out


def client_items():
    src = (SOURCES / "partnerships.html").read_text()
    out = []
    for aid, art in re.findall(r'(?s)<article id="([^"]+)" class="work[^"]*">(.*?)</article>', src):
        title = text(re.search(r"(?s)<h3[^>]*>(.*?)</h3>", art).group(1))
        img = re.search(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', art)
        kind = re.search(r'(?s)<div class="meta">(.*?)</div>', art) or re.search(r'(?s)</h3>\s*<p[^>]*>(.*?)</p>', art)
        if (SITE / "work" / aid / "index.html").exists():
            href = f"/work/{aid}/index.html"  # the archive's relative assets need the index.html URL
        else:
            zoom = re.search(r'class="zoom" href="([^"]+)"', art)
            href = zoom.group(1) if zoom else "/work"
        out.append(dict(href=href, title=title, kind=text(kind.group(1)) if kind else "Website", type="web",
                        img=img.group(1) if img else "", alt=img.group(2) if img else title))
    return out


def design_items():
    order = re.findall(r'href="/portfolio/([a-z0-9-]+)"', (SOURCES / "portfolio.html").read_text())
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
        img = re.search(r'<img src="(?:\.\./|/)([^"]+\.(?:webp|png|jpg|svg))"[^>]*alt="([^"]*)"', src)
        out.append(dict(href=f"/portfolio/{s}", title=title, kind=text(kind.group(1)) if kind else "Design",
                        type="web", img=img.group(1) if img else "", alt=img.group(2) if img else title))
    return out


def card(i, tag=True):
    label = f'<span class="wk-cat">{TYPE_LABEL[i["type"]]}</span>' if tag else ""
    if i["img"]:
        media = f'<div class="wk-media"><img src="/{esc(i["img"].lstrip("/"))}" alt="{esc(i["alt"])}" loading="lazy"></div>'
    else:
        stage = (f'<span class="wk-type-stage">{f"""<span class="stage-bar">{i["bar"]}</span>""" if i["bar"] else ""}'
                 f'{esc(i["stage"])}</span>') if i.get("stage") else ""
        media = f'<div class="wk-media wk-type"><span class="wk-type-title">{esc(i["title"])}</span>{stage}</div>'
    return (f'      <a class="wk-card" href="{esc(i["href"])}" data-type="{i["type"]}">\n        {media}\n'
            f'        <div class="wk-meta"><h3>{esc(i["title"])}</h3>{label}</div>\n'
            f'        <p class="wk-kind">{esc(i["kind"])}</p>\n      </a>')


def swap_page(name, main, title, desc, canonical, script=None, inline=""):
    """Write site/<name>.html from the shared shell (head, header, footer) with a new <main> and meta."""
    page = (SITE / "work.html").read_text()
    page = re.sub(r"(?s)<main[^>]*>.*?</main>", lambda _: main, page)
    page = re.sub(r"<title>[^<]*</title>", lambda _: f"<title>{esc(title)} · Butts Studios</title>", page)
    page = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"',
                  lambda m: m.group(1) + esc(desc) + '"', page)
    page = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda m: m.group(1) + esc(title) + ' · Butts Studios"', page)
    page = re.sub(r'(<link rel="canonical" href=")[^"]*"', lambda m: m.group(1) + canonical + '"', page)
    page = re.sub(r'(<meta property="og:url" content=")[^"]*"', lambda m: m.group(1) + canonical + '"', page)
    head_end = page.index("</header>")
    header = page[:head_end].replace(' aria-current="page"', "")
    header = header.replace(f'<a href="/{name}">', f'<a href="/{name}" aria-current="page">', 1)
    page = header + page[head_end:]
    page = re.sub(r'<script src="/(?:work|releases)\.js" defer></script>\n?', "", page)
    page = re.sub(r'<script>\(function\(\)\{var h=\(location\.hash.*?</script>\n?', "", page, flags=re.S)  # never inherit another page's redirect
    extra = (f'<script src="/{script}" defer></script>\n' if script else "") + inline
    if extra:
        page = page.replace("</body>", extra + "</body>", 1)
    (SITE / f"{name}.html").write_text(page)


def build():
    items = current_items()
    have = {i["href"] for i in items}
    items += section_items("books.html", "books", have)
    items += section_items("video.html", "video", have)
    items += game_items()
    links = ['<a href="#all" data-type="all">All <small>%d</small></a>' % len(items)]
    links += [f'<a href="#{t}" data-type="{t}">{label} <small>{sum(1 for i in items if i["type"] == t)}</small></a>'
              for t, label in TYPES]
    targets = "".join(f'<span class="wk-t" id="{c}"></span>' for c in ["all", "books", "video", "games"])
    how = (SOURCES / "how-it-works.html").read_text()
    main = f'''<main id="main" tabindex="-1">
  <section class="wrap hero">
    <p class="eyebrow">Releases</p>
    <h1 class="display">Our own <span class="gold">releases</span>.</h1>
    <div class="hero-row">
      <p class="lede">Books, comics, video and games written, drawn and built here. Each one shows how far along it is, from Development to Released.</p>
    </div>
  </section>

  <section class="wrap section wk">
    {targets}
    <div class="wk-controls" hidden>
      <nav class="wk-filters wk-types" aria-label="Kind of work">
        {"".join(links)}
      </nav>
    </div>
    <div class="wk-grid">
{chr(10).join(card(i, tag=False) for i in items)}
    </div>
  </section>
{how}</main>'''
    swap_page("releases", main, "Releases", "Our own books, comics, video and games, each with how far along it is.", "https://buttsstudios.com/releases", script="releases.js")

    mine = client_items() + design_items()
    steps = [("Start with a note", "Write to us on the <a href=\"/contact?topic=projects\">contact page</a> with what you're making and where it stands."),
             ("Identity first", "The mark, type and colour are set before anything is built, so every surface grows from one system."),
             ("Then the build", "The site, shop or product is designed and built on that identity, desktop and phone together.")]
    steps_html = "".join(f"\n        <div>\n          <h3>{t}</h3>\n          <p>{d}</p>\n        </div>" for t, d in steps)
    smain = f'''<main id="main" tabindex="-1">
  <section class="wrap hero">
    <p class="eyebrow">Work</p>
    <h1 class="display">Made <span class="gold">with others</span>.</h1>
    <div class="hero-row">
      <p class="lede">Identities, sites and products for musicians, galleries and young brands since 2019.</p>
    </div>
  </section>

  <section class="wrap section wk">
    <div class="section-head">
      <h2>What we have made</h2>
      <p>{len(mine)} projects, from artist sites to product interfaces.</p>
    </div>
    <div class="wk-grid">
{chr(10).join(card(i, tag=False) for i in mine)}
    </div>
  </section>

  <section class="wrap section">
    <div class="section-head">
      <h2>How it runs</h2>
      <p>We take on a few projects at a time, alongside our own releases.</p>
    </div>
    <div class="principles">{steps_html}
    </div>
    <p style="margin-top:32px"><a class="btn" href="/contact?topic=partnerships">Start with a note</a> <a class="btn" href="/how-we-work" style="color:var(--gold)">How we work</a></p>
  </section>
</main>'''
    redirect = ('<script>(function(){var h=(location.hash||"").slice(1);if(["books","video","games","current","originals","all"].indexOf(h)>=0)'
                'location.replace("/releases"+(["books","video","games"].indexOf(h)>=0?"#"+h:""));})();</script>\n')
    swap_page("work", smain, "Work", "Identities, sites and products Butts Studios makes with musicians, galleries and young brands.", "https://buttsstudios.com/work", inline=redirect)
    return len(items), len(mine)


if __name__ == "__main__":
    own, others = build()
    print(f"releases.html: {own} own titles; work.html: {others} projects")
