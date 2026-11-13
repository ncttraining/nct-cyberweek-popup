# Homepage hero: 3D scenes

Replaces the five flat illustrations in the homepage hero with Blender-modelled 3D scenes on a turntable.
Nothing else in the hero changes. Not yet packaged for WordPress.

- `hero3d.js` is the 3D stage. It needs three.js r128 and its GLTFLoader loaded first, and expects the theme's
  existing hero markup (`.hero-art`, `.fig-stage`, `.hero-fig`, `.fig-tab`) plus one added element as the first
  child of `.fig-stage`:
  `<div class="h3d" id="h3d"><canvas id="h3d-canvas" role="img" aria-label="3D model of the selected training area"></canvas></div>`
- Set `window.NCTHero3D = { models: '<url of the models folder>/', ext: '.glb' }` before the script.
- `models/` holds the five scenes, in tab order: counter, lorry, firstaid, fire, mewp.
- `blender-scripts/` holds the three scenes made for the hero; they use `nctlib.py` and `tpmlib.py` from
  `truck-finder/blender-scripts/`. The forklift and scissor lift scripts are there too.

The few CSS rules it needs:

    .fig-stage{grid-template-rows:auto auto}
    .h3d{grid-area:1/1;position:relative;aspect-ratio:1/0.82;display:none}
    .has-3d .h3d{display:block}
    .h3d canvas{position:absolute;left:-24%;top:-26%;width:148%;height:126%;display:block;touch-action:pan-y;cursor:grab}
    .has-3d .hero-fig{grid-area:2/1}
    .has-3d .hero-fig svg{display:none}
    @media (max-width:860px){.h3d canvas{left:-8%;width:116%;top:-10%;height:116%}}

The original SVG illustrations stay in the page and show again if WebGL is unavailable.
