#!/usr/bin/env python3
"""Static checks for ~/buttsstudios/site: broken internal links/anchors, img alt, head meta, nav/footer.

  python3 ~/buttsstudios/scripts/check_site_links.py          # exit 1 on any problem
  python3 ~/buttsstudios/scripts/check_site_links.py --links  # links + anchors only

Skips the vendored wham-studios bundle and archived/_check pages. Stdlib only.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import url_map  # noqa: E402
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site')
SITE = os.path.normpath(SITE)
SKIP_DIRS = ('work/wham-studios/vendor',)
META_REQ = ['description', 'viewport', 'og:title', 'og:description', 'og:image', 'og:type', 'twitter:card']


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.imgs, self.meta = [], set(), [], {}
        self.title = False
        self.head_nav = self.full_foot = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'a' and 'name' in a:
            self.ids.add(a['name'])
        for k in ('href', 'src', 'poster'):
            if a.get(k):
                self.refs.append((tag, a[k]))
        if a.get('srcset'):
            for part in a['srcset'].split(','):
                if part.strip():
                    self.refs.append((tag, part.strip().split()[0]))
        if tag == 'img':
            self.imgs.append(a)
        if tag == 'meta':
            key = a.get('name') or a.get('property')
            if key:
                self.meta[key] = a.get('content', '')
        if tag == 'title':
            self.title = True
        if tag == 'header' and 'site-head' in (a.get('class') or ''):
            self.head_nav = True
        if tag == 'footer' and 'full-foot' in (a.get('class') or ''):
            self.full_foot = True


def pages():
    for root, _, files in os.walk(SITE):
        rel = os.path.relpath(root, SITE)
        if any(rel.startswith(s) for s in SKIP_DIRS):
            continue
        for f in files:
            if f.endswith('.html') and not f.startswith('_'):
                yield os.path.join(root, f)


def main():
    links_only = '--links' in sys.argv
    parsed = {}
    for p in pages():
        pg = Page()
        pg.feed(open(p, encoding='utf-8').read())
        parsed[p] = pg
    problems = []
    for p, pg in sorted(parsed.items()):
        rel = os.path.relpath(p, SITE)
        for tag, ref in pg.refs:
            u = urlsplit(ref)
            if u.scheme or ref.startswith('//') or ref.startswith('data:'):
                continue
            path = unquote(u.path)
            ct = url_map.clean_target(path) if path.startswith('/') else None
            if ct:
                if ct[0] == 'file' and u.fragment and tag == 'a':
                    tp = parsed.get(os.path.join(SITE, ct[1]))
                    if tp and u.fragment not in tp.ids:
                        problems.append(f'{rel}: missing anchor {ref}')
                continue
            if path.endswith('.html') and path in ('/' + f for f in url_map.page_map()):
                problems.append(f'{rel}: link uses the legacy .html path {ref}')
                continue
            if path:
                target = os.path.normpath(os.path.join(SITE, path.lstrip('/')) if path.startswith('/')
                                          else os.path.join(os.path.dirname(p), path))
                if os.path.isdir(target):
                    target = os.path.join(target, 'index.html')
            else:
                target = p
            if not os.path.exists(target):
                problems.append(f'{rel}: missing {ref}')
                continue
            if u.fragment and target.endswith('.html') and tag == 'a':
                tp = parsed.get(target)
                if tp and u.fragment not in tp.ids:
                    problems.append(f'{rel}: missing anchor {ref}')
        if links_only or rel.startswith('work/'):
            continue  # client work pages are archived originals; links only
        for img in pg.imgs:
            if 'alt' not in img:
                problems.append(f'{rel}: img without alt: {img.get("src")}')
        if not pg.title:
            problems.append(f'{rel}: no <title>')
        for k in META_REQ:
            if not pg.meta.get(k):
                problems.append(f'{rel}: no meta {k}')
        if not pg.head_nav:
            problems.append(f'{rel}: no site header nav')
        if not pg.full_foot:
            problems.append(f'{rel}: no full footer')
    for line in problems:
        print(line)
    print(f'{len(parsed)} pages checked, {len(problems)} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
