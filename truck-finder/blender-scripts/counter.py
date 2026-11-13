import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nctlib import *
from cb_common import *
reset()

FA, RA = -0.45, 1.15          # front / rear axle Y (wheelbase 1.6)
RF, RR = 0.33, 0.25           # tyre radii

# ---- chassis, floor, step
box("frame", (0.66, 1.5, 0.36), (0, 0.2, 0.31), "chassis", bevel=0.03)
box("floor", (0.76, 0.84, 0.05), (0, -0.20, 0.475), "chassis", bevel=0.008)
for i in range(6):   # tread ribs on the floor mat
    box("floor_rib", (0.5, 0.012, 0.006), (0, -0.33 + i * 0.09, 0.502), "rubber", bevel=0, segments=1)
for sx in (-1, 1):
    box("step", (0.21, 0.25, 0.14), (sx * 0.465, 0.085, 0.31), "paint", bevel=0.02)
    box("step_tread", (0.17, 0.2, 0.012), (sx * 0.465, 0.08, 0.383), "rubber", bevel=0.003, segments=1)
    box("step_riser", (0.21, 0.03, 0.14), (sx * 0.465, 0.19, 0.44), "paint", bevel=0.01)

# ---- hood, sill, counterweight (with rear wheel arches cut through sill too)
sill = hood(None, y0=0.20, y1=0.90)
counterweight(None, y0=0.88, y1=1.58, axle_y=RA, axle_z=RR, also_cut=(sill,))
rear_axle(None, y=RA, z=RR, r=RR, w=0.17, x=0.47)
seat(None, yc=0.56, z=0.98)

# ---- front fenders over the drive wheels
for sx in (-1, 1):
    fp = [(-0.03, 0.26), (-0.03, 0.66)] + arc_pts(-0.09, 0.66, 0.06, 0, 90, 5) + arc_pts(-0.74, 0.66, 0.06, 90, 180, 5) + \
         arc_pts(FA, RF, 0.365, 163.5, -11, 20)
    profile("fender", fp, 0.21, (sx * 0.485, 0, 0), "paint", bevel=0.025)
    box("fender_in", (0.02, 0.5, 0.2), (sx * 0.385, -0.33, 0.58), "paint", bevel=0.005)
    wheel("w_front", RF, 0.22, (sx * 0.48, FA, RF), rim="rim")
cyl("drive_axle", 0.085, 0.78, (0, FA, RF), "chassis", axis='X')
cyl("diff", 0.15, 0.3, (0, FA, RF), "chassis", axis='X', bevel=0.04)

# ---- cowl, steering, controls
cowl(None, yf=-0.60, zf=0.50, hw=0.27)

# ---- overhead guard
guard(None, front_foot=(0.485, -0.60, 0.72), roof_front=(0.50, -0.22), roof_rear_y=0.95, roof_z=2.12, rear_foot=(0.50, 1.02, 1.06))

# ---- mast and tilt cylinders
inner, car = mast(None, yc=-0.73, zb=0.12, top=2.13, lift=1.55)
for sx in (-1, 1):
    tilt_cylinder(None, (sx * 0.335, -0.30, 0.58), (sx * 0.36, -0.675, 0.86))
    box("tilt_brk", (0.05, 0.08, 0.12), (sx * 0.335, -0.29, 0.54), "chassis", bevel=0.01)

export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "counter.glb"))
