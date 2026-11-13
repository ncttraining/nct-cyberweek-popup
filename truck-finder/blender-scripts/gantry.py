import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import *
from pg_common import *
from mathutils import Vector
reset()
R = math.radians

SPAN = 5.0                         # between leg centre lines
LX = SPAN / 2
BT, BD, BW = 4.10, 0.36, 0.20      # beam top, depth, flange width
BB = BT - BD                       # beam underside
FT = 0.02                          # flange thickness
LEG_TOP, LEG_BOT, Y_TOP, Y_BOT = 3.66, 0.37, 0.10, 0.85
X_REST, X_WORK = -0.6, 0.6         # trolley travel
HOOK_Z, HOIST = 1.15, 1.5          # hook bowl height at rest, height of lift


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lift(f):                       # lift first, travel overlapping the end of the lift
    return HOIST * smooth(f / 17.0)


def trav(f):
    return lerp(X_REST, X_WORK, smooth((f - 7) / 17.0))


def leg_y(z):
    return Y_TOP + (Y_BOT - Y_TOP) * (LEG_TOP - z) / (LEG_TOP - LEG_BOT)


def bolt(p, axis='Z', r=0.014, parent=None):
    cyl("bolt", r, 0.014, p, "steel", axis=axis, verts=6, parent=parent)


# ================================================================ main beam (I-section)
h, w, t = BD / 2, BW / 2, 0.007
I = [(-w, -h), (w, -h), (w, -h + FT), (t, -h + FT), (t, h - FT), (w, h - FT), (w, h), (-w, h), (-w, h - FT), (-t, h - FT), (-t, -h + FT), (-w, -h + FT)]
profile("beam", I, SPAN + 0.5, (0, 0, BT - h), "paint", bevel=0.004, plane='YZ', segments=1)
for sx in (-1, 1):
    box("beam_end", (0.014, BW + 0.01, BD + 0.01), (sx * (LX + 0.25), 0, BT - h), "hazard", bevel=0.003)
    for k in range(3):
        box("end_chev", (0.016, 0.03, BD * 1.2), (sx * (LX + 0.25), -0.07 + k * 0.07, BT - h), "chassis", bevel=0, rot=(R(30), 0, 0)).scale = (1, 1, 0.8)
    # trolley end stops with rubber buffers on the lower flange
    for sy in (-1, 1):
        box("stop", (0.05, 0.075, 0.09), (sx * 1.6, sy * 0.055, BB + FT + 0.045), "chassis", bevel=0.006)
        cyl("buffer", 0.028, 0.03, (sx * 1.565, sy * 0.055, BB + FT + 0.05), "rubber", axis='X', bevel=0.006)
    # web stiffeners over the legs
    for sy in (-1, 1):
        box("stiff", (0.012, w - t, BD - 2 * FT), (sx * LX, sy * (w + t) / 2, BT - h), "paint", bevel=0.002)
# load rating plate on both sides of the web (no lettering)
for sy in (-1, 1):
    box("rating", (0.62, 0.004, 0.16), (0, sy * (t + 0.002), BT - h), "decal", bevel=0)
    box("rating_band", (0.62, 0.005, 0.03), (0, sy * (t + 0.0025), BT - h - 0.05), "hazard", bevel=0)
    box("rating_mark", (0.1, 0.005, 0.06), (-0.2, sy * (t + 0.0025), BT - h + 0.025), "accent", bevel=0)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cyl("rivet", 0.006, 0.004, (sx * 0.295, sy * (t + 0.005), BT - h + sz * 0.065), "steel", axis='Y', verts=10)

# ================================================================ A-frame end legs
for sx in (-1, 1):
    x = sx * LX
    for sy in (-1, 1):
        bar3d("leg", (x, sy * Y_TOP, LEG_TOP), (x, sy * Y_BOT, LEG_BOT), 0.12, 0.12, "paint", bevel=0.014, extend=0.03)
        box("foot_plate", (0.2, 0.24, 0.016), (x, sy * Y_BOT, LEG_BOT + 0.006), "paint", bevel=0.004)
        for a in (-1, 1):
            for b in (-1, 1):
                bolt((x + a * 0.075, sy * Y_BOT + b * 0.09, LEG_BOT + 0.018))
        profile("foot_gus", [(0, 0), (-sy * 0.2, 0), (-sy * 0.045, 0.2)], 0.01, (x, sy * (Y_BOT - 0.04), LEG_BOT + 0.01), "paint", bevel=0.002)
    # head: socket block, top plate bolted to the beam, apex gussets both faces
    box("head", (0.14, 0.34, 0.12), (x, 0, LEG_TOP + 0.01), "paint", bevel=0.012)
    box("head_plate", (0.34, 0.36, 0.02), (x, 0, BB - 0.01), "paint", bevel=0.005)
    for a in (-1, 1):
        for b in (-1, 1):
            bolt((x + a * 0.13, b * 0.14, BB - 0.024))
            bolt((x + a * 0.13, b * 0.07, BB + FT + 0.006))
    for face in (-1, 1):
        profile("apex_gus", [(-0.235, 3.14), (0.235, 3.14), (0.15, 3.71), (-0.15, 3.71)], 0.012, (x + face * 0.066, 0, 0), "paint", bevel=0.003)
        for sy in (-1, 1):
            for z in (3.24, 3.42, 3.6):
                bolt((x + face * 0.074, sy * (leg_y(z) - 0.005), z), axis='X', r=0.012)
    # cross braces
    for z, s in ((1.2, 0.08), (2.9, 0.07)):
        box("brace", (s, 2 * leg_y(z), s), (x, 0, z), "paint", bevel=0.008)
        for sy in (-1, 1):
            box("brace_cleat", (0.012, 0.16, 0.16), (x - sx * 0.066, sy * (leg_y(z) - 0.02), z), "paint", bevel=0.003)
    # knee brace from the upper tie to the beam
    bar3d("knee", (x - sx * 0.03, 0, 2.93), (sx * (LX - 0.72), 0, BB - 0.01), 0.07, 0.07, "paint", bevel=0.008)
    box("knee_lug", (0.2, 0.12, 0.016), (sx * (LX - 0.74), 0, BB - 0.008), "paint", bevel=0.004)
    # base beam on lockable swivel castors
    box("base", (0.14, 2.0, 0.14), (x, 0, 0.30), "paint", bevel=0.014)
    for sy in (-1, 1):
        box("base_cap", (0.146, 0.012, 0.146), (x, sy * 1.0, 0.30), "hazard", bevel=0.003)
        box("base_haz", (0.146, 0.22, 0.05), (x, sy * 0.86, 0.30), "hazard", bevel=0.002)
        for k in range(3):
            box("base_chev", (0.148, 0.022, 0.07), (x, sy * (0.79 + k * 0.07), 0.30), "chassis", bevel=0, rot=(R(35), 0, 0)).scale = (1, 1, 0.72)
        yc = sy * 0.84
        wheel("castor", 0.1, 0.07, (x, yc, 0.1), rim="rim")
        box("cast_plate", (0.17, 0.2, 0.014), (x, yc, 0.223), "steel", bevel=0.004)
        cyl("cast_swivel", 0.06, 0.02, (x, yc, 0.208), "steel", bevel=0.004)
        for a in (-1, 1):
            profile("cast_fork", [(-0.05, 0.2), (0.05, 0.2), (0.035, 0.07), (-0.035, 0.07)], 0.008, (x + a * 0.048, yc, 0), "steel", bevel=0.002)
            for b in (-1, 1):
                bolt((x + a * 0.065, yc + b * 0.08, 0.232), r=0.01)
        cyl("cast_axle", 0.012, 0.125, (x, yc, 0.1), "steel", axis='X')
        # brake pedal
        bar3d("brake_arm", (x, yc + sy * 0.04, 0.19), (x, yc + sy * 0.125, 0.15), 0.05, 0.008, "steel", bevel=0.002)
        box("brake_pad", (0.07, 0.05, 0.012), (x, yc + sy * 0.14, 0.145), "tail", bevel=0.004, rot=(sy * R(-25), 0, 0))

# isolator / control box on the right-hand frame with its supply cable up the leg
cx = LX - 0.09
box("iso_box", (0.1, 0.26, 0.34), (cx, -0.3, 1.36), "plastic", bevel=0.012)
box("iso_door", (0.006, 0.22, 0.3), (cx - 0.052, -0.3, 1.36), "chassis", bevel=0.004)
cyl("iso_knob", 0.03, 0.03, (cx - 0.065, -0.3, 1.4), "tail", axis='X', bevel=0.006)
box("iso_knob_bar", (0.02, 0.07, 0.016), (cx - 0.082, -0.3, 1.4), "hazard", bevel=0.004)
cyl("iso_lamp", 0.012, 0.012, (cx - 0.058, -0.3, 1.47), "lamp", axis='X')
box("iso_label", (0.004, 0.1, 0.035), (cx - 0.056, -0.3, 1.28), "decal", bevel=0)
tube("iso_cable", fillet([(cx, -0.3, 1.53), (cx, -0.3, 1.75), (LX - 0.07, -leg_y(1.9) + 0.02, 1.9), (LX - 0.07, -leg_y(3.2) + 0.02, 3.2), (LX - 0.1, -0.13, 3.55), (LX - 0.2, -0.05, BB + 0.06)], 0.08, 4), 0.011, "rubber")

# ================================================================ hoist trolley (travels along the lower flange)
tro = empty("trolley", (X_REST, 0, 0))
for f in FRAMES:
    key(tro, f, loc=(trav(f), 0, 0))
WZ = BB + FT + 0.045
for sy in (-1, 1):
    profile("tro_plate", [(-0.2, BB + 0.14), (0.2, BB + 0.14), (0.2, BB + 0.02), (0.09, BB - 0.12), (-0.09, BB - 0.12), (-0.2, BB + 0.02)], 0.014, (0, sy * 0.127, 0), "chassis", bevel=0.004, parent=tro, plane='XZ')
    for sx in (-1, 1):
        cyl("tro_wheel", 0.045, 0.034, (sx * 0.115, sy * 0.058, WZ), "steel", axis='Y', parent=tro, bevel=0.004)
        cyl("tro_flange", 0.056, 0.008, (sx * 0.115, sy * 0.079, WZ), "steel", axis='Y', parent=tro, bevel=0.002)
        cyl("tro_axle", 0.014, 0.075, (sx * 0.115, sy * 0.105, WZ), "steel", axis='Y', parent=tro)
        cyl("tro_nut", 0.024, 0.014, (sx * 0.115, sy * 0.14, WZ), "steel", axis='Y', parent=tro, verts=6)
    cyl("bar_nut", 0.03, 0.016, (0, sy * 0.142, BB - 0.07), "steel", axis='Y', parent=tro, verts=6)
cyl("load_bar", 0.02, 0.28, (0, 0, BB - 0.07), "steel", axis='Y', parent=tro)
for sy in (-1, 1):
    cyl("bar_spacer", 0.03, 0.07, (0, sy * 0.08, BB - 0.07), "chassis", axis='Y', parent=tro)
box("hanger", (0.07, 0.07, 0.12), (0, 0, BB - 0.105), "chassis", bevel=0.01, parent=tro)
# electric wire-rope hoist
HZ = BB - 0.31                     # hoist centre height
box("hoist_body", (0.42, 0.3, 0.3), (0, 0, HZ), "paint", bevel=0.04, parent=tro, segments=4)
cyl("drum_l", 0.135, 0.44, (0, 0, HZ), "chassis", axis='X', parent=tro, bevel=0.008)
box("gearbox", (0.13, 0.33, 0.33), (-0.285, 0, HZ), "chassis", bevel=0.03, parent=tro)
cyl("gear_cover", 0.1, 0.03, (-0.36, 0, HZ), "paint", axis='X', parent=tro, bevel=0.008)
cyl("motor", 0.105, 0.26, (0.35, 0, HZ), "chassis", axis='X', parent=tro, bevel=0.006)
for k in range(6):
    cyl("motor_fin", 0.118, 0.012, (0.25 + k * 0.035, 0, HZ), "chassis", axis='X', parent=tro)
cyl("fan_cowl", 0.115, 0.07, (0.5, 0, HZ), "plastic", axis='X', parent=tro, bevel=0.015)
box("term_box", (0.1, 0.09, 0.05), (0.33, 0, HZ + 0.125), "chassis", bevel=0.008, parent=tro)
box("panel", (0.3, 0.07, 0.22), (-0.02, -0.18, HZ), "plastic", bevel=0.014, parent=tro)
box("panel_plate", (0.14, 0.004, 0.08), (-0.06, -0.216, HZ + 0.03), "decal", bevel=0, parent=tro)
box("panel_band", (0.26, 0.004, 0.025), (-0.02, -0.216, HZ - 0.06), "hazard", bevel=0, parent=tro)
box("rope_guide", (0.22, 0.12, 0.03), (0, 0, HZ - 0.155), "chassis", bevel=0.008, parent=tro)
# power feed: a cable on a taut wire along the back of the beam, from a bracket at the right-hand head to the trolley
FY, FZ = 0.165, BB + 0.1
box("feed_bracket", (0.04, 0.09, 0.05), (LX - 0.16, 0.125, FZ), "chassis", bevel=0.006)
box("feed_lug", (0.05, 0.05, 0.05), (0.2, 0.15, FZ), "chassis", bevel=0.006, parent=tro)
stretch("feed_cable", lambda f: (LX - 0.16, FY, FZ), lambda f: (trav(f) + 0.2, FY, FZ), 0.008, "rubber")
tube("feed_drop", fillet([(0.2, FY, FZ), (0.26, FY, FZ - 0.1), (0.33, 0.1, HZ + 0.2), (0.33, 0.02, HZ + 0.14)], 0.05, 4), 0.008, "rubber", parent=tro)
# pendant control on its cable, in front of the load path
PX, PY, PZ = -0.3, -0.5, 1.22
box("pend_arm", (0.03, 0.3, 0.03), (PX + 0.1, -0.36, HZ - 0.02), "chassis", bevel=0.006, parent=tro)
tube("pend_cable", fillet([(PX + 0.1, -0.2, HZ - 0.06), (PX + 0.1, -0.44, HZ - 0.06), (PX, PY, HZ - 0.22), (PX, PY, PZ + 0.3)], 0.07, 5), 0.009, "rubber", parent=tro)
rod3d("pend_wire", (PX + 0.1, -0.5, HZ - 0.02), (PX + 0.012, PY, PZ + 0.3), 0.003, "steel", parent=tro, verts=6)
cyl("pend_gland", 0.02, 0.06, (PX, PY, PZ + 0.28), "rubber", parent=tro, radius2=0.011)
box("pend_body", (0.085, 0.065, 0.26), (PX, PY, PZ + 0.13), "hazard", bevel=0.016, parent=tro)
cyl("pend_estop", 0.019, 0.02, (PX, PY - 0.04, PZ + 0.215), "tail", axis='Y', parent=tro, bevel=0.004)
for i, m in enumerate(("decal", "chassis", "decal", "chassis")):
    cyl("pend_btn", 0.013, 0.014, (PX + (-0.019 if i % 2 else 0.019), PY - 0.036, PZ + 0.15 - (i // 2) * 0.055), m, axis='Y', parent=tro, bevel=0.003)
cyl("pend_btn", 0.013, 0.014, (PX, PY - 0.036, PZ + 0.045), "accent", axis='Y', parent=tro, bevel=0.003)

# ================================================================ hook block, slings and load (all hang from the hoist ropes)
hook = empty("hook", (0, 0, HOOK_Z), tro)
for f in FRAMES:
    key(hook, f, loc=(0, 0, HOOK_Z + lift(f)))
SH = 0.33                          # sheave centre above the hook bowl
SR = 0.06
cyl("sheave", SR + 0.012, 0.03, (0, 0, SH), "steel", axis='Y', parent=hook, bevel=0.003)
cyl("sheave_pin", 0.016, 0.1, (0, 0, SH), "steel", axis='Y', parent=hook)
for sy in (-1, 1):
    profile("block_plate", [(-0.05, 0.17), (0.05, 0.17)] + arc_pts(0, SH, 0.1, -20, 200, 16), 0.012, (0, sy * 0.028, 0), "hazard", bevel=0.003, parent=hook, plane='XZ')
    cyl("block_boss", 0.032, 0.012, (0, sy * 0.04, SH), "chassis", axis='Y', parent=hook)
    box("block_stripe", (0.09, 0.003, 0.02), (0, sy * 0.0345, 0.215), "chassis", bevel=0, parent=hook)
box("crosshead", (0.085, 0.07, 0.05), (0, 0, 0.19), "steel", bevel=0.008, parent=hook)
cyl("hook_nut", 0.028, 0.02, (0, 0, 0.222), "steel", parent=hook, verts=6)
cyl("hook_collar", 0.026, 0.03, (0, 0, 0.155), "steel", parent=hook, bevel=0.004)
hp = [(0, 0, 0.17), (0, 0, 0.135), (0, 0.03, 0.105), (0, 0.052, 0.075)] + [(0, 0.055 * math.cos(R(a)), 0.05 - 0.055 * math.sin(R(a))) for a in range(0, 226, 15)]
tube("hook_body", hp, 0.019, "hazard", parent=hook, resolution=2)
tip = hp[-1]
cyl("hook_tip", 0.019, 0.035, (0, tip[1] + 0.008, tip[2] + 0.014), "hazard", parent=hook, radius2=0.006, rot=(R(-30), 0, 0))
bar3d("hook_latch", (0, 0.012, 0.13), (0, tip[1] + 0.012, tip[2] + 0.02), 0.022, 0.005, "steel", bevel=0.002, parent=hook)
cyl("latch_pin", 0.007, 0.05, (0, 0.012, 0.13), "steel", axis='X', parent=hook)
# two falls of wire rope: fixed at the drum, scale-keyed so they always reach the sheave
RTOP = HZ - 0.05
for sx in (-1, 1):
    rp = empty("rope%d" % sx, (sx * SR, 0, RTOP), tro)
    cyl("rope_m", 0.007, 1.0, (0, 0, -0.5), "steel", parent=rp, verts=10)
    for f in FRAMES:
        key(rp, f, scale=(1, 1, RTOP - (HOOK_Z + lift(f) + SH)))

# load: a banded bundle of steel box sections, slung with two web slings
BZ0 = 0.10 - HOOK_Z                # underside of the bundle relative to the hook empty
NX, NZ, S, BL = 4, 3, 0.1, 2.4
for i in range(NX):
    for j in range(NZ):
        y, z = (i - (NX - 1) / 2) * S, BZ0 + S / 2 + j * S
        box("section", (BL - (0.06 if (i + j) % 2 else 0), S - 0.003, S - 0.003), (0, y, z), "steel", bevel=0.01, parent=hook)
        for sx in (-1, 1):
            box("bore", (0.006, S - 0.026, S - 0.026), (sx * (BL / 2 - (0.03 if (i + j) % 2 else 0)), y, z), "chassis", bevel=0, parent=hook)
BWd, BH = NX * S, NZ * S


def band(name, x, wdt, th, material, gap=0.0):
    a, b = BWd / 2 + gap + th / 2, BH / 2 + gap + th / 2
    zc = BZ0 + BH / 2
    for sy in (-1, 1):
        box(name, (wdt, th, 2 * b + th), (x, sy * a, zc), material, bevel=0.002, parent=hook, segments=1)
        box(name, (wdt, 2 * a + th, th), (x, 0, zc + sy * b), material, bevel=0.002, parent=hook, segments=1)


for x in (-1.0, 0.0, 1.0):
    band("banding", x, 0.03, 0.003, "chassis")
    box("band_seal", (0.045, 0.03, 0.006), (x + 0.0, 0.08, BZ0 + BH + 0.005), "steel", bevel=0.001, parent=hook)
SLX = 0.62
EYE = (0, 0, 0.018)
for sx in (-1, 1):
    band("sling_wrap", sx * SLX, 0.075, 0.008, "accent", gap=0.003)
    top = (sx * SLX, 0, BZ0 + BH + 0.008)
    e = Vector((sx * 0.012, 0, 0.03)); tv = Vector(top)
    bar3d("sling_label", e.lerp(tv, 0.5), e.lerp(tv, 0.6), 0.08, 0.016, "decal", bevel=0.002, parent=hook)
    bar3d("sling_leg", top, (sx * 0.012, 0, 0.03), 0.075, 0.012, "accent", bevel=0.002, parent=hook)
    box("sling_choke", (0.09, 0.1, 0.014), (sx * SLX, 0, BZ0 + BH + 0.016), "accent", bevel=0.004, parent=hook)
ring("sling_eyes", 0.03, 0.011, (0, 0, 0.02), "accent", axis='Y', parent=hook)
# timber bearers the bundle was standing on (stay on the floor)
for dx in (-0.8, 0.8):
    box("bearer", (0.1, 0.7, 0.097), (X_REST + dx, 0, 0.0485), "wood", bevel=0.006)

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "gantry.glb"))
