#!/usr/bin/env python3
"""Headless-browser gate for site/: layout shift (CLS < 0.1), keyboard path, form labels, heading order.

Runs against a local static server of site/ (never the live site). Needs the playwright
python package and a Chromium binary (pass --exe to reuse an existing one).

  python3 -m http.server 8765 --directory site &
  python3 scripts/check_browser_a11y.py http://127.0.0.1:8765 [--exe /path/to/headless_shell] [--pages /a.html,/b.html]

Exit 1 on any FAIL. Build/test host only (xps); the laptop is control-only.
"""
import asyncio, sys, json
from playwright.async_api import async_playwright

args = sys.argv[1:]
base = args[0]
exe = args[args.index("--exe") + 1] if "--exe" in args else None
pages = args[args.index("--pages") + 1].split(",") if "--pages" in args else [
    "/index.html", "/releases.html", "/work.html", "/contact.html", "/books.html", "/video.html",
    "/how-we-work.html", "/titles/talon.html", "/titles/the-signal.html", "/titles/the-little-things.html",
    "/titles/us-against-the-world.html"]
CLS_MAX = 0.1

CLS_JS = """new Promise(res => { let cls = 0;
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) cls += e.value; }).observe({type:'layout-shift', buffered:true});
  setTimeout(() => res(+cls.toFixed(4)), 1800); })"""

HEAD_JS = """(() => { const hs = [...document.querySelectorAll('main h1, main h2, main h3, main h4, main h5, main h6')];
  const levels = hs.map(h => +h.tagName[1]); const skips = [];
  for (let i = 1; i < levels.length; i++) if (levels[i] > levels[i-1] + 1) skips.push(hs[i-1].tagName + '>' + hs[i].tagName + ' (' + hs[i].textContent.trim().slice(0,30) + ')');
  return {h1: levels.filter(l => l === 1).length, skips}; })()"""

LABEL_JS = """(() => { const out = [];
  for (const c of document.querySelectorAll('input, select, textarea')) { if (['hidden','submit','button'].includes(c.type)) continue;
    const ok = c.labels && c.labels.length || c.getAttribute('aria-label') || c.getAttribute('aria-labelledby');
    if (!ok) out.push(c.name || c.id || c.tagName); } return out; })()"""

FOCUS_JS = """(() => { const a = document.activeElement; const cs = getComputedStyle(a); const r = a.getBoundingClientRect();
  return {tag: a.tagName, cls: String(a.className).split(' ')[0], visible: r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight,
          ring: (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) >= 1) || (['INPUT','SELECT','TEXTAREA'].includes(a.tagName) && cs.borderColor === cs.color)}; })()"""

async def main():
    fails = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=exe) if exe else await p.chromium.launch()
        for vw in (390, 1280):
            ctx = await b.new_context(viewport={"width": vw, "height": 844 if vw == 390 else 800})
            for path in pages:
                pg = await ctx.new_page()
                await pg.goto(base + path, wait_until="load")
                cls = await pg.evaluate(CLS_JS)
                print(f"{vw:4}px {path:40} CLS {cls}")
                if cls >= CLS_MAX:
                    fails.append(f"{path} @{vw}: CLS {cls} >= {CLS_MAX}")
                if vw == 390:
                    h = await pg.evaluate(HEAD_JS)
                    if h["h1"] != 1:
                        fails.append(f"{path}: h1 count {h['h1']}")
                    for s in h["skips"]:
                        print(f"  WARN {path}: heading level skip {s}")
                    for n in await pg.evaluate(LABEL_JS):
                        fails.append(f"{path}: unlabelled control {n}")
                    # keyboard path: Tab 1 = skip link, visible, with a focus ring; Enter moves focus into main
                    await pg.keyboard.press("Tab")
                    f1 = await pg.evaluate(FOCUS_JS)
                    if not (f1["cls"] == "skip" and f1["visible"] and f1["ring"]):
                        fails.append(f"{path}: first Tab is {f1}")
                    await pg.keyboard.press("Enter")
                    await pg.wait_for_timeout(100)
                    inmain = await pg.evaluate("document.activeElement && (document.activeElement.id === 'main' || !!document.activeElement.closest('main'))")
                    if not inmain:
                        fails.append(f"{path}: skip link did not move focus into main")
                    # every header/nav control reachable with a visible ring
                    for _ in range(4):
                        await pg.keyboard.press("Tab")
                        f = await pg.evaluate(FOCUS_JS)
                        if not f["ring"]:
                            fails.append(f"{path}: no focus ring on {f['tag']}.{f['cls']}")
                await pg.close()
            await ctx.close()
        await b.close()
    for f in fails:
        print("FAIL", f)
    print(f"pages: {len(pages)} x 2 viewports  fails: {len(fails)}")
    sys.exit(1 if fails else 0)

asyncio.run(main())
