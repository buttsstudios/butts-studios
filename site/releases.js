// Releases page filter (2026-11-02). /releases shows the studio's own titles; the kind filter is #all, #books, #video,
// #games (state in the hash). #current and #originals show everything; #client, #commissions, #design and #web belong to /work. Without this script the page shows every title and the filter stays hidden.
(function () {
  var MOVED = ['client', 'commissions', 'design', 'web'];
  var TYPES = ['books', 'video', 'games'];
  var h = (location.hash || '').slice(1).split(/[\/&]/).pop();
  if (MOVED.indexOf(h) >= 0) { location.replace('/work'); return; }
  var root = document.querySelector('.wk');
  if (!root) return;
  var cards = [].slice.call(root.querySelectorAll('.wk-card'));
  var controls = root.querySelector('.wk-controls');
  var links = [].slice.call(root.querySelectorAll('.wk-types a'));
  function apply() {
    var t = (location.hash || '').slice(1);
    if (TYPES.indexOf(t) < 0) t = 'all';
    cards.forEach(function (c) { c.hidden = !(t === 'all' || c.dataset.type === t); });
    links.forEach(function (a) {
      if (a.dataset.type === t) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
    if (controls) controls.hidden = false;
  }
  window.addEventListener('hashchange', apply);
  apply();
})();
