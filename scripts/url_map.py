#!/usr/bin/env python3
"""Single source of truth for the buttsstudios.com URL map (2026-10-28, STUDIOS-URL-MAP-1).

Canonical URLs have no .html. Page files keep their names; vercel.json rewrites the clean path to the file.
`legacy_*` lists every URL that ever shipped; scripts/check_url_map.py proves each one 301s to a live page.
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

# Old host -> new home. The hosts must be attached to the buttsstudios.com Vercel project for these rules to fire.
HOST_REDIRECTS = {
    'glb.buttsstudios.com': '/games/glowgrid',
    'cards.buttsstudios.com': '/games/cards',
    'puzzle.buttsstudios.com': '/games/sliding-numbers',
    'games.buttsstudios.com': '/games',
    'portal.buttsstudios.com': '/games',
    'store.buttsstudios.com': '/shop',
}

# Subdomains that still hold their own site (novels = The Signal, film, animation, clients). They are NOT redirected:
# doing so would remove live content. Whether they fold into /books, /video and /partnerships is a Principal call.
KEPT_HOSTS = ['novels.buttsstudios.com', 'film.buttsstudios.com', 'animation.buttsstudios.com', 'clients.buttsstudios.com']

# Old path -> new path, beyond the generic "<page>.html -> <page>" rule.
EXTRA_REDIRECTS = {
    '/slate.html': '/titles',
    '/slate': '/titles',
    '/titles/the-channels.html': '/channels',
    '/titles/the-channels': '/channels',
    '/index.html': '/',
    '/the-signal': '/books',
    '/refund': '/refunds',
}

# Everything the Principal-facing site has ever linked or served (live crawl 2026-10-28 plus repo history).
LEGACY_PATHS = [
    '/index.html', '/books.html', '/video.html', '/games.html', '/slate.html', '/work.html', '/portfolio.html',
    '/partnerships.html', '/how-we-work.html', '/terms.html', '/privacy.html', '/refunds.html',
    '/titles/talon.html', '/titles/the-little-things.html', '/titles/us-against-the-world.html',
    '/titles/runwae-and-glb.html', '/titles/the-channels.html',
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
    """vercel.json for the buttsstudios.com project: host redirects, legacy .html redirects, clean-path rewrites, proxies."""
    redirects, rewrites = [], []
    # 1. old hosts -> new paths (inert until the host is attached to this Vercel project)
    for host, dest in HOST_REDIRECTS.items():
        has = [{'type': 'host', 'value': host}]
        redirects.append({'source': '/', 'has': has, 'destination': dest, 'statusCode': 301})
        redirects.append({'source': '/:path+', 'has': has, 'destination': dest + '/:path', 'statusCode': 301})
    # 2. old paths -> new paths
    for src, dest in EXTRA_REDIRECTS.items():
        redirects.append({'source': src, 'destination': dest, 'statusCode': 301})
    pm = page_map()
    for f, clean in sorted(pm.items()):
        if clean == '/' or f.startswith('portfolio/'):
            continue
        src = '/' + f
        if src not in EXTRA_REDIRECTS:
            redirects.append({'source': src, 'destination': clean, 'statusCode': 301})
    redirects.append({'source': '/portfolio/:slug([a-z0-9-]+).html', 'destination': '/portfolio/:slug', 'statusCode': 301})
    # 3. shop (separate project) and games (separate projects), proxied under this domain
    rewrites += [
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
    # 4. clean paths -> page files
    for f, clean in sorted(pm.items()):
        if clean == '/' or f.startswith('portfolio/'):
            continue
        rewrites.append({'source': clean, 'destination': '/' + f})
    rewrites.append({'source': '/portfolio/:slug([a-z0-9-]+)', 'destination': '/portfolio/:slug.html'})
    return {
        'cleanUrls': False,
        'trailingSlash': False,
        'headers': [{'source': '/assets/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=604800'}]}],
        'redirects': redirects,
        'rewrites': rewrites,
    }


if __name__ == '__main__':
    import json
    import sys
    if '--write-vercel' in sys.argv:
        with open(os.path.join(SITE, 'vercel.json'), 'w') as fh:
            json.dump(build_vercel(), fh, indent=2)
            fh.write('\n')
        print('wrote site/vercel.json')
    if '--write-sitemap' in sys.argv:
        urls = sorted(set(page_map().values()) | {'/games/%s' % g for g in GAMES} | {'/shop'})
        body = ''.join('  <url><loc>https://buttsstudios.com%s</loc></url>\n' % u for u in urls)
        with open(os.path.join(SITE, 'sitemap.xml'), 'w') as fh:
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '</urlset>\n')
        with open(os.path.join(SITE, 'robots.txt'), 'w') as fh:
            fh.write('User-agent: *\nAllow: /\nSitemap: https://buttsstudios.com/sitemap.xml\n')
        print('wrote sitemap.xml, robots.txt')
