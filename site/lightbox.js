// Portfolio lightbox: click any a.zoom to view it full size. Esc or a click outside closes,
// arrow keys and swipes move within the item's data-gallery. No libraries.
(function () {
  if (!document.querySelector('a.zoom')) return;

  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.hidden = true;
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-labelledby', 'lb-cap');
  lb.innerHTML =
    '<div class="lb-top"><p class="lb-cap" id="lb-cap"></p><span class="lb-count" aria-live="polite"></span>' +
    '<button type="button" class="lb-close" aria-label="Close">&times;</button></div>' +
    '<div class="lb-stage"><button type="button" class="lb-prev" aria-label="Previous image">&lsaquo;</button>' +
    '<img alt=""><button type="button" class="lb-next" aria-label="Next image">&rsaquo;</button></div>';
  document.body.appendChild(lb);

  var img = lb.querySelector('img');
  var cap = lb.querySelector('.lb-cap');
  var count = lb.querySelector('.lb-count');
  var stage = lb.querySelector('.lb-stage');
  var btnClose = lb.querySelector('.lb-close');
  var btnPrev = lb.querySelector('.lb-prev');
  var btnNext = lb.querySelector('.lb-next');
  var set = [], idx = 0, opener = null;

  function isShown(a) { return a.getClientRects().length > 0; }

  function preload(a) { if (a) { var i = new Image(); i.src = a.getAttribute('href'); } }

  function show(n) {
    idx = (n + set.length) % set.length;
    var a = set[idx];
    var href = a.getAttribute('href');
    var thumb = a.querySelector('img');
    img.src = href;
    img.alt = thumb ? thumb.alt : '';
    img.classList.toggle('is-svg', /\.svg$/i.test(href));
    cap.textContent = a.getAttribute('data-caption') || img.alt;
    var many = set.length > 1;
    count.textContent = many ? (idx + 1) + ' / ' + set.length : '';
    btnPrev.hidden = btnNext.hidden = !many;
    if (many) { preload(set[(idx + 1) % set.length]); preload(set[(idx - 1 + set.length) % set.length]); }
  }

  function open(a) {
    var g = a.getAttribute('data-gallery');
    set = Array.prototype.filter.call(document.querySelectorAll('a.zoom'), function (x) {
      return g && x.getAttribute('data-gallery') === g && isShown(x);
    });
    if (set.indexOf(a) < 0) set = [a];
    opener = a;
    show(set.indexOf(a));
    lb.hidden = false;
    document.documentElement.classList.add('lb-open');
    btnClose.focus();
  }

  function close() {
    lb.hidden = true;
    img.removeAttribute('src');
    document.documentElement.classList.remove('lb-open');
    if (opener) opener.focus();
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a.zoom') : null;
    if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    open(a);
  });

  lb.addEventListener('click', function (e) {
    if (e.target === lb || e.target === stage || e.target.classList.contains('lb-top')) close();
  });
  btnClose.addEventListener('click', close);
  btnPrev.addEventListener('click', function () { show(idx - 1); });
  btnNext.addEventListener('click', function () { show(idx + 1); });

  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowRight' && set.length > 1) { e.preventDefault(); show(idx + 1); }
    else if (e.key === 'ArrowLeft' && set.length > 1) { e.preventDefault(); show(idx - 1); }
    else if (e.key === 'Tab') {
      var f = [btnClose, btnPrev, btnNext].filter(function (b) { return !b.hidden; });
      var at = f.indexOf(document.activeElement);
      e.preventDefault();
      f[(at + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
    }
  });

  var x0 = null, y0 = null;
  stage.addEventListener('touchstart', function (e) {
    if (e.touches.length === 1) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }
  }, { passive: true });
  stage.addEventListener('touchend', function (e) {
    if (x0 === null || set.length < 2) { x0 = null; return; }
    var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(idx + (dx < 0 ? 1 : -1));
    x0 = null;
  }, { passive: true });
})();
