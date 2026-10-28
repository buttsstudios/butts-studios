#!/usr/bin/env python3
"""Site cohesion pass (STUDIOS-COHESION-1, 2026-10-28). Idempotent edits over site/*.html and the portfolio generator.

- Footer: the Contact column links /contact (Principal 2026-10-28: "a contact page instead of the email address in the
  footer"); one footer on every page.
- Body contact buttons and offer "Contact" links go to /contact. Legal pages keep the address in their text.
- Books / Video sub-nav: the subdomain links become on-site links (the titles and sections they hold).
- Books / Video index: The Signal, Butts Studios Film and Butts Studios Animation open their on-site pages
  (/titles/the-signal, /video/film, /video/animation; built by build_fold_pages.py).

  python3 scripts/cohesion_pass.py
"""
import glob
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SITE = os.path.join(ROOT, 'site')

FOOT_CONTACT_OLD = re.compile(r'<div class="ff-col"><h4>Contact</h4><a href="mailto:hello@buttsstudios\.com">hello@buttsstudios\.com</a>')
FOOT_CONTACT_NEW = '<div class="ff-col"><h4>Contact</h4><a href="/contact">Contact</a>'

BOOKS_HOSTS = '<span class="bs-sub-hosts"><a href="/titles/us-against-the-world">Us Against the World</a><a href="/titles/talon">Talon</a><a href="/titles/the-signal">The Signal</a></span>'
VIDEO_HOSTS = '<span class="bs-sub-hosts"><a href="/channels">The Channels</a><a href="/titles/the-little-things">The Little Things</a><a href="/video/film">Film</a><a href="/video/animation">Animation</a></span>'

ANIM_ROW = '''      <a class="title-row" href="/video/animation">
        <span class="no">04</span>
        <div><h3>Butts Studios Animation</h3><div class="kind">Animated shorts and motion</div></div>
        <p class="logline">Hand-drawn shorts and motion work. The first series is The Little Things.<span class="more">Read more →</span></p>
        <div class="stage"><span class="stage-label">Studio</span><span class="stage-note">Animated shorts and motion</span><span class="row-offer">Commissions</span></div>
      </a>
'''


def sub(s, old, new, count=0):
    return s.replace(old, new) if count == 0 else s.replace(old, new, count)


def edit(rel, s):
    s = FOOT_CONTACT_OLD.sub(FOOT_CONTACT_NEW, s)
    s = s.replace('<a href="mailto:hello@buttsstudios.com">Contact</a>', '<a href="/contact">Contact</a>')
    s = s.replace('<a class="btn" href="mailto:hello@buttsstudios.com" style="color:var(--gold)">hello@buttsstudios.com</a>',
                  '<a class="btn" href="/contact?topic=partnerships" style="color:var(--gold)">Start a project</a>')
    s = s.replace('<p>Write to <a href="mailto:hello@buttsstudios.com">hello@buttsstudios.com</a> with what you\'re making and where it stands.</p>',
                  '<p>Write to us on the <a href="/contact?topic=projects">contact page</a> with what you\'re making and where it stands.</p>')
    if (rel.startswith('portfolio/') or rel == 'portfolio.html') and 'rel="canonical"' not in s:
        s = re.sub(r'(<meta property="og:url" content="(https://buttsstudios\.com/portfolio(?:/[a-z0-9-]+)?)">)',
                   r'<link rel="canonical" href="\2">\n\1', s, count=1)
    if rel == 'books.html':
        s = re.sub(r'<span class="bs-sub-hosts">.*?</span></nav>', BOOKS_HOSTS + '</nav>', s, count=1, flags=re.S)
        s = s.replace('<a class="cover-card" href="https://novels.buttsstudios.com" target="_blank" rel="noopener">', '<a class="cover-card" href="/titles/the-signal">')
        s = s.replace('<b>The Signal</b> · Novel series ↗', '<b>The Signal</b> · Novel series · Book one in progress')
        s = s.replace('<a class="title-row" href="https://novels.buttsstudios.com" target="_blank" rel="noopener">', '<a class="title-row" href="/titles/the-signal">')
        s = s.replace('the books after it are coming soon.<span class="more">Open ↗</span>', 'the books after it are coming soon.<span class="more">Read more →</span>')
        s = s.replace('<span class="row-offer">Series site</span>', '<span class="row-offer">Updates by email</span>')
    if rel == 'video.html':
        s = re.sub(r'<span class="bs-sub-hosts">.*?</span></nav>', VIDEO_HOSTS + '</nav>', s, count=1, flags=re.S)
        s = s.replace('<a href="https://film.buttsstudios.com" target="_blank" rel="noopener"><span>03</span> Butts Studios Film ↗</a>',
                      '<a href="/video/film"><span>03</span> Butts Studios Film</a>')
        s = s.replace('<a class="title-row" href="https://film.buttsstudios.com" target="_blank" rel="noopener">', '<a class="title-row" href="/video/film">')
        s = s.replace('First reels coming soon.<span class="more">Open ↗</span>', 'First reels coming soon.<span class="more">Read more →</span>')
        s = s.replace('<span class="row-offer">Studio site</span>', '<span class="row-offer">Commissions</span>')
        if 'href="/video/animation">\n        <span class="no">04' not in s:
            s = re.sub(r'(<a class="title-row" href="/video/film">.*?</a>\n)', lambda m: m.group(1) + ANIM_ROW, s, count=1, flags=re.S)
        s = s.replace('<p>Channels, shorts and film, with where each one stands.</p>', '<p>Channels, shorts, film and animation, with where each one stands.</p>')
    return s


def main():
    pages = glob.glob(os.path.join(SITE, '*.html')) + glob.glob(os.path.join(SITE, 'titles', '*.html')) \
        + glob.glob(os.path.join(SITE, 'portfolio', '*.html')) + glob.glob(os.path.join(SITE, 'video', '*.html'))
    n = 0
    for p in sorted(pages):
        rel = os.path.relpath(p, SITE)
        s = open(p, encoding='utf-8').read()
        t = edit(rel, s)
        if t != s:
            open(p, 'w', encoding='utf-8').write(t)
            n += 1
    gen = os.path.join(ROOT, 'scripts', 'build_portfolio_pages.py')
    g = open(gen, encoding='utf-8').read()
    h = g.replace('<a href="https://store.buttsstudios.com">Store</a>', '<a href="/shop">Store</a>')
    h = h.replace('<div class="ff-col"><h4>Contact</h4><a href="mailto:hello@buttsstudios.com">hello@buttsstudios.com</a>', FOOT_CONTACT_NEW)
    h = h.replace('<a class="btn" href="mailto:hello@buttsstudios.com" style="color:var(--gold)">hello@buttsstudios.com</a>',
                  '<a class="btn" href="/contact?topic=partnerships" style="color:var(--gold)">Start a project</a>')
    if 'rel="canonical" href="https://buttsstudios.com/portfolio/{slug}"' not in h:
        h = h.replace('<meta property="og:url" content="https://buttsstudios.com/portfolio/{slug}">',
                      '<link rel="canonical" href="https://buttsstudios.com/portfolio/{slug}">\n<meta property="og:url" content="https://buttsstudios.com/portfolio/{slug}">')
    if h != g:
        open(gen, 'w', encoding='utf-8').write(h)
        n += 1
    print('cohesion pass: %d file(s) changed' % n)


if __name__ == '__main__':
    main()
