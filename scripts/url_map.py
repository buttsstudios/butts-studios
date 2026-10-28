#!/usr/bin/env python3
"""Single source of truth for the buttsstudios.com URL map (2026-10-28, STUDIOS-URL-MAP-1).

Canonical URLs have no .html. Page files keep their names in the repo; at deploy, stage_pages() moves each page to
<clean path>/index.html so the clean URL is served directly by the filesystem.

No forwarding (Principal 2026-10-28: "no forwarding except for the domains we particularly setup for the purpose of
forwarding"): retired URLs (old .html paths, /slate, /titles/the-channels, the old game/store subdomains) are not
redirected; they stop existing (404), and the old subdomains are removed (~/go-remove-studios-subdomains.sh).
scripts/check_url_map.py proves every LEGACY_PATHS entry 404s and that vercel.json carries no redirect rules.
"""
import glob
import os

SITE = os.path.normpath(os.environ.get('STUDIOS_SITE') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site'))

# file (relative to site/) -> canonical clean path
STATIC_PAGES = {
    'index.html': '/',
    'books.html': '/books',
    'video.html': '/video',
    'games.html': '/games',
    'slate.html': '/titles',
    'channels.html': '/channels',
    'work.html': '/work',
    'portfolio.html': '/portfolio',
    'partnerships.html': '/partnerships',
    'how-we-work.html': '/how-we-work',
    'terms.html': '/terms',
    'privacy.html': '/privacy',
    'refunds.html': '/refunds',
    'titles/talon.html': '/titles/talon',
    'titles/the-little-things.html': '/titles/the-little-things',
    'titles/us-against-the-world.html': '/titles/us-against-the-world',
    'titles/runwae-and-glb.html': '/titles/runwae-and-glb',
}

# Games run in their own Vercel projects and are served under /games/<slug> by a proxy rewrite (same pattern as /shop).
GAMES = {
    'glowgrid': {'origin': 'https://glb-game.vercel.app', 'host': 'glb.buttsstudios.com', 'basepath': False},
    'cards': {'origin': 'https://butts-cards.vercel.app', 'host': 'cards.buttsstudios.com', 'basepath': True},
    'sliding-numbers': {'origin': 'https://butts-puzzle.vercel.app', 'host': 'puzzle.buttsstudios.com', 'basepath': True},
}

# Retired subdomains (removed, not forwarded). The site must not link them.
RETIRED_HOSTS = ['glb.buttsstudios.com', 'cards.buttsstudios.com', 'puzzle.buttsstudios.com', 'games.buttsstudios.com',
                 'portal.buttsstudios.com', 'store.buttsstudios.com']

# Also slated for removal (Principal 2026-10-28), but they still hold their own live sites (novels = The Signal, film,
# animation, clients) and books.html / video.html link them. Their links get repointed when the content moves.
PENDING_REMOVAL_HOSTS = ['novels.buttsstudios.com', 'film.buttsstudios.com', 'animation.buttsstudios.com',
                         'clients.buttsstudios.com']

# Everything the Principal-facing site has ever linked or served (live crawl 2026-10-28 plus repo history).
LEGACY_PATHS = [
    '/index.html', '/books.html', '/video.html', '/games.html', '/slate.html', '/work.html', '/portfolio.html',
    '/partnerships.html', '/how-we-work.html', '/terms.html', '/privacy.html', '/refunds.html',
    '/titles/talon.html', '/titles/the-little-things.html', '/titles/us-against-the-world.html',
    '/titles/runwae-and-glb.html', '/titles/the-channels.html', '/slate', '/titles/the-channels', '/the-signal',
    '/refund', '/channels.html',
]


def clean_target(path):
    """Clean URL path -> ('file', relpath) | ('proxy', slug) | None."""
    path = path.rstrip('/') or '/'
    for f, clean in page_map().items():
        if clean == path:
            return ('file', f)
    if path == '/shop' or path.startswith('/shop/'):
        return ('proxy', 'shop')
    if path.startswith('/games/') and path.split('/')[2] in GAMES:
        return ('proxy', path.split('/')[2])
    return None


def portfolio_slugs():
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(SITE, 'portfolio', '*.html')))


def page_map():
    """file -> clean path, including the generated portfolio item pages."""
    m = dict(STATIC_PAGES)
    for s in portfolio_slugs():
        m['portfolio/%s.html' % s] = '/portfolio/%s' % s
    return m


SHOP_ORIGIN = 'https://shop-buttsstudios.vercel.app'


def build_vercel():
    """vercel.json for the buttsstudios.com project. No redirects (no forwarding); clean paths are served by the
    staged layout (stage_pages); only the separately deployed shop and games are proxied under this domain."""
    rewrites = [
        {'source': '/shop', 'destination': SHOP_ORIGIN + '/shop/'},
        {'source': '/shop/:path*', 'destination': SHOP_ORIGIN + '/shop/:path*'},
    ]
    for slug, g in GAMES.items():
        if g['basepath']:
            rewrites.append({'source': '/games/%s' % slug, 'destination': '%s/games/%s' % (g['origin'], slug)})
            rewrites.append({'source': '/games/%s/:path*' % slug, 'destination': '%s/games/%s/:path*' % (g['origin'], slug)})
        else:
            rewrites.append({'source': '/games/%s' % slug, 'destination': g['origin'] + '/'})
            rewrites.append({'source': '/games/%s/:path*' % slug, 'destination': g['origin'] + '/:path*'})
    return {
        'cleanUrls': False,
        'trailingSlash': False,
        'headers': [{'source': '/assets/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=604800'}]}],
        'rewrites': rewrites,
    }


def staged_file(f):
    """Repo page file -> path inside the deploy stage (clean path + /index.html; the home page stays index.html)."""
    clean = page_map().get(f)
    if clean is None or clean == '/':
        return f
    return clean.lstrip('/') + '/index.html'


def stage_pages(stage):
    """Move every page in a staged copy of site/ to <clean>/index.html, so /books serves and /books.html 404s.
    Browsers resolve relative refs against the URL, which does not change, so page content needs no edit."""
    moves = []
    for f in sorted(page_map(), key=lambda x: -x.count('/')):  # deepest first: titles/talon.html before slate.html
        dst = staged_file(f)
        if dst == f:
            continue
        src_p, dst_p = os.path.join(stage, f), os.path.join(stage, dst)
        if not os.path.isfile(src_p):
            continue
        if os.path.exists(dst_p):
            raise SystemExit('stage_pages: %s already exists' % dst)
        os.makedirs(os.path.dirname(dst_p), exist_ok=True)
        os.rename(src_p, dst_p)
        moves.append((f, dst))
    return moves


if __name__ == '__main__':
    import json
    import sys
    if '--write-vercel' in sys.argv:
        with open(os.path.join(SITE, 'vercel.json'), 'w') as fh:
            json.dump(build_vercel(), fh, indent=2)
            fh.write('\n')
        print('wrote site/vercel.json')
    if '--stage' in sys.argv:
        stage = sys.argv[sys.argv.index('--stage') + 1]
        moved = stage_pages(stage)
        print('staged %d pages as <clean>/index.html' % len(moved))
    if '--write-sitemap' in sys.argv:
        urls = sorted(set(page_map().values()) | {'/games/%s' % g for g in GAMES} | {'/shop'})
        body = ''.join('  <url><loc>https://buttsstudios.com%s</loc></url>\n' % u for u in urls)
        with open(os.path.join(SITE, 'sitemap.xml'), 'w') as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '</urlset>\n')
        with open(os.path.join(SITE, 'robots.txt'), 'w') as fh:
            fh.write('User-agent: *\nAllow: /\nSitemap: https://buttsstudios.com/sitemap.xml\n')
        print('wrote sitemap.xml, robots.txt')
