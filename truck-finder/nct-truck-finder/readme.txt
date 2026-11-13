=== NCT Truck Finder ===
Requires at least: 5.8
Requires PHP: 7.2
Stable tag: 1.1.0

Interactive 3D "Which truck do you need training on?" selector for National Compliance Training.

== What it does ==

Shows twelve 3D machines (counterbalance, reach, pivot steer, VNA, telehandler, powered pallet truck, pump truck,
low and high level order pickers, scissor and boom MEWPs, gantry crane). Visitors pick the one that looks like theirs,
read how to recognise it, try its controls and go to the matching course page.

== Install ==

1. WordPress admin > Plugins > Add New > Upload Plugin, choose nct-truck-finder.zip, Install, Activate.
2. That is all for the forklift training page: the finder is added to the top of the page with the slug
   "forklift-training" as soon as the plugin is active.

To remove it from that page, deactivate the plugin. Nothing is written to the database or to the page's content.

== Two views ==

Showcase (the default): each truck stands on a turntable, as in the homepage hero. Visitors pick a truck, read
how to recognise it, drag to turn it, and go to the course page. Each truck gently works through its own motion.

Interactive: the same trucks in a marked bay with a steering wheel or tiller, pedal and hydraulic levers.

To make interactive the default, add to the theme's functions.php:

    add_filter( 'nct_truck_finder_mode', function () { return 'interactive'; } );

Or choose per placement with the shortcode: [nct_truck_finder mode="interactive"] or [nct_truck_finder mode="showcase"].

== Using it elsewhere ==

Put the shortcode [nct_truck_finder] in any page or in an Elementor Shortcode widget. It appears where you put it.
[nct_truck_finder place="top"] moves it to the top of the page's main area, full width, under the site header.
Only one finder can appear on a page.

To change which pages get it automatically, add to the theme's functions.php:

    add_filter( 'nct_truck_finder_auto_pages', function () { return array( 'forklift-training', 'another-page-slug' ); } );

Return an empty array to turn automatic insertion off and use only the shortcode.

== Good to know ==

* The 3D model files are in assets/models (.glb, about 13 MB in total). A model is only downloaded when a visitor
  selects that truck; the page itself loads one model.
* If your site uses a page cache or a CDN, clear it after activating.
* three.js (MIT licence) is bundled in assets/js; nothing is loaded from other sites.
* The course buttons link to /courses/<course-slug>/ on this site. The slugs are listed near the top of assets/js/finder.js.
* The models were generated with Blender from the scripts kept alongside this plugin's source.
