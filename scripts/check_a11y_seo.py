#!/usr/bin/env python3
"""Static accessibility / SEO gate for site/ (buttsstudios.com).

Checks every page in the sitemap (restored client archives under site/work/*/ are
reported but not gated): lang, one h1, <main id="main">, skip link, title +
description + canonical uniqueness, og:image/og:url, twitter card, img alt and
width/height for local raster images, reduced-motion CSS, sitemap coverage.

Usage: python3 scripts/check_a11y_seo.py [site_dir]   (exit 1 on any failure)
"""
import re, sys, pathlib
from collections import Counter

SITE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1] / "site")
fails, warns = [], []

def attr(tag, name):
    m = re.search(name + r'="([^"]*)"', tag)
    return m.group(1) if m else None

sitemap = (SITE / "sitemap.xml").read_text()
locs = re.findall(r"<loc>https://buttsstudios\.com(/[^<]*)</loc>", sitemap)
pages = []
for loc in locs:
    rel = loc.strip("/")
    cand = [SITE / (rel + ".html"), SITE / rel / "index.html", SITE / "index.html" if rel == "" else None]
    f = next((c for c in cand if c and c.exists()), None)
    if f is None:
        if rel == "shop" or rel.startswith("games/"):
            continue  # served by the storefront / games projects
        fails.append(f"sitemap {loc}: no file")
        continue
    pages.append((loc, f))

titles, descs, canons = Counter(), Counter(), Counter()
for loc, f in pages:
    s = f.read_text()
    archive = f.parent != SITE and f.name == "index.html" and "work/" in f.as_posix()
    out = warns if archive else fails
    if not re.search(r'<html[^>]*\blang="', s):
        out.append(f"{loc}: missing lang")
    n_h1 = len(re.findall(r"<h1\b", s))
    if n_h1 != 1:
        out.append(f"{loc}: h1 count {n_h1}")
    if not re.search(r'<main[^>]*\bid="main"', s):
        out.append(f"{loc}: no <main id=main>")
    if 'class="skip"' not in s:
        out.append(f"{loc}: no skip link")
    for name, rx, c in (("title", r"<title>([^<]*)</title>", titles),
                        ("description", r'name="description" content="([^"]*)"', descs),
                        ("canonical", r'rel="canonical" href="([^"]*)"', canons)):
        m = re.search(rx, s)
        if not m or not m.group(1).strip():
            out.append(f"{loc}: missing {name}")
        else:
            c[m.group(1)] += 1
    for tag in ("og:image", "og:url", "twitter:card"):
        if tag not in s:
            out.append(f"{loc}: missing {tag}")
    for tag in re.findall(r"<img[^>]*>", s):
        src = attr(tag, "src") or ""
        if attr(tag, "alt") is None:
            out.append(f"{loc}: img without alt ({src})")
        if not src.endswith(".svg") and (src.startswith("/") or not src.startswith("http")):
            if attr(tag, "width") is None or attr(tag, "height") is None:
                out.append(f"{loc}: img without width/height ({src})")
    for tag in re.findall(r"<(?:input|select|textarea)[^>]*>", s):
        t = attr(tag, "type")
        if t in ("hidden", "submit", "button"):
            continue
        i = attr(tag, "id")
        wrapped = re.search(r"<label\b[^>]*>(?:(?!</label>).)*?" + re.escape(tag), s, re.S)
        if not wrapped and not (i and re.search(r'<label[^>]*for="%s"' % re.escape(i), s)) and not attr(tag, "aria-label"):
            out.append(f"{loc}: form control without label ({tag[:60]})")

for name, c in (("title", titles), ("description", descs), ("canonical", canons)):
    for v, n in c.items():
        if n > 1:
            fails.append(f"duplicate {name} x{n}: {v[:70]}")

css = (SITE / "styles.css").read_text()
if "prefers-reduced-motion" not in css:
    fails.append("styles.css: no prefers-reduced-motion block")
if ".skip" not in css:
    fails.append("styles.css: no .skip rule")
if ":focus-visible" not in css:
    fails.append("styles.css: no :focus-visible rule")

for w in warns:
    print("WARN", w)
for f in fails:
    print("FAIL", f)
print(f"pages checked: {len(pages)}  fails: {len(fails)}  warns (archives): {len(warns)}")
sys.exit(1 if fails else 0)
