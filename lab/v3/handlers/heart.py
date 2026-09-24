"""Heart handler: one closed contour, cleft + lobes, upright, asymmetry kept."""
from __future__ import annotations

from lab.v3.geom2d import bottom_point, find_cleft, shoelace_area
from lab.v3.handlers.common import envelope, volume_component


def handle_heart(source_id, meta, components):
    closed = [c for c in components if c.get("closed") and len(c.get("points") or []) >= 4]
    if not closed:
        return envelope(
            source_id=source_id,
            handler="heart_v3",
            subject_hypothesis="heart",
            confidence="LOW",
            orientation="as_drawn",
            components=[],
            relationships=[],
            must=["whatever closed contour exists"],
            may=["smooth stroke wobble"],
            never=["invent a face", "mirror the doodle", "add a banner or arrow"],
            notes="Heart handler found no closed contour.",
            camera_profile="heart",
        )
    main = max(closed, key=lambda c: shoelace_area(c["points"]))
    cleft = find_cleft(main["points"])
    tip = bottom_point(main["points"])
    confidence = "HIGH" if cleft else "MEDIUM"
    comp = volume_component(
        id="heart",
        name="heart",
        role="primary",
        points=main["points"],
        color=main.get("color") or "#FF4D6D",
        source_strokes=[main["id"]],
        z_order=0,
        feature_scale="primary",
        pin_points=[p for p in (cleft, tip) if p],
        notes="Single volume from the user's contour. Cleft and bottom tip are pinned. Not symmetrized.",
        resample=140,
    )
    must = [
        "upright heart (point toward -Y, lobes toward +Y)",
        "two lobes",
        "user asymmetry — do not mirror",
        "bottom point",
    ]
    if cleft:
        must.append("top cleft between the lobes")
    else:
        must.append("top contour as drawn (cleft was not clearly detected)")
    return envelope(
        source_id=source_id,
        handler="heart_v3",
        subject_hypothesis="heart",
        confidence=confidence,
        orientation="upright",
        components=[comp],
        relationships=[
            {
                "type": "single_contour",
                "components": ["heart"],
                "detail": "lobes and point are one user stroke, not separate invented parts",
            }
        ],
        must=must,
        may=[
            "smooth small stroke wobble",
            "give the contour a soft inflated thickness",
        ],
        never=[
            "a face, eyes, or smile",
            "an arrow, banner, or text",
            "a second heart",
            "bilateral symmetry that erases the wonky lobes",
            "a ground plane or drop shadow card",
        ],
        notes="Category handler heart_v3. Cleft "
        + ("detected and pinned." if cleft else "NOT detected; confidence lowered."),
        camera_profile="heart",
    )
