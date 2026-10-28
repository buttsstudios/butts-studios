#!/usr/bin/env python3
"""Build site/work.html: one filterable index of everything the studio makes (Principal 2026-10-25; filters
reworked 2026-10-28, STUDIOS-WORK-PAGE-1).

Filters: All · Current work · Books · Video · Games · Client work · Design. They are anchor links (#all, #current,
#books, #video, #games, #client, #design) filtered by CSS :target, so the page works without JS; work.js only
syncs aria-current and adds `hidden` for browsers without :has(). The page opens on Current work.

Sources (the retired slate/partnerships/portfolio pages live on as data in scripts/sources/, never served):
- Current work: scripts/sources/slate.html, minus Runwae Apparel and GLB (DECISIONS #56: no Runwae/GLB as studio titles).
- Books / Video: the index rows of site/books.html and site/video.html (adds The Signal, Film, Animation).
- Games: the plates on site/games.html, with start-screen thumbnails in assets/work/game-<slug>-720.webp.
- Client work: scripts/sources/partnerships.html; each card opens its archived site under /work/<client>/.
- Design: the portfolio item pages (site/portfolio/*.html) in scripts/sources/portfolio.html order.

    python3 ~/buttsstudios/scripts/build_work_page.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SOURCES = ROOT / "scripts" / "sources"

CATS = [("current", "Current work"), ("books", "Books"), ("video", "Video"), ("games", "Games"),
        ("client", "Client work"), ("design", "Design")]
LABEL = dict(CATS)
NOT_STUDIO_TITLES = ("runwae-and-glb",)  # apparel labels are not studio titles (DECISIONS #56)
EXTRA_CATS = {"/titles/us-against-the-world": ["books"], "/titles/talon": ["books"],
              "/channels": ["video"], "/titles/the-little-things": ["video"]}
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
        out.append(dict(r, cats=["current"] + EXTRA_CATS.get(r["href"], []), img=""))
    return out


def section_items(page, cat, have):
    out = []
    for r in rows((SITE / page).read_text()):
        if r["href"] in have or not r["href"].startswith("/"):
            continue
        out.append(dict(r, cats=[cat], img=""))
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
                        cats=["games"], img=img, alt=GAME_ALT.get(slug, slug)))
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
            href = zoom.group(1) if zoom else "/work#client"
        out.append(dict(href=href, title=title, kind=text(kind.group(1)) if kind else "Website", cats=["client"],
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
                        cats=["design"], img=img.group(1) if img else "", alt=img.group(2) if img else title))
    return out


def card(i):
    cls = " ".join(f"c-{c}" for c in i["cats"])
    tag = f'<span class="wk-cat">{LABEL[i["cats"][0]]}</span>'
    if i["img"]:
        media = f'<div class="wk-media"><img src="/{esc(i["img"].lstrip("/"))}" alt="{esc(i["alt"])}" loading="lazy"></div>'
    else:
        stage = (f'<span class="wk-type-stage">{f"""<span class="stage-bar">{i["bar"]}</span>""" if i["bar"] else ""}'
                 f'{esc(i["stage"])}</span>') if i.get("stage") else ""
        media = f'<div class="wk-media wk-type"><span class="wk-type-title">{esc(i["title"])}</span>{stage}</div>'
    return (f'      <a class="wk-card {cls}" href="{esc(i["href"])}" data-cat="{" ".join(i["cats"])}">\n        {media}\n'
            f'        <div class="wk-meta"><h3>{esc(i["title"])}</h3>{tag}</div>\n'
            f'        <p class="wk-kind">{esc(i["kind"])}</p>\n      </a>')


def build():
    items = current_items()
    have = {i["href"] for i in items}
    items += section_items("books.html", "books", have)
    items += section_items("video.html", "video", have)
    items += game_items() + client_items() + design_items()
    counts = {c: sum(1 for i in items if c in i["cats"]) for c, _ in CATS}
    targets = "".join(f'<span class="wk-t" id="{c}"></span>' for c in ["all"] + [c for c, _ in CATS])
    filters = [f'<a href="#all">All <small>{len(items)}</small></a>']
    filters += [f'<a href="#{c}">{label} <small>{counts[c]}</small></a>' for c, label in CATS]
    main = f'''<main>
  <section class="wrap hero">
    <p class="eyebrow">Work</p>
    <h1 class="display">Everything<br>we <span class="gold">make</span>.</h1>
    <div class="hero-row">
      <p class="lede">Our own books, video and games, sites for clients, and identity and product design.</p>
    </div>
  </section>

  <section class="wrap section wk">
    {targets}
    <nav class="wk-filters" aria-label="Filter work">
      {"".join(filters)}
    </nav>
    <div class="wk-grid">
{chr(10).join(card(i) for i in items)}
    </div>
    <p class="wk-more wk-portfolio"><a class="btn" href="#design">Check out the portfolio →</a></p>
  </section>
</main>'''
    page = (SITE / "work.html").read_text()
    page = re.sub(r"(?s)<main>.*?</main>", lambda _: main, page)
    desc = "Everything Butts Studios makes: books, video and games in progress, client sites, and identity and product design."
    page = re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*"',
                  lambda m: m.group(1) + desc + '"', page)
    (SITE / "work.html").write_text(page)
    return len(items), counts


if __name__ == "__main__":
    total, counts = build()
    print(f"work.html: {total} items {counts}")
