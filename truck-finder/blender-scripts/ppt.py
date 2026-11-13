import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import *
reset()
R = math.radians

LIFT = 0.12
W = 0.72
Y_TIP, Y_HEEL = -1.05, 0.10        # fork blades
Y_BATT = 0.30                      # back of the lifting battery box / front of the drive unit
Y_BACK = 0.60                      # back of the drive unit
BLW, BLH = 0.17, 0.085             # blade width, lowered height
BX = 0.27 - BLW / 2                # blade centre (0.54 over the outsides)


def lift(f):
    return LIFT * f / FRAME_WORK


# ================================================================ fixed drive unit ("power head")
def plan(x, y0, y1, r, n=8):
    """Plan outline with rounded rear corners."""
    return [(-x, y0), (x, y0)] + arc_pts(x - r, y1 - r, r, 0, 90, n) + arc_pts(-x + r, y1 - r, r, 90, 180, n)


profile("bumper", plan(W / 2, Y_BATT + 0.01, Y_BACK + 0.015, 0.13), 0.15, (0, 0, 0.135), "chassis", bevel=0.025, plane='XY')
profile("cover_low", plan(W / 2 - 0.012, Y_BATT + 0.015, Y_BACK, 0.12), 0.40, (0, 0, 0.405), "paint", bevel=0.02, plane='XY')
profile("cover_top", plan(W / 2 - 0.012, Y_BATT + 0.015, Y_BACK, 0.12), 0.33, (0, 0, 0.645), "paint", bevel=0.075, plane='XY', segments=5)
profile("cover_seam", plan(W / 2 - 0.008, Y_BATT + 0.02, Y_BACK + 0.004, 0.122), 0.014, (0, 0, 0.60), "chassis", bevel=0, plane='XY')
# top control panel: display, key switch, emergency stop
box("panel", (0.34, 0.2, 0.02), (-0.1, 0.45, 0.812), "plastic", bevel=0.008)
box("display", (0.12, 0.07, 0.012), (-0.17, 0.47, 0.826), "glass", bevel=0.003)
cyl("keysw", 0.016, 0.03, (-0.04, 0.47, 0.83), "steel", bevel=0.004)
cyl("estop_base", 0.04, 0.02, (0.23, 0.43, 0.815), "hazard", bevel=0.004)
cyl("estop", 0.03, 0.04, (0.23, 0.43, 0.84), "tail", bevel=0.01)
# rear vents, data plate, charger socket
for i in range(4):
    box("vent", (0.22, 0.012, 0.014), (0, Y_BACK + 0.001, 0.30 + i * 0.035), "chassis", bevel=0.003, segments=1)
box("plate", (0.004, 0.12, 0.08), (W / 2 - 0.011, 0.43, 0.44), "decal", bevel=0)
box("stripe_l", (0.004, 0.2, 0.03), (W / 2 - 0.011, 0.43, 0.3), "accent", bevel=0)
box("stripe_r", (0.004, 0.2, 0.03), (-W / 2 + 0.011, 0.43, 0.3), "accent", bevel=0)
# drive wheel and castors
wheel("drive", 0.115, 0.08, (0, 0.45, 0.115), rim="rim")
cyl("drive_motor", 0.09, 0.2, (0, 0.45, 0.25), "chassis", bevel=0.01)
for sx in (-1, 1):
    wheel("castor", 0.05, 0.04, (sx * 0.27, 0.49, 0.05), rim="rim")
    box("castor_fork", (0.06, 0.05, 0.1), (sx * 0.27, 0.47, 0.11), "steel", bevel=0.008)

# ---------------------------------------------------------------- tiller
T0, T1 = (0.45, 0.80), (0.70, 1.20)       # (y, z) pivot on the cover -> control head
cyl("till_turret", 0.085, 0.06, (0, T0[0], 0.83), "plastic", bevel=0.015)
for sx in (-1, 1):
    profile("till_cheek", [(-0.05, 0), (0.05, 0)] + arc_pts(0, 0.08, 0.045, 0, 180, 8), 0.018, (sx * 0.05, T0[0], 0.85), "chassis", bevel=0.004)
cyl("till_pin", 0.018, 0.14, (0, T0[0], 0.93), "steel", axis='X')
tilt = math.atan2(T1[0] - T0[0], T1[1] - T0[1])
bar3d("till_arm", (0, T0[0], 0.93), (0, T1[0], T1[1]), 0.075, 0.05, "chassis", bevel=0.018, segments=3)
tube("till_cable", [(0.03, T0[0] - 0.04, 0.85), (0.045, T0[0] - 0.03, 1.0), (0.03, T0[0] + 0.12, 1.14)], 0.008, "rubber")
head = empty("till_head", (0, T1[0], T1[1]), rot=(-tilt, 0, 0))
box("head_body", (0.15, 0.085, 0.2), (0, 0, 0.05), "plastic", bevel=0.025, parent=head)
box("head_neck", (0.09, 0.065, 0.1), (0, 0, -0.07), "plastic", bevel=0.02, parent=head)
for sx in (-1, 1):
    # loop hand grips
    tube("grip_frame", [(sx * 0.06, 0, -0.035), (sx * 0.2, 0, -0.035), (sx * 0.225, 0, 0.0), (sx * 0.225, 0, 0.13), (sx * 0.2, 0, 0.16), (sx * 0.06, 0, 0.14)], 0.014, "plastic", parent=head)
    cyl("grip", 0.021, 0.12, (sx * 0.225, 0, 0.065), "vinyl", bevel=0.006, parent=head)
    # butterfly throttle paddles
    box("butterfly", (0.075, 0.022, 0.06), (sx * 0.125, -0.03, 0.075), "paint", bevel=0.008, parent=head, rot=(R(20), 0, sx * R(-12)))
    cyl("bfly_axle", 0.012, 0.05, (sx * 0.09, -0.012, 0.075), "steel", axis='X', parent=head)
    cyl("horn", 0.013, 0.012, (sx * 0.04, -0.045, 0.11), "hazard", axis='Y', parent=head)
    box("liftbtn", (0.03, 0.01, 0.022), (sx * 0.035, -0.044, 0.03), "decal", bevel=0.003, parent=head)
# red belly (emergency reverse) button on the end of the head facing the operator
box("belly", (0.12, 0.07, 0.035), (0, 0, 0.165), "accent", bevel=0.014, parent=head)

# ---------------------------------------------------------------- fold-down operator platform
PZ = 0.13
box("platform", (0.58, 0.31, 0.035), (0, Y_BACK + 0.18, PZ), "chassis", bevel=0.012)
box("plat_mat", (0.52, 0.25, 0.008), (0, Y_BACK + 0.18, PZ + 0.02), "rubber", bevel=0.002)
for i in range(5):
    box("plat_rib", (0.5, 0.012, 0.006), (0, Y_BACK + 0.08 + i * 0.05, PZ + 0.026), "rubber", bevel=0, segments=1)
box("plat_edge", (0.58, 0.012, 0.037), (0, Y_BACK + 0.338, PZ), "hazard", bevel=0.003)
cyl("plat_hinge", 0.02, 0.6, (0, Y_BACK + 0.03, PZ), "steel", axis='X', bevel=0.004)
for sx in (-1, 1):
    bar3d("plat_stay", (sx * 0.3, Y_BACK - 0.01, 0.34), (sx * 0.3, Y_BACK + 0.22, PZ + 0.01), 0.012, 0.03, "steel", bevel=0.004)

# ================================================================ lifting part: forks + battery box
forks = empty("forks", (0, 0, 0))
key(forks, FRAME_REST, loc=(0, 0, 0))
key(forks, FRAME_WORK, loc=(0, 0, LIFT))
# battery box
box("batt_box", (W - 0.01, Y_BATT - Y_HEEL, 0.62), (0, (Y_BATT + Y_HEEL) / 2, 0.39), "paint", bevel=0.03, parent=forks)
box("batt_lid", (W - 0.05, Y_BATT - Y_HEEL - 0.03, 0.03), (0, (Y_BATT + Y_HEEL) / 2, 0.71), "plastic", bevel=0.012, parent=forks)
tube("batt_handle", [(-0.1, 0.2, 0.72), (-0.1, 0.2, 0.75), (0.1, 0.2, 0.75), (0.1, 0.2, 0.72)], 0.008, "steel", parent=forks)
box("batt_plug", (0.07, 0.05, 0.05), (0.24, 0.2, 0.735), "tail", bevel=0.01, parent=forks)
box("batt_panel", (0.5, 0.006, 0.34), (0, Y_HEEL - 0.001, 0.46), "chassis", bevel=0.004, parent=forks)
box("batt_hazard", (0.62, 0.006, 0.04), (0, Y_HEEL - 0.002, 0.2), "hazard", bevel=0, parent=forks)
for i in range(8):
    box("batt_chev", (0.025, 0.008, 0.04), (-0.265 + i * 0.076, Y_HEEL - 0.003, 0.2), "chassis", bevel=0, parent=forks, rot=(0, R(35), 0))
# fork heel cross-member
box("heel_xm", (0.56, 0.1, 0.09), (0, Y_HEEL - 0.03, 0.105), "paint", bevel=0.012, parent=forks)
t, sk = 0.012, 0.03                # top plate thickness, skirt bottom height
for sx in (-1, 1):
    x = sx * BX
    u = [(-BLW / 2, sk), (-BLW / 2, BLH), (BLW / 2, BLH), (BLW / 2, sk), (BLW / 2 - 0.015, sk), (BLW / 2 - 0.015, BLH - t), (-BLW / 2 + 0.015, BLH - t), (-BLW / 2 + 0.015, sk)]
    L = Y_HEEL - (Y_TIP + 0.14)
    profile("blade", u, L, (x, Y_HEEL - L / 2, 0), "paint", bevel=0.005, parent=forks, plane='XZ', segments=2)
    profile("blade_tip", [(Y_TIP + 0.15, sk), (Y_TIP + 0.15, BLH), (Y_TIP + 0.07, BLH), (Y_TIP, 0.06), (Y_TIP, 0.04), (Y_TIP + 0.03, sk)], BLW, (x, 0, 0), "paint", bevel=0.008, parent=forks)
    # small entry roller in the tip
    cyl("entry_roller", 0.018, BLW - 0.05, (x, Y_TIP + 0.035, 0.036), "rim", axis='X', parent=forks)
    # load roller on a trailing link: keyed every frame so the roller stays on the floor
    RR, LL = 0.037, 0.16
    pz = 0.052
    link = empty("roller_link%d" % sx, (x, -0.70, pz), forks)
    for s2 in (-1, 1):
        bar3d("link_plate", (s2 * 0.05, 0.015, 0), (s2 * 0.05, -LL - 0.015, 0), 0.008, 0.035, "steel", bevel=0.003, parent=link)
    cyl("link_pin", 0.01, 0.13, (0, 0, 0), "steel", axis='X', parent=link)
    cyl("load_roller", RR, 0.085, (0, -LL, 0), "rim", axis='X', parent=link, bevel=0.006)
    cyl("load_roller_ax", 0.009, 0.11, (0, -LL, 0), "steel", axis='X', parent=link)
    for f in FRAMES:
        key(link, f, rot=(math.asin((pz + lift(f) - RR) / LL), 0, 0))

# ================================================================ pallet: stands on the floor until the blades pick it up
DECK_UNDER = 0.122                 # underside of the pallet's top deck above its own base
pal = pallet("pal", (0, -0.45, 0))
for f in FRAMES:
    key(pal, f, loc=(0, -0.45, max(0.0, BLH + lift(f) - DECK_UNDER)))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "ppt.glb"))
