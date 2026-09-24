"""Fixed studio 3-point lighting from recipe."""
from __future__ import annotations


def _ensure_bpy():
    import bpy
    return bpy


def setup_lighting(recipe: dict):
    bpy = _ensure_bpy()
    cfg = recipe.get("lighting", {})
    # World soft fill
    world = bpy.data.worlds.new("StudioWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        bg.inputs["Strength"].default_value = float(cfg.get("world_strength", 0.2))

    def add_area(name, spec):
        light_data = bpy.data.lights.new(name=name, type="AREA")
        light_data.energy = float(spec.get("energy", 50))
        light_data.size = float(spec.get("size", 3.0))
        col = spec.get("color", [1, 1, 1])
        light_data.color = (col[0], col[1], col[2])
        obj = bpy.data.objects.new(name, light_data)
        loc = spec.get("loc", [2, -2, 3])
        obj.location = (loc[0], loc[1], loc[2])
        # point toward origin
        import math
        direction = (
            -loc[0],
            -loc[1],
            -loc[2],
        )
        # track to origin
        bpy.context.collection.objects.link(obj)
        # constrain
        track = obj.constraints.new(type="TRACK_TO")
        # need empty at origin
        return obj

    # empty target
    target = bpy.data.objects.new("LightTarget", None)
    bpy.context.collection.objects.link(target)
    target.location = (0, 0, 0)

    for key in ("key", "fill", "rim"):
        if key in cfg:
            obj = add_area(f"Light_{key}", cfg[key])
            track = obj.constraints.new(type="TRACK_TO")
            track.target = target
            track.track_axis = "TRACK_NEGATIVE_Z"
            track.up_axis = "UP_Y"
