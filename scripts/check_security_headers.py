#!/usr/bin/env python3
"""Gate: site/vercel.json must set the baseline security headers on every path and a CSP on first-party pages.
Exit 1 on any gap. Run: python3 scripts/check_security_headers.py"""
import json, os, sys
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "vercel.json")
d = json.load(open(p))
need = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": None, "Referrer-Policy": None, "Permissions-Policy": None, "Strict-Transport-Security": None}
got = {}
csp_sources = []
for blk in d.get("headers", []):
    for h in blk.get("headers", []):
        if blk["source"] == "/(.*)":
            got[h["key"]] = h["value"]
        if h["key"] == "Content-Security-Policy":
            csp_sources.append(blk["source"])
            v = h["value"]
            for must in ["frame-ancestors", "base-uri", "object-src 'none'", "form-action"]:
                if must not in v:
                    print("FAIL csp missing", must); sys.exit(1)
            if "'unsafe-inline'" in v.split("script-src", 1)[-1].split(";")[0]:
                print("FAIL csp allows unsafe-inline scripts"); sys.exit(1)
fails = [k for k, v in need.items() if k not in got or (v and got[k] != v)]
if fails or not csp_sources:
    print("FAIL missing on /(.*):", fails, "csp_sources:", csp_sources); sys.exit(1)
print("PASS security headers:", sorted(got), "csp on", csp_sources)
