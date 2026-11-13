=== NCT Hero 3D ===
Requires at least: 5.8
Requires PHP: 7.2
Stable tag: 1.0.0

Replaces the flat illustrations in the homepage hero with 3D scenes on a turntable.

== What it does ==

On the site's front page, the picture area of the hero shows a 3D scene for each training-area tab:
forklift, lorry, first aid station, fire point and scissor lift. The headline, copy, buttons, tabs and
captions are untouched. The hero's tabs keep working exactly as they do now, including switching by
themselves every few seconds; the 3D scene follows whichever tab is active.

== Install ==

1. WordPress admin > Plugins > Add New > Upload Plugin, choose nct-hero-3d.zip, Install, Activate.
2. Clear any page cache (and Autoptimize's cache).

To remove it, deactivate the plugin. It changes no theme files, page content or database entries.

== Good to know ==

* It relies on the current theme's hero markup (.hero, .hero-art, .fig-stage, .hero-fig, .fig-tab).
  If the theme's hero is rebuilt with different class names the plugin simply does nothing.
* If a visitor's browser cannot run 3D, the original illustrations show as before.
* Visitors who have asked their device to reduce motion get a still scene.
* The five model files are in assets/models (.glb, about 7 MB in total). The first loads with the page;
  the rest follow one at a time in the background.
* three.js (MIT licence) is bundled in assets/js; nothing is loaded from other sites.
* To switch it off without deactivating:  add_filter( 'nct_hero_3d_enabled', '__return_false' );
