#!/usr/bin/env python3
"""Rewrite every internal link in site/**/*.html to the canonical clean path from url_map.py (idempotent).

Run after any generator (build_work_page.py, build_portfolio_pages.py, apply_studios_sections.py):
  python3 scripts/normalize_urls.py
Archived client pages under site/work/ only get their links to mapped pages rewritten; their own assets are untouched.
"""
import os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import url_map as U
SITE = U.SITE
PM = U.page_map()
CLEAN = {v: k for k, v in PM.items()}
ATTR = re.compile(r'\b(href|src|poster)="([^"]*)"')
CANON = re.compile(r'(content|href)="https://buttsstudios\.com/([^"#?]*)"')
changed = 0
for p in glob.glob(SITE + '/**/*.html', recursive=True):
    rel = os.path.relpath(p, SITE)
    inwork = rel.startswith('work/')
    if rel.startswith('work/wham-studios/vendor'): continue
    s = open(p, encoding='utf-8').read(); o = s
    # the moved channels page: it lived in titles/
    base_rel = 'titles/the-channels.html' if rel == 'channels.html' else rel
    basedir = os.path.dirname(base_rel)
    def fix_attr(m):
        attr, val = m.group(1), m.group(2)
        if re.match(r'^(?:[a-z][a-z0-9+.-]*:|//|#|\?)', val, re.I) or val == '': return m.group(0)
        path, frag = (val.split('#', 1) + [''])[:2] if '#' in val else (val, '')
        if '?' in path: return m.group(0)
        tgt = os.path.normpath(os.path.join(basedir, path)) if not path.startswith('/') else path.lstrip('/')
        tgt = tgt.replace('titles/the-channels.html', 'channels.html')
        clean = PM.get(tgt)
        if clean is None and tgt in ('', '.'): clean = '/'
        if clean is not None:
            out = clean + ('#' + frag if frag else '')
        elif inwork and rel != 'channels.html':
            return m.group(0)
        else:
            out = '/' + tgt + ('#' + frag if frag else '')
        return '%s="%s"' % (attr, out)
    s = ATTR.sub(fix_attr, s)
    def fix_abs(m):
        attr, path = m.group(1), m.group(2)
        if path == '' : return m.group(0)
        path = path.replace('titles/the-channels.html', 'channels.html')
        if path in PM: return '%s="https://buttsstudios.com%s"' % (attr, PM[path]) if PM[path] != '/' else '%s="https://buttsstudios.com/"' % attr
        return m.group(0)
    s = CANON.sub(fix_abs, s)
    # absolute store link -> the shop path
    s = s.replace('https://store.buttsstudios.com', '/shop')
    if s != o:
        open(p, 'w', encoding='utf-8').write(s); changed += 1
print('changed', changed)
