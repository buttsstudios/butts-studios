#!/usr/bin/env python3
"""Apply the shared Butts Studios section system to a subdomain source tree (2026-10-16).

Canonical parts: ~/buttsstudios/site/shared/{studios-section.css,bar.tmpl,foot.tmpl}.
Usage: apply_studios_sections.py <target-name> <worktree-dir>
Idempotent: the bar/foot sit between <!--bs:bar--> / <!--bs:foot--> markers and are replaced on re-run;
the retheme only rewrites the old magenta/navy template values, so a second run is a no-op.
Light: plain text edits, no build.
"""
import re, sys, shutil, pathlib

SHARED = pathlib.Path.home() / "buttsstudios/site/shared"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&display=swap" rel="stylesheet">')
SECTIONS = {
    "books": ("Books", "https://buttsstudios.com/books", "#E8B521"),
    "video": ("Video", "https://buttsstudios.com/video", "#E2553A"),
    "games": ("Games", "https://buttsstudios.com/games", "#7BC47F"),
    "partnerships": ("Partnerships", "https://buttsstudios.com/partnerships", "#C9B98F"),
}
NAV_ORDER = ["books", "video", "games"]

# name: (section, product label shown after the crumb or None, kind)
TARGETS = {
    "games-hub": ("games", None, "static"),
    "glb": ("games", "GLB", "static"),
    "cards": ("games", "Card Battle", "next"),
    "puzzle": ("games", "Sliding Numbers", "next"),
    "film": ("video", "Butts Studios Film", "static"),
    "animation": ("video", "Butts Studios Animation", "static"),
    "novels": ("books", "The Signal", "static"),
    "clients": ("partnerships", "Clients", "static"),
}


def nav(section):
    out = []
    for k in NAV_ORDER:
        name, url, _ = SECTIONS[k]
        cur = ' aria-current="true"' if k == section else ""
        out.append(f'<a href="{url}"{cur}>{name}</a>')
    return "".join(out)


def bar(section, here):
    name, url, _ = SECTIONS[section]
    h = f'<span class="bs-sep">/</span><span class="bs-here">{here}</span>' if here else ""
    t = (SHARED / "bar.tmpl").read_text().strip()
    return t.replace("{{SECTION_URL}}", url).replace("{{SECTION_NAME}}", name).replace("{{HERE}}", h).replace("{{NAV}}", nav(section))


def foot(section):
    return (SHARED / "foot.tmpl").read_text().strip().replace("{{NAV}}", nav(section))


# ---------- retheme the old generic template (CSS text only) ----------
MAG = r"#(?:9C27B0|E91E63)"
def _mix(m):
    a = float(m.group(1))
    return f"color-mix(in srgb, var(--bs-accent) {round(a*100)}%, transparent)"

def retheme_css(css):
    # gradient text -> solid bone heading
    def degrad(rule):
        sel, body = rule.group(1), rule.group(2)
        if "text-fill-color: transparent" not in body:
            return rule.group(0)
        body = re.sub(r"\n?[ \t]*(-webkit-)?(background|background-clip|text-fill-color)[^;]*;", "", body)
        ind = re.search(r"\n([ \t]*)\S", body)
        ind = ind.group(1) if ind else " "
        tail = re.search(r"\n([ \t]*)$", body)
        return sel + "{" + body.rstrip() + "\n" + ind + "color: var(--bs-bone);" + ("\n" + tail.group(1) if tail else " ") + "}"
    css = re.sub(r"([^{}]+)\{([^{}]*)\}", degrad, css)
    # magenta gradients (with or without rgba stops) -> accent
    css = re.sub(r"linear-gradient\(\s*\d+deg,\s*rgba\(\s*(?:156|233)[^)]*\)[^,]*,\s*rgba\([^)]*\)[^)]*\)",
                 "color-mix(in srgb, var(--bs-accent) 8%, transparent)", css)
    css = re.sub(r"linear-gradient\([^()]*" + MAG + r"[^()]*\)", "var(--bs-accent)", css, flags=re.I)
    css = re.sub(r"linear-gradient\(\s*\d+deg,\s*var\(--(?:primary|secondary)\)\s*,\s*var\(--(?:primary|secondary)\)\s*\)", "var(--bs-accent)", css)
    css = re.sub(r"linear-gradient\([^()]*#FFD700[^()]*\)", "var(--bs-gold)", css, flags=re.I)
    css = re.sub(r"linear-gradient\(\s*135deg,\s*#2a2a4a,\s*#1a1a3a\s*\)", "var(--bs-ink-3)", css)
    css = re.sub(r"linear-gradient\(\s*135deg,\s*(?:var\(--bg-dark\)|#1a1a2e)\s*0%,\s*(?:var\(--bg-darker\)|#16213e)\s*100%\s*\)", "var(--bs-ink-2)", css, flags=re.I)
    css = re.sub(r"rgba\(\s*(?:156,\s*39,\s*176|233,\s*30,\s*99)\s*,\s*([\d.]+)\s*\)", _mix, css)
    css = re.sub(MAG, "var(--bs-accent)", css, flags=re.I)
    css = re.sub(r"#1a1a2e", "#121110", css, flags=re.I)
    # no one-sided accent borders (Principal rule): full, even, neutral border instead
    css = re.sub(r"border-(?:left|top|right|bottom):\s*\d+px solid var\(--bs-accent\)", "border: 1px solid var(--bs-line)", css)
    # ink type on accent / gold fills (white on the light accents is unreadable)
    def ink_on_fill(rule):
        body = rule.group(2)
        if re.search(r"background:\s*var\(--bs-(accent|gold)\)", body):
            body = re.sub(r"(?<![-\w])color:\s*(#fff(fff)?|white|#1a1a2e|#121110)\s*;", "color: var(--bs-ink);", body, flags=re.I)
        return rule.group(1) + "{" + body + "}"
    css = re.sub(r"([^{}]+)\{([^{}]*)\}", ink_on_fill, css)
    css = re.sub(r"#16213e", "#0C0C0B", css, flags=re.I)
    css = re.sub(r"'Poppins'|\"Poppins\"|'Source Sans Pro'", '"Archivo"', css)
    css = re.sub(r"'Playfair Display'", '"Newsreader"', css)
    # radius <= 4px (keep 50% circles and 0)
    def rad(m):
        v = m.group(1).strip()
        if v.endswith("%") or v in ("0", "0px"):
            return m.group(0)
        n = re.match(r"([\d.]+)(px|rem|em)", v)
        if n and (float(n.group(1)) * (16 if n.group(2) != "px" else 1)) <= 4:
            return m.group(0)
        return "border-radius: 2px"
    css = re.sub(r"border-radius:\s*([^;}\n]+)", rad, css)
    # pills/lifts: no scale-up hovers on buttons (calm, measured)
    css = css.replace("transform: scale(1.05)", "filter: brightness(1.08)").replace("transform: scale(1.1)", "filter: brightness(1.08)")
    return css


def retheme_html(s, accent_hex):
    s = re.sub(r"(<style[^>]*>)(.*?)(</style>)", lambda m: m.group(1) + retheme_css(m.group(2)) + m.group(3), s, flags=re.S)
    # inline style attributes
    s = re.sub(r'style="([^"]*)"', lambda m: 'style="' + retheme_css(m.group(1)) + '"', s)
    # canvas / script colors: literal accent hex (var() does not work in canvas)
    s = re.sub(r"(['\"])#E91E63\1", lambda m: m.group(1) + accent_hex + m.group(1), s, flags=re.I)
    s = re.sub(r"(['\"])#9C27B0\1", lambda m: m.group(1) + accent_hex + m.group(1), s, flags=re.I)
    s = re.sub(r"%23(?:9C27B0|E91E63)", "%23" + accent_hex.lstrip("#"), s, flags=re.I)
    s = re.sub(r'(<meta name="theme-color" content=")[^"]*"', r'\1#050707"', s)
    s = re.sub(r"<link[^>]*fonts\.googleapis\.com/css2?\?family=[^>]*>\s*", "", s)
    return s


def inject(s, section, here):
    s = re.sub(r"<!--bs:(bar|foot|head)-->.*?<!--/bs:\1-->\s*", "", s, flags=re.S)
    head = f'<!--bs:head-->{FONTS}<link rel="stylesheet" href="studios-section.css"><!--/bs:head-->'
    s = s.replace("</head>", head + "\n</head>", 1)
    s = re.sub(r"<html([^>]*?)(\s+data-bs-section=\"[^\"]*\")?>", lambda m: f'<html{m.group(1)} data-bs-section="{section}">', s, count=1)
    s = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + bar(section, here), s, count=1)
    # replace the old one-line "A Butts Studios Production" footer if present
    s = re.sub(r"<footer>\s*<p>(?:A|Part of) <a href=\"https://buttsstudios\.com\">Butts Studios</a>(?: Production)?</p>\s*</footer>", "", s)
    s = s.replace("</body>", foot(section) + "\n</body>", 1)
    return s


# ---------- per-target adjustments ----------
def tweak(name, s):
    if name in ("film", "animation", "novels"):
        # product nav sits under the Studios bar instead of fixed over it; the bar carries the Studios link
        s = re.sub(r"(\n\s*nav \{[^}]*?)position: fixed;", r"\1position: sticky;", s, count=1)
        s = re.sub(r'\s*<a href="https://buttsstudios\.com">Studios</a>', "", s)
    if name == "glb":
        s = s.replace("display: flex;\n            justify-content: center;\n            align-items: center;\n            min-height: 100vh;",
                      "display: flex;\n            flex-direction: column;\n            min-height: 100vh;\n            background: var(--bs-ink-2);", 1)
        s = s.replace("#game-container {\n            position: relative;", "#game-container {\n            position: relative;\n            margin: 32px auto 64px;\n            max-width: 100%;", 1)
    if name == "games-hub":
        for old, new in (("https://glb-game.vercel.app", "https://glb.buttsstudios.com"),
                         ("https://butts-cards.vercel.app", "https://cards.buttsstudios.com"),
                         ("https://butts-puzzle.vercel.app", "https://puzzle.buttsstudios.com"),
                         (">Butts Cards<", ">Card Battle<"), (">Butts Puzzle<", ">Sliding Numbers<"),
                         ("<h1>Butts Games</h1>", "<h1>Games<span class=\"accent\">.</span></h1>"),
                         ("An immersive canvas-based adventure game with stunning visuals and engaging gameplay.",
                          "A canvas game for the browser: move with the arrow keys or WASD, collect what's on the board and avoid the obstacles."),
                         ("A strategic card game with unique mechanics and competitive multiplayer modes.", "A strategy card game, played in the browser."),
                         ("Mind-bending puzzles that challenge your logic and problem-solving skills.",
                          "The classic sliding-tile puzzle, set cleanly: put the numbers back in order in as few moves as you can."),
                         ("&#127918;", "&#9698;"), ("&#127183;", "&#9635;"), ("&#129513;", "&#8862;")):
            s = s.replace(old, new)
        s = s.replace("<p class=\"tagline\">Web games that push boundaries</p>",
                      "<p class=\"tagline\">Small games made with the same care as everything else here: clear rules, clean screens, and nothing in the way of playing.</p>")
        s = s.replace(".game-thumbnail {\n            height: 200px;\n            background: var(--bs-accent);",
                      ".game-thumbnail {\n            height: 200px;\n            background: var(--bs-ink-3);\n            color: var(--bs-accent);")
        s = s.replace("header {\n            text-align: center;", "header {\n            text-align: left;")
        s = s.replace(".game-card {\n            background: rgba(255,255,255,0.05);",
                      ".game-card {\n            background: rgba(255,255,255,0.03);\n            border: 1px solid var(--bs-line);")
        s = s.replace("transform: translateY(-8px);\n            box-shadow: 0 20px 40px color-mix(in srgb, var(--bs-accent) 30%, transparent);",
                      "border-color: var(--bs-accent);")
        s = s.replace("color: #1a1a2e;", "color: var(--bs-ink);").replace("color: #121110;", "color: var(--bs-ink);")
    if name == "clients":
        s = s.replace("background: #f5f5f5;", "background: var(--bs-ink-2);", 1)
        s = s.replace(".login-left {\n            flex: 1;\n            background: var(--bs-accent);", ".login-left {\n            flex: 1;\n            background: var(--bs-ink-3);", 1)
        s = s.replace("padding: 3rem;\n            color: var(--bs-ink);\n        }", "padding: 3rem;\n            color: var(--bs-bone);\n        }", 1)
        s = s.replace("padding: 3rem;\n            background: #fff;", "padding: 3rem;\n            background: var(--bs-bone);", 1)
    return s


def apply_static(name, root):
    section, here, _ = TARGETS[name]
    p = root / "index.html"
    s = p.read_text()
    # pages redesigned natively in the Studios system (film, animation, clients: 2026-10-16) carry <!--bs:native-->;
    # they only get the bar/foot/head re-injected, never the old-template retheme or tweaks
    if "<!--bs:native-->" not in s:
        s = retheme_html(s, SECTIONS[section][2])
        s = tweak(name, s)
    s = inject(s, section, here)
    p.write_text(s)
    shutil.copy(SHARED / "studios-section.css", root / "studios-section.css")


def apply_next(name, root):
    section, here, _ = TARGETS[name]
    g = root / "app/globals.css"
    css = retheme_css(g.read_text())
    css = css.replace("--primary: #9C27B0;", "--primary: var(--bs-accent);").replace("--secondary: #E91E63;", "--secondary: var(--bs-accent);")
    css = css.replace("--primary: var(--bs-accent);\n  --secondary: var(--bs-accent);\n  --bg-dark: #121110;\n  --bg-darker: #0C0C0B;",
                      "--primary: var(--bs-accent);\n  --secondary: var(--bs-accent);\n  --bg-dark: #121110;\n  --bg-darker: #0C0C0B;")
    css = css.replace("color: #1a1a2e;", "color: var(--bs-ink);").replace("color: #121110;", "color: var(--bs-ink);")
    g.write_text(css)
    shutil.copy(SHARED / "studios-section.css", root / "app/studios-section.css")
    lay = root / "app/layout.tsx"
    t = lay.read_text()
    if "studios-section.css" not in t:
        t = t.replace('import "./globals.css";', 'import "./studios-section.css";\nimport "./globals.css";', 1)
    t = re.sub(r'themeColor: "#[0-9A-Fa-f]+"', 'themeColor: "#050707"', t)
    jsx_bar = html_to_jsx(bar(section, here))
    jsx_foot = html_to_jsx(foot(section))
    fonts = ('<head>\n        <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
             '        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />\n'
             '        <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400&display=swap" rel="stylesheet" />\n      </head>')
    new_html = (f'<html lang="en" data-bs-section="{section}">\n      {fonts}\n      <body>\n        {{/* bs:bar */}}\n        {jsx_bar}\n'
                f'        {{children}}\n        {{/* bs:foot */}}\n        {jsx_foot}\n      </body>\n    </html>')
    t = re.sub(r'<html lang="en"[^>]*>.*?</html>', lambda m: new_html, t, count=1, flags=re.S)
    lay.write_text(t)
    # paid-only copy: the daily-limit message must not call the games "free"
    pg = root / "app/page.tsx"
    s = pg.read_text().replace("Daily limit reached! Come back tomorrow for more free games.",
                               "Daily limit reached. Come back tomorrow, or unlock the full game.")
    s = s.replace("'#E91E63' : '#fff'", "'#E2553A' : '#fff'")
    pg.write_text(s)


def html_to_jsx(h):
    h = re.sub(r"<!--/?bs:\w+-->", "", h)
    h = h.replace('class="', 'className="').replace('stroke-width="', 'strokeWidth="').replace('aria-hidden="true"', 'aria-hidden="true"')
    h = re.sub(r"<(path|rect)([^>]*?)(?<!/)>", r"<\1\2 />", h)
    h = h.replace("<i className=\"bs-dot\"></i>", "<i className=\"bs-dot\" />")
    return h


if __name__ == "__main__":
    name, root = sys.argv[1], pathlib.Path(sys.argv[2])
    (apply_next if TARGETS[name][2] == "next" else apply_static)(name, root)
    print("applied", name, "->", root)
