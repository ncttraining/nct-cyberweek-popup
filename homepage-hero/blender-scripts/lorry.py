import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import bar3d, rod3d, arch, FRAMES
import bmesh
reset()
R = math.radians


# ---------------------------------------------------------------- own helpers
def rrect(hw, yf, yr, z, rf=0.2, rr=0.06, n=5):
    """Plan outline (rounded rectangle) at height z: half width hw, front yf, rear yr, front/rear corner radii."""
    pts = []
    for cx, cy, r, a0 in ((hw - rr, yr - rr, rr, 0), (-hw + rr, yr - rr, rr, 90), (-hw + rf, yf + rf, rf, 180), (hw - rf, yf + rf, rf, 270)):
        for i in range(n + 1):
            a = R(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    return pts


def loft(name, sections, material, bevel=0.0, parent=None, segments=2):
    """Skin a stack of same-length outlines into a closed solid."""
    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in s] for s in sections]
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    from nctlib import _new_obj, _finish
    return _finish(_new_obj(name, bm), material, bevel, parent, segments=segments)


def b0(name, size, loc, material, parent=None, rot=(0, 0, 0)):
    return box(name, size, loc, material, bevel=0, parent=parent, rot=rot)


def b1(name, size, loc, material, bevel=0.01, parent=None, rot=(0, 0, 0)):
    return box(name, size, loc, material, bevel=bevel, parent=parent, rot=rot, segments=1)


def coil(name, p0, p1, sag, turns, rc, rt, material):
    """A coiled (suzie) line from p0 to p1 that droops by sag."""
    a, b = Vector(p0), Vector(p1)
    def P(t):
        p = a.lerp(b, t)
        p.z -= sag * 4 * t * (1 - t)
        return p
    pts = [tuple(a)]
    N = turns * 7
    for i in range(N + 1):
        t = 0.08 + 0.84 * i / N
        T = (P(min(t + 0.01, 1)) - P(max(t - 0.01, 0))).normalized()
        n1 = T.cross(Vector((1, 0, 0))).normalized()
        n2 = T.cross(n1)
        ph = 2 * math.pi * turns * i / N
        ramp = min(1.0, i / 6, (N - i) / 6)
        pts.append(tuple(P(t) + rc * ramp * (math.cos(ph) * n1 + math.sin(ph) * n2)))
    pts.append(tuple(b))
    return tube(name, pts, rt, material, resolution=1)


# ---------------------------------------------------------------- layout
WR = 0.525                       # wheel radius (1.05 m dia)
F = -8.25                        # very front (bumper)
CF, CR = -8.20, -6.05            # cab front face / rear wall
HW = 1.25                        # cab half width
AX1, AX2 = -6.90, -3.10          # tractor axles (3.8 m wheelbase)
TF, TB = -5.35, 8.25             # trailer front / back (13.6 m)
KP = -3.75                       # kingpin / fifth wheel
TAX = (2.64, 3.95, 5.26)         # trailer axles
DECK = 1.34                      # trailer floor top
SILL, HEAD = 2.02, 2.92          # window band
BW = 1.275                       # trailer half width


def spin(e):
    for f in FRAMES:
        key(e, f, rot=(2 * math.pi * f / FRAME_WORK, 0, 0))


_wheel = wheel
def wheel(*a, **k):
    """nctlib wheel, with the bevels taken off the tiny tread lugs and hub discs (they are small in this picture)."""
    t = _wheel(*a, **k)
    for c in t.children:
        if "_tr" in c.name or "_hub" in c.name:
            c.modifiers.clear()
    return t


# ---------------------------------------------------------------- wheels (one keyed pivot per axle)
ax = empty("axle_steer", (0, AX1, WR)); spin(ax)
for sx in (-1, 1):
    wheel("w_steer", WR, 0.32, (sx * 1.085, 0, 0), rim="rim", parent=ax, tread=True)
    cyl("hub_steer", 0.17, 0.10, (sx * 1.25, 0, 0), "chassis", axis='X', bevel=0.025, parent=ax, verts=24)
    cyl("hub_steer2", 0.085, 0.05, (sx * 1.31, 0, 0), "plastic", axis='X', bevel=0.012, parent=ax, verts=20)
cyl("stub_steer", 0.06, 2.0, (0, 0, 0), "chassis", axis='X', parent=ax, verts=16)

ax = empty("axle_drive", (0, AX2, WR)); spin(ax)
for sx in (-1, 1):
    wheel("w_drive_o", WR, 0.30, (sx * 1.095, 0, 0), rim="rim", parent=ax, tread=True)
    wheel("w_drive_i", WR, 0.30, (sx * 0.775, 0, 0), rim="rim", parent=ax, tread=True)
    cyl("hub_drive", 0.20, 0.16, (sx * 1.15, 0, 0), "chassis", axis='X', bevel=0.03, parent=ax, verts=24)
    cyl("hub_drive2", 0.10, 0.06, (sx * 1.245, 0, 0), "plastic", axis='X', bevel=0.015, parent=ax, verts=20)
cyl("stub_drive", 0.07, 2.0, (0, 0, 0), "chassis", axis='X', parent=ax, verts=16)

for i, ay in enumerate(TAX):
    ax = empty(f"axle_trailer{i + 1}", (0, ay, WR)); spin(ax)
    for sx in (-1, 1):
        wheel("w_tr", WR, 0.385, (sx * 1.05, 0, 0), rim="rim", parent=ax, tread=True)
        cyl("hub_tr", 0.15, 0.10, (sx * 1.24, 0, 0), "chassis", axis='X', bevel=0.025, parent=ax, verts=24)
        cyl("hub_tr2", 0.075, 0.05, (sx * 1.30, 0, 0), "plastic", axis='X', bevel=0.012, parent=ax, verts=20)
    cyl("stub_tr", 0.065, 2.0, (0, 0, 0), "chassis", axis='X', parent=ax, verts=16)

# ================================================================ TRACTOR UNIT
# ---------------------------------------------------------------- chassis
for sx in (-1, 1):
    b1("rail", (0.09, 5.75, 0.28), (sx * 0.42, -5.15, 0.89), "chassis", 0.012)
    b1("rail_flange", (0.16, 5.75, 0.025), (sx * 0.40, -5.15, 1.03), "chassis", 0.004)
for y in (-7.9, -6.1, -4.6, -2.32):
    b1("xmember", (0.84, 0.10, 0.22), (0, y, 0.89), "chassis", 0.012)
# engine / gearbox under the cab, propshaft, diff
box("engine", (0.74, 1.5, 0.72), (0, -7.25, 0.80), "chassis", bevel=0.08)
box("sump", (0.5, 0.9, 0.2), (0, -7.25, 0.42), "plastic", bevel=0.05)
box("gearbox", (0.5, 0.95, 0.5), (0, -6.05, 0.72), "plastic", bevel=0.1)
cyl("propshaft", 0.05, 2.3, (0, -4.45, 0.62), "steel", axis='Y', verts=16)
cyl("diff", 0.25, 0.42, (0, AX2, WR), "chassis", axis='Y', bevel=0.09)
box("drive_axle", (1.3, 0.2, 0.2), (0, AX2, WR), "chassis", bevel=0.05)
box("steer_beam", (1.75, 0.12, 0.13), (0, AX1, WR - 0.04), "chassis", bevel=0.03)
for sx in (-1, 1):
    # leaf springs front, air bags rear
    profile("leaf", [(-0.75, 0.16)] + arc_pts(0, 1.6, 1.62, 242, 298, 8) + [(0.75, 0.21)] + arc_pts(0, 1.6, 1.57, 298, 242, 8), 0.09,
            (sx * 0.42, AX1, WR - 0.05), "plastic", bevel=0.004)
    for dy in (-0.42, 0.42):
        cyl("airbag", 0.13, 0.26, (sx * 0.42, AX2 + dy, 0.66), "rubber", bevel=0.03, verts=20)
        b1("bagplate", (0.3, 0.3, 0.03), (sx * 0.42, AX2 + dy, 0.52), "chassis", 0.005)
    b1("trail_arm", (0.08, 1.2, 0.09), (sx * 0.42, AX2, 0.49), "chassis", 0.01)
    cyl("damper", 0.035, 0.5, (sx * 0.55, AX1 + 0.25, 0.75), "steel", verts=12)
# catwalk and rear end
b1("catwalk", (1.0, 1.25, 0.03), (0, -5.38, 1.06), "steel", 0.006)
for i in range(6):
    b0("catwalk_rib", (0.96, 0.02, 0.012), (0, -5.9 + i * 0.21, 1.08), "chassis")
b1("tail_xm", (2.3, 0.07, 0.14), (0, -2.33, 0.93), "chassis", 0.012)
for sx in (-1, 1):
    b1("t_tail", (0.32, 0.04, 0.12), (sx * 0.93, -2.29, 0.93), "tail", 0.008)
    b1("t_tail_amb", (0.1, 0.04, 0.12), (sx * 0.68, -2.29, 0.93), "beacon", 0.008)
    b1("t_flap", (0.62, 0.02, 0.5), (sx * 0.935, -2.37, 0.55), "rubber", 0.004)
    # drive wheel mudguards: curved top over the twins, flat ends
    arch("mg_drive", WR + 0.06, WR + 0.085, 8, 172, 0.68, (sx * 0.935, AX2, WR), "plastic", bevel=0.01)
    for dy in (-1, 1):
        rod3d("mg_stay", (sx * 0.46, AX2 + dy * 0.5, 0.98), (sx * 0.95, AX2 + dy * 0.5, 0.86), 0.02, "chassis", verts=10)

# fifth wheel: pedestal, plate with rear V notch, lead-in ramps
b1("fw_sub", (1.0, 1.0, 0.045), (0, KP, 1.055), "chassis", 0.008)
for sx in (-1, 1):
    profile("fw_ped", [(-0.22, 0), (0.22, 0), (0.1, 0.09), (-0.1, 0.09)], 0.1, (sx * 0.38, KP, 1.075), "chassis", bevel=0.008, segments=1)
fwp = arc_pts(0, 0, 0.48, 150, 390, 22) + [(0.34, 0.52), (0.09, 0.50), (0.05, 0.05), (-0.05, 0.05), (-0.09, 0.50), (-0.34, 0.52)]
profile("fw_plate", fwp, 0.045, (0, KP, 1.175), "plastic", bevel=0.01, plane='XY', segments=1)
b1("fw_handle", (0.3, 0.03, 0.03), (0.6, KP + 0.1, 1.16), "steel", 0.006)

# fuel tank (left), battery / exhaust box and air tanks (right)
cyl("tank", 0.33, 1.5, (-0.90, -5.15, 0.72), "steel", axis='Y', bevel=0.06, verts=36)
for dy in (-0.45, 0.45):
    cyl("tank_strap", 0.337, 0.06, (-0.90, -5.15 + dy, 0.72), "chassis", axis='Y', verts=36)
    b1("tank_brk", (0.5, 0.07, 0.08), (-0.62, -5.15 + dy, 0.82), "chassis", 0.01)
cyl("tank_cap", 0.055, 0.05, (-1.1, -5.65, 0.99), "black", bevel=0.01, verts=16, rot=(0, R(-40), 0))
box("exbox", (0.62, 1.0, 0.62), (0.93, -5.42, 0.70), "plastic", bevel=0.05)
b1("exbox_lid", (0.02, 0.8, 0.42), (1.245, -5.42, 0.72), "chassis", 0.01)
for k in range(4):
    b0("exbox_louvre", (0.012, 0.6, 0.025), (1.258, -5.42, 0.58 + k * 0.09), "plastic")
b1("exbox_step", (0.1, 0.8, 0.03), (1.2, -5.42, 1.02), "steel", 0.006)
for z in (0.55, 0.85):
    cyl("airtank", 0.13, 0.7, (0.86, -4.42, z), "chassis", axis='Y', bevel=0.05, verts=20)
box("adblue", (0.42, 0.5, 0.5), (-0.95, -4.05, 0.72), "plastic", bevel=0.07)
cyl("adblue_cap", 0.05, 0.05, (-1.0, -4.15, 0.98), "screen", bevel=0.01, verts=16)
# exhaust stack up the back of the cab, with heat shield
tube("stack", [(0.95, -5.6, 0.95), (0.95, -5.6, 1.5), (0.95, -5.6, 3.3), (0.95, -5.6, 3.62), (0.95, -5.52, 3.72)], 0.065, "steel")
cyl("stack_shield", 0.09, 1.3, (0.95, -5.6, 2.2), "chassis", verts=20, bevel=0.01)
for z in (1.5, 2.9, 3.4):
    b1("stack_brk", (0.06, 0.42, 0.05), (0.95, -5.82, z), "chassis", 0.008)
# air intake snorkel (other side)
box("intake", (0.2, 0.16, 1.9), (-0.95, -5.93, 2.4), "plastic", bevel=0.05)
box("intake_top", (0.26, 0.2, 0.3), (-0.95, -5.93, 3.4), "plastic", bevel=0.06)

# ---------------------------------------------------------------- cab
# bumper
loft("bumper", [rrect(1.26, F + 0.03, -7.5, 0.28, 0.2), rrect(1.265, F, -7.5, 0.36, 0.22), rrect(1.265, F, -7.5, 0.68, 0.22), rrect(1.255, F + 0.04, -7.5, 0.76, 0.2)], "chassis", bevel=0.012)
b1("bumper_lip", (2.0, 0.06, 0.07), (0, F - 0.0, 0.30), "plastic", 0.015)
for sx in (-1, 1):
    box("lamp_bezel", (0.56, 0.03, 0.25), (sx * 0.76, F - 0.004, 0.54), "black", bevel=0.03)
    box("headlamp", (0.27, 0.03, 0.17), (sx * 0.87, F - 0.012, 0.54), "lamp", bevel=0.03)
    cyl("headlamp2", 0.075, 0.03, (sx * 0.62, F - 0.012, 0.54), "lamp", axis='Y', bevel=0.008, verts=20)
    cyl("headlamp_ring", 0.09, 0.02, (sx * 0.62, F - 0.008, 0.54), "chrome", axis='Y', verts=20)
    b1("indicator", (0.035, 0.1, 0.12), (sx * 1.262, F + 0.2, 0.56), "beacon", 0.008)
    cyl("fog", 0.04, 0.03, (sx * 0.98, F - 0.003, 0.37), "lamp", axis='Y', bevel=0.006, verts=16)
b1("plate", (0.52, 0.012, 0.11), (0, F - 0.004, 0.50), "decal", 0.004)
b1("bumper_step", (0.8, 0.06, 0.03), (0, F + 0.0, 0.70), "steel", 0.006)
# lower front module (entry steps each side) flush with the shell above
loft("front_mod", [rrect(HW, CF, -7.5, 0.72, 0.2), rrect(HW, CF, -7.5, 1.27, 0.2)], "accent", bevel=0.01)
# main shell, floor to window sill
loft("shell", [rrect(HW, CF, CR, 1.25, 0.2), rrect(HW, CF, CR, 1.85, 0.2), rrect(HW, CF + 0.015, CR, SILL, 0.2)], "accent", bevel=0.012)
# skirt behind the front wheel
for sx in (-1, 1):
    box("skirt", (0.26, 0.34, 0.75), (sx * 1.12, -6.22, 0.89), "accent", bevel=0.03)
    arch("arch_steer", WR + 0.07, WR + 0.16, 0, 180, 0.34, (sx * 1.085, AX1, WR), "plastic", bevel=0.015)
    b1("arch_liner", (0.02, 1.2, 0.6), (sx * 0.9, AX1, 0.98), "black", 0.005)
    b1("arch_flap", (0.3, 0.02, 0.3), (sx * 1.09, -6.33, 0.38), "rubber", 0.004)
    # step well and treads
    b1("stepwell", (0.02, 0.44, 0.84), (sx * 1.252, -7.76, 0.80), "black", 0.006)
    for z in (0.47, 0.84):
        b1("step", (0.07, 0.40, 0.03), (sx * 1.27, -7.76, z), "steel", 0.006)
    # door seams and handle
    b0("seam_r", (0.008, 0.014, 1.66), (sx * 1.251, -6.98, 2.09), "black")
    b0("seam_f", (0.008, 0.014, 0.76), (sx * 1.251, -8.0, 1.64), "black")
    b0("seam_b", (0.008, 1.02, 0.014), (sx * 1.251, -7.49, 1.27), "black")
    b1("handle", (0.03, 0.16, 0.05), (sx * 1.262, -7.12, 1.62), "black", 0.008)
    b0("side_trim", (0.01, 0.9, 0.04), (sx * 1.252, -6.52, 1.45), "plastic")
# grille: dark trapezoid with slats inside a raised magenta surround
gp = [(-0.92, 0.86), (0.92, 0.86), (0.80, 1.78), (-0.80, 1.78)]
profile("grille_back", gp, 0.02, (0, CF - 0.004, 0), "black", bevel=0, plane='XZ')
for k in range(8):
    z = 0.93 + k * 0.112
    w = 1.84 - (z - 0.86) * 0.26 - 0.12
    b1("grille_slat", (w, 0.03, 0.045), (0, CF - 0.02, z), "plastic", 0.008)
for sx in (-1, 1):
    bar3d("grille_side", (sx * 0.95, CF - 0.012, 0.84), (sx * 0.83, CF - 0.012, 1.80), 0.07, 0.04, "accent", bevel=0.012, segments=1)
b1("grille_top", (1.74, 0.04, 0.07), (0, CF - 0.012, 1.81), "accent", 0.012)
b1("grille_badge", (0.26, 0.02, 0.06), (0, CF - 0.04, 1.66), "chrome", 0.01)
b0("front_seam", (2.1, 0.008, 0.012), (0, CF - 0.001, 0.80), "black")
for sx in (-1, 1):
    b0("corner_vent", (0.16, 0.01, 0.5), (sx * 0.99, CF - 0.002, 1.3), "black")
    b0("bumper_grille", (0.5, 0.012, 0.09), (sx * 0.3, F - 0.002, 0.33), "black")
b1("wiper_panel", (2.1, 0.02, 0.12), (0, CF - 0.002, 1.92), "black", 0.01)
# interior visible through the glass
b0("int_floor", (2.3, 1.2, 0.02), (0, -7.55, SILL + 0.005), "vinyl")
box("dash", (2.3, 0.38, 0.16), (0, -7.92, SILL + 0.06), "plastic", bevel=0.05)
box("binnacle", (0.5, 0.2, 0.14), (-0.68, -7.86, SILL + 0.19), "plastic", bevel=0.04)
st = empty("steer_col", (-0.68, -7.66, SILL + 0.2), rot=(R(-62), 0, 0))
from tpmlib import ring
ring("st_wheel", 0.21, 0.018, (0, 0, 0.0), "vinyl", parent=st)
cyl("st_hub", 0.05, 0.04, (0, 0, -0.02), "vinyl", parent=st, verts=14)
for a in (90, 210, 330):
    rod3d("st_spoke", (0, 0, -0.02), (0.2 * math.cos(R(a)), 0.2 * math.sin(R(a)), 0), 0.012, "vinyl", parent=st, verts=8)
for sx in (-1, 1):
    box("seat_back", (0.5, 0.12, 0.62), (sx * 0.68, -7.18, SILL + 0.3), "vinyl", bevel=0.05, rot=(R(-8), 0, 0))
    box("headrest", (0.26, 0.1, 0.18), (sx * 0.68, -7.14, SILL + 0.7), "vinyl", bevel=0.04)
# sleeper block behind the doors, pillars, roof
loft("sleeper", [rrect(HW, -7.0, CR, SILL - 0.02, 0.03), rrect(HW, -7.0, CR, HEAD + 0.02, 0.03)], "accent", bevel=0.01)
b0("int_back", (2.36, 0.02, HEAD - SILL), (0, -7.012, (SILL + HEAD) / 2), "vinyl")
b0("int_head", (2.3, 1.0, 0.02), (0, -7.5, HEAD - 0.012), "vinyl")
for sx in (-1, 1):
    b0("cab_stripe", (0.006, 1.92, 0.1), (sx * 1.2515, -7.03, 1.9), "paint")
    b0("cab_stripe2", (0.006, 1.92, 0.03), (sx * 1.2515, -7.03, 1.80), "cream")
    b1("sleeper_win", (0.012, 0.42, 0.34), (sx * 1.249, -6.5, 2.55), "black", 0.004)
    b1("sleeper_glass", (0.012, 0.36, 0.28), (sx * 1.253, -6.5, 2.55), "glass", 0.004)
    cyl("horn", 0.035, 0.5, (sx * 0.55, -7.35, 3.52), "chrome", axis='Y', radius2=0.07, verts=14)
    b1("horn_ft", (0.05, 0.08, 0.06), (sx * 0.55, -7.2, 3.47), "black", 0.006)
    cyl("beacon_base", 0.07, 0.03, (sx * 0.95, -7.55, 3.47), "black", verts=16)
    cyl("beacon", 0.06, 0.1, (sx * 0.95, -7.55, 3.53), "beacon", bevel=0.02, verts=16)
WS0, WS1 = (CF + 0.07, SILL - 0.03), (CF + 0.27, HEAD + 0.03)       # windscreen line (y, z)
for sx in (-1, 1):
    bar3d("a_pillar", (sx * 1.185, *WS0), (sx * 1.185, *WS1), 0.13, 0.14, "accent", bevel=0.045, segments=3)
    profile("side_glass", [(WS0[0] + 0.07, SILL), (-6.98, SILL), (-6.98, HEAD), (WS1[0] + 0.07, HEAD)], 0.012, (sx * 1.225, 0, 0), "glass", bevel=0)
    b0("quarter_bar", (0.03, 0.03, 0.9), (sx * 1.228, -7.72, 2.47), "black")
bar3d("windscreen", (0, *WS0), (0, *WS1), 2.3, 0.012, "glass", bevel=0)
bar3d("ws_sill", (0, WS0[0] - 0.012, SILL - 0.02), (0, WS0[0] + 0.003, SILL + 0.05), 2.26, 0.014, "black", bevel=0)
bar3d("ws_head", (0, WS1[0] - 0.027, HEAD - 0.06), (0, WS1[0] - 0.012, HEAD + 0.01), 2.26, 0.014, "black", bevel=0)
bar3d("ws_centre", (0, WS0[0] - 0.01, WS0[1]), (0, WS1[0] - 0.01, WS1[1]), 0.02, 0.012, "black", bevel=0)
for sx, x0 in ((-1, -0.75), (1, 0.35)):
    rod3d("wiper", (x0, WS0[0] - 0.03, SILL + 0.02), (x0 + 0.42, WS0[0] + 0.1, SILL + 0.52), 0.012, "black", verts=8)
loft("roof", [rrect(HW, CF + 0.20, CR, HEAD, 0.2), rrect(HW, CF + 0.22, CR, 3.2, 0.2), rrect(1.21, CF + 0.34, CR, 3.4, 0.22, 0.1), rrect(1.1, CF + 0.55, CR - 0.05, 3.47, 0.25, 0.12)], "accent", bevel=0.012)
# sun visor and roof marker lamps
profile("visor", [(CF + 0.22, 3.06), (CF - 0.16, 2.90), (CF - 0.17, 2.86), (CF + 0.22, 2.96)], 2.36, (0, 0, 0), "black", bevel=0.012, segments=1)
for sx in (-1, 1):
    b1("visor_end", (0.05, 0.36, 0.14), (sx * 1.19, CF + 0.04, 2.97), "black", 0.012, rot=(R(-22), 0, 0))
for x in (-0.9, -0.3, 0.3, 0.9):
    b1("roof_lamp", (0.12, 0.03, 0.035), (x, CF + 0.225, 3.25), "lamp", 0.006)
# mirrors on arms
for sx in (-1, 1):
    tube("mirror_arm", [(sx * 1.2, CF + 0.16, 2.84), (sx * 1.5, CF - 0.02, 2.8), (sx * 1.5, CF - 0.02, 2.08), (sx * 1.2, CF + 0.1, 2.04)], 0.016, "black")
    box("mirror", (0.1, 0.2, 0.46), (sx * 1.53, CF - 0.01, 2.52), "black", bevel=0.04)
    b0("mirror_glass", (0.085, 0.006, 0.4), (sx * 1.53, CF + 0.092, 2.52), "chrome")
    box("mirror_wide", (0.1, 0.18, 0.2), (sx * 1.53, CF - 0.01, 2.17), "black", bevel=0.04)
    b0("mirror_wglass", (0.085, 0.006, 0.15), (sx * 1.53, CF + 0.082, 2.17), "chrome")
# roof air deflector and side fairings (to trailer height)
loft("deflector", [rrect(1.2, -7.7, CR + 0.03, 3.40, 0.3, 0.05), rrect(1.21, -7.3, CR + 0.03, 3.62, 0.3, 0.05), rrect(1.22, -6.85, CR + 0.03, 3.82, 0.3, 0.05),
                   rrect(1.22, -6.5, CR + 0.03, 3.94, 0.25, 0.05), rrect(1.2, -6.25, CR + 0.01, 3.99, 0.15, 0.05)], "accent", bevel=0.012)
for sx in (-1, 1):
    profile("fairing", [(CR - 0.05, 1.3), (-5.76, 1.3), (-5.76, 3.9), (-5.9, 3.98), (CR - 0.05, 3.98)], 0.05, (sx * 1.225, 0, 0), "accent", bevel=0.015)
b1("cab_back", (2.3, 0.04, 2.0), (0, CR + 0.01, 2.35), "plastic", 0.01)

# suzie coils, cab back to trailer bulkhead
b1("suzie_rack", (0.5, 0.05, 0.1), (0, CR + 0.05, 2.25), "steel", 0.008)
b1("suzie_plate", (0.6, 0.04, 0.16), (0, TF - 0.02, 1.62), "steel", 0.008)
for x, m in ((-0.16, "red"), (0, "hazard"), (0.16, "black")):
    coil("suzie", (x, CR + 0.08, 2.22), (x * 1.5, TF - 0.04, 1.62), 0.22, 7, 0.035, 0.009, m)
    cyl("suzie_plug", 0.025, 0.06, (x * 1.5, TF - 0.06, 1.62), "steel", axis='Y', verts=10)

# ================================================================ TRAILER
L = TB - TF
YC = (TF + TB) / 2
# floor, raves, chassis beams with neck
b0("floor", (2.46, L - 0.1, 0.12), (0, YC, DECK - 0.06), "chassis")
for sx in (-1, 1):
    b1("rave", (0.05, L, 0.17), (sx * (BW - 0.025), YC, DECK - 0.075), "chassis", 0.012)
    profile("beam", [(TF + 0.4, 1.20), (-2.5, 1.20), (-1.9, 0.86), (8.05, 0.86), (8.05, 1.24), (TF + 0.4, 1.24)], 0.12, (sx * 0.5, 0, 0), "chassis", bevel=0.01, segments=1)
    b1("beam_flange", (0.2, 9.9, 0.025), (sx * 0.5, 3.1, 0.86), "chassis", 0.004)
    for k in range(7):
        b0("marker", (0.015, 0.11, 0.05), (sx * (BW + 0.005), TF + 0.9 + k * 1.95, DECK - 0.07), "beacon")
y = TF + 0.5
while y < 8.1:
    b0("xm", (2.44, 0.07, 0.1), (0, y, 1.17 if y > -1.9 else 1.215), "chassis") if y > -1.9 else None
    y += 0.62
box("rub_plate", (1.3, 1.9, 0.03), (0, KP + 0.1, 1.212), "steel", bevel=0.01, segments=1)
cyl("kingpin", 0.04, 0.1, (0, KP, 1.16), "steel", verts=12)

# body: bulkhead, roof, cant rails, posts
box("bulkhead", (2 * BW, 0.08, 4.0 - DECK), (0, TF + 0.04, (4.0 + DECK) / 2), "cream", bevel=0.01, segments=1)
for z in (2.0, 2.7, 3.4):
    b1("bulk_rib", (2.3, 0.03, 0.08), (0, TF - 0.012, z), "white", 0.01)
b1("bulk_band", (2.3, 0.012, 0.5), (0, TF - 0.004, 2.42), "accent", 0.004)
b0("roof_t", (2 * BW - 0.04, L - 0.04, 0.05), (0, YC, 3.972), "cream")
for sx in (-1, 1):
    box("cantrail", (0.07, L, 0.17), (sx * (BW - 0.035), YC, 3.915), "white", bevel=0.015, segments=2)
    for yy in (TF + 0.06, TB - 0.06):
        box("post", (0.12, 0.12, 4.0 - DECK), (sx * (BW - 0.06), yy, (4.0 + DECK) / 2), "white", bevel=0.015, segments=2)
    # curtain with livery bands, straps and buckles
    cx = sx * (BW - 0.03)
    b0("curtain", (0.03, L - 0.22, 3.84 - DECK), (cx, YC, (3.84 + DECK) / 2), "cream")
    b0("band_accent", (0.006, L - 0.24, 0.62), (cx + sx * 0.015, YC, 2.48), "accent")
    b0("band_paint", (0.006, L - 0.24, 0.17), (cx + sx * 0.015, YC, 1.93), "paint")
    n = 22
    for k in range(n):
        yy = TF + 0.42 + k * (L - 0.84) / (n - 1)
        b0("strap", (0.006, 0.05, 3.84 - DECK - 0.04), (cx + sx * 0.02, yy, (3.84 + DECK) / 2), "plum")
        b0("buckle", (0.02, 0.07, 0.11), (cx + sx * 0.025, yy, 1.52), "steel")
        b0("strap_hook", (0.012, 0.035, 0.1), (sx * (BW + 0.004), yy, DECK - 0.1), "steel")
    # curtain tensioner poles at each end
    for yy in (TF + 0.16, TB - 0.16):
        cyl("tension_pole", 0.03, 3.84 - DECK, (sx * (BW - 0.02), yy, (3.84 + DECK) / 2), "steel", verts=12)
    b1("ratchet", (0.05, 0.08, 0.2), (sx * (BW + 0.0), TB - 0.16, DECK - 0.1), "steel", 0.008)

for k in range(11):
    b0("roof_rib", (2 * BW - 0.1, 0.05, 0.012), (0, TF + 0.7 + k * 1.22, 4.0), "white")
# rear frame, doors, lock bars
b1("rear_head", (2 * BW, 0.12, 0.17), (0, TB - 0.06, 3.915), "white", 0.015)
b1("rear_sill", (2 * BW, 0.12, 0.17), (0, TB - 0.06, DECK - 0.075), "chassis", 0.012)
for sx in (-1, 1):
    box("door", (1.13, 0.04, 3.84 - DECK - 0.02), (sx * 0.575, TB - 0.02, (3.84 + DECK) / 2), "cream", bevel=0.012, segments=1)
    for x in (0.2, 0.9):
        cyl("lockbar", 0.018, 3.84 - DECK + 0.1, (sx * x, TB + 0.022, (3.84 + DECK) / 2), "steel", verts=10)
        for z in (DECK + 0.02, 3.82, 2.0, 3.0):
            b0("lock_keep", (0.08, 0.03, 0.05), (sx * x, TB + 0.012, z), "steel")
        b1("lock_handle", (0.3, 0.02, 0.035), (sx * (x - 0.13), TB + 0.04, 1.9), "steel", 0.006)
    for z in (1.6, 2.3, 3.0, 3.6):
        b0("hinge", (0.16, 0.025, 0.07), (sx * 1.13, TB + 0.008, z), "steel")
    # marker boards
    b0("mboard", (0.56, 0.008, 0.2), (sx * 0.56, TB + 0.006, 1.52), "hazard")
    b0("mboard_r", (0.56, 0.01, 0.05), (sx * 0.56, TB + 0.007, 1.44), "red")
    b0("mboard_r2", (0.56, 0.01, 0.05), (sx * 0.56, TB + 0.007, 1.60), "red")
    b0("top_marker", (0.1, 0.02, 0.04), (sx * 1.1, TB + 0.005, 3.93), "tail")
# rear light panel and underrun bar
b1("light_panel", (2.46, 0.06, 0.2), (0, TB - 0.06, 1.08), "chassis", 0.01)
for sx in (-1, 1):
    b1("tail", (0.34, 0.03, 0.13), (sx * 0.98, TB - 0.022, 1.08), "tail", 0.01)
    b1("tail_amb", (0.13, 0.03, 0.13), (sx * 0.72, TB - 0.022, 1.08), "beacon", 0.01)
    b1("tail_rev", (0.1, 0.03, 0.13), (sx * 0.58, TB - 0.022, 1.08), "lamp", 0.01)
    b1("ur_stay", (0.08, 0.1, 0.5), (sx * 0.5, TB - 0.16, 0.7), "chassis", 0.01)
    rod3d("ur_brace", (sx * 0.5, 7.6, 0.9), (sx * 0.5, TB - 0.14, 0.5), 0.03, "chassis", verts=10)
    cyl("buffer", 0.06, 0.06, (sx * 0.5, TB - 0.0, 1.28), "rubber", axis='Y', bevel=0.01, verts=14)
b1("rplate", (0.52, 0.012, 0.11), (0, TB - 0.026, 1.08), "hazard", 0.004)
box("underrun", (2.4, 0.12, 0.12), (0, TB - 0.1, 0.5), "chassis", bevel=0.02)

# running gear
for ay in TAX:
    box("t_axle", (1.5, 0.14, 0.14), (0, ay, WR), "chassis", bevel=0.04)
    for sx in (-1, 1):
        profile("hanger", [(-0.62, 0.86), (-0.38, 0.86), (-0.42, 0.56), (-0.56, 0.56)], 0.1, (sx * 0.5, ay, 0), "chassis", bevel=0.01, segments=1)
        b1("t_arm", (0.09, 0.95, 0.09), (sx * 0.5, ay - 0.05, 0.53), "chassis", 0.012)
        cyl("t_bag", 0.14, 0.26, (sx * 0.5, ay + 0.34, 0.72), "rubber", bevel=0.035, verts=20)
        arch("t_mg", WR + 0.06, WR + 0.085, 12, 168, 0.44, (sx * 1.05, ay, WR), "plastic", bevel=0.01)
        rod3d("t_mgstay", (sx * 0.55, ay, 1.0), (sx * 1.05, ay, WR + 0.07), 0.018, "chassis", verts=8)
for sx in (-1, 1):
    b1("t_flap", (0.42, 0.02, 0.6), (sx * 1.05, TAX[2] + 0.66, 0.6), "rubber", 0.004)
    # landing legs
    box("leg_outer", (0.13, 0.13, 0.66), (sx * 0.78, -1.4, 0.9), "chassis", bevel=0.012, segments=1)
    box("leg_inner", (0.09, 0.09, 0.4), (sx * 0.78, -1.4, 0.48), "steel", bevel=0.008, segments=1)
    box("leg_foot", (0.26, 0.3, 0.035), (sx * 0.78, -1.4, 0.275), "chassis", bevel=0.01, segments=1)
    b1("leg_mount", (0.5, 0.2, 0.1), (sx * 0.62, -1.4, 1.17), "chassis", 0.01)
    rod3d("leg_brace", (sx * 0.78, -1.34, 0.72), (sx * 0.5, -0.7, 1.0), 0.022, "chassis", verts=8)
    # side underrun guards
    for z in (0.52, 0.86):
        box("side_guard", (0.035, 3.05, 0.11), (sx * (BW - 0.04), 0.5, z), "chassis", bevel=0.012, segments=1)
        box("side_guard_r", (0.035, 2.1, 0.11), (sx * (BW - 0.04), 7.05, z), "chassis", bevel=0.012, segments=1)
    for yy in (-0.8, 0.5, 1.8, 6.2, 7.9):
        b1("guard_post", (0.04, 0.07, 0.82), (sx * (BW - 0.08), yy, 0.86), "chassis", 0.008)
rod3d("leg_shaft", (-0.78, -1.4, 1.02), (0.78, -1.4, 1.02), 0.02, "steel", verts=8)
tube("leg_crank", [(-0.85, -1.4, 1.02), (-1.12, -1.4, 1.02), (-1.12, -1.4, 0.8), (-1.2, -1.4, 0.8)], 0.014, "steel")
rod3d("leg_tie", (-0.78, -1.4, 0.62), (0.78, -1.4, 0.62), 0.025, "chassis", verts=8)
# pallet locker (left) and spare wheel in a cradle (right), air tanks
box("locker", (0.62, 1.5, 0.52), (-0.88, 0.45, 0.74), "plastic", bevel=0.03)
b1("locker_door", (0.015, 1.36, 0.4), (-1.195, 0.45, 0.74), "chassis", 0.008)
b1("locker_latch", (0.02, 0.1, 0.04), (-1.205, 0.45, 0.88), "steel", 0.005)
sp = empty("spare_piv", (0.78, 0.45, 0.62), rot=(0, R(90), 0))
wheel("spare", WR, 0.385, (0, 0, 0), rim="rim", parent=sp, tread=False)
for dy in (-0.35, 0.35):
    b1("spare_cradle", (1.0, 0.05, 0.05), (0.75, 0.45 + dy, 0.40), "chassis", 0.008)
    b1("spare_hang", (0.05, 0.05, 0.5), (0.3, 0.45 + dy, 0.62), "chassis", 0.008)
for x in (-0.25, 0.25):
    cyl("t_airtank", 0.14, 0.8, (0, 1.6 + x * 1.4, 0.68), "chassis", axis='X', bevel=0.05, verts=20)

if os.environ.get("LSTAT"):
    dg = bpy.context.evaluated_depsgraph_get(); agg = {}; low = {}
    for o in bpy.context.scene.objects:
        if o.type != 'MESH': continue
        me = o.evaluated_get(dg).to_mesh(); me.calc_loop_triangles()
        k = o.name.split('.')[0]; agg[k] = agg.get(k, 0) + len(me.loop_triangles)
        mz = min((o.matrix_world @ v.co).z for v in me.vertices)
        if mz < 0.0: low[k] = min(low.get(k, 0), mz)
    print("TRIS", sorted(agg.items(), key=lambda kv: -kv[1])[:25]); print("LOW", low)
export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "lorry.glb"))
