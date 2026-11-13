"""Shared helpers for the warehouse trucks (reach, vna). Uses nctlib only."""
import math
from nctlib import *
from mathutils import Vector


def rtube(name, pts, radius, material, parent=None, bend=0.08, n=6, closed=False):
    """Round tube through pts with filleted (bent) corners."""
    P = [Vector(p) for p in pts]
    out = []
    N = len(P)
    for i, p in enumerate(P):
        if not closed and (i == 0 or i == N - 1):
            out.append(tuple(p)); continue
        a, b = P[(i - 1) % N], P[(i + 1) % N]
        d = min(bend, (a - p).length / 2.01, (b - p).length / 2.01)
        p1 = p + (a - p).normalized() * d
        p2 = p + (b - p).normalized() * d
        for k in range(n + 1):
            t = k / n
            q = (1 - t) ** 2 * p1 + 2 * t * (1 - t) * p + t * t * p2
            out.append(tuple(q))
    return tube(name, out, radius, material, parent=parent, closed=closed)


def channel(name, w, d, t, length, loc, material, parent=None, open_dir=1, bevel=0.004):
    """Vertical C-channel (mast upright). w across X, d along Y, wall t, opening toward open_dir (+1 = +X)."""
    s = open_dir
    pts = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, -d / 2 + t), (-w / 2 + t, -d / 2 + t),
           (-w / 2 + t, d / 2 - t), (w / 2, d / 2 - t), (w / 2, d / 2), (-w / 2, d / 2)]
    pts = [(a * s, b) for a, b in pts]
    return profile(name, pts, length, loc, material, bevel=bevel, parent=parent, plane='XY', segments=1)


def seat(name, loc, yaw, parent=None, armrests=True):
    """Operator seat; local frame faces -Y, origin at underside of cushion centre."""
    e = empty(name, loc, parent, rot=(0, 0, yaw))
    box(name + "_base", (0.40, 0.36, 0.05), (0, 0.0, -0.02), "chassis", 0.01, e)
    box(name + "_cush", (0.47, 0.44, 0.10), (0, -0.01, 0.055), "vinyl", 0.04, e, segments=4)
    box(name + "_bol", (0.47, 0.07, 0.05), (0, -0.2, 0.10), "vinyl", 0.024, e, segments=3)
    box(name + "_back", (0.45, 0.10, 0.52), (0, 0.235, 0.36), "vinyl", 0.045, e, rot=(math.radians(-8), 0, 0), segments=4)
    box(name + "_lum", (0.33, 0.05, 0.28), (0, 0.185, 0.30), "vinyl", 0.024, e, rot=(math.radians(-8), 0, 0))
    box(name + "_head", (0.26, 0.08, 0.16), (0, 0.285, 0.70), "vinyl", 0.035, e, rot=(math.radians(-8), 0, 0))
    if armrests:
        for sx in (-1, 1):
            box(name + "_arm", (0.06, 0.30, 0.045), (sx * 0.265, 0.03, 0.27), "vinyl", 0.02, e)
            box(name + "_armp", (0.03, 0.04, 0.2), (sx * 0.265, 0.17, 0.2), "chassis", 0.008, e)
    return e


def chain(name, length, loc, parent=None, width=0.034):
    """Leaf chain hanging DOWN from loc... built upward from loc (origin at bottom) so it can be scaled in Z."""
    e = empty(name, loc, parent)
    box(name + "_s", (width, 0.012, length), (0, 0, length / 2), "steel", 0.002, e, segments=1)
    box(name + "_c", (width * 0.45, 0.016, length), (0, 0, length / 2), "chassis", 0.0, e)
    return e


def backrest(name, parent, width=0.92, z0=0.56, z1=1.25, y=0.0, bars=5):
    hw = width / 2
    for sx in (-1, 1):
        box(name + "_side", (0.035, 0.03, z1 - z0), (sx * hw, y, (z0 + z1) / 2), "mast", 0.006, parent)
    box(name + "_top", (width + 0.035, 0.03, 0.035), (0, y, z1), "mast", 0.006, parent)
    box(name + "_mid", (width, 0.02, 0.03), (0, y, (z0 + z1) / 2), "mast", 0.004, parent)
    for i in range(bars):
        x = -hw + width * (i + 1) / (bars + 1)
        box(name + "_bar", (0.022, 0.016, z1 - z0), (x, y, (z0 + z1) / 2), "mast", 0.003, parent, segments=1)


def lamp(name, loc, parent=None, axis='Y', r=0.045):
    cyl(name + "_h", r, 0.06, loc, "plastic", axis=axis, bevel=0.008, parent=parent)
    l = list(loc)
    i = 'XYZ'.index(axis)
    l[i] -= 0.031
    cyl(name + "_l", r * 0.82, 0.006, tuple(l), "lamp", axis=axis, parent=parent)


def beacon(name, loc, parent=None):
    cyl(name + "_b", 0.045, 0.03, loc, "plastic", parent=parent, bevel=0.005)
    lathe(name + "_d", [(0.0, 0.085), (0.02, 0.083), (0.034, 0.07), (0.038, 0.0), (0.0, 0.0)], (loc[0], loc[1], loc[2] + 0.015), "beacon", axis='Z', parent=parent, steps=20)
