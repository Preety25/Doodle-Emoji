"""Rose handler: bloom, spiral, stem, leaf. Spiral stays a separate cord."""
from __future__ import annotations

from lab.v3.handlers.common import by_id, envelope, tube_component, volume_component


def handle_rose(source_id, meta, components):
    ids = by_id(components)
    notes = []
    confidence = "HIGH"
    bloom = ids.get("bloom")
    spiral = ids.get("spiral")
    leaf = ids.get("leaf")
    stem = ids.get("stem")
    if not all((bloom, spiral, stem, leaf)):
        confidence = "MEDIUM"
        notes.append("expected bloom, spiral, stem, leaf")

    comps = []
    if bloom:
        comps.append(
            volume_component(
                id="bloom",
                name="bloom",
                role="bloom",
                points=bloom["points"],
                color=bloom.get("color") or "#E53935",
                source_strokes=[bloom["id"]],
                z_order=0,
                feature_scale="primary",
                notes="Outer bloom contour. The spiral is not filled into this mesh.",
                resample=120,
            )
        )
    if spiral:
        comps.append(
            tube_component(
                id="spiral",
                name="spiral",
                role="spiral",
                points=spiral["points"],
                color=spiral.get("color") or "#C62828",
                source_strokes=[spiral["id"]],
                z_order=5,
                feature_scale="detail",
                notes="User spiral kept as a raised cord on the bloom, including any part that sticks past the bloom.",
                smooth_iters=1,
                resample=80,
            )
        )
    if stem:
        comps.append(
            tube_component(
                id="stem",
                name="stem",
                role="stem",
                points=stem["points"],
                color=stem.get("color") or "#2E7D32",
                source_strokes=[stem["id"]],
                z_order=1,
                feature_scale="secondary",
                notes="Open stem stroke as a stalk.",
                smooth_iters=1,
                resample=16,
            )
        )
    if leaf:
        comps.append(
            volume_component(
                id="leaf",
                name="leaf",
                role="leaf",
                points=leaf["points"],
                color=leaf.get("color") or "#43A047",
                source_strokes=[leaf["id"]],
                z_order=3,
                feature_scale="secondary",
                notes="Single leaf, separate from bloom and stem.",
                resample=40,
            )
        )

    present = {c["id"] for c in comps}
    rels = [
        {"type": "on_surface", "a": "spiral", "b": "bloom", "detail": "spiral is a separate cord, not a texture painted into the bloom"},
        {"type": "below", "a": "stem", "b": "bloom", "detail": "stem continues under the bloom"},
        {"type": "attached_to", "a": "leaf", "b": "stem", "detail": "one leaf, not fused into the stem"},
    ]
    rels = [r for r in rels if r["a"] in present and r["b"] in present]
    if "spiral" not in present:
        confidence = "MEDIUM"
        notes.append("spiral stroke missing — rose structure is weak")

    return envelope(
        source_id=source_id,
        handler="rose_v3",
        subject_hypothesis="rose",
        confidence=confidence,
        orientation="upright",
        components=comps,
        relationships=rels,
        must=[
            "bloom silhouette",
            "spiral structure (the drawn swirl, not a generic rose top)",
            "stem",
            "single leaf",
            "spiral that extends outside the bloom if the user drew it that way",
        ],
        may=["round the spiral cord", "thicken the stem stroke"],
        never=[
            "replace the spiral with a photoreal petal stack",
            "add thorns, extra leaves, or a vase",
            "add a face",
            "fuse the spiral into the bloom so it disappears",
            "a ground plane",
        ],
        notes=" ".join(notes) if notes else "Bloom volume plus spiral cord, stem, and one leaf.",
        camera_profile="rose",
    )
