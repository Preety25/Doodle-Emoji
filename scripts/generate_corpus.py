"""Generate 20 imperfect hand-drawn-ish doodle stroke JSONs (regeneratable)."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus" / "doodles"
MANIFEST = ROOT / "corpus" / "manifest.json"
CANVAS = {"width": 512, "height": 512}


def jitter(pts, rng, amp=2.5):
    return [[p[0] + rng.uniform(-amp, amp), p[1] + rng.uniform(-amp, amp)] for p in pts]


def ellipse(cx, cy, rx, ry, n=36, rng=None, wobble=0.08):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        wr = 1.0 + (rng.uniform(-wobble, wobble) if rng else 0)
        pts.append([cx + rx * wr * math.cos(a), cy + ry * wr * math.sin(a)])
    return pts


def heart(cx, cy, s=90, n=48, rng=None):
    """Classic parametric heart, scaled so max extent ~ s pixels."""
    pts = []
    raw = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        raw.append((x, y))
    max_ext = max(max(abs(x), abs(y)) for x, y in raw) or 1.0
    scale = s / max_ext
    for x, y in raw:
        px, py = cx + x * scale, cy + y * scale
        if rng:
            px += rng.uniform(-3, 3)
            py += rng.uniform(-3, 3)
        pts.append([px, py])
    return pts


def star(cx, cy, r_out=100, r_in=40, points=5, rng=None):
    pts = []
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        r = r_out if i % 2 == 0 else r_in
        if rng:
            r *= 1 + rng.uniform(-0.12, 0.12)
            ang += rng.uniform(-0.08, 0.08)
        pts.append([cx + r * math.cos(ang), cy + r * math.sin(ang)])
    return pts


def cloud(cx, cy, rng):
    # several overlapping ellipses as one polyline outline approx
    bumps = []
    for i, (dx, dy, rx, ry) in enumerate([(-60, 10, 55, 40), (-10, -25, 60, 50), (55, 5, 50, 38), (10, 30, 70, 35)]):
        bumps.extend(ellipse(cx + dx, cy + dy, rx, ry, n=20, rng=rng, wobble=0.1))
    # take convex-ish hull approx by angle sort
    ang = sorted(bumps, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
    return ang


def stroke(sid, points, closed=True, color="#FF6699"):
    return {"id": sid, "points": [[round(p[0], 2), round(p[1], 2)] for p in points], "closed": closed, "color": color, "pressure": None}


def save(doodle_id, strokes, seed, description, category):
    data = {"canvas": CANVAS, "strokes": strokes, "seed": seed, "meta": {"description": description, "category": category}}
    path = OUT / f"{doodle_id}.json"
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    return {"id": doodle_id, "category": category, "description": description, "path": f"corpus/doodles/{doodle_id}.json"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    # 01 blob
    rng = random.Random(101)
    manifest.append(save("01_blob", [stroke("s1", ellipse(256, 260, 110, 90, n=40, rng=rng, wobble=0.15), True, "#FF8A5B")], 1, "closed organic blob", "closed_blob"))
    # 02 heart asymmetric
    rng = random.Random(102)
    h = heart(256, 250, s=100, rng=rng)
    h = jitter(h, rng, 2.0)
    # squash one side
    h = [[p[0] - (8 if p[0] < 256 else 0), p[1]] for p in h]
    manifest.append(save("02_heart", [stroke("s1", h, True, "#FF4D6D")], 1, "asymmetric heart", "heart"))
    # 03 cloud
    rng = random.Random(103)
    manifest.append(save("03_cloud", [stroke("s1", cloud(256, 256, rng), True, "#7EC8FF")], 1, "lumpy cloud", "cloud"))
    # 04 star wonky
    rng = random.Random(104)
    manifest.append(save("04_star", [stroke("s1", star(256, 256, 120, 48, 5, rng), True, "#FFD166")], 1, "wonky 5-point star", "star"))
    # 05 simple face
    rng = random.Random(105)
    face = ellipse(256, 256, 100, 110, n=36, rng=rng, wobble=0.06)
    le = ellipse(220, 230, 12, 16, n=12, rng=rng)
    re = ellipse(295, 235, 11, 15, n=12, rng=rng)
    smile = [[210 + i * 8, 300 + 18 * math.sin(i / 10 * math.pi) + rng.uniform(-1, 1)] for i in range(12)]
    manifest.append(save("05_face", [
        stroke("head", face, True, "#FFE066"),
        stroke("le", le, True, "#222222"),
        stroke("re", re, True, "#222222"),
        stroke("mouth", smile, False, "#222222"),
    ], 1, "simple face with open smile", "simple_face"))
    # 06 stick figure
    rng = random.Random(106)
    head = ellipse(256, 140, 28, 28, n=16, rng=rng)
    body = jitter([[256, 170], [256, 300]], rng, 3)
    arm_l = jitter([[256, 210], [200, 250]], rng, 3)
    arm_r = jitter([[256, 210], [320, 245]], rng, 3)
    leg_l = jitter([[256, 300], [220, 380]], rng, 3)
    leg_r = jitter([[256, 300], [295, 385]], rng, 3)
    manifest.append(save("06_stick", [
        stroke("head", head, True, "#333333"),
        stroke("body", body, False, "#333333"),
        stroke("arm_l", arm_l, False, "#333333"),
        stroke("arm_r", arm_r, False, "#333333"),
        stroke("leg_l", leg_l, False, "#333333"),
        stroke("leg_r", leg_r, False, "#333333"),
    ], 1, "stick figure", "stick_figure"))
    # 07 animal-like (cat-ish)
    rng = random.Random(107)
    body = ellipse(256, 280, 90, 60, n=30, rng=rng)
    head = ellipse(256, 190, 55, 50, n=24, rng=rng)
    ear_l = jitter([[220, 160], [200, 110], [245, 150]], rng, 2)
    ear_r = jitter([[290, 160], [320, 115], [270, 150]], rng, 2)
    tail = [[340, 280], [380, 240], [400, 200], [370, 180]]
    tail = jitter(tail, rng, 3)
    manifest.append(save("07_animal", [
        stroke("body", body, True, "#F4A261"),
        stroke("head", head, True, "#F4A261"),
        stroke("ear_l", ear_l, True, "#F4A261"),
        stroke("ear_r", ear_r, True, "#F4A261"),
        stroke("tail", tail, False, "#F4A261"),
    ], 1, "cat-like animal", "animal"))
    # 08 object (mug)
    rng = random.Random(108)
    cup = jitter([[200, 180], [190, 340], [330, 340], [320, 180], [200, 180]], rng, 3)
    handle = [[330, 220], [370, 230], [375, 290], [330, 300]]
    handle = jitter(handle, rng, 2)
    manifest.append(save("08_object", [
        stroke("cup", cup, True, "#A8DADC"),
        stroke("handle", handle, False, "#A8DADC"),
    ], 1, "coffee mug object", "object"))
    # 09 flower
    rng = random.Random(109)
    petals = []
    strokes = []
    for i in range(6):
        a = i * math.pi / 3 + rng.uniform(-0.1, 0.1)
        px = 256 + 70 * math.cos(a)
        py = 220 + 70 * math.sin(a)
        petals.append(stroke(f"p{i}", ellipse(px, py, 35 + rng.uniform(-5, 5), 28, n=16, rng=rng), True, "#E76F51"))
    strokes.extend(petals)
    strokes.append(stroke("center", ellipse(256, 220, 28, 28, n=16, rng=rng), True, "#E9C46A"))
    strokes.append(stroke("stem", jitter([[256, 250], [250, 380]], rng, 2), False, "#2A9D8F"))
    manifest.append(save("09_flower", strokes, 1, "flower with stem", "flower"))
    # 10 open stroke (arc)
    rng = random.Random(110)
    arc = [[120 + i * 12, 300 - 80 * math.sin(i / 22 * math.pi) + rng.uniform(-4, 4)] for i in range(24)]
    manifest.append(save("10_open", [stroke("arc", arc, False, "#9B5DE5")], 1, "open arc stroke", "open_stroke"))
    # 11 scribble
    rng = random.Random(111)
    scrib = []
    x, y = 180, 200
    for i in range(40):
        x += rng.uniform(-25, 35)
        y += rng.uniform(-30, 30)
        scrib.append([min(450, max(60, x)), min(450, max(60, y))])
    manifest.append(save("11_scribble", [stroke("sc", scrib, False, "#333333")], 1, "loose scribble", "scribble"))
    # 12 multiple disconnected
    rng = random.Random(112)
    manifest.append(save("12_multi", [
        stroke("a", ellipse(160, 200, 40, 35, rng=rng), True, "#FF6B6B"),
        stroke("b", ellipse(320, 220, 45, 30, rng=rng), True, "#4ECDC4"),
        stroke("c", ellipse(240, 340, 50, 25, rng=rng), True, "#FFE66D"),
    ], 1, "three disconnected blobs", "multiple_disconnected"))
    # 13 overlapping
    rng = random.Random(113)
    manifest.append(save("13_overlap", [
        stroke("a", ellipse(230, 250, 80, 70, rng=rng), True, "#FF85A1"),
        stroke("b", ellipse(290, 270, 75, 65, rng=rng), True, "#7BDFF2"),
    ], 1, "overlapping blobs", "overlapping"))
    # 14 asymmetrical
    rng = random.Random(114)
    pts = ellipse(256, 256, 100, 80, n=40, rng=rng, wobble=0.2)
    pts = [[p[0] + (40 if p[0] > 256 else -10), p[1] + (30 if p[1] < 256 else 0)] for p in pts]
    manifest.append(save("14_asym", [stroke("s1", pts, True, "#C77DFF")], 1, "strongly asymmetrical form", "asymmetrical"))
    # 15 letter A
    rng = random.Random(115)
    A = jitter([[180, 360], [256, 140], [330, 360]], rng, 3)
    cross = jitter([[210, 280], [300, 280]], rng, 2)
    manifest.append(save("15_letter", [
        stroke("A", A, False, "#222222"),
        stroke("cross", cross, False, "#222222"),
    ], 1, "letter A", "letter"))
    # 16 number 5
    rng = random.Random(116)
    five = jitter([[300, 160], [200, 160], [200, 250], [280, 250], [300, 300], [280, 360], [200, 360]], rng, 3)
    manifest.append(save("16_number", [stroke("five", five, False, "#222222")], 1, "number 5", "number"))
    # 17 tiny
    rng = random.Random(117)
    manifest.append(save("17_tiny", [stroke("t", ellipse(256, 256, 18, 14, n=12, rng=rng), True, "#FF9F1C")], 1, "tiny doodle", "tiny"))
    # 18 detailed
    rng = random.Random(118)
    house = jitter([[160, 300], [160, 200], [256, 130], [350, 200], [350, 300], [160, 300]], rng, 2)
    door = jitter([[230, 300], [230, 240], [280, 240], [280, 300]], rng, 1)
    win = ellipse(200, 220, 18, 18, n=10, rng=rng)
    chimney = jitter([[300, 170], [300, 130], [330, 130], [330, 185]], rng, 2)
    manifest.append(save("18_detailed", [
        stroke("house", house, True, "#8D99AE"),
        stroke("door", door, True, "#EF233C"),
        stroke("win", win, True, "#90E0EF"),
        stroke("chimney", chimney, True, "#8D99AE"),
    ], 1, "detailed house", "detailed"))
    # 19 intentionally messy
    rng = random.Random(119)
    messy = ellipse(256, 256, 100, 90, n=50, rng=rng, wobble=0.35)
    messy = jitter(messy, rng, 8)
    manifest.append(save("19_messy", [stroke("m", messy, True, "#6A4C93")], 1, "intentionally messy closed shape", "messy"))
    # 20 deliberately bad
    rng = random.Random(120)
    bad = [[100, 100], [400, 120], [150, 400], [380, 380], [120, 250], [300, 200]]
    bad = jitter(bad, rng, 15)
    manifest.append(save("20_bad", [stroke("b", bad, True, "#555555")], 1, "deliberately bad self-intersecting-ish polygon", "bad"))

    with MANIFEST.open("w") as f:
        json.dump({"version": "corpus.v1", "count": len(manifest), "doodles": manifest}, f, indent=2)
    print(f"Wrote {len(manifest)} doodles to {OUT}")


if __name__ == "__main__":
    main()
