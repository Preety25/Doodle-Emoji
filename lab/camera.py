"""Camera and framing from recipe."""
from __future__ import annotations

import math


def _ensure_bpy():
    import bpy
    return bpy


def setup_camera(recipe: dict, objects: list | None = None):
    bpy = _ensure_bpy()
    cfg = recipe.get("camera", {})
    cam_data = bpy.data.cameras.new("HeroCam")
    cam_data.lens = float(cfg.get("lens", 50))
    cam_obj = bpy.data.objects.new("HeroCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    yaw = math.radians(float(cfg.get("yaw_deg", 15)))
    pitch = math.radians(float(cfg.get("pitch_deg", 10)))
    # orbit distance from default loc or derived
    loc = cfg.get("loc", [0.0, -3.6, 1.0])
    # apply yaw/pitch orbit around look_at
    look = cfg.get("look_at", [0.0, 0.0, 0.0])
    dist = math.sqrt(loc[0] ** 2 + loc[1] ** 2 + loc[2] ** 2) or 3.6
    # spherical-ish from -Y
    x = dist * math.sin(yaw) * math.cos(pitch)
    y = -dist * math.cos(yaw) * math.cos(pitch)
    z = dist * math.sin(pitch) + 0.15
    cam_obj.location = (x, y, z)

    # track to empty
    target = bpy.data.objects.new("CamTarget", None)
    bpy.context.collection.objects.link(target)
    target.location = (look[0], look[1], look[2])
    track = cam_obj.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    bpy.context.scene.camera = cam_obj

    # frame objects with padding via ortho_scale / view_frame approximation:
    # use camera view fit if objects provided
    if objects:
        # compute bbox
        import mathutils
        min_c = mathutils.Vector((1e9, 1e9, 1e9))
        max_c = mathutils.Vector((-1e9, -1e9, -1e9))
        any_ok = False
        for obj in objects:
            for corner in obj.bound_box:
                wc = obj.matrix_world @ mathutils.Vector(corner)
                min_c = mathutils.Vector((min(min_c.x, wc.x), min(min_c.y, wc.y), min(min_c.z, wc.z)))
                max_c = mathutils.Vector((max(max_c.x, wc.x), max(max_c.y, wc.y), max(max_c.z, wc.z)))
                any_ok = True
        if any_ok:
            center = (min_c + max_c) * 0.5
            target.location = center
            extent = (max_c - min_c).length
            padding = float(cfg.get("padding", 0.15))
            # pull camera back based on extent
            dist2 = max(2.5, extent * (1.2 + padding * 2))
            cam_obj.location = (
                center.x + dist2 * math.sin(yaw) * math.cos(pitch),
                center.y - dist2 * math.cos(yaw) * math.cos(pitch),
                center.z + dist2 * math.sin(pitch),
            )
    return cam_obj
