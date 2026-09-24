"""Studio lighting from recipe — V2 reusable key/fill/rim + AO readability."""
from __future__ import annotations


def _ensure_bpy():
    import bpy
    return bpy


def setup_lighting(recipe: dict):
    bpy = _ensure_bpy()
    cfg = recipe.get("lighting", {})
    world = bpy.data.worlds.new("StudioWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        col = cfg.get("world_color", [1.0, 1.0, 1.0])
        bg.inputs["Color"].default_value = (col[0], col[1], col[2], 1.0)
        bg.inputs["Strength"].default_value = float(cfg.get("world_strength", 0.25))

    target = bpy.data.objects.new("LightTarget", None)
    bpy.context.collection.objects.link(target)
    target.location = (0, 0, 0)

    def add_area(name, spec):
        light_data = bpy.data.lights.new(name=name, type="AREA")
        light_data.energy = float(spec.get("energy", 50))
        light_data.size = float(spec.get("size", 3.0))
        col = spec.get("color", [1, 1, 1])
        light_data.color = (col[0], col[1], col[2])
        # soft shadows for clay/plush readability
        if hasattr(light_data, "use_shadow"):
            light_data.use_shadow = bool(spec.get("shadow", True))
        obj = bpy.data.objects.new(name, light_data)
        loc = spec.get("loc", [2, -2, 3])
        obj.location = (loc[0], loc[1], loc[2])
        bpy.context.collection.objects.link(obj)
        track = obj.constraints.new(type="TRACK_TO")
        track.target = target
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"
        return obj

    for key in ("key", "fill", "rim"):
        if key in cfg:
            add_area(f"Light_{key}", cfg[key])

    # Optional AO / ambient accent light for crevice readability (V2)
    if "ao" in cfg:
        add_area("Light_ao", cfg["ao"])
    elif cfg.get("ao_boost"):
        add_area(
            "Light_ao",
            {
                "energy": float(cfg.get("ao_boost", 15)),
                "size": 6.0,
                "color": [0.9, 0.92, 1.0],
                "loc": [0.0, -2.5, 0.3],
            },
        )
