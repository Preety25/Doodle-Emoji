"""Turn a blueprint into style-ready render primitives.

Thickness is per component, from that component's own span — small parts are
not given the body's thickness. Nothing here remeshes a global doodle.
"""
from __future__ import annotations

from lab.v3.geom2d import bbox, grade_color, hex_to_rgb, span, vertical_seam
from lab.v3.styles import CAMERAS, STYLES


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _base_dims(comp):
    pts = comp.get("polygon") or comp.get("path") or []
    w, h, sp = span(pts) if pts else (0.1, 0.1, 0.1)
    scale = comp.get("feature_scale", "secondary")
    kind = comp.get("kind")
    if kind == "open_tube":
        # Radius is absolute so a nearly-straight stem stays visible.
        if scale == "detail":
            radius = 0.011
        elif scale == "secondary":
            radius = 0.02
        else:
            radius = 0.028
        return {
            "radius": radius,
            "thickness": radius * 2,
            "inflate": 0.0,
            "bevel": 0.0,
            "crease": 0.0,
        }
    if scale == "primary":
        thickness = _clamp(sp * 0.16, 0.07, 0.15)
        inflate = thickness * 0.62
        bevel = 0.007
        crease = 0.15
    elif scale == "detail":
        thickness = _clamp(sp * 0.35, 0.012, 0.028)
        inflate = thickness * 0.35
        bevel = 0.0025
        crease = 0.92
    else:
        thickness = _clamp(sp * 0.28, 0.028, 0.08)
        inflate = thickness * 0.45
        bevel = 0.004
        crease = 0.78
    return {
        "radius": 0.0,
        "thickness": thickness,
        "inflate": inflate,
        "bevel": bevel,
        "crease": crease,
    }


def _z_lift(comp, primary_thickness):
    """Stack parts so details sit on the parent instead of inside it."""
    z = int(comp.get("z_order") or 0)
    scale = comp.get("feature_scale")
    if scale == "detail":
        return primary_thickness * 0.55 + 0.004 * z
    if scale == "secondary":
        return 0.006 + 0.004 * min(z, 3)
    return 0.003 * min(z, 2)


def primitives_from_blueprint(bp: dict) -> list[dict]:
    comps = bp.get("major_components") or []
    primary_th = 0.1
    for c in comps:
        if c.get("feature_scale") == "primary" and c.get("kind") != "open_tube":
            primary_th = _base_dims(c)["thickness"]
            break
    prims = []
    for c in comps:
        dims = _base_dims(c)
        color = hex_to_rgb(c.get("color"))
        prim = {
            "id": c["id"],
            "name": c.get("name") or c["id"],
            "kind": "tube" if c.get("kind") == "open_tube" else "volume",
            "role": c.get("role"),
            "feature_scale": c.get("feature_scale", "secondary"),
            "polygon": c.get("polygon"),
            "path": c.get("path"),
            "color": color,
            "z_lift": _z_lift(c, primary_th),
            "pin_points": c.get("pin_points") or [],
            "thickness": dims["thickness"],
            "inflate": dims["inflate"],
            "bevel": dims["bevel"],
            "crease": dims["crease"],
            "radius": dims["radius"],
            "allow_bubbles": c.get("feature_scale") == "primary" and c.get("kind") != "open_tube",
            "allow_fur": c.get("feature_scale") in ("primary", "secondary") and c.get("role") not in ("eye", "window", "spiral"),
            "allow_lump": c.get("feature_scale") in ("primary", "secondary") and c.get("role") not in ("eye", "window", "spiral", "flame"),
            "allow_seam": c.get("feature_scale") == "primary" and c.get("kind") != "open_tube",
            "completed": bool(c.get("completed")),
        }
        if prim["allow_seam"] and prim.get("polygon"):
            prim["seam_path"] = vertical_seam(prim["polygon"])
        else:
            prim["seam_path"] = []
        prims.append(prim)
    return prims


def apply_style(prims: list[dict], style_name: str) -> list[dict]:
    st = STYLES[style_name]
    out = []
    for src in prims:
        p = dict(src)
        p["color"] = grade_color(
            list(src["color"]),
            saturation=st["saturation"],
            value=st["value"],
            toward=st["toward"],
            toward_amt=st["toward_amt"],
        )
        p["thickness"] = src["thickness"] * st["thickness_mul"]
        p["inflate"] = src["inflate"] * st["inflate_mul"]
        p["radius"] = src["radius"] * st["radius_mul"]
        p["bevel"] = src["bevel"] * st["bevel_mul"]
        if src["feature_scale"] == "detail":
            p["thickness"] = min(p["thickness"], 0.03)
            p["inflate"] = min(p["inflate"], 0.012)
            p["allow_fur"] = False
            p["allow_bubbles"] = False
            p["allow_lump"] = False
        if style_name == "glossy":
            p["crease"] = max(src["crease"], 0.45 if src["feature_scale"] != "primary" else 0.25)
        if style_name == "plush" and src["kind"] == "tube":
            p["radius"] = src["radius"] * st["radius_mul"]
        # eyes / window stay dark and small in every style
        if src.get("role") in ("eye",):
            p["color"] = [0.08, 0.07, 0.07]
            p["allow_fur"] = False
        out.append(p)
    return out


def build_job(bp: dict, style_name: str, output_path: str, *, seed: int, resolution: int, samples: int) -> dict:
    base = primitives_from_blueprint(bp)
    prims = apply_style(base, style_name)
    profile = bp.get("camera_profile") or "heart"
    camera = dict(CAMERAS.get(profile, CAMERAS["heart"]))
    st = STYLES[style_name]
    return {
        "schema": "doodle.renderjob.v3",
        "source_id": bp.get("source_id"),
        "subject": bp.get("subject_hypothesis"),
        "style": style_name,
        "seed": int(seed),
        "output": output_path,
        "resolution": int(resolution),
        "samples": int(samples),
        "camera": camera,
        "style_params": {
            "roughness": st["roughness"],
            "metallic": st["metallic"],
            "transmission": st["transmission"],
            "ior": st["ior"],
            "subsurface": st["subsurface"],
            "sss_scale": st["sss_scale"],
            "sss_radius": list(st["sss_radius"]),
            "specular": st["specular"],
            "coat": st["coat"],
            "coat_roughness": st["coat_roughness"],
            "sheen": st["sheen"],
            "sheen_roughness": st["sheen_roughness"],
            "bubbles": st["bubbles"],
            "lumps": st["lumps"],
            "fur": st["fur"],
            "seam": st["seam"],
            "key": st["key"],
            "fill": st["fill"],
            "rim": st["rim"],
            "world": st["world"],
            "exposure": st["exposure"],
            "gtao": st["gtao"],
        },
        "primitives": prims,
    }
