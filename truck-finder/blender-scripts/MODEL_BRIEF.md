# NCT truck models: modelling brief

We are building our own 3D model files (.glb) of the truck types National Compliance Training teaches, for a "Which truck do you need training on?" selector on their website. A visitor must be able to recognise their own truck from the model, so correct proportions and the defining features of each type matter more than anything else. The current stand-ins are crude block models (see ../proposal-g/shots/models.png); yours must look like a proper scale model of a real machine.

## How you work
- Folder: /tmp/claude-0/-home-user-nct-cyberweek-popup/b62af6cd-744e-576d-9ff5-25539e601603/scratchpad/models3d/
- Blender runs headless as a Python module. Run a model script with: `../bl/bin/python <key>.py 2>&1 | grep -E "EXPORTED|Error|Traceback|line "` (run from the models3d folder).
- Each truck is ONE script `<key>.py` that starts with:
  ```python
  import sys, os, math
  sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
  from nctlib import *
  reset()
  ...build...
  export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "<key>.glb"))
  ```
- READ nctlib.py first, all of it. It has the conventions and the tools: box (bevelled), cyl, profile (extrude a 2D outline: use this for anything curved or stepped), arc_pts, lathe, tube (bent round tube), wheel, pallet, fork_tine, empty, set_parent, key, export. test_lib.py is a tiny working example. Do NOT edit nctlib.py, viewer.html or check.js (other agents are using them at the same time). If you need more helpers, put them in your own script.
- Check your work: `node check.js <key> <dist> <ty>` renders six views (four at rest, two in the working pose) to shots/<key>-sheet.png and prints the bounding box. dist is camera distance (about 9 for small trucks, 11 for a counterbalance, 14 for tall ones), ty is the height the camera aims at. LOOK at the sheet with the Read tool, and at individual views shots/<key>-<view>.png when you need detail. You can also render any angle: the viewer takes ?az= (0 front, 1.57 right side, 3.14 rear), el, t (0 rest to 1 working), dist, ty; copy check.js into your own file if you want other views.
- Iterate. Do at least four build-look-fix rounds per truck. Compare what you see against what the real machine looks like and fix the biggest difference each round. Do not stop while anything floats, intersects wrongly, is out of proportion, or looks like a stack of boxes.

## Conventions (must follow exactly, the web page depends on them)
- Metres. X = width, -Y = FORWARD (forks point to -Y), +Z up. Origin on the floor under the middle of the truck; tyres touch Z = 0.
- Materials only via the names in nctlib.PALETTE (pass the name string). Body colour is "paint" (orange). Use "accent" (magenta) only for small touches (a stripe, a button, the load strap). No logos, no manufacturer names or lettering, no textures.
- Exactly one working motion per truck, keyframed with key(obj, FRAME_REST, ...) and key(obj, FRAME_WORK, ...) on empties (pivots) that the moving parts are parented to. Everything that should move together must be parented under the keyed empty. The specified motion for each truck is below. The load (pallet) rides on the forks.
- Parent a mesh to an empty or to another object with parent=...; a child's loc is then LOCAL to its parent. Rotation of a parented empty rotates all its children about the empty's origin, so put pivots where the real hinge is.
- Budgets per truck: under 150,000 triangles, file under 3 MB (export() prints both). export() automatically bakes modifiers and merges static meshes, so do not worry about object count.
- Wheels: warehouse trucks have smooth solid tyres (default wheel()); only rough-terrain machines get tread=True.

## What "realistic" means here
Look at how the real machines are built and reproduce the visible construction, not just the outline:
- Bodywork with real shapes: curved cast counterweights, sloped/stepped hoods and cowls, wheel arches, side panels with a visible step or seam, a floor plate, foot step, grab handle. Use profile() with arcs for these. Generous bevels on cast and pressed parts, tight bevels on machined steel.
- Mast: two-stage look (outer channels and inner channels), cross-members, lift chains over pulleys at the top, a central lift cylinder with a chrome rod, tilt cylinders from chassis to mast where the type has them, hydraulic hoses (tube()).
- Fork carriage: carriage plate, load backrest (a frame with vertical bars), two forged tines (fork_tine()), the loaded pallet sitting ON the tines (pallet() origin is the pallet underside; a tine is 0.045 m thick).
- Operator position: shaped seat with backrest, steering wheel on a column (or the right control for the type), control levers, pedals, dash/display, overhead guard made from bent tube or bar with roof bars, rear-view mirror, work lights ("lamp"), amber beacon ("beacon"), tail lights ("tail").
- Small truthful details: data plate ("decal"), hazard chevrons or stripe on the counterweight edge ("hazard"), tow pin, wheel nuts, mudguards, battery/engine cover seams, handrails.
- Real proportions (given per truck below). Nothing paper-thin, nothing floating; parts meet or overlap where they would be bolted or welded.
The look is a clean, well-made scale model in studio light. It does not need dirt or wear.

## Finish
Leave `<key>.py`, `out/<key>.glb` and `shots/<key>-sheet.png` for each of your trucks. Report for each: triangle count and file size, the name of the keyed pivot(s) and what the motion does, a good camera dist and ty for the web page (so the whole truck in its working pose fits with a little margin), and anything you are not happy with. Do not publish anything, do not touch git, do not write outside the models3d folder.

## Round two additions
Seven machines are already finished and set the standard you must match: look at shots/counter-sheet.png, shots/reach-sheet.png, shots/ppt-sheet.png, shots/mewp-sheet.png and shots/tele-sheet.png before you start, and read the scripts that made them (counter.py with cb_common.py, reach.py with wh_common.py, ppt.py / mewp.py / tele.py with tpmlib.py). You may import and reuse functions from cb_common.py, wh_common.py and tpmlib.py, but do NOT edit those files, the existing model scripts, nctlib.py, viewer.html or check.js; put new helpers in a new file of your own. Notes from round one that matter:
- The exporter writes several animation clips per file (one per keyed object); that is fine, the web page plays them all together.
- You may keyframe every frame from 0 to 24 (not just the two ends) where a linkage must stay pinned through the motion (rams, scissor arms, ropes); tpmlib.py has a per-frame hydraulic ram helper.
- A rope, chain or ram that changes length can be done by scale-keying a part whose origin is at its fixed end.
