/* NCT homepage hero: keeps the 3D model in step with the theme's tabs.
   The theme moves to the next tab by itself every few seconds without a click, so hero3d.js (which listens for
   clicks) would otherwise leave the first model showing under the next tab's caption. Loaded after hero3d.js. */
(function () {
  var api = window.__hero3d, art = document.querySelector('.hero-art');
  if (!api || !art || !window.MutationObserver) return;
  var tabs = Array.prototype.slice.call(art.querySelectorAll('.fig-tab'));
  if (!tabs.length) return;
  var last = 0; // hero3d.js starts on the first tab
  function sync() {
    var active = -1;
    tabs.forEach(function (t, n) { if (active < 0 && t.classList.contains('is-active')) active = n; });
    if (active < 0 || active === last) return;
    last = active;
    api.select(active);
  }
  var seen = new MutationObserver(sync);
  tabs.forEach(function (t) { seen.observe(t, { attributes: true, attributeFilter: ['class'] }); });
  sync();
})();
