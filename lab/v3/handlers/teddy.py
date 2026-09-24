"""Teddy handler: head, ears, body, and the eyes the user actually drew."""
from __future__ import annotations

from lab.v3.geom2d import centroid, shoelace_area
from lab.v3.handlers.common import by_id, envelope, volume_component


def handle_teddy(source_id, meta, components):
    ids = by_id(components)
    closed = [c for c in components if c.get("closed")]
    notes = []
    confidence = "HIGH"

    def need(key, role_name):
        if key in ids:
            return ids[key]
        notes.append(f"missing stroke {key}")
        return None

    body_s = need("body", "body")
    head_s = need("head", "head")
    ear_l_s = need("ear_l", "ear")
    ear_r_s = need("ear_r", "ear")
    eye_l_s = need("eye_l", "eye")
    eye_r_s = need("eye_r", "eye")

    if body_s is None or head_s is None:
        confidence = "LOW"
        # still try largest two rounds
        ordered = sorted(closed, key=lambda c: shoelace_area(c["points"]), reverse=True)
        if body_s is None and ordered:
            body_s = ordered[0]
            notes.append("body guessed as largest closed shape")
        if head_s is None and len(ordered) > 1:
            head_s = ordered[1]
            notes.append("head guessed as second largest")

    if ear_l_s is None or ear_r_s is None or eye_l_s is None or eye_r_s is None:
        confidence = "MEDIUM" if confidence == "HIGH" else confidence

    comps = []

    def add_volume(stroke, cid, name, role, scale, z, kind="closed_volume", resample=64):
        if stroke is None:
            return
        comps.append(
            volume_component(
                id=cid,
                name=name,
                role=role,
                points=stroke["points"],
                color=stroke.get("color") or "#D7A86E",
                source_strokes=[stroke["id"]],
                z_order=z,
                feature_scale=scale,
                kind=kind,
                notes="Separate mesh. Not boolean-unioned into its neighbor.",
                resample=resample,
            )
        )

    add_volume(body_s, "body", "body", "body", "primary", 0, resample=100)
    add_volume(head_s, "head", "head", "head", "primary", 2, resample=90)
    add_volume(ear_l_s, "ear_l", "left ear", "ear", "secondary", 3, resample=36)
    add_volume(ear_r_s, "ear_r", "right ear", "ear", "secondary", 3, resample=36)
    add_volume(eye_l_s, "eye_l", "left eye", "eye", "detail", 6, kind="disc", resample=28)
    add_volume(eye_r_s, "eye_r", "right eye", "eye", "detail", 6, kind="disc", resample=28)

    present = {c["id"] for c in comps}
    rels = [
        {"type": "above", "a": "head", "b": "body", "detail": "head overlaps the body but stays a separate mesh"},
        {"type": "sits_on", "a": "ear_l", "b": "head", "detail": "left ear is not fused into the skull"},
        {"type": "sits_on", "a": "ear_r", "b": "head", "detail": "right ear is not fused into the skull"},
        {"type": "on_face", "a": "eye_l", "b": "head", "detail": "user-drawn eye, proud of the face"},
        {"type": "on_face", "a": "eye_r", "b": "head", "detail": "user-drawn eye, proud of the face"},
    ]
    rels = [r for r in rels if r["a"] in present and r["b"] in present]

    # asymmetry note from eye positions
    if eye_l_s and eye_r_s:
        dl = centroid(eye_l_s["points"])
        dr = centroid(eye_r_s["points"])
        if abs(abs(dl[0]) - abs(dr[0])) > 0.01 or abs(dl[1] - dr[1]) > 0.01:
            notes.append("eyes are not perfectly symmetric; keep that")

    must = []
    if "head" in present:
        must.append("round head")
    if "body" in present:
        must.append("larger body under the head")
    if "ear_l" in present:
        must.append("left ear, separate from the head")
    if "ear_r" in present:
        must.append("right ear, separate from the head")
    if "eye_l" in present and "eye_r" in present:
        must.append("two eyes, count and rough placement")
    must.append("no extra face parts beyond what was drawn")

    return envelope(
        source_id=source_id,
        handler="teddy_v3",
        subject_hypothesis="teddy",
        confidence=confidence,
        orientation="upright",
        components=comps,
        relationships=rels,
        must=must,
        may=["soften silhouette wobble", "puff each part on its own"],
        never=[
            "fuse ears into the head",
            "invent a snout, nose, mouth, or smile",
            "invent a bow, belly badge, or clothing",
            "replace with a generic teddy render",
            "drop either eye",
        ],
        notes=" ".join(notes) if notes else "Parts mapped from stroke ids. Facial features = the two drawn eyes only.",
        camera_profile="teddy",
    )
