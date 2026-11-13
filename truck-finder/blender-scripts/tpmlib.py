"""Extra helpers shared by tele.py, ppt.py and mewp.py (kept out of nctlib.py on purpose)."""
import math
from mathutils import Vector
from nctlib import *

FRAMES = list(range(FRAME_REST, FRAME_WORK + 1))


def lerp(a, b, t):
    return a + (b - a) * t


def rot2(p, deg):
    """Rotate a (y, z) point about the X axis by deg (same sense as a Blender X rotation)."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def bar3d(name, p0, p1, w, h, material, bevel=0.008, parent=None, segments=2, extend=0.0):
    """A rectangular bar (w across, h thick) running from point p0 to p1."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    L = d.length + 2 * extend
    o = box(name, (w, h, L), (a + b) / 2, material, bevel=bevel, parent=parent, segments=segments)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def rod3d(name, p0, p1, r, material, parent=None, verts=20):
    """A round rod from p0 to p1."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    o = cyl(name, r, d.length, (a + b) / 2, material, parent=parent, verts=verts)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def arch(name, r_in, r_out, a0, a1, width, loc, material, bevel=0.01, parent=None, n=18):
    """A curved band (mudguard) in the YZ plane, extruded across X."""
    pts = arc_pts(0, 0, r_out, a0, a1, n) + arc_pts(0, 0, r_in, a1, a0, n)
    return profile(name, pts, width, loc, material, bevel=bevel, parent=parent, plane='YZ', segments=2)


def ring(name, r, tube_r, loc, material, axis='Z', parent=None, n=24, rot=None):
    pts = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 0) for i in range(n)]
    o = tube(name, pts, tube_r, material, parent=parent, closed=True, resolution=2)
    o.location = loc
    o.rotation_euler = rot if rot is not None else {'Z': (0, 0, 0), 'X': (0, math.radians(90), 0), 'Y': (math.radians(90), 0, 0)}[axis]
    return o


def aim_yz(a, b):
    """X rotation that points a local +Y axis from a towards b ((y, z) points)."""
    return math.atan2(b[1] - a[1], b[0] - a[0])


def hyd_ram(name, x, A, B, barrel_r, barrel_len, rod_r, rod_len, frames=FRAMES, barrel_mat="chassis", parent=None):
    """A hydraulic cylinder working in the YZ plane at width x. A(f) and B(f) give the (y, z) of the barrel
    and rod pins at frame f; both halves are keyed on every frame so the ram stays pinned at both ends."""
    ea = empty(name + "_barrel", (x, *A(frames[0])), parent)
    eb = empty(name + "_rod", (x, *B(frames[0])), parent)
    cyl(name + "_b", barrel_r, barrel_len, (0, barrel_len / 2, 0), barrel_mat, axis='Y', parent=ea, bevel=0.006, verts=24)
    cyl(name + "_bcap", barrel_r * 1.12, 0.05, (0, barrel_len - 0.025, 0), "steel", axis='Y', parent=ea, bevel=0.004, verts=24)
    cyl(name + "_beye", barrel_r * 1.05, barrel_r * 2.3, (0, 0, 0), barrel_mat, axis='X', parent=ea, bevel=0.004, verts=20)
    cyl(name + "_r", rod_r, rod_len, (0, -rod_len / 2, 0), "chrome", axis='Y', parent=eb, verts=20)
    cyl(name + "_reye", rod_r * 1.7, rod_r * 3.2, (0, 0, 0), "steel", axis='X', parent=eb, bevel=0.004, verts=20)
    for f in frames:
        a, b = A(f), B(f)
        ang = aim_yz(a, b)
        key(ea, f, loc=(x, *a), rot=(ang, 0, 0))
        key(eb, f, loc=(x, *b), rot=(ang, 0, 0))
    return ea, eb
