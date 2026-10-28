#!/usr/bin/env python3
"""URL-map test for buttsstudios.com (STUDIOS-URL-MAP-1). Stdlib only; emulates Vercel routing from site/vercel.json.

  python3 scripts/check_url_map.py                  # exit 1 on any problem
  STUDIOS_SITE=/path/to/other/site python3 scripts/check_url_map.py   # test another checkout (e.g. main)

Routing is emulated against the deploy layout (url_map.stage_pages: each page at <clean>/index.html).
Proves: every internal link is a live canonical clean URL; no link points at a retired URL or retired subdomain;
vercel.json has no redirect rules (no forwarding, Principal 2026-10-28) and every retired URL (old .html paths,
/slate, /titles/the-channels ...) 404s; canonical tags carry no .html; the game is Glowgrid, never GLB, in game copy;
the three paid-game Payment Links are on /games; vercel.json is the one url_map.py generates.
"""
import atexit
import json
import os
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import url_map as U  # noqa: E402

SITE = U.SITE
PAYMENT_LINKS = ['6oU7sE8SL7Ug4Gt99t7Re09', '8x24gsed5gqM6OBdpJ7Re0a', '4gM7sEd912zWc8V0CX7Re0b']
RETIRED_HOSTS = set(U.RETIRED_HOSTS)


def staged_site():
    """Copy site/ and apply the deploy layout, so the emulation sees what Vercel serves."""
    d = tempfile.mkdtemp(prefix='studios-stage-')
    atexit.register(shutil.rmtree, d, True)
    dst = os.path.join(d, 'site')
    shutil.copytree(SITE, dst)
    U.stage_pages(dst)
    return dst


ROOT = SITE  # replaced by the staged copy in main()


def compile_source(src):
    """Vercel/path-to-regexp subset: :name, :name(regex), :name*, :name+ ."""
    out, i = '^', 0
    while i < len(src):
        c = src[i]
        if c == ':':
            m = re.match(r':([A-Za-z_]+)(\((?:[^()]*)\))?([*+?])?', src[i:])
            name, rx, mod = m.group(1), m.group(2), m.group(3)
            body = rx[1:-1] if rx else '[^/]+'
            if mod == '*':
                out += '(?P<%s>(?:%s)(?:/(?:%s))*)?' % (name, body, body) if rx else '(?P<%s>.*)' % name
            elif mod == '+':
                out += '(?P<%s>.+)' % name if not rx else '(?P<%s>(?:%s)(?:/(?:%s))*)' % (name, body, body)
            else:
                out += '(?P<%s>%s)' % (name, body)
            i += len(m.group(0))
        else:
            out += re.escape(c)
            i += 1
    return re.compile(out + '$')


def subst(dest, groups):
    for k, v in groups.items():
        dest = dest.replace(':' + k, v or '')
    return dest


class Router:
    def __init__(self, cfg):
        self.redirects = [(compile_source(r['source']), r) for r in cfg.get('redirects', [])]
        self.rewrites = [(compile_source(r['source']), r) for r in cfg.get('rewrites', [])]

    @staticmethod
    def file_exists(path):
        p = os.path.join(ROOT, path.lstrip('/'))
        return os.path.isfile(p) or os.path.isfile(os.path.join(p, 'index.html')) and os.path.isdir(p)

    def route(self, host, path, hops=0):
        """-> ('redirect', status, dest) | ('file', path) | ('proxy', url) | ('404',)"""
        for rx, r in self.redirects:
            has = r.get('has')
            if has and not all(h['type'] == 'host' and h['value'] == host for h in has):
                continue
            m = rx.match(path)
            if m:
                return ('redirect', r.get('statusCode', 308), subst(r['destination'], m.groupdict()))
        if path != '/' and path.endswith('/'):
            return ('redirect', 308, path.rstrip('/'))
        if self.file_exists(path):
            return ('file', path)
        for rx, r in self.rewrites:
            m = rx.match(path)
            if m:
                d = subst(r['destination'], m.groupdict())
                if d.startswith('http'):
                    return ('proxy', d)
                return ('file', d) if self.file_exists(d) else ('404',)
        return ('404',)

    def final(self, host, path):
        chain = []
        for _ in range(6):
            res = self.route(host, path)
            if res[0] != 'redirect':
                return chain, res
            chain.append(res)
            dest = res[2]
            if dest.startswith('http'):
                u = urlsplit(dest)
                host, path = u.netloc, u.path or '/'
            else:
                path = dest
                host = host if host == 'buttsstudios.com' else 'buttsstudios.com'
        return chain, ('loop',)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.meta, self.canon = [], {}, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ('href', 'src', 'poster'):
            if a.get(k) and tag in ('a', 'link', 'script', 'img', 'source', 'video'):
                self.refs.append((tag, a[k]))
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canon = a.get('href')
        if tag == 'meta' and a.get('property') == 'og:url':
            self.meta['og:url'] = a.get('content')


def html_files():
    for root, _, files in os.walk(SITE):
        for f in files:
            if f.endswith('.html') and not f.startswith('_'):
                p = os.path.join(root, f)
                rel = os.path.relpath(p, SITE)
                if rel.startswith('work/wham-studios/vendor'):
                    continue
                yield rel


def main():
    problems = []

    def bad(msg):
        problems.append(msg)

    vpath = os.path.join(SITE, 'vercel.json')
    if not os.path.exists(vpath):
        bad('site/vercel.json missing')
        cfg = {}
    else:
        cfg = json.load(open(vpath))
        if json.dumps(cfg, sort_keys=True) != json.dumps(U.build_vercel(), sort_keys=True):
            bad('vercel.json differs from url_map.build_vercel(): run python3 scripts/url_map.py --write-vercel')
    if cfg.get('redirects'):
        bad('vercel.json has %d redirect rules; retired URLs are not forwarded (Principal 2026-10-28)' % len(cfg['redirects']))
    global ROOT
    ROOT = staged_site()
    rt = Router(cfg)
    pm = U.page_map()

    # 1. every canonical page serves 200 at its clean URL, and every internal link is a live canonical URL
    for f, clean in sorted(pm.items()):
        chain, res = rt.final('buttsstudios.com', clean)
        if chain or res[0] != 'file' or res[1] != clean:
            bad('clean URL %s does not serve %s directly (got %s %s)' % (clean, f, chain, res))
    for g in U.GAMES:
        chain, res = rt.final('buttsstudios.com', '/games/%s' % g)
        if chain or res[0] != 'proxy':
            bad('/games/%s is not served' % g)
    chain, res = rt.final('buttsstudios.com', '/shop')
    if chain or res[0] != 'proxy':
        bad('/shop is not served')

    for rel in html_files():
        pg = Page()
        text = open(os.path.join(SITE, rel), encoding='utf-8').read()
        pg.feed(text)
        for tag, ref in pg.refs:
            u = urlsplit(ref)
            if u.scheme in ('mailto', 'tel', 'data', 'javascript') or ref.startswith('#'):
                continue
            if u.scheme or ref.startswith('//'):
                if u.netloc in RETIRED_HOSTS:
                    bad('%s: links the retired host %s' % (rel, ref))
                if u.netloc == 'buttsstudios.com' and tag == 'a' and u.path.endswith('.html'):
                    bad('%s: absolute link keeps .html: %s' % (rel, ref))
                continue
            if rel.startswith('work/') and not ref.startswith('/'):
                continue  # archived originals keep their own relative bundle
            path = u.path
            if not path:
                continue
            if not path.startswith('/'):
                path = os.path.normpath(os.path.join('/' + os.path.dirname(rel), path))
            chain, res = rt.final('buttsstudios.com', path)
            if res[0] in ('404', 'loop'):
                bad('%s: broken link %s' % (rel, ref))
            elif chain:
                bad('%s: link %s redirects (%s); link the canonical URL' % (rel, ref, chain[0][2]))
        if not rel.startswith('work/') and rel in pm and (pg.canon or pg.meta.get('og:url')):
            want = 'https://buttsstudios.com' + (pm[rel] if pm[rel] != '/' else '/')
            if pg.canon is not None and pg.canon != want:
                bad('%s: canonical %s should be %s' % (rel, pg.canon, want))
            if pg.meta.get('og:url') is not None and pg.meta.get('og:url') != want:
                bad('%s: og:url %s should be %s' % (rel, pg.meta.get('og:url'), want))

    # 2. retired URLs stop existing: no redirect, 404 (no forwarding)
    legacy = list(U.LEGACY_PATHS) + ['/portfolio/%s.html' % s for s in U.portfolio_slugs()]
    for p in sorted(set(legacy) - {'/index.html'}):  # /index.html is the home page file itself; static hosting serves it
        chain, res = rt.final('buttsstudios.com', p)
        if chain:
            bad('retired %s is forwarded (%s); retired URLs must not redirect' % (p, chain[0]))
        elif res[0] != '404':
            bad('retired %s still serves (%s); it must 404' % (p, res))
    for host in sorted(RETIRED_HOSTS):
        chain, res = rt.final(host, '/')
        if chain:
            bad('retired host %s is forwarded by the site config (%s)' % (host, chain[0]))

    # 3. copy: the game is Glowgrid; the three paid-game Payment Links are on /games
    games = open(os.path.join(SITE, 'games.html'), encoding='utf-8').read() if os.path.exists(os.path.join(SITE, 'games.html')) else ''
    if re.search(r'\bGLB\b', games):
        bad('games.html still says GLB (the game is Glowgrid)')
    for plink in PAYMENT_LINKS:
        if 'buy.stripe.com/' + plink not in games:
            bad('games.html lost Payment Link %s' % plink)
    for rel in ('index.html', 'video.html', 'books.html'):
        t = open(os.path.join(SITE, rel), encoding='utf-8').read() if os.path.exists(os.path.join(SITE, rel)) else ''
        if re.search(r'store\.buttsstudios\.com', t):
            bad('%s links store.buttsstudios.com (the shop is /shop)' % rel)

    # 4. sitemap
    sm = os.path.join(SITE, 'sitemap.xml')
    if not os.path.exists(sm):
        bad('sitemap.xml missing')
    else:
        for loc in re.findall(r'<loc>https://buttsstudios\.com([^<]*)</loc>', open(sm).read()):
            chain, res = rt.final('buttsstudios.com', loc or '/')
            if chain or res[0] not in ('file', 'proxy'):
                bad('sitemap lists %s which is not a live canonical URL' % loc)

    for p in problems:
        print('FAIL', p)
    print('%d problem(s)' % len(problems))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
