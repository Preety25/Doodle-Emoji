"""Shared blueprint constructors."""
from __future__ import annotations

from lab.v3.geom2d import dedupe_path, dedupe_ring, resample_closed, resample_open


def by_id(components):
    return {c["id"]: c for c in components}


def volume_component(
    *,
    id,
    name,
    role,
    points,
    color,
    source_strokes,
    z_order,
    feature_scale,
    completed=False,
    kind="closed_volume",
    pin_points=None,
    notes="",
    resample=96,
):
    ring = dedupe_ring(points)
    if resample and len(ring) >= 3 and feature_scale == "primary":
        ring = resample_closed(ring, resample, pins=pin_points)
    elif resample and kind == "disc":
        ring = resample_closed(ring, max(24, min(resample, 48)), pins=pin_points)
    elif feature_scale == "secondary" and len(ring) >= 3:
        # keep corners; only densify a little so bevel has edges to work with
        ring = resample_closed(ring, max(len(ring), min(36, resample // 2)), pins=pin_points)
    return {
        "id": id,
        "name": name,
        "role": role,
        "kind": kind,
        "source_strokes": list(source_strokes),
        "completed": bool(completed),
        "closed": True,
        "polygon": ring,
        "path": None,
        "color": color,
        "z_order": int(z_order),
        "feature_scale": feature_scale,
        "pin_points": [list(p) for p in (pin_points or []) if p is not None],
        "notes": notes,
    }


def tube_component(
    *,
    id,
    name,
    role,
    points,
    color,
    source_strokes,
    z_order,
    feature_scale,
    completed=False,
    notes="",
    smooth_iters=1,
    resample=48,
):
    path = dedupe_path(points)
    if smooth_iters:
        from lab.v3.geom2d import chaikin_open

        path = chaikin_open(path, smooth_iters)
    if resample:
        path = resample_open(path, max(8, resample))
    return {
        "id": id,
        "name": name,
        "role": role,
        "kind": "open_tube",
        "source_strokes": list(source_strokes),
        "completed": bool(completed),
        "closed": False,
        "polygon": None,
        "path": path,
        "color": color,
        "z_order": int(z_order),
        "feature_scale": feature_scale,
        "pin_points": [],
        "notes": notes,
    }


def envelope(
    *,
    source_id,
    handler,
    subject_hypothesis,
    confidence,
    orientation,
    components,
    relationships,
    must,
    may,
    never,
    notes,
    camera_profile,
):
    return {
        "schema_version": "doodle.blueprint.v3",
        "source_id": source_id,
        "handler": handler,
        "handler_kind": "category_specific",
        "general_recognition": False,
        "subject_hypothesis": subject_hypothesis,
        "confidence": confidence,
        "orientation": orientation,
        "camera_profile": camera_profile,
        "major_components": components,
        "component_relationships": relationships,
        "features_must_preserve": must,
        "features_may_complete": may,
        "features_must_never_invent": never,
        "notes": notes,
    }
