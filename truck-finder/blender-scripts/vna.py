import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from wh_common import *
reset()
R = math.radians
W = 0.65
LIFT = 3.9

# ================= chassis =================
# rear frame slab under battery + drive unit
slab = [(-W, 0.08), (W, 0.08)] + arc_pts(W - 0.15, 1.30, 0.15, 0, 90, 6) + arc_pts(-W + 0.15, 1.30, 0.15, 90, 180, 6)
profile("slab", slab, 0.2, (0, 0, 0.2), "chassis", bevel=0.02, plane='XY')
band = [(-W - 0.012, 0.9), (W + 0.012, 0.9)] + arc_pts(W - 0.15, 1.30, 0.162, 0, 90, 6) + arc_pts(-W + 0.15, 1.30, 0.162, 90, 180, 6)
profile("bumper", band, 0.1, (0, 0, 0.2), "rubber", bevel=0.015, plane='XY')
for i in range(8):
    profile("haz", [(0, 0), (0.055, 0), (0.095, 0.075), (0.04, 0.075)], 0.008, (-0.46 + i * 0.11, 1.462, 0.163), "hazard", bevel=0, plane='XZ')
# front legs with load wheels
for sx in (-1, 1):
    x = sx * 0.55
    box("leg", (0.2, 1.25, 0.22), (x, -0.12, 0.17), "chassis", 0.02)
    profile("leg_gus", [(0.0, 0.0), (-0.4, 0.0), (0.0, 0.16)], 0.2, (x, 0.1, 0.27), "chassis", bevel=0.01)
    nose = [(0.0, 0.065), (0.0, 0.28), (-0.13, 0.28)] + arc_pts(-0.17, 0.16, 0.12, 100, 255, 12)
    for o in (-0.088, 0.088):
        profile("leg_fork", nose, 0.024, (x + o, -0.73, 0), "chassis", bevel=0.006)
    box("leg_cap", (0.2, 0.22, 0.02), (x, -0.82, 0.272), "chassis", 0.006)
    wheel("load_w", 0.15, 0.14, (x, -0.90, 0.15), rim="rim")
    cyl("load_ax", 0.022, 0.21, (x, -0.90, 0.15), "steel", axis='X', bevel=0.004)
    box("leg_tip", (0.204, 0.05, 0.1), (x, -0.70, 0.215), "hazard", 0.004)
    # side guide rollers (rail guidance) on brackets, front and rear
    for yy, zz in ((-0.55, 0.13), (1.22, 0.2)):
        box("gr_brk", (0.12, 0.1, 0.03), (sx * (W + 0.02), yy, zz + 0.045), "chassis", 0.006)
        cyl("gr", 0.065, 0.05, (sx * (W + 0.055), yy, zz), "rubber", bevel=0.01)
        cyl("gr_c", 0.03, 0.056, (sx * (W + 0.055), yy, zz), "rim", bevel=0.004)
box("leg_x", (1.1, 0.4, 0.14), (0, 0.27, 0.19), "chassis", 0.02)          # cross frame under the mast
wheel("drive", 0.2, 0.15, (0.0, 1.12, 0.2), rim="rim")
box("drive_fork", (0.24, 0.24, 0.1), (0, 1.12, 0.26), "chassis", 0.02)

# battery compartment
box("batt", (2 * W, 0.6, 0.86), (0, 0.74, 0.55), "paint", 0.03)
box("batt_lid", (2 * W - 0.08, 0.5, 0.03), (0, 0.74, 0.985), "plastic", 0.012)
for xx in (-0.3, 0.3):
    box("lid_grip", (0.16, 0.03, 0.025), (xx, 0.6, 1.005), "chassis", 0.008)
for sx in (-1, 1):
    box("batt_door", (0.02, 0.5, 0.62), (sx * (W + 0.002), 0.74, 0.56), "paint", 0.012)
    box("batt_handle", (0.02, 0.16, 0.035), (sx * (W + 0.012), 0.74, 0.78), "chassis", 0.008)
    box("batt_latch", (0.02, 0.04, 0.04), (sx * (W + 0.012), 0.93, 0.4), "accent", 0.006)
    for k in range(5):
        box("batt_vent", (0.02, 0.3, 0.012), (sx * (W + 0.006), 0.74, 0.36 + k * 0.035), "chassis", 0.002, segments=1)
box("plate", (0.012, 0.12, 0.08), (W + 0.004, 0.56, 0.86), "decal", 0.002)
# drive / hydraulic unit hood with rounded rear
hood = [(1.03, 0.12), (1.03, 1.12)] + arc_pts(1.27, 0.94, 0.18, 90, 0, 8) + [(1.45, 0.12)]
profile("hood", hood, 2 * W, (0, 0, 0), "paint", bevel=0.04, segments=4)
box("hood_cover", (0.8, 0.02, 0.5), (0, 1.452, 0.6), "paint", 0.012)
for k in range(6):
    box("hood_vent", (0.5, 0.02, 0.014), (0, 1.46, 0.46 + k * 0.04), "chassis", 0.002, segments=1)
box("hood_grip", (0.24, 0.03, 0.03), (0, 1.462, 0.8), "chassis", 0.008)
for sx in (-1, 1):
    box("tail", (0.07, 0.02, 0.12), (sx * 0.54, 1.455, 0.82), "tail", 0.006)
    box("hood_side", (0.02, 0.3, 0.5), (sx * (W + 0.002), 1.21, 0.58), "paint", 0.012)
cyl("estop", 0.03, 0.03, (0.45, 1.2, 1.13), "accent", bevel=0.006)
cyl("estop_b", 0.04, 0.012, (0.45, 1.2, 1.122), "hazard")
beacon("beacon_r", (-0.45, 1.25, 1.135))
cyl("tow", 0.02, 0.1, (0, 1.49, 0.3), "steel")
box("tow_b", (0.12, 0.08, 0.02), (0, 1.47, 0.34), "chassis", 0.004); box("tow_b", (0.12, 0.08, 0.02), (0, 1.47, 0.26), "chassis", 0.004)

# ================= mast =================
MY, MT = 0.27, 4.5
box("mast_base", (1.0, 0.36, 0.1), (0, MY, 0.3), "chassis", 0.015)
inn = empty("mast_inner", (0, 0, 0))
for sx in (-1, 1):
    channel("m_out", 0.12, 0.24, 0.02, MT - 0.3, (sx * 0.36, MY, 0.3 + (MT - 0.3) / 2), "mast", open_dir=-sx)
    channel("m_inn", 0.085, 0.16, 0.016, MT - 0.45, (sx * 0.255, MY, 0.4 + (MT - 0.45) / 2), "mast", inn, open_dir=-sx)
    profile("m_gus", [(0.0, 0.0), (0.3, 0.0), (0.0, 0.6)], 0.03, (sx * 0.44, MY + 0.12, 0.33), "chassis", bevel=0.006)
    cyl("lift_cyl", 0.045, 2.9, (sx * 0.36, MY + 0.175, 1.8), "chassis", bevel=0.005)
    cyl("lift_cap", 0.052, 0.05, (sx * 0.36, MY + 0.175, 3.25), "steel", bevel=0.005)
    cyl("lift_rod", 0.03, 1.3, (sx * 0.36, MY + 0.175, 2.66), "chrome", parent=inn)
    box("lift_lug", (0.16, 0.2, 0.05), (sx * 0.31, MY + 0.1, 3.32), "mast", 0.008, inn)
    cyl("top_pul", 0.07, 0.04, (sx * 0.255, MY - 0.02, MT - 0.03), "steel", axis='X', parent=inn, bevel=0.005)
    rtube("stay", [(sx * 0.36, MY + 0.12, 2.5), (sx * 0.5, 1.3, 1.1)], 0.028, "mast")
    cyl("stay_ft", 0.05, 0.03, (sx * 0.5, 1.3, 1.125), "mast", bevel=0.006)
    rtube("hose", [(sx * 0.44, MY + 0.05, 0.5), (sx * 0.44, MY + 0.05, 3.9), (sx * 0.44, MY - 0.05, 4.05), (sx * 0.44, MY - 0.13, 3.9)], 0.013, "rubber", bend=0.06)
    for k in range(3):
        profile("m_haz", [(0, 0), (0.04, 0), (0.08, 0.07), (0.04, 0.07)], 0.004, (sx * 0.36 - 0.06 + k * 0.04, MY - 0.121, 2.9), "hazard" if k != 1 else "chassis", bevel=0, plane='XZ')
for z in (0.55, 1.5, 2.5, 3.5, 4.4):
    box("out_x", (0.84, 0.02, 0.14), (0, MY + 0.125, z), "mast", 0.004)
box("inn_x", (0.6, 0.03, 0.1), (0, MY + 0.07, MT - 0.12), "mast", 0.006, inn)
box("inn_x", (0.6, 0.03, 0.1), (0, MY + 0.07, 0.6), "mast", 0.006, inn)
box("inn_x", (0.6, 0.03, 0.1), (0, MY + 0.07, 2.5), "mast", 0.006, inn)
cyl("top_ax", 0.02, 0.56, (0, MY - 0.02, MT - 0.03), "steel", axis='X', parent=inn)

# ================= lifting cab + turret =================
lift = empty("lift", (0, 0, 0))
FZ = 0.39    # cab floor surface
CF, CR = -0.80, 0.05   # cab front / rear
# carriage on the mast
box("cab_car", (0.46, 0.05, 1.5), (0, MY - 0.15, 1.1), "chassis", 0.01, lift)
for sx in (-1, 1):
    box("car_side", (0.03, 0.2, 1.4), (sx * 0.2, MY - 0.07, 1.1), "chassis", 0.006, lift)
    for zz in (0.5, 1.1, 1.7):
        cyl("car_roll", 0.05, 0.035, (sx * 0.228, MY, zz), "steel", axis='X', parent=lift, bevel=0.005)
    box("fl_arm", (0.1, 0.92, 0.08), (sx * 0.3, -0.36, 0.3), "chassis", 0.012, lift)
    pass
box("floor", (1.2, CR - CF, 0.06), (0, (CR + CF) / 2, FZ - 0.03), "chassis", 0.012, lift)
box("mat", (1.1, CR - CF - 0.08, 0.01), (0, (CR + CF) / 2, FZ + 0.004), "rubber", 0.003, lift)
# cab back wall (towards the mast), lower skirts
box("back", (1.2, 0.06, 0.9), (0, CR + 0.02, FZ + 0.45), "paint", 0.02, lift)
box("back_pad", (0.5, 0.03, 0.4), (0, CR - 0.02, FZ + 0.62), "plastic", 0.012, lift)
for sx in (-1, 1):
    side = [(CR + 0.05, -0.03), (CF - 0.02, -0.03), (CF - 0.02, 0.23), (CF + 0.2, 0.23)] + arc_pts(CF + 0.2, 0.53, 0.3, 270, 330, 6) + arc_pts(CR - 0.12, 0.6, 0.3, 150, 90, 6) + [(CR + 0.05, 0.9)]
    profile("skirt", side, 0.04, (sx * 0.6, 0, FZ), "paint", bevel=0.012, parent=lift)
    box("skirt_tr", (0.045, CR - CF - 0.1, 0.03), (sx * 0.6, (CR + CF) / 2, FZ + 0.0), "hazard", 0.004, lift)
box("skirt_f", (1.2, 0.04, 0.26), (0, CF + 0.0, FZ + 0.1), "paint", 0.012, lift)
box("front_glass", (1.1, 0.008, 0.5), (0, CF + 0.0, FZ + 0.48), "glass", 0, lift)
# posts + overhead guard
GZ = FZ + 2.25
for sx in (-1, 1):
    x = sx * 0.575
    rtube("post", [(x, CF + 0.03, FZ), (x, CF + 0.03, GZ), (x, CR + 0.02, GZ), (x, CR + 0.02, FZ + 0.9)], 0.026, "mast", lift, bend=0.12)
    # side gate bars (yellow), hinged at the rear post
    rtube("gate", [(x, CR + 0.0, FZ + 1.08), (x, CF + 0.1, FZ + 1.08), (x, CF + 0.1, FZ + 0.72), (x, CR + 0.0, FZ + 0.72)], 0.018, "hazard", lift, bend=0.06)
    cyl("gate_h", 0.03, 0.5, (x, CR + 0.01, FZ + 0.9), "chassis", parent=lift, bevel=0.005)
    lamp("wl", (sx * 0.42, CF + 0.06, GZ - 0.08), lift)
    lamp("spot", (sx * 0.5, CF + 0.02, FZ + 0.33), lift, r=0.03)
for k in range(8):
    box("roof_bar", (1.15, 0.016, 0.045), (0, CF + 0.12 + k * 0.095, GZ), "mast", 0.004, lift, segments=1)
box("roof_rail", (0.02, 0.8, 0.04), (0, (CR + CF) / 2, GZ - 0.005), "mast", 0.004, lift, segments=1)
box("screen", (1.1, 0.006, 1.3), (0, CR + 0.02, FZ + 1.56), "glass", 0, lift)
box("front_rail", (1.15, 0.03, 0.04), (0, CF + 0.0, FZ + 0.74), "mast", 0.008, lift)
beacon("beacon", (0.4, CR - 0.1, GZ + 0.035), lift)
# seat on pedestal, armrest control pods
box("ped", (0.3, 0.26, 0.42), (0, -0.16, FZ + 0.21), "plastic", 0.03, lift)
seat("seat", (0, -0.2, FZ + 0.46), 0, lift, armrests=False)
for sx in (-1, 1):
    rtube("pod_arm", [(sx * 0.2, -0.1, FZ + 0.45), (sx * 0.36, -0.1, FZ + 0.5), (sx * 0.36, -0.2, FZ + 0.68)], 0.02, "chassis", lift, bend=0.05)
    box("pod", (0.15, 0.4, 0.07), (sx * 0.36, -0.36, FZ + 0.71), "plastic", 0.025, lift)
    box("pod_pad", (0.1, 0.2, 0.03), (sx * 0.36, -0.27, FZ + 0.755), "vinyl", 0.012, lift)
# right pod (-X is the operator's right): joystick; left pod: steering knob wheel
cyl("joy_boot", 0.035, 0.03, (-0.36, -0.48, FZ + 0.76), "rubber", radius2=0.02, parent=lift)
cyl("joy", 0.011, 0.08, (-0.36, -0.48, FZ + 0.81), "steel", parent=lift)
box("joy_knob", (0.045, 0.04, 0.06), (-0.36, -0.48, FZ + 0.86), "vinyl", 0.015, lift)
cyl("st_disc", 0.065, 0.014, (0.36, -0.47, FZ + 0.765), "vinyl", parent=lift, bevel=0.005)
cyl("st_knob", 0.018, 0.05, (0.40, -0.47, FZ + 0.795), "plastic", parent=lift, bevel=0.006)
cyl("estop2", 0.02, 0.025, (0.36, -0.2, FZ + 0.76), "accent", parent=lift, bevel=0.005)
box("disp", (0.2, 0.03, 0.14), (-0.44, CF + 0.08, FZ + 1.25), "plastic", 0.012, lift, rot=(R(15), 0, R(20)))
box("disp_s", (0.16, 0.004, 0.1), (-0.434, CF + 0.097, FZ + 1.25), "glass", 0, lift, rot=(R(15), 0, R(20)))
rtube("disp_arm", [(-0.575, CF + 0.03, FZ + 1.2), (-0.5, CF + 0.05, FZ + 1.22)], 0.012, "chassis", lift)
box("deadman", (0.26, 0.12, 0.02), (0.0, -0.55, FZ + 0.02), "chassis", 0.006, lift, rot=(R(8), 0, 0))

# ---- turret head: traverse frame in front of the cab ----
BY = -0.90
box("beam", (1.26, 0.16, 0.18), (0, BY, 0.40), "chassis", 0.015, lift)
box("beam_rack", (1.2, 0.03, 0.02), (0, BY - 0.05, 0.495), "steel", 0.003, lift)
box("rail_up", (1.26, 0.09, 0.08), (0, BY, FZ + 0.86), "chassis", 0.012, lift)
for sx in (-1, 1):
    box("frame_post", (0.06, 0.12, 0.78), (sx * 0.6, BY, 0.86), "chassis", 0.01, lift)
    box("beam_brk", (0.12, 0.12, 0.1), (sx * 0.45, CF - 0.02, 0.36), "chassis", 0.01, lift)
PX, PY = -0.5, BY - 0.08 - 0.14
# traverse carriage (slides along the beam) carrying the pivot
box("trav", (0.3, 0.05, 1.0), (PX + 0.02, BY - 0.105, 0.82), "paint", 0.012, lift)
for zz in (0.36, FZ + 0.9):
    box("trav_lug", (0.18, 0.2, 0.06), (PX, PY + 0.06, zz), "chassis", 0.012, lift)
    for xx in (-0.1, 0.12):
        cyl("trav_roll", 0.035, 0.03, (PX + xx, BY - 0.07, zz + 0.09 if zz < 1 else zz - 0.09), "steel", axis='Y', parent=lift, bevel=0.004)
cyl("pivot_pin", 0.03, 1.0, (PX, PY, 0.83), "steel", parent=lift, bevel=0.004)
cyl("trav_motor", 0.06, 0.16, (PX + 0.08, BY - 0.02, FZ + 1.02), "plastic", parent=lift, bevel=0.012)

# rotating fork head
tur = empty("turret", (PX, PY, 0), lift)
cyl("piv_sleeve", 0.06, 0.74, (0, 0, 0.82), "mast", parent=tur, bevel=0.008)
for zz in (0.50, 1.14):
    box("arm", (0.86, 0.08, 0.09), (0.4, 0.0, zz), "mast", 0.012, tur)
profile("arm_web", [(0.0, 0.0), (0.3, 0.0), (0.0, 0.3)], 0.02, (0.06, 0, 0.545), "mast", bevel=0.004, parent=tur, plane='XZ')
profile("arm_web", [(0.0, 0.0), (0.3, 0.0), (0.0, -0.3)], 0.02, (0.06, 0, 1.095), "mast", bevel=0.004, parent=tur, plane='XZ')
FX = 0.5
for sx in (-1, 1):
    channel("aux", 0.06, 0.09, 0.012, 1.2, (FX + sx * 0.3, -0.07, 0.70), "mast", tur, open_dir=-sx)
    fork_tine("tine", (FX + sx * 0.27, -0.15, 0.06), tur, length=1.15, height=0.5, width=0.1)
    box("tine_hook", (0.11, 0.05, 0.05), (FX + sx * 0.27, -0.13, 0.585), "steel", 0.008, tur)
box("aux_top", (0.66, 0.06, 0.06), (FX, -0.07, 1.31), "mast", 0.01, tur)
box("aux_bot", (0.66, 0.06, 0.05), (FX, -0.07, 0.115), "mast", 0.01, tur)
cyl("aux_cyl", 0.03, 0.8, (FX, -0.06, 0.6), "chassis", parent=tur, bevel=0.004)
cyl("aux_rod", 0.018, 0.3, (FX, -0.06, 1.13), "chrome", parent=tur)
box("fc_top", (0.9, 0.04, 0.09), (FX, -0.13, 0.52), "mast", 0.008, tur)
box("fc_bot", (0.9, 0.04, 0.09), (FX, -0.13, 0.2), "mast", 0.008, tur)
box("fc_plate", (0.5, 0.02, 0.26), (FX, -0.125, 0.36), "mast", 0.004, tur)
e = empty("br", (FX, -0.13, 0), tur)
backrest("br", e, width=0.9, z0=0.57, z1=1.22)
pallet("pal", (FX, -0.72, 0.105), tur)

# chains: inner-stage pulley -> cab carriage (front) and -> outer mast anchor (rear); scaled to stay joined
PZ = MT - 0.03
for sx in (-1, 1):
    cf = chain("chain_f", 1.0, (sx * 0.255, MY - 0.09, 1.85), lift, width=0.04)
    key(cf, FRAME_REST, scale=(1, 1, PZ - 1.85)); key(cf, FRAME_WORK, scale=(1, 1, max(0.02, PZ + 2.0 - 1.85 - LIFT)))
    cr = chain("chain_r", 1.0, (sx * 0.255, MY + 0.05, 3.2), None, width=0.04)
    key(cr, FRAME_REST, scale=(1, 1, PZ - 3.2)); key(cr, FRAME_WORK, scale=(1, 1, PZ + 2.0 - 3.2))
box("chain_anchor", (0.62, 0.03, 0.05), (0, MY + 0.05, 3.2), "mast", 0.006)
box("chain_lug", (0.62, 0.04, 0.05), (0, MY - 0.1, 1.85), "chassis", 0.006, lift)

# ================= motion =================
key(lift, FRAME_REST, loc=(0, 0, 0)); key(lift, FRAME_WORK, loc=(0, 0, LIFT))
key(inn, FRAME_REST, loc=(0, 0, 0)); key(inn, FRAME_WORK, loc=(0, 0, 2.0))
key(tur, FRAME_REST, rot=(0, 0, 0)); key(tur, FRAME_WORK, rot=(0, 0, R(-90)))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "vna.glb"))
