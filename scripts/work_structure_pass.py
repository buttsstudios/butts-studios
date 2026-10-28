#!/usr/bin/env python3
"""Site structure pass (STUDIOS-WORK-PAGE-1, Principal 2026-10-28). Idempotent edits over site/ and the generators.

- Header on every page: Studio (/) · Work (/work) · Shop (/shop), shown on phones too (theme.js folds only longer navs).
- Footer on every page: Work (All work, Books, Video, Games) · Studio (How we work, Contact, Instagram) · Shop.
- Retired pages (slate, partnerships, portfolio, titles/runwae-and-glb; sources kept in scripts/sources/, URLs 404 with
  no forwarding): every internal link is repointed. Portfolio crumbs -> /work#design; client archives -> /work#client.
- /how-we-work: the partnership section links /contact?topic=partnerships; the closing teaser links /work#client and
  /work#design.

  python3 scripts/work_structure_pass.py && python3 scripts/build_work_page.py
"""
import glob
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SITE = os.path.join(ROOT, 'site')

STUDIO_PAGES = {'index.html', 'how-we-work.html', 'contact.html'}
WORK_PAGES = {'work.html', 'books.html', 'video.html', 'games.html', 'channels.html'}

FOOT_COLS = ('<nav class="ff-col" aria-label="Work"><h4>Work</h4><a href="/work">All work</a><a href="/books">Books</a>'
             '<a href="/video">Video</a><a href="/games">Games</a></nav>\n'
             '    <nav class="ff-col" aria-label="Studio"><h4>Studio</h4><a href="/how-we-work">How we work</a>'
             '<a href="/contact">Contact</a><a href="https://www.instagram.com/buttsstudios/" target="_blank" rel="noopener">Instagram</a></nav>\n'
             '    <!--ff-shop--><nav class="ff-col ff-shop" aria-label="Shop"><h4>Shop</h4><a href="/shop">Shop</a></nav><!--/ff-shop-->')
FOOT_RE = re.compile(r'<nav class="ff-col" aria-label="Work">.*?(?=\n  </div>\n  <div class="wrap ff-base">)', re.S)
NAV_LINKS_RE = re.compile(r'(<header class="wrap site-head">.*?</button>)(.*?)(\n  </nav>\n</header>)', re.S)

BODY = [
    # home
    ('<strong>6</strong> titles on the slate', '<strong>4</strong> titles on the slate'),
    ('<a class="btn" href="/titles">See the full slate · 6 titles</a>', '<a class="btn" href="/work#current">See all current work · 4 titles</a>'),
    ('<a class="btn" href="/partnerships">See partnerships</a>', '<a class="btn" href="/work#client">See client work</a>'),
    # how we work
    ('<a class="btn" href="/titles" style="color:var(--gold)">See the slate</a>', '<a class="btn" href="/work#current" style="color:var(--gold)">See current work</a>'),
    ('<a class="btn" href="/portfolio">See the portfolio</a>', '<a class="btn" href="/work#design">See the portfolio</a>'),
    # portfolio items
    ('<p class="pi-crumb"><a href="/portfolio">← Portfolio</a></p>', '<p class="pi-crumb"><a href="/work#design">← Portfolio</a></p>'),
    ('<a class="all" href="/portfolio">← All work</a>', '<a class="all" href="/work#design">← All design work</a>'),
    # The Little Things: the apparel line is design work now (the Runwae and GLB page is retired)
    ('<a href="/titles/runwae-and-glb#runwae-apparel">The Little Things line from Runwae Apparel</a>',
     '<a href="/portfolio/runwae-apparel">The Little Things line from Runwae Apparel</a>'),
]
HWW_PARTNER_ANCHOR = ('<p>The site, shop or product is designed and built on that identity, desktop and phone together.</p>\n'
                      '      </div>\n    </div>\n')
HWW_PARTNER_CTA = '    <p style="margin-top:32px"><a class="btn" href="/contact?topic=partnerships">Start a partnership</a></p>\n'


def nav(rel):
    cur = lambda on: ' aria-current="page"' if on else ''
    studio = rel in STUDIO_PAGES
    work = rel in WORK_PAGES or rel.split('/')[0] in ('titles', 'video', 'portfolio')
    return (f'\n    <a href="/"{cur(studio)}>Studio</a>\n    <a href="/work"{cur(work)}>Work</a>\n    <a href="/shop">Shop</a>')


def edit_page(rel, s):
    s = NAV_LINKS_RE.sub(lambda m: m.group(1) + nav(rel) + m.group(3), s, count=1)
    s = FOOT_RE.sub(lambda _: FOOT_COLS, s, count=1)
    for old, new in BODY:
        s = s.replace(old, new)
    if rel == 'how-we-work.html' and HWW_PARTNER_CTA not in s:
        s = s.replace(HWW_PARTNER_ANCHOR, HWW_PARTNER_ANCHOR + HWW_PARTNER_CTA, 1)
    return s


def edit_generators():
    n = 0
    p = os.path.join(ROOT, 'scripts', 'build_portfolio_pages.py')
    g = open(p, encoding='utf-8').read()
    h = re.sub(r'(<header class="wrap site-head">.*?</button>)(.*?)(\n  </nav>\n</header>)',
               lambda m: m.group(1) + nav('portfolio/x.html') + m.group(3), g, count=1, flags=re.S)
    h = FOOT_RE.sub(lambda _: FOOT_COLS, h, count=1)
    for old, new in BODY:
        h = h.replace(old, new)
    h = h.replace("open(os.path.join(SITE, 'portfolio.html'))", "open(os.path.join(ROOT, 'scripts', 'sources', 'portfolio.html'))")
    h = h.replace('  site/portfolio.html                    images', '  scripts/sources/portfolio.html         images')
    h = h.replace('Remove it from the portfolio.html card too.', 'Remove it from the scripts/sources/portfolio.html card too.')
    if h != g:
        open(p, 'w', encoding='utf-8').write(h)
        n += 1
    p = os.path.join(SITE, 'theme.js')
    t = open(p, encoding='utf-8').read()
    old = "  if (!links.length) return;\n"
    new = ("  // Three tabs or fewer (Studio · Work · Shop) stay visible on phones (Principal 2026-10-28); only longer navs fold.\n"
           "  if (links.length <= 3) return;\n")
    if new not in t:
        t = t.replace(old, new, 1)
        open(p, 'w', encoding='utf-8').write(t)
        n += 1
    return n


def main():
    pages = [p for p in glob.glob(os.path.join(SITE, '**', '*.html'), recursive=True)]
    n = 0
    for p in sorted(pages):
        rel = os.path.relpath(p, SITE)
        s = open(p, encoding='utf-8').read()
        if rel.startswith('work/'):  # archived client sites: only their way back
            t = s.replace('href="/partnerships">← Back to Butts Studios</a>', 'href="/work#client">← Back to Butts Studios</a>')
        else:
            t = edit_page(rel, s)
        if t != s:
            open(p, 'w', encoding='utf-8').write(t)
            n += 1
    n += edit_generators()
    print('structure pass: %d file(s) changed' % n)


if __name__ == '__main__':
    main()
