"""Helpers for pump.py and gantry.py (kept out of nctlib.py / tpmlib.py on purpose)."""
import math
from mathutils import Vector
from nctlib import *
from tpmlib import FRAMES, bar3d, rod3d, ring, lerp


def fillet(points, r, n=5, closed=False):
    """Round the corners of a 3D polyline with radius r; returns a denser point list for tube()."""
    P = [Vector(p) for p in points]
    out = []
    N = len(P)
    for i in range(N):
        if not closed and i in (0, N - 1):
            out.append(tuple(P[i])); continue
        a, b, c = P[i - 1], P[i], P[(i + 1) % N]
        u, v = (a - b), (c - b)
        d = min(r, u.length * 0.49, v.length * 0.49)
        p0, p1 = b + u.normalized() * d, b + v.normalized() * d
        for k in range(n + 1):
            t = k / n
            out.append(tuple((1 - t) ** 2 * p0 + 2 * t * (1 - t) * b + t ** 2 * p1))
    return out


def stretch(name, A, B, radius, material, parent=None, frames=FRAMES, verts=12, square=None):
    """A rod/rope pinned at A(f) and B(f) (3D points in the parent's space) on every frame.
    Origin at A, scale-keyed along its length so it always reaches B."""
    e = empty(name, A(frames[0]), parent)
    if square:
        box(name + "_m", (square[0], square[1], 1.0), (0, 0, 0.5), material, bevel=0, parent=e)
    else:
        cyl(name + "_m", radius, 1.0, (0, 0, 0.5), material, parent=e, verts=verts)
    for f in frames:
        a, b = Vector(A(f)), Vector(B(f))
        d = b - a
        key(e, f, loc=tuple(a), rot=tuple(d.to_track_quat('Z', 'Y').to_euler()), scale=(1, 1, max(d.length, 1e-4)))
    return e


def helix_pts(r, turns, height=1.0, n=14):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), height * i / (turns * n)) for i in range(int(turns * n) + 1)]
