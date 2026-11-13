# Homepage hero: 3D scenes

Replaces the five flat illustrations in the homepage hero with Blender-modelled 3D scenes on a turntable.
Nothing else in the hero changes.

- `nct-hero-3d/` is the WordPress plugin. Upload the folder to `wp-content/plugins/` (or zip it and use
  Plugins > Add New > Upload Plugin), activate "NCT Hero 3D", clear the page cache. See its `readme.txt`.
- `blender-scripts/` holds the three scenes made for the hero; they use `nctlib.py` and `tpmlib.py` from
  `truck-finder/blender-scripts/`, where the forklift and scissor lift scripts also live.

The plugin loads on the front page only, adds its own stage element to the theme's hero, and follows the
theme's tabs (including their automatic switching). The original illustrations stay as the fallback.

Status: tested against a copy of the live homepage with the theme's own styles and tab script. Not yet run
inside WordPress itself.
