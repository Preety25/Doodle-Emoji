"""Load versioned style recipes (renderer-agnostic JSON)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECIPES_DIR = ROOT / "recipes"


def recipe_path(style_id: str, style_version: str = "v1") -> Path:
    ver = style_version.lstrip("v")
    # accept "v1" or "1"
    name = f"{style_id}.v{ver}.json" if not style_version.startswith("v") else f"{style_id}.{style_version}.json"
    # normalize: style_id.v1.json
    candidates = [
        RECIPES_DIR / f"{style_id}.{style_version}.json",
        RECIPES_DIR / f"{style_id}.v{ver}.json",
        RECIPES_DIR / name,
    ]
    for c in candidates:
        if c.exists():
            return c
    # default pattern style.v1.json
    p = RECIPES_DIR / f"{style_id}.v1.json"
    if p.exists():
        return p
    raise FileNotFoundError(f"No recipe for {style_id} {style_version}; tried {candidates}")


def load_recipe(style_id: str, style_version: str = "v1") -> dict[str, Any]:
    path = recipe_path(style_id, style_version)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data["_recipe_path"] = str(path)
    return data


def list_recipes() -> list[str]:
    return sorted(p.stem for p in RECIPES_DIR.glob("*.json"))
