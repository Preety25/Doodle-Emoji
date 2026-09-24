"""
Heuristic semantic Transformation Plan (NO neural nets / cloud AI).

Shape cues → subject + confidence + completion_budget (0–2).
Ambiguous blob → LOW → Level 0–1 only.
Style recipes must NOT invent semantics; this layer decides limited completion only.

Heuristics (documented):
- Point-count / radial peaks → star (5-ish alternating radii)
- Parametric heart-ish top cleft + bottom point → heart
- Round outer + ≥2 small dark interior closed marks + open arc → face
- Vertical open stroke under closed mass(es) + side lobes → plant / flower
- Tall tapered body + side triangles → rocket
- Large round body + smaller round head + ear lobes + eyes → teddy
- Spiral open stroke inside round bloom → rose
- Single open stroke only → open_stroke (LOW)
- ≥3 disconnected similar-size closed → multi_part
- Fragmented / incomplete closed attempts → messy_incomplete (LOW)
- Default single soft closed → blob (LOW)
"""
from __future__ import annotations

import math
from typing import Any


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _area_est(pts):
    if len(pts) < 3:
        return 0.0
    # shoelace
    a = 0.0
    for i in range(len(pts) - 1):
        a += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
    return abs(a) * 0.5


def _radial_profile(pts, n=24):
    if len(pts) < 3:
        return []
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    bins = [0.0] * n
    counts = [0] * n
    for p in pts:
        ang = math.atan2(p[1] - cy, p[0] - cx)
        idx = int((ang + math.pi) / (2 * math.pi) * n) % n
        r = math.hypot(p[0] - cx, p[1] - cy)
        bins[idx] += r
        counts[idx] += 1
    return [bins[i] / counts[i] if counts[i] else 0.0 for i in range(n)]


def _count_peaks(profile, min_rel=0.15):
    if not profile:
        return 0
    mean = sum(profile) / len(profile) or 1.0
    peaks = 0
    n = len(profile)
    for i in range(n):
        a, b, c = profile[(i - 1) % n], profile[i], profile[(i + 1) % n]
        if b > a and b >= c and (b - mean) / mean > min_rel:
            peaks += 1
    return peaks


def _aspect(pts):
    x0, y0, x1, y1 = _bbox(pts)
    w, h = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
    return w / h, w, h


def _has_top_cleft(pts):
    """Heart cue: local minimum near top center."""
    if len(pts) < 8:
        return False
    x0, y0, x1, y1 = _bbox(pts)
    cy_top = y0 + 0.25 * (y1 - y0)
    top = [p for p in pts if p[1] <= cy_top]
    if len(top) < 4:
        return False
    cx = 0.5 * (x0 + x1)
    # look for dip near center
    near = sorted(top, key=lambda p: abs(p[0] - cx))[:6]
    mid_y = sum(p[1] for p in near) / len(near)
    left = [p for p in top if p[0] < cx - 0.05 * (x1 - x0)]
    right = [p for p in top if p[0] > cx + 0.05 * (x1 - x0)]
    if not left or not right:
        return False
    left_peak = min(p[1] for p in left)
    right_peak = min(p[1] for p in right)
    return mid_y > left_peak + 0.02 * (y1 - y0) and mid_y > right_peak + 0.02 * (y1 - y0)


def _is_spiral_like(pts):
    if len(pts) < 20:
        return False
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    angs = [math.atan2(p[1] - cy, p[0] - cx) for p in pts]
    # unwrap-ish: count monotonic angle travel
    travel = 0.0
    for i in range(1, len(angs)):
        d = angs[i] - angs[i - 1]
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        travel += d
    return abs(travel) > 2.5 * math.pi



def _finalize(subject, confidence, completion_budget, transform_mode, cues, invent_faces, preserve_user_faces, n, closed, open_):
    if confidence == "LOW":
        completion_budget = min(int(completion_budget), 1)
    if subject in ("face", "teddy") and preserve_user_faces and confidence == "HIGH":
        invent_faces = False
    return {
        "subject": subject,
        "confidence": confidence,
        "completion_budget": int(completion_budget),
        "transform_mode": transform_mode,
        "cues": cues,
        "invent_faces": invent_faces,
        "preserve_user_faces": preserve_user_faces,
        "n_components": n,
        "n_closed": len(closed),
        "n_open": len(open_),
        "planner": "heuristic_v2",
        "planner_version": "sem.v2.0",
    }


def plan_from_components(components: list[dict[str, Any]], meta: dict | None = None) -> dict[str, Any]:
    """
    Build Transformation Plan from normalized components.
    completion_budget: 0=none, 1=minor implied, 2=strong character cues only.
    Never invent faces unless HIGH confidence character + partial face cues already present.
    """
    meta = meta or {}
    n = len(components)
    closed = [c for c in components if c.get("closed")]
    open_ = [c for c in components if not c.get("closed")]
    areas = sorted([(_area_est(c["points"]), c) for c in closed], key=lambda x: -x[0])

    subject = "blob"
    confidence = "LOW"
    completion_budget = 0
    transform_mode = "polish"
    cues: list[str] = []
    invent_faces = False
    preserve_user_faces = False

    # Prefer category hint only as weak prior (corpus labels); still run geometry cues
    hint = (meta.get("category") or meta.get("description") or "").lower()

    # --- Early structural gates (before object-identity heuristics) ---
    # Open stroke only
    if n == 1 and open_ and not closed:
        subject = "open_stroke"
        confidence = "LOW"
        completion_budget = 0
        cues.append("single_open")
        return _finalize(subject, confidence, completion_budget, transform_mode, cues, invent_faces, preserve_user_faces, n, closed, open_)

    # Messy incomplete: mostly open fragments
    if len(open_) >= 2 and len(closed) <= 1 and ("messy" in hint or "incomplete" in hint or len(open_) >= 2):
        # only if no strong face/teddy pattern
        if not (len(closed) >= 1 and len(open_) == 1 and areas and any(a < areas[0][0] * 0.08 for a, _ in areas[1:])):
            subject = "messy_incomplete"
            confidence = "LOW"
            completion_budget = 0
            cues.append("fragmented")
            if "messy" in hint or "incomplete" in hint or sum(1 for c in open_ if len(c.get("points", [])) < 12) >= 1:
                return _finalize(subject, confidence, completion_budget, transform_mode, cues, invent_faces, preserve_user_faces, n, closed, open_)

    # Rocket early: dominant tall body + smaller side parts
    if len(closed) >= 3 and areas:
        main = areas[0][1]
        aspect, w, h = _aspect(main["points"])
        sizes = [a for a, _ in areas]
        if len(sizes) >= 3 and h > w * 1.15 and sizes[0] > 1.6 * (sum(sizes[1:3]) / 2.0):
            subject = "rocket"
            confidence = "HIGH"
            completion_budget = 1
            cues.append("tall_body+fins")
            return _finalize(subject, confidence, completion_budget, transform_mode, cues, invent_faces, preserve_user_faces, n, closed, open_)
        if "rocket" in hint and h > w * 1.05:
            subject = "rocket"
            confidence = "MEDIUM"
            completion_budget = 1
            cues.append("hint:rocket")
            return _finalize(subject, confidence, completion_budget, transform_mode, cues, invent_faces, preserve_user_faces, n, closed, open_)

    # Multi-part: ≥3 disconnected similar-size closed, no opens
    if len(closed) >= 3 and not open_:
        sizes = [_area_est(c["points"]) for c in closed]
        mean = sum(sizes) / len(sizes)
        if max(sizes) < 3.5 * mean and min(sizes) > 0.2 * mean:
            # check separation: centroids far relative to sizes
            cents = []
            for c in closed:
                pts = c["points"]
                cents.append((sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)))
            # if pairwise distances suggest separated peers
            import math as _m
            sep = 0
            for i in range(len(cents)):
                for j in range(i + 1, len(cents)):
                    d = _m.hypot(cents[i][0] - cents[j][0], cents[i][1] - cents[j][1])
                    if d > 0.25:
                        sep += 1
            if sep >= 2:
                subject = "multi_part"
                confidence = "MEDIUM"
                completion_budget = 0
                cues.append("disconnected_peers")
                return _finalize(subject, confidence, completion_budget, transform_mode, cues, invent_faces, preserve_user_faces, n, closed, open_)

    # Face: large closed + ≥2 tiny closed + ≥1 open (smile)
    if closed and len(closed) >= 3 and open_:
        if areas:
            main_a, main = areas[0]
            tiny = [c for a, c in areas[1:] if a < main_a * 0.08]
            if len(tiny) >= 2:
                subject = "face"
                confidence = "HIGH"
                completion_budget = 1
                preserve_user_faces = True
                cues.append("round_head+eyes+open_arc")

    # Teddy: body+head+ears pattern
    if subject == "blob" and len(closed) >= 4:
        if areas and len(areas) >= 3:
            a0 = areas[0][0]
            mid = [a for a, _ in areas[1:4] if a0 * 0.15 < a < a0 * 0.75]
            tiny = [a for a, _ in areas if a < a0 * 0.08]
            if len(mid) >= 1 and len(tiny) >= 2:
                subject = "teddy"
                confidence = "HIGH"
                completion_budget = 2
                preserve_user_faces = True
                cues.append("body+head+ears+eyes")

    # Star: single closed with ~5 radial peaks
    if subject == "blob" and len(closed) == 1 and not open_:
        prof = _radial_profile(closed[0]["points"])
        peaks = _count_peaks(prof)
        if peaks >= 4:
            subject = "star"
            confidence = "HIGH"
            completion_budget = 1
            cues.append(f"radial_peaks={peaks}")

    # Heart: top cleft on a single dominant closed (not fragments)
    if subject == "blob" and len(closed) == 1 and len(open_) == 0:
        cleft = _has_top_cleft(closed[0]["points"])
        if cleft or "heart" in hint:
            subject = "heart"
            confidence = "HIGH" if cleft else "MEDIUM"
            completion_budget = 1
            cues.append("top_cleft" if cleft else "hint:heart")

    # Rose: spiral open + round closed
    if subject == "blob" and closed and any(_is_spiral_like(c["points"]) for c in open_):
        subject = "rose"
        confidence = "MEDIUM"
        completion_budget = 1
        cues.append("spiral_in_bloom")

    # Flower: many similar closed petals around center
    if subject == "blob" and len(closed) >= 5:
        sizes = [_area_est(c["points"]) for c in closed]
        med = sorted(sizes)[len(sizes) // 2]
        similar = sum(1 for a in sizes if 0.4 * med < a < 2.5 * med)
        if similar >= 4:
            subject = "flower"
            confidence = "HIGH"
            completion_budget = 1
            cues.append("petal_ring")

    # Plant: pot-like wide bottom closed + vertical open stem + leaf closed
    if subject == "blob" and closed and open_:
        # stem-like open with mostly vertical travel
        vert_opens = 0
        for c in open_:
            pts = c["points"]
            if len(pts) < 2:
                continue
            dx = abs(pts[-1][0] - pts[0][0])
            dy = abs(pts[-1][1] - pts[0][1])
            if dy > dx * 1.4:
                vert_opens += 1
        if vert_opens >= 1 and len(closed) >= 2:
            subject = "plant"
            confidence = "HIGH"
            completion_budget = 1
            cues.append("pot+stem+leaves")

    # Rocket: tall aspect main body + side fins (and not peer-equal multi blobs)
    if subject == "blob" and len(closed) >= 3:
        main = areas[0][1] if areas else None
        if main:
            aspect, w, h = _aspect(main["points"])
            sizes = [a for a, _ in areas]
            dominant = sizes[0] > 1.8 * (sum(sizes[1:3]) / 2.0) if len(sizes) >= 3 else False
            if h > w * 1.2 and (dominant or "rocket" in hint):
                subject = "rocket"
                confidence = "HIGH" if dominant else "MEDIUM"
                completion_budget = 1
                cues.append("tall_body+fins")

    # Multi-part
    if subject == "blob" and len(closed) >= 3 and not open_:
        sizes = [_area_est(c["points"]) for c in closed]
        if max(sizes) < 3.5 * (sum(sizes) / len(sizes)):
            subject = "multi_part"
            confidence = "MEDIUM"
            completion_budget = 0
            cues.append("disconnected_peers")

    # Open stroke only
    if n == 1 and open_:
        subject = "open_stroke"
        confidence = "LOW"
        completion_budget = 0
        cues.append("single_open")

    # Messy incomplete: mostly open fragments / partial
    if subject == "blob" and len(open_) >= 2 and len(closed) <= 1:
        subject = "messy_incomplete"
        confidence = "LOW"
        completion_budget = 0
        cues.append("fragmented")

    # Ambiguous single blob
    if subject == "blob":
        confidence = "LOW"
        completion_budget = 0
        transform_mode = "polish"
        cues.append("ambiguous_closed" if closed else "ambiguous")

    # Hint reinforcement (never upgrade LOW blob to invent)
    if hint and subject == "blob":
        for key in ("heart", "star", "face", "plant", "rocket", "teddy", "flower", "rose"):
            if key in hint:
                subject = key
                confidence = "MEDIUM"
                completion_budget = min(1, completion_budget + 1)
                cues.append(f"hint:{key}")
                break

    # Face rule: never invent faces from style; only preserve / limited complete
    if subject in ("face", "teddy") and preserve_user_faces and confidence == "HIGH":
        invent_faces = False  # completion may close gaps only; no new features
        # completion_budget already set; semantic completion of partial cues allowed at budget

    if confidence == "LOW":
        completion_budget = min(completion_budget, 1)

    return {
        "subject": subject,
        "confidence": confidence,  # HIGH | MEDIUM | LOW
        "completion_budget": int(completion_budget),  # 0–2
        "transform_mode": transform_mode,
        "cues": cues,
        "invent_faces": invent_faces,
        "preserve_user_faces": preserve_user_faces,
        "n_components": n,
        "n_closed": len(closed),
        "n_open": len(open_),
        "planner": "heuristic_v2",
        "planner_version": "sem.v2.0",
    }


def plan_doodle(normalized: dict[str, Any]) -> dict[str, Any]:
    comps = normalized.get("normalized", {}).get("components") or []
    meta = normalized.get("meta") or {}
    return plan_from_components(comps, meta)
