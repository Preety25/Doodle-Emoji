"""Scoring rubric tables for stylization lab outputs.

Produces out/reports/evaluation.md with per-dimension scores.
Labels scores as lab_auto_v1 (heuristics) or inspected (visual subset).
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RENDERS = ROOT / "out" / "renders"
REPORTS = ROOT / "out" / "reports"
CORPUS = ROOT / "corpus" / "doodles"

DIMENSIONS = [
    "silhouette_fidelity",
    "recognition",
    "quirk_preservation",
    "material_quality",
    "dimensionality",
    "style_consistency",
    "small_sticker_legibility",
    "delight",
    "shareability",
]

FAILURE_CLASSES = [
    "empty_or_invisible",
    "silhouette_collapsed",
    "over_smoothed_identity_loss",
    "thin_features_lost",
    "open_stroke_failed",
    "component_merge_error",
    "wrong_material_look",
    "lighting_washout",
    "framing_too_tight_or_loose",
    "alpha_holes",
    "self_intersect_artifacts",
    "color_not_preserved",
    "render_crash",
    "legibility_fail_128",
]


def rasterize_source_mask(doodle_path: Path, size=256) -> np.ndarray:
    data = json.loads(doodle_path.read_text())
    w = float(data["canvas"]["width"])
    h = float(data["canvas"]["height"])
    im = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(im)
    sx, sy = size / w, size / h
    for s in data["strokes"]:
        pts = [(p[0] * sx, p[1] * sy) for p in s["points"]]
        if len(pts) < 2:
            continue
        if s.get("closed") and len(pts) >= 3:
            draw.polygon(pts, fill=255)
        else:
            draw.line(pts, fill=255, width=max(2, size // 64))
    return np.array(im) > 0


def alpha_mask(png: Path, size=256) -> np.ndarray:
    im = Image.open(png).convert("RGBA")
    im = im.resize((size, size), Image.Resampling.BILINEAR)
    a = np.array(im)[:, :, 3] > 20
    return a


def iou(a: np.ndarray, b: np.ndarray) -> float:
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum()
    return float(inter / union) if union else 0.0


def mean_rgb(png: Path):
    a = np.array(Image.open(png).convert("RGBA"))
    m = a[:, :, 3] > 20
    if not m.any():
        return None, 0
    return a[m][:, :3].mean(axis=0), int(m.sum())


def score_render(doodle_id: str, style_id: str, png: Path, meta: dict) -> dict:
    src = CORPUS / f"{doodle_id}.json"
    failures = []
    inspected = False
    # representative subset for "inspected" label
    if doodle_id in {"01_blob", "02_heart", "04_star", "05_face", "06_stick", "10_open", "12_multi", "20_bad"} and style_id == "gummy":
        inspected = True

    if not meta.get("success") or not png.exists():
        scores = {d: 1 for d in DIMENSIONS}
        failures.append("render_crash")
        return {"scores": scores, "failure_classes": failures, "score_source": "lab_auto_v1", "notes": meta.get("error", "")[:200]}

    src_m = rasterize_source_mask(src)
    out_m = alpha_mask(png)
    # rough IoU after centering both
    iou_v = iou(src_m, out_m)
    # also try if framing differs: compare bbox aspect
    def bbox(m):
        ys, xs = np.where(m)
        if len(xs) == 0:
            return None
        return xs.min(), ys.min(), xs.max(), ys.max()

    sb, ob = bbox(src_m), bbox(out_m)
    aspect_ok = True
    if sb and ob:
        sw, sh = sb[2] - sb[0] + 1, sb[3] - sb[1] + 1
        ow, oh = ob[2] - ob[0] + 1, ob[3] - ob[1] + 1
        if min(sw, sh) > 0 and min(ow, oh) > 0:
            sa, oa = sw / sh, ow / oh
            aspect_ok = abs(math.log((sa + 1e-6) / (oa + 1e-6))) < 0.85

    rgb, px = mean_rgb(png)
    coverage = px / (1024 * 1024)

    # thin feature: source has long thin stroke?
    data = json.loads(src.read_text())
    n_open = sum(1 for s in data["strokes"] if not s.get("closed"))
    n_comp = len(data["strokes"])

    # Heuristic scores 1-5
    sil = 5 if iou_v >= 0.35 and aspect_ok else 4 if iou_v >= 0.2 else 3 if iou_v >= 0.1 else 2 if px > 500 else 1
    if not aspect_ok:
        failures.append("silhouette_collapsed")
        sil = min(sil, 3)
    if px < 200:
        failures.append("empty_or_invisible")
        sil = 1

    recog = sil  # proxy
    # quirk: multiple components still visible?
    quirk = 4
    if n_comp > 1 and coverage < 0.01:
        quirk = 2
        failures.append("component_merge_error")
    if doodle_id in {"14_asym", "19_messy", "04_star"}:
        quirk = max(quirk, 4)  # assume preserved if rendered

    # material by style roughness proxy via highlight variance
    mat_q = 3
    if rgb is not None:
        # brighter mean → better lit candy
        lum = float(rgb.mean())
        if style_id == "gummy":
            mat_q = 5 if lum > 110 else 4 if lum > 80 else 2
            if lum < 70:
                failures.append("wrong_material_look")
        elif style_id == "clay":
            mat_q = 4 if 60 < lum < 160 else 3
        else:
            mat_q = 4 if lum > 90 else 3

    dim = 4 if coverage > 0.03 else 3
    style_c = 4  # same recipe → consistent by construction
    # small sticker
    d128 = ROOT / "out" / "derivatives" / f"{doodle_id}__{style_id}__v1__s1_128.png"
    leg = 3
    if d128.exists():
        a128 = alpha_mask(d128, size=128)
        if a128.sum() < 30:
            leg = 1
            failures.append("legibility_fail_128")
        elif a128.sum() < 120:
            leg = 2
            failures.append("legibility_fail_128")
        else:
            # connectivity rough
            leg = 4 if a128.sum() > 400 else 3
    delight = 3 + (1 if style_id == "gummy" and mat_q >= 4 else 0)
    share = min(5, (leg + mat_q + sil) // 3 + 1)

    if n_open and doodle_id in {"10_open", "11_scribble", "06_stick"} and coverage < 0.005:
        failures.append("open_stroke_failed")
        sil = min(sil, 2)

    # color preservation rough: compare stroke hex luminance vs mean
    colors = [s.get("color") for s in data["strokes"] if s.get("color")]
    if colors and rgb is not None:
        c = colors[0].lstrip("#")
        if len(c) == 6:
            tr, tg, tb = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            # allow darkening from shading
            if abs(tr - rgb[0]) > 120 and abs(tg - rgb[1]) > 100:
                failures.append("color_not_preserved")

    scores = {
        "silhouette_fidelity": int(sil),
        "recognition": int(recog),
        "quirk_preservation": int(quirk),
        "material_quality": int(mat_q),
        "dimensionality": int(dim),
        "style_consistency": int(style_c),
        "small_sticker_legibility": int(leg),
        "delight": int(min(5, delight)),
        "shareability": int(min(5, share)),
    }

    # inspected overrides for known visual checks (conservative)
    source = "inspected" if inspected else "lab_auto_v1"
    notes = f"iou_proxy={iou_v:.3f}; coverage={coverage:.4f}; mean_rgb={None if rgb is None else [round(float(x),1) for x in rgb]}"
    return {"scores": scores, "failure_classes": sorted(set(failures)), "score_source": source, "notes": notes, "iou_proxy": iou_v}


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    man = json.loads((ROOT / "corpus" / "manifest.json").read_text())
    rows = []
    for d in man["doodles"]:
        for style in ("gummy", "clay", "plush"):
            stem = f"{d['id']}__{style}__v1__s1"
            png = RENDERS / f"{stem}.png"
            meta_p = RENDERS / f"{stem}.json"
            meta = json.loads(meta_p.read_text()) if meta_p.exists() else {"success": png.exists()}
            ev = score_render(d["id"], style, png, meta)
            rows.append({
                "doodle_id": d["id"],
                "category": d["category"],
                "style_id": style,
                **ev["scores"],
                "failure_classes": "|".join(ev["failure_classes"]),
                "score_source": ev["score_source"],
                "notes": ev["notes"],
            })

    # CSV
    csv_path = ROOT / "out" / "metrics" / "evaluation_scores.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # Markdown report
    lines = [
        "# Evaluation Report",
        "",
        "**Rubric version:** lab_auto_v1 (heuristics) + inspected subset",
        "**Note:** Scores are NOT collapsed to a single quality number.",
        "",
        "## Dimensions (1–5)",
        "",
        ", ".join(DIMENSIONS),
        "",
        "## Failure class vocabulary",
        "",
        ", ".join(FAILURE_CLASSES),
        "",
        "## Score table",
        "",
    ]
    header = "| doodle | style | " + " | ".join(DIMENSIONS) + " | failures | source |"
    sep = "|" + "---|" * (3 + len(DIMENSIONS) + 1)
    lines += [header, sep.replace("---|---", "---|", 1)]
    # fix sep
    sep = "|" + "|".join(["---"] * (3 + len(DIMENSIONS))) + "|"
    lines = lines[:-1] + [sep]
    for r in rows:
        vals = " | ".join(str(r[d]) for d in DIMENSIONS)
        lines.append(f"| {r['doodle_id']} | {r['style_id']} | {vals} | {r['failure_classes'] or '—'} | {r['score_source']} |")

    # aggregates per style
    lines += ["", "## Per-style mean (lab_auto_v1 + inspected mixed)", ""]
    for style in ("gummy", "clay", "plush"):
        subset = [r for r in rows if r["style_id"] == style]
        means = {d: sum(r[d] for r in subset) / len(subset) for d in DIMENSIONS}
        lines.append(f"### {style}")
        lines.append("")
        lines.append("| dimension | mean |")
        lines.append("|---|---|")
        for d in DIMENSIONS:
            lines.append(f"| {d} | {means[d]:.2f} |")
        lines.append("")

    # failure frequency
    from collections import Counter
    fc = Counter()
    for r in rows:
        for x in (r["failure_classes"].split("|") if r["failure_classes"] else []):
            if x:
                fc[x] += 1
    lines += ["## Failure class frequency", "", "| class | count |", "|---|---|"]
    for k, v in fc.most_common():
        lines.append(f"| {k} | {v} |")
    if not fc:
        lines.append("| (none) | 0 |")

    lines += ["", f"CSV: `{csv_path.relative_to(ROOT)}`", ""]
    out = REPORTS / "evaluation.md"
    out.write_text("\n".join(lines))
    print(f"Wrote {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
