import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import *
from pg_common import *
reset()
R = math.radians

LIFT = 0.115
Y_TIP, H = -0.90, 0.25             # fork tips, heel (front face of the back plate)
BLW, BLH = 0.16, 0.085             # blade width, lowered height
BX = 0.27 - BLW / 2                # blade centre (0.54 over the outsides)
YC = H + 0.11                      # lift cylinder centre line
YW = H + 0.13                      # steer wheel axle
PIV = (H + 0.24, 0.29)             # tiller pivot (y, z)
A_REST, A_WORK = -5.0, -40.0       # tiller angle from vertical (negative = leaning back towards the operator)


def lift(f):
    return LIFT * f / FRAME_WORK


def ang(f):
    return R(lerp(A_REST, A_WORK, f / FRAME_WORK))


# ================================================================ pump unit (stays on the floor)
for sx in (-1, 1):
    wheel("steer", 0.09, 0.05, (sx * 0.08, YW, 0.09), rim="rim")
cyl("axle", 0.012, 0.25, (0, YW, 0.09), "steel", axis='X')
for sx in (-1, 1):
    cyl("axle_nut", 0.02, 0.012, (sx * 0.122, YW, 0.09), "steel", axis='X', verts=6)
cyl("turntable", 0.044, 0.1, (0, YW, 0.14), "chassis", bevel=0.006)
cyl("thrust", 0.058, 0.02, (0, YW, 0.193), "steel", bevel=0.004)
box("pump_body", (0.12, 0.27, 0.06), (0, H + 0.185, 0.228), "chassis", bevel=0.014)
cyl("reservoir", 0.062, 0.1, (0, YC, 0.25), "chassis", bevel=0.01)
cyl("barrel", 0.044, 0.1, (0, YC, 0.31), "chassis", bevel=0.004)
cyl("gland", 0.05, 0.018, (0, YC, 0.361), "steel", bevel=0.004)
cyl("filler", 0.012, 0.02, (0.04, YC + 0.035, 0.305), "steel", bevel=0.003, verts=6)
# lowering valve block on the side with its little lever
box("valve", (0.035, 0.05, 0.04), (0.07, H + 0.2, 0.225), "steel", bevel=0.006)
bar3d("valve_lever", (0.085, H + 0.2, 0.235), (0.085, H + 0.25, 0.275), 0.008, 0.016, "steel", bevel=0.003)
# tiller pivot cheeks and pin
for sx in (-1, 1):
    profile("cheek", [(-0.04, -0.045), (0.04, -0.045)] + arc_pts(0, 0, 0.032, 0, 180, 8), 0.012, (sx * 0.052, PIV[0], PIV[1]), "chassis", bevel=0.003)
cyl("till_pin", 0.011, 0.14, (0, PIV[0], PIV[1]), "steel", axis='X')
# hand pump plunger behind the pivot, pressed by a roller on the tiller foot
ROLL = (0.05, 0.03)                # roller centre in the tiller's own (y, z)
RR_ = 0.013


def roll_pos(f):
    a = ang(f)
    return (PIV[0] + ROLL[0] * math.cos(a) - ROLL[1] * math.sin(a), PIV[1] + ROLL[0] * math.sin(a) + ROLL[1] * math.cos(a))


PY = roll_pos(12)[0]
cyl("plunger_barrel", 0.02, 0.07, (0, PY, 0.227), "chassis", bevel=0.004)
cyl("plunger_seat", 0.024, 0.008, (0, PY, 0.262), "steel")
plg = empty("plunger", (0, PY, 0.3))
cyl("plunger_cap", 0.021, 0.008, (0, 0, -0.004), "steel", parent=plg, bevel=0.002)
cyl("plunger_rod", 0.009, 0.075, (0, 0, -0.04), "chrome", parent=plg)
for f in FRAMES:
    key(plg, f, loc=(0, PY, roll_pos(f)[1] - RR_))
spring = stretch("spring", lambda f: (0, PY, 0.264), lambda f: (0, PY, roll_pos(f)[1] - RR_ - 0.008), 0, "steel")
for o in list(spring.children):
    bpy.data.objects.remove(o)
tube("spring_coil", helix_pts(0.016, 4.5), 0.0028, "steel", parent=spring, resolution=1)

# ================================================================ tiller (drawbar handle)
till = empty("tiller", (0, PIV[0], PIV[1]))
key(till, FRAME_REST, rot=(R(A_REST), 0, 0))
key(till, FRAME_WORK, rot=(R(A_WORK), 0, 0))
box("till_foot", (0.084, 0.052, 0.1), (0, 0, 0.025), "paint", bevel=0.012, parent=till)
box("roll_arm", (0.03, 0.05, 0.034), (0, 0.035, ROLL[1]), "paint", bevel=0.006, parent=till)
cyl("roller", RR_, 0.034, (0, ROLL[0], ROLL[1]), "steel", axis='X', parent=till, bevel=0.002)
cyl("till_neck", 0.03, 0.06, (0, 0, 0.1), "paint", parent=till, radius2=0.02, bevel=0.003)
cyl("drawbar", 0.02, 0.6, (0, 0, 0.41), "paint", parent=till, verts=24)
# closed loop grip
LW, LB, LT = 0.175, 0.79, 0.92
loop = [(-0.055, 0, 0.695), (-LW, 0, LB), (-LW, 0, LT), (LW, 0, LT), (LW, 0, LB), (0.055, 0, 0.695)]
tube("loop", fillet(loop, 0.045, 6, closed=True), 0.015, "chassis", parent=till, closed=True, resolution=1)
box("loop_knuckle", (0.14, 0.04, 0.05), (0, 0, 0.7), "paint", bevel=0.014, parent=till)
cyl("grip_top", 0.0195, 0.24, (0, 0, LT), "vinyl", axis='X', parent=till, bevel=0.005)
for sx in (-1, 1):
    cyl("grip_side", 0.0195, 0.075, (sx * LW, 0, (LB + LT) / 2 + 0.005), "vinyl", parent=till, bevel=0.005)
    for k in range(4):
        cyl("grip_rib", 0.0215, 0.006, (sx * (0.03 + k * 0.025), 0, LT), "vinyl", axis='X', parent=till)
# three-position release lever inside the loop
box("lever_box", (0.05, 0.034, 0.05), (0, -0.004, 0.752), "chassis", bevel=0.008, parent=till)
cyl("lever_pin", 0.006, 0.062, (0, -0.004, 0.76), "steel", axis='X', parent=till)
bar3d("lever_arm", (0, -0.012, 0.765), (0, -0.04, 0.83), 0.022, 0.008, "accent", bevel=0.003, parent=till)
box("lever_pad", (0.06, 0.012, 0.032), (0, -0.045, 0.842), "accent", bevel=0.005, parent=till, rot=(R(-20), 0, 0))
# release rod down the front of the drawbar
rod3d("rel_rod", (0, -0.026, 0.74), (0, -0.03, 0.12), 0.004, "steel", parent=till, verts=8)
for z in (0.25, 0.5):
    box("rod_clip", (0.02, 0.018, 0.012), (0, -0.024, z), "steel", bevel=0.002, parent=till)

# ================================================================ lifting fork frame
forks = empty("forks", (0, 0, 0))
key(forks, FRAME_REST, loc=(0, 0, 0))
key(forks, FRAME_WORK, loc=(0, 0, LIFT))
TOP = 0.425
t, sk = 0.008, 0.03                # top plate thickness, skirt bottom height
# back plate (tapering to the bridge over the pump) with a pressed stiffening panel
profile("back_plate", [(-0.27, sk), (-0.27, 0.17), (-0.12, TOP), (0.12, TOP), (0.27, 0.17), (0.27, sk)], 0.012, (0, H - 0.006, 0), "paint", bevel=0.004, parent=forks, plane='XZ')
profile("back_press", [(-0.2, 0.1), (-0.2, 0.17), (-0.09, 0.37), (0.09, 0.37), (0.2, 0.17), (0.2, 0.1)], 0.01, (0, H - 0.014, 0), "paint", bevel=0.004, parent=forks, plane='XZ')
box("cap_plate", (0.11, 0.004, 0.07), (0, H - 0.02, 0.25), "decal", bevel=0, parent=forks)
box("cap_band", (0.11, 0.005, 0.014), (0, H - 0.0205, 0.276), "hazard", bevel=0, parent=forks)
# hood: side gussets and the bridge the lift ram pushes on
for sx in (-1, 1):
    profile("gusset", [(H - 0.004, 0.15), (H - 0.004, TOP), (H + 0.2, TOP), (H + 0.2, 0.355)], 0.01, (sx * 0.11, 0, 0), "paint", bevel=0.003, parent=forks)
    profile("flange", [(H - 0.004, 0.035), (H - 0.004, 0.17), (H + 0.05, 0.17), (H + 0.05, 0.11)], 0.01, (sx * 0.265, 0, 0), "paint", bevel=0.003, parent=forks)
box("bridge", (0.23, 0.204, 0.025), (0, H + 0.098, TOP - 0.0125), "paint", bevel=0.006, parent=forks)
cyl("ram_boss", 0.034, 0.03, (0, YC, 0.385), "steel", bevel=0.004, parent=forks)
cyl("ram_rod", 0.023, 0.19, (0, YC, 0.29), "chrome", parent=forks)
box("id_plate", (0.004, 0.09, 0.05), (0.1165, H + 0.09, 0.37), "decal", bevel=0, parent=forks)
box("stripe", (0.004, 0.14, 0.02), (-0.1165, H + 0.09, 0.385), "accent", bevel=0, parent=forks)
# torsion tube across the heel (drives the push rods)
cyl("torsion", 0.02, 0.5, (0, H - 0.03, 0.055), "steel", axis='X', parent=forks)
RRL, LL, pz = 0.037, 0.18, 0.052   # load roller radius, link length, link pivot height
YL = Y_TIP + 0.37
LUG = (0.03, -0.012)               # push rod eye on the link, in the link's own (y, z)


def link_ang(f):
    return math.asin((pz + lift(f) - RRL) / LL)


for sx in (-1, 1):
    x = sx * BX
    u = [(-BLW / 2, sk), (-BLW / 2, BLH), (BLW / 2, BLH), (BLW / 2, sk), (BLW / 2 - 0.008, sk), (BLW / 2 - 0.008, BLH - t), (-BLW / 2 + 0.008, BLH - t), (-BLW / 2 + 0.008, sk)]
    L = H - (Y_TIP + 0.14)
    profile("blade", u, L, (x, H - L / 2, 0), "paint", bevel=0.004, parent=forks, plane='XZ', segments=2)
    profile("blade_tip", [(Y_TIP + 0.15, sk), (Y_TIP + 0.15, BLH), (Y_TIP + 0.08, BLH), (Y_TIP + 0.012, 0.062), (Y_TIP, 0.05), (Y_TIP, 0.04), (Y_TIP + 0.03, sk)], BLW, (x, 0, 0), "paint", bevel=0.008, parent=forks)
    cyl("entry_roller", 0.017, BLW - 0.05, (x, Y_TIP + 0.04, 0.034), "rim", axis='X', parent=forks)
    # heel gusset between blade top and back plate
    profile("heel_gus", [(H - 0.004, BLH - 0.002), (H - 0.004, 0.15), (H - 0.1, BLH - 0.002)], 0.008, (sx * 0.2, 0, 0), "paint", bevel=0.002, parent=forks)
    # load roller on a swinging link: keyed every frame so the roller stays on the floor
    link = empty("roller_link%d" % sx, (x, YL, pz), forks)
    for s2 in (-1, 1):
        bar3d("link_plate", (s2 * 0.05, 0.045, -0.01), (s2 * 0.05, -LL - 0.015, 0), 0.007, 0.036, "steel", bevel=0.003, parent=link)
    cyl("link_pin", 0.009, 0.14, (0, 0, 0), "steel", axis='X', parent=link)
    cyl("link_eye", 0.007, 0.11, (0, LUG[0], LUG[1]), "steel", axis='X', parent=link)
    cyl("load_roller", RRL, 0.085, (0, -LL, 0), "rim", axis='X', parent=link, bevel=0.006)
    cyl("load_roller_ax", 0.008, 0.11, (0, -LL, 0), "steel", axis='X', parent=link)
    for f in FRAMES:
        key(link, f, rot=(link_ang(f), 0, 0))

    def eye(f, x=x):
        a = link_ang(f)
        return (x, YL + LUG[0] * math.cos(a) - LUG[1] * math.sin(a), pz + LUG[0] * math.sin(a) + LUG[1] * math.cos(a))
    stretch("push_rod%d" % sx, lambda f, x=x: (x, H - 0.03, 0.05), eye, 0.008, "steel", parent=forks)

# ================================================================ pallet: stands on the floor until the blades pick it up
DECK_UNDER = 0.122
PAL_Y = -0.30
pal = pallet("pal", (0, PAL_Y, 0), load=False)
# a low load so the truck stays visible: one layer of cartons, strapped, with two smaller boxes on top
for sx in (-1, 1):
    box("carton", (0.56, 0.9, 0.36), (sx * 0.285, 0, 0.144 + 0.18), "card" if sx > 0 else "card2", 0.008, pal, segments=2)
    box("tape", (0.07, 0.902, 0.003), (sx * 0.285, 0, 0.144 + 0.36), "tape", 0, pal)
box("carton_s", (0.5, 0.42, 0.24), (-0.2, -0.16, 0.504 + 0.12), "card", 0.008, pal, segments=2, rot=(0, 0, R(6)))
box("tape_s", (0.502, 0.06, 0.003), (-0.2, -0.16, 0.504 + 0.24), "tape", 0, pal, rot=(0, 0, R(6)))
box("carton_t", (0.36, 0.3, 0.2), (0.3, 0.1, 0.504 + 0.1), "card2", 0.008, pal, segments=2, rot=(0, 0, R(-8)))
box("tape_t", (0.362, 0.05, 0.003), (0.3, 0.1, 0.504 + 0.2), "tape", 0, pal, rot=(0, 0, R(-8)))
for y in (-0.25, 0.25):
    box("strap", (1.135, 0.03, 0.364), (0, y, 0.144 + 0.181), "accent", 0.002, pal, segments=1)
for f in FRAMES:
    key(pal, f, loc=(0, PAL_Y, max(0.0, BLH + lift(f) - DECK_UNDER)))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "pump.glb"))
