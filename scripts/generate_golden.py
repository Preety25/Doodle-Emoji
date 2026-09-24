"""Generate golden-12 imperfect human-like doodles + preview PNGs + plan stubs."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus" / "golden"
CANVAS = {"width": 512, "height": 512}


def jitter(pts, rng, amp=3.0):
    return [[p[0] + rng.uniform(-amp, amp), p[1] + rng.uniform(-amp, amp)] for p in pts]


def ellipse(cx, cy, rx, ry, n=40, rng=None, wobble=0.1):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        wr = 1.0 + (rng.uniform(-wobble, wobble) if rng else 0)
        pts.append([cx + rx * wr * math.cos(a), cy + ry * wr * math.sin(a)])
    return pts


def heart(cx, cy, s=95, n=52, rng=None):
    pts, raw = [], []
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
            px += rng.uniform(-3.5, 3.5)
            py += rng.uniform(-3.5, 3.5)
        pts.append([px, py])
    return pts


def star(cx, cy, r_out=105, r_in=42, points=5, rng=None):
    pts = []
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        r = r_out if i % 2 == 0 else r_in
        if rng:
            r *= 1 + rng.uniform(-0.14, 0.14)
            ang += rng.uniform(-0.1, 0.1)
        pts.append([cx + r * math.cos(ang), cy + r * math.sin(ang)])
    return pts


def stroke(sid, points, closed=True, color="#FF6699"):
    return {
        "id": sid,
        "points": [[round(p[0], 2), round(p[1], 2)] for p in points],
        "closed": closed,
        "color": color,
        "pressure": None,
    }


def save_doodle(doodle_id, strokes, seed, description, category):
    data = {
        "canvas": CANVAS,
        "strokes": strokes,
        "seed": seed,
        "meta": {"description": description, "category": category, "corpus": "golden"},
    }
    path = OUT / f"{doodle_id}.json"
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    return data, path


def save_preview(doodle_id, data):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    im = Image.new("RGBA", (512, 512), (250, 250, 252, 255))
    draw = ImageDraw.Draw(im)
    for s in data["strokes"]:
        pts = [(p[0], p[1]) for p in s["points"]]
        col = s.get("color") or "#333333"
        if s.get("closed") and len(pts) >= 3:
            draw.line(pts + [pts[0]], fill=col, width=3)
            try:
                draw.polygon(pts, outline=col)
            except Exception:
                pass
        else:
            if len(pts) >= 2:
                draw.line(pts, fill=col, width=4)
    p = OUT / f"{doodle_id}_preview.png"
    im.save(p)
    return p


def plan_stub(subject, confidence, completion_budget, transform_mode="polish"):
    return {
        "subject": subject,
        "confidence": confidence,
        "completion_budget": completion_budget,
        "transform_mode": transform_mode,
        "planner": "heuristic_v2_stub",
        "notes": "Filled by lab.semantic_plan at runtime; stub mirrors expected cues.",
    }


def build_all():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = []

    # 01 blob — ambiguous organic closed shape
    rng = random.Random(101)
    pts = ellipse(255, 260, 110, 90, n=44, rng=rng, wobble=0.18)
    pts = jitter(pts, rng, 4)
    data, _ = save_doodle("01_blob", [stroke("s1", pts, True, "#7EC8E3")], 101, "messy organic blob", "blob")
    save_preview("01_blob", data)
    (OUT / "01_blob.plan.json").write_text(json.dumps(plan_stub("blob", "LOW", 0), indent=2))
    entries.append({"id": "01_blob", "category": "blob", "path": "corpus/golden/01_blob.json"})

    # 02 heart
    rng = random.Random(102)
    pts = heart(250, 255, s=100, n=56, rng=rng)
    # slight left lean asymmetry
    pts = [[p[0] - 6 if p[0] < 250 else p[0] + 2, p[1]] for p in pts]
    data, _ = save_doodle("02_heart", [stroke("s1", pts, True, "#FF4D6D")], 102, "wonky asymmetric heart", "heart")
    save_preview("02_heart", data)
    (OUT / "02_heart.plan.json").write_text(json.dumps(plan_stub("heart", "HIGH", 1), indent=2))
    entries.append({"id": "02_heart", "category": "heart", "path": "corpus/golden/02_heart.json"})

    # 03 star
    rng = random.Random(103)
    pts = star(256, 250, r_out=108, r_in=44, points=5, rng=rng)
    data, _ = save_doodle("03_star", [stroke("s1", pts, True, "#FFD166")], 103, "wonky 5-point star", "star")
    save_preview("03_star", data)
    (OUT / "03_star.plan.json").write_text(json.dumps(plan_stub("star", "HIGH", 1), indent=2))
    entries.append({"id": "03_star", "category": "star", "path": "corpus/golden/03_star.json"})

    # 04 face — circle + two eye dots + smile arc (user-drawn face)
    rng = random.Random(104)
    head = ellipse(256, 240, 95, 100, n=48, rng=rng, wobble=0.06)
    eye_l = ellipse(220, 220, 10, 12, n=12, rng=rng, wobble=0.05)
    eye_r = ellipse(292, 218, 11, 12, n=12, rng=rng, wobble=0.05)
    smile = [[210 + i * 8, 280 + 18 * math.sin(i / 12 * math.pi)] for i in range(13)]
    smile = jitter(smile, rng, 2.0)
    data, _ = save_doodle(
        "04_face",
        [
            stroke("head", head, True, "#FFE08A"),
            stroke("eye_l", eye_l, True, "#333333"),
            stroke("eye_r", eye_r, True, "#333333"),
            stroke("smile", smile, False, "#333333"),
        ],
        104,
        "simple face with smile",
        "face",
    )
    save_preview("04_face", data)
    (OUT / "04_face.plan.json").write_text(json.dumps(plan_stub("face", "HIGH", 1), indent=2))
    entries.append({"id": "04_face", "category": "face", "path": "corpus/golden/04_face.json"})

    # 05 plant — pot + stem + leaves
    rng = random.Random(105)
    pot = [[200, 340], [210, 400], [300, 400], [310, 340], [200, 340]]
    pot = jitter(pot[:-1], rng, 3) + [jitter(pot[:-1], rng, 0)[0]]
    stem = jitter([[255, 340], [258, 280], [252, 220], [256, 170]], rng, 2.5)
    leaf_l = ellipse(220, 200, 35, 18, n=20, rng=rng)
    leaf_r = ellipse(295, 185, 32, 16, n=20, rng=rng)
    data, _ = save_doodle(
        "05_plant",
        [
            stroke("pot", pot, True, "#C4A484"),
            stroke("stem", stem, False, "#4CAF50"),
            stroke("leaf_l", leaf_l, True, "#66BB6A"),
            stroke("leaf_r", leaf_r, True, "#43A047"),
        ],
        105,
        "potted plant with two leaves",
        "plant",
    )
    save_preview("05_plant", data)
    (OUT / "05_plant.plan.json").write_text(json.dumps(plan_stub("plant", "HIGH", 1), indent=2))
    entries.append({"id": "05_plant", "category": "plant", "path": "corpus/golden/05_plant.json"})

    # 06 rocket — body + fins + nose + window
    rng = random.Random(106)
    body = [[230, 360], [235, 200], [256, 150], [277, 200], [282, 360], [230, 360]]
    body = jitter(body[:-1], rng, 3) 
    body.append(body[0][:])
    fin_l = jitter([[230, 320], [190, 370], [230, 350]], rng, 2)
    fin_r = jitter([[282, 320], [322, 370], [282, 350]], rng, 2)
    window = ellipse(256, 230, 18, 20, n=16, rng=rng, wobble=0.05)
    data, _ = save_doodle(
        "06_rocket",
        [
            stroke("body", body, True, "#90CAF9"),
            stroke("fin_l", fin_l, True, "#EF5350"),
            stroke("fin_r", fin_r, True, "#EF5350"),
            stroke("window", window, True, "#BBDEFB"),
        ],
        106,
        "simple rocket with fins and window",
        "rocket",
    )
    save_preview("06_rocket", data)
    (OUT / "06_rocket.plan.json").write_text(json.dumps(plan_stub("rocket", "HIGH", 1), indent=2))
    entries.append({"id": "06_rocket", "category": "rocket", "path": "corpus/golden/06_rocket.json"})

    # 07 teddy — round body + head + ear bumps + eyes
    rng = random.Random(107)
    body = ellipse(256, 300, 80, 70, n=36, rng=rng, wobble=0.08)
    head = ellipse(256, 200, 55, 50, n=32, rng=rng, wobble=0.07)
    ear_l = ellipse(210, 160, 22, 20, n=16, rng=rng)
    ear_r = ellipse(302, 158, 22, 20, n=16, rng=rng)
    eye_l = ellipse(238, 195, 7, 8, n=10, rng=rng)
    eye_r = ellipse(274, 195, 7, 8, n=10, rng=rng)
    data, _ = save_doodle(
        "07_teddy",
        [
            stroke("body", body, True, "#D7A86E"),
            stroke("head", head, True, "#D7A86E"),
            stroke("ear_l", ear_l, True, "#C48A4A"),
            stroke("ear_r", ear_r, True, "#C48A4A"),
            stroke("eye_l", eye_l, True, "#333333"),
            stroke("eye_r", eye_r, True, "#333333"),
        ],
        107,
        "teddy-like round bear",
        "teddy",
    )
    save_preview("07_teddy", data)
    (OUT / "07_teddy.plan.json").write_text(json.dumps(plan_stub("teddy", "HIGH", 2), indent=2))
    entries.append({"id": "07_teddy", "category": "teddy", "path": "corpus/golden/07_teddy.json"})

    # 08 flower — center + petals + stem
    rng = random.Random(108)
    center = ellipse(256, 200, 28, 28, n=20, rng=rng)
    petals = []
    for i in range(6):
        a = i * math.pi / 3
        cx = 256 + 55 * math.cos(a)
        cy = 200 + 55 * math.sin(a)
        petals.append(stroke(f"petal_{i}", ellipse(cx, cy, 28, 18, n=16, rng=rng), True, "#F48FB1"))
    stem = jitter([[256, 230], [258, 300], [254, 380]], rng, 2)
    data, _ = save_doodle(
        "08_flower",
        [stroke("center", center, True, "#FFEB3B"), *petals, stroke("stem", stem, False, "#66BB6A")],
        108,
        "six-petal flower with stem",
        "flower",
    )
    save_preview("08_flower", data)
    (OUT / "08_flower.plan.json").write_text(json.dumps(plan_stub("flower", "HIGH", 1), indent=2))
    entries.append({"id": "08_flower", "category": "flower", "path": "corpus/golden/08_flower.json"})

    # 09 rose — spiral-ish overlapping lobes + leaf
    rng = random.Random(109)
    spiral = []
    for i in range(60):
        t = i / 60 * 3.2 * math.pi
        r = 12 + t * 12
        spiral.append([256 + r * math.cos(t), 230 + r * math.sin(t) * 0.9])
    spiral = jitter(spiral, rng, 2.5)
    # close spiral blob loosely
    outer = ellipse(256, 230, 70, 65, n=36, rng=rng, wobble=0.12)
    leaf = ellipse(320, 300, 40, 18, n=18, rng=rng)
    stem = jitter([[256, 295], [260, 360], [255, 400]], rng, 2)
    data, _ = save_doodle(
        "09_rose",
        [
            stroke("bloom", outer, True, "#E53935"),
            stroke("spiral", spiral, False, "#C62828"),
            stroke("leaf", leaf, True, "#43A047"),
            stroke("stem", stem, False, "#2E7D32"),
        ],
        109,
        "rose-like bloom with spiral cue and leaf",
        "rose",
    )
    save_preview("09_rose", data)
    (OUT / "09_rose.plan.json").write_text(json.dumps(plan_stub("rose", "MEDIUM", 1), indent=2))
    entries.append({"id": "09_rose", "category": "rose", "path": "corpus/golden/09_rose.json"})

    # 10 open_stroke — single open arc / swoosh
    rng = random.Random(110)
    arc = [[120 + i * 12, 280 - 80 * math.sin(i / 22 * math.pi) + rng.uniform(-4, 4)] for i in range(23)]
    data, _ = save_doodle("10_open_stroke", [stroke("arc", arc, False, "#7E57C2")], 110, "open swoosh stroke", "open_stroke")
    save_preview("10_open_stroke", data)
    (OUT / "10_open_stroke.plan.json").write_text(json.dumps(plan_stub("open_stroke", "LOW", 0), indent=2))
    entries.append({"id": "10_open_stroke", "category": "open_stroke", "path": "corpus/golden/10_open_stroke.json"})

    # 11 multi_part — three disconnected blobs
    rng = random.Random(111)
    a = ellipse(160, 220, 45, 40, n=24, rng=rng)
    b = ellipse(300, 200, 50, 35, n=24, rng=rng)
    c = ellipse(240, 340, 40, 45, n=24, rng=rng)
    data, _ = save_doodle(
        "11_multi_part",
        [
            stroke("a", a, True, "#FF8A65"),
            stroke("b", b, True, "#4FC3F7"),
            stroke("c", c, True, "#AED581"),
        ],
        111,
        "three disconnected colored blobs",
        "multi_part",
    )
    save_preview("11_multi_part", data)
    (OUT / "11_multi_part.plan.json").write_text(json.dumps(plan_stub("multi_part", "MEDIUM", 0), indent=2))
    entries.append({"id": "11_multi_part", "category": "multi_part", "path": "corpus/golden/11_multi_part.json"})

    # 12 messy_incomplete — partial star-ish + broken lines (incomplete)
    rng = random.Random(112)
    partial = star(250, 240, r_out=100, r_in=40, points=5, rng=rng)[:7]  # incomplete
    scribble = jitter([[180, 320], [220, 300], [260, 330], [300, 290], [340, 340]], rng, 5)
    orphan = ellipse(360, 180, 20, 15, n=10, rng=rng)
    data, _ = save_doodle(
        "12_messy_incomplete",
        [
            stroke("partial", partial, False, "#AB47BC"),
            stroke("scribble", scribble, False, "#AB47BC"),
            stroke("orphan", orphan, True, "#CE93D8"),
        ],
        112,
        "messy incomplete star-like strokes",
        "messy_incomplete",
    )
    save_preview("12_messy_incomplete", data)
    (OUT / "12_messy_incomplete.plan.json").write_text(json.dumps(plan_stub("messy_incomplete", "LOW", 0), indent=2))
    entries.append({"id": "12_messy_incomplete", "category": "messy_incomplete", "path": "corpus/golden/12_messy_incomplete.json"})

    man = {"version": "golden.v2", "count": len(entries), "doodles": entries}
    (OUT / "manifest.json").write_text(json.dumps(man, indent=2))
    print(f"Wrote {len(entries)} golden doodles to {OUT}")
    return man


if __name__ == "__main__":
    build_all()
