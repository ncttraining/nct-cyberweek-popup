import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from cb_common import *
reset()

DZ = 0.12                     # rear chassis sits this much higher than the counterbalance (front wheels tuck under the floor)
YS = -0.10
PY = -0.62                    # pivot axis, chassis-local Y
RFW, RRW = 0.25, 0.27         # front / rear tyre radii
SWING = math.radians(75)

ch = empty("chassis", (0, YS, DZ))

# ---- rear chassis: frame, gooseneck floor, step
box("frame", (0.66, 1.25, 0.40), (0, 0.63, 0.30), "chassis", bevel=0.03, parent=ch)
fl = [(-0.30, -0.55), (0.30, -0.55), (0.57, -0.15), (0.57, 0.22), (-0.57, 0.22), (-0.57, -0.15)]
profile("floor", fl, 0.09, (0, 0, 0.455), "paint", bevel=0.02, parent=ch, plane='XY')
mat_ = [(-0.24, -0.33), (0.24, -0.33), (0.50, -0.12), (0.50, 0.19), (-0.50, 0.19), (-0.50, -0.12)]
profile("floor_mat", mat_, 0.012, (0, 0, 0.503), "rubber", bevel=0.003, parent=ch, plane='XY', segments=1)
for sx in (-1, 1):
    # raised kick lip along the chamfered nose of the floor, tying the cowl to the floor corners
    profile("floor_lip", [(sx * 0.27, -0.55), (sx * 0.30, -0.55), (sx * 0.57, -0.15), (sx * 0.57, -0.08), (sx * 0.54, -0.08), (sx * 0.54, -0.14)],
            0.13, (0, 0, 0.56), "paint", bevel=0.012, parent=ch, plane='XY')
    box("step", (0.2, 0.2, 0.05), (sx * 0.47, 0.11, 0.24), "chassis", bevel=0.01, parent=ch)
    box("step_hanger", (0.02, 0.2, 0.2), (sx * 0.56, 0.11, 0.33), "chassis", bevel=0.005, parent=ch)
    box("step_tread", (0.16, 0.16, 0.01), (sx * 0.47, 0.11, 0.268), "hazard", bevel=0.002, parent=ch, segments=1)

sill = hood(ch, y0=0.20, y1=0.80, zs0=0.18)
counterweight(ch, y0=0.78, y1=1.45, zb=0.16, zt=1.08, axle_y=1.08, axle_z=RRW - DZ, arch_r=0.32, also_cut=(sill,))
rear_axle(ch, y=1.08, z=RRW - DZ, r=RRW, w=0.17, x=0.47)
seat(ch, yc=0.52, z=0.98)
cowl(ch, yf=-0.55, zf=0.50, hw=0.27)
guard(ch, front_foot=(0.45, -0.28, 0.50), roof_front=(0.50, -0.06), roof_rear_y=0.87, roof_z=2.03, rear_foot=(0.50, 0.92, 1.06))

# ---- articulation: heavy pivot housing on the chassis nose
box("neck", (0.36, 0.2, 0.34), (0, PY + 0.12, 0.60), "chassis", bevel=0.03, parent=ch)
cyl("pivot_housing", 0.19, 0.40, (0, PY, 0.62), "chassis", bevel=0.02, parent=ch, verts=40)
cyl("pivot_band", 0.193, 0.05, (0, PY, 0.50), "hazard", parent=ch, verts=40)
cyl("pivot_cap", 0.13, 0.03, (0, PY, 0.83), "steel", bevel=0.006, parent=ch, verts=32)
cyl("pivot_pin", 0.05, 0.05, (0, PY, 0.86), "steel", bevel=0.01, parent=ch, verts=20)
for k in range(8):
    a = k * math.pi / 4
    cyl("pivot_bolt", 0.014, 0.02, (0.1 * math.cos(a), PY + 0.1 * math.sin(a), 0.85), "chassis", parent=ch, verts=6)

# ---- front unit: swings about the pivot (world coordinates of the hinge)
front = empty("front_pivot", (0, YS + PY, 0))
yoke = arc_pts(0, 0, 0.24, 0, 180, 16) + [(-0.31, -0.12), (-0.31, -0.44), (-0.27, -0.48), (0.27, -0.48), (0.31, -0.44), (0.31, -0.12)]
profile("yoke", yoke, 0.36, (0, 0, 0.32), "paint", bevel=0.03, parent=front, plane='XY')
cyl("turntable", 0.215, 0.035, (0, 0, 0.512), "chassis", parent=front, verts=40, bevel=0.005)
cyl("front_axle", 0.08, 0.80, (0, -0.30, RFW), "chassis", axis='X', parent=front)
box("motor_cover", (0.5, 0.2, 0.012), (0, -0.33, 0.502), "chassis", bevel=0.003, parent=front, segments=1)
box("yoke_plate", (0.012, 0.16, 0.1), (0.316, -0.3, 0.36), "decal", bevel=0, parent=front)
for sx in (-1, 1):
    wheel("w_front", RFW, 0.18, (sx * 0.46, -0.30, RFW), rim="rim", parent=front)
    tilt_cylinder(front, (sx * 0.335, -0.26, 0.44), (sx * 0.36, -0.465, 0.86), r=0.03)
    box("tilt_brk", (0.05, 0.08, 0.1), (sx * 0.325, -0.25, 0.42), "chassis", bevel=0.01, parent=front)
inner, car = mast(front, yc=-0.52, zb=0.12, top=2.15, lift=0.45)
key(front, FRAME_REST, rot=(0, 0, 0)); key(front, FRAME_WORK, rot=(0, 0, SWING))

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "pivot.glb"))
