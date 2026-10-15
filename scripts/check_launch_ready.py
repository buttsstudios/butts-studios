#!/usr/bin/env python3
"""Launch guard for ~/buttsstudios/site: exits 1 while any fill-in or draft marker remains.

Markers: "[CONFIRM" fill-ins (entity, mailing address, governing-law state, refund windows, dates) and the
"Draft · not yet in effect" badge on the legal pages. These wait on Principal decisions
(~/jarvis/JARVIS QUESTIONS.md); fill them in, delete the badge, then this passes.

  python3 ~/buttsstudios/scripts/check_launch_ready.py [site_dir]
"""
import os
import re
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site'))
MARKERS = re.compile(r'\[CONFIRM\b[^\]]*\]?|Draft\s*(?:·|&middot;|&#183;)\s*not yet in effect|\[FILL\b[^\]]*\]?', re.I)

hits = []
for root, _, files in os.walk(SITE):
    if '/vendor' in root:
        continue
    for f in files:
        if not f.endswith(('.html', '.txt', '.xml', '.json')) or f.startswith('_'):
            continue
        p = os.path.join(root, f)
        for n, line in enumerate(open(p, encoding='utf-8', errors='replace'), 1):
            for m in MARKERS.finditer(line):
                hits.append(f'{os.path.relpath(p, SITE)}:{n}: {m.group(0)[:90]}')

for h in hits:
    print(h)
if hits:
    print(f'NOT LAUNCH-READY: {len(hits)} placeholder(s) remain (Principal decisions pending)')
    sys.exit(1)
print('launch-ready: no placeholders')
