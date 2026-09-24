"""Objective checks. They do not replace looking at the picture."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def _load(path: Path):
    im = Image.open(path).convert("RGBA")
    return np.asarray(im)


def alpha_stats(path: Path) -> dict:
    arr = _load(path)
    a = arr[..., 3]
    h, w = a.shape
    ys, xs = np.where(a > 12)
    if len(xs) == 0:
        return {"empty": True, "touch_border": False, "fill": 0.0, "span": 0.0}
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    touch = x0 <= 1 or y0 <= 1 or x1 >= w - 2 or y1 >= h - 2
    span = max(x1 - x0, y1 - y0) / float(max(w, h))
    fill = float((a > 12).mean())
    return {
        "empty": False,
        "touch_border": bool(touch),
        "fill": round(fill, 4),
        "span": round(span, 4),
        "bounds": [x0, y0, x1, y1],
    }


def horizontal_band_score(path: Path) -> float:
    """Std-dev of row-mean luminance after a wide blur.

    High values mean the interior brightness flickers row to row (ripple / stripe).
    A smooth dome highlight scores low because the moving average removes it.
    """
    arr = _load(path).astype("float32")
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    a = arr[..., 3] > 20
    h, w = lum.shape
    row = np.full(h, np.nan, dtype="float32")
    for y in range(h):
        m = a[y]
        if int(m.sum()) > w * 0.08:
            row[y] = lum[y, m].mean()
    valid = ~np.isnan(row)
    if int(valid.sum()) < 32:
        return 0.0
    filled = row.copy()
    filled[~valid] = np.nanmean(row)
    k = 21
    kernel = np.ones(k, dtype="float32") / k
    smooth = np.convolve(filled, kernel, mode="same")
    resid = (filled - smooth)[valid]
    return float(np.std(resid))


def mean_color(path: Path) -> list[float]:
    arr = _load(path).astype("float32")
    m = arr[..., 3] > 20
    if not np.any(m):
        return [0, 0, 0]
    rgb = arr[..., :3][m].mean(axis=0)
    return [round(float(c), 1) for c in rgb]


def judge_example(folder: Path) -> dict:
    panels = {
        "C_gummy": folder / "C_gummy.png",
        "D_clay": folder / "D_clay.png",
        "E_plush": folder / "E_plush.png",
        "F_glossy": folder / "F_glossy.png",
    }
    out = {"folder": str(folder), "panels": {}}
    for name, path in panels.items():
        if not path.exists():
            out["panels"][name] = {"missing": True}
            continue
        stats = alpha_stats(path)
        stats["band_score"] = round(horizontal_band_score(path), 3)
        stats["mean_rgb"] = mean_color(path)
        stats["missing"] = False
        out["panels"][name] = stats
    # plush should cover more pixels than clay if the pile shell is real
    clay = out["panels"].get("D_clay") or {}
    plush = out["panels"].get("E_plush") or {}
    if not clay.get("missing") and not plush.get("missing") and "fill" in clay and "fill" in plush:
        out["plush_fill_minus_clay"] = round(plush["fill"] - clay["fill"], 4)
    glossy = out["panels"].get("F_glossy") or {}
    gummy = out["panels"].get("C_gummy") or {}
    if glossy.get("mean_rgb") and clay.get("mean_rgb"):
        out["clay_vs_glossy_luma"] = round(
            abs(sum(glossy["mean_rgb"]) - sum(clay["mean_rgb"])) / 3.0,
            2,
        )
    if gummy.get("band_score") is not None:
        out["max_band_score"] = max(
            p.get("band_score") or 0 for p in out["panels"].values() if not p.get("missing")
        )
    return out
