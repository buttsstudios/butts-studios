#!/usr/bin/env python3
"""Regression check: nothing deployable names a removed Butts Studios subdomain (SS1102-SUBDOMAIN-LEFTOVERS, 2026-11-02).

Butts Studios has no subdomains (Principal 2026-10-28, 2026-11-02). The ten hosts in url_map.RETIRED_HOSTS were removed
from DNS and Vercel, not forwarded, so any mention is a dead link or a false claim, whether it is an href, a canonical,
an og:url, a sitemap <loc>, a Stripe return URL in code, legal copy or a code comment. Dead partner / typo domains
(url_map.DEAD_DOMAINS) are checked the same way.

Usage: check_removed_hosts.py [DIR ...]      (default: site/ games/ nginx/ of this repo)
       check_removed_hosts.py --live URL ...  (fetch pages and scan the served HTML, stdlib only)
Exit 1 on any hit. Scans text files only (html, htm, xml, txt, json, js, mjs, ts, tsx, css, md, conf, sh, py).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import url_map as U  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIRS = [os.path.join(ROOT, d) for d in ('site', 'games', 'nginx')]
EXTS = ('.html', '.htm', '.xml', '.txt', '.json', '.js', '.mjs', '.ts', '.tsx', '.css', '.md', '.conf', '.sh', '.py')
SKIP_DIRS = ('.git', 'node_modules', '.next', '__pycache__', 'archive')
HOSTS = list(U.RETIRED_HOSTS) + list(getattr(U, 'PENDING_REMOVAL_HOSTS', [])) + list(getattr(U, 'DEAD_DOMAINS', []))
PAT = re.compile(r'\b(' + '|'.join(re.escape(h) for h in HOSTS) + r')\b', re.I)
PATHS = getattr(U, 'RETIRED_HOST_PATHS', {})


def scan_text(label, text, problems):
    for i, line in enumerate(text.splitlines(), 1):
        for m in PAT.finditer(line):
            host = m.group(1).lower()
            hint = PATHS.get(host, '')
            problems.append('%s:%d: names removed host %s%s' % (label, i, host, (' (use %s)' % hint) if hint else ''))


def scan_dir(d, problems):
    for root, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if not f.endswith(EXTS):
                continue
            p = os.path.join(root, f)
            try:
                text = open(p, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            scan_text(os.path.relpath(p, ROOT), text, problems)


def scan_live(urls, problems):
    import urllib.request
    for u in urls:
        try:
            body = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'check_removed_hosts'}), timeout=20).read()
        except Exception as e:  # noqa: BLE001
            problems.append('%s: fetch failed (%s)' % (u, str(e)[:80]))
            continue
        scan_text(u, body.decode('utf-8', 'replace'), problems)


def main(argv):
    problems = []
    if argv and argv[0] == '--live':
        scan_live(argv[1:], problems)
    else:
        for d in (argv or DEFAULT_DIRS):
            if os.path.isdir(d):
                scan_dir(d, problems)
            elif os.path.isfile(d):
                scan_text(os.path.relpath(d, ROOT), open(d, encoding='utf-8', errors='replace').read(), problems)
            else:
                problems.append('%s: no such path' % d)
    for p in problems:
        print('FAIL', p)
    print('removed-host check: %d hit(s) across %d host pattern(s)' % (len(problems), len(HOSTS)))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
