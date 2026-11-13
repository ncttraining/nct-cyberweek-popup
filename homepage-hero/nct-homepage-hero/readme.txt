=== NCT Homepage Hero 3D ===
Requires at least: 5.8
Requires PHP: 7.2
Stable tag: 1.0.0

Replaces the five flat illustrations in the homepage hero with 3D models on a turntable.

== What it does ==

On the front page only, it adds a 3D stage to the theme's existing hero (the block with the five tabs: Forklift & Plant,
Transport & CPC, First Aid, Fire Safety, Working at Height). Each tab shows its own model: counterbalance truck, lorry,
first aid kit, fire extinguisher scene, scissor lift. Visitors can drag the turntable round. Nothing else in the hero
changes: the captions, the tabs and the automatic change of tab every few seconds are the theme's own.

== Install ==

1. WordPress admin > Plugins > Add New > Upload Plugin, choose nct-homepage-hero.zip, Install, Activate.
2. Clear the page cache (Kinsta, then Autoptimize).

To remove it, deactivate the plugin. Nothing is written to the database or to the page's content.

== Good to know ==

* It relies on the nct-momentum theme's hero markup (.hero-art, .fig-stage, .hero-fig, .fig-tab). If the theme's hero is
  changed or removed, the plugin does nothing and the page is left as the theme draws it.
* The original illustrations stay in the page and are shown again if the visitor's browser cannot do 3D (no WebGL).
* The five model files are in assets/models (.glb, about 7 MB in total). The first loads with the page; the other four
  are fetched one at a time in the first few seconds so that changing tab is instant. three.js is about 600 KB.
* three.js (MIT licence) is bundled in assets/js; nothing is loaded from other sites.
* To turn it off without deactivating, add to the theme's functions.php:
      add_filter( 'nct_homepage_hero_enabled', '__return_false' );
* The models were generated with Blender from the scripts kept alongside this plugin's source.
