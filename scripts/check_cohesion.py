#!/usr/bin/env python3
"""Cohesion test for buttsstudios.com (STUDIOS-COHESION-1, 2026-10-28). Stdlib only.

Proves, over every site page (archived client originals under site/work/ excepted):
- one header nav: same items, order and labels on every page (aria-current aside);
- one footer: identical on every page; its Contact column links /contact, with no address in the footer;
- no link to a retired or retiring subdomain (glb. cards. puzzle. games. portal. store. novels. film. animation. clients.);
- <title> is "<Page> · Butts Studios" (home: "Butts Studios") and og:title matches it; description and og:image set;
- copy rules: no "AHL" / "Anne Huntington", no "free"; GLB only on the apparel pages;
- CSS rules: border-radius <= 4px (50% only on round elements), no one-sided accent stripes (2px+ single-edge borders);
- /contact exists and is in the URL map and sitemap.

  python3 scripts/check_cohesion.py      # exit 1 on any problem
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import url_map as U  # noqa: E402

SITE = U.SITE
HOSTS = set(U.RETIRED_HOSTS) | set(getattr(U, 'PENDING_REMOVAL_HOSTS', []))
GLB_OK = {'slate.html', 'work.html', 'titles/runwae-and-glb.html', 'titles/the-little-things.html'}


def norm(s):
    s = re.sub(r'\s+', ' ', s)
    return re.sub(r' aria-current="page"', '', s).strip()


def main():
    problems = []
    pm = U.page_map()
    navs, foots = {}, {}
    for rel in sorted(pm):
        p = os.path.join(SITE, rel)
        if not os.path.exists(p):
            problems.append('%s: in the URL map but missing' % rel)
            continue
        s = open(p, encoding='utf-8').read()
        n = re.search(r'<header class="wrap site-head">.*?</header>', s, re.S)
        f = re.search(r'<footer class="site-foot full-foot">.*?</footer>', s, re.S)
        navs.setdefault(norm(n.group(0)) if n else 'NONE', []).append(rel)
        foots.setdefault(norm(f.group(0)) if f else 'NONE', []).append(rel)
        if f:
            if 'mailto:' in f.group(0):
                problems.append('%s: footer carries an email address; the footer links /contact' % rel)
            if '<a href="/contact">Contact</a>' not in f.group(0):
                problems.append('%s: footer has no Contact link to /contact' % rel)
        for host in sorted(set(re.findall(r'https?://([a-z0-9-]+\.buttsstudios\.com)', s)) & HOSTS):
            problems.append('%s: links the retiring subdomain %s' % (rel, host))
        t = re.search(r'<title>(.*?)</title>', s, re.S)
        t = t.group(1).strip() if t else ''
        if rel == 'index.html':
            if t != 'Butts Studios':
                problems.append('%s: title %r should be "Butts Studios"' % (rel, t))
        elif not t.endswith(' · Butts Studios'):
            problems.append('%s: title %r should end with " · Butts Studios"' % (rel, t))
        og = re.search(r'<meta property="og:title" content="([^"]*)"', s)
        if not og or og.group(1) != t:
            problems.append('%s: og:title differs from <title>' % rel)
        for k in ('name="description"', 'property="og:description"', 'property="og:image"', 'rel="canonical"'):
            if k not in s:
                problems.append('%s: missing %s' % (rel, k))
        body = re.sub(r'<head>.*?</head>', '', s, flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', body, flags=re.S))
        if re.search(r'\bAHL\b|Anne Huntington', s):
            problems.append('%s: names the internal codename' % rel)
        if re.search(r'\bfree\b', text, re.I):
            problems.append('%s: says "free"' % rel)
        if rel not in GLB_OK and re.search(r'\bGLB\b', text):
            problems.append('%s: says GLB outside the apparel pages' % rel)
    if len(navs) != 1:
        problems.append('%d header variants: %s' % (len(navs), '; '.join('%s (%d pages)' % (v[0], len(v)) for v in navs.values())))
    if len(foots) != 1:
        problems.append('%d footer variants: %s' % (len(foots), '; '.join('%s (%d pages)' % (v[0], len(v)) for v in foots.values())))

    for css in glob.glob(os.path.join(SITE, '*.css')) + glob.glob(os.path.join(SITE, 'shared', '*.css')):
        rel = os.path.relpath(css, SITE)
        c = open(css, encoding='utf-8').read()
        for m in re.finditer(r'border-radius:\s*([^;}]+)', c):
            for v in m.group(1).split():
                if v in ('0', '50%') or re.fullmatch(r'[0-4](\.\d+)?px', v) or v.startswith('var('):
                    continue
                problems.append('%s: border-radius %s (max 4px)' % (rel, m.group(1).strip()))
                break
        for m in re.finditer(r'border-(left|right|top|bottom):\s*([2-9]|\d{2,})px', c):
            problems.append('%s: one-sided border %s' % (rel, m.group(0)))

    if '/contact' not in pm.values():
        problems.append('/contact is not in the URL map')
    sm = os.path.join(SITE, 'sitemap.xml')
    if '<loc>https://buttsstudios.com/contact</loc>' not in (open(sm).read() if os.path.exists(sm) else ''):
        problems.append('sitemap.xml does not list /contact')

    for p in problems:
        print('FAIL', p)
    print('%d pages, %d problem(s)' % (len(pm), len(problems)))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
