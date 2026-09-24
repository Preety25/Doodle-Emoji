"""Rasterize the original doodle (panel A). Canvas Y-down, source colors."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


def _parse_color(c):
    if not c:
        return (40, 40, 50, 255)
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4)) + (255,)


def rasterize_doodle(doodle_path: str | Path, out_png: str | Path, size: int = 1024) -> Path:
    data = json.loads(Path(doodle_path).read_text())
    w = float(data["canvas"]["width"])
    h = float(data["canvas"]["height"])
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    sx, sy = size / w, size / h
    # pad the drawing slightly by drawing into a fitted box — keep canvas mapping
    # so the preview matches the source framing, then the contact sheet letterboxes.
    strokes = data["strokes"]
    # line width scales with stroke role
    for s in strokes:
        pts = [(p[0] * sx, p[1] * sy) for p in s["points"]]
        col = _parse_color(s.get("color"))
        if len(pts) < 2:
            continue
        width = max(8, size // 70)
        if s.get("closed") and len(pts) >= 3:
            draw.polygon(pts, fill=col)
            draw.line(pts + [pts[0]], fill=col, width=max(3, size // 180))
        else:
            draw.line(pts, fill=col, width=width, joint="curve")
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out
