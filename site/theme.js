// Theme toggle: follows the system setting until the viewer picks light or dark.
(function () {
  var root = document.documentElement;
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;
  function current() {
    if (root.dataset.theme === 'light' || root.dataset.theme === 'dark') return root.dataset.theme;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function label() {
    btn.setAttribute('aria-label', current() === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }
  btn.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try { localStorage.setItem('bs-theme', next); } catch (e) {}
    label();
  });
  label();
})();

// Phone menu: under 700px the nav links fold behind a menu button next to the theme toggle.
(function () {
  var head = document.querySelector('.site-head');
  var nav = head && head.querySelector('nav');
  if (!nav || nav.querySelector('.menu-toggle')) return;
  var links = nav.querySelectorAll('a');
  if (!links.length) return;
  var wrap = document.createElement('div');
  wrap.className = 'nav-links';
  wrap.id = 'site-nav-links';
  links[0].parentNode.insertBefore(wrap, links[0]);
  links.forEach(function (a) { wrap.appendChild(a); });
  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'menu-toggle';
  btn.setAttribute('aria-controls', wrap.id);
  btn.setAttribute('aria-expanded', 'false');
  btn.setAttribute('aria-label', 'Open menu');
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path class="l1" d="M4 7h16"/><path class="l2" d="M4 12h16"/><path class="l3" d="M4 17h16"/></svg>';
  var toggle = nav.querySelector('.theme-toggle');
  nav.insertBefore(btn, wrap);
  function set(open) {
    head.classList.toggle('menu-open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  btn.addEventListener('click', function (e) { e.stopPropagation(); set(!head.classList.contains('menu-open')); });
  links.forEach(function (a) { a.addEventListener('click', function () { set(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && head.classList.contains('menu-open')) { set(false); btn.focus(); } });
  document.addEventListener('click', function (e) { if (head.classList.contains('menu-open') && !head.contains(e.target)) set(false); });
  window.addEventListener('resize', function () { if (window.innerWidth > 700) set(false); });
})();
