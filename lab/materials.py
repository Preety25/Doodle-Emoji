"""Assign style recipe materials inside Blender."""
from __future__ import annotations

from typing import Any

from lab.parse_input import hex_to_rgba


def _ensure_bpy():
    import bpy
    return bpy


def make_material(bpy, name: str, color_rgba: list, mat_cfg: dict):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    bsdf.inputs["Base Color"].default_value = (
        color_rgba[0], color_rgba[1], color_rgba[2], 1.0
    )
    bsdf.inputs["Roughness"].default_value = float(mat_cfg.get("roughness", 0.5))
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = float(mat_cfg.get("specular", 0.5))
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = float(mat_cfg.get("specular", 0.5))
    bsdf.inputs["Metallic"].default_value = float(mat_cfg.get("metallic", 0.0))
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = float(mat_cfg.get("clearcoat", 0.0))
        bsdf.inputs["Coat Roughness"].default_value = float(mat_cfg.get("clearcoat_roughness", 0.03))
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = float(mat_cfg.get("clearcoat", 0.0))
        bsdf.inputs["Clearcoat Roughness"].default_value = float(mat_cfg.get("clearcoat_roughness", 0.03))

    # Transmission
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = float(mat_cfg.get("transmission", 0.0))
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = float(mat_cfg.get("transmission", 0.0))
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = float(mat_cfg.get("ior", 1.45))

    # SSS
    sss_w = float(mat_cfg.get("sss_weight", 0.0))
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = sss_w
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = sss_w
    radius = mat_cfg.get("sss_radius", [0.1, 0.1, 0.1])
    if "Subsurface Radius" in bsdf.inputs:
        bsdf.inputs["Subsurface Radius"].default_value = (radius[0], radius[1], radius[2])
    sss_color = mat_cfg.get("sss_color", color_rgba[:3])
    if "Subsurface Color" in bsdf.inputs:
        bsdf.inputs["Subsurface Color"].default_value = (sss_color[0], sss_color[1], sss_color[2], 1.0)

    # Optional velvet / fabric sheen (Blender 4.x Principled)
    sheen_w = float(mat_cfg.get("sheen_weight", 0.0))
    if sheen_w > 0 and "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = sheen_w
        if "Sheen Roughness" in bsdf.inputs:
            bsdf.inputs["Sheen Roughness"].default_value = float(mat_cfg.get("sheen_roughness", 0.35))
        sheen_col = mat_cfg.get("sheen_color")
        if sheen_col and "Sheen Tint" in bsdf.inputs:
            # Sheen Tint is float in some builds; Color in others — set safely
            try:
                bsdf.inputs["Sheen Tint"].default_value = float(sheen_col[0]) if isinstance(sheen_col, list) else float(sheen_col)
            except Exception:
                pass

    bump_s = float(mat_cfg.get("bump_strength", 0.0))
    if bump_s > 0:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.location = (-400, -200)
        noise.inputs["Scale"].default_value = float(mat_cfg.get("bump_scale", 25.0))
        if "Detail" in noise.inputs:
            noise.inputs["Detail"].default_value = float(mat_cfg.get("bump_detail", 8.0))
        if "Roughness" in noise.inputs:
            noise.inputs["Roughness"].default_value = float(mat_cfg.get("bump_noise_roughness", 0.55))
        bump = nodes.new("ShaderNodeBump")
        bump.location = (-200, -200)
        bump.inputs["Strength"].default_value = bump_s
        if "Distance" in bump.inputs:
            bump.inputs["Distance"].default_value = float(mat_cfg.get("bump_distance", 0.08))
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat


def assign_materials(objects: list, recipe: dict):
    bpy = _ensure_bpy()
    mat_cfg = recipe.get("material", {})
    fallback = mat_cfg.get("fallback_color", [1.0, 0.5, 0.7, 1.0])
    for obj in objects:
        color_hex = obj.get("stroke_color") or None
        if mat_cfg.get("use_stroke_color", True) and color_hex:
            rgba = hex_to_rgba(color_hex, fallback)
        else:
            rgba = list(fallback)
        mat = make_material(bpy, f"mat_{obj.name}", rgba, mat_cfg)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)


def add_gummy_bubbles(objects: list, recipe: dict):
    """Sparse internal air-bubble spheres for gummy signature (geo approx, not texture-only)."""
    bpy = _ensure_bpy()
    mat_cfg = recipe.get("material", {})
    if not mat_cfg.get("bubbles"):
        return
    density = float(mat_cfg.get("bubble_density", 0.35))
    scale = float(mat_cfg.get("bubble_scale", 0.018))
    import random
    rng = random.Random(int(recipe.get("_seed", 1)))
    for obj in objects:
        # bbox
        import mathutils
        bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
        min_c = mathutils.Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
        max_c = mathutils.Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
        diag = (max_c - min_c).length
        n = max(0, min(8, int(2 + density * 6 * diag)))
        for i in range(n):
            # bias tightly toward volume center so bubbles read as internal air
            t = [rng.uniform(0.38, 0.62) for _ in range(3)]
            loc = mathutils.Vector((
                min_c.x + t[0] * (max_c.x - min_c.x),
                min_c.y + t[1] * (max_c.y - min_c.y),
                min_c.z + t[2] * (max_c.z - min_c.z),
            ))
            r = scale * rng.uniform(0.45, 0.95)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=12, ring_count=8)
            bub = bpy.context.view_layer.objects.active
            bub.name = f"bubble_{obj.name}_{i}"
            # glassy bubble material
            mat = bpy.data.materials.new(name=f"bubmat_{bub.name}")
            mat.use_nodes = True
            nt = mat.node_tree
            nodes = nt.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.95, 0.98, 1.0, 1)
                bsdf.inputs["Roughness"].default_value = 0.02
                if "Transmission Weight" in bsdf.inputs:
                    bsdf.inputs["Transmission Weight"].default_value = 1.0
                elif "Transmission" in bsdf.inputs:
                    bsdf.inputs["Transmission"].default_value = 1.0
                if "IOR" in bsdf.inputs:
                    bsdf.inputs["IOR"].default_value = 1.05
                if "Alpha" in bsdf.inputs:
                    bsdf.inputs["Alpha"].default_value = 0.35
                mat.blend_method = "BLEND"
                if hasattr(mat, "shadow_method"):
                    try:
                        mat.shadow_method = "NONE"
                    except Exception:
                        pass
            bub.data.materials.append(mat)
            bpy.ops.object.shade_smooth()
