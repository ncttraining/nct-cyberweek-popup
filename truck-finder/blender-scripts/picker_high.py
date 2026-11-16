import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from wh_common import *
reset()
R = math.radians

W = 0.50            # half width of the chassis
LIFT = 3.9          # platform rise
INN = 2.2           # inner mast stage rise
MY = 0.62           # mast centre (y)
MT = 2.78           # top of the outer mast
Y0, Y1 = 0.74, 1.38  # drive / battery unit front and back
FZ = 0.25           # platform floor surface (lowered)
PF, PR = -0.30, 0.45  # platform front / rear edge


def plan(x, y0, y1, r, n=8):
    return [(-x, y0), (x, y0)] + arc_pts(x - r, y1 - r, r, 0, 90, n) + arc_pts(-x + r, y1 - r, r, 90, 180, n)


# ================================================================ chassis
profile("slab", plan(W, 0.47, Y1 + 0.02, 0.14), 0.17, (0, 0, 0.145), "chassis", bevel=0.02, plane='XY')
profile("bumper", plan(W + 0.012, 1.0, Y1 + 0.032, 0.15), 0.09, (0, 0, 0.15), "rubber", bevel=0.015, plane='XY')
for i in range(7):
    profile("haz", [(0, 0), (0.05, 0), (0.085, 0.07), (0.035, 0.07)], 0.008, (-0.36 + i * 0.1, Y1 + 0.045, 0.115), "hazard", bevel=0, plane='XZ')
# base legs running forward under the platform, load wheels in the forked tips
for sx in (-1, 1):
    x = sx * 0.42
    box("leg", (0.13, 0.62, 0.13), (x, 0.18, 0.115), "chassis", 0.015)
    profile("leg_gus", [(0.0, 0.0), (-0.3, 0.0), (0.0, 0.05)], 0.13, (x, 0.47, 0.18), "chassis", bevel=0.006)
    nose = [(0.0, 0.05), (0.0, 0.18), (-0.1, 0.18)] + arc_pts(-0.13, 0.09, 0.085, 95, 265, 12) + [(-0.1, 0.05)]
    for o in (-0.056, 0.056):
        profile("leg_fork", nose, 0.018, (x + o, -0.085, 0), "chassis", bevel=0.005)
    wheel("load_w", 0.08, 0.085, (x, -0.2, 0.08), rim="rim")
    cyl("load_ax", 0.014, 0.135, (x, -0.2, 0.08), "steel", axis='X', bevel=0.003)
    box("leg_tip", (0.134, 0.03, 0.05), (x, -0.105, 0.15), "hazard", 0.004)
    # aisle guide rollers
    for yy in (0.0, 1.2):
        box("gr_brk", (0.08, 0.08, 0.02), (sx * (W + 0.0), yy, 0.135), "chassis", 0.005)
        cyl("gr", 0.045, 0.04, (sx * (W + 0.03), yy, 0.105), "rubber", bevel=0.008)
        cyl("gr_c", 0.02, 0.046, (sx * (W + 0.03), yy, 0.105), "rim", bevel=0.003)
box("leg_x", (0.84, 0.1, 0.1), (0, 0.42, 0.11), "chassis", 0.012)
wheel("drive", 0.14, 0.11, (0.0, 1.08, 0.14), rim="rim")
box("drive_fork", (0.2, 0.2, 0.08), (0, 1.08, 0.2), "chassis", 0.02)
for sx in (-1, 1):
    wheel("castor", 0.06, 0.05, (sx * 0.36, 1.2, 0.06), rim="rim")

# ---------------------------------------------------------------- drive / battery unit
profile("unit_low", plan(W - 0.01, Y0, Y1, 0.13), 0.56, (0, 0, 0.50), "paint", bevel=0.02, plane='XY')
profile("unit_top", plan(W - 0.01, Y0, Y1, 0.13), 0.32, (0, 0, 0.94), "paint", bevel=0.07, plane='XY', segments=5)
profile("unit_seam", plan(W - 0.006, Y0 + 0.005, Y1 + 0.004, 0.132), 0.014, (0, 0, 0.785), "chassis", bevel=0, plane='XY')
box("lid", (0.78, 0.4, 0.02), (0, 1.04, 1.105), "plastic", 0.008)
for xx in (-0.22, 0.22):
    box("lid_grip", (0.14, 0.03, 0.022), (xx, 0.9, 1.122), "chassis", 0.008)
for sx in (-1, 1):
    box("batt_door", (0.02, 0.42, 0.46), (sx * (W - 0.006), 1.0, 0.5), "paint", 0.012)
    box("batt_handle", (0.02, 0.14, 0.03), (sx * (W + 0.004), 1.0, 0.66), "chassis", 0.008)
    box("batt_latch", (0.02, 0.035, 0.035), (sx * (W + 0.004), 1.17, 0.36), "accent", 0.006)
    for k in range(4):
        box("batt_vent", (0.02, 0.26, 0.012), (sx * (W - 0.002), 1.0, 0.33 + k * 0.035), "chassis", 0.002, segments=1)
    box("tail", (0.06, 0.02, 0.1), (sx * 0.3, Y1 + 0.002, 0.9), "tail", 0.006)
box("plate", (0.012, 0.1, 0.07), (W - 0.006, 0.86, 0.92), "decal", 0.002)
box("rear_cover", (0.5, 0.02, 0.36), (0, Y1 + 0.0, 0.52), "paint", 0.012)
for k in range(5):
    box("rear_vent", (0.34, 0.02, 0.013), (0, Y1 + 0.008, 0.42 + k * 0.04), "chassis", 0.002, segments=1)
box("rear_grip", (0.2, 0.03, 0.028), (0, Y1 + 0.012, 0.66), "chassis", 0.008)
cyl("estop_b", 0.04, 0.012, (0.34, 1.2, 1.102), "hazard")
cyl("estop", 0.03, 0.03, (0.34, 1.2, 1.115), "accent", bevel=0.006)
beacon("beacon_r", (-0.34, 1.22, 1.11))
cyl("tow", 0.016, 0.09, (0, Y1 + 0.05, 0.24), "steel")
for zz in (0.205, 0.275):
    box("tow_b", (0.1, 0.07, 0.018), (0, Y1 + 0.035, zz), "chassis", 0.004)

# ================================================================ mast
box("mast_base", (0.86, 0.3, 0.08), (0, MY, 0.25), "chassis", 0.012)
inn = empty("mast_inner", (0, 0, 0))
for sx in (-1, 1):
    channel("m_out", 0.11, 0.2, 0.018, MT - 0.25, (sx * 0.345, MY, 0.25 + (MT - 0.25) / 2), "mast", open_dir=-sx)
    channel("m_inn", 0.08, 0.14, 0.014, MT - 0.38, (sx * 0.245, MY, 0.33 + (MT - 0.38) / 2), "mast", inn, open_dir=-sx)
    profile("m_gus", [(0.0, 0.0), (0.24, 0.0), (0.0, 0.5)], 0.025, (sx * 0.41, MY + 0.1, 0.29), "chassis", bevel=0.005)
    cyl("lift_cyl", 0.04, 1.5, (sx * 0.345, MY + 0.15, 1.05), "chassis", bevel=0.005)
    cyl("lift_cap", 0.046, 0.045, (sx * 0.345, MY + 0.15, 1.8), "steel", bevel=0.005)
    cyl("lift_rod", 0.026, 1.6, (sx * 0.345, MY + 0.15, 1.35), "chrome", parent=inn)
    box("lift_lug", (0.15, 0.17, 0.045), (sx * 0.3, MY + 0.085, 2.14), "mast", 0.008, inn)
    cyl("top_pul", 0.06, 0.035, (sx * 0.245, MY - 0.01, MT - 0.1), "steel", axis='X', parent=inn, bevel=0.005)
    rtube("hose", [(sx * 0.42, MY + 0.04, 0.4), (sx * 0.42, MY + 0.04, 2.5), (sx * 0.42, MY - 0.03, 2.62), (sx * 0.42, MY - 0.11, 2.5), (sx * 0.42, MY - 0.11, 2.3)], 0.012, "rubber", bend=0.05)
    for k in range(3):
        profile("m_haz", [(0, 0), (0.035, 0), (0.07, 0.06), (0.035, 0.06)], 0.004, (sx * 0.345 - 0.052 + k * 0.035, MY + 0.101, 1.3), "hazard" if k != 1 else "chassis", bevel=0, plane='XZ')
for z in (0.5, 1.25, 2.0, MT - 0.08):
    box("out_x", (0.8, 0.02, 0.12), (0, MY + 0.105, z), "mast", 0.004)
for z in (0.5, 1.6, MT - 0.2):
    box("inn_x", (0.56, 0.025, 0.09), (0, MY + 0.06, z), "mast", 0.006, inn)
cyl("top_ax", 0.018, 0.54, (0, MY - 0.01, MT - 0.1), "steel", axis='X', parent=inn)
# rear mesh guard between mast and drive unit side (protects the chains)
for sx in (-1, 1):
    box("unit_stripe", (0.006, 0.36, 0.035), (sx * (W - 0.008), 1.0, 0.86), "accent", 0)

# ================================================================ lifting operator platform
lift = empty("lift", (0, 0, 0))
PW = 0.5            # half width of the platform
PC = (PF + PR) / 2
# carriage in the mast
box("car_plate", (0.42, 0.04, 1.2), (0, MY - 0.115, 0.85), "chassis", 0.008, lift)
for sx in (-1, 1):
    box("car_side", (0.025, 0.17, 1.1), (sx * 0.19, MY - 0.045, 0.85), "chassis", 0.006, lift)
    for zz in (0.42, 0.85, 1.28):
        cyl("car_roll", 0.045, 0.03, (sx * 0.215, MY, zz), "steel", axis='X', parent=lift, bevel=0.005)
    # floor bearers (cantilever arms from the carriage)
    box("bearer", (0.07, PR - PF + 0.05, 0.06), (sx * 0.27, PC - 0.0, FZ - 0.075), "chassis", 0.01, lift)
    profile("bearer_gus", [(0.0, 0.0), (-0.28, 0.0), (0.0, -0.1)], 0.02, (sx * 0.27, PR + 0.02, FZ - 0.1), "chassis", bevel=0.004, parent=lift)
# floor with ribbed mat and presence (dead-man) pad
box("floor", (2 * PW, PR - PF, 0.045), (0, PC, FZ - 0.0225), "chassis", 0.01, lift)
box("mat", (2 * PW - 0.1, PR - PF - 0.1, 0.008), (0, PC, FZ + 0.003), "rubber", 0.002, lift)
for i in range(9):
    box("mat_rib", (2 * PW - 0.14, 0.014, 0.006), (0, PF + 0.1 + i * 0.07, FZ + 0.008), "rubber", 0, lift, segments=1)
box("deadman", (0.3, 0.2, 0.012), (0, PC + 0.02, FZ + 0.012), "plastic", 0.004, lift)
box("floor_edge", (2 * PW - 0.42, 0.03, 0.047), (0, PF + 0.012, FZ - 0.0225), "hazard", 0.004, lift)
# back wall towards the mast: storage/back panel, lean pad, mesh screen above
box("back", (2 * PW, 0.05, 1.0), (0, PR + 0.0, FZ + 0.5), "paint", 0.018, lift)
box("back_pad", (0.46, 0.04, 0.3), (0, PR - 0.035, FZ + 0.82), "vinyl", 0.018, lift)
box("back_tray", (0.7, 0.12, 0.02), (0, PR - 0.07, FZ + 0.42), "plastic", 0.006, lift)
box("back_tray_l", (0.7, 0.012, 0.06), (0, PR - 0.13, FZ + 0.44), "plastic", 0.004, lift)
box("screen", (2 * PW - 0.08, 0.006, 1.2), (0, PR + 0.005, FZ + 1.6), "glass", 0, lift)
for i in range(7):
    box("screen_bar", (0.012, 0.012, 1.2), (-0.36 + i * 0.12, PR + 0.005, FZ + 1.6), "mast", 0, lift, segments=1)
# side kick panels
for sx in (-1, 1):
    side = [(PR + 0.025, -0.045), (PF, -0.045), (PF, 0.15), (PF + 0.08, 0.2), (PR - 0.42, 0.2)] + arc_pts(PR - 0.42, 0.5, 0.3, 270, 360, 8) + [(PR - 0.12, 0.88)] + arc_pts(PR - 0.0, 0.88, 0.12, 180, 90, 6) + [(PR + 0.025, 1.0)]
    profile("skirt", side, 0.035, (sx * (PW - 0.0175), 0, FZ), "paint", bevel=0.01, parent=lift)
    box("skirt_tr", (0.04, PR - PF - 0.1, 0.028), (sx * (PW - 0.0175), PC, FZ - 0.03), "hazard", 0.004, lift)
# posts + overhead guard
GZ = FZ + 2.2
GX = PW - 0.03
for sx in (-1, 1):
    x = sx * GX
    rtube("post", [(x, PF + 0.03, FZ), (x, PF + 0.03, GZ), (x, PR - 0.0, GZ), (x, PR - 0.0, FZ + 0.95)], 0.024, "mast", lift, bend=0.12)
    cyl("post_ft", 0.036, 0.03, (x, PF + 0.03, FZ + 0.015), "mast", parent=lift, bevel=0.005)
    # side gate (yellow), hinged on the rear post, latching on the front post
    rtube("gate", [(x, PR - 0.02, FZ + 1.1), (x, PF + 0.09, FZ + 1.1), (x, PF + 0.09, FZ + 0.58), (x, PR - 0.02, FZ + 0.58)], 0.017, "hazard", lift, bend=0.06)
    cyl("gate_h", 0.028, 0.62, (x, PR - 0.01, FZ + 0.84), "chassis", parent=lift, bevel=0.005)
    box("gate_latch", (0.03, 0.07, 0.05), (x, PF + 0.06, FZ + 1.1), "accent", 0.008, lift)
    lamp("wl", (sx * 0.33, PF + 0.05, GZ - 0.075), lift)
    lamp("spot", (sx * 0.36, PF + 0.0, FZ + 0.08), lift, r=0.028)
rtube("guard_f", [(-GX, PF + 0.03, GZ), (GX, PF + 0.03, GZ)], 0.024, "mast", lift)
rtube("guard_r", [(-GX, PR, GZ), (GX, PR, GZ)], 0.024, "mast", lift)
for k in range(7):
    box("roof_bar", (2 * GX, 0.014, 0.04), (0, PF + 0.12 + k * 0.085, GZ), "mast", 0.004, lift, segments=1)
box("roof_rail", (0.018, PR - PF - 0.05, 0.035), (0, PC + 0.015, GZ - 0.004), "mast", 0.004, lift, segments=1)
beacon("beacon", (0.33, PR - 0.1, GZ + 0.03), lift)

# ---- control console: two pods on the front posts, leaving the centre open to step onto the pallet
CZ = FZ + 1.02
for sx in (-1, 1):
    x = sx * 0.345
    box("pod_col", (0.09, 0.07, 0.8), (sx * 0.4, PF + 0.07, FZ + 0.6), "plastic", 0.02, lift)
    pod = [(-0.08, -0.05), (-0.08, 0.02), (0.12, 0.07), (0.16, 0.05), (0.16, -0.03), (0.05, -0.09)]
    profile("pod", pod, 0.21, (x, PF + 0.07, CZ), "plastic", bevel=0.018, parent=lift)
    box("pod_grip", (0.2, 0.03, 0.03), (x, PF + 0.255, CZ + 0.0), "vinyl", 0.012, lift)
    rtube("pod_gr", [(x - 0.09, PF + 0.2, CZ - 0.0), (x - 0.09, PF + 0.255, CZ), (x + 0.09, PF + 0.255, CZ), (x + 0.09, PF + 0.2, CZ)], 0.01, "chassis", lift, bend=0.02)
tilt = math.atan2(0.05, 0.2)
# operator's left (+X, facing -Y): steering wheel with spinner knob;  right (-X): travel/lift joystick + buttons
st = empty("steer", (0.345, PF + 0.1, CZ + 0.065), lift, rot=(tilt, 0, 0))
cyl("st_hub", 0.03, 0.03, (0, 0, 0.0), "plastic", parent=st, bevel=0.006)
tube("st_rim", [(0.075 * math.cos(a * math.pi / 12), 0.075 * math.sin(a * math.pi / 12), 0.022) for a in range(24)], 0.011, "vinyl", parent=st, closed=True, resolution=2)
for a in (0, 120, 240):
    box("st_spoke", (0.012, 0.075, 0.008), (0.037 * math.sin(R(a)), 0.037 * math.cos(R(a)), 0.02), "plastic", 0.003, st, rot=(0, 0, -R(a)))
cyl("st_knob", 0.014, 0.04, (0.07, 0.0, 0.05), "plastic", parent=st, bevel=0.005)
jo = empty("joy", (-0.345, PF + 0.1, CZ + 0.055), lift, rot=(tilt, 0, 0))
cyl("joy_boot", 0.032, 0.025, (0, 0, 0.012), "rubber", radius2=0.018, parent=jo)
cyl("joy_st", 0.01, 0.07, (0, 0, 0.05), "steel", parent=jo)
box("joy_knob", (0.042, 0.038, 0.055), (0, 0, 0.1), "vinyl", 0.014, jo)
cyl("estop2_b", 0.026, 0.008, (-0.07, 0.07, 0.022), "hazard", parent=jo)
cyl("estop2", 0.02, 0.025, (-0.07, 0.07, 0.032), "accent", parent=jo, bevel=0.005)
for i in range(3):
    box("btn", (0.022, 0.022, 0.01), (0.06, -0.03 + i * 0.035, 0.012), "decal" if i else "hazard", 0.003, jo)
box("disp", (0.15, 0.025, 0.1), (0.07, 0.085, 0.07), "plastic", 0.01, st, rot=(R(55), 0, 0))
box("disp_s", (0.12, 0.004, 0.075), (0.07, 0.078, 0.079), "glass", 0, st, rot=(R(55), 0, 0))

# ---- fixed forks on the front of the platform, pallet clamp at the heel
TZ = 0.06
box("fork_car", (2 * PW - 0.06, 0.05, 0.25), (0, PF - 0.02, TZ + 0.12), "chassis", 0.01, lift)
box("fork_bar", (0.74, 0.03, 0.05), (0, PF - 0.052, TZ + 0.19), "mast", 0.006, lift)
for sx in (-1, 1):
    fork_tine("tine", (sx * 0.21, PF - 0.04, TZ), lift, length=1.2, height=0.245, width=0.1)
    box("tine_hook", (0.115, 0.05, 0.04), (sx * 0.21, PF - 0.06, TZ + 0.235), "steel", 0.006, lift)
# pallet clamp: a sprung jaw that grips the pallet's centre block
box("clamp_body", (0.26, 0.07, 0.11), (0, PF - 0.075, TZ + 0.16), "paint", 0.014, lift)
box("clamp_jaw", (0.2, 0.13, 0.022), (0, PF - 0.15, TZ + 0.105), "steel", 0.005, lift)
box("clamp_pad", (0.2, 0.03, 0.03), (0, PF - 0.2, TZ + 0.1), "hazard", 0.006, lift)
box("clamp_pedal", (0.12, 0.08, 0.015), (0.0, PF + 0.07, FZ + 0.02), "accent", 0.005, lift, rot=(R(-12), 0, 0))

# pallet (1.0 wide, 1.2 long) part-picked: three cartons so far
PY = PF - 0.1 - 0.6
pal = pallet("pal", (0, PY, TZ - 0.055), lift, load=False, rot=(0, 0, R(90)))
DZ = 0.144
cart = [((0.44, 0.56, 0.36), (-0.25, 0.0, 0.18), "card"), ((0.44, 0.56, 0.36), (0.22, -0.02, 0.18), "card2"),
        ((0.5, 0.42, 0.3), (-0.2, 0.02, 0.51), "card2")]
for i, (s, l, m) in enumerate(cart):
    # pallet is turned 90 deg: local x = world y. build in a world-aligned helper empty instead
    pass
cz = empty("cartons", (0, PY, TZ - 0.055 + DZ), lift)
for i, (s, l, m) in enumerate(cart):
    box("carton", s, l, m, 0.008, cz, segments=2)
    box("carton_tape", (0.06, s[1] + 0.002, 0.003), (l[0], l[1], l[2] + s[2] / 2), "tape", 0, cz)

# ================================================================ chains (scaled so they stay connected)
PZ = MT - 0.1
CA, RA = 1.42, 1.9           # carriage anchor (local to lift), outer-mast anchor
for sx in (-1, 1):
    cf = chain("chain_f", 1.0, (sx * 0.245, MY - 0.07, CA), lift, width=0.035)
    key(cf, FRAME_REST, scale=(1, 1, PZ - CA)); key(cf, FRAME_WORK, scale=(1, 1, max(0.02, PZ + INN - CA - LIFT)))
    cr = chain("chain_r", 1.0, (sx * 0.245, MY + 0.05, RA), None, width=0.035)
    key(cr, FRAME_REST, scale=(1, 1, PZ - RA)); key(cr, FRAME_WORK, scale=(1, 1, PZ + INN - RA))
box("chain_anchor", (0.6, 0.03, 0.045), (0, MY + 0.06, RA), "mast", 0.006)
box("chain_lug", (0.56, 0.05, 0.045), (0, MY - 0.085, CA), "chassis", 0.006, lift)

# cable from the carriage down to the chassis, hung in a loop that stays put at the mast foot
rtube("car_cable", [(0.1, MY - 0.09, 0.5), (0.1, MY - 0.09, 0.34), (0.1, MY - 0.02, 0.3)], 0.012, "rubber", lift, bend=0.03)
box("car_jbox", (0.14, 0.05, 0.1), (0.1, MY - 0.1, 0.55), "plastic", 0.012, lift)
# ================================================================ motion
key(lift, FRAME_REST, loc=(0, 0, 0)); key(lift, FRAME_WORK, loc=(0, 0, LIFT))
key(inn, FRAME_REST, loc=(0, 0, 0)); key(inn, FRAME_WORK, loc=(0, 0, INN))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "picker_high.glb"))
