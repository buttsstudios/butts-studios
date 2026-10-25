// Work page filter: All · Current work · Client work · Design. The hash (#current, #client, #design) is shareable.
(function () {
  var btns = document.querySelectorAll('.wk-filters button');
  var cards = document.querySelectorAll('.wk-card');
  function apply(f) {
    if (!document.querySelector('.wk-filters [data-filter="' + f + '"]')) f = 'all';
    btns.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.filter === f)); });
    cards.forEach(function (c) { c.hidden = !(f === 'all' || c.dataset.cat === f); });
  }
  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.dataset.filter;
      history.replaceState(null, '', f === 'all' ? location.pathname : '#' + f);
      apply(f);
    });
  });
  apply((location.hash || '#all').slice(1));
})();
