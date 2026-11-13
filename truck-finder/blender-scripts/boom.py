import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from tpmlib import *
reset()
R = math.radians

# ================================================================ linkage geometry (side view, (y, z); forward = -y)
WR, WW = 0.40, 0.30            # wheel radius / width
TRK, AXY = 0.95, 0.90          # wheel centre x, axle y
P1 = (-0.55, 1.15)             # riser lower-arm pivot on the turntable tower
DO = (-0.19, 0.282)            # offset lower-arm pin -> upper-arm pin (same on tower and on upright)
L1 = 1.90                      # riser arm length pin to pin
A0, A1 = 3.0, 40.0             # riser arm angle above horizontal (arms point rearward)
MO = (0.15, 0.58)              # main boom pivot M relative to the upright's lower pin U
B0, B1 = 0.0, 78.0             # main boom elevation
LB = 3.70                      # M -> boom tip pin J, retracted
EXT = 1.10                     # telescope stroke
HA = (-0.16, 0.06)             # jib upper-arm pin on the (level) jib head, relative to J
DJ = (0.142, -0.155)           # offset upper-arm pin -> lower-arm pin (same on head and on basket bracket)
LJ = 1.30                      # jib arm length
T0, T1 = 65.0, 40.0            # jib angle below horizontal
FLOOR = -0.40                  # basket floor relative to the basket bracket's upper pin Ka


def fr(f):
    return f / FRAME_WORK


def a_(f): return lerp(A0, A1, fr(f))
def b_(f): return lerp(B0, B1, fr(f))
def t_(f): return lerp(T0, T1, fr(f))
def ext(f): return lerp(0, EXT, fr(f))


def add(p, q):
    return (p[0] + q[0], p[1] + q[1])


def U(f):
    a = R(a_(f))
    return (P1[0] + L1 * math.cos(a), P1[1] + L1 * math.sin(a))


def up_pt(p, f):               # point fixed on the upright (relative to U)
    return add(U(f), p)


def M(f):
    return up_pt(MO, f)


def boom_pt(p, f, inner=False):  # p in boom-local (y, z): forward is -y, origin at M
    y, z = p
    if inner:
        y -= ext(f)
    return add(M(f), rot2((y, z), -b_(f)))


def J(f):
    return boom_pt((-LB, 0), f, True)


def head_pt(p, f):
    return add(J(f), p)


def Ha(f): return head_pt(HA, f)
def Hb(f): return head_pt(add(HA, DJ), f)


def jib_pt(s, off, f, lower=False):   # s along the arm from its head pin, off = perpendicular (up when level)
    base = Hb(f) if lower else Ha(f)
    return add(base, rot2((-s, off), t_(f)))


def Ka(f):
    return jib_pt(LJ, 0, f)


def low_arm_pt(s, off, f):
    return add(P1, rot2((s, off), a_(f)))


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def body(name, pos, ang=None):
    """An unparented pivot keyed in world space on every frame."""
    e = empty(name, (0, *pos(0)))
    for f in FRAMES:
        key(e, f, loc=(0, *pos(f)), rot=(R(ang(f)) if ang else 0, 0, 0))
    return e


# ram pin positions
RR_A = (1.20, 0.955)                                   # riser ram: turntable deck bracket
def RR_B(f): return low_arm_pt(0.90, -0.15, f)         #            lug under the lower arm
BR_C = (0.20, 0.03)                                    # boom lift rams: on the upright (rel. U)
BR_P = (-1.30, -0.10)                                  #                 on the boom side (boom-local)
LV_Q = (-LB + 0.60, -0.20)                             # level (slave) ram: under the inner section
LV_H = (0.05, -0.24)                                   #                    on the jib head (rel. J)
def JR_B(f): return jib_pt(0.85, 0, f)                 # jib ram: head lower pin Hb -> cross tube on the upper arms

for nm, A, B in (("riser ram", lambda f: RR_A, RR_B), ("boom ram", lambda f: up_pt(BR_C, f), lambda f: boom_pt(BR_P, f)),
                 ("level ram", lambda f: boom_pt(LV_Q, f, True), lambda f: head_pt(LV_H, f)), ("jib ram", Hb, JR_B)):
    ls = [dist(A(f), B(f)) for f in FRAMES]
    print("line GEOM %-10s len %.3f -> %.3f (min %.3f max %.3f)" % (nm, ls[0], ls[-1], min(ls), max(ls)))
for f in (0, 12, 24):
    k = Ka(f)
    print("line GEOM f%2d U=(%.2f,%.2f) M=(%.2f,%.2f) J=(%.2f,%.2f) Ka=(%.2f,%.2f) floor z=%.2f basket centre y=%.2f" %
          (f, *U(f), *M(f), *J(f), *k, k[1] + FLOOR, k[0] - 0.555))

# ================================================================ chassis
profile("chassis", [(-1.30, 0.42), (-1.18, 0.29), (1.18, 0.29), (1.30, 0.42), (1.30, 0.66), (1.24, 0.72), (-1.24, 0.72), (-1.30, 0.66)],
        1.24, (0, 0, 0), "paint", bevel=0.03)
box("belly", (1.0, 2.2, 0.08), (0, 0, 0.27), "chassis", bevel=0.02)
for sy in (-1, 1):
    ay = sy * AXY
    box("axle_beam", (1.62, 0.22, 0.20), (0, ay, WR), "chassis", bevel=0.04)
    cyl("axle", 0.07, 2 * TRK - WW + 0.04, (0, ay, WR), "chassis", axis='X')
    box("end_hz", (1.0, 0.008, 0.09), (0, sy * 1.303, 0.54), "hazard", bevel=0)
    for i in range(9):
        box("end_chev", (0.045, 0.01, 0.09), (-0.44 + i * 0.11, sy * 1.304, 0.54), "chassis", bevel=0, rot=(0, R(35), 0))
    for sx in (-1, 1):
        wheel("wheel", WR, WW, (sx * TRK, ay, WR), rim="rim", tread=True)
        box("knuckle", (0.10, 0.20, 0.30), (sx * 0.76, ay, WR), "chassis", bevel=0.03)
        cyl("hub_motor", 0.13, 0.12, (sx * 0.72, ay, WR), "chassis", axis='X', bevel=0.02)
        # tie-down / lifting lug on each corner
        profile("lug", [(-0.07, 0), (0.07, 0)] + arc_pts(0, 0.05, 0.07, 0, 180, 8), 0.03, (sx * 0.56, sy * 1.2, 0.71), "chassis", bevel=0.006)
        box("corner_decal", (0.006, 0.16, 0.10), (sx * 0.622, sy * 0.3, 0.56), "decal" if sy < 0 else "hazard", bevel=0)
    # steering tie rod and cylinder on the front axle, drive cover on the rear
    if sy < 0:
        cyl("tie_rod", 0.02, 1.5, (0, ay - 0.17, WR - 0.03), "steel", axis='X')
        cyl("steer_cyl", 0.04, 0.5, (0, ay - 0.17, WR - 0.03), "chassis", axis='X', bevel=0.008)
for sx in (-1, 1):
    box("side_stripe", (0.006, 1.5, 0.045), (sx * 0.622, 0, 0.36), "accent", bevel=0)
    box("fork_pocket", (0.01, 0.30, 0.10), (sx * 0.622, 0, 0.47), "rubber", bevel=0)
# slew ring
cyl("slew_base", 0.56, 0.04, (0, 0, 0.735), "chassis", bevel=0.008, verts=48)
cyl("slew_ring", 0.50, 0.08, (0, 0, 0.775), "steel", bevel=0.008, verts=48)
for i in range(24):
    an = i * math.pi / 12
    cyl("slew_bolt", 0.014, 0.02, (0.53 * math.cos(an), 0.53 * math.sin(an), 0.76), "steel", verts=6)

# ================================================================ turntable (no slew: faces forward)
TD = 0.80                      # deck underside
profile("tt_deck", [(-0.95, -0.80), (0.95, -0.80), (0.95, 1.30), (-0.95, 1.30)], 0.08, (0, 0, TD + 0.04), "chassis", bevel=0.02, plane='XY')
# side covers: +X engine cover, -X hydraulic / ground-control cover
CX0, CX1 = 0.40, 0.97
cov = [(-0.86, 0.86), (1.28, 0.86), (1.28, 1.50)] + arc_pts(-0.50, 1.24, 0.28, 90, 150, 8) + [(-0.86, 1.18)]
for sx in (-1, 1):
    xc = sx * (CX0 + CX1) / 2
    xo = sx * CX1
    profile("cover", cov, CX1 - CX0, (xc, 0, 0), "paint", bevel=0.05)
    box("cover_skirt", (CX1 - CX0 - 0.03, 2.1, 0.05), (xc, 0.21, 0.865), "chassis", bevel=0.01)
    box("cover_seam", (0.004, 0.012, 0.56), (xo + 0.001, 0.25, 1.19), "chassis", bevel=0)
    box("cover_seam2", (0.004, 0.012, 0.42), (xo + 0.001, -0.55, 1.10), "chassis", bevel=0)
    box("cover_handle", (0.025, 0.14, 0.03), (xo + 0.008, 0.02, 1.34), "chassis", bevel=0.008)
    box("cover_latch", (0.02, 0.05, 0.07), (xo + 0.006, 0.52, 1.0), "steel", bevel=0.006)
    box("cover_stripe", (0.006, 1.9, 0.04), (xo + 0.001, 0.2, 0.93), "accent", bevel=0)
    tube("cover_grab", [(sx * 0.5, -0.6, 1.5), (sx * 0.5, -0.6, 1.58), (sx * 0.86, -0.6, 1.58), (sx * 0.86, -0.6, 1.5)], 0.012, "mast")
    # top of the cover: lid seam, hinge line and a tread strip
    box("cover_topseam", (CX1 - CX0 - 0.08, 0.012, 0.004), (xc, 0.25, 1.501), "chassis", bevel=0)
    box("cover_hinge", (0.02, 1.5, 0.012), (sx * (CX0 + 0.06), 0.45, 1.503), "chassis", bevel=0.003)
    for i in range(6):
        box("cover_tread", (0.30, 0.03, 0.006), (xc + sx * 0.05, 0.50 + i * 0.09, 1.506), "chassis", bevel=0, segments=1)
# engine side: louvres, exhaust, filler
for i in range(7):
    box("louvre", (0.02, 0.58, 0.022), (CX1 + 0.004, 0.86, 1.08 + i * 0.047), "chassis", bevel=0.004, segments=1)
box("louvre_bg", (0.012, 0.64, 0.38), (CX1 + 0.001, 0.86, 1.22), "plastic", bevel=0.006)
cyl("exhaust", 0.035, 0.22, (0.78, 1.0, 1.60), "mast")
cyl("exhaust_cap", 0.045, 0.03, (0.78, 1.0, 1.70), "mast", bevel=0.008)
cyl("fuel_cap", 0.04, 0.03, (0.62, -0.2, 1.515), "hazard", bevel=0.008)
# ground control side: panel with e-stop, key switch, display, toggle row
GX = -CX1
box("gcp", (0.03, 0.46, 0.30), (GX - 0.012, 0.75, 1.24), "plastic", bevel=0.01)
box("gcp_face", (0.006, 0.40, 0.24), (GX - 0.029, 0.75, 1.24), "chassis", bevel=0)
cyl("gcp_estop", 0.032, 0.04, (GX - 0.045, 0.60, 1.31), "tail", axis='X', bevel=0.01)
cyl("gcp_key", 0.016, 0.03, (GX - 0.04, 0.70, 1.31), "steel", axis='X')
box("gcp_disp", (0.006, 0.13, 0.07), (GX - 0.033, 0.84, 1.30), "glass", bevel=0)
for i in range(6):
    cyl("gcp_tog", 0.008, 0.035, (GX - 0.04, 0.59 + i * 0.065, 1.18), "steel", axis='X', verts=8)
box("gcp_plate", (0.006, 0.20, 0.12), (GX - 0.001, 0.0, 1.22), "decal", bevel=0)
box("hyd_tank_gauge", (0.006, 0.03, 0.16), (GX - 0.001, -0.3, 1.12), "glass", bevel=0)
cyl("beacon_base", 0.05, 0.03, (-0.7, 1.05, 1.515), "plastic")
cyl("beacon", 0.04, 0.09, (-0.7, 1.05, 1.57), "beacon", bevel=0.014)
# counterweight: a U-shaped casting wrapped round the tail, open at the front for the stowed upright
SL = 0.34                      # half width of the slot
cw = ([(-0.97, 1.28), (-SL, 1.28), (-SL, 1.70)] + [(SL, 1.70), (SL, 1.28), (0.97, 1.28)]
      + arc_pts(0.72, 1.70, 0.25, 0, 90, 8) + arc_pts(-0.72, 1.70, 0.25, 90, 180, 8))
profile("counterweight", cw, 0.66, (0, 0, TD + 0.33), "paint", bevel=0.09, plane='XY', segments=5)
box("cw_groove", (1.5, 0.012, 0.02), (0, 1.951, 1.16), "chassis", bevel=0)
box("cw_hitch", (0.18, 0.12, 0.10), (0, 1.97, 0.90), "chassis", bevel=0.02)
cyl("cw_hitch_pin", 0.02, 0.16, (0, 2.0, 0.92), "steel")
box("cw_floor", (2 * SL + 0.1, 0.5, 0.10), (0, 1.5, TD + 0.05), "chassis", bevel=0.02)
box("cw_stripe", (1.30, 0.012, 0.09), (0, 1.951, 0.98), "hazard", bevel=0)
for i in range(11):
    box("cw_chev", (0.05, 0.014, 0.09), (-0.6 + i * 0.12, 1.952, 0.98), "chassis", bevel=0, rot=(0, R(35), 0))
for sx in (-1, 1):
    box("tail_lamp", (0.14, 0.03, 0.08), (sx * 0.5, 1.952, 1.30), "tail", bevel=0.008)
    cyl("cw_lift_eye", 0.035, 0.03, (sx * 0.6, 1.6, 1.47), "steel", bevel=0.006)
box("cw_plate", (0.24, 0.01, 0.08), (0, 1.952, 1.30), "decal", bevel=0)
# riser tower: two plates carrying the lower pins of both riser arms
P1U = add(P1, DO)
TX = 0.165
tower = [(-1.0, 0.86), (-0.20, 0.86)] + arc_pts(P1[0], P1[1], 0.11, -30, 60, 6) + arc_pts(P1U[0], P1U[1], 0.11, 20, 170, 8) + [(-1.0, 1.0)]
for sx in (-1, 1):
    profile("tower", tower, 0.03, (sx * TX, 0, 0), "paint", bevel=0.008)
    for p in (P1, P1U):
        cyl("tower_boss", 0.06, 0.03, (sx * (TX + 0.02), *p), "steel", axis='X', bevel=0.006)
box("tower_web", (2 * TX, 0.04, 0.40), (0, -0.93, 1.02), "paint", bevel=0.008, rot=(R(-12), 0, 0))
for p in (P1, P1U):
    cyl("tower_pin", 0.035, 2 * TX + 0.1, (0, *p), "steel", axis='X')
# riser ram bracket on the deck
for sx in (-1, 1):
    profile("rr_brkt", [(-0.12, 0.87), (0.12, 0.87)] + arc_pts(0, RR_A[1], 0.07, 0, 180, 8), 0.025, (sx * 0.085, RR_A[0], 0), "chassis", bevel=0.005)
cyl("rr_pin", 0.025, 0.22, (0, *RR_A), "steel", axis='X')
# hydraulic hoses from the deck up the tower
for x in (-0.05, 0.05):
    tube("tt_hose", [(x, 0.4, 0.89), (x, -0.3, 0.90), (x, -0.62, 1.0), (x, -0.70, 1.25)], 0.014, "rubber")

# ================================================================ riser: two parallel arms + upright
AW, AH = 0.26, 0.17
for nm, piv in (("riser_lower", P1), ("riser_upper", P1U)):
    e = body(nm, lambda f, piv=piv: piv, a_)
    profile(nm + "_arm", arc_pts(0, 0, AH / 2, 90, 270, 6) + arc_pts(L1, 0, AH / 2, -90, 90, 6), AW, (0, 0, 0), "paint", bevel=0.012, parent=e)
    for sx in (-1, 1):
        box(nm + "_rib", (0.008, L1 - 0.5, 0.04), (sx * (AW / 2 + 0.003), L1 / 2, 0), "paint", bevel=0.003, parent=e, segments=1)
    if nm == "riser_lower":
        for sx in (-1, 1):
            profile("rr_lug", [(0.74, -AH / 2 + 0.02), (1.06, -AH / 2 + 0.02)] + arc_pts(0.90, -0.15, 0.06, 0, -180, 8), 0.025, (sx * 0.085, 0, 0), "paint", bevel=0.005, parent=e)
        cyl("rr_lug_pin", 0.022, 0.22, (0, 0.90, -0.15), "steel", axis='X', parent=e)
        tube("riser_hose", [(-0.06, 0.15, AH / 2 + 0.012), (-0.06, L1 - 0.15, AH / 2 + 0.012)], 0.013, "rubber", parent=e)
        tube("riser_hose2", [(-0.03, 0.15, AH / 2 + 0.012), (-0.03, L1 - 0.15, AH / 2 + 0.012)], 0.013, "rubber", parent=e)
    else:
        box("riser_decal", (AW + 0.004, 0.4, 0.08), (0, 1.2, 0), "hazard", bevel=0, parent=e)

upr = body("upright", U)
uo = [(-0.11, -0.06)] + arc_pts(0.0, 0.0, 0.11, 200, 300, 5) + [(0.30, -0.09), (0.34, 0.50)] + arc_pts(MO[0], MO[1], 0.17, -10, 120, 8) + arc_pts(DO[0], DO[1], 0.11, 100, 200, 6)
for sx in (-1, 1):
    profile("upright_plate", uo, 0.03, (sx * TX, 0, 0), "paint", bevel=0.008, parent=upr)
    for p in ((0, 0), DO):
        cyl("upr_boss", 0.06, 0.03, (sx * (TX + 0.02), *p), "steel", axis='X', bevel=0.006, parent=upr)
    cyl("upr_boss_m", 0.085, 0.035, (sx * (TX + 0.022), *MO), "steel", axis='X', bevel=0.008, parent=upr)
for p in ((0, 0), DO):
    cyl("upr_pin", 0.035, 2 * TX + 0.1, (0, *p), "steel", axis='X', parent=upr)
cyl("upr_pin_m", 0.045, 2 * TX + 0.12, (0, *MO), "steel", axis='X', parent=upr)
cyl("upr_pin_c", 0.03, 0.64, (0, *BR_C), "steel", axis='X', parent=upr)
box("upr_back", (2 * TX, 0.025, 0.42), (0, 0.325, 0.21), "paint", bevel=0.006, parent=upr, rot=(R(-4), 0, 0))

# ================================================================ main boom (base section + telescoping inner section)
BW, BH = 0.30, 0.34
BEND = -2.95
boom = body("boom", M, lambda f: -b_(f))
profile("boom_base", arc_pts(0.12, 0, BH / 2, 90, -90, 8) + [(BEND, -BH / 2), (BEND, BH / 2)], BW, (0, 0, 0), "paint", bevel=0.02, parent=boom)
box("boom_collar", (BW + 0.05, 0.16, BH + 0.05), (0, BEND + 0.08, 0), "paint", bevel=0.015, parent=boom)
for sx in (-1, 1):
    box("wear_pad", (0.03, 0.10, 0.12), (sx * (BW / 2 + 0.03), BEND + 0.08, 0), "steel", bevel=0.006, parent=boom)
    box("boom_rib", (0.010, 1.3, 0.05), (sx * (BW / 2 + 0.003), -2.15, 0), "paint", bevel=0.003, parent=boom, segments=1)
    box("boom_hz", (0.004, 0.5, 0.12), (sx * (BW / 2 + 0.010), -2.3, 0), "hazard", bevel=0, parent=boom)
    # lift-ram lug on each side
    cyl("br_boss", 0.07, 0.05, (sx * (BW / 2 + 0.02), *BR_P), "paint", axis='X', bevel=0.008, parent=boom)
    cyl("br_pinend", 0.03, 0.03, (sx * 0.31, *BR_P), "steel", axis='X', parent=boom)
cyl("br_pin", 0.028, 0.62, (0, *BR_P), "steel", axis='X', parent=boom)
# cable / hose track on top of the base section: a tray with a link chain lying in it
TRX = 0.0
box("track_tray", (0.17, 2.75, 0.015), (TRX, -1.50, BH / 2 + 0.008), "chassis", bevel=0.003, parent=boom)
for sx in (-1, 1):
    box("track_wall", (0.012, 2.75, 0.075), (TRX + sx * 0.085, -1.50, BH / 2 + 0.04), "chassis", bevel=0.003, parent=boom)
n_link = 30
for i in range(n_link):
    box("track_link", (0.13, 0.070, 0.05), (TRX, -0.25 - i * 0.085, BH / 2 + 0.045), "plastic", bevel=0.008, parent=boom, segments=1)
tube("track_feed", [(TRX, 0.27, -0.02), (TRX, 0.31, 0.08), (TRX, 0.22, BH / 2 + 0.03), (TRX, 0.0, BH / 2 + 0.05), (TRX, -0.25, BH / 2 + 0.05)], 0.028, "rubber", parent=boom)

inner = empty("boom_inner", (0, 0, 0), boom)
key(inner, FRAME_REST, loc=(0, 0, 0))
key(inner, FRAME_WORK, loc=(0, -EXT, 0))
IW, IH = 0.22, 0.26
box("inner_sec", (IW, 3.25, IH), (0, -2.02, 0), "chassis", bevel=0.012, parent=inner)        # y -0.40 .. -3.65
for sx in (-1, 1):
    profile("tip_fork", [(-3.45, IH / 2), (-3.45, -IH / 2), (-LB, -0.09)] + arc_pts(-LB, 0, 0.09, 270, 90, 8), 0.025, (sx * 0.1225, 0, 0), "paint", bevel=0.006, parent=inner)
    profile("lv_lug", [(LV_Q[0] - 0.12, -IH / 2 + 0.02), (LV_Q[0] + 0.12, -IH / 2 + 0.02)] + arc_pts(LV_Q[0], LV_Q[1], 0.05, 0, -180, 8), 0.02, (sx * 0.06, 0, 0), "chassis", bevel=0.004, parent=inner)
cyl("lv_lug_pin", 0.018, 0.16, (0, *LV_Q), "steel", axis='X', parent=inner)
# upper run of the cable track rides out with the inner section
box("track_arm", (0.13, 0.9, 0.03), (TRX, -3.05, IH / 2 + 0.035), "plastic", bevel=0.006, parent=inner)
box("track_post", (0.10, 0.05, 0.09), (TRX, -3.45, IH / 2 + 0.03), "chassis", bevel=0.006, parent=inner)
tube("tip_hose", [(0.04, -3.45, IH / 2 + 0.05), (0.04, -3.62, IH / 2 + 0.07), (0.04, -3.78, 0.14)], 0.014, "rubber", parent=inner)
tube("tip_hose2", [(-0.04, -3.45, IH / 2 + 0.05), (-0.04, -3.62, IH / 2 + 0.07), (-0.04, -3.78, 0.14)], 0.014, "rubber", parent=inner)

# ================================================================ jib head (kept level by the slave ram), jib parallelogram
HB = add(HA, DJ)
head = body("jib_head", J)
ho = arc_pts(HA[0], HA[1], 0.075, 60, 200, 6) + arc_pts(HB[0] - 0.03, HB[1], 0.06, 180, 250, 4) + arc_pts(LV_H[0], LV_H[1], 0.055, 200, 360, 6) + arc_pts(0.02, 0.0, 0.10, -30, 80, 6)
for sx in (-1, 1):
    profile("head_plate", ho, 0.022, (sx * 0.147, 0, 0), "paint", bevel=0.006, parent=head)
cyl("head_pin_j", 0.035, 0.36, (0, 0, 0), "steel", axis='X', parent=head)
for p in (HA, HB):
    cyl("head_pin", 0.022, 0.46, (0, *p), "steel", axis='X', parent=head)
cyl("head_pin_lv", 0.02, 0.32, (0, *LV_H), "steel", axis='X', parent=head)

JX = 0.195
for nm, piv in (("jib_upper", Ha), ("jib_lower", Hb)):
    e = body(nm, piv, t_)
    for sx in (-1, 1):
        profile(nm + "_arm", arc_pts(0, 0, 0.045, -90, 90, 6) + arc_pts(-LJ, 0, 0.045, 90, 270, 6), 0.05, (sx * JX, 0, 0), "paint", bevel=0.008, parent=e)
    if nm == "jib_upper":
        cyl("jib_xtube", 0.03, 2 * JX, (0, -0.85, 0), "paint", axis='X', parent=e)
        cyl("jib_xtube2", 0.022, 2 * JX, (0, -0.30, 0), "paint", axis='X', parent=e)
        tube("jib_hose", [(JX - 0.02, -0.08, 0.06), (JX - 0.02, -LJ + 0.1, 0.06)], 0.011, "rubber", parent=e)
        for yy in (-0.3, -0.9):
            box("jib_hose_clip", (0.05, 0.03, 0.02), (JX - 0.01, yy, 0.055), "steel", bevel=0.004, parent=e)
    else:
        cyl("jib_xtube3", 0.022, 2 * JX, (0, -1.0, 0), "paint", axis='X', parent=e)

# ================================================================ basket (always level)
bk = body("basket", Ka)
bo = arc_pts(0, 0, 0.07, 30, 180, 6) + arc_pts(DJ[0], DJ[1], 0.06, 150, 300, 6) + [(-0.02, -0.40), (-0.12, -0.40), (-0.12, 0.05)]
for sx in (-1, 1):
    profile("bk_plate", bo, 0.022, (sx * 0.147, 0, 0), "paint", bevel=0.006, parent=bk)
for p in ((0, 0), DJ):
    cyl("bk_pin", 0.022, 0.46, (0, *p), "steel", axis='X', parent=bk)
cyl("rotator", 0.085, 0.36, (0, -0.07, -0.20), "chassis", bevel=0.015, parent=bk)
cyl("rotator_cap", 0.06, 0.04, (0, -0.07, -0.01), "steel", bevel=0.008, parent=bk)
PWD, PD = 1.70, 0.75           # basket width / depth
YR_, YF_ = -0.18, -0.18 - PD   # rear (boom side) and front rails
YC_ = (YR_ + YF_) / 2
FZ = FLOOR
# support frame under the floor
for sx in (-1, 1):
    box("bk_beam", (0.06, PD + 0.06, 0.09), (sx * 0.22, YC_ + 0.03, FZ - 0.075), "chassis", bevel=0.01, parent=bk)
box("bk_xbeam", (0.56, 0.07, 0.09), (0, YR_ + 0.07, FZ - 0.075), "chassis", bevel=0.01, parent=bk)
box("bk_mount", (0.40, 0.10, 0.34), (0, YR_ + 0.045, FZ + 0.15), "chassis", bevel=0.012, parent=bk)
box("floor", (PWD, PD, 0.03), (0, YC_, FZ - 0.015), "chassis", bevel=0.006, parent=bk)
box("floor_plate", (PWD - 0.08, PD - 0.08, 0.006), (0, YC_, FZ + 0.002), "steel", bevel=0, parent=bk)
for i in range(12):
    box("floor_rib", (0.012, PD - 0.12, 0.004), (-0.77 + i * 0.14, YC_, FZ + 0.006), "chassis", bevel=0, parent=bk, segments=1)
T = 0.036
RXh = PWD / 2 - T / 2
yr, yf = YR_ - T / 2, YF_ + T / 2
ZT, ZM = FZ + 1.1 - T / 2, FZ + 0.56
GATE = (0.10, 0.70)            # gate opening along the rear rail on the +X side? no: gate is in the +X end rail
for sx in (-1, 1):
    for py in (yr, yf):
        bar3d("post", (sx * RXh, py, FZ), (sx * RXh, py, ZT), T, T, "paint", bevel=0.006, parent=bk)
    box("toe_side", (0.012, PD, 0.15), (sx * (PWD / 2 - 0.006), YC_, FZ + 0.075), "paint", bevel=0.003, parent=bk)
    bar3d("end_top", (sx * RXh, yr, ZT), (sx * RXh, yf, ZT), T, T, "paint", bevel=0.006, parent=bk)
# -X end: fixed mid rail; +X end: entry gate (swing gate, dark)
bar3d("end_mid", (-RXh, yr, ZM), (-RXh, yf, ZM), T, T, "paint", bevel=0.006, parent=bk)
G = 0.028
gy0, gy1 = yr - 0.05, yf + 0.05
for zz in (ZT - 0.10, ZM, FZ + 0.20):
    bar3d("gate_rail", (RXh, gy0, zz), (RXh, gy1, zz), G, G, "mast", bevel=0.005, parent=bk)
for gy in (gy0, gy1):
    bar3d("gate_stile", (RXh, gy, FZ + 0.20), (RXh, gy, ZT - 0.10), G, G, "mast", bevel=0.005, parent=bk)
for zz in (FZ + 0.35, FZ + 0.85):
    cyl("gate_hinge", 0.02, 0.09, (RXh, gy0 + 0.03, zz), "chassis", parent=bk)
box("gate_latch", (0.05, 0.07, 0.09), (RXh, gy1 - 0.015, FZ + 0.80), "accent", bevel=0.01, parent=bk)
for py, nm in ((yr, "rear"), (yf, "front")):
    for zz in (ZT, ZM):
        bar3d(nm + "_rail", (-RXh, py, zz), (RXh, py, zz), T, T, "paint", bevel=0.006, parent=bk, extend=T / 2)
    for px in (-0.42, 0.42):
        bar3d(nm + "_post", (px, py, FZ), (px, py, ZT), T, T, "paint", bevel=0.006, parent=bk)
    sgn = 1 if nm == "rear" else -1
    box("toe_" + nm, (PWD, 0.012, 0.15), (0, py + sgn * (T / 2 - 0.006), FZ + 0.075), "paint", bevel=0.003, parent=bk)
    box("hz_" + nm, (PWD, 0.006, 0.05), (0, py + sgn * (T / 2 + 0.002), FZ + 0.03), "hazard", bevel=0, parent=bk)
# platform control box on the boom-side rail, facing the operator
cbx, cby, cbz = -0.42, yr - 0.13, ZT - 0.02
tilt = R(20)
box("ctrl_box", (0.46, 0.20, 0.22), (cbx, cby, cbz - 0.02), "plastic", bevel=0.02, parent=bk, rot=(tilt, 0, 0))
box("ctrl_face", (0.40, 0.15, 0.008), (cbx, cby - 0.035, cbz + 0.088), "decal", bevel=0, parent=bk, rot=(tilt, 0, 0))
for dx in (-0.12, 0.02):
    rod3d("ctrl_joy", (cbx + dx, cby - 0.03, cbz + 0.09), (cbx + dx, cby - 0.06, cbz + 0.19), 0.012, "chassis", parent=bk)
    cyl("ctrl_knob", 0.024, 0.06, (cbx + dx, cby - 0.066, cbz + 0.21), "vinyl", bevel=0.01, parent=bk, rot=(tilt, 0, 0))
cyl("ctrl_estop", 0.028, 0.04, (cbx + 0.15, cby - 0.035, cbz + 0.10), "tail", bevel=0.01, parent=bk, rot=(tilt, 0, 0))
tube("ctrl_guard", [(cbx - 0.21, cby - 0.10, cbz + 0.04), (cbx - 0.21, cby - 0.14, cbz + 0.22), (cbx + 0.21, cby - 0.14, cbz + 0.22), (cbx + 0.21, cby - 0.10, cbz + 0.04)], 0.008, "steel", parent=bk)
for dx in (-0.15, 0.15):
    box("ctrl_brkt", (0.03, 0.14, 0.03), (cbx + dx, cby + 0.08, ZT - 0.02), "steel", bevel=0.005, parent=bk)
tube("ctrl_cable", [(cbx + 0.1, cby + 0.05, cbz - 0.12), (cbx + 0.2, cby + 0.08, FZ + 0.5), (cbx + 0.3, yr - 0.03, FZ + 0.25), (cbx + 0.34, yr - 0.02, FZ + 0.02)], 0.012, "rubber", parent=bk)
# foot switch, manual box, lanyard anchors
box("foot_sw", (0.20, 0.26, 0.05), (cbx, cby - 0.22, FZ + 0.03), "plastic", bevel=0.012, parent=bk)
box("foot_pedal", (0.12, 0.16, 0.02), (cbx, cby - 0.23, FZ + 0.065), "accent", bevel=0.006, parent=bk, rot=(R(8), 0, 0))
box("manual_box", (0.30, 0.05, 0.22), (0.42, yf + 0.045, FZ + 0.75), "plastic", bevel=0.012, parent=bk)
for px in (-0.2, 0.62):
    ring("anchor", 0.03, 0.007, (px, yr - 0.03, FZ + 0.62), "hazard", axis='Y', parent=bk, n=12)

# ================================================================ hydraulic rams (keyed every frame, pinned both ends)
hyd_ram("riser_ram", 0, lambda f: RR_A, RR_B, 0.05, 0.66, 0.028, 0.72, barrel_mat="chassis")
for sx in (-1, 1):
    hyd_ram("boom_ram%d" % sx, sx * 0.255, lambda f: up_pt(BR_C, f), lambda f: boom_pt(BR_P, f), 0.05, 1.12, 0.028, 1.20)
hyd_ram("level_ram", 0, lambda f: boom_pt(LV_Q, f, True), lambda f: head_pt(LV_H, f), 0.032, 0.27, 0.018, 0.30)
hyd_ram("jib_ram", 0, Hb, JR_B, 0.038, 0.60, 0.022, 0.62)

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "boom.glb"))
