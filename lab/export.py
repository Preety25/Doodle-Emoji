"""Export master PNG + derivatives + metadata."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def write_metadata(path: str | Path, meta: dict[str, Any]):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def make_derivatives_pillow(master_png: Path, out_dir: Path, stem: str) -> dict:
    """Create 512 / 256 / 128 derivatives. Prefer Pillow; fall back to note."""
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    try:
        from PIL import Image
    except ImportError:
        results["error"] = "Pillow not installed"
        return results
    im = Image.open(master_png).convert("RGBA")
    for size in (512, 256, 128):
        # fit inside size×size preserving aspect of alpha bbox-ish: just thumbnail
        d = im.copy()
        d.thumbnail((size, size), Image.Resampling.LANCZOS)
        # pad to exact square
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ox = (size - d.width) // 2
        oy = (size - d.height) // 2
        canvas.paste(d, (ox, oy), d)
        p = out_dir / f"{stem}_{size}.png"
        canvas.save(p, "PNG")
        results[str(size)] = str(p)
    return results
