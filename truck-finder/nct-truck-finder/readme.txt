=== NCT Truck Finder ===
Requires at least: 5.8
Requires PHP: 7.2
Stable tag: 1.3.1

3D truck finder and truck simulator for National Compliance Training.

== What it does ==

Shows twelve 3D machines (counterbalance, reach, pivot steer, VNA, telehandler, powered pallet truck, pump truck,
low and high level order pickers, scissor and boom MEWPs, gantry crane). Visitors pick the one that looks like theirs,
read how to recognise it, try its controls and go to the matching course page.

== Install ==

1. WordPress admin > Plugins > Add New > Upload Plugin, choose nct-truck-finder.zip, Install, Activate.
2. That is all for the forklift training page: the finder is added to the top of the page with the slug
   "forklift-training" as soon as the plugin is active.

To remove it from that page, deactivate the plugin. Nothing is written to the database or to the page's content.

== Truck simulator page ==

While the plugin is active the site has a page at /truck-simulator/ (for example
https://nationalcompliancetraining.co.uk/truck-simulator/). Visitors pick a truck, drive it round a yard with a
steering wheel or tiller, pedal and hydraulic levers, and move four pallets into marked floor bays or four free
rack positions (floor level and each of the three beams, the top one at about 3.7 m). To lift a pallet: line the forks up, drive in with the forks low, raise them. To set it down: lower
the forks. Scissor lift, boom lift and gantry crane can be driven and worked but do not carry pallets.

Trucks, forks and carried pallets are solid: they stop at pallets and at the racking. Forks only go into a pallet at
the right height and roughly square on, and only into the racking at a free position. The counterbalance, reach,
pivot steer, VNA and high-level order picker lift to about 4 m and reach the top beam; the pallet trucks and the
low-level order picker work at floor level only.

A truck that is touching something can always back away from it, and reversing always draws the forks out. The
"Recover truck" button on the control panel parks the truck in a clear part of the yard with the forks down.

The page is produced by the plugin; it is not stored in WordPress, so it does not appear under Pages and it
disappears when the plugin is deactivated. It is not added to any menu: link to it wherever you like. The truck
finder on the forklift training page has a "Try driving one" button that goes to it.

If you would rather have it inside a normal WordPress page, put the shortcode [nct_truck_simulator] in that page.
A real page with the address /truck-simulator/ takes priority over the built-in one.

To change the address, or switch the built-in page off, add to the theme's functions.php:

    add_filter( 'nct_truck_simulator_slug', function () { return 'forklift-simulator'; } );   // new address
    add_filter( 'nct_truck_simulator_slug', '__return_empty_string' );                         // off

== Truck finder view ==

The finder on the forklift training page shows each truck on a turntable, as in the homepage hero. To show the
simulator there instead, use [nct_truck_finder mode="interactive"], or:

    add_filter( 'nct_truck_finder_mode', function () { return 'interactive'; } );

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
