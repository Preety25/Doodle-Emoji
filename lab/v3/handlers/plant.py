"""Plant handler: pot, stem, leaves. Leaves stay off the stem mesh."""
from __future__ import annotations

from lab.v3.handlers.common import by_id, envelope, tube_component, volume_component


def handle_plant(source_id, meta, components):
    ids = by_id(components)
    notes = []
    confidence = "HIGH"
    comps = []

    pot = ids.get("pot")
    stem = ids.get("stem")
    leaf_l = ids.get("leaf_l")
    leaf_r = ids.get("leaf_r")
    if not all((pot, stem, leaf_l, leaf_r)):
        confidence = "MEDIUM"
        notes.append("expected pot, stem, leaf_l, leaf_r stroke ids")

    if pot:
        comps.append(
            volume_component(
                id="pot",
                name="pot",
                role="pot",
                points=pot["points"],
                color=pot.get("color") or "#C4A484",
                source_strokes=[pot["id"]],
                z_order=0,
                feature_scale="primary",
                notes="Pot is its own solid. The stem is not carved out of it.",
                resample=48,
            )
        )
    if stem:
        comps.append(
            tube_component(
                id="stem",
                name="stem",
                role="stem",
                points=stem["points"],
                color=stem.get("color") or "#4CAF50",
                source_strokes=[stem["id"]],
                z_order=2,
                feature_scale="secondary",
                notes="Open stroke as a round stem, not a flat ribbon slab.",
                smooth_iters=1,
                resample=24,
            )
        )
    for stroke, cid, name in ((leaf_l, "leaf_l", "left leaf"), (leaf_r, "leaf_r", "right leaf")):
        if not stroke:
            continue
        comps.append(
            volume_component(
                id=cid,
                name=name,
                role="leaf",
                points=stroke["points"],
                color=stroke.get("color") or "#43A047",
                source_strokes=[stroke["id"]],
                z_order=3,
                feature_scale="secondary",
                notes="Leaf mesh is separate from the stem.",
                resample=48,
            )
        )

    present = {c["id"] for c in comps}
    rels = [
        {"type": "grows_from", "a": "stem", "b": "pot", "detail": "stem rises out of the pot"},
        {"type": "attached_to", "a": "leaf_l", "b": "stem", "detail": "left leaf is not fused into the stem"},
        {"type": "attached_to", "a": "leaf_r", "b": "stem", "detail": "right leaf is not fused into the stem"},
    ]
    rels = [r for r in rels if r["a"] in present and r["b"] in present]
    if confidence == "HIGH" and len(comps) < 4:
        confidence = "MEDIUM"

    return envelope(
        source_id=source_id,
        handler="plant_v3",
        subject_hypothesis="potted_plant",
        confidence=confidence,
        orientation="upright",
        components=comps,
        relationships=rels,
        must=[
            "pot at the base",
            "single stem",
            "left leaf",
            "right leaf",
            "leaf shapes as drawn (not replaced with generic botanicals)",
        ],
        may=["thicken the nearly-flat stem stroke into a round stalk", "smooth leaf wobble"],
        never=[
            "extra leaves, flowers, or fruit",
            "a face on the pot",
            "fuse leaves into one canopy blob",
            "a ground or table",
            "replace with a photoreal houseplant",
        ],
        notes=" ".join(notes) if notes else "Pot, stem, and two leaves from stroke ids.",
        camera_profile="plant",
    )
