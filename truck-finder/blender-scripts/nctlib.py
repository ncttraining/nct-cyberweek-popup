"""Shared Blender helpers for the NCT truck models.

Conventions (do not change):
  * Units are metres. X = width (truck's left/right), -Y = FORWARD (forks point to -Y), +Z = up.
    The glTF exporter turns this into Y-up with the truck's front facing +Z, which is what the web page expects.
  * Origin (0,0,0) is on the floor under the middle of the truck. Wheels touch Z = 0.
  * Every model has ONE working motion, keyframed from frame 0 (rest) to frame 24 (fully working).
  * Materials come only from PALETTE below so all seven trucks match.
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix

FRAME_REST, FRAME_WORK = 0, 24

# name: (sRGB hex, metallic, roughness, extras)
PALETTE = {
    "paint":   ("#F08418", 0.0, 0.40, {"coat": 0.8}),     # body orange (brand)
    "accent":  ("#E4125D", 0.0, 0.40, {"coat": 0.8}),     # brand magenta, use sparingly
    "chassis": ("#2A262D", 0.3, 0.55, {}),                # dark painted steel
    "mast":    ("#1B191D", 0.65, 0.42, {}),               # mast channels, guard tube
    "steel":   ("#9A9CA3", 0.95, 0.34, {}),               # bare steel: forks, pins
    "chrome":  ("#E3E5EA", 1.0, 0.10, {}),                # hydraulic rods
    "rubber":  ("#0E0D0F", 0.0, 0.93, {}),
    "vinyl":   ("#17151A", 0.0, 0.62, {}),                # seat, grips
    "rim":     ("#D9D6D2", 0.4, 0.45, {}),
    "plastic": ("#3A363D", 0.0, 0.60, {}),                # cowls, dash, covers
    "glass":   ("#A9BCCB", 0.0, 0.05, {"alpha": 0.30}),
    "lamp":    ("#FFF6DD", 0.0, 0.30, {"emit": ("#FFF0C0", 2.0)}),
    "beacon":  ("#FF9A2A", 0.0, 0.35, {"emit": ("#FF7A00", 1.5)}),
    "tail":    ("#C01818", 0.0, 0.35, {"emit": ("#A00808", 1.0)}),
    "card":    ("#B58A5A", 0.0, 0.90, {}),                # cartons
    "card2":   ("#A27A4E", 0.0, 0.90, {}),
    "tape":    ("#D8C39A", 0.0, 0.50, {}),
    "wood":    ("#CDAA78", 0.0, 0.85, {}),                # pallets
    "decal":   ("#FDFBFC", 0.0, 0.50, {}),                # white data plates / stripes
    "hazard":  ("#F2C200", 0.0, 0.50, {}),                # yellow warning marks
}
_mats = {}


def _lin(hexstr):
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def reset():
    """Start from an empty scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = FRAME_REST, FRAME_WORK
    sc.render.fps = 24
    sc.frame_set(FRAME_REST)
    try:
        bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    except Exception:
        pass


def mat(name):
    if name in _mats:
        return _mats[name]
    hexc, metal, rough, extra = PALETTE[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = _lin(hexc)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if "coat" in extra:
        b.inputs["Coat Weight"].default_value = extra["coat"]
        b.inputs["Coat Roughness"].default_value = 0.2
    if "emit" in extra:
        b.inputs["Emission Color"].default_value = _lin(extra["emit"][0])
        b.inputs["Emission Strength"].default_value = extra["emit"][1]
    if "alpha" in extra:
        b.inputs["Alpha"].default_value = extra["alpha"]
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    _mats[name] = m
    return m


def _finish(obj, material, bevel, parent, smooth=True, segments=3):
    me = obj.data
    if material:
        me.materials.append(mat(material) if isinstance(material, str) else material)
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    if bevel and bevel > 0:
        md = obj.modifiers.new("Bevel", 'BEVEL')
        md.width = bevel
        md.segments = segments
        md.limit_method = 'ANGLE'
        md.angle_limit = math.radians(35)
        md.harden_normals = True
    elif smooth:
        try:
            me.set_sharp_from_angle(angle=math.radians(35))
        except Exception:
            pass
    if parent is not None:
        set_parent(obj, parent)
    return obj


def _new_obj(name, bm, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def set_parent(obj, parent):
    """Parent obj to parent. obj.location / rotation are then LOCAL to the parent."""
    obj.parent = parent
    return obj


def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    """An invisible pivot. Parent moving parts to an empty and keyframe the empty."""
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.empty_display_size = 0.2
    e.location = loc
    e.rotation_euler = rot
    if parent is not None:
        e.parent = parent
    return e


def box(name, size, loc, material, bevel=0.02, parent=None, rot=(0, 0, 0), segments=3):
    """Box of size (x, y, z) centred on loc, with bevelled (rounded) edges."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    b = min(bevel, min(size) / 2 * 0.9) if bevel else 0
    return _finish(_new_obj(name, bm, loc, rot), material, b, parent, segments=segments)


def cyl(name, radius, length, loc, material, axis='Z', bevel=0.0, parent=None, verts=32, rot=None, radius2=None):
    """Cylinder (or cone if radius2 given) with its length along axis 'X', 'Y' or 'Z'."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=radius, radius2=radius if radius2 is None else radius2, depth=length)
    r = rot if rot is not None else {'Z': (0, 0, 0), 'X': (0, math.radians(90), 0), 'Y': (math.radians(90), 0, 0)}[axis]
    return _finish(_new_obj(name, bm, loc, r), material, bevel, parent)


def profile(name, pts, width, loc, material, bevel=0.02, parent=None, plane='YZ', rot=(0, 0, 0), segments=3):
    """Extrude a 2D outline into a solid: the main tool for curved or stepped shapes
    (counterweights, cowls, mudguards, fork tines, side frames).
    pts: list of (a, b) outline points, in order. plane 'YZ' -> a=Y (negative = forward), b=Z (up), extruded across X.
    plane 'XZ' -> a=X, b=Z, extruded along Y. plane 'XY' -> a=X, b=Y, extruded up Z.
    The solid is centred on loc along the extrusion direction; a/b are offsets from loc."""
    bm = bmesh.new()
    if plane == 'YZ':
        vs = [bm.verts.new((-width / 2, a, b)) for a, b in pts]; d = Vector((width, 0, 0))
    elif plane == 'XZ':
        vs = [bm.verts.new((a, -width / 2, b)) for a, b in pts]; d = Vector((0, width, 0))
    else:
        vs = [bm.verts.new((a, b, -width / 2)) for a, b in pts]; d = Vector((0, 0, width))
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=d, verts=[v for v in res["geom"] if isinstance(v, bmesh.types.BMVert)])
    return _finish(_new_obj(name, bm, loc, rot), material, bevel, parent, segments=segments)


def arc_pts(cx, cy, r, a0, a1, n=10):
    """Points along an arc (degrees, anticlockwise from +a axis): handy inside profile() outlines for round corners."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def lathe(name, pts, loc, material, axis='X', parent=None, steps=40, bevel=0.0):
    """Spin a (radius, along) outline round an axis: tyres, rims, lamps, beacons."""
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, a)) for r, a in pts]
    edges = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + edges, cent=(0, 0, 0), axis=(0, 0, 1), angle=math.radians(360), steps=steps, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
    r = {'Z': (0, 0, 0), 'X': (0, math.radians(90), 0), 'Y': (math.radians(90), 0, 0)}[axis]
    return _finish(_new_obj(name, bm, loc, r), material, bevel, parent)


def tube(name, points, radius, material, parent=None, closed=False, resolution=8):
    """A round tube through 3D points (smoothly curved): guard frames, handrails, hoses, tillers."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.resolution_u = resolution
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for p, co in zip(sp.points, points):
        p.co = (*co, 1.0)
    sp.use_cyclic_u = closed
    tmp = bpy.data.objects.new(name + "_c", cu)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return _finish(ob, material, 0, parent)


def wheel(name, radius, width, loc, rim="paint", parent=None, tread=False):
    """A complete wheel with its axle along X, centred on loc (so loc Z should equal radius to sit on the floor).
    Returns the tyre object; rim, hub and nuts are parented to it."""
    r, w = radius, width
    prof = [(0.60 * r, -0.50 * w), (0.86 * r, -0.50 * w), (0.95 * r, -0.44 * w), (0.99 * r, -0.34 * w), (r, -0.2 * w),
            (r, 0.2 * w), (0.99 * r, 0.34 * w), (0.95 * r, 0.44 * w), (0.86 * r, 0.50 * w), (0.60 * r, 0.50 * w)]
    t = lathe(name, prof, loc, "rubber", axis='X', parent=parent, steps=48)
    if tread:
        n = max(14, int(2 * math.pi * r / 0.11))
        for i in range(n):
            a = 2 * math.pi * i / n
            for sx in (-1, 1):
                b = box(f"{name}_tr", (0.36 * w, 0.045 * r + 0.012, 0.05), (0, 0, 0), "rubber", bevel=0.004, parent=t, segments=1)
                b.location = (math.cos(a) * 0.985 * r, math.sin(a) * 0.985 * r, sx * 0.24 * w)
                b.rotation_euler = (0, 0, a + (0.35 * sx))
                b.scale = (0.45, 1.0, 1.0)
    rimp = [(0.0, -0.30 * w), (0.22 * r, -0.30 * w), (0.26 * r, -0.36 * w), (0.50 * r, -0.36 * w), (0.58 * r, -0.44 * w), (0.615 * r, -0.44 * w),
            (0.615 * r, 0.44 * w), (0.58 * r, 0.44 * w), (0.50 * r, 0.36 * w), (0.26 * r, 0.36 * w), (0.22 * r, 0.30 * w), (0.0, 0.30 * w)]
    lathe(name + "_rim", rimp, (0, 0, 0), rim, axis='Z', parent=t, steps=40)
    for sx in (-1, 1):
        cyl(name + "_hub", 0.17 * r, 0.06 * w, (0, 0, sx * 0.38 * w), "chassis", parent=t, bevel=0.004)
        for k in range(6):
            a = k * math.pi / 3
            cyl(name + "_nut", 0.035 * r + 0.004, 0.05 * w, (math.cos(a) * 0.37 * r, math.sin(a) * 0.37 * r, sx * 0.375 * w), "steel", parent=t, verts=6)
    return t


def pallet(name, loc, parent=None, load=True, rot=(0, 0, 0)):
    """A 1.2 x 1.0 m timber pallet (1.2 across X), optionally loaded with four taped cartons and a magenta strap.
    loc is the centre of the pallet's underside. Returns an empty that everything is parented to."""
    p = empty(name, loc, parent, rot)
    for k in range(5):
        box(name + "_top", (1.2, 0.145, 0.022), (0, -0.4275 + k * 0.21375, 0.133), "wood", 0.003, p, segments=1)
    for x in (-0.55, 0, 0.55):
        box(name + "_run", (0.1, 1.0, 0.022), (x, 0, 0.111), "wood", 0.003, p, segments=1)
        for y in (-0.4275, 0, 0.4275):
            box(name + "_blk", (0.1, 0.145, 0.078), (x, y, 0.061), "wood", 0.003, p, segments=1)
        box(name + "_bot", (0.1, 1.0, 0.022), (x, 0, 0.011), "wood", 0.003, p, segments=1)
    if load:
        for row in range(2):
            for sx in (-1, 1):
                z = 0.144 + 0.2 + row * 0.405
                box(name + "_carton", (0.56, 0.9, 0.4), (sx * 0.285, 0, z), "card" if (row + sx) % 2 else "card2", 0.008, p, segments=2)
                box(name + "_tape", (0.07, 0.902, 0.003), (sx * 0.285, 0, z + 0.2), "tape", 0, p)
        box(name + "_strap", (1.15, 0.905, 0.035), (0, 0, 0.55), "accent", 0.003, p, segments=1)
    return p


def fork_tine(name, loc, parent=None, length=1.1, height=0.55, width=0.1):
    """One L-shaped forged steel fork. loc = the heel (bottom back corner); the tine points forward (-Y) and tapers to the tip."""
    pts = [(0, 0), (-length, 0), (-length, 0.012), (-length + 0.22, 0.04), (-0.05, 0.045), (-0.05, height), (0, height)]
    return profile(name, pts, width, loc, "steel", bevel=0.006, parent=parent, plane='YZ', segments=2)


def key(obj, frame, loc=None, rot=None, scale=None):
    """Keyframe an object's local transform. Use frame FRAME_REST (0) and FRAME_WORK (24)."""
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def stats():
    dg = bpy.context.evaluated_depsgraph_get()
    tris = 0
    for o in bpy.context.scene.objects:
        if o.type == 'MESH':
            me = o.evaluated_get(dg).to_mesh()
            me.calc_loop_triangles()
            tris += len(me.loop_triangles)
    return tris


def _merge():
    """Bake modifiers, then join meshes that share a parent (and are not animated or parents themselves)
    so the file has few objects. Called by export(); models do not need to call it."""
    sc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    meshes = [o for o in sc.objects if o.type == 'MESH']
    for o in meshes:
        if o.modifiers:
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
            o.modifiers.clear()
            o.data = me
    has_kids = {o.parent for o in sc.objects if o.parent is not None}
    groups = {}
    for o in meshes:
        if o in has_kids or o.animation_data is not None:
            continue
        groups.setdefault(o.parent, []).append(o)
    for parent, objs in groups.items():
        if len(objs) < 2:
            continue
        for o in sc.objects:
            o.select_set(False)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        with bpy.context.temp_override(active_object=objs[0], selected_objects=objs, selected_editable_objects=objs):
            bpy.ops.object.join()


def export(path):
    """Write the scene to a .glb with modifiers applied and the rest->work animation baked in."""
    sc = bpy.context.scene
    sc.frame_set(FRAME_REST)
    _merge()
    for o in sc.objects:
        o.select_set(True)
    kw = dict(filepath=path, export_format='GLB', export_apply=True, export_yup=True, export_animations=True,
              export_frame_range=True, export_force_sampling=True, export_materials='EXPORT', export_cameras=False, export_lights=False)
    try:
        bpy.ops.export_scene.gltf(export_animation_mode='SCENE', **kw)
    except TypeError:
        bpy.ops.export_scene.gltf(**kw)
    import os
    print(f"EXPORTED {path}: {os.path.getsize(path) / 1024:.0f} KB, {stats()} triangles, {len(sc.objects)} objects")
