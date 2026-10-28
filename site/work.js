// Work page filters (STUDIOS-WORK-PAGE-1, 2026-10-28): anchor links (#all, #current, #books, #video, #games, #client,
// #design) that CSS :target filters with no JS. This script only enhances: it marks the active filter with
// aria-current and sets `hidden` on cards for browsers without :has(). Opens on Current work (Principal 2026-10-26).
(function () {
  var links = document.querySelectorAll('.wk-filters a');
  var cards = document.querySelectorAll('.wk-card');
  var more = document.querySelector('.wk-portfolio');
  function apply() {
    var f = (location.hash || '').slice(1);
    if (!document.querySelector('.wk-filters a[href="#' + f + '"]')) f = 'current';
    links.forEach(function (a) {
      if (a.getAttribute('href') === '#' + f) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });
    cards.forEach(function (c) { c.hidden = !(f === 'all' || (' ' + c.dataset.cat + ' ').indexOf(' ' + f + ' ') >= 0); });
    if (more) more.hidden = f !== 'current';
  }
  window.addEventListener('hashchange', apply);
  apply();
})();
