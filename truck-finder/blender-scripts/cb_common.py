"""Shared parts for counter.py (counterbalance) and pivot.py (pivot steer): the rear half of a
sit-down truck (counterweight, hood, seat, guard, cowl, steering) and the two-stage mast with carriage.
All functions build in the LOCAL coordinates of `parent` (None = world), -Y forward."""
import math
import bpy, bmesh
from mathutils import Vector
import nctlib
from nctlib import *


# ----------------------------------------------------------------------------- generic helpers
def rod(name, p0, p1, r, material, parent=None, verts=20, r2=None):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    o = cyl(name, r, d.length, (a + b) / 2, material, parent=parent, verts=verts, radius2=r2)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def bar(name, p0, p1, w, h, material, bevel=0.006, parent=None, segments=2):
    """Rectangular bar (w across X-ish, h thick) from p0 to p1."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    o = box(name, (w, h, d.length), (a + b) / 2, material, bevel=bevel, parent=parent, segments=segments)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def fillet_path(pts, r=0.1, n=6):
    """Round the corners of a 3D polyline."""
    P = [Vector(p) for p in pts]
    out = [tuple(P[0])]
    for i in range(1, len(P) - 1):
        u = (P[i - 1] - P[i]); v = (P[i + 1] - P[i])
        lu, lv = u.length, v.length
        u.normalize(); v.normalize()
        phi = u.angle(v)
        if phi > math.radians(175):
            out.append(tuple(P[i])); continue
        t = min(r / math.tan(phi / 2), lu * 0.45, lv * 0.45)
        rr = t * math.tan(phi / 2)
        c = P[i] + (u + v).normalized() * (rr / math.sin(phi / 2))
        a0 = (P[i] + u * t - c).normalized(); a1 = (P[i] + v * t - c).normalized()
        for k in range(n + 1):
            out.append(tuple(c + a0.slerp(a1, k / n) * rr))
    out.append(tuple(P[-1]))
    return out


def loft(name, rings, material, parent=None, loc=(0, 0, 0)):
    """Skin a list of rings (each a list of (x,y,z), same count) and cap both ends."""
    bm = bmesh.new()
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(vr[0])
    for a, b in zip(vr[:-1], vr[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(vr[0]); bm.faces.new(vr[-1])
    return nctlib._finish(nctlib._new_obj(name, bm, loc), material, 0, parent)


def bake(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    obj.modifiers.clear()
    obj.data = me


def cut(targets, cutters, resharp=()):
    """Boolean-subtract cutters from targets (before their bevel), bake, and delete the cutters."""
    for t in targets:
        for c in cutters:
            m = t.modifiers.new("cut", 'BOOLEAN')
            m.operation = 'DIFFERENCE'; m.object = c; m.solver = 'EXACT'
            t.modifiers.move(len(t.modifiers) - 1, 0)
    bpy.context.view_layer.update()
    for t in targets:
        bake(t)
        if t in resharp:
            t.data.polygons.foreach_set("use_smooth", [True] * len(t.data.polygons))
            t.data.set_sharp_from_angle(angle=math.radians(40))
    for c in cutters:
        bpy.data.objects.remove(c)


def ring_xy(cx, cy, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def lamp_unit(name, loc, parent=None, face=-1, r=0.05):
    """Round work light facing -Y (face=-1) or +Y."""
    cyl(name + "_h", r, 0.07, loc, "plastic", axis='Y', bevel=0.012, parent=parent, verts=24)
    cyl(name + "_l", r * 0.8, 0.012, (loc[0], loc[1] + face * 0.036, loc[2]), "lamp", axis='Y', parent=parent, verts=24)


# ----------------------------------------------------------------------------- counterweight
def cw_outline(y0, yr, hw, rc, z, n=8):
    rc = max(rc, 0.02)
    pts = [(-hw, y0, z)]
    pts += [(x, y, z) for x, y in arc_pts(-hw + rc, yr - rc, rc, 180, 90, n)]
    pts += [(x, y, z) for x, y in arc_pts(hw - rc, yr - rc, rc, 90, 0, n)]
    pts += [(hw, y0, z)]
    return pts


def cw_rear_y(y1, z, zb, zt):
    """Side-view curve of the counterweight's rear face (bulges out mid-height, leans in at the top)."""
    t = (z - (zb + 0.42 * (zt - zb))) / (zt - zb)
    return y1 - 0.26 * t * t - 0.04 * max(0.0, t)


def counterweight(parent, y0=0.88, y1=1.58, zb=0.24, zt=1.08, hw=0.58, rc=0.30, axle_y=1.15, axle_z=0.25, arch_r=0.30,
                  arch_x=0.36, also_cut=()):
    """Cast counterweight: rounded in plan, curved in side view, wheel arches and tow-pin pocket cut in."""
    rings = []
    R = 0.07
    levels = []
    for k in range(4):   # bottom fillet
        a = math.radians(90 * k / 3)
        levels.append((zb + 0.05 * (1 - math.sin(a)) if False else zb + 0.05 * (1 - math.cos(a)), 0.05 * (1 - math.sin(a))))
    nz = 12
    for k in range(1, nz):
        levels.append((zb + 0.05 + (zt - R - zb - 0.05) * k / nz, 0.0))
    for k in range(6):   # top fillet
        a = math.radians(90 * k / 5)
        levels.append((zt - R + R * math.sin(a), R * (1 - math.cos(a))))
    for z, inset in levels:
        yr = cw_rear_y(y1, z, zb, zt) - inset
        rings.append(cw_outline(y0, yr, hw - inset, rc - inset * 0.5, z))
    cw = loft("counterweight", rings, "paint", parent)
    cutters = []
    for sx in (-1, 1):
        L = 0.5
        cutters.append(cyl("cut_arch", arch_r, L, (sx * (arch_x + L / 2), axle_y, axle_z), None, axis='X', parent=parent, verts=48))
        cutters.append(box("cut_arch2", (L, 2 * arch_r, 0.6), (sx * (arch_x + L / 2), axle_y, axle_z - 0.3), None, bevel=0, parent=parent))
    yb = cw_rear_y(y1, zb + 0.14, zb, zt)
    cutters.append(box("cut_tow", (0.26, 0.24, 0.13), (0, yb, zb + 0.15), None, bevel=0, parent=parent))
    cut([cw] + list(also_cut), cutters, resharp=(cw,))
    # tow pin in its pocket
    cyl("tow_pin", 0.018, 0.17, (0, yb - 0.05, zb + 0.15), "steel", parent=parent, verts=16)
    cyl("tow_pin_head", 0.03, 0.02, (0, yb - 0.05, zb + 0.225), "steel", parent=parent, verts=16, bevel=0.004)
    box("tow_back", (0.26, 0.02, 0.13), (0, yb - 0.115, zb + 0.15), "chassis", bevel=0, parent=parent)
    # hazard band wrapped round the lower edge
    band = []
    for z in (zb + 0.30, zb + 0.36):
        band.append(cw_outline(y0 + 0.02, cw_rear_y(y1, z, zb, zt) + 0.004, hw + 0.004, rc, z))
    hz = loft("cw_band", band, "hazard", parent)
    # tail lights (upright clusters near the corners) and a slatted grille set into the rear face
    zl = zt - 0.27
    yl = cw_rear_y(y1, zl, zb, zt)
    for sx in (-1, 1):
        box("tail_bez", (0.075, 0.05, 0.2), (sx * 0.235, yl - 0.012, zl), "plastic", bevel=0.012, parent=parent)
        box("tail", (0.05, 0.03, 0.10), (sx * 0.235, yl + 0.005, zl - 0.035), "tail", bevel=0.008, parent=parent)
        box("tail_ind", (0.05, 0.03, 0.05), (sx * 0.235, yl + 0.005, zl + 0.055), "beacon", bevel=0.008, parent=parent)
    box("grille_bg", (0.34, 0.05, 0.2), (0, yl - 0.014, zl), "chassis", bevel=0.012, parent=parent)
    for k in range(6):
        box("grille_slat", (0.31, 0.03, 0.012), (0, yl + 0.0, zl - 0.075 + k * 0.03), "plastic", bevel=0.003, parent=parent, segments=1)
    # lifting eye plug and cast recess on top
    cyl("cw_plug", 0.035, 0.012, (0, (y0 + y1) / 2 + 0.1, zt + 0.004), "chassis", parent=parent, verts=20, bevel=0.003)
    return cw


def rear_axle(parent, y=1.15, z=0.25, r=0.25, w=0.17, x=0.47, rim="rim"):
    """Steer axle beam with two wheels."""
    box("steer_axle", (2 * x - w, 0.12, 0.1), (0, y, z), "chassis", bevel=0.02, parent=parent)
    box("steer_axle_mid", (0.3, 0.2, 0.16), (0, y, z + 0.03), "chassis", bevel=0.03, parent=parent)
    for sx in (-1, 1):
        cyl("kingpin", 0.035, 0.2, (sx * (x - w / 2 - 0.04), y, z), "steel", parent=parent, verts=16)
        wheel("w_rear", r, w, (sx * x, y, z), rim=rim, parent=parent)


# ----------------------------------------------------------------------------- hood, sill, seat
def hood(parent, y0=0.20, y1=0.90, zs0=0.26, zs1=0.62, zt=0.98, hw=0.57):
    """Lower side sill (full width) with the stepped-in hood / seat deck on top. Returns the sill (for arch cuts)."""
    sill = profile("sill", [(y0, zs0), (y1, zs0), (y1, zs1), (y0, zs1)], 2 * hw, (0, 0, 0), "paint", bevel=0.025, parent=parent)
    hw2 = hw - 0.035
    hp = [(y0 + 0.02, zs1 - 0.02), (y1, zs1 - 0.02), (y1, zt)] + arc_pts(y0 + 0.16, zt - 0.10, 0.10, 90, 165, 6) + [(y0 + 0.02, zs1 + 0.1)]
    profile("hood", hp, 2 * hw2, (0, 0, 0), "paint", bevel=0.045, parent=parent, segments=4)
    for sx in (-1, 1):
        # seam between hood and sill, louvres, accent stripe, hood latch
        box("seam", (0.01, y1 - y0 - 0.06, 0.012), (sx * (hw2 + 0.001), (y0 + y1) / 2, zs1 + 0.012), "chassis", bevel=0, parent=parent)
        for k in range(5):
            box("louvre", (0.012, 0.2, 0.016), (sx * (hw2 + 0.001), y1 - 0.18, zs1 + 0.10 + k * 0.035), "chassis", bevel=0.003, parent=parent, segments=1)
        box("stripe", (0.008, y1 - y0 - 0.34, 0.022), (sx * (hw2 + 0.002), y0 + 0.2, zt - 0.1), "accent", bevel=0, parent=parent)
        box("latch", (0.02, 0.07, 0.03), (sx * (hw2 + 0.004), y0 + 0.12, zs1 + 0.06), "steel", bevel=0.006, parent=parent)
    box("plate", (0.006, 0.14, 0.09), (-(hw + 0.001), y0 + 0.25, (zs0 + zs1) / 2 + 0.02), "decal", bevel=0, parent=parent)
    # hood top seam (lift-up cover) and hinge line
    box("hood_seam", (2 * hw2 - 0.12, 0.012, 0.006), (0, y1 - 0.06, zt + 0.001), "chassis", bevel=0, parent=parent)
    return sill


def seat(parent, yc=0.55, z=0.98):
    """Shaped operator seat facing forwards (-Y); z = deck height."""
    box("seat_base", (0.40, 0.38, 0.07), (0, yc, z + 0.03), "plastic", bevel=0.015, parent=parent)
    for sx in (-1, 1):
        box("seat_rail", (0.03, 0.44, 0.025), (sx * 0.16, yc, z + 0.012), "steel", bevel=0.004, parent=parent, segments=1)
    cush = [(-0.26, 0.02)] + arc_pts(-0.21, 0.07, 0.055, 180, 90, 5) + [(0.0, 0.105), (0.22, 0.10), (0.24, 0.0), (-0.2, -0.01)]
    profile("seat_cushion", cush, 0.40, (0, yc, z + 0.07), "vinyl", bevel=0.03, parent=parent, segments=3)
    back = [(0.0, 0.0), (0.09, 0.0), (0.105, 0.3)] + arc_pts(0.07, 0.52, 0.04, 0, 90, 4) + arc_pts(0.035, 0.53, 0.03, 90, 180, 4) + [(-0.02, 0.3)]
    b = profile("seat_back", back, 0.40, (0, yc + 0.17, z + 0.15), "vinyl", bevel=0.03, parent=parent, segments=3)
    b.rotation_euler = (math.radians(-13), 0, 0)
    for sx in (-1, 1):   # side bolsters
        box("bolster", (0.07, 0.40, 0.09), (sx * 0.20, yc - 0.02, z + 0.135), "vinyl", bevel=0.03, parent=parent)
        bb = box("bolster_b", (0.07, 0.09, 0.42), (sx * 0.20, yc + 0.275, z + 0.42), "vinyl", bevel=0.03, parent=parent)
        bb.rotation_euler = (math.radians(-13), 0, 0)
    hr = box("headrest", (0.24, 0.07, 0.15), (0, yc + 0.375, z + 0.78), "vinyl", bevel=0.03, parent=parent)
    hr.rotation_euler = (math.radians(-13), 0, 0)
    rod("headrest_post", (0.06, yc + 0.34, z + 0.64), (0.06, yc + 0.365, z + 0.74), 0.008, "steel", parent)
    rod("headrest_post", (-0.06, yc + 0.34, z + 0.64), (-0.06, yc + 0.365, z + 0.74), 0.008, "steel", parent)
    # armrest (right) and belt buckle (left)
    box("armrest", (0.065, 0.30, 0.045), (0.265, yc + 0.03, z + 0.36), "vinyl", bevel=0.018, parent=parent)
    rod("arm_sup", (0.265, yc + 0.2, z + 0.15), (0.265, yc + 0.15, z + 0.35), 0.015, "steel", parent)
    box("buckle", (0.03, 0.05, 0.09), (-0.245, yc + 0.12, z + 0.17), "accent", bevel=0.008, parent=parent)


# ----------------------------------------------------------------------------- cowl, steering, controls
def cowl(parent, yf=-0.60, zf=0.50, hw=0.27):
    """Front cowl / dash with steering column and wheel, levers, display, pedals. yf = front face."""
    cp = [(yf, zf - 0.1), (yf + 0.22, zf - 0.1), (yf + 0.22, zf + 0.34), (yf + 0.15, zf + 0.50)] + arc_pts(yf + 0.07, zf + 0.47, 0.05, 80, 180, 5)
    profile("cowl", cp, 2 * hw, (0, 0, 0), "paint", bevel=0.03, parent=parent, segments=3)
    # dash panel on the sloped face
    d = box("dash", (2 * hw - 0.08, 0.015, 0.15), (0, yf + 0.19, zf + 0.42), "plastic", bevel=0.005, parent=parent)
    d.rotation_euler = (math.radians(-24), 0, 0)
    ds = box("display", (0.13, 0.03, 0.085), (-0.14, yf + 0.14, zf + 0.57), "plastic", bevel=0.01, parent=parent)
    ds.rotation_euler = (math.radians(-24), 0, 0)
    sc = box("screen", (0.105, 0.006, 0.06), (-0.14, yf + 0.157, zf + 0.563), "glass", bevel=0, parent=parent)
    sc.rotation_euler = (math.radians(-24), 0, 0)
    cyl("key_sw", 0.012, 0.02, (0.17, yf + 0.2, zf + 0.44), "accent", axis='Y', parent=parent, verts=12)
    # steering column and wheel
    c0 = Vector((0, yf + 0.13, zf + 0.47)); c1 = Vector((0, yf + 0.33, zf + 0.72))
    rod("steer_col", c0, c1, 0.032, "plastic", parent)
    rod("steer_col2", c0 + (c1 - c0) * 0.9, c1 + (c1 - c0) * 0.06, 0.045, "plastic", parent)
    dvec = (c1 - c0).normalized()
    wc = c1 + dvec * 0.03
    e1 = Vector((1, 0, 0)); e2 = dvec.cross(e1).normalized()
    rw = 0.165
    ringp = [tuple(wc + (e1 * math.cos(a) + e2 * math.sin(a)) * rw) for a in [2 * math.pi * i / 36 for i in range(36)]]
    tube("steer_wheel", ringp, 0.016, "vinyl", parent, closed=True, resolution=2)
    for a in (90, 210, 330):
        v = (e1 * math.cos(math.radians(a)) + e2 * math.sin(math.radians(a)))
        rod("steer_spoke", wc - dvec * 0.02, wc + v * rw, 0.011, "plastic", parent, verts=10)
    rod("steer_hub", wc - dvec * 0.03, wc + dvec * 0.012, 0.045, "plastic", parent)
    kn = wc + (e1 * math.cos(math.radians(150)) + e2 * math.sin(math.radians(150))) * rw
    rod("steer_knob", kn, kn + dvec * 0.06, 0.02, "vinyl", parent, verts=14)
    # direction stalk
    rod("stalk", c0 + (c1 - c0) * 0.75, c0 + (c1 - c0) * 0.75 + Vector((-0.13, 0, 0.02)), 0.008, "plastic", parent, verts=10)
    # hydraulic levers (right of the wheel)
    for k, x in enumerate((0.15, 0.19, 0.23)):
        p0 = (x, yf + 0.10, zf + 0.5); p1 = (x, yf + 0.18, zf + 0.66)
        rod("lever", p0, p1, 0.007, "steel", parent, verts=10)
        cyl("lever_knob", 0.018, 0.035, p1, "accent" if k == 0 else "vinyl", parent=parent, verts=14, bevel=0.006)
    box("lever_boot", (0.14, 0.07, 0.03), (0.19, yf + 0.10, zf + 0.5), "rubber", bevel=0.012, parent=parent)
    # parking brake lever (left)
    rod("pbrake", (-0.2, yf + 0.2, zf + 0.3), (-0.2, yf + 0.3, zf + 0.42), 0.01, "steel", parent, verts=10)
    rod("pbrake_grip", (-0.2, yf + 0.28, zf + 0.4), (-0.2, yf + 0.33, zf + 0.46), 0.017, "vinyl", parent, verts=12)
    # pedals
    for x, w in ((0.14, 0.07), (0.02, 0.1)):
        p = box("pedal", (w, 0.012, 0.11), (x, yf + 0.29, zf + 0.07), "rubber", bevel=0.004, parent=parent, segments=1)
        p.rotation_euler = (math.radians(-50), 0, 0)
        rod("pedal_arm", (x, yf + 0.22, zf + 0.02), (x, yf + 0.285, zf + 0.06), 0.008, "steel", parent, verts=8)


# ----------------------------------------------------------------------------- overhead guard
def guard(parent, front_foot=(0.475, -0.62, 0.72), front_knee=None, roof_front=(0.50, -0.25), roof_rear_y=0.93, roof_z=2.12,
          rear_foot=(0.50, 1.0, 1.06), rt=0.027):
    """Four-leg overhead guard from bent tube, with roof bars, lights, beacon, mirror and grab handle."""
    xr, yrf = roof_front
    for sx in (-1, 1):
        pts = [(sx * front_foot[0], front_foot[1], front_foot[2])]
        if front_knee:
            pts.append((sx * front_knee[0], front_knee[1], front_knee[2]))
        pts += [(sx * xr, yrf, roof_z), (sx * xr, roof_rear_y, roof_z), (sx * rear_foot[0], rear_foot[1], rear_foot[2])]
        tube("guard_side", fillet_path(pts, 0.11, 7), rt, "mast", parent)
        # feet plates
        box("guard_foot", (0.09, 0.11, 0.02), (sx * front_foot[0], front_foot[1], front_foot[2] + 0.008), "mast", bevel=0.005, parent=parent, segments=1)
        box("guard_foot", (0.09, 0.11, 0.02), (sx * rear_foot[0], rear_foot[1], rear_foot[2] + 0.008), "mast", bevel=0.005, parent=parent, segments=1)
    # cross tubes
    for y in (yrf + 0.1, roof_rear_y - 0.1):
        rod("guard_cross", (-xr, y, roof_z), (xr, y, roof_z), rt, "mast", parent)
    # roof bars (flat, fore-aft, as on most cast/pressed guards)
    n = 7
    for i in range(n):
        x = -xr + 2 * xr * (i + 1) / (n + 1)
        box("roof_bar", (0.035, roof_rear_y - yrf - 0.2, 0.022), (x, (yrf + roof_rear_y) / 2, roof_z + 0.005), "mast", bevel=0.005, parent=parent, segments=1)
    box("roof_mid", (2 * xr, 0.04, 0.02), (0, (yrf + roof_rear_y) / 2, roof_z - 0.012), "mast", bevel=0.005, parent=parent, segments=1)
    # work lights on the front legs, beacon at the back, mirror
    f = Vector((front_knee if front_knee else front_foot)); r = Vector((xr, yrf, roof_z))
    lp = f + (r - f) * 0.86
    for sx in (-1, 1):
        lamp_unit("worklight", (sx * (lp.x + 0.075), lp.y - 0.02, lp.z), parent)
        box("light_brk", (0.06, 0.02, 0.02), (sx * (lp.x + 0.035), lp.y, lp.z), "mast", bevel=0.004, parent=parent, segments=1)
    by = roof_rear_y - 0.1
    cyl("beacon_base", 0.045, 0.03, (xr - 0.12, by, roof_z + 0.04), "plastic", parent=parent, verts=20)
    lathe("beacon", [(0.0, 0.0), (0.04, 0.0), (0.04, 0.06), (0.03, 0.085), (0.0, 0.092)], (xr - 0.12, by, roof_z + 0.055), "beacon", axis='Z', parent=parent, steps=20)
    lamp_unit("rearlight", (-(xr - 0.12), roof_rear_y + 0.005, roof_z - 0.07), parent, face=1, r=0.04)
    mp = f + (r - f) * 0.62
    rod("mirror_arm", (-mp.x, mp.y, mp.z), (-(mp.x + 0.11), mp.y - 0.03, mp.z + 0.03), 0.008, "mast", parent, verts=8)
    box("mirror", (0.11, 0.02, 0.17), (-(mp.x + 0.13), mp.y - 0.03, mp.z + 0.03), "plastic", bevel=0.012, parent=parent)
    box("mirror_gl", (0.09, 0.004, 0.15), (-(mp.x + 0.13), mp.y - 0.018, mp.z + 0.03), "chrome", bevel=0, parent=parent)
    # grab handle on the left front leg
    gp = f + (r - f) * 0.30; gq = f + (r - f) * 0.52
    tube("grab", fillet_path([(-gp.x, gp.y, gp.z), (-gp.x, gp.y + 0.07, gp.z + 0.01), (-gq.x, gq.y + 0.07, gq.z - 0.01), (-gq.x, gq.y, gq.z)], 0.03, 4), 0.012, "steel", parent)


# ----------------------------------------------------------------------------- mast + carriage
def mast(parent, yc=-0.73, zb=0.12, top=2.13, lift=1.55, xr=0.315, fork_z=0.03, fork_len=1.1, fork_x=0.28, load=True):
    """Two-stage mast. Outer stage is parented to `parent` (static relative to it); returns (inner, carriage) empties.
    inner rises lift/2, carriage rises a further lift/2 relative to inner (so the forks rise `lift`).
    yc = Y of the rail centres; rails are 0.12 deep."""
    H = top - zb
    zc = zb + H / 2
    # --- outer stage: C channels opening inwards
    for sx in (-1, 1):
        cs = [(-0.035, -0.06), (0.035, -0.06), (0.035, -0.042), (-0.017, -0.042), (-0.017, 0.042), (0.035, 0.042), (0.035, 0.06), (-0.035, 0.06)]
        cs = [(-sx * a, b) for a, b in cs]
        profile("mast_outer", cs, H, (sx * xr, yc, zc), "mast", bevel=0.004, parent=parent, plane='XY', segments=1)
        box("mast_foot", (0.09, 0.16, 0.14), (sx * xr, yc + 0.02, zb + 0.07), "chassis", bevel=0.02, parent=parent)
        box("tilt_lug", (0.03, 0.07, 0.09), (sx * (xr + 0.045), yc + 0.055, zb + 0.74), "chassis", bevel=0.01, parent=parent)
    yb = yc + 0.07   # rear tie bars (behind the rails)
    for z, h in ((zb + 0.10, 0.14), (zb + 0.98, 0.09), (top - 0.07, 0.10)):
        box("mast_tie", (2 * xr + 0.07, 0.03, h), (0, yb, z), "mast", bevel=0.008, parent=parent)
    # lift cylinder barrel (fixed), behind the inner stage
    ycyl = yc + 0.04
    cyl("lift_barrel", 0.045, 1.36, (0, ycyl, zb + 0.02 + 0.68), "mast", parent=parent, verts=24)
    cyl("lift_gland", 0.052, 0.05, (0, ycyl, zb + 1.38), "steel", parent=parent, verts=24, bevel=0.006)
    box("lift_base", (0.2, 0.09, 0.05), (0, ycyl + 0.01, zb + 0.045), "chassis", bevel=0.01, parent=parent)
    box("chain_anchor", (0.3, 0.035, 0.04), (0, yc + 0.035, zb + 1.16), "chassis", bevel=0.008, parent=parent)
    # hoses from the chassis up the mast (static)
    for i, x in enumerate((-0.07, 0.07)):
        tube("mast_hose", fillet_path([(x, yb + 0.12, zb + 0.42), (x, yb + 0.035, zb + 0.42), (x, yb + 0.035, zb + 0.2), (x * 0.6, ycyl + 0.03, zb + 0.1)], 0.04, 4), 0.011, "rubber", parent)

    # --- inner stage (moves)
    inner = empty("mast_inner", (0, 0, 0), parent)
    xi = xr - 0.063
    Hi = H + 0.02
    for sx in (-1, 1):
        isec = [(-0.024, -0.05), (0.024, -0.05), (0.024, -0.036), (0.008, -0.036), (0.008, 0.036), (0.024, 0.036), (0.024, 0.05), (-0.024, 0.05), (-0.024, 0.036), (-0.008, 0.036), (-0.008, -0.036), (-0.024, -0.036)]
        profile("mast_inner_rail", isec, Hi, (sx * xi, yc, zb + 0.04 + Hi / 2), "mast", bevel=0.003, parent=inner, plane='XY', segments=1)
    ztop = zb + 0.04 + Hi
    box("inner_top", (2 * xi + 0.05, 0.11, 0.06), (0, yc, ztop - 0.03), "mast", bevel=0.01, parent=inner)
    box("inner_bot", (2 * xi, 0.03, 0.07), (0, yc - 0.035, zb + 0.085), "mast", bevel=0.008, parent=inner)
    box("inner_mid", (2 * xi, 0.025, 0.06), (0, yc - 0.04, zb + 1.25), "mast", bevel=0.008, parent=inner)
    # chrome rod: hidden in the barrel at rest, exposed as the stage rises
    cyl("lift_rod", 0.026, 1.38, (0, ycyl, ztop - 0.06 - 0.69), "chrome", parent=inner, verts=20)
    # chain pulleys under the top cross-member
    zp = ztop - 0.115; rp = 0.042
    chains = []
    for sx in (-1, 1):
        x = sx * 0.11
        cyl("pulley", rp, 0.035, (x, yc, zp), "steel", axis='X', parent=inner, verts=24, bevel=0.004)
        cyl("pulley_fl", rp + 0.012, 0.006, (x - 0.02, yc, zp), "chassis", axis='X', parent=inner, verts=24)
        cyl("pulley_fl", rp + 0.012, 0.006, (x + 0.02, yc, zp), "chassis", axis='X', parent=inner, verts=24)
        box("pulley_brk", (0.012, 0.05, 0.1), (x + sx * 0.03, yc, zp + 0.035), "mast", bevel=0.004, parent=inner, segments=1)
        # chain over the pulley (half ring)
        tube("chain_top", [(x, yc + (rp + 0.005) * math.cos(a), zp + (rp + 0.005) * math.sin(a)) for a in [math.pi * i / 10 for i in range(11)]], 0.009, "steel", inner, resolution=1)
        # front run (to carriage) and rear run (to fixed anchor): stretched by keyed scale
        Lf = zp - (fork_z + 0.50)
        ef = empty("chain_front_%d" % sx, (x, yc - rp - 0.005, zp), inner)
        box("chain_f", (0.028, 0.012, Lf), (0, 0, -Lf / 2), "steel", bevel=0, parent=ef)
        key(ef, FRAME_REST, scale=(1, 1, 1)); key(ef, FRAME_WORK, scale=(1, 1, (Lf - lift / 2) / Lf))
        Lr = zp - (zb + 1.17)
        er = empty("chain_rear_%d" % sx, (x, yc + rp + 0.005, zp), inner)
        box("chain_r", (0.028, 0.012, Lr), (0, 0, -Lr / 2), "steel", bevel=0, parent=er)
        key(er, FRAME_REST, scale=(1, 1, 1)); key(er, FRAME_WORK, scale=(1, 1, (Lr + lift / 2) / Lr))
    key(inner, FRAME_REST, loc=(0, 0, 0)); key(inner, FRAME_WORK, loc=(0, 0, lift / 2))

    # --- carriage (moves relative to inner); origin = fork heel line at floor side
    cy = yc - 0.125
    car = empty("carriage", (0, cy, fork_z), inner)
    cwid = 0.96
    box("car_bar_lo", (cwid, 0.04, 0.12), (0, 0.02, 0.13), "chassis", bevel=0.008, parent=car)
    box("car_bar_hi", (cwid, 0.04, 0.12), (0, 0.02, 0.45), "chassis", bevel=0.008, parent=car)
    box("car_lip", (cwid, 0.02, 0.025), (0, -0.008, 0.50), "steel", bevel=0.004, parent=car, segments=1)
    for sx in (-1, 1):
        box("car_side", (0.03, 0.04, 0.40), (sx * (cwid / 2 - 0.03), 0.02, 0.29), "chassis", bevel=0.006, parent=car)
        box("car_plate", (0.022, 0.075, 0.36), (sx * (xi - 0.045), 0.075, 0.40), "chassis", bevel=0.006, parent=car)
        for z in (0.26, 0.54):
            cyl("car_roller", 0.04, 0.03, (sx * (xi - 0.018), 0.125, z), "steel", axis='X', parent=car, verts=20, bevel=0.004)
        box("chain_lug", (0.05, 0.05, 0.04), (sx * 0.11, 0.06, 0.49), "chassis", bevel=0.006, parent=car, segments=1)
    box("car_web", (2 * xi - 0.08, 0.02, 0.2), (0, 0.05, 0.36), "chassis", bevel=0.005, parent=car, segments=1)
    # load backrest
    bw = 1.04; bt = 1.24
    for sx in (-1, 1):
        box("lbr_side", (0.04, 0.03, bt - 0.5), (sx * (bw / 2 - 0.02), 0.015, (bt + 0.5) / 2), "chassis", bevel=0.006, parent=car, segments=1)
    box("lbr_top", (bw, 0.03, 0.04), (0, 0.015, bt - 0.02), "chassis", bevel=0.006, parent=car, segments=1)
    box("lbr_mid", (bw, 0.025, 0.03), (0, 0.015, 0.87), "chassis", bevel=0.005, parent=car, segments=1)
    for i in range(1, 8):
        x = -bw / 2 + bw * i / 8
        box("lbr_bar", (0.02, 0.018, bt - 0.52), (x, 0.015, (bt + 0.5) / 2), "chassis", bevel=0.004, parent=car, segments=1)
    # forks hooked on the carriage, pallet on the tines
    for sx in (-1, 1):
        fork_tine("tine", (sx * fork_x, 0, 0), car, length=fork_len, height=0.52)
        box("tine_hook", (0.1, 0.07, 0.035), (sx * fork_x, 0.0, 0.535), "steel", bevel=0.006, parent=car, segments=1)
        box("tine_hook2", (0.1, 0.035, 0.03), (sx * fork_x, 0.0, 0.085), "steel", bevel=0.005, parent=car, segments=1)
    if load:
        pallet("pallet", (0, -0.06 - 0.5, 0.047), car)
    key(car, FRAME_REST, loc=(0, cy, fork_z)); key(car, FRAME_WORK, loc=(0, cy, fork_z + lift / 2))
    return inner, car


def tilt_cylinder(parent, p_rear, p_mast, r=0.034):
    """Tilt cylinder from a chassis bracket (p_rear) to the mast lug (p_mast)."""
    a, b = Vector(p_rear), Vector(p_mast)
    d = b - a
    mid = a + d * 0.6
    rod("tilt_barrel", a, mid, r, "chassis", parent, verts=20)
    rod("tilt_gland", mid - d.normalized() * 0.03, mid, r + 0.006, "steel", parent, verts=20)
    rod("tilt_rod", mid, b, r * 0.5, "chrome", parent, verts=16)
    cyl("tilt_eye", r * 0.9, 0.05, tuple(b), "steel", axis='X', parent=parent, verts=16)
    cyl("tilt_eye", r * 1.1, 0.06, tuple(a), "chassis", axis='X', parent=parent, verts=16)
