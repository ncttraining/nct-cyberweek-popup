# NCT Truck Finder

Interactive 3D "Which truck do you need training on?" selector for the forklift training page.
This folder is separate from the discount banner plugin in the repository root.

- `nct-truck-finder/` is the WordPress plugin, ready to deploy.
- `blender-scripts/` generates the twelve `.glb` models (`pip install bpy`, then `python counter.py` etc.; each script writes to an `out/` folder beside it, which must exist).
- `mockup/index.html` is the standalone design mockup the plugin was generated from.

## Deploy

1. Upload the `nct-truck-finder` folder to `wp-content/plugins/` on the server (SFTP/WinSCP), or zip it and use Plugins > Add New > Upload Plugin.
2. Activate "NCT Truck Finder" in WordPress admin and clear any page cache.

Once active it adds itself to the top of the page with the slug `forklift-training`. It writes nothing to the database or page content; deactivating it removes it. `[nct_truck_finder]` places it anywhere else. See `nct-truck-finder/readme.txt`.

## Status

Tested by rendering the plugin's output into a copy of the live page with the theme's styles (desktop and phone). Not yet run inside WordPress itself. The spotting descriptions and model dimensions have not been checked by an instructor.
