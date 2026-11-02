#!/usr/bin/env python3
"""Gate: site/vercel.json must set the baseline security headers on every path and a hashed CSP on the first-party
pages, and the CSP's script-src hashes must be exactly the sha256 of the inline <script> blocks on those pages
(computed here from the pages, via url_map.inline_script_hashes, never hard-coded). Exit 1 on any gap.
  python3 scripts/check_security_headers.py"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import url_map  # noqa: E402

p = os.path.join(HERE, "..", "site", "vercel.json")
d = json.load(open(p))
need = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": None, "Referrer-Policy": None, "Permissions-Policy": None, "Strict-Transport-Security": None}
got, csp_sources, csp = {}, [], None
for blk in d.get("headers", []):
    for h in blk.get("headers", []):
        if blk["source"] == "/(.*)":
            got[h["key"]] = h["value"]
        if h["key"] == "Content-Security-Policy":
            csp_sources.append(blk["source"]); csp = h["value"]
fails = [k for k, v in need.items() if k not in got or (v and got[k] != v)]
if fails or not csp_sources:
    print("FAIL missing on /(.*):", fails, "csp_sources:", csp_sources); sys.exit(1)
for must in ["frame-ancestors", "base-uri", "object-src 'none'", "form-action"]:
    if must not in csp:
        print("FAIL csp missing", must); sys.exit(1)
script_src = next((x.strip() for x in csp.split(";") if x.strip().startswith("script-src")), "")
if "'unsafe-inline'" in script_src or "'unsafe-eval'" in script_src:
    print("FAIL csp allows unsafe-inline/unsafe-eval scripts"); sys.exit(1)
in_csp = set(re.findall(r"'sha256-[A-Za-z0-9+/=]+'", script_src))
on_pages = set(url_map.inline_script_hashes())
if in_csp != on_pages:
    print("FAIL csp script hashes differ from the pages' inline scripts: run python3 scripts/url_map.py --write-vercel")
    print("  only in csp:", sorted(in_csp - on_pages)); print("  only on pages:", sorted(on_pages - in_csp)); sys.exit(1)
print("PASS security headers:", sorted(got), "csp on", csp_sources, "inline script hashes:", len(on_pages))
