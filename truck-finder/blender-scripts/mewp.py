import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import *
reset()
R = math.radians

# ---------------------------------------------------------------- scissor geometry
N = 4                    # crossed pairs per side
L = 2.0                  # arm length pin to pin
Z0 = 0.38                # height of the chassis pins
YR = 1.0                 # fixed (rear) pins; the front ends slide
S0 = 0.06                # sin(arm angle) stowed: each stage 0.10 m tall
RISE = 3.0
S1 = S0 + RISE / (N * L)
DECK = 0.10              # platform floor above the top pins
XO, XI = 0.335, 0.275    # outer (A) and inner (B) arm layers
AT, AD = 0.045, 0.105     # arm thickness / depth
HW = 0.55                # half width of the chassis
WR, WW = 0.2, 0.13


def sn(f):
    return lerp(S0, S1, f / FRAME_WORK)


def ang(f):
    return math.asin(sn(f))


def yc(f):
    return YR - L / 2 * math.cos(ang(f))


def zc(k, f):
    return Z0 + (k + 0.5) * L * sn(f)


def ztop(f):
    return Z0 + N * L * sn(f)


def on_b(k, y, f):
    """World (y, z) of a point y along inner arm B of stage k (+y = towards its rear-bottom end)."""
    a = ang(f)
    return (yc(f) + y * math.cos(a), zc(k, f) - y * math.sin(a))


# ================================================================ chassis
box("base", (0.80, 2.26, 0.2), (0, 0, 0.22), "chassis", bevel=0.02)
for sx in (-1, 1):
    box("well_wall", (0.035, 2.26, 0.36), (sx * 0.39, 0, 0.44), "chassis", bevel=0.008)
    # side tray (battery tray one side, hydraulic/ground-control tray the other)
    box("tray", (0.16, 1.28, 0.47), (sx * 0.475, 0, 0.385), "paint", bevel=0.03)
    box("tray_seam", (0.004, 0.01, 0.4), (sx * 0.556, 0.2, 0.385), "chassis", bevel=0)
    box("tray_handle", (0.02, 0.12, 0.03), (sx * 0.558, -0.2, 0.5), "chassis", bevel=0.006)
    box("tray_stripe", (0.004, 1.1, 0.035), (sx * 0.556, 0, 0.2), "accent", bevel=0)
    for yy in (-0.38, 0.38):
        box("fork_pocket", (0.006, 0.22, 0.08), (sx * 0.556, yy, 0.3), "rubber", bevel=0)
    # pothole guard under the tray
    box("pothole", (0.025, 1.2, 0.085), (sx * 0.52, 0, 0.095), "chassis", bevel=0.006)
    for yy in (-0.45, 0.45):
        box("pothole_arm", (0.03, 0.05, 0.08), (sx * 0.49, yy, 0.13), "steel", bevel=0.006)
    for sy in (-1, 1):
        wheel("wheel", WR, WW, (sx * 0.475, sy * 0.9, WR), rim="rim")
        # wheel housing over each wheel
        profile("housing", [(-0.25, 0.0), (0.25, 0.0), (0.25, 0.19), (-0.25, 0.19)], 0.16, (sx * 0.475, sy * 0.9, 0.43), "paint", bevel=0.03)
        cyl("stub", 0.045, 0.14, (sx * 0.40, sy * 0.9, WR), "chassis", axis='X')
        box("corner_hz", (0.006, 0.1, 0.17), (sx * 0.556, sy * 1.09, 0.525), "hazard", bevel=0)
for sy in (-1, 1):
    box("end_plate", (2 * HW, 0.05, 0.50), (0, sy * 1.14, 0.37), "paint", bevel=0.015)
    box("end_hz", (0.9, 0.006, 0.06), (0, sy * 1.166, 0.17), "hazard", bevel=0)
    for i in range(9):
        box("end_chev", (0.04, 0.008, 0.06), (-0.4 + i * 0.1, sy * 1.167, 0.17), "chassis", bevel=0, rot=(0, R(35), 0))
# ground control panel, charger socket, data plate, beacon
box("gcp", (0.012, 0.3, 0.2), (0.557, 0.42, 0.47), "plastic", bevel=0.005)
cyl("gcp_estop", 0.025, 0.03, (0.57, 0.5, 0.5), "tail", axis='X', bevel=0.008)
cyl("gcp_key", 0.012, 0.02, (0.567, 0.4, 0.5), "steel", axis='X')
box("gcp_disp", (0.004, 0.09, 0.04), (0.564, 0.4, 0.42), "glass", bevel=0)
box("data_plate", (0.004, 0.16, 0.1), (-0.556, 0.42, 0.47), "decal", bevel=0)
box("end_plate_decal", (0.2, 0.004, 0.07), (0.3, -1.166, 0.5), "decal", bevel=0)
cyl("beacon_base", 0.04, 0.02, (-0.475, -0.55, 0.63), "plastic")
cyl("beacon", 0.032, 0.06, (-0.475, -0.55, 0.665), "beacon", bevel=0.012)
# hydraulic power pack and tank visible in the well when the stack is raised
box("pump_tank", (0.3, 0.34, 0.14), (-0.1, -0.3, 0.36), "plastic", bevel=0.03)
cyl("pump_motor", 0.07, 0.26, (0.16, -0.3, 0.38), "chassis", axis='Y', bevel=0.015)
cyl("tank_cap", 0.03, 0.03, (-0.16, -0.36, 0.44), "hazard", bevel=0.006)
tube("pump_hose", [(0.16, -0.16, 0.38), (0.12, 0.0, 0.36), (0.05, 0.3, 0.36)], 0.012, "rubber")
# rear entry ladder
for sx in (-1, 1):
    bar3d("ladder_stile", (sx * 0.2, 1.24, 0.12), (sx * 0.2, 1.24, 0.66), 0.03, 0.03, "chassis", bevel=0.006)
    for zz in (0.18, 0.6):
        bar3d("ladder_stay", (sx * 0.2, 1.16, zz), (sx * 0.2, 1.24, zz), 0.03, 0.03, "chassis", bevel=0.006)
for zz in (0.22, 0.44, 0.64):
    box("rung", (0.4, 0.1, 0.022), (0, 1.235, zz), "steel", bevel=0.005)
# fixed rear pin and front slide channels for the bottom of the stack
cyl("pin_fix", 0.022, 0.74, (0, YR, Z0), "steel", axis='X')
for sx in (-1, 1):
    profile("pin_brkt", [(-0.09, -0.12), (0.09, -0.12)] + arc_pts(0, 0, 0.06, 0, 180, 8), 0.02, (sx * 0.235, YR, Z0), "chassis", bevel=0.004)
    for dz in (-0.062, 0.062):
        box("slide_ch", (0.05, 0.5, 0.016), (sx * 0.365, -0.86, Z0 + dz), "steel", bevel=0.004)

# ================================================================ scissor stack (every arm keyed on every frame)
arm_pts = arc_pts(-L / 2, 0, AD / 2, 90, 270, 6) + arc_pts(L / 2, 0, AD / 2, -90, 90, 6)   # rounded-end flat bar, (y, z)
A, B = [], []
for k in range(N):
    ea = empty("armA%d" % k, (0, 0, 0))
    eb = empty("armB%d" % k, (0, 0, 0))
    for sx in (-1, 1):
        profile("a_bar", arm_pts, AT, (sx * XO, 0, 0), "paint", bevel=0.006, parent=ea, segments=2)
        profile("b_bar", arm_pts, AT, (sx * XI, 0, 0), "paint", bevel=0.006, parent=eb, segments=2)
        # pins: centre and both ends, carried by the outer arm
        for yy in (-L / 2, 0, L / 2):
            cyl("pin", 0.02, 0.15, (sx * (XO + XI) / 2, yy, 0), "steel", axis='X', parent=ea, verts=16)
            cyl("pin_head", 0.032, 0.012, (sx * (XO + AT / 2 + 0.006), yy, 0), "steel", axis='X', parent=ea, verts=16)
        if k == 0:      # roller in the chassis slide channel
            cyl("slide_roller", 0.045, 0.04, (sx * 0.368, -L / 2, 0), "plastic", axis='X', parent=ea, bevel=0.006)
        if k == N - 1:  # roller in the platform slide channel
            cyl("pin_top", 0.02, 0.15, (sx * (XI - 0.03), -L / 2, 0), "steel", axis='X', parent=eb, verts=16)
            cyl("slide_roller_t", 0.045, 0.04, (sx * (XI - 0.045), -L / 2, 0), "plastic", axis='X', parent=eb, bevel=0.006)
    if k >= 2:
        cyl("xtube", 0.028, 2 * XI, (0, 0, 0), "chassis", axis='X', parent=eb, verts=16)
    A.append(ea); B.append(eb)
    for f in FRAMES:
        a = ang(f)
        key(ea, f, loc=(0, yc(f), zc(k, f)), rot=(a, 0, 0))      # front-bottom -> rear-top
        key(eb, f, loc=(0, yc(f), zc(k, f)), rot=(-a, 0, 0))     # rear-bottom -> front-top

# lift cylinder between cross tubes on the inner arms of stages 0 and 1
RAM0, RAM1 = 0.70, -0.50
for eb, yy in ((B[0], RAM0), (B[1], RAM1)):
    cyl("ram_xtube", 0.03, 2 * XI, (0, yy, 0), "chassis", axis='X', parent=eb, verts=16)
    for sx in (-1, 1):
        box("ram_lug", (0.02, 0.1, 0.1), (sx * 0.075, yy, 0), "chassis", bevel=0.01, parent=eb)
hyd_ram("lift_cyl", 0, lambda f: on_b(0, RAM0, f), lambda f: on_b(1, RAM1, f), 0.05, 0.98, 0.028, 1.05)

# ================================================================ platform
plat = empty("platform", (0, 0, ztop(0) + DECK))
for f in FRAMES:
    key(plat, f, loc=(0, 0, ztop(f) + DECK))
PW, PL = 0.52, 1.15            # half width / half length
box("deck", (2 * PW, 2 * PL, 0.06), (0, 0, -0.03), "chassis", bevel=0.01, parent=plat)
box("deck_plate", (2 * PW - 0.08, 2 * PL - 0.08, 0.006), (0, 0, 0.002), "steel", bevel=0, parent=plat)
for i in range(11):
    box("deck_rib", (2 * PW - 0.12, 0.012, 0.004), (0, -1.0 + i * 0.2, 0.006), "chassis", bevel=0, parent=plat, segments=1)
for sx in (-1, 1):
    box("underframe", (0.05, 2 * PL - 0.1, 0.11), (sx * 0.2, 0, -0.10), "chassis", bevel=0.008, parent=plat)
    # fixed pin bracket (rear) and slide channel (front) under the platform
    profile("top_brkt", [(-0.08, 0.06), (0.08, 0.06)] + arc_pts(0, 0, 0.05, 0, -180, 8), 0.02, (sx * (XO + 0.04), YR, -DECK), "chassis", bevel=0.004, parent=plat)
    for dz in (-0.062, 0.062):
        box("top_slide", (0.05, 0.5, 0.016), (sx * (XI - 0.045), -0.86, -DECK + dz), "steel", bevel=0.004, parent=plat)
for sy in (-1, 1):
    box("under_x", (0.46, 0.05, 0.11), (0, sy * 0.9, -0.10), "chassis", bevel=0.008, parent=plat)
cyl("top_pin_fix", 0.022, 2 * XO + 0.14, (0, YR, -DECK), "steel", axis='X', parent=plat)

# guard rails: square tube, top rail 1.1, mid rail 0.55, toe boards 0.15
T = 0.035
RX, RY = PW - T / 2, PL - T / 2
ZT, ZM = 1.1 - T / 2, 0.57
post_y = (-RY, -0.38, 0.38, RY)
for sx in (-1, 1):
    for py in post_y:
        bar3d("post", (sx * RX, py, 0), (sx * RX, py, ZT), T, T, "paint", bevel=0.006, parent=plat)
    for zz in (ZT, ZM):
        bar3d("side_rail", (sx * RX, -RY, zz), (sx * RX, RY, zz), T, T, "paint", bevel=0.006, parent=plat, extend=T / 2)
    box("toe_side", (0.012, 2 * PL, 0.15), (sx * (PW - 0.006), 0, 0.075), "paint", bevel=0.003, parent=plat)
for zz in (ZT, ZM):
    bar3d("front_rail", (-RX, -RY, zz), (RX, -RY, zz), T, T, "paint", bevel=0.006, parent=plat)
bar3d("front_post", (0, -RY, 0), (0, -RY, ZT), T, T, "paint", bevel=0.006, parent=plat)
box("toe_front", (2 * PW, 0.012, 0.15), (0, -PL + 0.006, 0.075), "paint", bevel=0.003, parent=plat)
# rear entry gate (swing gate between the rear corner posts)
G = 0.028
gx0, gx1 = -RX + 0.05, RX - 0.05
gy = RY
for zz in (ZT - 0.02, ZM, 0.2):
    bar3d("gate_rail", (gx0, gy, zz), (gx1, gy, zz), G, G, "mast", bevel=0.005, parent=plat)
for gx in (gx0, gx1):
    bar3d("gate_stile", (gx, gy, 0.2), (gx, gy, ZT - 0.02), G, G, "mast", bevel=0.005, parent=plat)
for zz in (0.35, 0.9):
    cyl("gate_hinge", 0.02, 0.09, (gx0 - 0.03, gy, zz), "chassis", parent=plat)
box("gate_latch", (0.07, 0.05, 0.09), (gx1 + 0.015, gy, 0.82), "accent", bevel=0.01, parent=plat)
box("toe_gate", (gx1 - gx0, 0.012, 0.15), ((gx0 + gx1) / 2, gy, 0.11), "steel", bevel=0.003, parent=plat)
box("rear_hz", (2 * PW, 0.006, 0.05), (0, PL + 0.002, -0.03), "hazard", bevel=0, parent=plat)
box("front_hz", (2 * PW, 0.006, 0.05), (0, -PL - 0.002, -0.03), "hazard", bevel=0, parent=plat)
# platform control box hung on the front rail, with joystick, e-stop and coiled cable
cbx, cby, cbz = 0.26, -RY + 0.10, ZT - 0.1
box("ctrl_box", (0.26, 0.15, 0.2), (cbx, cby, cbz), "plastic", bevel=0.02, parent=plat, rot=(R(-20), 0, 0))
box("ctrl_hook", (0.2, 0.08, 0.02), (cbx, cby - 0.07, ZT + 0.025), "steel", bevel=0.004, parent=plat)
box("ctrl_face", (0.22, 0.11, 0.008), (cbx, cby + 0.035, cbz + 0.098), "decal", bevel=0, parent=plat, rot=(R(-20), 0, 0))
rod3d("ctrl_joy", (cbx - 0.05, cby + 0.03, cbz + 0.1), (cbx - 0.05, cby + 0.07, cbz + 0.2), 0.012, "chassis", parent=plat)
cyl("ctrl_knob", 0.024, 0.06, (cbx - 0.05, cby + 0.078, cbz + 0.22), "vinyl", bevel=0.01, parent=plat, rot=(R(-20), 0, 0))
cyl("ctrl_estop", 0.026, 0.04, (cbx + 0.06, cby + 0.04, cbz + 0.12), "tail", bevel=0.01, parent=plat, rot=(R(-20), 0, 0))
tube("ctrl_guard", [(cbx - 0.12, cby + 0.09, cbz + 0.03), (cbx - 0.12, cby + 0.12, cbz + 0.2), (cbx + 0.12, cby + 0.12, cbz + 0.2), (cbx + 0.12, cby + 0.09, cbz + 0.03)], 0.008, "steel", parent=plat)
coil = []
for i in range(60):
    tt = i / 59
    coil.append((cbx + 0.1 + 0.025 * math.cos(i * 1.3), cby - 0.02 + 0.025 * math.sin(i * 1.3), cbz - 0.1 - tt * (cbz - 0.12)))
tube("ctrl_cable", coil, 0.006, "rubber", parent=plat, resolution=2)
# manual box and lanyard anchor points
box("manual_box", (0.05, 0.3, 0.22), (-RX + 0.045, -0.75, 0.75), "plastic", bevel=0.012, parent=plat)
for sx in (-1, 1):
    ring("anchor", 0.03, 0.007, (sx * (RX - 0.03), 0.38, 0.1), "hazard", axis='X', parent=plat, n=12)

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mewp.glb"))
