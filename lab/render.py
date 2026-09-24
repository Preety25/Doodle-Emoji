"""EEVEE still render configuration."""
from __future__ import annotations

from pathlib import Path


def _ensure_bpy():
    import bpy
    return bpy


def configure_render(recipe: dict, output_path: str | Path, resolution: int | None = None):
    bpy = _ensure_bpy()
    scene = bpy.context.scene
    rcfg = recipe.get("render", {})
    engine = rcfg.get("engine", "BLENDER_EEVEE_NEXT")
    # Blender 4.2 uses BLENDER_EEVEE_NEXT
    try:
        scene.render.engine = engine
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"

    res = int(resolution or rcfg.get("resolution", 1024))
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = bool(rcfg.get("film_transparent", True))
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.filepath = str(output_path)

    # EEVEE samples
    samples = int(rcfg.get("samples", 64))
    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = samples
        if hasattr(scene.eevee, "use_bloom"):
            scene.eevee.use_bloom = bool(rcfg.get("bloom", False))
        # SSS / raytracing toggles when available
        for attr, val in (
            ("use_raytracing", True),
            ("use_shadows", True),
        ):
            if hasattr(scene.eevee, attr):
                try:
                    setattr(scene.eevee, attr, val)
                except Exception:
                    pass
    # Prefer punchier sticker look under EEVEE software GL
    if hasattr(scene.view_settings, "exposure"):
        scene.view_settings.exposure = 0.4
    if hasattr(scene.view_settings, "gamma"):
        scene.view_settings.gamma = 1.0
    if hasattr(scene.view_settings, "view_transform"):
        try:
            scene.view_settings.view_transform = "Standard"
        except Exception:
            pass
    return scene


def render_still():
    bpy = _ensure_bpy()
    bpy.ops.render.render(write_still=True)
