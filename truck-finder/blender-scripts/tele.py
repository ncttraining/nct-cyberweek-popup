import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import *
reset()
R = math.radians

# ---------------------------------------------------------------- layout
WR, WW = 0.58, 0.40            # wheel radius / width
AX_F, AX_R = -1.4, 1.4         # axle Y
TRK = 0.95                     # wheel centre X
BX = -0.15                     # boom centre line (slightly to the right of centre; cab is on the left = +X)
CX, CWID = 0.57, 0.86          # cab centre X and width
PIV = (2.0, 1.56)              # boom pivot (y, z)
TH_REST, TH_WORK = 8.0, -39.0  # boom angle (deg about X): +8 = nose down at rest, raised 47 deg
EXT = 1.3                      # telescope stroke
HEAD = (-4.30, -0.36)          # carriage pivot in boom-local (y, z), on the inner section


def th(f):
    return lerp(TH_REST, TH_WORK, f / FRAME_WORK)


def boom_pt(p, f, inner=False):
    y, z = p
    if inner:
        y -= EXT * f / FRAME_WORK
    y, z = rot2((y, z), th(f))
    return (PIV[0] + y, PIV[1] + z)


# ---------------------------------------------------------------- wheels, axles, mudguards
for nm, sx, ay in (("wfl", 1, AX_F), ("wfr", -1, AX_F), ("wrl", 1, AX_R), ("wrr", -1, AX_R)):
    wheel(nm, WR, WW, (sx * TRK, ay, WR), rim="rim", tread=True)
    # mudguard: curved band plus a flat inner valance
    arch(nm + "_mg", WR + 0.09, WR + 0.125, 12, 168, WW + 0.08, (sx * TRK, ay, WR), "plastic", bevel=0.012)
    profile(nm + "_mgv", arc_pts(0, 0, WR + 0.125, 20, 160, 14) + [(-0.45, 0.42), (0.45, 0.42)], 0.03,
            (sx * (TRK - WW / 2 - 0.035), ay, WR), "plastic", bevel=0.008)
    cyl(nm + "_hubred", 0.2, 0.1, (sx * (TRK - WW / 2 - 0.05), ay, WR), "chassis", axis='X', bevel=0.01)
for ay in (AX_F, AX_R):
    cyl("axle", 0.095, 2 * TRK - WW, (0, ay, WR), "chassis", axis='X', bevel=0.01)
    box("axle_beam", (1.3, 0.2, 0.2), (0, ay, WR), "chassis", bevel=0.04)
    cyl("diff", 0.21, 0.36, (BX + 0.15, ay, WR), "chassis", axis='Y', bevel=0.05)
    box("axle_mount", (0.9, 0.36, 0.22), (0, ay, WR + 0.16), "chassis", bevel=0.03)
# prop shaft
cyl("propshaft", 0.045, 2.5, (0, 0, WR - 0.02), "steel", axis='Y')

# ---------------------------------------------------------------- chassis
# belly frame
profile("frame", [(-2.02, 0.50), (-1.95, 0.40), (2.2, 0.40), (2.35, 0.55), (2.35, 0.66), (-2.02, 0.66)], 1.16, (0, 0, 0), "chassis", bevel=0.02)
# side rails either side of the boom well
RAIL_R = (-0.58, BX - 0.21)     # x range right rail
RAIL_L = (BX + 0.21, 0.58)
for nm, (x0, x1) in (("rail_r", RAIL_R), ("rail_l", RAIL_L)):
    profile(nm, [(-2.02, 0.62), (2.3, 0.62), (2.3, 1.22), (1.15, 1.22), (0.8, 0.95), (-1.75, 0.95), (-2.02, 0.80)],
            x1 - x0, ((x0 + x1) / 2, 0, 0), "paint", bevel=0.025)
# front cross member / nose plate with tow eye and lamps
box("front_xm", (1.16, 0.10, 0.34), (0, -2.02, 0.60), "chassis", bevel=0.02)
for sx in (-1, 1):
    cyl("headlamp", 0.07, 0.05, (sx * 0.47, -2.075, 0.72), "lamp", axis='Y', bevel=0.008)
    cyl("headlamp_bz", 0.085, 0.04, (sx * 0.47, -2.06, 0.72), "plastic", axis='Y', bevel=0.008)

# rear body: pivot towers, counterweight
for sx in (-1, 1):
    profile("tower", [(1.2, 0.95), (2.32, 0.95), (2.30, 1.52)] + arc_pts(PIV[0], PIV[1], 0.26, 0, 150, 10) + [(1.45, 1.22)], 0.06,
            (BX + sx * 0.20, 0, 0), "paint", bevel=0.012)
    cyl("piv_boss", 0.12, 0.05, (BX + sx * 0.245, PIV[0], PIV[1]), "steel", axis='X', bevel=0.008)
cyl("piv_pin", 0.06, 0.56, (BX, PIV[0], PIV[1]), "steel", axis='X', bevel=0.006)
cw = profile("counterweight", [(2.22, 0.42)] + arc_pts(2.36, 0.56, 0.12, 270, 360, 6) + arc_pts(2.33, 1.12, 0.15, 0, 90, 6) + [(2.22, 1.27)],
             1.46, (0, 0, 0), "paint", bevel=0.04)
box("cw_stripe", (1.30, 0.012, 0.09), (0, 2.483, 0.62), "hazard", bevel=0)
for i in range(9):
    box("cw_chev", (0.05, 0.014, 0.09), (-0.56 + i * 0.14, 2.484, 0.62), "chassis", bevel=0, rot=(0, R(35), 0))
for sx in (-1, 1):
    box("tail", (0.16, 0.03, 0.09), (sx * 0.55, 2.485, 1.05), "tail", bevel=0.008)
    box("tail_amb", (0.07, 0.03, 0.09), (sx * 0.42, 2.485, 1.05), "beacon", bevel=0.008)
box("hitch", (0.16, 0.16, 0.12), (0, 2.5, 0.52), "chassis", bevel=0.02)
cyl("hitch_pin", 0.022, 0.2, (0, 2.54, 0.55), "steel")
box("plate", (0.26, 0.01, 0.08), (0.0, 2.484, 0.88), "decal", bevel=0)
# rear deck covers either side of the towers
box("deck_r", (0.36, 1.0, 0.05), (-0.56, 1.75, 1.235), "plastic", bevel=0.012)
box("deck_l", (0.50, 1.0, 0.05), (0.33, 1.75, 1.235), "plastic", bevel=0.012)

# ---------------------------------------------------------------- engine cover (right side, -X)
EXc, EW = -0.685, 0.60
hood = profile("hood", [(-0.74, 0.52), (0.76, 0.52), (0.76, 1.22)] + arc_pts(0.62, 1.22, 0.14, 0, 90, 6) + arc_pts(-0.50, 1.14, 0.22, 90, 165, 8) + [(-0.74, 0.95)],
               EW, (EXc, 0, 0), "paint", bevel=0.05)
# side grille with slats
box("grille_bg", (0.02, 0.62, 0.36), (EXc - EW / 2 - 0.004, 0.30, 0.98), "plastic", bevel=0.01)
for i in range(7):
    box("slat", (0.03, 0.58, 0.022), (EXc - EW / 2 - 0.012, 0.30, 0.84 + i * 0.047), "chassis", bevel=0.004, segments=1)
box("hood_seam", (EW + 0.012, 0.012, 0.6), (EXc, -0.08, 0.95), "chassis", bevel=0)
box("hood_handle", (0.03, 0.12, 0.03), (EXc - EW / 2 - 0.01, -0.3, 1.1), "chassis", bevel=0.008)
box("eng_skirt", (EW - 0.04, 1.44, 0.14), (EXc, 0.01, 0.47), "chassis", bevel=0.03)
box("data_plate", (0.006, 0.16, 0.1), (EXc - EW / 2 - 0.002, -0.42, 0.72), "decal", bevel=0)
box("hood_stripe", (0.006, 1.3, 0.04), (EXc - EW / 2 - 0.002, 0.0, 0.6), "accent", bevel=0)
# exhaust stack and air intake
cyl("exhaust", 0.045, 0.75, (EXc - 0.1, 0.55, 1.68), "mast")
cyl("exhaust_muff", 0.07, 0.3, (EXc - 0.1, 0.55, 1.5), "mast", bevel=0.02)
tube("exhaust_tip", [(EXc - 0.1, 0.55, 2.0), (EXc - 0.1, 0.55, 2.1), (EXc - 0.1, 0.62, 2.15)], 0.04, "mast")
cyl("intake", 0.06, 0.3, (EXc + 0.12, 0.2, 1.45), "plastic", bevel=0.01)
cyl("intake_cap", 0.085, 0.08, (EXc + 0.12, 0.2, 1.62), "plastic", bevel=0.02)

# ---------------------------------------------------------------- cab (left side, +X)
cab_x0, cab_x1 = CX - CWID / 2, CX + CWID / 2
YF, YB = -0.74, 0.72           # cab front / back at floor
# floor pan + lower body shell
profile("cab_tub", [(YF, 0.50), (YB, 0.50), (YB, 1.22), (0.30, 1.22), (0.30, 1.02), (-0.72, 1.02), (YF - 0.02, 0.92)],
        CWID, (CX, 0, 0), "paint", bevel=0.035)
box("cab_floor", (CWID - 0.06, 1.0, 0.03), (CX, -0.2, 1.03), "rubber", bevel=0.005)
box("tank", (0.2, 0.9, 0.34), (cab_x1 + 0.0, 0.0, 0.50), "plastic", bevel=0.04)       # fuel tank / step box under door
box("step", (0.24, 0.42, 0.035), (cab_x1 + 0.06, -0.3, 0.42), "steel", bevel=0.006)
for sx in (-0.19, 0.19):
    bar3d("step_hang", (cab_x1 + 0.06, -0.3 + sx, 0.42), (cab_x1 + 0.02, -0.3 + sx, 0.62), 0.03, 0.02, "chassis")
# ROPS frame
ZR = 2.34                      # underside of roof
A_TOP, A_BOT = (-0.52, ZR), (YF, 1.0)
P = 0.07
for x in (cab_x0 + P / 2, cab_x1 - P / 2):
    bar3d("pillar_a", (x, A_BOT[0], A_BOT[1]), (x, A_TOP[0], A_TOP[1]), P, P, "mast", bevel=0.015, extend=0.02)
    bar3d("pillar_b", (x, 0.30, 1.02), (x, 0.30, ZR), P, 0.06, "mast", bevel=0.015)
    bar3d("pillar_c", (x, YB - P / 2, 1.2), (x, YB - P / 2, ZR), P, P, "mast", bevel=0.015)
    bar3d("sill", (x, A_BOT[0], 1.02), (x, 0.3, 1.02), P, 0.05, "mast", bevel=0.012)
bar3d("hdr_f", (cab_x0, A_TOP[0], ZR - 0.02), (cab_x1, A_TOP[0], ZR - 0.02), P, 0.06, "mast", bevel=0.015)
bar3d("sill_f", (cab_x0, A_BOT[0], A_BOT[1]), (cab_x1, A_BOT[0], A_BOT[1]), P, 0.06, "mast", bevel=0.015)
bar3d("hdr_r", (cab_x0, YB - P / 2, ZR - 0.02), (cab_x1, YB - P / 2, ZR - 0.02), P, 0.06, "mast", bevel=0.015)
# roof with overhang and FOPS bars
profile("roof", [(-0.66, ZR), (YB + 0.05, ZR), (YB + 0.05, ZR + 0.07), (-0.45, ZR + 0.09), (-0.66, ZR + 0.05)], CWID + 0.06, (CX, 0, 0), "paint", bevel=0.03)
for i in range(5):
    box("fops", (CWID - 0.1, 0.03, 0.02), (CX, -0.3 + i * 0.2, ZR + 0.09), "mast", bevel=0.005, segments=1)
# glazing
gl = 0.012
bar3d("glass_f", (CX, A_BOT[0] + 0.005, A_BOT[1] + 0.02), (CX, A_TOP[0] + 0.005, A_TOP[1] - 0.03), CWID - 0.1, gl, "glass", bevel=0)
for x in (cab_x0 + 0.03, cab_x1 - 0.03):
    profile("glass_s", [(A_BOT[0] + 0.05, 1.05), (0.27, 1.05), (0.27, ZR - 0.04), (A_TOP[0] + 0.05, ZR - 0.04)], gl, (x, 0, 0), "glass", bevel=0)
    profile("glass_s2", [(0.33, 1.25), (YB - P, 1.25), (YB - P, ZR - 0.04), (0.33, ZR - 0.04)], gl, (x, 0, 0), "glass", bevel=0)
box("glass_r", (CWID - 0.12, gl, ZR - 1.28), (CX, YB - 0.03, (ZR + 1.24) / 2), "glass", bevel=0)
# door details on the outer side
box("door_handle", (0.025, 0.14, 0.035), (cab_x1 + 0.005, 0.16, 1.12), "chassis", bevel=0.008)
tube("grab", [(cab_x1 + 0.01, 0.34, 1.3), (cab_x1 + 0.06, 0.34, 1.36), (cab_x1 + 0.06, 0.34, 1.84), (cab_x1 + 0.01, 0.34, 1.9)], 0.014, "mast")
box("wiper", (0.5, 0.015, 0.015), (CX - 0.05, -0.685, 1.3), "rubber", bevel=0, rot=(R(-10), R(25), 0))
# interior
box("seat_base", (0.46, 0.46, 0.12), (CX, 0.25, 1.2), "vinyl", bevel=0.04)
box("seat_ped", (0.3, 0.3, 0.14), (CX, 0.27, 1.1), "plastic", bevel=0.02)
box("seat_back", (0.44, 0.12, 0.58), (CX, 0.5, 1.52), "vinyl", bevel=0.05, rot=(R(-10), 0, 0))
box("headrest", (0.26, 0.09, 0.16), (CX, 0.57, 1.88), "vinyl", bevel=0.035, rot=(R(-10), 0, 0))
box("dash", (CWID - 0.12, 0.2, 0.3), (CX, -0.6, 1.14), "plastic", bevel=0.04, rot=(R(-20), 0, 0))
rod3d("steer_col", (CX, -0.52, 1.2), (CX, -0.3, 1.5), 0.028, "plastic")
ring("steer_wheel", 0.17, 0.016, (CX, -0.29, 1.51), "vinyl", rot=(R(-36), 0, 0))
cyl("steer_hub", 0.04, 0.03, (CX, -0.29, 1.51), "plastic", rot=(R(-36), 0, 0))
box("joy_base", (0.12, 0.3, 0.1), (cab_x0 + 0.13, 0.12, 1.32), "plastic", bevel=0.02)
rod3d("joystick", (cab_x0 + 0.13, 0.02, 1.36), (cab_x0 + 0.13, 0.0, 1.5), 0.014, "chassis")
cyl("joy_knob", 0.028, 0.07, (cab_x0 + 0.13, 0.0, 1.52), "vinyl", bevel=0.012)
# lights, beacon, mirrors
for x in (cab_x0 + 0.14, cab_x1 - 0.14):
    box("worklight", (0.13, 0.07, 0.1), (x, -0.63, ZR + 0.125), "plastic", bevel=0.015)
    box("worklight_l", (0.1, 0.012, 0.07), (x, -0.668, ZR + 0.125), "lamp", bevel=0.004)
box("worklight_rr", (0.13, 0.07, 0.1), (CX, YB + 0.02, ZR + 0.125), "plastic", bevel=0.015)
box("worklight_rl", (0.1, 0.012, 0.07), (CX, YB + 0.058, ZR + 0.125), "lamp", bevel=0.004)
cyl("beacon_base", 0.055, 0.03, (CX + 0.2, 0.35, ZR + 0.1), "plastic")
cyl("beacon", 0.045, 0.1, (CX + 0.2, 0.35, ZR + 0.16), "beacon", bevel=0.015)
tube("mirror_arm", [(cab_x1 - 0.02, -0.6, 1.9), (cab_x1 + 0.2, -0.72, 1.95), (cab_x1 + 0.2, -0.72, 1.82)], 0.012, "mast")
box("mirror", (0.14, 0.03, 0.24), (cab_x1 + 0.2, -0.72, 1.72), "plastic", bevel=0.012)
tube("mirror_arm_r", [(EXc - 0.2, -0.62, 1.0), (EXc - 0.34, -0.7, 1.3), (EXc - 0.34, -0.7, 1.6)], 0.012, "mast")
box("mirror_r", (0.14, 0.03, 0.24), (EXc - 0.34, -0.7, 1.7), "plastic", bevel=0.012)

# ---------------------------------------------------------------- boom
boom = empty("boom", (BX, PIV[0], PIV[1]))
key(boom, FRAME_REST, rot=(R(TH_REST), 0, 0))
key(boom, FRAME_WORK, rot=(R(TH_WORK), 0, 0))
OW, OH = 0.30, 0.40
OUT_END = -3.55
profile("boom_outer", arc_pts(0, 0, OH / 2, 90, -90, 8) + [(OUT_END, -OH / 2), (OUT_END, OH / 2)], OW, (0, 0, 0), "paint", bevel=0.02, parent=boom)
box("boom_collar", (OW + 0.05, 0.16, OH + 0.05), (0, OUT_END + 0.08, 0), "paint", bevel=0.015, parent=boom)
for sx in (-1, 1):
    box("wear_pad", (0.03, 0.1, 0.12), (sx * (OW / 2 + 0.03), OUT_END + 0.08, 0), "steel", bevel=0.006, parent=boom)
    box("boom_rib", (0.012, 3.0, 0.05), (sx * (OW / 2 + 0.004), -1.75, 0), "paint", bevel=0.004, parent=boom, segments=1)
# ram lugs under the boom
RAM_B = (-2.0, -OH / 2 - 0.07)
for sx in (-1, 1):
    profile("ram_lug", [(-2.2, -OH / 2 + 0.02), (-1.8, -OH / 2 + 0.02)] + arc_pts(RAM_B[0], RAM_B[1], 0.07, 0, -180, 8), 0.03, (sx * 0.09, 0, 0), "paint", bevel=0.006, parent=boom)
# hoses along the top to the nose
tube("boom_hose", [(-0.09, 0.25, 0.05), (-0.09, 0.0, 0.225), (-0.09, -3.3, 0.225)], 0.018, "rubber", parent=boom)
tube("boom_hose2", [(-0.04, 0.25, 0.05), (-0.04, 0.0, 0.225), (-0.04, -3.3, 0.225)], 0.018, "rubber", parent=boom)
box("boom_decal", (0.004, 0.5, 0.1), (-OW / 2 - 0.002, -2.6, 0), "hazard", bevel=0, parent=boom)
box("boom_decal2", (0.004, 0.5, 0.1), (OW / 2 + 0.002, -2.6, 0), "hazard", bevel=0, parent=boom)

inner = empty("boom_inner", (0, 0, 0), boom)
key(inner, FRAME_REST, loc=(0, 0, 0))
key(inner, FRAME_WORK, loc=(0, -EXT, 0))
IW, IH = 0.23, 0.31
box("inner_sec", (IW, 3.5, IH), (0, -2.3, 0), "chassis", bevel=0.015, parent=inner)       # y -0.55 .. -4.05
# boom head: goose-neck down to the carriage pivot
hp = HEAD
profile("boom_head", [(-3.9, IH / 2 + 0.02), (-4.12, IH / 2 + 0.02)] + arc_pts(-4.12, IH / 2 - 0.2, 0.22, 90, 180, 6)
        + arc_pts(hp[0], hp[1], 0.13, 180, 340, 10) + [(-3.9, -IH / 2 - 0.02)], IW + 0.06, (0, 0, 0), "paint", bevel=0.02, parent=inner)
cyl("head_pin", 0.045, 0.62, (0, hp[0], hp[1]), "steel", axis='X', bevel=0.006, parent=inner)

# ---------------------------------------------------------------- fork carriage (stays level)
car = empty("carriage", (0, hp[0], hp[1]), inner)
key(car, FRAME_REST, rot=(R(-TH_REST), 0, 0))
key(car, FRAME_WORK, rot=(R(-TH_WORK), 0, 0))
CWD = 1.25
ZB, ZT = -0.44, 0.46           # carriage frame bottom / top relative to the pivot
YC = -0.20                     # carriage face
for sx in (-1, 1):
    # hinge plates from the pivot pin to the carriage frame
    profile("car_lug", arc_pts(0, 0, 0.10, -20, 60, 6) + arc_pts(-0.07, 0.40, 0.06, 0, 180, 6) + [(YC + 0.02, ZT - 0.08), (YC + 0.02, ZB + 0.08)], 0.035, (sx * 0.20, 0, 0), "chassis", bevel=0.008, parent=car)
    box("car_side", (0.06, 0.07, ZT - ZB), (sx * (CWD / 2 - 0.03), YC, (ZT + ZB) / 2), "chassis", bevel=0.012, parent=car)
box("car_top", (CWD, 0.07, 0.11), (0, YC, ZT - 0.05), "chassis", bevel=0.012, parent=car)
box("car_bot", (CWD, 0.07, 0.11), (0, YC, ZB + 0.055), "chassis", bevel=0.012, parent=car)
box("car_mid", (CWD, 0.05, 0.07), (0, YC + 0.01, 0.02), "chassis", bevel=0.01, parent=car)
# load backrest
BT = ZT + 0.62
tube("backrest", [(-CWD / 2 + 0.03, YC, ZT - 0.02), (-CWD / 2 + 0.03, YC, BT), (CWD / 2 - 0.03, YC, BT), (CWD / 2 - 0.03, YC, ZT - 0.02)], 0.022, "chassis", parent=car)
for i in range(5):
    x = -0.4 + i * 0.2
    box("br_bar", (0.03, 0.025, BT - ZT), (x, YC, (BT + ZT) / 2), "chassis", bevel=0.006, parent=car, segments=1)
# forks
FZ = ZB - 0.07
for sx in (-1, 1):
    fork_tine("tine", (sx * 0.30, YC - 0.035, FZ), car, length=1.15, height=ZT - FZ, width=0.12)
pallet("pal", (0, YC - 0.035 - 0.07 - 0.5, FZ + 0.047), car)

# ---------------------------------------------------------------- boom lift ram (keyed every frame, pinned both ends)
RAM_A = (1.25, 0.74)
for sx in (-1, 1):
    profile("ram_mount", [(1.05, 0.64), (1.45, 0.64)] + arc_pts(RAM_A[0], RAM_A[1], 0.08, 0, 180, 8), 0.03, (BX + sx * 0.09, 0, 0), "chassis", bevel=0.006)
hyd_ram("lift_ram", BX, lambda f: RAM_A, lambda f: boom_pt(RAM_B, f), 0.075, 1.06, 0.04, 1.14)

# ---------------------------------------------------------------- carriage crowd (tilt) rams either side of the boom head
CR_A = (-3.98, 0.10)           # on the head (boom-local)
CR_K = (-0.07, 0.40)           # on the carriage hinge plates (carriage-local, level)


def crowd_b(f):
    k = rot2(CR_K, -th(f))
    return (hp[0] + k[0], hp[1] + k[1])


for sx in (-1, 1):
    cyl("crowd_boss", 0.04, 0.08, (sx * 0.17, CR_A[0], CR_A[1]), "steel", axis='X', bevel=0.005, parent=inner)
    hyd_ram("crowd_ram%d" % sx, sx * 0.20, lambda f: CR_A, crowd_b, 0.04, 0.33, 0.022, 0.37, parent=inner)

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "tele.glb"))
