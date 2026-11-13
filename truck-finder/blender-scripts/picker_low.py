import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import *
from wh_common import rtube, beacon
reset()
R = math.radians

LIFT = 0.12
HW = 0.40                          # half width of the truck body
Y_TIP, Y_HEEL = -1.97, 0.47        # fork blades (2.44 m: two pallets end to end)
Y_BULK = 0.86                      # fixed bulkhead behind the lifting battery box
Y_PLAT = 1.47                      # back of the operator platform / front of the drive unit
Y_BACK = 1.95                      # back of the drive unit
BLW, BLH = 0.17, 0.085             # blade width, lowered height
BX = 0.27 - BLW / 2                # blade centre (0.54 over the outsides)
FZ = 0.15                          # platform floor surface


def lift(f):
    return LIFT * f / FRAME_WORK


def plan(x, y0, y1, r, n=8):
    """Plan outline with rounded rear corners."""
    return [(-x, y0), (x, y0)] + arc_pts(x - r, y1 - r, r, 0, 90, n) + arc_pts(-x + r, y1 - r, r, 90, 180, n)


# ================================================================ fixed chassis: drive unit, platform, bulkhead
profile("bumper", plan(HW, Y_PLAT - 0.02, Y_BACK + 0.015, 0.15), 0.16, (0, 0, 0.14), "chassis", bevel=0.025, plane='XY')
for i in range(6):
    profile("haz", [(0, 0), (0.045, 0), (0.08, 0.06), (0.035, 0.06)], 0.008, (-0.27 + i * 0.09, Y_BACK + 0.018, 0.085), "hazard", bevel=0, plane='XZ')
DT = 1.15                          # top of the drive unit cover
profile("cover_low", plan(HW - 0.012, Y_PLAT, Y_BACK, 0.14), 0.60, (0, 0, 0.51), "paint", bevel=0.02, plane='XY')
profile("cover_top", plan(HW - 0.012, Y_PLAT, Y_BACK, 0.14), DT - 0.82, (0, 0, (DT + 0.82) / 2), "paint", bevel=0.08, plane='XY', segments=5)
profile("cover_seam", plan(HW - 0.008, Y_PLAT + 0.005, Y_BACK + 0.004, 0.142), 0.014, (0, 0, 0.815), "chassis", bevel=0, plane='XY')
# operator side of the drive unit: knee pad, document pocket
box("knee_pad", (0.5, 0.035, 0.3), (0, Y_PLAT - 0.012, 0.62), "vinyl", bevel=0.016)
box("pocket", (0.44, 0.03, 0.14), (0, Y_PLAT - 0.012, 0.95), "plastic", bevel=0.01)
# rear: service cover, vents, tail lights, tow pin
box("rear_cover", (0.44, 0.02, 0.4), (0, Y_BACK - 0.002, 0.5), "paint", bevel=0.012)
for i in range(5):
    box("vent", (0.3, 0.02, 0.013), (0, Y_BACK + 0.004, 0.38 + i * 0.04), "chassis", bevel=0.002, segments=1)
box("rear_grip", (0.18, 0.03, 0.026), (0, Y_BACK + 0.008, 0.64), "chassis", bevel=0.008)
for sx in (-1, 1):
    box("tail", (0.05, 0.02, 0.09), (sx * 0.22, Y_BACK + 0.002, 0.98), "tail", bevel=0.006)
    box("stripe", (0.006, 0.3, 0.035), (sx * (HW - 0.011), 1.71, 0.72), "accent", bevel=0)
    for i in range(4):
        box("side_vent", (0.012, 0.2, 0.012), (sx * (HW - 0.01), 1.71, 0.36 + i * 0.035), "chassis", bevel=0.002, segments=1)
box("plate", (0.006, 0.11, 0.075), (HW - 0.011, 1.66, 0.96), "decal", bevel=0)
# top console: display, key switch, emergency stop, beacon
box("panel", (0.56, 0.26, 0.02), (0, 1.76, DT + 0.004), "plastic", bevel=0.008)
box("display", (0.13, 0.08, 0.012), (-0.14, 1.78, DT + 0.018), "glass", bevel=0.003)
cyl("keysw", 0.015, 0.03, (0.02, 1.8, DT + 0.02), "steel", bevel=0.004)
cyl("estop_base", 0.038, 0.016, (0.2, 1.8, DT + 0.016), "hazard", bevel=0.004)
cyl("estop", 0.028, 0.035, (0.2, 1.8, DT + 0.035), "tail", bevel=0.01)
for sx in (-1, 1):
    # grab handles on the corners of the drive unit for stepping on and off
    rtube("grab", [(sx * 0.33, Y_PLAT + 0.07, DT - 0.03), (sx * 0.33, Y_PLAT + 0.07, DT + 0.1), (sx * 0.33, Y_PLAT + 0.3, DT + 0.1), (sx * 0.33, Y_PLAT + 0.3, DT - 0.03)], 0.014, "mast", bend=0.04)
# drive wheel and castors
wheel("drive", 0.125, 0.09, (0, 1.72, 0.125), rim="rim")
cyl("drive_motor", 0.09, 0.2, (0, 1.72, 0.27), "chassis", bevel=0.01)
for sx in (-1, 1):
    wheel("castor", 0.055, 0.045, (sx * 0.3, 1.8, 0.055), rim="rim")
    box("castor_fork", (0.065, 0.05, 0.08), (sx * 0.3, 1.78, 0.11), "steel", bevel=0.008)

# ---------------------------------------------------------------- steering head on a short column, facing the operator
T0, T1 = (Y_PLAT + 0.1, DT), (Y_PLAT - 0.06, DT + 0.12)
cyl("till_turret", 0.075, 0.05, (0, T0[0], DT + 0.02), "plastic", bevel=0.015)
bar3d("till_arm", (0, T0[0], DT + 0.02), (0, T1[0], T1[1]), 0.075, 0.05, "chassis", bevel=0.018, segments=3)
tilt = math.atan2(T0[0] - T1[0], T1[1] - T0[1])
head = empty("till_head", (0, T1[0], T1[1]), rot=(tilt, 0, 0))
box("head_body", (0.15, 0.085, 0.17), (0, 0, 0.04), "plastic", bevel=0.025, parent=head)
for sx in (-1, 1):
    tube("grip_frame", [(sx * 0.06, 0, -0.035), (sx * 0.2, 0, -0.035), (sx * 0.225, 0, 0.0), (sx * 0.225, 0, 0.13), (sx * 0.2, 0, 0.16), (sx * 0.06, 0, 0.12)], 0.014, "plastic", parent=head)
    cyl("grip", 0.021, 0.12, (sx * 0.225, 0, 0.065), "vinyl", bevel=0.006, parent=head)
    box("butterfly", (0.075, 0.022, 0.06), (sx * 0.125, 0.03, 0.075), "paint", bevel=0.008, parent=head, rot=(R(-20), 0, sx * R(12)))
    cyl("bfly_axle", 0.012, 0.05, (sx * 0.09, 0.012, 0.075), "steel", axis='X', parent=head)
    cyl("horn", 0.013, 0.012, (sx * 0.04, 0.045, 0.09), "hazard", axis='Y', parent=head)
    box("liftbtn", (0.03, 0.01, 0.022), (sx * 0.035, 0.044, 0.02), "decal", bevel=0.003, parent=head)
box("belly", (0.12, 0.07, 0.03), (0, 0, 0.135), "accent", bevel=0.012, parent=head)

# ---------------------------------------------------------------- stand-on platform (open both sides)
PC = (Y_BULK + Y_PLAT) / 2
PL = Y_PLAT - Y_BULK
box("plat_frame", (2 * HW - 0.02, PL + 0.06, 0.09), (0, PC, FZ - 0.05), "chassis", bevel=0.014)
box("plat_mat", (2 * HW - 0.1, PL - 0.06, 0.008), (0, PC, FZ - 0.002), "rubber", bevel=0.002)
for i in range(8):
    box("plat_rib", (2 * HW - 0.14, 0.014, 0.006), (0, Y_BULK + 0.07 + i * 0.066, FZ + 0.004), "rubber", bevel=0, segments=1)
box("deadman", (0.3, 0.22, 0.012), (0, PC + 0.03, FZ + 0.006), "plastic", bevel=0.004)
for sx in (-1, 1):
    box("plat_edge", (0.022, PL - 0.02, 0.092), (sx * (HW - 0.012), PC, FZ - 0.05), "hazard", bevel=0.004)
    wheel("plat_castor", 0.04, 0.04, (sx * 0.3, PC, 0.04), rim="rim")
# bulkhead between the platform and the lifting battery, carrying the padded backrest
BT = 0.98
bx = HW - 0.01
profile("bulkhead", [(-bx, 0.06), (bx, 0.06), (bx, 0.72)] + arc_pts(bx - 0.14, BT - 0.14, 0.14, 20, 90, 6) + arc_pts(-bx + 0.14, BT - 0.14, 0.14, 90, 160, 6) + [(-bx, 0.72)], 0.05, (0, Y_BULK + 0.005, 0), "paint", bevel=0.016, plane='XZ')
box("bulk_cap", (0.5, 0.058, 0.02), (0, Y_BULK + 0.005, BT - 0.002), "plastic", bevel=0.006)
# pick terminal on an arm from the drive unit
rtube("term_arm", [(-0.33, Y_PLAT + 0.3, DT + 0.1), (-0.33, Y_PLAT + 0.34, DT + 0.16)], 0.012, "mast")
box("term", (0.2, 0.03, 0.14), (-0.3, Y_PLAT + 0.34, DT + 0.19), "plastic", bevel=0.01, rot=(R(-20), 0, 0))
box("term_s", (0.17, 0.004, 0.11), (-0.3, Y_PLAT + 0.324, DT + 0.184), "glass", bevel=0, rot=(R(-20), 0, 0))
box("bulk_kick", (0.6, 0.012, 0.3), (0, Y_BULK + 0.032, 0.36), "chassis", bevel=0.004)
for sx in (-1, 1):
    rtube("rest_post", [(sx * 0.2, Y_BULK + 0.005, BT - 0.05), (sx * 0.2, Y_BULK + 0.005, 1.25)], 0.018, "mast")
    box("rest_wing", (0.06, 0.1, 0.3), (sx * 0.27, Y_BULK + 0.06, 1.2), "vinyl", bevel=0.025, rot=(0, 0, sx * R(-25)))
for sx in (-1, 1):
    # grab hoops on the bulkhead corners
    rtube("bulk_grab", [(sx * 0.32, Y_BULK + 0.005, BT - 0.06), (sx * 0.32, Y_BULK + 0.005, BT + 0.2), (sx * 0.25, Y_BULK + 0.005, BT + 0.2)], 0.015, "mast", bend=0.06)
box("rest_plate", (0.5, 0.02, 0.42), (0, Y_BULK + 0.0, 1.2), "plastic", bevel=0.008)
box("rest_pad", (0.48, 0.07, 0.4), (0, Y_BULK + 0.04, 1.2), "vinyl", bevel=0.03, segments=4)
box("rest_lum", (0.36, 0.04, 0.16), (0, Y_BULK + 0.07, 1.12), "vinyl", bevel=0.018)
# pick-list clip and shrink-wrap holder on the load side of the backrest
box("clip", (0.24, 0.012, 0.3), (0.08, Y_BULK - 0.018, 1.2), "decal", bevel=0.003, rot=(R(6), 0, 0))
box("clip_top", (0.1, 0.02, 0.03), (0.08, Y_BULK - 0.03, 1.34), "steel", bevel=0.004)

# ================================================================ lifting part: long forks + battery box
forks = empty("forks", (0, 0, 0))
key(forks, FRAME_REST, loc=(0, 0, 0))
key(forks, FRAME_WORK, loc=(0, 0, LIFT))
BY0, BY1 = Y_HEEL, Y_BULK - 0.035
BC = (BY0 + BY1) / 2
box("batt_box", (2 * HW - 0.02, BY1 - BY0, 0.68), (0, BC, 0.43), "paint", bevel=0.03, parent=forks)
box("batt_lid", (2 * HW - 0.07, BY1 - BY0 - 0.04, 0.03), (0, BC, 0.78), "plastic", bevel=0.012, parent=forks)
tube("batt_handle", [(-0.1, BC, 0.79), (-0.1, BC, 0.82), (0.1, BC, 0.82), (0.1, BC, 0.79)], 0.008, "steel", parent=forks)
box("batt_plug", (0.07, 0.05, 0.05), (0.27, BC + 0.05, 0.805), "tail", bevel=0.01, parent=forks)
cyl("wrap_roll", 0.05, 0.22, (-0.24, BC, 0.845), "decal", bevel=0.004, parent=forks)
cyl("wrap_core", 0.02, 0.24, (-0.24, BC, 0.845), "card", parent=forks)
box("batt_panel", (0.56, 0.006, 0.36), (0, BY0 - 0.001, 0.52), "chassis", bevel=0.004, parent=forks)
box("batt_hazard", (0.7, 0.006, 0.04), (0, BY0 - 0.002, 0.22), "hazard", bevel=0, parent=forks)
for i in range(9):
    box("batt_chev", (0.025, 0.008, 0.04), (-0.304 + i * 0.076, BY0 - 0.003, 0.22), "chassis", bevel=0, parent=forks, rot=(0, R(35), 0))
for sx in (-1, 1):
    box("batt_latch", (0.012, 0.04, 0.04), (sx * (HW - 0.008), BC, 0.62), "accent", bevel=0.004, parent=forks)
    box("batt_door", (0.012, BY1 - BY0 - 0.1, 0.4), (sx * (HW - 0.01), BC, 0.4), "paint", bevel=0.008, parent=forks)
box("heel_xm", (0.6, 0.1, 0.09), (0, Y_HEEL - 0.03, 0.105), "paint", bevel=0.012, parent=forks)
t, sk = 0.012, 0.03                # top plate thickness, skirt bottom height
RR, LL, pz = 0.037, 0.16, 0.052
for sx in (-1, 1):
    x = sx * BX
    u = [(-BLW / 2, sk), (-BLW / 2, BLH), (BLW / 2, BLH), (BLW / 2, sk), (BLW / 2 - 0.015, sk), (BLW / 2 - 0.015, BLH - t), (-BLW / 2 + 0.015, BLH - t), (-BLW / 2 + 0.015, sk)]
    L = Y_HEEL - (Y_TIP + 0.14)
    profile("blade", u, L, (x, Y_HEEL - L / 2, 0), "paint", bevel=0.005, parent=forks, plane='XZ', segments=2)
    profile("blade_tip", [(Y_TIP + 0.15, sk), (Y_TIP + 0.15, BLH), (Y_TIP + 0.07, BLH), (Y_TIP, 0.06), (Y_TIP, 0.04), (Y_TIP + 0.03, sk)], BLW, (x, 0, 0), "paint", bevel=0.008, parent=forks)
    cyl("entry_roller", 0.018, BLW - 0.05, (x, Y_TIP + 0.035, 0.036), "rim", axis='X', parent=forks)
    # tandem load rollers on a trailing link: keyed every frame so the rollers stay on the floor
    link = empty("roller_link%d" % sx, (x, -1.46, pz), forks)
    for s2 in (-1, 1):
        bar3d("link_plate", (s2 * 0.05, 0.015, 0), (s2 * 0.05, -LL - 0.015, 0), 0.008, 0.035, "steel", bevel=0.003, parent=link)
    cyl("link_pin", 0.01, 0.13, (0, 0, 0), "steel", axis='X', parent=link)
    cyl("load_roller", RR, 0.085, (0, -LL, 0), "rim", axis='X', parent=link, bevel=0.006)
    cyl("load_roller_ax", 0.009, 0.11, (0, -LL, 0), "steel", axis='X', parent=link)
    for f in FRAMES:
        key(link, f, rot=(math.asin((pz + lift(f) - RR) / LL), 0, 0))

# ================================================================ two pallets, standing on the floor until the blades pick them up
DECK_UNDER = 0.10                  # underside of the (turned) pallet's stringer boards above its own base
PAL_F, PAL_R = Y_TIP + 0.6, Y_TIP + 1.82
pf = pallet("pal_front", (0, PAL_F, 0), rot=(0, 0, R(90)))            # front pallet: fully loaded
pr = pallet("pal_rear", (0, PAL_R, 0), load=False, rot=(0, 0, R(90)))  # rear pallet: being picked onto
cz = empty("cartons", (0, 0, 0.144), pr, rot=(0, 0, -R(90)))
cart = [((0.44, 0.56, 0.36), (-0.25, -0.28, 0.18), "card"), ((0.44, 0.56, 0.36), (0.22, -0.3, 0.18), "card2"),
        ((0.5, 0.4, 0.3), (-0.2, 0.26, 0.15), "card2"), ((0.42, 0.5, 0.28), (-0.2, -0.3, 0.50), "card")]
for s, l, m in cart:
    box("carton", s, l, m, 0.008, cz, segments=2)
    box("carton_tape", (0.06, s[1] + 0.002, 0.003), (l[0], l[1], l[2] + s[2] / 2), "tape", 0, cz)
for f in FRAMES:
    z = max(0.0, BLH + lift(f) - DECK_UNDER)
    key(pf, f, loc=(0, PAL_F, z))
    key(pr, f, loc=(0, PAL_R, z))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "picker_low.glb"))
