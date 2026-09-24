"""Low-confidence handler: polish the strokes that exist. Do not name a new object."""
from __future__ import annotations

from lab.v3.handlers.common import envelope, tube_component, volume_component


def handle_messy(source_id, meta, components):
    comps = []
    for c in components:
        pts = c.get("points") or []
        if c.get("closed") and len(pts) >= 4:
            comps.append(
                volume_component(
                    id=c["id"],
                    name=f"closed mark ({c['id']})",
                    role="mark",
                    points=pts,
                    color=c.get("color") or "#CE93D8",
                    source_strokes=[c["id"]],
                    z_order=1,
                    feature_scale="secondary",
                    notes="Closed fragment kept as its own small volume. Not promoted into a known object.",
                    resample=40,
                )
            )
        elif len(pts) >= 2:
            comps.append(
                tube_component(
                    id=c["id"],
                    name=f"stroke ({c['id']})",
                    role="stroke",
                    points=pts,
                    color=c.get("color") or "#AB47BC",
                    source_strokes=[c["id"]],
                    z_order=2,
                    feature_scale="secondary",
                    notes="Open stroke polished as a tube. Not closed, not completed into a symbol.",
                    smooth_iters=1,
                    resample=36,
                )
            )
    return envelope(
        source_id=source_id,
        handler="messy_v3",
        subject_hypothesis="unresolved_gesture",
        confidence="LOW",
        orientation="as_drawn",
        components=comps,
        relationships=[
            {
                "type": "unrelated_fragments",
                "components": [c["id"] for c in comps],
                "detail": "fragments are not connected into a single invented silhouette",
            }
        ],
        must=[
            "each source stroke remains visible",
            "open strokes stay open",
            "the small closed fragment stays a small fragment",
            "relative placement of the three marks",
        ],
        may=[
            "round caps and even out stroke radius",
            "light smoothing of jitter",
        ],
        never=[
            "close the partial into a star",
            "invent a face, object, or character",
            "add the missing points that would finish a symbol",
            "drop the orphan loop or the scribble",
            "a ground, frame, or caption",
        ],
        notes=(
            "LOW confidence on purpose. The partial stroke can be read as star-like; "
            "this handler refuses that reading and only polishes the ink that is there."
        ),
        camera_profile="messy",
    )
