"""bpy curve/mesh geometry ops — intended to run inside Blender.

V1: solidify extrude + bevel + remesh/smooth (slabby risk).
V2 (tx.v2): silhouette-aware front inflation, stronger fillets, thinner walls,
open-stroke tubes, adaptive min thickness, preserve disconnected components.
Prefer subsurf over voxel remesh to avoid melting concave silhouettes.
"""
from __future__ import annotations

from typing import Any


def _ensure_bpy():
    import bpy
    return bpy


def clear_scene(bpy):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for b in list(block):
            block.remove(b)


def _set_poly_points(spline, points, closed: bool):
    use_pts = list(points)
    if closed and len(use_pts) > 2:
        if abs(use_pts[0][0] - use_pts[-1][0]) < 1e-8 and abs(use_pts[0][1] - use_pts[-1][1]) < 1e-8:
            use_pts = use_pts[:-1]
    n = len(use_pts)
    spline.points.add(max(0, n - 1))
    for i, p in enumerate(use_pts):
        spline.points[i].co = (float(p[0]), float(p[1]), 0.0, 1.0)
    spline.use_cyclic_u = bool(closed)


def _geom_version(recipe_geom: dict) -> str:
    return str(recipe_geom.get("version", "v1")).lower()


def _chaikin(points, iterations=2):
    """Light Chaikin corner-cutting — softens faceting without erasing overall silhouette."""
    pts = [list(p) for p in points]
    if len(pts) > 2 and abs(pts[0][0] - pts[-1][0]) < 1e-9 and abs(pts[0][1] - pts[-1][1]) < 1e-9:
        pts = pts[:-1]
    for _ in range(max(0, int(iterations))):
        n = len(pts)
        nxt = []
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            nxt.append([0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]])
            nxt.append([0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]])
        pts = nxt
    pts.append(pts[0][:])
    return pts


def _adaptive_min_thickness(points: list, recipe_geom: dict) -> float:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    base = float(recipe_geom.get("min_feature_thickness", 0.03))
    if span < 0.12:
        return max(base, 0.04)
    if span < 0.25:
        return max(base * 0.9, 0.028)
    return base


def _front_inflate(mesh_obj, recipe_geom: dict):
    """Displace verts along +Z by radial falloff from XY centroid → soft front bulge."""
    import bmesh
    from mathutils import Vector

    inflate = float(recipe_geom.get("inflation_amount", 0.2))
    if inflate <= 0:
        return
    bpy = _ensure_bpy()
    bpy.context.view_layer.objects.active = mesh_obj
    mesh_obj.select_set(True)

    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    bm.verts.ensure_lookup_table()
    if not bm.verts:
        bm.free()
        return

    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    cx = 0.5 * (min(xs) + max(xs))
    cy = 0.5 * (min(ys) + max(ys))
    max_r = max((Vector((v.co.x - cx, v.co.y - cy)).length for v in bm.verts), default=1.0) or 1.0
    front_bias = float(recipe_geom.get("front_bias", 0.9))
    z_vals = [v.co.z for v in bm.verts]
    zmin, zmax = min(z_vals), max(z_vals)
    zspan = max(zmax - zmin, 1e-6)

    for v in bm.verts:
        r = Vector((v.co.x - cx, v.co.y - cy)).length / max_r
        falloff = max(0.0, 1.0 - r ** 1.8)
        falloff = falloff * falloff * (3 - 2 * falloff)
        zn = (v.co.z - zmin) / zspan
        side = front_bias * zn + (1.0 - front_bias) * 0.35
        v.co.z += inflate * falloff * side

    bm.to_mesh(mesh_obj.data)
    bm.free()
    mesh_obj.data.update()


def create_closed_filled_v1(bpy, name: str, points: list, recipe_geom: dict):
    curve_data = bpy.data.curves.new(name=name, type="CURVE")
    curve_data.dimensions = "2D"
    curve_data.resolution_u = int(recipe_geom.get("curve_resolution_u", 24))
    curve_data.fill_mode = "BOTH"
    spline = curve_data.splines.new("POLY")
    _set_poly_points(spline, points, closed=True)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    mesh_obj = bpy.context.view_layer.objects.active

    extrude = float(recipe_geom.get("extrusion", 0.22))
    bevel = float(recipe_geom.get("bevel_depth", 0.08))

    bpy.ops.object.modifier_add(type="SOLIDIFY")
    sol = mesh_obj.modifiers[-1]
    sol.thickness = extrude
    sol.offset = 0.0
    bpy.ops.object.modifier_apply(modifier=sol.name)

    if bevel > 0:
        bpy.ops.object.modifier_add(type="BEVEL")
        bev = mesh_obj.modifiers[-1]
        bev.width = min(max(bevel, extrude * 0.38), extrude * 0.49)
        bev.segments = max(4, int(recipe_geom.get("bevel_resolution", 4)))
        bev.limit_method = "NONE"
        bpy.ops.object.modifier_apply(modifier=bev.name)

    if bool(recipe_geom.get("remesh", True)):
        bpy.ops.object.modifier_add(type="REMESH")
        rem = mesh_obj.modifiers[-1]
        rem.mode = "VOXEL"
        rem.voxel_size = float(recipe_geom.get("voxel_size", 0.035))
        bpy.ops.object.modifier_apply(modifier=rem.name)

    smooth_iters = int(recipe_geom.get("smooth_iters", 8))
    if smooth_iters > 0:
        bpy.ops.object.modifier_add(type="SMOOTH")
        mod = mesh_obj.modifiers[-1]
        mod.iterations = smooth_iters
        mod.factor = float(recipe_geom.get("smooth_factor", 0.5))
        bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.ops.object.shade_smooth()
    import mathutils
    bpy.context.view_layer.update()
    bbox = [mesh_obj.matrix_world @ mathutils.Vector(c) for c in mesh_obj.bound_box]
    zmin = min(v.z for v in bbox)
    zmax = max(v.z for v in bbox)
    mesh_obj.location.z -= (zmin + zmax) * 0.5
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return mesh_obj


def create_closed_filled_v2(bpy, name: str, points: list, recipe_geom: dict):
    """Silhouette-aware inflation: thin wall + fillet + subsurf + front dome."""
    if int(recipe_geom.get("chaikin_iters", 2)) > 0:
        points = _chaikin(points, int(recipe_geom.get("chaikin_iters", 2)))

    curve_data = bpy.data.curves.new(name=name, type="CURVE")
    curve_data.dimensions = "2D"
    curve_data.resolution_u = int(recipe_geom.get("curve_resolution_u", 28))
    curve_data.fill_mode = "BOTH"
    spline = curve_data.splines.new("POLY")
    _set_poly_points(spline, points, closed=True)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    mesh_obj = bpy.context.view_layer.objects.active

    wall = float(recipe_geom.get("extrusion_wall", recipe_geom.get("extrusion", 0.12)))
    wall = min(max(wall, _adaptive_min_thickness(points, recipe_geom)), 0.16)
    bevel = float(recipe_geom.get("bevel_fillet", recipe_geom.get("bevel_depth", 0.06)))

    bpy.ops.object.modifier_add(type="SOLIDIFY")
    sol = mesh_obj.modifiers[-1]
    sol.thickness = wall
    sol.offset = float(recipe_geom.get("solidify_offset", 0.65))
    bpy.ops.object.modifier_apply(modifier=sol.name)

    if bevel > 0:
        bpy.ops.object.modifier_add(type="BEVEL")
        bev = mesh_obj.modifiers[-1]
        bev.width = min(max(bevel, wall * 0.28), wall * 0.55)
        bev.segments = max(5, int(recipe_geom.get("bevel_resolution", 6)))
        bev.limit_method = "NONE"
        if hasattr(bev, "profile"):
            bev.profile = float(recipe_geom.get("bevel_profile", 0.7))
        bpy.ops.object.modifier_apply(modifier=bev.name)

    if bool(recipe_geom.get("remesh", False)):
        bpy.ops.object.modifier_add(type="REMESH")
        rem = mesh_obj.modifiers[-1]
        rem.mode = "VOXEL"
        rem.voxel_size = float(recipe_geom.get("voxel_size", 0.02))
        bpy.ops.object.modifier_apply(modifier=rem.name)
    elif bool(recipe_geom.get("subsurf", True)):
        bpy.ops.object.modifier_add(type="SUBSURF")
        sub = mesh_obj.modifiers[-1]
        sub.levels = int(recipe_geom.get("subsurf_levels", 2))
        sub.render_levels = int(recipe_geom.get("subsurf_levels", 2))
        bpy.ops.object.modifier_apply(modifier=sub.name)

    _front_inflate(mesh_obj, recipe_geom)

    smooth_iters = int(recipe_geom.get("smooth_iters", 2))
    if smooth_iters > 0:
        bpy.ops.object.modifier_add(type="SMOOTH")
        mod = mesh_obj.modifiers[-1]
        mod.iterations = smooth_iters
        mod.factor = float(recipe_geom.get("smooth_factor", 0.25))
        bpy.ops.object.modifier_apply(modifier=mod.name)

    if bool(recipe_geom.get("soft_junctions", True)):
        bpy.ops.object.modifier_add(type="SMOOTH")
        mod = mesh_obj.modifiers[-1]
        mod.iterations = int(recipe_geom.get("junction_smooth_iters", 1))
        mod.factor = float(recipe_geom.get("junction_smooth_factor", 0.25))
        bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.ops.object.shade_smooth()
    import math
    import mathutils
    # Face-toward-camera: doodle drawn in XY (normal +Z). Rotate -90° about X so
    # the silhouette faces -Y (default camera) and extrusion depth goes into +Y.
    # Front inflate (done in +Z above) becomes a bulge toward the camera.
    if bool(recipe_geom.get("face_toward_camera", True)):
        mesh_obj.rotation_euler = (math.radians(-90.0), 0.0, 0.0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bpy.context.view_layer.update()
    bbox = [mesh_obj.matrix_world @ mathutils.Vector(c) for c in mesh_obj.bound_box]
    min_c = mathutils.Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
    max_c = mathutils.Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
    center = (min_c + max_c) * 0.5
    mesh_obj.location -= center
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return mesh_obj


def create_closed_filled(bpy, name: str, points: list, recipe_geom: dict):
    if _geom_version(recipe_geom).startswith("v2"):
        return create_closed_filled_v2(bpy, name, points, recipe_geom)
    return create_closed_filled_v1(bpy, name, points, recipe_geom)


def create_open_tube(bpy, name: str, points: list, recipe_geom: dict):
    curve_data = bpy.data.curves.new(name=name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = int(recipe_geom.get("curve_resolution_u", 24))
    curve_data.fill_mode = "FULL"
    radius = float(recipe_geom.get("tube_radius_open", recipe_geom.get("tube_radius", 0.045)))
    if len(points) >= 2:
        span = max(abs(points[-1][0] - points[0][0]), abs(points[-1][1] - points[0][1]), 1e-6)
        min_t = float(recipe_geom.get("min_feature_thickness", 0.03))
        if span < 0.2:
            radius = max(radius, min_t)
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = int(recipe_geom.get("bevel_resolution", 5))
    curve_data.use_fill_caps = True
    spline = curve_data.splines.new("POLY")
    _set_poly_points(spline, points, closed=False)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    mesh_obj = bpy.context.view_layer.objects.active

    if _geom_version(recipe_geom).startswith("v2"):
        smooth_iters = int(recipe_geom.get("tube_smooth_iters", 3))
        if smooth_iters > 0:
            bpy.ops.object.modifier_add(type="SMOOTH")
            mod = mesh_obj.modifiers[-1]
            mod.iterations = smooth_iters
            mod.factor = 0.35
            bpy.ops.object.modifier_apply(modifier=mod.name)
        if bool(recipe_geom.get("face_toward_camera", True)):
            import math
            mesh_obj.rotation_euler = (math.radians(-90.0), 0.0, 0.0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    bpy.ops.object.shade_smooth()
    return mesh_obj


def build_geometry(components: list[dict[str, Any]], recipe: dict) -> list:
    bpy = _ensure_bpy()
    geom = recipe.get("geometry", {})
    objects = []
    for i, comp in enumerate(components):
        name = f"doodle_{comp.get('id', i)}"
        pts = comp["points"]
        bpy.ops.object.select_all(action="DESELECT")
        if comp.get("closed", False) and len(pts) >= 3:
            mesh_obj = create_closed_filled(bpy, name, pts, geom)
        else:
            mesh_obj = create_open_tube(bpy, name, pts, geom)
        mesh_obj["stroke_id"] = comp.get("id", str(i))
        mesh_obj["stroke_color"] = comp.get("color") or ""
        mesh_obj.select_set(False)
        objects.append(mesh_obj)
    return objects
