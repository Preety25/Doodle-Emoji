"""Optional stroke-JSON → PNG raster via lab.v3 helper (thin wrap)."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any


def strokes_to_png_bytes(strokes: dict[str, Any], *, size: int = 1024) -> bytes:
    """Rasterize stroke JSON to PNG bytes using ``lab.v3.raster.rasterize_doodle``."""
    from lab.v3.raster import rasterize_doodle

    with tempfile.TemporaryDirectory(prefix="dooji_raster_") as tmp:
        src = Path(tmp) / "strokes.json"
        out = Path(tmp) / "doodle.png"
        src.write_text(json.dumps(strokes), encoding="utf-8")
        rasterize_doodle(src, out, size=size)
        return out.read_bytes()
