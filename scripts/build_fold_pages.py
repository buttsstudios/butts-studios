#!/usr/bin/env python3
"""Fold-in pages for the retiring Studios subdomains (STUDIOS-COHESION-1, 2026-10-28).

novels. (The Signal)  -> site/titles/the-signal.html   (/titles/the-signal, linked from /books)
film.                 -> site/video/film.html          (/video/film, linked from /video)
animation.            -> site/video/animation.html     (/video/animation, linked from /video)
clients.              -> site/contact.html             (/contact: start a project + already working with us)

Content comes from each subdomain repo's restyled branch (style/studios-sections-2026-10-16), the version the Principal
approved on 2026-10-16, with invented titles left out ("Coming soon" per DECISIONS 2026-10-16) and the per-section
addresses (film@, animation@, clients@) folded into the one studio contact page (one address per org, 2026-10-21).
Head, header and footer are copied from site/video.html so the pages match the rest of the site.

  python3 scripts/build_fold_pages.py      # writes the four pages (idempotent)
"""
import html
import os
import re

SITE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'site'))
E = html.escape


def chrome():
    src = open(os.path.join(SITE, 'video.html'), encoding='utf-8').read()
    head = re.search(r'<head>.*?</head>', src, re.S).group(0)
    header = re.search(r'<header class="wrap site-head">.*?</header>', src, re.S).group(0)
    header = header.replace(' aria-current="page"', '')
    footer = re.search(r'<footer class="site-foot full-foot">.*?</footer>', src, re.S).group(0)
    return head, header, footer


def page_head(head, title, desc, path, image='https://buttsstudios.com/assets/og-default.png', section_css=True):
    url = 'https://buttsstudios.com' + path
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % E(title), head)
    h = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + E(desc), h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + E(desc), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + E(title), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, h)
    h = re.sub(r'(<meta property="og:image" content=")[^"]*', lambda m: m.group(1) + image, h)
    if not section_css:
        h = h.replace('<link rel="stylesheet" href="/shared/studios-section.css">\n', '')
    return h


def subnav(section, hosts):
    items = [('/books', 'Books'), ('/video', 'Video'), ('/games', 'Games')]
    a = ''.join('<a href="%s"%s><i class="bs-dot"></i>%s</a>' % (u, ' aria-current="page"' if n.lower() == section else '', n)
                for u, n in items)
    h = ''.join('<a href="%s">%s</a>' % (u, E(n)) for u, n in hosts)
    return ('<!--bs:subnav--><div class="wrap"><nav class="bs-subnav" aria-label="Sections"><span class="bs-sub-label">Sections</span>'
            '%s<span class="bs-sub-hosts">%s</span></nav></div><!--/bs:subnav-->' % (a, h))


BOOKS_HOSTS = [('/titles/us-against-the-world', 'Us Against the World'), ('/titles/talon', 'Talon'), ('/titles/the-signal', 'The Signal')]
VIDEO_HOSTS = [('/channels', 'The Channels'), ('/titles/the-little-things', 'The Little Things'), ('/video/film', 'Film'), ('/video/animation', 'Animation')]


def doc(section, head, header, footer, body, sub=None):
    attr = ' data-bs-section="%s"' % section if section else ''
    return ('<!doctype html>\n<html lang="en"%s>\n%s\n<body>\n\n%s\n\n%s\n<main>\n%s\n</main>\n\n%s\n\n</body>\n</html>\n'
            % (attr, head, header, (sub or '') + '\n', body, footer))


def rows(items):
    out = []
    for i, (name, line, label, note) in enumerate(items, 1):
        out.append('      <div class="title-row">\n        <span class="no">%02d</span>\n        <div><h3>%s</h3><div class="kind">%s</div></div>\n'
                   '        <p class="logline">%s</p>\n        <div class="stage"><span class="stage-label">%s</span></div>\n      </div>'
                   % (i, E(name), E(note), E(line), E(label)))
    return '\n'.join(out)


def steps(title, lede, items, cta_href, cta):
    cols = '\n'.join('        <div>\n          <h3>%s</h3>\n          <p>%s</p>\n        </div>' % (E(h), E(p)) for h, p in items)
    return ('  <section class="ink section">\n    <div class="wrap">\n      <div class="section-head">\n        <h2>%s</h2>\n        <p>%s</p>\n      </div>\n'
            '      <div class="principles">\n%s\n      </div>\n      <a class="btn" href="%s">%s</a>\n    </div>\n  </section>'
            % (E(title), E(lede), cols, cta_href, E(cta)))


def hero(eyebrow, word, lede, meta):
    m = ''.join('<span><strong>%s</strong> %s</span>' % (E(a), E(b)) for a, b in meta)
    return ('  <section class="wrap hero sec-hero">\n    <p class="eyebrow">%s</p>\n    <h1 class="display">%s<span class="accent">.</span></h1>\n'
            '    <div class="hero-row">\n      <p class="lede">%s</p>\n      <div class="hero-meta">%s</div>\n    </div>\n  </section>'
            % (E(eyebrow), E(word), E(lede), m))


def screen(tr, bl, title_eyebrow, title, strip):
    s = ''.join('\n        <a href="%s"><span>%02d</span> %s</a>' % (u, i, E(n)) for i, (u, n) in enumerate(strip, 1))
    return ('  <section class="wrap section">\n    <div class="screen" aria-label="%s">\n      <div class="screen-frame">\n'
            '        <span class="tc tc-tl">00:00:00:00</span><span class="tc tc-tr">%s</span>\n        <span class="tc tc-bl">%s</span><span class="tc tc-br">16:9</span>\n'
            '        <div class="screen-title"><span class="eyebrow">%s</span><span class="screen-h">%s</span></div>\n      </div>\n'
            '      <div class="screen-strip">%s\n      </div>\n    </div>\n  </section>'
            % (E(title), E(tr), E(bl), E(title_eyebrow), E(title), s))


def film(head, header, footer):
    h = page_head(head, 'Butts Studios Film · Butts Studios',
                  'Butts Studios Film: short films, music videos and brand films, shot and cut at the studio.', '/video/film')
    body = '\n\n'.join([
        hero('Butts Studios · Video', 'Film', 'Short films, music videos and brand films, shot and cut at the studio.',
             [('4', 'kinds of work'), ('Reel 01', 'coming soon')]),
        screen('BUTTS STUDIOS FILM', 'REEL 01', 'Reel 01 · Coming soon', 'The first reel goes up here when it is cut.',
               [('#make', 'What we make'), ('#work-with-us', 'Work with us'), ('/video', 'Video front page')]),
        '  <section class="wrap section" id="make">\n    <div class="section-head"><h2>What we make</h2><p>Four kinds of work, from the first idea to the final file.</p></div>\n'
        '    <div class="slate">\n' + rows([
            ('Short films', 'Narrative shorts, written and shot here, cut to the length the story needs.', 'Narrative', 'Written and shot at the studio'),
            ('Music videos', 'Performance and concept videos, made with the artist from treatment to final cut.', 'Music', 'Treatment to final cut'),
            ('Brand films', 'Short films for products and companies, cut for where they will run.', 'Commercial', 'Cut for each placement'),
            ('Post-production', 'Edit, color and sound finishing for footage you already have.', 'Finishing', 'Edit · color · sound'),
        ]) + '\n    </div>\n  </section>',
        steps('Bring us a film.', 'Tell us what you are making, when you need it and where it will run.',
              [('Write', 'Send the idea, the date and where it will be seen.'),
               ('Scope', 'We agree what gets made, the schedule and the price, in writing.'),
               ('Shoot and cut', 'Drafts come to you on the same thread until the final cut.')],
              '/contact?topic=projects', 'Start a film').replace('<section class="ink section">', '<section class="ink section" id="work-with-us">'),
        '  <section class="wrap section">\n    <div class="section-head"><h2>Also on Video</h2><p>The rest of the video slate.</p></div>\n    <div class="slate">\n'
        '      <a class="title-row" href="/channels"><span class="no">01</span><div><h3>The Channels</h3><div class="kind">YouTube · Five channels</div></div>'
        '<p class="logline">A small network of channels built to run on a schedule.<span class="more">Read more →</span></p><div class="stage"><span class="stage-label">Pre-production</span><span class="stage-note">First episodes in draft</span></div></a>\n'
        '      <a class="title-row" href="/video/animation"><span class="no">02</span><div><h3>Butts Studios Animation</h3><div class="kind">Animated shorts · Motion</div></div>'
        '<p class="logline">Hand-drawn shorts and motion work. The first series is The Little Things.<span class="more">Read more →</span></p><div class="stage"><span class="stage-label">Development</span><span class="stage-note">First shorts in development</span></div></a>\n'
        '    </div>\n  </section>',
    ])
    return doc('video', h, header, footer, body, subnav('video', VIDEO_HOSTS))


def animation(head, header, footer):
    h = page_head(head, 'Butts Studios Animation · Butts Studios',
                  'Butts Studios Animation: hand-drawn shorts and motion work. The first series is The Little Things.', '/video/animation',
                  image='https://buttsstudios.com/assets/little-things.jpg')
    shorts = [('The Held Door', 'Someone holds a door, and it ripples through the whole block.'),
              ('The Lost Glove', 'Found on a fence and returned, three neighbors later.'),
              ('The Borrowed Charger', 'One cord, four phones, a whole evening.'),
              ('The Wave', 'One of them waves first, every day, until someone waves back.')]
    body = '\n\n'.join([
        hero('Butts Studios · Video', 'Animation', 'Hand-drawn shorts and motion work. The first series is The Little Things.',
             [('1', 'shorts series'), ('4', 'first shorts in development')]),
        '  <section class="wrap section">\n    <figure class="work" style="margin:0">\n      <div class="frame contain" style="aspect-ratio:1080/530"><img src="/assets/little-things.jpg" alt="Three chalk-line characters on black: a round-headed one, a surprised one with a long neck, and an egg-shaped one" style="object-fit:cover;height:100%"></div>\n    </figure>\n  </section>',
        '  <section class="wrap section">\n    <div class="section-head"><h2>The Little Things</h2><p>Animated shorts · Wordless · 30–60 s. Four shorts, each one small act. They go up here as they are finished.</p></div>\n'
        '    <div class="slate">\n' + '\n'.join(
            '      <a class="title-row" href="/titles/the-little-things"><span class="no">%02d</span><div><h3>%s</h3><div class="kind">Short %02d · The Little Things</div></div>'
            '<p class="logline">%s<span class="more">Read more →</span></p><div class="stage"><span class="stage-label">Development</span><span class="stage-bar"><i class="now"></i><i></i><i></i><i></i></span><span class="stage-note">Coming soon</span></div></a>'
            % (i, E(n), i, E(l)) for i, (n, l) in enumerate(shorts, 1)) + '\n    </div>\n  </section>',
        '  <section class="wrap section">\n    <div class="section-head"><h2>What we make</h2><p>The same hand, for your project.</p></div>\n    <div class="slate">\n' + rows([
            ('Character animation', 'Hand-drawn 2D characters, animated in the line they were drawn in.', '2D', 'Drawn and animated by hand'),
            ('Motion graphics', 'Titles, logos and type set in motion for film, video and the web.', 'Motion', 'Titles · logos · type'),
            ('Animated shorts', 'Short pieces for brands and artists, from the first sketch to the final file.', 'Commission', 'Sketch to final file'),
        ]) + '\n    </div>\n  </section>',
        steps('Bring us a character.', 'Tell us who or what needs to move, how long it runs and where it will be seen.',
              [('Write', 'Send the idea, any drawings you have and the date.'),
               ('Scope', 'We agree the length, the style, the schedule and the price, in writing.'),
               ('Draw and animate', 'Sketches, motion tests and cuts come to you on the same thread.')],
              '/contact?topic=projects', 'Start an animation'),
    ])
    return doc('video', h, header, footer, body, subnav('video', VIDEO_HOSTS))


def signal(head, header, footer):
    h = page_head(head, 'The Signal · Butts Studios',
                  'The Signal, a novel series by Latarence Butts. Book one is being written at Butts Studios.', '/titles/the-signal',
                  section_css=False)
    body = '''  <div class="wrap">
  <section class="t-hero">
    <p class="eyebrow">Books · Novel series</p>
    <h1 class="display" style="font-size:clamp(44px,8vw,112px)">The Signal</h1>
    <div class="t-hero-meta">
      <p class="stage-badge">Book one in progress</p>
      <p class="kind">Novel series · Latarence Butts</p>
    </div>
  </section>

  <div class="t-grid" style="padding-bottom:clamp(56px,8vw,104px)">
    <article class="prose">
      <h2>The story</h2>
      <p>In a world where consciousness can be digitized and transmitted across the cosmos, humanity discovers an ancient signal from a civilization that faced the same existential questions we grapple with today. As scientists race to decode the message, they uncover truths that challenge everything we believe about life, death, and what it means to be human.</p>
      <blockquote class="excerpt">"The signal arrived at 3:47 AM on a Tuesday, as most world-changing events do—without ceremony, without warning. It was not a message from the stars, but something far more unsettling: a message from ourselves, sent from a future that no longer existed."<cite>Chapter One</cite></blockquote>

      <h2>The series</h2>
      <p><b>Book one, The Signal.</b> The discovery that changes everything. A signal from the void carries the secrets of a civilization that transcended death itself. Being written now.</p>
      <p><b>Next in the series.</b> The books that follow The Signal are coming soon.</p>
    </article>

    <aside>
      <div class="offer">
        <p class="stage-badge">Book one in progress</p>
        <p class="eyebrow">Updates</p>
        <h3>Chapters and release dates</h3>
        <p class="offer-stage">Ask for updates on the contact page and we add you to the list for new chapters and the release date.</p>
        <a class="btn" style="margin-top:6px" href="/contact?topic=updates">Get updates</a>
      </div>
      <dl>
        <div><dt>Format</dt><dd>Novel series</dd></div>
        <div><dt>Stage</dt><dd>Book one in progress</dd></div>
        <div><dt>Author</dt><dd>Latarence Butts</dd></div>
      </dl>
    </aside>
  </div>
  </div>'''
    return doc(None, h, header.replace('<a href="/work">', '<a href="/work" aria-current="page">'), footer, body)


TOPICS = [('projects', 'Projects'), ('partnerships', 'Partnerships'), ('press', 'Press'), ('shop', 'Shop orders'), ('updates', 'Title updates')]


def contact(head, header, footer):
    h = page_head(head, 'Contact · Butts Studios',
                  'Write to Butts Studios about a project, a partnership, press, a shop order or updates on a title.', '/contact',
                  section_css=False)
    opts = '\n'.join('          <option value="%s">%s</option>' % (v, E(n)) for v, n in TOPICS)
    body = '''  <section class="wrap hero sec-hero">
    <p class="eyebrow">Butts Studios · Contact</p>
    <h1 class="display">Contact<span class="accent">.</span></h1>
    <div class="hero-row">
      <p class="lede">Projects, partnerships, press, shop orders or updates on a title. Write to the studio and we reply by email.</p>
    </div>
  </section>

  <section class="wrap section">
    <div class="t-grid">
      <form class="cform" id="contact-form" action="mailto:hello@buttsstudios.com" method="post" enctype="text/plain">
        <label>Name<input name="name" type="text" autocomplete="name" required></label>
        <label>Email<input name="email" type="email" autocomplete="email" required></label>
        <label><span>Topic <span class="opt">(optional)</span></span>
          <select name="topic">
          <option value="">Choose a topic</option>
%s
          </select>
        </label>
        <label>Message<textarea name="message" rows="7" required></textarea></label>
        <button class="btn" type="submit">Write to the studio</button>
        <p class="offer-when">Sending opens your email app with the message filled in. It goes to hello@buttsstudios.com when you press send there.</p>
      </form>

      <aside>
        <div>
          <p class="eyebrow" style="margin-bottom:12px">Write directly</p>
          <p><a class="btn" style="margin-top:0" href="mailto:hello@buttsstudios.com">hello@buttsstudios.com</a></p>
        </div>
        <dl>
          <div><dt>Starting a project</dt><dd>Tell us what you are making, when you need it and where it will be seen. We agree scope, schedule and price by email.</dd></div>
          <div><dt>Already working with us</dt><dd>Reply on your project thread, or write with the project name in the subject.</dd></div>
          <div><dt>Shop orders</dt><dd>Include your order number from the Stripe receipt.</dd></div>
        </dl>
      </aside>
    </div>
  </section>

<script>
(function () {
  var f = document.getElementById('contact-form'); if (!f) return;
  try { var t = new URLSearchParams(location.search).get('topic'); if (t && f.topic.querySelector('option[value="' + t + '"]')) f.topic.value = t; } catch (e) {}
  f.addEventListener('submit', function (ev) {
    if (!f.reportValidity()) return;
    ev.preventDefault();
    var topic = f.topic.value ? f.topic.options[f.topic.selectedIndex].text : 'Message';
    var subject = topic + ' from ' + f.name.value.trim();
    var body = f.message.value.trim() + '\\n\\n' + f.name.value.trim() + '\\n' + f.email.value.trim();
    location.href = 'mailto:hello@buttsstudios.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
})();
</script>''' % opts
    return doc(None, h, header, footer, body)


def main():
    head, header, footer = chrome()
    out = {
        'video/film.html': film(head, header, footer),
        'video/animation.html': animation(head, header, footer),
        'titles/the-signal.html': signal(head, header, footer),
        'contact.html': contact(head, header, footer),
    }
    for rel, s in out.items():
        p = os.path.join(SITE, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(s)
        print('wrote site/' + rel)


if __name__ == '__main__':
    main()
