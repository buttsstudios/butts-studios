#!/usr/bin/env python3
"""Build site/portfolio/<slug>.html, one page per portfolio item.

Inputs:
  site/portfolio.html                     images, palette/type rows, names (source of truth for the cards)
  scripts/portfolio_copy.json             about / tagline / studio / articles per item (paraphrased from each item's own site)
  scripts/portfolio_extra_images.json     extra gallery images (fresh captures) with captions + alt text
Run: python3 scripts/build_portfolio_pages.py   (re-checks every live URL with curl; Visit only on 200)
"""
import html, json, os, re, subprocess
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
ASSETS = os.path.join(SITE, 'assets', 'portfolio')
OUT = os.path.join(SITE, 'portfolio')

ITEMS = [  # slug, url, made
    ('huntington-applied', 'https://huntingtonapplied.com', 'Identity · Website'),
    ('runwae-apparel', None, 'Identity · Print · Product imagery'),
    ('dailyaitoll', 'https://dailyaitoll.com', 'Identity · Data site'),
    ('latarence', 'https://latarence.com', 'Identity · Personal site'),
    ('ridgefield', 'https://ridgefieldtech.com', 'Identity · Website'),
    ('signals-institute', 'https://thesignalsinstitute.com', 'Identity · Website'),
    ('boltzmann', 'https://boltzmann.app', None),
    ('chief', 'https://badgechief.com', None),
    ('landslide', 'https://landslide.global', None),
    ('tillio', 'https://tillio.ai', None),
    ('document-scanner', 'https://documentscanner.app', None),
    ('runwae', 'https://runwae.com', None),
    ('chrona', 'https://chronarf.com', None),
    ('blacklab', 'https://blacklab.world', None),
    ('raphael', 'https://raphaelresearch.com', None),
    ('sage', 'https://sagesimulation.com', None),
    ('farad', 'https://faraddefense.com', None),
    ('tiffany', 'https://tiffanyapp.com', None),
    ('nods', 'https://nods.dev', None),
    ('rigor', 'https://rigor.world', None),
    ('kitch', 'https://kitch.global', None),
    ('fasci', 'https://fasci.app', None),
    ('good-tea', 'https://goodtea.world', None),
    ('prophet', 'https://prophetai.world', None),
    ('sentinel', 'https://sentinelscanner.com', None),
]

E = html.escape


def live(url):
    if not url:
        return False
    try:
        code = subprocess.run(['curl', '-sL', '-o', '/dev/null', '-m', '25', '-w', '%{http_code}', url],
                              capture_output=True, text=True, timeout=40).stdout.strip()
    except Exception:
        return False
    return code == '200'


def dims(rel):
    with Image.open(os.path.join(SITE, rel)) as im:
        return im.size


def thumb_for(href):
    base, ext = os.path.splitext(href)
    t = base + '-720' + ext
    return t if os.path.exists(os.path.join(SITE, t)) else None


def parse_block(src, slug):
    m = re.search(r'<article class="(case|pf-product[^"]*)" id="%s">(.*?)</article>' % re.escape(slug), src, re.S)
    assert m, slug
    is_case = m.group(1) == 'case'
    body = m.group(2)
    name = re.sub(r'<[^>]+>', '', re.search(r'<h[23]>(.*?)</h[23]>', body, re.S).group(1)).strip()
    info = {'case': is_case, 'name': html.unescape(name), 'images': [], 'rows': []}
    if is_case:
        info['kind'] = html.unescape(re.search(r'<p class="kind">(.*?)</p>', body).group(1))
        info['desc'] = re.search(r'<p class="desc">(.*?)</p>', body, re.S).group(1)
        dl = re.search(r'<dl>(.*?)</dl>', body, re.S).group(1)
        info['rows'] = re.findall(r'<div><dt>.*?</dd></div>', dl, re.S)
    else:
        info['desc'] = re.search(r'</h3><p>(.*?)</p>', body, re.S).group(1)
    for z in re.finditer(r'<a class="zoom" href="([^"]+)" data-gallery="[^"]*" data-caption="([^"]*)"><img ([^>]*)></a>', body):
        before = body[max(0, z.start() - 400):z.start()]
        kinds = {'phone': before.rfind('class="phone'), 'plate': before.rfind('class="plate'), 'shot': before.rfind('class="pf-frame')}
        kind = max(kinds, key=kinds.get)
        attrs = dict(re.findall(r'([a-z-]+)="([^"]*)"', z.group(3)))
        img = {'href': z.group(1), 'caption': html.unescape(z.group(2)), 'alt': html.unescape(attrs.get('alt', '')),
               'kind': kind, 'imgclass': attrs.get('class')}
        if kind == 'plate':
            pm = re.findall(r'class="plate ([^"]+)"', before)
            img['plate'] = pm[-1] if pm else ''
        info['images'].append(img)
    return info


def short_caption(name, cap):
    for pre in (name + ' · ', 'Daily AI Toll · ', 'The Signals Institute · '):
        if cap.startswith(pre):
            return cap[len(pre):]
    return cap


def img_tag(img, sizes):
    href = img['href']
    cls = f' class="{img["imgclass"]}"' if img.get('imgclass') else ''
    if href.endswith('.svg'):
        return f'<img{cls} src="../{href}" alt="{E(img["alt"])}">'
    w, h = dims(href)
    t = thumb_for(href)
    if t:
        return (f'<img{cls} src="../{t}" srcset="../{t} 720w, ../{href} {w}w" sizes="{sizes}" width="{w}" height="{h}" '
                f'alt="{E(img["alt"])}" loading="lazy">')
    return f'<img{cls} src="../{href}" width="{w}" height="{h}" alt="{E(img["alt"])}" loading="lazy">'


def zoom(img, slug, name, sizes):
    cap = f'{name} · {img["short"]}'
    return (f'<a class="zoom" href="../{img["href"]}" data-gallery="{slug}" data-caption="{E(cap)}">'
            f'{img_tag(img, sizes)}</a>')


def figure(img, slug, name):
    s = E(img['short'])
    if img['kind'] == 'phone':
        return (f'<figure class="g-phone"><div class="phone">{zoom(img, slug, name, "(max-width: 900px) 50vw, 25vw")}</div>'
                f'<figcaption>{s}</figcaption></figure>')
    if img['kind'] == 'plate':
        return (f'<figure class="plate-fig"><div class="plate {img["plate"]}"><div>{zoom(img, slug, name, "50vw")}</div></div>'
                f'<figcaption>{s}</figcaption></figure>')
    return (f'<figure class="pf-shot"><div class="pf-frame">{zoom(img, slug, name, "(max-width: 900px) 100vw, 50vw")}</div>'
            f'<figcaption>{s}</figcaption></figure>')


HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} · Portfolio · Butts Studios</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex">
<link rel="icon" type="image/svg+xml" href="../favicon.svg">
<link rel="icon" type="image/png" href="../favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&display=swap" rel="stylesheet">
<script>try{{var t=localStorage.getItem("bs-theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<link rel="stylesheet" href="../styles.css">
<link rel="stylesheet" href="../portfolio.css">
<link rel="stylesheet" href="../portfolio-item.css">
<script src="../theme.js" defer></script>
</head>
<body>

<header class="wrap site-head">
  <a class="mark" href="../index.html" aria-label="Butts Studios home"><svg class="brand-x" viewBox="0 0 100 100" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="12"><rect x="10" y="10" width="80" height="80"/><path d="M10 10 L90 90 M90 10 L10 90"/></g></svg><span class="brand-word">Butts<br>Studios</span></a>
  <nav>
    <button class="theme-toggle" type="button" aria-label="Switch color mode"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    <a href="../slate.html">Slate</a>
    <a href="../how-we-work.html">How we work</a>
    <a href="../partnerships.html">Partnerships</a>
    <a href="../portfolio.html" aria-current="page">Portfolio</a>
  </nav>
</header>
'''

FOOT = '''
<footer class="site-foot">
  <div class="wrap">
    <span><span class="gold">Butts Studios</span> · Production studio since 2018</span>
    <span><a href="../partnerships.html">Partnerships</a> &nbsp;·&nbsp; <a href="../portfolio.html">← All work</a></span>
  </div>
</footer>

<script src="../lightbox.js" defer></script>
</body>
</html>
'''


def build():
    src = open(os.path.join(SITE, 'portfolio.html')).read()
    copy = json.load(open(os.path.join(ROOT, 'scripts', 'portfolio_copy.json')))
    extra = json.load(open(os.path.join(ROOT, 'scripts', 'portfolio_extra_images.json')))
    mock_path = os.path.join(ROOT, 'scripts', 'portfolio_mockups.json')
    mockups = json.load(open(mock_path)) if os.path.exists(mock_path) else {}
    vids_path = os.path.join(ROOT, 'scripts', 'portfolio_videos.json')
    videos = json.load(open(vids_path)) if os.path.exists(vids_path) else {}
    os.makedirs(OUT, exist_ok=True)
    infos = []
    for slug, url, made in ITEMS:
        info = parse_block(src, slug)
        info.update(slug=slug, url=url, made=made, live=live(url))
        infos.append(info)
    report = []
    for i, info in enumerate(infos):
        slug, name = info['slug'], info['name']
        c = copy[slug]
        imgs = []
        for img in info['images']:
            img['short'] = short_caption(name, img['caption'])
            imgs.append(img)
        for row in extra.get(slug, []):
            base, cap, alt = row[:3]
            href = f'assets/portfolio/{base}.webp'
            assert os.path.exists(os.path.join(SITE, href)), href
            imgs.append({'href': href, 'short': cap, 'alt': alt, 'kind': row[3] if len(row) > 3 else 'shot'})
        lead = next(x for x in imgs if x['kind'] == 'shot')
        rest = [x for x in imgs if x is not lead]
        rest.sort(key=lambda x: {'shot': 0, 'plate': 1, 'phone': 2}[x['kind']])
        kind = info.get('kind') or ('Product · ' + (c.get('made') or 'Landing site'))
        tagline = c.get('tagline') or re.sub(r'<[^>]+>', '', info['desc'])
        visit = (f'<a class="open-site" href="{info["url"]}" target="_blank" rel="noopener">Visit ↗</a>' if info['live'] else '')

        out = [HEAD.format(title=E(name), desc=E(f'{name}: {tagline} Designed by Butts Studios.'))]
        out.append('<main>\n  <div class="wrap">\n')
        mock = mockups.get(slug)
        mock_fig = ''
        if mock:
            mhref = f'assets/portfolio/{mock[0]}.webp'
            assert os.path.exists(os.path.join(SITE, mhref)), mhref
            m = {'href': mhref, 'short': 'Mockup: ' + mock[1], 'alt': mock[2]}
            mock_fig = (f'\n      <figure class="pi-mock">{zoom(m, slug, name, "(max-width: 900px) 100vw, 55vw")}'
                        f'<figcaption><span class="mock-tag">Mockup</span> {E(mock[1])}</figcaption></figure>')
        out.append(f'''    <section class="pi-hero{' has-mock' if mock else ''}">
      <div class="pi-hero-text">
      <p class="pi-crumb"><a href="../portfolio.html">← Portfolio</a></p>
      <h1 class="display">{E(name)}</h1>
      <p class="kind">{E(kind)}</p>
      <p class="lede">{E(tagline)}</p>
      {visit}
      </div>{mock_fig}
    </section>
''')
        out.append(f'    <figure class="pf-shot pi-lead"><div class="pf-frame">{zoom(lead, slug, name, "(max-width: 1400px) 100vw, 1360px")}</div>'
                   f'<figcaption><b>{E(lead["short"])}</b></figcaption></figure>\n')
        # about + details
        paras = ''.join(f'        <p>{E(p)}</p>\n' for p in c['about'])
        studio = f'        <p class="pi-studio">{E(c["studio"])}</p>\n' if c.get('studio') else ''
        made_txt = info['made'] or c.get('made') or 'Landing site'
        rows = [f'<div><dt>What we made</dt><dd>{E(made_txt)}</dd></div>']
        rows += info['rows']
        if info['live']:
            dom = info['url'].split('//', 1)[1]
            rows.append(f'<div><dt>Live</dt><dd><a href="{info["url"]}" target="_blank" rel="noopener">{dom} ↗</a></dd></div>')
        rows.append('<div><dt>Captured</dt><dd>October 2026</dd></div>')
        out.append(f'''    <section class="pi-body t-grid" aria-labelledby="about-h">
      <div class="prose">
        <h2 id="about-h">About</h2>
{paras}{studio}      </div>
      <div class="pi-details">
        <h2>Details</h2>
        <dl>
          {chr(10).join("          " + r for r in rows).strip()}
        </dl>
      </div>
    </section>
''')
        if rest:
            n = len(imgs)
            figs = '\n'.join('        ' + figure(x, slug, name) for x in rest)
            out.append(f'''    <section class="pi-section" aria-labelledby="gallery-h">
      <div class="section-head"><h2 id="gallery-h">Gallery</h2><p>{n} images. Tap any one to see it full size.</p></div>
      <div class="pi-gallery">
{figs}
      </div>
    </section>
''')
        vids = videos.get(slug, [])
        if vids:
            vs = []
            for base, form, cap in vids:
                v = f'../assets/video/{base}'
                assert os.path.exists(os.path.join(SITE, 'assets', 'video', base + '-transcode.mp4')), base
                vs.append(f'        <figure class="pi-film {form}"><video autoplay muted loop playsinline preload="metadata" poster="{v}-poster.jpg" aria-label="{E(cap)}">'
                          f'<source src="{v}-transcode.webm" type="video/webm"><source src="{v}-transcode.mp4" type="video/mp4"></video>'
                          f'<figcaption>{E(cap)}</figcaption></figure>')
            out.append(f'''    <section class="pi-section" aria-labelledby="film-h">
      <div class="section-head"><h2 id="film-h">From the original studio site</h2><p>A short screen recording from the first Butts Studios site.</p></div>
{chr(10).join(vs)}
    </section>
''')
        arts = c.get('articles') or []
        if arts:
            lis = []
            for a in arts:
                dom = re.sub(r'^https?://(www\.)?', '', a['url']).split('/')[0]
                lis.append(f'        <li><a href="{E(a["url"])}" target="_blank" rel="noopener"><small>{E(dom)} ↗</small>'
                           f'<b>{E(a["title"])}</b><span>{E(a["desc"])}</span></a></li>')
            out.append(f'''    <section class="pi-section" aria-labelledby="articles-h">
      <div class="section-head"><h2 id="articles-h">Articles &amp; notes</h2><p>Published pages from {E(name)}: write-ups, docs and data. Each opens on its own site.</p></div>
      <ul class="pi-articles">
{chr(10).join(lis)}
      </ul>
    </section>
''')
        prev, nxt = infos[i - 1], infos[(i + 1) % len(infos)]
        out.append(f'''    <nav class="pi-pager" aria-label="More work">
      <a class="prev" href="{prev["slug"]}.html"><small>← Previous</small><b>{E(prev["name"])}</b></a>
      <a class="all" href="../portfolio.html">← All work</a>
      <a class="next" href="{nxt["slug"]}.html"><small>Next →</small><b>{E(nxt["name"])}</b></a>
    </nav>
''')
        out.append('  </div>\n</main>\n')
        out.append(FOOT)
        open(os.path.join(OUT, slug + '.html'), 'w').write(''.join(out))
        report.append((slug, len(imgs), len(arts), info['live']))
    for r in report:
        print('%-20s images=%-2d articles=%-2d live=%s' % r)


if __name__ == '__main__':
    build()
