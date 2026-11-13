/* NCT homepage hero: adds the 3D stage element to the theme's hero so hero3d.js (loaded next) can draw into it.
   Does nothing if the hero is not on the page or the stage is already there. */
(function () {
  var stage = document.querySelector('.hero-art .fig-stage');
  if (!stage || document.getElementById('h3d')) return;
  var box = document.createElement('div');
  box.className = 'h3d';
  box.id = 'h3d';
  var canvas = document.createElement('canvas');
  canvas.id = 'h3d-canvas';
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', '3D model of the selected training area');
  box.appendChild(canvas);
  stage.insertBefore(box, stage.firstChild);
})();
