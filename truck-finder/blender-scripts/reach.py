import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from wh_common import *
reset()
R = math.radians
W = 0.625          # half width
BF, BR = 0.05, 1.20  # body front / rear
ZB = 0.33          # floor / chassis top
ZT = 0.98          # battery compartment top
ZC = 1.02          # rear cowl top

# ---------------- chassis base & legs ----------------
base = [(-W, BF), (W, BF)] + arc_pts(W - 0.2, BR - 0.2, 0.2, 0, 90, 8) + arc_pts(-W + 0.2, BR - 0.2, 0.2, 90, 180, 8)
profile("base", base, 0.22, (0, 0, 0.22), "chassis", bevel=0.02, plane='XY')
# rear bumper band + hazard stripe
bump = [(-W - 0.012, 0.75)] + [(-W - 0.012, 0.75), (W + 0.012, 0.75)] + arc_pts(W - 0.2, BR - 0.2, 0.212, 0, 90, 8) + arc_pts(-W + 0.2, BR - 0.2, 0.212, 90, 180, 8)
profile("bumper", bump[1:], 0.09, (0, 0, 0.2), "rubber", bevel=0.015, plane='XY')
for i in range(7):
    profile("haz", [(0, 0), (0.055, 0), (0.095, 0.07), (0.04, 0.07)], 0.008, (-0.41 + i * 0.11, BR + 0.012, 0.165), "hazard", bevel=0, plane='XZ')
for sx in (-1, 1):
    x = sx * 0.55
    box("leg", (0.15, 1.05, 0.25), (x, -0.375, 0.185), "chassis", 0.018)
    box("leg_root", (0.15, 0.30, 0.34), (x, -0.02, 0.23), "chassis", 0.03)       # gusset where leg meets body
    profile("leg_gus", [(0.0, 0.0), (-0.32, 0.0), (0.0, 0.14)], 0.15, (x, -0.16, 0.30), "chassis", bevel=0.01)
    nose = [(0.0, 0.065), (0.0, 0.305), (-0.13, 0.305)] + arc_pts(-0.15, 0.165, 0.135, 100, 255, 12)
    for o in (-0.064, 0.064):
        profile("leg_fork", nose, 0.022, (x + o, -0.90, 0), "chassis", bevel=0.006)
    box("leg_cap", (0.15, 0.2, 0.02), (x, -0.98, 0.297), "chassis", 0.006)
    wheel("load_w", 0.15, 0.10, (x, -1.05, 0.15), rim="rim")
    cyl("load_ax", 0.022, 0.16, (x, -1.05, 0.15), "steel", axis='X', bevel=0.004)
    # wear strip / roller track on the inner face and top
    box("leg_track", (0.012, 1.0, 0.09), (x - sx * 0.079, -0.42, 0.18), "steel", 0.003)
    box("leg_top", (0.10, 0.9, 0.006), (x, -0.42, 0.312), "mast", 0.002)
    box("leg_tip", (0.153, 0.05, 0.12), (x, -0.87, 0.24), "hazard", 0.004)

# drive wheel + caster under the body
wheel("drive", 0.175, 0.13, (0.0, 0.88, 0.175), rim="rim")
box("drive_fork", (0.2, 0.2, 0.1), (0, 0.88, 0.2), "chassis", 0.02)
wheel("caster", 0.09, 0.07, (0.4, 0.95, 0.09), rim="rim")
wheel("caster", 0.09, 0.07, (-0.4, 0.95, 0.09), rim="rim")

# ---------------- battery compartment ----------------
box("batt", (2 * W, 0.45, ZT - ZB + 0.02), (0, BF + 0.225, (ZT + ZB) / 2 - 0.01), "paint", 0.03)
for sx in (-1, 1):
    # battery side door, proud panel with handle and latch
    box("batt_door", (0.02, 0.36, 0.48), (sx * (W + 0.002), BF + 0.225, 0.63), "paint", 0.012)
    box("batt_handle", (0.02, 0.14, 0.035), (sx * (W + 0.012), BF + 0.225, 0.80), "chassis", 0.008)
    box("batt_latch", (0.02, 0.04, 0.04), (sx * (W + 0.012), BF + 0.36, 0.5), "accent", 0.006)
    for k in range(4):
        box("batt_vent", (0.02, 0.2, 0.012), (sx * (W + 0.006), BF + 0.225, 0.47 + k * 0.035), "chassis", 0.002, segments=1)
box("batt_lid", (2 * W - 0.06, 0.40, 0.03), (0, BF + 0.225, ZT + 0.005), "plastic", 0.012)
box("batt_front", (1.0, 0.012, 0.5), (0, BF - 0.004, 0.66), "chassis", 0.004)   # dark panel facing the mast
box("plate", (0.012, 0.11, 0.075), (W + 0.004, BF + 0.1, 0.9), "decal", 0.002)

# ---------------- rear cowl (L shape: rear wall + wall behind seat) ----------------
XI = -0.49
cowl = [(-W, 0.50), (XI, 0.50), (XI, 0.96), (W - 0.03, 0.96), (W, 0.99)] + arc_pts(W - 0.2, BR - 0.2, 0.2, 0, 90, 8) + arc_pts(-W + 0.2, BR - 0.2, 0.2, 90, 180, 8)
profile("cowl", cowl, ZC - ZB, (0, 0, (ZC + ZB) / 2), "paint", bevel=0.035, plane='XY', segments=4)
# seam + service cover on the rear, tail lights
box("rear_cover", (0.62, 0.02, 0.42), (0, BR + 0.0, 0.66), "paint", 0.012)
for k in range(5):
    box("rear_vent", (0.36, 0.02, 0.014), (0, BR + 0.008, 0.52 + k * 0.04), "chassis", 0.002, segments=1)
box("rear_grip", (0.2, 0.03, 0.03), (0, BR + 0.012, 0.82), "chassis", 0.008)
for sx in (-1, 1):
    box("tail", (0.06, 0.02, 0.1), (sx * 0.4, BR - 0.012, 0.86), "tail", 0.006, rot=(0, 0, sx * R(-18)))
box("side_cover", (0.02, 0.4, 0.5), (-W - 0.002, 0.76, 0.66), "paint", 0.012)
for k in range(4):
    box("side_vent", (0.02, 0.24, 0.012), (-W - 0.008, 0.76, 0.5 + k * 0.035), "chassis", 0.002, segments=1)
box("cowl_top", (0.11, 0.42, 0.02), (-0.56, 0.74, ZC + 0.004), "plastic", 0.008)

# ---------------- operator compartment ----------------
box("floor", (0.66, 0.46, 0.012), (0.28, 0.73, ZB + 0.004), "rubber", 0.003)
box("sill", (0.035, 0.46, 0.03), (W - 0.02, 0.73, ZB + 0.012), "hazard", 0.006)
box("pedestal", (0.47, 0.44, 0.33), (-0.25, 0.75, ZB + 0.16), "paint", 0.03)
box("ped_kick", (0.012, 0.3, 0.16), (-0.012, 0.75, 0.47), "plastic", 0.004)
seat("seat", (-0.215, 0.75, 0.68), R(90), armrests=False)
# pedals
box("deadman", (0.2, 0.11, 0.02), (0.3, 0.86, ZB + 0.03), "chassis", 0.006, rot=(0, R(-10), 0))
box("accel", (0.16, 0.07, 0.016), (0.32, 0.62, ZB + 0.05), "chassis", 0.005, rot=(0, R(-28), 0))
box("brake", (0.12, 0.09, 0.016), (0.3, 0.73, ZB + 0.05), "chassis", 0.005, rot=(0, R(-28), 0))
# right-hand console on the battery lid: armrest, joystick, display
box("cons_r", (0.56, 0.2, 0.09), (-0.1, 0.42, ZT + 0.05), "plastic", 0.03)
box("armpad", (0.3, 0.1, 0.035), (-0.22, 0.44, ZT + 0.105), "vinyl", 0.016)
cyl("joy_boot", 0.035, 0.03, (0.02, 0.42, ZT + 0.105), "rubber", radius2=0.02)
cyl("joy", 0.011, 0.09, (0.02, 0.42, ZT + 0.16), "steel")
box("joy_knob", (0.04, 0.045, 0.06), (0.02, 0.42, ZT + 0.215), "vinyl", 0.015)
for k in range(3):
    cyl("fing", 0.008, 0.045, (0.09 + k * 0.03, 0.42, ZT + 0.115), "chassis")
cyl("estop", 0.024, 0.03, (0.3, 0.38, ZT + 0.03), "accent", bevel=0.006)
box("disp", (0.2, 0.03, 0.13), (0.42, 0.3, ZT + 0.1), "plastic", 0.012, rot=(R(-25), 0, R(-25)))
box("disp_s", (0.16, 0.004, 0.09), (0.427, 0.316, ZT + 0.107), "glass", 0.0, rot=(R(-25), 0, R(-25)))
cyl("disp_arm", 0.012, 0.08, (0.42, 0.29, ZT + 0.04), "chassis")
# steering console on rear cowl (operator's left hand)
pod = [(-0.14, 0.0), (0.14, 0.0), (0.14, 0.05)] + arc_pts(0.08, 0.05, 0.06, 0, 90, 5) + arc_pts(-0.08, 0.05, 0.06, 90, 180, 5)
profile("steer_pod", pod, 0.2, (-0.05, 1.06, ZC), "plastic", bevel=0.02, plane='XZ')
st = empty("steer", (-0.05, 1.04, ZC + 0.15), rot=(R(20), R(12), 0))
cyl("st_col", 0.016, 0.06, (0, 0, -0.03), "chassis", parent=st)
lathe("st_rim", [(0.07, -0.01), (0.092, -0.012), (0.1, 0.0), (0.092, 0.012), (0.07, 0.01), (0.07, -0.01)], (0, 0, 0.0), "vinyl", axis='Z', parent=st, steps=28)
cyl("st_disc", 0.072, 0.012, (0, 0, 0), "plastic", parent=st, bevel=0.003)
cyl("st_knob", 0.02, 0.05, (0.07, 0.0, 0.035), "vinyl", parent=st, bevel=0.008)
cyl("keysw", 0.014, 0.02, (0.3, 1.08, ZC + 0.01), "steel")
box("sw_panel", (0.2, 0.1, 0.012), (0.33, 1.08, ZC + 0.002), "plastic", 0.004)
for k in range(3):
    box("sw", (0.025, 0.03, 0.012), (0.36 + k * 0.04, 1.08, ZC + 0.012), "chassis" if k else "accent", 0.003)

# ---------------- overhead guard ----------------
GZ = 2.17
for sx in (-1, 1):
    x = sx * 0.565
    rtube("guard_side", [(x, 0.13, ZT - 0.02), (x, 0.13, GZ), (x, 1.10, GZ), (x, 1.10, ZC - 0.02)], 0.028, "mast", bend=0.12)
    cyl("guard_foot", 0.04, 0.03, (x, 0.13, ZT + 0.012), "mast", bevel=0.006)
    cyl("guard_foot", 0.04, 0.03, (x, 1.10, ZC + 0.012), "mast", bevel=0.006)
for k in range(9):
    y = 0.23 + k * 0.097
    box("roof_bar", (1.13, 0.016, 0.045), (0, y, GZ), "mast", 0.004, segments=1)
box("roof_rail", (0.02, 0.86, 0.04), (0, 0.615, GZ - 0.005), "mast", 0.004, segments=1)
rtube("grab", [(0.565, 0.13, 1.25), (0.50, 0.19, 1.3), (0.50, 0.19, 1.6), (0.565, 0.13, 1.65)], 0.014, "accent", bend=0.04)
lamp("worklamp", (-0.45, 0.16, GZ - 0.08))
lamp("worklamp", (0.45, 0.16, GZ - 0.08))
beacon("beacon", (-0.4, 1.02, GZ + 0.035))
rtube("mirror_arm", [(0.565, 1.1, 1.75), (0.66, 1.1, 1.8), (0.68, 1.08, 1.86)], 0.008, "mast", bend=0.03)
box("mirror", (0.02, 0.12, 0.18), (0.685, 1.07, 1.92), "plastic", 0.012)
box("mirror_g", (0.004, 0.1, 0.16), (0.685, 1.058, 1.92), "chrome", 0.0, rot=(0, 0, 0))

# clear screen between operator and mast, battery plug
box("screen", (1.07, 0.006, 1.02), (0, 0.13, 1.58), "glass", 0)
box("screen_rail", (1.1, 0.02, 0.03), (0, 0.13, 1.06), "mast", 0.005)
box("plug", (0.07, 0.1, 0.05), (-0.45, 0.2, ZT + 0.04), "tail", 0.012)
rtube("plug_cable", [(-0.45, 0.25, ZT + 0.04), (-0.45, 0.33, ZT + 0.05), (-0.5, 0.36, ZT + 0.02)], 0.012, "rubber", bend=0.03)
# ---------------- reach carriage + mast (slides along the legs) ----------------
YM = -0.14
reach = empty("reach", (0, YM, 0))
box("rc_beam", (0.90, 0.26, 0.11), (0, 0.04, 0.135), "chassis", 0.015, reach)
for sx in (-1, 1):
    box("rc_side", (0.05, 0.42, 0.2), (sx * 0.44, -0.04, 0.18), "chassis", 0.012, reach)
    for yy in (-0.2, 0.1):
        cyl("rc_roller", 0.045, 0.04, (sx * 0.462, yy, 0.18), "steel", axis='X', parent=reach, bevel=0.005)
    profile("rc_brace", [(0.075, 0.0), (0.075, 0.5), (0.2, 0.0)], 0.03, (sx * 0.425, 0, 0.19), "chassis", bevel=0.006, parent=reach)
    cyl("reach_rod", 0.022, 0.72, (sx * 0.22, 0.51, 0.15), "chrome", axis='Y', parent=reach)
    cyl("reach_eye", 0.035, 0.06, (sx * 0.22, 0.16, 0.15), "chassis", axis='Y', parent=reach, bevel=0.006)

MH = 2.62
mid = empty("mast_mid", (0, 0, 0), reach)
inn = empty("mast_inner", (0, 0, 0), reach)
for sx in (-1, 1):
    channel("m_out", 0.085, 0.16, 0.016, MH - 0.08, (sx * 0.40, 0, 0.08 + (MH - 0.08) / 2), "mast", reach, open_dir=-sx)
    channel("m_mid", 0.07, 0.12, 0.013, MH - 0.14, (sx * 0.32, 0, 0.12 + (MH - 0.14) / 2), "mast", mid, open_dir=-sx)
    channel("m_inn", 0.06, 0.09, 0.012, MH - 0.2, (sx * 0.25, 0, 0.16 + (MH - 0.2) / 2), "mast", inn, open_dir=-sx)
    # main lift cylinders behind the outer uprights; rods ride with the middle stage
    cyl("lift_cyl", 0.032, 2.2, (sx * 0.40, 0.115, 1.25), "chassis", parent=reach, bevel=0.004)
    cyl("lift_cap", 0.037, 0.04, (sx * 0.40, 0.115, 2.35), "steel", parent=reach, bevel=0.004)
    cyl("lift_rod", 0.02, 0.72, (sx * 0.40, 0.115, 2.14), "chrome", parent=mid)
    box("lift_lug", (0.09, 0.12, 0.04), (sx * 0.37, 0.075, 2.52), "mast", 0.006, mid)
    # chain rollers at the top of the middle stage
    cyl("mid_pul", 0.045, 0.03, (sx * 0.32, 0.0, MH - 0.01), "steel", axis='X', parent=mid, bevel=0.004)
    # hose run down the outer upright
    rtube("hose", [(sx * 0.455, 0.05, 0.3), (sx * 0.455, 0.05, 2.3), (sx * 0.455, -0.0, 2.42), (sx * 0.43, -0.07, 2.3)], 0.011, "rubber", reach, bend=0.05)
for sx in (-1, 1):
    for k in range(3):
        profile("m_haz", [(0, 0), (0.03, 0), (0.06, 0.05), (0.03, 0.05)], 0.004, (sx * 0.40 - 0.045 + k * 0.03, -0.081, 1.45), "hazard" if k != 1 else "chassis", bevel=0, plane='XZ', parent=reach)
for z in (0.3, 1.3, 2.5):
    box("out_x", (0.86, 0.018, 0.12), (0, 0.076, z), "mast", 0.004, reach)
box("out_foot", (0.88, 0.16, 0.05), (0, 0.0, 0.215), "mast", 0.008, reach)
box("mid_x", (0.68, 0.014, 0.10), (0, 0.054, 2.52), "mast", 0.003, mid)
box("mid_x", (0.68, 0.014, 0.10), (0, 0.054, 0.3), "mast", 0.003, mid)
box("inn_x", (0.54, 0.03, 0.08), (0, 0.02, MH - 0.1), "mast", 0.006, inn)
box("inn_x", (0.54, 0.03, 0.08), (0, 0.02, 0.24), "mast", 0.006, inn)
# free-lift cylinder on the inner stage, rod + chain pulley on their own pivot
cyl("fl_cyl", 0.042, 1.0, (0, 0.0, 0.78), "chassis", parent=inn, bevel=0.005)
cyl("fl_cap", 0.047, 0.04, (0, 0.0, 1.27), "steel", parent=inn, bevel=0.004)
pul = empty("mast_pulley", (0, 0, 0), inn)
cyl("fl_rod", 0.026, 0.62, (0, 0, 1.03), "chrome", parent=pul)
box("fl_head", (0.2, 0.05, 0.05), (0, 0, 1.36), "mast", 0.01, pul)
for sx in (-1, 1):
    cyl("fl_pul", 0.055, 0.035, (sx * 0.075, 0, 1.39), "steel", axis='X', parent=pul, bevel=0.005)

# fork carriage
CZ = 0.33
car = empty("carriage", (0, -0.105, CZ), reach)
for sx in (-1, 1):
    fork_tine("tine", (sx * 0.27, -0.02, 0), car, length=1.15, height=0.56, width=0.1)
    box("car_side", (0.025, 0.14, 0.52), (sx * 0.20, 0.06, 0.32), "mast", 0.004, car)
    for zz in (0.14, 0.5):
        cyl("car_roll", 0.04, 0.03, (sx * 0.225, 0.105, zz), "steel", axis='X', parent=car, bevel=0.004)
    box("tine_hook", (0.11, 0.05, 0.05), (sx * 0.27, 0.0, 0.585), "steel", 0.008, car)
box("car_top", (0.92, 0.04, 0.10), (0, 0.0, 0.51), "mast", 0.008, car)
box("car_bot", (0.92, 0.04, 0.10), (0, 0.0, 0.13), "mast", 0.008, car)
box("car_plate", (0.42, 0.02, 0.3), (0, 0.012, 0.32), "mast", 0.004, car)
cyl("sideshift", 0.028, 0.5, (0, -0.005, 0.32), "chassis", axis='X', parent=car, bevel=0.004)
cyl("sideshift_r", 0.014, 0.7, (0, -0.005, 0.32), "chrome", axis='X', parent=car)
backrest("br", car, width=0.9, z0=0.57, z1=1.22)
pallet("pal", (0, -0.59, 0.045), car)
# lift chains: scale with the motion so they always join pulley and carriage
PZ = 1.39 + 0.055
for sx in (-1, 1):
    cf = chain("chain_f", 1.0, (sx * 0.075, 0.05, 0.55), car)          # carriage -> pulley
    key(cf, FRAME_REST, scale=(1, 1, (PZ - (CZ + 0.55)) / 1.0))
    key(cf, FRAME_WORK, scale=(1, 1, max(0.02, (PZ + 1.2 + 0.55 - (CZ + 0.55 + 2.3)) / 1.0)))
    cr = chain("chain_r", 1.0, (sx * 0.075, 0.055, 0.9), inn)            # anchor on cylinder -> pulley
    key(cr, FRAME_REST, scale=(1, 1, PZ - 0.9))
    key(cr, FRAME_WORK, scale=(1, 1, PZ + 0.55 - 0.9))
box("chain_anchor", (0.22, 0.03, 0.04), (0, 0.045, 0.9), "mast", 0.006, inn)

# ---------------- motion ----------------
key(reach, FRAME_REST, loc=(0, YM, 0)); key(reach, FRAME_WORK, loc=(0, YM - 0.6, 0))
key(mid, FRAME_REST, loc=(0, 0, 0)); key(mid, FRAME_WORK, loc=(0, 0, 0.6))
key(inn, FRAME_REST, loc=(0, 0, 0)); key(inn, FRAME_WORK, loc=(0, 0, 1.2))
key(pul, FRAME_REST, loc=(0, 0, 0)); key(pul, FRAME_WORK, loc=(0, 0, 0.55))
key(car, FRAME_REST, loc=(0, -0.105, CZ)); key(car, FRAME_WORK, loc=(0, -0.105, CZ + 2.3))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "reach.glb"))
