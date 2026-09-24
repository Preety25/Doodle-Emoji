"""Parse and lightly validate stroke JSON input."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_stroke_json(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return validate_stroke_dict(data)


def validate_stroke_dict(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("stroke JSON must be an object")
    canvas = data.get("canvas")
    if not isinstance(canvas, dict) or "width" not in canvas or "height" not in canvas:
        raise ValueError("canvas.width and canvas.height required")
    strokes = data.get("strokes")
    if not isinstance(strokes, list) or len(strokes) == 0:
        raise ValueError("strokes must be a non-empty array")
    for i, s in enumerate(strokes):
        if "id" not in s:
            s["id"] = f"s{i}"
        pts = s.get("points")
        if not isinstance(pts, list) or len(pts) < 2:
            raise ValueError(f"stroke {s['id']} needs >=2 points")
        for p in pts:
            if not (isinstance(p, (list, tuple)) and len(p) >= 2):
                raise ValueError(f"bad point in stroke {s['id']}")
        if "closed" not in s:
            s["closed"] = False
        if "color" not in s:
            s["color"] = None
    if "seed" not in data:
        data["seed"] = 1
    return data


def hex_to_rgba(color: str | None, fallback=(1.0, 0.5, 0.7, 1.0)):
    if not color or not isinstance(color, str):
        return list(fallback)
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    if len(c) != 6:
        return list(fallback)
    r = int(c[0:2], 16) / 255.0
    g = int(c[2:4], 16) / 255.0
    b = int(c[4:6], 16) / 255.0
    return [r, g, b, 1.0]
