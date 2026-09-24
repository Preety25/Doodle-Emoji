"""Camera and framing from recipe.

V2 modes: front_ortho | front_perspective | subtle_34 | adaptive
Prioritize silhouette readability; avoid large side-wall reveals as the way to show 3D.
"""
from __future__ import annotations

import math


def _ensure_bpy():
    import bpy
    return bpy


def _bbox_world(objects):
    import mathutils
    min_c = mathutils.Vector((1e9, 1e9, 1e9))
    max_c = mathutils.Vector((-1e9, -1e9, -1e9))
    any_ok = False
    for obj in objects or []:
        for corner in obj.bound_box:
            wc = obj.matrix_world @ mathutils.Vector(corner)
            min_c = mathutils.Vector((min(min_c.x, wc.x), min(min_c.y, wc.y), min(min_c.z, wc.z)))
            max_c = mathutils.Vector((max(max_c.x, wc.x), max(max_c.y, wc.y), max(max_c.z, wc.z)))
            any_ok = True
    if not any_ok:
        return None, None, None
    center = (min_c + max_c) * 0.5
    extent = (max_c - min_c).length
    return center, extent, (min_c, max_c)


def setup_camera(recipe: dict, objects: list | None = None):
    bpy = _ensure_bpy()
    cfg = recipe.get("camera", {})
    mode = str(cfg.get("mode", "subtle_34")).lower()

    cam_data = bpy.data.cameras.new("HeroCam")
    cam_obj = bpy.data.objects.new("HeroCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)

    # V2 camera modes — keep yaw/pitch small so silhouette dominates
    if mode in ("front_ortho", "ortho", "front"):
        cam_data.type = "ORTHO"
        yaw = math.radians(float(cfg.get("yaw_deg", 0)))
        pitch = math.radians(float(cfg.get("pitch_deg", 0)))
        cam_data.lens = float(cfg.get("lens", 50))
    elif mode in ("front_perspective", "front_persp"):
        cam_data.type = "PERSP"
        yaw = math.radians(float(cfg.get("yaw_deg", 4)))
        pitch = math.radians(float(cfg.get("pitch_deg", 3)))
        cam_data.lens = float(cfg.get("lens", 85))  # longer lens = flatter
    elif mode == "adaptive":
        cam_data.type = "PERSP"
        # slightly more angle for multi-part depth read, still silhouette-first
        yaw = math.radians(float(cfg.get("yaw_deg", 8)))
        pitch = math.radians(float(cfg.get("pitch_deg", 6)))
        cam_data.lens = float(cfg.get("lens", 65))
    else:  # subtle_34 / v1 default
        cam_data.type = "PERSP"
        yaw = math.radians(float(cfg.get("yaw_deg", 8)))
        pitch = math.radians(float(cfg.get("pitch_deg", 6)))
        cam_data.lens = float(cfg.get("lens", 55))

    loc = cfg.get("loc", [0.0, -3.6, 1.0])
    look = cfg.get("look_at", [0.0, 0.0, 0.0])
    dist = math.sqrt(loc[0] ** 2 + loc[1] ** 2 + loc[2] ** 2) or 3.6
    x = dist * math.sin(yaw) * math.cos(pitch)
    y = -dist * math.cos(yaw) * math.cos(pitch)
    z = dist * math.sin(pitch) + float(cfg.get("z_lift", 0.05))
    cam_obj.location = (x, y, z)

    target = bpy.data.objects.new("CamTarget", None)
    bpy.context.collection.objects.link(target)
    target.location = (look[0], look[1], look[2])
    track = cam_obj.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    bpy.context.scene.camera = cam_obj

    padding = float(cfg.get("padding", 0.16))
    center, extent, bounds = _bbox_world(objects)
    if center is not None:
        target.location = center
        # pull camera back based on extent
        dist2 = max(2.4, extent * (1.15 + padding * 2.2))
        cam_obj.location = (
            center.x + dist2 * math.sin(yaw) * math.cos(pitch),
            center.y - dist2 * math.cos(yaw) * math.cos(pitch),
            center.z + dist2 * math.sin(pitch) + float(cfg.get("z_lift", 0.05)),
        )
        if cam_data.type == "ORTHO" and bounds is not None:
            min_c, max_c = bounds
            # ortho_scale is half-height of view roughly; use max XY extent
            span_x = max_c.x - min_c.x
            span_y = max_c.y - min_c.y
            span_z = max_c.z - min_c.z
            # camera looks roughly -Y; visible span is X and Z primarily at front
            visible = max(span_x, span_z, span_y * 0.35, 0.5)
            cam_data.ortho_scale = visible * (1.0 + padding * 2.0)

    return cam_obj
