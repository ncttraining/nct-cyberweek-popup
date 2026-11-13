"""First aid station hero scene: open first aid case on a flight crate, AED on a lower crate, sign on a post.
Motion: the case lid (pivot empty "lid_hinge") swings from closed to 105 degrees open."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nctlib
from nctlib import *
import bmesh
from mathutils import Vector
from tpmlib import rot2, rod3d, bar3d
reset()
R = math.radians


# ================================================================ helpers
def rr(sx, sy, r, n=6):
    """Rounded-rectangle outline centred on 0,0."""
    hx, hy = sx / 2, sy / 2
    r = min(r, hx - 1e-4, hy - 1e-4)
    return (arc_pts(hx - r, hy - r, r, 0, 90, n) + arc_pts(-hx + r, hy - r, r, 90, 180, n)
            + arc_pts(-hx + r, -hy + r, r, 180, 270, n) + arc_pts(hx - r, -hy + r, r, 270, 360, n))


def rbox(name, sx, sy, sz, r, loc, material, bevel=0.004, parent=None, plane='XY', rot=(0, 0, 0), segments=3):
    """Box with rounded corners in its outline plane. For plane 'XY': sx, sy outline and sz height;
    'XZ': sx, sy(=Z size) outline and sz depth along Y; 'YZ': sx(=Y), sy(=Z) outline and sz width along X."""
    return profile(name, rr(sx, sy, r), sz, loc, material, bevel=bevel, parent=parent, plane=plane, rot=rot, segments=segments)


def loft(name, loops, loc, material, bevel=0.0, parent=None, flip=None, n=6, ring=False):
    """Skin a stack of rounded-rectangle loops (sx, sy, r, z); first and last are capped.
    flip = height h mirrors z -> h - z."""
    bm = bmesh.new()
    rings = []
    for sx, sy, r, z in loops:
        zz = (flip - z) if flip is not None else z
        rings.append([bm.verts.new((a, b, zz)) for a, b in rr(sx, sy, max(r, 0.002), n)])
    m = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(m):
            bm.faces.new((a[k], a[(k + 1) % m], b[(k + 1) % m], b[k]))
    if ring:
        a, b = rings[-1], rings[0]
        for k in range(m):
            bm.faces.new((a[k], a[(k + 1) % m], b[(k + 1) % m], b[k]))
    else:
        bm.faces.new(rings[0])
        bm.faces.new(rings[-1])
    return nctlib._finish(nctlib._new_obj(name, bm, loc), material, bevel, parent)


def cup(name, sx, sy, r, t, h, ft, rb, loc, material, parent=None, flip=False, bevel=0.003):
    """A moulded open shell: outer size sx, sy, corner radius r, wall t, height h, floor ft, rounded closed edge rb."""
    loops = []
    for j in range(5):
        a = R(90 * j / 4)
        d = rb * (1 - math.sin(a))
        loops.append((sx - 2 * d, sy - 2 * d, r - d, rb * (1 - math.cos(a))))
    loops += [(sx, sy, r, h), (sx - 2 * t, sy - 2 * t, r - t, h), (sx - 2 * t, sy - 2 * t, r - t, ft)]
    return loft(name, loops, loc, material, bevel=bevel, parent=parent, flip=h if flip else None)


def smooth(pts, n=8):
    """Catmull-Rom through 3D points, so tube() bends are round."""
    P = [Vector(p) for p in pts]
    P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(P[-2]))
    return out


def ellipse(rx, ry, n=20):
    return [(rx * math.cos(2 * math.pi * i / n), ry * math.sin(2 * math.pi * i / n), 0) for i in range(n)]


# ================================================================ layout
DX = 0.035
A_CX, A_CY, A_W, A_D, A_H = -0.12 + DX, 0.0, 0.54, 0.40, 0.42       # main crate (under the case)
B_CX, B_CY, B_W, B_D, B_H = 0.37 + DX, -0.17, 0.44, 0.50, 0.20      # low crate (under the AED)


def crate(name, cx, cy, w, d, h, seam=None, band=None, latches=(), handles=(-1, 1)):
    """Flight-case style equipment crate standing on the floor."""
    e = 0.022
    box(name + "_body", (w - 0.010, d - 0.010, h - 0.012), (cx, cy, h / 2), "chassis", bevel=0.004)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(name + "_ev", (e, e, h - 0.03), (cx + sx * (w / 2 - e / 2), cy + sy * (d / 2 - e / 2), h / 2), "steel", bevel=0.007)
            for z in (0.022, h - 0.022):
                box(name + "_ball", (0.046, 0.046, 0.044), (cx + sx * (w / 2 - 0.021), cy + sy * (d / 2 - 0.021), z), "steel", bevel=0.016, segments=4)
        for z in (e / 2, h - e / 2):
            box(name + "_ex", (w - 0.03, e, e), (cx, cy + sx * (d / 2 - e / 2), z), "steel", bevel=0.007)
            box(name + "_ey", (e, d - 0.03, e), (cx + sx * (w / 2 - e / 2), cy, z), "steel", bevel=0.007)
    if band is not None:
        box(name + "_band", (w - 0.006, d - 0.006, 0.06), (cx, cy, band), "plum", bevel=0.002, segments=1)
        box(name + "_stripe", (w - 0.004, d - 0.004, 0.012), (cx, cy, band), "accent", bevel=0.002, segments=1)
    if seam is not None:
        for dz in (-0.011, 0.011):
            box(name + "_seam", (w - 0.002, d - 0.002, 0.018), (cx, cy, seam + dz), "steel", bevel=0.005)
        box(name + "_gap", (w - 0.008, d - 0.008, 0.006), (cx, cy, seam), "black", bevel=0)
    for lx in latches:   # butterfly latches across the seam, on the front
        y = cy - d / 2
        box(name + "_lplate", (0.075, 0.006, 0.095), (cx + lx, y + 0.001, seam), "steel", bevel=0.003)
        cyl(name + "_ldish", 0.027, 0.006, (cx + lx, y - 0.003, seam - 0.012), "chassis", axis='Y', bevel=0.002)
        box(name + "_lwing", (0.05, 0.006, 0.012), (cx + lx, y - 0.007, seam - 0.012), "steel", bevel=0.003, rot=(0, R(25), 0))
        box(name + "_lhook", (0.022, 0.006, 0.03), (cx + lx, y - 0.004, seam + 0.028), "steel", bevel=0.003)
    if handles:          # recessed sprung handles on both ends
        hz = (seam - 0.13) if seam else h / 2
        for sx in handles:
            x = cx + sx * w / 2
            box(name + "_hplate", (0.006, 0.19, 0.11), (x - sx * 0.001, cy, hz), "steel", bevel=0.003)
            box(name + "_hdish", (0.006, 0.15, 0.075), (x + sx * 0.001, cy, hz), "black", bevel=0.002)
            pts = [(x + sx * 0.002, cy - 0.055, hz + 0.02), (x + sx * 0.016, cy - 0.055, hz - 0.012), (x + sx * 0.018, cy - 0.04, hz - 0.02),
                   (x + sx * 0.018, cy + 0.04, hz - 0.02), (x + sx * 0.016, cy + 0.055, hz - 0.012), (x + sx * 0.002, cy + 0.055, hz + 0.02)]
            tube(name + "_hbar", smooth(pts, 4), 0.006, "steel")
            cyl(name + "_hgrip", 0.009, 0.07, (x + sx * 0.018, cy, hz - 0.02), "rubber", axis='Y', bevel=0.002, verts=16)


crate("crateA", A_CX, A_CY, A_W, A_D, A_H, seam=0.31, band=0.22, latches=(-0.15, 0.15), handles=(-1,))
crate("crateB", B_CX, B_CY, B_W, B_D, B_H, band=0.10, handles=())
# small vent / data plate on the main crate front
box("a_plate_frame", (0.124, 0.006, 0.074), (A_CX, A_CY - A_D / 2 + 0.002, 0.11), "steel", bevel=0.002)
box("a_plate", (0.108, 0.004, 0.058), (A_CX, A_CY - A_D / 2 - 0.001, 0.11), "decal", bevel=0.001)
for sx in (-1, 1):
    cyl("a_plate_rivet", 0.003, 0.004, (A_CX + sx * 0.058, A_CY - A_D / 2 - 0.001, 0.11), "chrome", axis='Y', verts=8)

# ================================================================ first aid case
CW, CD, HB, HL = 0.45, 0.32, 0.10, 0.06       # width, depth, base height, lid height
CR, CT = 0.045, 0.013                         # corner radius, wall
CX, CY = A_CX, A_CY - 0.01
CZ = A_H + 0.006                              # underside of the case (on rubber feet)
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl("case_foot", 0.014, 0.008, (CX + sx * 0.17, CY + sy * 0.11, A_H + 0.004), "rubber", bevel=0.002, verts=16)
cup("case_base", CW, CD, CR, CT, HB - 0.003, 0.012, 0.016, (CX, CY, CZ), "green")
loft("case_gasket", [(CW - 0.005, CD - 0.005, CR - 0.0025, 0), (CW - 0.005, CD - 0.005, CR - 0.0025, 0.0032),
                     (CW - 2 * CT + 0.004, CD - 2 * CT + 0.004, CR - CT + 0.002, 0.0032), (CW - 2 * CT + 0.004, CD - 2 * CT + 0.004, CR - CT + 0.002, 0)],
     (CX, CY, CZ + HB - 0.0035), "black", ring=True)
# moulded rib round the base
loft("case_rib", [(CW + 0.006, CD + 0.006, CR + 0.003, 0), (CW + 0.006, CD + 0.006, CR + 0.003, 0.014), (CW - 0.004, CD - 0.004, CR - 0.002, 0.014), (CW - 0.004, CD - 0.004, CR - 0.002, 0)],
     (CX, CY, CZ + HB - 0.026), "green", bevel=0.003, ring=True)

# ---- tray and contents
TZ = CZ + 0.050                                # tray surface
IW, ID = CW - 2 * CT, CD - 2 * CT
loft("tray", [(IW + 0.002, ID + 0.002, CR - CT, 0), (IW + 0.002, ID + 0.002, CR - CT, 0.012)], (CX, CY, TZ - 0.012), "plastic")
DIVH = 0.034
for x in (-0.080, 0.070):
    box("tray_div", (0.005, ID - 0.004, DIVH), (CX + x, CY, TZ + DIVH / 2), "plastic", bevel=0.002, segments=2)
box("tray_div", (0.145, 0.005, DIVH), (CX - 0.005, CY + 0.030, TZ + DIVH / 2), "plastic", bevel=0.002, segments=2)
box("tray_div", (0.138, 0.005, DIVH), (CX + 0.141, CY + 0.050, TZ + DIVH / 2), "plastic", bevel=0.002, segments=2)

# left bay: eight rolled bandages standing on end (wound layers show on top)
k = 0
for iy in range(4):
    for ix in range(2):
        m = "white" if k in (2, 5) else "cream"
        x = CX - 0.176 + ix * 0.061
        y = CY - 0.101 + iy * 0.067
        rh = 0.064 if m == "cream" else 0.058
        lathe("roll", [(0, 0), (0.0275, 0), (0.0290, 0.002), (0.0290, rh - 0.002), (0.0275, rh), (0.0075, rh), (0.0075, rh - 0.010), (0, rh - 0.010)],
              (x, y, TZ), m, axis='Z', steps=28)
        for rr_ in (0.0115, 0.0160, 0.0205, 0.0250):
            lathe("roll_ring", [(rr_, rh + 0.0004), (rr_ + 0.0011, rh + 0.0004)], (x, y, TZ), "tape", axis='Z', steps=24)
        lathe("roll_core", [(0, rh - 0.0095), (0.0075, rh - 0.0095)], (x, y, TZ), "tape", axis='Z', steps=14)
        a = 0.7 + k * 1.9      # loose end of the bandage, held by a small clip
        box("roll_tail", (0.0016, 0.020, rh - 0.008), (x + math.cos(a) * 0.0293, y + math.sin(a) * 0.0293, TZ + rh / 2), m, bevel=0.0006, rot=(0, 0, a), segments=1)
        box("roll_clip", (0.003, 0.006, 0.014), (x + math.cos(a) * 0.0300, y + math.sin(a) * 0.0300, TZ + rh / 2), "steel", bevel=0.001, rot=(0, 0, a), segments=1)
        k += 1

# middle bay, rear: stack of wrapped dressings
for i in range(3):
    z = TZ + 0.0105 + i * 0.021
    x = CX - 0.005 + (0.004, -0.003, 0.002)[i]
    y = CY + 0.087 + (0.0, 0.003, -0.002)[i]
    box("dress", (0.126, 0.096, 0.020), (x, y, z), "white" if i != 1 else "cream", bevel=0.007, segments=3)
    box("dress_band", (0.030, 0.0965, 0.0205), (x - 0.03, y, z), "green", bevel=0.0065, segments=3)
box("dress_label", (0.045, 0.05, 0.002), (CX + 0.022, CY + 0.085, TZ + 0.063), "cream", bevel=0.0008, segments=1)

# middle bay, front: foil blanket pack, face shield pouch and plasters box standing on edge
box("foil", (0.128, 0.034, 0.064), (CX - 0.005, CY + 0.006, TZ + 0.032), "rim", bevel=0.009, segments=3)
box("foil_seal", (0.132, 0.004, 0.012), (CX - 0.005, CY + 0.006, TZ + 0.067), "rim", bevel=0.0015, segments=1)
box("foil_label", (0.07, 0.002, 0.03), (CX - 0.005, CY - 0.0115, TZ + 0.036), "white", bevel=0.0008, segments=1)
box("pouch", (0.118, 0.026, 0.058), (CX - 0.005, CY - 0.043, TZ + 0.029), "paint", bevel=0.010, segments=3)
box("pouch_zip", (0.108, 0.006, 0.004), (CX - 0.005, CY - 0.043, TZ + 0.059), "black", bevel=0.0015, segments=1)
box("pouch_label", (0.05, 0.002, 0.026), (CX - 0.02, CY - 0.0565, TZ + 0.030), "white", bevel=0.0008, segments=1)
tube("pouch_ring", [(p[0] + CX + 0.048, CY - 0.043, p[1] + TZ + 0.066) for p in [(q[0], q[1]) for q in ellipse(0.009, 0.009, 14)]], 0.0015, "steel", closed=True)
box("plasters", (0.120, 0.046, 0.068), (CX - 0.005, CY - 0.100, TZ + 0.034), "white", bevel=0.004, segments=2)
box("plasters_band", (0.1205, 0.0465, 0.020), (CX - 0.005, CY - 0.100, TZ + 0.030), "green", bevel=0.004, segments=2)
box("plasters_flap", (0.118, 0.044, 0.002), (CX - 0.005, CY - 0.100, TZ + 0.0685), "cream", bevel=0.0008, segments=1)

# right bay, front: eyewash bottle lying down, tough-cut shears on a moulded riser
BX_, BY_ = CX + 0.103, CY - 0.045
lathe("eyewash", [(0, 0), (0.019, 0), (0.025, 0.006), (0.025, 0.084), (0.022, 0.094), (0.012, 0.102), (0.012, 0.108), (0, 0.108)],
      (BX_, BY_ + 0.062, TZ + 0.025), "white", axis='Y', steps=28)
lathe("eyewash_cap", [(0, 0), (0.015, 0), (0.015, 0.020), (0.011, 0.028), (0.005, 0.034), (0, 0.034)],
      (BX_, BY_ + 0.062 - 0.104, TZ + 0.025), "green", axis='Y', steps=24)
lathe("eyewash_label", [(0.0256, 0.026), (0.0256, 0.070)], (BX_, BY_ + 0.062, TZ + 0.025), "cream", axis='Y', steps=28)
lathe("eyewash_band", [(0.0259, 0.058), (0.0259, 0.066)], (BX_, BY_ + 0.062, TZ + 0.025), "green", axis='Y', steps=28)
RZ = TZ + 0.040
box("riser", (0.066, 0.186, 0.040), (CX + 0.172, CY - 0.047, TZ + 0.020), "plastic", bevel=0.006)
sh = empty("shears", (CX + 0.172, CY - 0.022, RZ), rot=(0, 0, R(4)))
sh.scale = (1.22, 1.22, 1.5)
# blades point to the back (+Y local), handles to the front; local origin = pivot screw
profile("sh_blade1", [(-0.008, -0.012), (0.004, -0.012), (0.006, 0.050), (0.004, 0.060), (-0.002, 0.063), (-0.006, 0.056)], 0.003, (0, 0, 0.0020), "steel", bevel=0.001, parent=sh, plane='XY', segments=1)
profile("sh_blade2", [(0.008, -0.012), (-0.004, -0.012), (-0.008, 0.046), (-0.004, 0.058), (0.004, 0.060), (0.002, 0.050)], 0.003, (0, 0, 0.0050), "steel", bevel=0.001, parent=sh, plane='XY', segments=1)
cyl("sh_pin", 0.0045, 0.009, (0, 0, 0.0040), "chrome", parent=sh, bevel=0.001, verts=14)
for sx, ry, ly in ((-1, 0.020, -0.062), (1, 0.027, -0.068)):
    bar3d("sh_arm", (sx * 0.003, -0.008, 0.0035), (sx * 0.013, ly + ry + 0.002, 0.0035), 0.010, 0.006, "paint", bevel=0.0025, parent=sh)
    tube("sh_loop", [(p[0] + sx * 0.016, p[1] + ly, 0.0035) for p in ellipse(0.0125, ry, 22)], 0.0042, "paint", parent=sh, closed=True)

# right bay, rear: folded gloves on a sealed pack
GX, GY = CX + 0.141, CY + 0.097
box("glove_pack", (0.122, 0.078, 0.030), (GX, GY, TZ + 0.015), "cream", bevel=0.008)
for i in range(2):
    gz = TZ + 0.030 + 0.006 + i * 0.012
    gx = GX + (0.0, 0.004)[i]
    gyaw = R((-3, 4)[i])
    g = empty("glove", (gx, GY, gz), rot=(0, 0, gyaw))
    box("glove_palm", (0.064, 0.070, 0.012), (-0.026, 0, 0), "white", bevel=0.005, parent=g)
    box("glove_cuff", (0.012, 0.072, 0.013), (-0.054, 0, 0), "white", bevel=0.004, parent=g)
    for k in range(4):
        box("glove_finger", (0.050, 0.0155, 0.011), (0.028, -0.0265 + k * 0.0177, 0), "white", bevel=0.005, parent=g)

# ---- hinge, latch catches, carry handle (fixed to the base)
HY, HZ = CY + CD / 2 + 0.005, CZ + HB          # hinge line
for hx in (-0.13, 0.13):
    cyl("hinge_knuckle", 0.006, 0.026, (CX + hx, HY, HZ), "steel", axis='X', bevel=0.001, verts=16)
    cyl("hinge_pin", 0.0028, 0.082, (CX + hx, HY, HZ), "chrome", axis='X', verts=10)
    box("hinge_leaf", (0.026, 0.006, 0.030), (CX + hx, HY - 0.003, HZ - 0.016), "steel", bevel=0.002)
FY = CY - CD / 2                                # front face of the case
LX = 0.135
for sx in (-1, 1):
    box("catch", (0.030, 0.006, 0.010), (CX + sx * LX, FY - 0.002, CZ + HB - 0.036), "steel", bevel=0.002)
# carry handle: swing handle on two lugs, resting angled forward
for sx in (-1, 1):
    box("handle_lug", (0.016, 0.016, 0.022), (CX + sx * 0.062, FY - 0.006, CZ + 0.052), "white", bevel=0.004)
hp = [(-0.062, FY - 0.012, CZ + 0.052), (-0.062, FY - 0.036, CZ + 0.030), (-0.050, FY - 0.046, CZ + 0.022),
      (0.050, FY - 0.046, CZ + 0.022), (0.062, FY - 0.036, CZ + 0.030), (0.062, FY - 0.012, CZ + 0.052)]
tube("handle_bar", smooth([(CX + p[0], p[1], p[2]) for p in hp], 5), 0.0065, "white")
rod3d("handle_grip", (CX - 0.042, FY - 0.046, CZ + 0.022), (CX + 0.042, FY - 0.046, CZ + 0.022), 0.0095, "white", verts=18)

# ---- the lid (everything parented to the hinge pivot; local origin on the hinge line)
lid = empty("lid_hinge", (CX, HY, HZ))
LY = -(CD / 2 + 0.005)                          # lid centre in hinge coordinates
cup("lid_shell", CW, CD, CR, CT, HL, 0.012, 0.020, (0, LY, 0), "green", parent=lid, flip=True)
loft("lid_rib", [(CW + 0.006, CD + 0.006, CR + 0.003, 0), (CW + 0.006, CD + 0.006, CR + 0.003, 0.012), (CW - 0.004, CD - 0.004, CR - 0.002, 0.012), (CW - 0.004, CD - 0.004, CR - 0.002, 0)],
     (0, LY, 0.004), "green", bevel=0.003, parent=lid, ring=True)
# raised panel and cross on the lid top
loft("lid_panel", [(0.34, 0.235, 0.03, 0), (0.34, 0.235, 0.03, 0.003), (0.328, 0.223, 0.026, 0.003), (0.328, 0.223, 0.026, 0.0012),
                   (0.20, 0.12, 0.01, 0.0012)], (0, LY, HL - 0.0005), "green", parent=lid)
cyl("lid_disc", 0.088, 0.004, (0, LY, HL + 0.0015), "green", parent=lid, bevel=0.0015, verts=48)
for s in ((0.135, 0.044), (0.044, 0.135)):
    box("lid_cross", (s[0], s[1], 0.007), (0, LY, HL + 0.006), "white", bevel=0.0025, parent=lid)
for hx in (-0.13, 0.13):
    for dx in (-0.027, 0.027):
        cyl("lid_knuckle", 0.006, 0.026, (hx + dx, 0, 0), "steel", axis='X', bevel=0.001, verts=16, parent=lid)
        box("lid_leaf", (0.026, 0.006, 0.026), (hx + dx, -0.003, 0.015), "steel", bevel=0.002, parent=lid)
LFY = LY - CD / 2                               # lid front face (local)
for sx in (-1, 1):
    cyl("latch_barrel", 0.006, 0.050, (sx * LX, LFY - 0.006, 0.024), "white", axis='X', bevel=0.0015, verts=16, parent=lid)
    box("latch_body", (0.046, 0.008, 0.066), (sx * LX, LFY - 0.0095, -0.007), "white", bevel=0.003, parent=lid)
    box("latch_lip", (0.046, 0.014, 0.008), (sx * LX, LFY - 0.013, -0.040), "white", bevel=0.003, parent=lid, rot=(R(-25), 0, 0))
    box("latch_grip", (0.030, 0.003, 0.020), (sx * LX, LFY - 0.014, -0.010), "steel", bevel=0.001, parent=lid)
# inside the lid: two dressings under an elastic strap
CEIL = HL - 0.012
for sx in (-1, 1):
    box("lid_dress", (0.150, 0.105, 0.018), (sx * 0.090, LY, CEIL - 0.009), "cream" if sx < 0 else "white", bevel=0.006, parent=lid)
    box("lid_dress_band", (0.032, 0.1055, 0.0185), (sx * 0.090 - 0.035, LY, CEIL - 0.009), "green", bevel=0.006, parent=lid)
box("lid_strap", (0.372, 0.030, 0.003), (0, LY, CEIL - 0.0195), "black", bevel=0.001, parent=lid, segments=1)
for x in (-0.180, 0.0, 0.180):
    box("lid_strap_anchor", (0.012, 0.030, 0.021), (x, LY, CEIL - 0.0105), "black", bevel=0.002, parent=lid, segments=1)
    cyl("lid_strap_rivet", 0.004, 0.003, (x, LY, CEIL - 0.0215), "steel", parent=lid, verts=10)
key(lid, FRAME_REST, rot=(0, 0, 0))
key(lid, FRAME_WORK, rot=(R(-105), 0, 0))

# ================================================================ AED on its stand
AW, AHH, AD = 0.30, 0.22, 0.09
AX = B_CX + 0.04
TILT = -15
PZ = B_H + 0.028
aed = empty("aed", (AX, B_CY + 0.13, PZ), rot=(R(TILT), 0, 0))   # origin = back-bottom edge of the unit
# stand: base plate, wedge, cradle
box("stand_base", (0.27, 0.17, 0.012), (AX, B_CY + 0.085, B_H + 0.006), "chassis", bevel=0.005)
p1 = rot2((-0.104, -0.010), TILT)
p2 = rot2((0.010, -0.010), TILT)
oy = B_CY + 0.13
for sx in (-1, 1):
    profile("stand_wedge", [(oy + p1[0], B_H + 0.010), (oy + p1[0], PZ + p1[1]), (oy + p2[0], PZ + p2[1]), (oy + p2[0], B_H + 0.010)],
            0.018, (AX + sx * 0.10, 0, 0), "chassis", bevel=0.004)
box("cradle", (0.25, 0.114, 0.010), (0, -0.047, -0.005), "steel", bevel=0.003, parent=aed)
box("cradle_lip", (0.25, 0.008, 0.032), (0, -0.100, 0.011), "steel", bevel=0.003, parent=aed)
box("cradle_back", (0.19, 0.008, 0.12), (0, 0.006, 0.055), "steel", bevel=0.003, parent=aed)
# unit body
BY0 = -0.002 - AD / 2                           # body centre (local y), unit sits just in front of the back rest
rbox("aed_body", AW, AHH, AD, 0.040, (0, BY0, AHH / 2 + 0.001), "plastic", bevel=0.016, parent=aed, plane='XZ', segments=4)
FYL = BY0 - AD / 2                              # front face (local y)
rbox("aed_face", AW - 0.034, AHH - 0.034, 0.016, 0.028, (0, FYL, AHH / 2 + 0.001), "paint", bevel=0.006, parent=aed, plane='XZ')
rbox("aed_backshell", AW - 0.05, AHH - 0.05, 0.010, 0.024, (0, BY0 + AD / 2 - 0.002, AHH / 2 + 0.001), "paint", bevel=0.004, parent=aed, plane='XZ')
FS = FYL - 0.008                                # surface of the orange face
ZC = AHH / 2 + 0.001
# display
rbox("aed_bezel", 0.132, 0.086, 0.006, 0.010, (-0.050, FS, ZC + 0.040), "black", bevel=0.002, parent=aed, plane='XZ')
rbox("aed_screen", 0.112, 0.066, 0.008, 0.005, (-0.050, FS, ZC + 0.040), "screen", bevel=0.001, parent=aed, plane='XZ')
# shock button with its ring
cyl("shock_ring", 0.043, 0.008, (0.073, FS, ZC - 0.030), "white", axis='Y', bevel=0.003, parent=aed, verts=40)
lathe("shock_btn", [(0, 0.016), (0.012, 0.0155), (0.024, 0.0135), (0.031, 0.009), (0.034, 0.003), (0.034, -0.004), (0, -0.004)],
      (0.073, FS, ZC - 0.030), "accent", axis='Y', parent=aed, steps=36)
# power button
cyl("power_ring", 0.020, 0.006, (0.073, FS, ZC + 0.052), "black", axis='Y', bevel=0.002, parent=aed, verts=28)
lathe("power_btn", [(0, 0.009), (0.008, 0.0085), (0.0135, 0.006), (0.015, 0.002), (0.015, -0.003), (0, -0.003)],
      (0.073, FS, ZC + 0.052), "green", axis='Y', parent=aed, steps=24)
cyl("status_led", 0.006, 0.006, (0.114, FS, ZC + 0.052), "lamp", axis='Y', parent=aed, verts=14)
# speaker grille
for i in range(5):
    box("aed_slot", (0.062 - abs(i - 2) * 0.010, 0.004, 0.0045), (-0.028, FS, ZC - 0.050 + i * 0.011), "black", bevel=0.0015, parent=aed, segments=1)
# electrode connector socket and plug
rbox("aed_socket", 0.040, 0.032, 0.006, 0.006, (-0.098, FS, ZC - 0.030), "black", bevel=0.002, parent=aed, plane='XZ')
box("aed_plug", (0.026, 0.026, 0.018), (-0.098, FS - 0.012, ZC - 0.030), "white", bevel=0.004, parent=aed)
cyl("aed_plug_relief", 0.005, 0.014, (-0.098, FS - 0.026, ZC - 0.030), "white", axis='Y', parent=aed, verts=12)
# carry handle
hh = [(-0.092, BY0, AHH - 0.012), (-0.088, BY0, AHH + 0.028), (-0.070, BY0, AHH + 0.042), (0.070, BY0, AHH + 0.042), (0.088, BY0, AHH + 0.028), (0.092, BY0, AHH - 0.012)]
tube("aed_handle", smooth(hh, 6), 0.011, "plastic", parent=aed)
rod3d("aed_handle_grip", (-0.05, BY0, AHH + 0.042), (0.05, BY0, AHH + 0.042), 0.0135, "rubber", parent=aed, verts=20)
# side bumpers
for sx in (-1, 1):
    box("aed_bump", (0.010, 0.060, 0.10), (sx * (AW / 2 - 0.002), BY0, ZC), "rubber", bevel=0.004, parent=aed)

# ---- pads and coiled lead on the crate top
TOPB = B_H
pad_tabs = []
for i, (px, py, yaw) in enumerate(((B_CX - 0.050, B_CY - 0.135, R(8)), (B_CX + 0.085, B_CY - 0.125, R(-7)))):
    pe = empty("pad", (px, py, TOPB), rot=(0, 0, yaw))
    rbox("pad_body", 0.105, 0.135, 0.005, 0.024, (0, 0, 0.0025), "white", bevel=0.0015, parent=pe)
    rbox("pad_inner", 0.085, 0.115, 0.002, 0.018, (0, 0, 0.0055), "cream", bevel=0.0006, parent=pe, segments=1)
    # plain pictogram: torso outline hint (a rounded green patch and a small accent dot where the pad goes)
    rbox("pad_mark", 0.040, 0.052, 0.0012, 0.012, (0, -0.012, 0.0068), "green", bevel=0, parent=pe)
    cyl("pad_dot", 0.006, 0.0012, ((-0.008, 0.008)[i], (-0.002, -0.024)[i], 0.0076), "white", parent=pe, verts=14)
    box("pad_tab", (0.022, 0.020, 0.007), (0, 0.062, 0.0035), "paint", bevel=0.002, parent=pe)
    c, s = math.cos(yaw), math.sin(yaw)
    pad_tabs.append((px - s * 0.074, py + c * 0.074, TOPB + 0.004))

# lead: plug -> down to the crate top -> coil -> splitter -> two pad wires
plug_l = (-0.098, FS - 0.033, ZC - 0.030)
pw = rot2((plug_l[1], plug_l[2]), TILT)
plug_w = (AX + plug_l[0], oy + pw[0], PZ + pw[1])
pd = rot2((plug_l[1] - 0.03, plug_l[2] - 0.004), TILT)
c0 = (B_CX - 0.150, B_CY - 0.005, TOPB + 0.014)
c1 = (B_CX - 0.170, B_CY - 0.105, TOPB + 0.014)
lead_in = smooth([plug_w, (AX + plug_l[0] - 0.004, oy + pd[0], PZ + pd[1]), (B_CX - 0.125, B_CY + 0.035, TOPB + 0.030), c0], 8)
v0, v1 = Vector(c0), Vector(c1)
ax = (v1 - v0).normalized()
u = ax.cross(Vector((0, 0, 1))).normalized()
TURNS, CRAD = 13, 0.0095
coil = []
for k in range(TURNS * 12 + 1):
    t = k / (TURNS * 12)
    a = 2 * math.pi * TURNS * t
    p = v0.lerp(v1, t) + u * (CRAD * math.sin(a)) + Vector((0, 0, 1)) * (CRAD * (1 - math.cos(a)) - CRAD + 0.0)
    coil.append((p.x, p.y, p.z))
split = (B_CX - 0.150, B_CY - 0.060 - 0.085, TOPB + 0.006)
split = (B_CX - 0.125, B_CY - 0.030, TOPB + 0.005)
tube("aed_lead", lead_in[:-1] + coil, 0.0026, "black")
# coil lies on the crate: lowest point of the helix is TOPB + 0.014 - CRAD - 0.0026 -> just above the top
out = smooth([c1, (c1[0] + 0.012, c1[1] - 0.035, TOPB + 0.005), (B_CX - 0.120, B_CY - 0.215, TOPB + 0.004), (B_CX - 0.02, B_CY - 0.228, TOPB + 0.004)], 8)
tube("aed_lead_out", out, 0.0026, "black")
sp = out[-1]
box("lead_split", (0.022, 0.012, 0.008), (sp[0] + 0.006, sp[1], TOPB + 0.004), "black", bevel=0.003)
# pad wires leave the splitter, loop round the front and come back to each pad's tab (tabs face the AED)
for i, tab in enumerate(pad_tabs):
    side = (-1, 1)[i]
    mid = [(sp[0] + 0.02, sp[1] + 0.004 * side, TOPB + 0.003)]
    if i == 0:
        w = [mid[0], (B_CX + 0.02, B_CY - 0.21, TOPB + 0.003), (B_CX + 0.022, B_CY - 0.10, TOPB + 0.003), (B_CX + 0.016, B_CY - 0.045, TOPB + 0.003),
             (tab[0] + 0.02, tab[1] + 0.03, TOPB + 0.003), (tab[0], tab[1] + 0.012, TOPB + 0.004), tab]
    else:
        w = [mid[0], (B_CX + 0.10, B_CY - 0.222, TOPB + 0.003), (B_CX + 0.175, B_CY - 0.18, TOPB + 0.003), (B_CX + 0.178, B_CY - 0.07, TOPB + 0.003),
             (tab[0] + 0.03, tab[1] + 0.03, TOPB + 0.003), (tab[0] + 0.004, tab[1] + 0.014, TOPB + 0.004), tab]
    tube("pad_wire", smooth(w, 8), 0.0018, "white" if i else "cream")

# ================================================================ first aid sign on a post
SX, SY = -0.535 + DX, 0.20
lathe("sign_base", [(0, 0), (0.105, 0), (0.112, 0.006), (0.112, 0.014), (0.100, 0.024), (0.035, 0.034), (0.024, 0.050), (0, 0.050)], (SX, SY, 0), "chassis", axis='Z', steps=40)
cyl("sign_collar", 0.022, 0.035, (SX, SY, 0.060), "steel", bevel=0.004, verts=24)
cyl("sign_post", 0.0135, 0.90, (SX, SY, 0.49), "steel", verts=20)
cyl("sign_cap", 0.016, 0.012, (SX, SY, 0.944), "black", bevel=0.004, verts=20)
sg = empty("sign", (SX, SY, 0.845), rot=(0, 0, R(14)))
SS = 0.27
rbox("sign_plate", SS, SS, 0.010, 0.030, (0, -0.022, 0), "white", bevel=0.003, parent=sg, plane='XZ')
rbox("sign_green", SS - 0.024, SS - 0.024, 0.006, 0.020, (0, -0.0275, 0), "green", bevel=0.0015, parent=sg, plane='XZ')
for s in ((0.150, 0.050), (0.050, 0.150)):
    box("sign_cross", (s[0], 0.006, s[1]), (0, -0.031, 0), "white", bevel=0.0015, parent=sg)
for z in (-0.075, 0.075):
    box("sign_clamp", (0.060, 0.022, 0.026), (0, -0.008, z), "steel", bevel=0.004, parent=sg)
    box("sign_clamp_back", (0.046, 0.012, 0.026), (0, 0.016, z), "steel", bevel=0.004, parent=sg)
    for sx in (-1, 1):
        cyl("sign_bolt", 0.004, 0.044, (sx * 0.022, 0.002, z), "chrome", axis='Y', parent=sg, verts=8)

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "firstaid.glb"))
