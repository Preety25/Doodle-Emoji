"""Rocket handler: body, nose, window, left fin, right fin, optional small flame.

Fins stay separate meshes. Nose is split out of the body taper, not a new silhouette.
"""
from __future__ import annotations

from lab.v3.geom2d import bbox, centroid, pull_vertices_into, shoelace_area, span, split_tapered_nose
from lab.v3.handlers.common import by_id, envelope, tube_component, volume_component


def _largest(comps):
    return max(comps, key=lambda c: shoelace_area(c["points"]))


def handle_rocket(source_id, meta, components):
    ids = by_id(components)
    closed = [c for c in components if c.get("closed")]
    notes = []
    confidence = "HIGH"

    body_s = ids.get("body")
    if body_s is None and closed:
        body_s = _largest(closed)
        notes.append("body stroke id missing; used largest closed contour")
        confidence = "MEDIUM"
    if body_s is None:
        confidence = "LOW"
        return envelope(
            source_id=source_id,
            handler="rocket_v3",
            subject_hypothesis="rocket",
            confidence="LOW",
            orientation="as_drawn",
            components=[],
            relationships=[],
            must=[],
            may=[],
            never=["invent a rocket from an empty page"],
            notes="No closed contours.",
            camera_profile="rocket",
        )

    split = split_tapered_nose(body_s["points"])
    if split is None:
        confidence = "MEDIUM"
        notes.append("nose taper not split; body kept whole")
        body_pts = body_s["points"]
        nose_comp = None
    else:
        body_pts = split["body"]
        nose_comp = volume_component(
            id="nose",
            name="nose",
            role="nose",
            points=split["nose"],
            color=body_s.get("color") or "#90CAF9",
            source_strokes=[body_s["id"]],
            z_order=2,
            feature_scale="secondary",
            pin_points=[split["tip"]],
            notes="Split from the body stroke's upper taper. Separate mesh, embedded at the shoulders. Not a new silhouette.",
            resample=48,
        )

    body_comp = volume_component(
        id="body",
        name="body",
        role="body",
        points=body_pts,
        color=body_s.get("color") or "#90CAF9",
        source_strokes=[body_s["id"]],
        z_order=0,
        feature_scale="primary",
        notes="Fuselage only. Fins are not unioned into this mesh.",
        resample=80,
    )

    def fin_from(stroke, cid, name, side):
        if stroke is None:
            return None
        pulled = pull_vertices_into(stroke["points"], body_pts, amount=0.014, near=0.03)
        return volume_component(
            id=cid,
            name=name,
            role="fin",
            points=pulled,
            color=stroke.get("color") or "#EF5350",
            source_strokes=[stroke["id"]],
            z_order=1,
            feature_scale="secondary",
            pin_points=[],
            notes=f"{side} fin is its own mesh. Attachment edge is embedded a hair into the body so it reads connected, not fused.",
            resample=24,
        )

    fin_l_s = ids.get("fin_l")
    fin_r_s = ids.get("fin_r")
    if fin_l_s is None or fin_r_s is None:
        # geometric fallback inside this category only: small closed shapes flanking the body
        bcx, _ = centroid(body_pts)
        others = [c for c in closed if c is not body_s and c["id"] not in ("window",)]
        lefts = [c for c in others if centroid(c["points"])[0] < bcx]
        rights = [c for c in others if centroid(c["points"])[0] > bcx]
        if fin_l_s is None and lefts:
            fin_l_s = min(lefts, key=lambda c: centroid(c["points"])[0])
            notes.append("left fin assigned by flanking position")
            confidence = "MEDIUM"
        if fin_r_s is None and rights:
            fin_r_s = max(rights, key=lambda c: centroid(c["points"])[0])
            notes.append("right fin assigned by flanking position")
            confidence = "MEDIUM"
    fin_l = fin_from(fin_l_s, "fin_l", "left fin", "Left")
    fin_r = fin_from(fin_r_s, "fin_r", "right fin", "Right")
    if fin_l is None or fin_r is None:
        confidence = "MEDIUM" if confidence == "HIGH" else confidence
        notes.append("one or both fins missing from strokes")

    window_s = ids.get("window")
    window = None
    if window_s is not None:
        window = volume_component(
            id="window",
            name="window",
            role="window",
            points=window_s["points"],
            color=window_s.get("color") or "#BBDEFB",
            source_strokes=[window_s["id"]],
            z_order=4,
            feature_scale="detail",
            kind="disc",
            notes="Separate disc, proud of the body. Not boolean-cut and not melted in.",
            resample=40,
        )
    else:
        notes.append("no window stroke; not inventing one")
        confidence = "MEDIUM" if confidence == "HIGH" else confidence

    # Flame: the golden rocket has no flame stroke. A small exhaust is a
    # category completion, kept separate, and listed as may-complete — not as
    # something the user drew.
    flame = None
    x0, y0, x1, y1 = bbox(body_pts)
    bw, bh, _ = span(body_pts)
    cx = 0.5 * (x0 + x1)
    fw = bw * 0.62
    fh = bh * 0.18
    flame_poly = [
        [cx - fw * 0.5, y0 + bh * 0.02],
        [cx - fw * 0.42, y0 - fh * 0.35],
        [cx - fw * 0.12, y0 - fh * 0.72],
        [cx, y0 - fh],
        [cx + fw * 0.12, y0 - fh * 0.72],
        [cx + fw * 0.42, y0 - fh * 0.35],
        [cx + fw * 0.5, y0 + bh * 0.02],
    ]
    flame = volume_component(
        id="flame",
        name="flame",
        role="flame",
        points=flame_poly,
        color="#FF8A3D",
        source_strokes=[],
        z_order=1,
        feature_scale="secondary",
        completed=True,
        notes="NOT in the source strokes. Small separate exhaust tucked under the body, between the fins. Category completion, easy to reject.",
        resample=32,
    )
    notes.append("flame is a completion (no flame stroke in the doodle)")

    comps = [body_comp]
    if nose_comp:
        comps.append(nose_comp)
    if fin_l:
        comps.append(fin_l)
    if fin_r:
        comps.append(fin_r)
    if window:
        comps.append(window)
    if flame:
        comps.append(flame)

    # open strokes (if a user actually drew a flame) replace the completion
    for c in components:
        if c.get("closed"):
            continue
        if c["id"] in ("flame", "exhaust"):
            comps = [x for x in comps if x["id"] != "flame"]
            comps.append(
                tube_component(
                    id="flame",
                    name="flame",
                    role="flame",
                    points=c["points"],
                    color=c.get("color") or "#FF8A3D",
                    source_strokes=[c["id"]],
                    z_order=1,
                    feature_scale="secondary",
                    notes="User-drawn exhaust, kept as a tube.",
                )
            )
            notes.append("used drawn flame stroke instead of completion")

    rels = [
        {"type": "stacked_on", "a": "nose", "b": "body", "detail": "nose continues the body taper; meshes overlap only at the shoulder"},
        {"type": "flanking", "a": "fin_l", "b": "body", "detail": "left fin is a separate mesh, never unioned"},
        {"type": "flanking", "a": "fin_r", "b": "body", "detail": "right fin is a separate mesh, never unioned"},
        {"type": "proud_of", "a": "window", "b": "body", "detail": "window sits on the fuselage"},
        {"type": "below", "a": "flame", "b": "body", "detail": "exhaust under the base, between the fins"},
    ]
    rels = [r for r in rels if r["a"] in {c["id"] for c in comps} and r["b"] in {c["id"] for c in comps}]

    must = ["upright rocket", "body kept distinct from fins"]
    if nose_comp:
        must.append("pointed nose from the user's taper")
    if fin_l:
        must.append("left fin, separate")
    if fin_r:
        must.append("right fin, separate")
    if window:
        must.append("window placement and count (one)")
    must.append("user proportions of body vs fins")

    return envelope(
        source_id=source_id,
        handler="rocket_v3",
        subject_hypothesis="rocket",
        confidence=confidence,
        orientation="upright",
        components=comps,
        relationships=rels,
        must=must,
        may=[
            "small exhaust flame between the fins (not drawn — completed)",
            "smooth the body corners slightly",
        ],
        never=[
            "fuse either fin into the body",
            "add a second window, portholes, or a face",
            "add landing legs, stars, text, or a ground",
            "replace the doodle with a generic NASA rocket",
            "drop the nose point",
        ],
        notes=" ".join(notes) if notes else "Rocket parts mapped from stroke ids.",
        camera_profile="rocket",
    )
