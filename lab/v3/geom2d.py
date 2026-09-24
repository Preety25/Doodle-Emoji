"""2D helpers for stroke polygons. Pure Python, no Blender."""
from __future__ import annotations

import math


def hypot(x, y):
    return math.hypot(x, y)


def dedupe_ring(pts, tol=1e-5):
    out = []
    for p in pts:
        x, y = float(p[0]), float(p[1])
        if not out or hypot(x - out[-1][0], y - out[-1][1]) > tol:
            out.append([x, y])
    if len(out) > 2 and hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= tol:
        out = out[:-1]
    return out


def dedupe_path(pts, tol=1e-5):
    out = []
    for p in pts:
        x, y = float(p[0]), float(p[1])
        if not out or hypot(x - out[-1][0], y - out[-1][1]) > tol:
            out.append([x, y])
    return out


def bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def span(pts):
    x0, y0, x1, y1 = bbox(pts)
    return x1 - x0, y1 - y0, max(x1 - x0, y1 - y0)


def centroid(pts):
    ring = dedupe_ring(pts) if len(pts) > 2 else [list(p) for p in pts]
    if len(ring) < 3:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return sum(xs) / len(xs), sum(ys) / len(ys)
    a = 0.0
    cx = 0.0
    cy = 0.0
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        cross = x1 * y2 - x2 * y1
        a += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(a) < 1e-10:
        return sum(p[0] for p in ring) / n, sum(p[1] for p in ring) / n
    a *= 0.5
    return cx / (6 * a), cy / (6 * a)


def shoelace_area(pts):
    ring = dedupe_ring(pts)
    if len(ring) < 3:
        return 0.0
    a = 0.0
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) * 0.5


def point_segment_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return hypot(px - (ax + t * dx), py - (ay + t * dy))


def dist_to_edges(x, y, pts):
    ring = dedupe_ring(pts)
    if len(ring) < 2:
        return 0.0
    n = len(ring)
    dmin = 1e9
    for i in range(n):
        ax, ay = ring[i]
        bx, by = ring[(i + 1) % n]
        dmin = min(dmin, point_segment_dist(x, y, ax, ay, bx, by))
    return dmin


def point_in_poly(x, y, pts):
    ring = dedupe_ring(pts)
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-15) + xi):
            inside = not inside
        j = i
    return inside


def path_length(pts):
    total = 0.0
    for i in range(1, len(pts)):
        total += hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
    return total


def _walk_samples(pts, closed, count):
    if len(pts) < 2 or count < 2:
        return [list(p) for p in pts]
    seq = [list(p) for p in pts]
    if closed:
        seq = seq + [seq[0]]
    lengths = [0.0]
    for i in range(1, len(seq)):
        lengths.append(lengths[-1] + hypot(seq[i][0] - seq[i - 1][0], seq[i][1] - seq[i - 1][1]))
    total = lengths[-1]
    if total < 1e-8:
        return [list(p) for p in pts]
    samples = []
    steps = count if not closed else count
    for s in range(steps):
        if closed:
            d = total * (s / steps)
        else:
            d = total * (s / (steps - 1))
        # find segment
        i = 1
        while i < len(lengths) - 1 and lengths[i] < d:
            i += 1
        span_l = lengths[i] - lengths[i - 1]
        t = 0.0 if span_l < 1e-9 else (d - lengths[i - 1]) / span_l
        ax, ay = seq[i - 1]
        bx, by = seq[i]
        samples.append([ax + (bx - ax) * t, ay + (by - ay) * t])
    return samples


def resample_closed(pts, count, pins=None):
    ring = dedupe_ring(pts)
    if len(ring) < 3:
        return ring
    samples = _walk_samples(ring, True, max(count, len(ring)))
    if pins:
        for pin in pins:
            if pin is None:
                continue
            # replace nearest sample so the feature survives uniform sampling
            j = min(range(len(samples)), key=lambda i: hypot(samples[i][0] - pin[0], samples[i][1] - pin[1]))
            samples[j] = [float(pin[0]), float(pin[1])]
    return samples


def resample_open(pts, count):
    path = dedupe_path(pts)
    if len(path) < 2:
        return path
    return _walk_samples(path, False, max(count, len(path)))


def chaikin_open(pts, iterations=1):
    cur = dedupe_path(pts)
    if len(cur) < 3:
        return cur
    for _ in range(iterations):
        nxt = [cur[0]]
        for i in range(len(cur) - 1):
            p, q = cur[i], cur[i + 1]
            nxt.append([0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]])
            nxt.append([0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]])
        nxt.append(cur[-1])
        cur = nxt
    return cur


def find_cleft(pts):
    """Top-center dip between two lobes. Y-up coordinates. Returns point or None."""
    ring = dedupe_ring(pts)
    if len(ring) < 8:
        return None
    x0, y0, x1, y1 = bbox(ring)
    height = y1 - y0
    width = x1 - x0
    if height < 1e-4 or width < 1e-4:
        return None
    y_cut = y1 - 0.32 * height
    cx = 0.5 * (x0 + x1)
    band = [p for p in ring if p[1] >= y_cut]
    central = [p for p in band if abs(p[0] - cx) <= 0.22 * width]
    if len(central) < 1 or len(band) < 4:
        return None
    cleft = min(central, key=lambda p: p[1])
    left = [p for p in band if p[0] < cleft[0] - 0.06 * width]
    right = [p for p in band if p[0] > cleft[0] + 0.06 * width]
    if not left or not right:
        return None
    left_peak = max(p[1] for p in left)
    right_peak = max(p[1] for p in right)
    if left_peak > cleft[1] + 0.025 * height and right_peak > cleft[1] + 0.025 * height:
        return cleft
    return None


def bottom_point(pts):
    ring = dedupe_ring(pts) or [list(p) for p in pts]
    return min(ring, key=lambda p: (p[1], abs(p[0])))


def split_tapered_nose(pts):
    """Split a tall tapered outline into nose triangle + body.

    The nose is the upper taper (tip + shoulders). The body keeps the shoulders
    so the two meshes meet, and drops only the tip chain.
    """
    ring = dedupe_ring(pts)
    n = len(ring)
    if n < 4:
        return None
    tip_i = max(range(n), key=lambda i: ring[i][1])
    tip = ring[tip_i]
    x0, y0, x1, y1 = bbox(ring)
    height = max(y1 - y0, 1e-6)
    width = max(x1 - x0, 1e-6)
    # Immediate neighbors are the shoulders on the golden pentagon-like body.
    li = (tip_i - 1) % n
    ri = (tip_i + 1) % n
    # If the outline is denser, walk out while the cross-width is still the taper.
    guard = 0
    while guard < n - 3:
        guard += 1
        cross = abs(ring[li][0] - ring[ri][0])
        drop = tip[1] - min(ring[li][1], ring[ri][1])
        if cross >= 0.72 * width and drop >= 0.08 * height:
            break
        # step the higher side downward (still on the nose)
        nli = (li - 1) % n
        nri = (ri + 1) % n
        if ring[nli][1] >= ring[nri][1] and ring[nli][1] < ring[li][1] + 1e-6:
            if nli == ri or nli == tip_i:
                break
            li = nli
        else:
            if nri == li or nri == tip_i:
                break
            ri = nri
        if abs(ring[li][0] - ring[ri][0]) > 0.9 * width:
            break
    left, right = ring[li], ring[ri]
    if tip[1] - max(left[1], right[1]) < 0.06 * height:
        return None
    # Nose polygon: shoulders, tip, and a short embed below the shoulder line.
    embed = 0.012 * height
    nose = [
        [left[0], left[1]],
        [tip[0], tip[1]],
        [right[0], right[1]],
        [right[0], right[1] - embed],
        [left[0], left[1] - embed],
    ]
    # Body: ring with the open chain from li..tip..ri removed, shoulders kept.
    body = []
    i = ri
    body.append(ring[ri])
    while i != li:
        i = (i + 1) % n
        body.append(ring[i])
    if len(body) < 3:
        return None
    return {
        "nose": nose,
        "body": body,
        "tip": tip,
        "shoulders": [left, right],
    }


def pull_vertices_into(poly, target, amount=0.012, near=0.025):
    """Nudge vertices that touch `target` slightly toward its centroid (embed, don't union)."""
    cx, cy = centroid(target)
    out = []
    for x, y in dedupe_ring(poly):
        inside = point_in_poly(x, y, target)
        d = dist_to_edges(x, y, target)
        if inside or d < near:
            vx, vy = cx - x, cy - y
            L = hypot(vx, vy) or 1.0
            out.append([x + vx / L * amount, y + vy / L * amount])
        else:
            out.append([x, y])
    return out


def vertical_seam(poly, samples=16):
    ring = dedupe_ring(poly)
    if len(ring) < 3:
        return []
    cx, _cy = centroid(ring)
    _x0, y0, _x1, y1 = bbox(ring)
    pts = []
    for i in range(samples):
        y = y1 - (y1 - y0) * (i / (samples - 1))
        if point_in_poly(cx, y, ring) or dist_to_edges(cx, y, ring) < 1e-3:
            # nudge just inside if we landed on the boundary
            pts.append([cx, y])
    # drop endpoints that sit on the silhouette so the stitch reads as a seam, not a spike
    if len(pts) > 4:
        pts = pts[1:-1]
    return pts


def hex_to_rgb(h):
    h = (h or "#888888").lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return [int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]


def grade_color(rgb, saturation=1.0, value=1.0, toward=None, toward_amt=0.0):
    m = sum(rgb) / 3.0
    out = [m + (c - m) * saturation for c in rgb]
    out = [max(0.0, min(1.0, c * value)) for c in out]
    if toward and toward_amt:
        out = [(1 - toward_amt) * c + toward_amt * t for c, t in zip(out, toward)]
    return [max(0.0, min(1.0, c)) for c in out]
