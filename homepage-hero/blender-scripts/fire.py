"""Homepage hero scene: free-standing workplace FIRE POINT (key `fire`).
Double extinguisher stand with back panel, call point, sign, sounder, fire blanket, a water/foam and a CO2 extinguisher.
Motion: the CO2 extinguisher lifts out of the stand, comes forward and tilts, its horn swings up ready to use."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import FRAMES, ring, bar3d
reset()
R = math.radians

# ------------------------------------------------------------------ helpers (local to this script)
def smooth_path(pts, n=8):
    """Catmull-Rom through 3D points so hoses bend smoothly."""
    P = [Vector(p) for p in pts]
    P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(P[-2]))
    return out


def hose(name, pts, r, material, parent=None):
    return tube(name, smooth_path(pts), r, material, parent=parent, resolution=1)


def curved_panel(name, r, z0, z1, a_mid, a_width, material, parent=None, thick=0.003, proud=0.0015, n=14):
    """A label wrapped round a cylinder of radius r (angles in degrees, anticlockwise from local +X)."""
    a0, a1 = a_mid - a_width / 2, a_mid + a_width / 2
    pts = arc_pts(0, 0, r + proud, a0, a1, n) + arc_pts(0, 0, r + proud - thick, a1, a0, n)
    return profile(name, pts, z1 - z0, (0, 0, (z0 + z1) / 2), material, bevel=0, parent=parent, plane='XY')


def band(name, r, z0, z1, material, parent=None, proud=0.0015):
    e = 0.0015
    return lathe(name, [(r - 0.002, z0), (r + proud, z0 + e), (r + proud, z1 - e), (r - 0.002, z1)], (0, 0, 0), material, axis='Z', parent=parent, steps=48)


def strip(name, pts, thick, width, loc, material, parent=None, bevel=0.002, plane='YZ'):
    """A bent flat bar: pts is the top edge polyline, the bar is `thick` deep below it."""
    low = []
    for i, (a, b) in enumerate(pts):
        a0, b0 = pts[max(i - 1, 0)]
        a1, b1 = pts[min(i + 1, len(pts) - 1)]
        d = math.hypot(a1 - a0, b1 - b0)
        nx, ny = (b1 - b0) / d, -(a1 - a0) / d
        low.append((a + nx * thick, b + ny * thick))
    return profile(name, list(pts) + low[::-1], width, loc, material, bevel=bevel, parent=parent, plane=plane, segments=2)


def cut(obj, cutters, bevel=0.0, segments=3):
    """Boolean-subtract the cutters from obj, bake it, delete the cutters, then (optionally) bevel the result."""
    for c in cutters:
        md = obj.modifiers.new("cut", 'BOOLEAN')
        md.operation = 'DIFFERENCE'
        md.object = c
        md.solver = 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg), depsgraph=dg)
    obj.modifiers.clear()
    obj.data = me
    for c in cutters:
        bpy.data.objects.remove(c)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    if bevel:
        md = obj.modifiers.new("Bevel", 'BEVEL')
        md.width, md.segments, md.limit_method, md.angle_limit, md.harden_normals = bevel, segments, 'ANGLE', R(35), True
    return obj


def rrect(w, h, r, n=6, cx=0.0, cy=0.0):
    x, y = w / 2 - r, h / 2 - r
    return (arc_pts(cx + x, cy + y, r, 0, 90, n) + arc_pts(cx - x, cy + y, r, 90, 180, n)
            + arc_pts(cx - x, cy - y, r, 180, 270, n) + arc_pts(cx + x, cy - y, r, 270, 360, n))


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ layout
BW, BD, BH = 0.80, 0.48, 0.12          # base tub
WELL = 0.05                            # depth of the wells
ZF = BH - WELL                         # well floor height
EX_Y = -0.055
WX, CX = -0.19, 0.19                   # water / CO2 extinguisher centres
WR, CR = 0.09, 0.07                    # body radii
PY, PT = 0.19, 0.026                   # panel centre Y and thickness
PF = PY - PT / 2                       # panel front face
PW = 0.64

# ================================================================== the stand
base = profile("base", rrect(BW, BD, 0.07, 8), BH - 0.012, (0, 0, 0.012 + (BH - 0.012) / 2), "red", bevel=0, plane='XY')
cutters = [cyl("cutw", WR + 0.009, 0.2, (WX, EX_Y, ZF + 0.1), None, verts=48),
           cyl("cutc", CR + 0.009, 0.2, (CX, EX_Y, ZF + 0.1), None, verts=48)]
cut(base, cutters, bevel=0.014, segments=4)
# raised moulded collars round each well and a centre rib
for x, r in ((WX, WR), (CX, CR)):
    lathe("collar", [(r + 0.010, BH - 0.004), (r + 0.010, BH + 0.012), (r + 0.014, BH + 0.016), (r + 0.026, BH + 0.016), (r + 0.034, BH + 0.008), (r + 0.038, BH - 0.004)],
          (x, EX_Y, 0), "red", axis='Z', steps=48)
    cyl("well_mat", r + 0.008, 0.004, (x, EX_Y, ZF + 0.002), "rubber", verts=40)
box("base_rib", (0.035, 0.30, 0.02), (0, EX_Y, BH + 0.004), "red", bevel=0.008)
for sx in (-1, 1):
    for sy in (-1, 1):
        box("foot", (0.12, 0.08, 0.02), (sx * 0.29, sy * 0.16, 0.01), "rubber", bevel=0.006)
    # ballast filler caps
    cyl("fill_boss", 0.032, 0.012, (sx * 0.335, 0.115, BH + 0.004), "red", bevel=0.004)
    cyl("fill_cap", 0.025, 0.016, (sx * 0.335, 0.115, BH + 0.016), "black", bevel=0.005, verts=12)
box("base_stripe", (0.50, 0.004, 0.022), (0, -BD / 2 - 0.0005, 0.05), "hazard", bevel=0)
for i in range(9):
    box("base_chev", (0.016, 0.005, 0.03), (-0.2 + i * 0.05, -BD / 2 - 0.001, 0.05), "black", bevel=0, rot=(0, R(35), 0))
for sx in (-1, 1):   # moulded hand grips in the ends of the base
    box("grip_recess", (0.006, 0.14, 0.035), (sx * (BW / 2 - 0.001), 0, 0.075), "black", bevel=0.002)

# back panel with a rounded head for the sounder
r_c, HT, HR, HZ = 0.045, 1.30, 0.075, 1.372
outline = ([(-PW / 2, 0.06), (PW / 2, 0.06)] + arc_pts(PW / 2 - r_c, HT - r_c, r_c, 0, 90, 6)
           + arc_pts(HR + 0.03, HT + 0.03, 0.03, 270, 180, 5) + arc_pts(0, HZ, HR, 0, 180, 16)
           + arc_pts(-HR - 0.03, HT + 0.03, 0.03, 360, 270, 5) + arc_pts(-PW / 2 + r_c, HT - r_c, r_c, 90, 180, 6))
profile("panel", outline, PT, (0, PY, 0), "red", bevel=0.007, plane='XZ')
# pale backing board behind the extinguishers so they read against the red stand
profile("backboard", rrect(PW - 0.07, 0.56, 0.03), 0.005, (0, PF - 0.0015, 0.475), "cream", bevel=0.0015, plane='XZ')
for sx in (-1, 1):
    for sz in (-1, 1):
        cyl("board_screw", 0.006, 0.004, (sx * (PW / 2 - 0.06), PF - 0.004, 0.475 + sz * 0.255), "steel", axis='Y', verts=10)
box("rear_plate", (0.16, 0.004, 0.11), (0, PY + PT / 2 + 0.001, 0.95), "white", bevel=0.001)
# socket moulding where the panel enters the base
box("panel_socket", (PW + 0.04, 0.07, 0.05), (0, PY, BH + 0.015), "red", bevel=0.014)
# tubular frame behind
TY = PY + PT / 2 + 0.017
for sx in (-1, 1):
    tube("post", [(sx * 0.25, TY, BH - 0.02), (sx * 0.25, TY, 1.16), (sx * 0.235, TY, 1.215), (sx * 0.18, TY, 1.24), (0, TY, 1.24)], 0.017, "red")
    cyl("post_flange", 0.034, 0.012, (sx * 0.25, TY, BH + 0.005), "red", bevel=0.004)
    profile("gusset", [(0, 0), (0.0, 0.24), (-0.012, 0.24), (-0.13, 0.012), (-0.13, 0)], 0.014, (sx * 0.295, PF + 0.002, BH - 0.002), "red", bevel=0.003)
for z in (0.42, 0.80, 1.10):
    box("rail", (0.52, 0.018, 0.04), (0, TY - 0.006, z), "red", bevel=0.006)
    for sx in (-1, 1):
        for dx in (0.08, 0.2):
            cyl("rail_bolt", 0.007, 0.006, (sx * dx, TY + 0.004, z), "steel", axis='Y', verts=6)

# ------------------------------------------------------------------ sounder / beacon on the head
lathe("sounder", [(0, 0), (0.064, 0), (0.064, 0.016), (0.058, 0.022), (0.058, 0.03), (0.055, 0.033), (0.055, 0.04), (0.058, 0.043), (0.058, 0.05),
                  (0.055, 0.053), (0.055, 0.06), (0.058, 0.063), (0.058, 0.074), (0.05, 0.082), (0, 0.082)], (0, PF, HZ), "red", axis='Y', steps=40)
for a in (0.0365, 0.0565):
    lathe("sounder_slot", [(0.0556, a - 0.0035), (0.0556, a + 0.0035)], (0, PF, HZ), "black", axis='Y', steps=40)
lathe("sounder_lens", [(0.046, 0.080)] + [(0.046 * math.cos(R(a)), 0.080 + 0.034 * math.sin(R(a))) for a in range(10, 91, 10)], (0, PF, HZ), "lamp", axis='Y', steps=32)
box("sounder_back", (0.10, 0.03, 0.10), (0, PY + PT / 2 + 0.012, HZ), "red", bevel=0.01)

# ------------------------------------------------------------------ manual call point (break glass)
MX, MZ = 0.19, 1.16
box("mcp_box", (0.092, 0.036, 0.092), (MX, PF - 0.018, MZ), "red", bevel=0.009)
box("mcp_bezel", (0.066, 0.004, 0.066), (MX, PF - 0.0365, MZ), "black", bevel=0.001)
box("mcp_glass", (0.058, 0.004, 0.058), (MX, PF - 0.038, MZ), "white", bevel=0.001)
cyl("mcp_dot", 0.0075, 0.003, (MX, PF - 0.0405, MZ), "black", axis='Y', verts=20)
for sx in (-1, 1):
    profile("mcp_arrow", [(sx * 0.013, 0), (sx * 0.023, 0.007), (sx * 0.023, -0.007)], 0.003, (MX, PF - 0.0405, MZ), "black", bevel=0, plane='XZ')
cyl("mcp_key", 0.005, 0.006, (MX, PF - 0.018, MZ - 0.047), "black", verts=12)
cyl("mcp_gland", 0.009, 0.014, (MX, PF - 0.012, MZ + 0.05), "black", verts=12)
hose("mcp_cable", [(MX, PF - 0.012, MZ + 0.05), (MX, PF - 0.008, MZ + 0.09), (MX - 0.02, PF - 0.008, MZ + 0.115), (0.07, PF - 0.008, MZ + 0.118),
                   (0.045, PF - 0.008, MZ + 0.14), (0.04, PF - 0.008, HZ - 0.055)], 0.005, "black")
for p in ((MX - 0.06, MZ + 0.117),):
    box("cable_clip", (0.02, 0.008, 0.016), (p[0], PF - 0.006, p[1]), "black", bevel=0.003)

# ------------------------------------------------------------------ sign plate: flame + extinguisher silhouettes, no lettering
SX, SZ, SW, SH = -0.125, 1.16, 0.30, 0.21
profile("sign_back", rrect(SW, SH, 0.014), 0.005, (SX, PF - 0.0025, SZ), "white", bevel=0.001, plane='XZ')
profile("sign_face", rrect(SW - 0.022, SH - 0.022, 0.008), 0.003, (SX, PF - 0.006, SZ), "red", bevel=0, plane='XZ')
for sx in (-1, 1):
    for sz in (-1, 1):
        cyl("sign_screw", 0.004, 0.003, (SX + sx * (SW / 2 - 0.006), PF - 0.0055, SZ + sz * (SH / 2 - 0.006)), "steel", axis='Y', verts=10)
s = 0.036
flame = [(-s, 0)] + arc_pts(0, 0, s, 180, 360, 12)[1:] + [(1.05 * s, 0.5 * s), (0.9 * s, 1.05 * s), (0.5 * s, 1.6 * s), (0.2 * s, 2.5 * s), (-0.1 * s, 1.9 * s),
                                                           (-0.32 * s, 1.35 * s), (-0.62 * s, 1.75 * s), (-0.8 * s, 1.2 * s), (-1.04 * s, 0.55 * s)]
profile("sign_flame", flame, 0.003, (SX - 0.07, PF - 0.0085, SZ - 0.035), "white", bevel=0, plane='XZ')
s2 = 0.017
flame2 = [(-s2, 0)] + arc_pts(0, 0, s2, 180, 360, 8)[1:] + [(0.95 * s2, 0.7 * s2), (0.45 * s2, 1.5 * s2), (0.1 * s2, 2.3 * s2), (-0.5 * s2, 1.3 * s2), (-0.98 * s2, 0.6 * s2)]
profile("sign_flame_in", flame2, 0.003, (SX - 0.068, PF - 0.0095, SZ - 0.045), "red", bevel=0, plane='XZ')
ex, ez = SX + 0.075, SZ - 0.012
body_o = [(-0.027, -0.058), (0.027, -0.058), (0.027, 0.03)] + arc_pts(0, 0.03, 0.027, 0, 180, 10)[1:]
profile("sign_ext", body_o, 0.003, (ex, PF - 0.0085, ez), "white", bevel=0, plane='XZ')
box("sign_neck", (0.016, 0.003, 0.014), (ex, PF - 0.0085, ez + 0.062), "white", bevel=0)
box("sign_lever", (0.05, 0.003, 0.009), (ex + 0.014, PF - 0.0085, ez + 0.078), "white", bevel=0, rot=(0, R(-12), 0))
strip("sign_hose", [(-0.006, 0.066), (-0.03, 0.064), (-0.043, 0.045), (-0.046, 0.0), (-0.046, -0.03)], 0.007, 0.003, (ex, PF - 0.0085, ez), "white", bevel=0, plane='XZ')

# ------------------------------------------------------------------ blank fire-action notice under the call point
NX, NZ = 0.19, 0.93
profile("notice", rrect(0.16, 0.21, 0.01), 0.004, (NX, PF - 0.002, NZ), "white", bevel=0.001, plane='XZ')
box("notice_head", (0.14, 0.002, 0.035), (NX, PF - 0.0045, NZ + 0.075), "red", bevel=0)
box("notice_green", (0.062, 0.002, 0.062), (NX - 0.036, PF - 0.0045, NZ - 0.045), "green", bevel=0)
profile("notice_arrow", [(-0.02, -0.006), (0.002, -0.006), (0.002, -0.016), (0.02, 0), (0.002, 0.016), (0.002, 0.006), (-0.02, 0.006)], 0.002,
        (NX - 0.036, PF - 0.0055, NZ - 0.045), "white", bevel=0, plane='XZ')
box("notice_blue", (0.062, 0.002, 0.062), (NX + 0.036, PF - 0.0045, NZ - 0.045), "red", bevel=0)
cyl("notice_dot", 0.02, 0.002, (NX + 0.036, PF - 0.0055, NZ - 0.045), "white", axis='Y', verts=24)
box("notice_bar", (0.134, 0.002, 0.02), (NX, PF - 0.0045, NZ + 0.03), "plum", bevel=0)

# ------------------------------------------------------------------ fire blanket in its wall case
KX, KZ = -0.125, 0.925
box("blanket_case", (0.27, 0.052, 0.19), (KX, PF - 0.026, KZ), "red", bevel=0.016, segments=4)
box("blanket_seam", (0.262, 0.046, 0.004), (KX, PF - 0.0275, KZ + 0.05), "black", bevel=0)
profile("blanket_label", rrect(0.15, 0.085, 0.008), 0.003, (KX, PF - 0.0525, KZ - 0.02), "white", bevel=0, plane='XZ')
box("blanket_slot", (0.23, 0.03, 0.006), (KX, PF - 0.028, KZ - 0.094), "black", bevel=0)
box("blanket_edge", (0.21, 0.018, 0.012), (KX, PF - 0.028, KZ - 0.097), "cream", bevel=0.003)
for sx in (-1, 1):
    box("pull_tape", (0.034, 0.004, 0.10), (KX + sx * 0.07, PF - 0.028, KZ - 0.145), "black", bevel=0.001)
    cyl("pull_end", 0.007, 0.046, (KX + sx * 0.07, PF - 0.028, KZ - 0.197), "black", axis='X', bevel=0.002, verts=14)
for sx in (-1, 1):
    cyl("case_screw", 0.006, 0.004, (KX + sx * 0.105, PF - 0.0525, KZ + 0.075), "steel", axis='Y', verts=10)


# ================================================================== extinguisher parts
def valve_head(n, P, z0, body_mat, handle_mat, lever_mat, ring_side=1):
    """Squeeze-grip valve: hex, body, plunger, cheeks, carry handle (+Y), operating lever, safety pin + ring + tamper tag."""
    cyl(n + "_hex", 0.03, 0.02, (0, 0, z0 + 0.008), body_mat, parent=P, verts=6, bevel=0.002)
    cyl(n + "_vbody", 0.021, 0.05, (0, 0, z0 + 0.04), body_mat, parent=P, bevel=0.003, verts=24)
    cyl(n + "_vcap", 0.016, 0.008, (0, 0, z0 + 0.067), body_mat, parent=P, bevel=0.002, verts=20)
    cyl(n + "_plunger", 0.006, 0.02, (0, 0, z0 + 0.076), "steel", parent=P, verts=12)
    for sx in (-1, 1):
        profile(n + "_cheek", [(-0.028, 0.048), (0.05, 0.04), (0.05, 0.062), (0.0, 0.088), (-0.02, 0.092), (-0.03, 0.084)], 0.004, (sx * 0.018, 0, z0), handle_mat, bevel=0.0015, parent=P)
    strip(n + "_carry", [(0.0, 0.050), (0.05, 0.050), (0.10, 0.044), (0.138, 0.034), (0.152, 0.02)], 0.008, 0.03, (0, 0, z0), handle_mat, parent=P, bevel=0.003)
    strip(n + "_lever", [(-0.026, 0.090), (0.0, 0.092), (0.04, 0.098), (0.09, 0.111), (0.14, 0.118), (0.158, 0.112)], 0.007, 0.03, (0, 0, z0), lever_mat, parent=P, bevel=0.003)
    cyl(n + "_lpin", 0.005, 0.048, (0, -0.018, z0 + 0.083), "steel", axis='X', parent=P, verts=12)
    cyl(n + "_hrivet", 0.0045, 0.046, (0, 0.04, z0 + 0.051), "steel", axis='X', parent=P, verts=12)
    # safety pin through the cheeks under the lever, pull ring and yellow tamper tag
    py, pz = 0.024, z0 + 0.073
    cyl(n + "_pin", 0.003, 0.062, (ring_side * 0.004, py, pz), "steel", axis='X', parent=P, verts=10)
    ring(n + "_pinring", 0.014, 0.0022, (ring_side * 0.036, py, pz - 0.011), "steel", axis='X', parent=P, n=20)
    tube(n + "_tagtie", [(ring_side * 0.036, py, pz - 0.024), (ring_side * 0.039, py + 0.002, pz - 0.04), (ring_side * 0.038, py + 0.003, pz - 0.052)], 0.0012, "hazard", parent=P)
    box(n + "_tag", (0.002, 0.024, 0.036), (ring_side * 0.038, py + 0.004, pz - 0.066), "hazard", bevel=0.0008, parent=P, rot=(R(6), R(ring_side * -5), 0))


def dome(rb, rn, z0, h, n=12):
    return [(rn + (rb - rn) * math.cos(R(90 * i / n)), z0 + h * math.sin(R(90 * i / n))) for i in range(n + 1)]


# ------------------------------------------------------------------ 1. water / foam extinguisher (static)
TH = R(-105)
W = empty("water", (WX, EX_Y, ZF + 0.004), rot=(0, 0, TH))
r = WR
wprof = ([(0, 0.012), (r - 0.03, 0.012), (r - 0.018, 0.0), (r - 0.004, 0.0), (r, 0.004), (r, 0.03), (r - 0.003, 0.033), (r - 0.003, 0.038), (r, 0.041)]
         + dome(r, 0.036, 0.425, 0.085) + [(0.036, 0.512), (0.034, 0.516), (0.034, 0.522), (0.039, 0.526), (0.039, 0.538), (0.035, 0.542), (0.03, 0.542), (0.03, 0.55), (0, 0.55)])
lathe("w_body", wprof, (0, 0, 0), "red", axis='Z', parent=W, steps=56)
lathe("w_skirt", [(r - 0.004, 0.0), (r + 0.003, 0.002), (r + 0.004, 0.008), (r + 0.004, 0.026), (r + 0.001, 0.03), (r - 0.002, 0.03)], (0, 0, 0), "black", axis='Z', parent=W, steps=56)
band("w_band", r, 0.335, 0.405, "cream", W)
LA = -90 - math.degrees(TH)          # local angle that faces the front of the scene
curved_panel("w_label", r, 0.095, 0.305, LA, 105, "white", W)
curved_panel("w_label_top", r, 0.262, 0.297, LA, 96, "red", W, proud=0.0022, thick=0.002)
for k, m in enumerate(("green", "green", "black")):
    curved_panel("w_picto", r, 0.108, 0.148, LA - 28 + k * 28, 22, m, W, proud=0.0022, thick=0.002)
Z0 = 0.55
valve_head("w", W, Z0, "brass", "black", "black", ring_side=1)
# pressure gauge on the side of the valve (local +X)
cyl("w_gstem", 0.008, 0.02, (0.028, 0, Z0 + 0.034), "brass", axis='X', parent=W, verts=12)
lathe("w_gcase", [(0, 0), (0.019, 0), (0.023, 0.003), (0.023, 0.013), (0.0205, 0.016), (0.0195, 0.0125), (0, 0.0125)], (0.036, 0, Z0 + 0.034), "steel", axis='X', parent=W, steps=28)
cyl("w_gface", 0.0196, 0.002, (0.0488, 0, Z0 + 0.034), "white", axis='X', parent=W, verts=28)
GX = 0.0502
profile("w_ggreen", arc_pts(0, 0, 0.017, 55, 125, 8) + arc_pts(0, 0, 0.0105, 125, 55, 8), 0.0012, (GX, 0, Z0 + 0.034), "green", bevel=0, parent=W)
profile("w_gred1", arc_pts(0, 0, 0.017, 130, 200, 8) + arc_pts(0, 0, 0.0105, 200, 130, 8), 0.0012, (GX, 0, Z0 + 0.034), "red", bevel=0, parent=W)
profile("w_gred2", arc_pts(0, 0, 0.017, -20, 50, 8) + arc_pts(0, 0, 0.0105, 50, -20, 8), 0.0012, (GX, 0, Z0 + 0.034), "red", bevel=0, parent=W)
profile("w_gneedle", [(-0.0012, -0.004), (0.0012, -0.004), (0.0004, 0.015), (-0.0004, 0.015)], 0.0012, (GX + 0.001, 0, Z0 + 0.034), "black", bevel=0, parent=W, rot=(R(8), 0, 0))
cyl("w_ghub", 0.003, 0.003, (GX + 0.001, 0, Z0 + 0.034), "black", axis='X', parent=W, verts=10)
# discharge outlet (local -Y), hose down the side into a clip, nozzle
HZ0 = Z0 + 0.034
cyl("w_outlet", 0.012, 0.03, (0, -0.03, HZ0), "brass", axis='Y', parent=W, bevel=0.002, verts=16)
cyl("w_ferrule", 0.0125, 0.026, (0, -0.056, HZ0), "steel", axis='Y', parent=W, bevel=0.002, verts=16)
HR_ = 0.0095
yh = -(r + HR_ + 0.003)
hose("w_hose", [(0, -0.06, HZ0), (0, -0.092, HZ0 - 0.004), (0, -0.117, HZ0 - 0.035), (0, -0.118, HZ0 - 0.09), (0, yh - 0.004, 0.44), (0, yh, 0.38), (0, yh, 0.20)], HR_, "black", parent=W)
lathe("w_nozzle", [(0, 0.118), (0.007, 0.118), (0.0095, 0.122), (0.011, 0.15), (0.0135, 0.152), (0.0135, 0.186), (0.012, 0.19), (0.012, 0.205), (0, 0.205)], (0, yh, 0), "black", axis='Z', parent=W, steps=20)
lathe("w_nozzle_tip", [(0, 0.112), (0.0055, 0.112), (0.0072, 0.12), (0, 0.12)], (0, yh, 0), "brass", axis='Z', parent=W, steps=16)
for z in (0.36, 0.215):
    band("w_strap", r, z - 0.007, z + 0.007, "steel", W, proud=0.001)
    profile("w_clip", arc_pts(0, 0, HR_ + 0.004, 200, 340, 8) + [(0.008, 0.011), (-0.008, 0.011)], 0.022, (0, yh, z), "black", bevel=0.0015, parent=W, plane='XY')
# hanging lug on the back of the body
box("w_lug", (0.04, 0.008, 0.05), (r * math.cos(R(LA + 180)), r * math.sin(R(LA + 180)), 0.37), "red", bevel=0.003, parent=W, rot=(0, 0, R(LA + 90)))

# ------------------------------------------------------------------ 2. CO2 extinguisher (moves)
C0 = (CX, EX_Y, ZF + 0.004)
C = empty("co2", C0)
r = CR
cprof = ([(0, 0.012), (r - 0.03, 0.012), (r - 0.016, 0.0), (r - 0.005, 0.0), (r, 0.006), (r, 0.024), (r - 0.0025, 0.027), (r - 0.0025, 0.031), (r, 0.034)]
         + dome(r, 0.026, 0.49, 0.075) + [(0.026, 0.566), (0.0245, 0.575), (0.0245, 0.59), (0.031, 0.594), (0.031, 0.608), (0.027, 0.612), (0.022, 0.612), (0.022, 0.62), (0, 0.62)])
lathe("c_body", cprof, (0, 0, 0), "red", axis='Z', parent=C, steps=48)
band("c_band", r, 0.395, 0.475, "black", C)
curved_panel("c_label", r, 0.13, 0.36, -90, 110, "white", C)
curved_panel("c_label_top", r, 0.315, 0.35, -90, 100, "red", C, proud=0.0022, thick=0.002)
for k, m in enumerate(("green", "black")):
    curved_panel("c_picto", r, 0.145, 0.185, -90 - 16 + k * 32, 26, m, C, proud=0.0022, thick=0.002)
Z1 = 0.62
valve_head("c", C, Z1, "brass", "steel", "black", ring_side=-1)
# outlet to local +X: swivel arm to the horn pivot
HPX, HPZ = 0.118, Z1 + 0.036
cyl("c_outlet", 0.012, 0.03, (0.03, 0, HPZ), "brass", axis='X', parent=C, bevel=0.002, verts=16)
cyl("c_arm", 0.008, 0.07, (0.07, 0, HPZ), "steel", axis='X', parent=C, verts=14)
cyl("c_armnut", 0.0125, 0.012, (0.048, 0, HPZ), "brass", axis='X', parent=C, verts=6)
# body-side rest clip for the folded horn
band("c_strap", r, 0.435, 0.447, "steel", C, proud=0.0028)
box("c_hornrest", (0.03, 0.03, 0.016), (r + 0.012, 0, 0.441), "black", bevel=0.004, parent=C)

H = empty("co2_horn", (HPX, 0, HPZ), parent=C)
cyl("h_knuckle", 0.017, 0.034, (0, 0, 0), "brass", axis='X', parent=H, bevel=0.003, verts=20)
cyl("h_knuckle_cap", 0.011, 0.042, (0, 0, 0), "steel", axis='X', parent=H, bevel=0.002, verts=6)
cyl("h_stem", 0.0105, 0.05, (0, 0, -0.035), "brass", parent=H, verts=16)
lathe("h_grip", [(0.0105, -0.05), (0.018, -0.054), (0.019, -0.06), (0.0175, -0.068), (0.019, -0.076), (0.0175, -0.084), (0.019, -0.092), (0.0175, -0.10), (0.019, -0.108),
                 (0.019, -0.116), (0.022, -0.122)], (0, 0, 0), "vinyl", axis='Z', parent=H, steps=24)
lathe("h_horn", [(0.019, -0.118), (0.024, -0.124), (0.028, -0.15), (0.034, -0.22), (0.0405, -0.31), (0.043, -0.352), (0.0465, -0.356), (0.0465, -0.366), (0.043, -0.37),
                 (0.0395, -0.366), (0.037, -0.31), (0.031, -0.22), (0.025, -0.15), (0.012, -0.132), (0, -0.132)], (0, 0, 0), "black", axis='Z', parent=H, steps=36)

# ------------------------------------------------------------------ motion
LIFT, FWD, TILT, SWING = 0.25, 0.15, 12.0, -87.0
for f in FRAMES:
    s = f / FRAME_WORK
    up = ease(s / 0.7)
    out = ease((s - 0.3) / 0.7)
    key(C, f, loc=(C0[0], C0[1] - FWD * out, C0[2] + LIFT * up), rot=(R(TILT) * out, 0, 0))
    key(H, f, rot=(R(SWING) * ease((s - 0.25) / 0.75), 0, 0))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "fire.glb"))
