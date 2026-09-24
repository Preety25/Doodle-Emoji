"""Read-only helpers for V3 semantic blueprints used by V4 rendering.

V4 does not regenerate blueprints; it consumes existing out/v3/*/blueprint.json
files produced by the V3 pipeline. lab/v3/ is never modified from this package.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def blueprint_path(source_id: str, *, root: Path | None = None) -> Path:
    base = root or ROOT
    return base / "out" / "v3" / source_id / "blueprint.json"


def doodle_path(source_id: str, *, root: Path | None = None) -> Path:
    """Prefer A_original.png (V3 raster name)."""
    base = root or ROOT
    folder = base / "out" / "v3" / source_id
    for name in ("A_original.png", "A_original"):
        p = folder / name
        if p.is_file():
            return p
    return folder / "A_original.png"


def load_blueprint(source_id: str, *, root: Path | None = None) -> dict:
    path = blueprint_path(source_id, root=root)
    if not path.is_file():
        raise FileNotFoundError(f"V3 blueprint not found (read-only): {path}")
    return json.loads(path.read_text())
