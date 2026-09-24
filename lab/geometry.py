"""bpy curve/mesh geometry ops — intended to run inside Blender."""
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


def create_closed_filled(bpy, name: str, points: list, recipe_geom: dict):
    """Filled 2D curve → solidify → bevel → light remesh/smooth for soft inflation."""
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

    # Soft inflated silhouette: voxel remesh then smooth (light — preserve identity)
    use_remesh = bool(recipe_geom.get("remesh", True))
    if use_remesh:
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
    # recompute world bbox after transforms
    bpy.context.view_layer.update()
    bbox = [mesh_obj.matrix_world @ mathutils.Vector(c) for c in mesh_obj.bound_box]
    zmin = min(v.z for v in bbox)
    zmax = max(v.z for v in bbox)
    mesh_obj.location.z -= (zmin + zmax) * 0.5
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return mesh_obj


def create_open_tube(bpy, name: str, points: list, recipe_geom: dict):
    curve_data = bpy.data.curves.new(name=name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = int(recipe_geom.get("curve_resolution_u", 24))
    curve_data.fill_mode = "FULL"
    curve_data.bevel_depth = float(recipe_geom.get("tube_radius", 0.045))
    curve_data.bevel_resolution = int(recipe_geom.get("bevel_resolution", 4))
    curve_data.use_fill_caps = True
    spline = curve_data.splines.new("POLY")
    _set_poly_points(spline, points, closed=False)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    mesh_obj = bpy.context.view_layer.objects.active
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
