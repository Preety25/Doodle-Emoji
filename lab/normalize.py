"""Normalize canvas strokes into unit-bbox Blender-friendly coordinates."""
from __future__ import annotations

import copy
import math
from typing import Any


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _perp_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def rdp(points, epsilon: float):
    """Ramer–Douglas–Peucker; keeps sharp corners when epsilon modest."""
    if len(points) < 3:
        return points
    dmax = 0.0
    idx = 0
    for i in range(1, len(points) - 1):
        d = _perp_dist(points[i], points[0], points[-1])
        if d > dmax:
            idx = i
            dmax = d
    if dmax > epsilon:
        left = rdp(points[: idx + 1], epsilon)
        right = rdp(points[idx:], epsilon)
        return left[:-1] + right
    return [points[0], points[-1]]


def classify_closed(points, declared: bool | None, close_tol_frac: float = 0.04) -> bool:
    if declared is True:
        return True
    if len(points) < 3:
        return False
    # bbox diagonal
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    if _dist(points[0], points[-1]) <= close_tol_frac * diag:
        return True
    return bool(declared)


def normalize_doodle(
    data: dict[str, Any],
    *,
    y_flip: bool = True,
    padding: float = 0.08,
    rdp_epsilon_frac: float = 0.004,
) -> dict[str, Any]:
    """
    Returns a new dict with strokes in Blender-ish coords:
    - Y flipped (canvas Y-down → Y-up)
    - centered at origin
    - scaled so max bbox axis fits in [-0.5+pad, 0.5-pad] roughly unit square
    """
    out = copy.deepcopy(data)
    canvas_w = float(out["canvas"]["width"])
    canvas_h = float(out["canvas"]["height"])

    raw_pts = []
    for s in out["strokes"]:
        pts = [[float(p[0]), float(p[1])] for p in s["points"]]
        if y_flip:
            pts = [[x, canvas_h - y] for x, y in pts]
        s["_raw"] = pts
        raw_pts.extend(pts)

    if not raw_pts:
        raise ValueError("no points")

    xs = [p[0] for p in raw_pts]
    ys = [p[1] for p in raw_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    cx = 0.5 * (min_x + max_x)
    cy = 0.5 * (min_y + max_y)
    bw = max(max_x - min_x, 1e-6)
    bh = max(max_y - min_y, 1e-6)
    scale = (1.0 - 2 * padding) / max(bw, bh)
    # target span ~1.0
    eps = rdp_epsilon_frac * max(bw, bh)

    components = []
    for s in out["strokes"]:
        pts = s["_raw"]
        simplified = rdp(pts, eps)
        if len(simplified) < 2:
            simplified = pts
        closed = classify_closed(simplified, s.get("closed"))
        norm = [[(p[0] - cx) * scale, (p[1] - cy) * scale] for p in simplified]
        if closed and _dist(norm[0], norm[-1]) > 1e-6:
            norm = norm + [norm[0][:]]
        comp = {
            "id": s["id"],
            "points": norm,
            "closed": closed,
            "color": s.get("color"),
            "n_raw": len(pts),
            "n_simplified": len(simplified),
        }
        components.append(comp)
        s["points"] = norm
        s["closed"] = closed
        del s["_raw"]

    out["normalized"] = {
        "padding": padding,
        "scale": scale,
        "center_canvas": [cx, cy],
        "bbox_canvas": [min_x, min_y, max_x, max_y],
        "y_flip": y_flip,
        "components": components,
    }
    return out
