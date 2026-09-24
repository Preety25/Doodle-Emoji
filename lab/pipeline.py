"""Orchestrate stylization inside Blender."""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Any

from lab import TRANSFORMATION_VERSION
from lab.camera import setup_camera
from lab.export import write_metadata
from lab.geometry import build_geometry, clear_scene
from lab.interpret import interpret_doodle
from lab.lighting import setup_lighting
from lab.materials import assign_materials
from lab.normalize import normalize_doodle
from lab.parse_input import load_stroke_json, validate_stroke_dict
from lab.render import configure_render, render_still
from lab.styles import load_recipe


def run_pipeline(
    doodle_path: str | Path,
    style_id: str,
    style_version: str,
    seed: int,
    output_png: str | Path,
    metadata_path: str | Path | None = None,
    doodle_id: str | None = None,
) -> dict[str, Any]:
    import bpy

    t0 = time.time()
    doodle_path = Path(doodle_path)
    output_png = Path(output_png)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    doodle_id = doodle_id or doodle_path.stem

    meta: dict[str, Any] = {
        "doodle_id": doodle_id,
        "style_id": style_id,
        "style_version": style_version,
        "transformation_version": TRANSFORMATION_VERSION,
        "seed": seed,
        "success": False,
        "error": None,
        "output_path": str(output_png),
        "blender_version": bpy.app.version_string,
    }

    try:
        raw = load_stroke_json(doodle_path)
        raw["seed"] = seed
        recipe = load_recipe(style_id, style_version)
        padding = float(recipe.get("camera", {}).get("padding", 0.15))
        # use half of camera padding for normalize so framing has room
        norm = normalize_doodle(raw, y_flip=True, padding=0.08)
        interp = interpret_doodle(norm)

        clear_scene(bpy)
        objects = build_geometry(interp["components"], recipe)
        assign_materials(objects, recipe)
        setup_lighting(recipe)
        setup_camera(recipe, objects)
        configure_render(recipe, output_png)
        render_still()

        meta["success"] = True
        meta["n_components"] = interp["n_components"]
        meta["n_closed"] = interp["n_closed"]
        meta["n_open"] = interp["n_open"]
        if output_png.exists():
            meta["file_size_bytes"] = output_png.stat().st_size
            meta["width"] = int(recipe.get("render", {}).get("resolution", 1024))
            meta["height"] = meta["width"]
            meta["has_alpha"] = True
    except Exception as e:
        meta["success"] = False
        meta["error"] = f"{e}\n{traceback.format_exc()}"

    meta["render_time_ms"] = int((time.time() - t0) * 1000)
    if metadata_path:
        write_metadata(metadata_path, meta)
    else:
        write_metadata(output_png.with_suffix(".json"), meta)
    return meta
