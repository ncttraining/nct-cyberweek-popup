# Homepage hero: 3D scenes

Replaces the five flat illustrations in the homepage hero with Blender-modelled 3D scenes on a turntable.
Nothing else in the hero changes. This folder is separate from the discount banner plugin in the repository root
and from `truck-finder/`.

- `nct-homepage-hero/` is the WordPress plugin, ready to deploy.
- `blender-scripts/` holds the three scenes made for the hero (lorry, first aid, fire); they use `nctlib.py` and
  `tpmlib.py` from `truck-finder/blender-scripts/`. The forklift and scissor lift scripts are there too, and their
  models are the same files the truck finder uses.

## How the plugin is put together

On the front page only, `nct-homepage-hero.php` loads, in this order:

1. `assets/css/hero3d.css`: the few layout rules the stage needs, scoped to `.hero-art`. The stage is laid over the
   illustration it replaces (which is hidden but keeps its space), so nothing in the hero moves when 3D switches
   on. The mockup's rules moved the caption block to a second grid row, which measured as a layout shift (CLS) of
   0.17 on desktop.
2. `assets/js/three.min.js` and `GLTFLoader.js` (three.js r128).
3. `assets/js/hero3d-stage.js`: adds `<div class="h3d" id="h3d"><canvas id="h3d-canvas">` as the first child of the
   theme's `.fig-stage`.
4. `assets/js/hero3d.js`: the 3D stage itself, unchanged from the design mockup. It reads `window.NCTHero3D`
   (`models` URL and `ext`), which the plugin sets.
5. `assets/js/hero3d-sync.js`: keeps the model in step with the theme's tabs. The theme moves to the next tab by
   itself every five seconds without a click; `hero3d.js` only listens for clicks, so without this the first model
   stayed on screen under the next tab's caption.

`assets/models/` holds the five scenes, in tab order: counter, lorry, firstaid, fire, mewp.

The original SVG illustrations stay in the page and show again if WebGL is unavailable.

## Deploy

1. Upload the `nct-homepage-hero` folder to `wp-content/plugins/` on the server (SFTP/WinSCP), or zip it and use
   Plugins > Add New > Upload Plugin.
2. Activate "NCT Homepage Hero 3D" in WordPress admin and clear the page caches (Kinsta, then Autoptimize).

It writes nothing to the database or page content; deactivating it removes it.

## Status

Tested by rendering the plugin's output into the live homepage in a headless browser (the page HTML fetched from the
live site, the plugin's tags added, its files served from this folder) at phone, tablet and desktop widths, and by
running the PHP file against a stand-in for WordPress's enqueue functions. Not yet run inside WordPress itself.
