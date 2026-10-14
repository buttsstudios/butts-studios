#!/usr/bin/env python3
"""Butts Studios device mockups, drawn from scratch (no third-party templates, no licensing risk).

A laptop (16:10 screen) and a phone (390x844 screen), ink frames with a thin light rim so they read on
bone and on near-black, soft even shadows, transparent background. Screens are our own captures.

Output: site/assets/<dir>/mockup-<name>.webp (full, 2400 px wide) + mockup-<name>-720.webp.
Run: python3 scripts/make_mockups.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')
P = 'assets/portfolio/'
V = 'assets/video/'
W = 'assets/work/'

INK = (22, 22, 24, 255)
RIM = (74, 74, 80, 255)
BASE_TOP = (206, 203, 196, 255)
BASE_BOT = (168, 165, 158, 255)

# name -> (out dir, desktop screen or None, phone screen or None)
JOBS = {
    # identity cases
    'huntington-applied': (P, P + 'screen-huntington-applied.webp', P + 'mobile-huntington-applied.webp'),
    'runwae-apparel': (P, None, P + 'runwae-apparel-mobile.webp'),
    'dailyaitoll': (P, P + 'screen-dailyaitoll.webp', P + 'mobile-dailyaitoll.webp'),
    'latarence': (P, P + 'screen-latarence-light.webp', P + 'mobile-latarence.webp'),
    'ridgefield': (P, P + 'screen-ridgefield.webp', P + 'mobile-ridgefield.webp'),
    'signals-institute': (P, P + 'screen-signals-institute.webp', P + 'mobile-signals-institute.webp'),
    # featured products
    'boltzmann': (P, P + 'screen-boltzmann.webp', P + 'mobile-boltzmann.webp'),
    'chief': (P, P + 'screen-chief.webp', P + 'mobile-chief.webp'),
    'landslide': (P, P + 'screen-landslide.webp', P + 'mobile-landslide.webp'),
    'tillio': (P, P + 'screen-tillio.webp', P + 'mobile-tillio.webp'),
    'document-scanner': (P, P + 'screen-document-scanner.webp', P + 'mobile-document-scanner.webp'),
    'runwae': (P, P + 'screen-runwae.webp', P + 'mobile-runwae.webp'),
    # partnerships (2021 captures from the original studio site)
    'latarence-2021': (W, P + 'latarence-2021-desktop.webp', P + 'latarence-2021-mobile.webp'),
    'wham': (W, W + 'wham-landing.webp', V + 'whammobilerender-poster.jpg'),
    'pablo': (W, W + 'pablo-landing.webp', None),
}


def rrect(size, box, r, fill):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255)
    layer = Image.new('RGBA', size, fill)
    layer.putalpha(m)
    return layer, m


def cover(src, w, h, anchor_top=True):
    im = Image.open(os.path.join(SITE, src)).convert('RGBA')
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x = (im.width - w) // 2
    y = 0 if anchor_top else (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def shadow(canvas, mask, dy, blur, alpha):
    sh = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    a = mask.point(lambda v: v * alpha // 255)
    sh.putalpha(a)
    sh = sh.transform(sh.size, Image.AFFINE, (1, 0, 0, 0, 1, -dy)).filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh)


def laptop(canvas, x, y, sw, src):
    """Lid with screen sw x sw*10/16 at (x, y) = lid top-left; base slab below."""
    sh_ = round(sw * 10 / 16)
    b = round(sw * .022)  # bezel
    lw, lh = sw + 2 * b, sh_ + b + round(b * 1.5)
    r = round(sw * .022)
    full = canvas.size
    lid_box = (x, y, x + lw, y + lh)
    base_h = round(sw * .03)
    over = round(sw * .07)
    base_box = (x - over, y + lh, x + lw + over, y + lh + base_h)
    # shadow from the whole device
    m = Image.new('L', full, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle(lid_box, r, fill=255)
    d.rounded_rectangle(base_box, base_h // 2, fill=255)
    shadow(canvas, m, round(sw * .02), round(sw * .03), 70)
    rim, _ = rrect(full, lid_box, r, RIM)
    canvas.alpha_composite(rim)
    lid, _ = rrect(full, (x + 3, y + 3, x + lw - 3, y + lh - 3), r - 3, INK)
    canvas.alpha_composite(lid)
    scr = cover(src, sw, sh_)
    sm = Image.new('L', (sw, sh_), 0)
    ImageDraw.Draw(sm).rounded_rectangle((0, 0, sw - 1, sh_ - 1), max(2, r // 3), fill=255)
    canvas.paste(scr, (x + b, y + round(b * 1.5)), sm)
    # camera dot
    ImageDraw.Draw(canvas).ellipse((x + lw // 2 - 5, y + round(b * .75) - 5, x + lw // 2 + 5, y + round(b * .75) + 5), fill=(40, 40, 44, 255))
    # base: two-tone slab with a centered lip notch
    base = Image.new('RGBA', full, (0, 0, 0, 0))
    bd = ImageDraw.Draw(base)
    bd.rounded_rectangle(base_box, base_h // 2, fill=BASE_BOT)
    bd.rounded_rectangle((base_box[0], base_box[1], base_box[2], base_box[1] + base_h * .55), base_h // 3, fill=BASE_TOP)
    nw = round(sw * .16)
    cx = x + lw // 2
    bd.rounded_rectangle((cx - nw // 2, base_box[1], cx + nw // 2, base_box[1] + base_h * .32), base_h // 4, fill=BASE_BOT)
    canvas.alpha_composite(base)
    return base_box[3]


def phone(canvas, x, y, sw, src):
    """Phone with screen sw x sw*844/390 at frame top-left (x, y)."""
    sh_ = round(sw * 844 / 390)
    b = round(sw * .045)
    fw, fh = sw + 2 * b, sh_ + 2 * b
    r = round(fw * .15)
    full = canvas.size
    box = (x, y, x + fw, y + fh)
    m = Image.new('L', full, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255)
    shadow(canvas, m, round(sw * .05), round(sw * .07), 90)
    rim, _ = rrect(full, box, r, RIM)
    canvas.alpha_composite(rim)
    body, _ = rrect(full, (x + 3, y + 3, x + fw - 3, y + fh - 3), r - 3, INK)
    canvas.alpha_composite(body)
    # status strip (ink) holds the island; the capture fills the screen below it
    top = round(sw * .11)
    scr = Image.new('RGBA', (sw, sh_), INK)
    scr.paste(cover(src, sw, sh_ - top), (0, top))
    sm = Image.new('L', (sw, sh_), 0)
    ImageDraw.Draw(sm).rounded_rectangle((0, 0, sw - 1, sh_ - 1), r - b, fill=255)
    canvas.paste(scr, (x + b, y + b), sm)
    # island
    iw, ih = round(sw * .26), round(sw * .07)
    cx = x + fw // 2
    ImageDraw.Draw(canvas).rounded_rectangle((cx - iw // 2, y + b + round(sw * .02), cx + iw // 2, y + b + round(sw * .02) + ih), ih // 2, fill=(0, 0, 0, 255))


def compose(desk, ph):
    if desk and ph:
        cw, chh = 2400, 1640
        c = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
        laptop(c, 170, 90, 1760, desk)
        phone(c, 1760, 480, 440, ph)
    elif desk:
        cw, chh = 2400, 1420
        c = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
        laptop(c, 260, 80, 1800, desk)
    else:
        cw, chh = 1400, 1600
        c = Image.new('RGBA', (cw, chh), (0, 0, 0, 0))
        phone(c, 460, 70, 560, ph)
    return c


def main():
    for name, (out, desk, ph) in JOBS.items():
        c = compose(desk, ph)
        bbox = c.getbbox()
        pad = 40
        c = c.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(c.width, bbox[2] + pad), min(c.height, bbox[3] + pad)))
        base = os.path.join(SITE, out, f'mockup-{name}')
        c.save(base + '.webp', 'WEBP', quality=86, method=4)
        t = c.resize((720, round(c.height * 720 / c.width)), Image.LANCZOS)
        t.save(base + '-720.webp', 'WEBP', quality=84, method=4)
        print(f'{out}mockup-{name}.webp {c.width}x{c.height}')


if __name__ == '__main__':
    main()
