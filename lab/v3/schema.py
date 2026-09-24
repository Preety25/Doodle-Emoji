"""Blueprint schema for V3 semantic reconstruction."""
from __future__ import annotations

REQUIRED_TOP = (
    "schema_version",
    "source_id",
    "subject_hypothesis",
    "confidence",
    "orientation",
    "major_components",
    "component_relationships",
    "features_must_preserve",
    "features_may_complete",
    "features_must_never_invent",
)

REQUIRED_COMPONENT = (
    "id",
    "name",
    "source_strokes",
    "kind",
)


def validate_blueprint(bp: dict) -> list[str]:
    errors = []
    for key in REQUIRED_TOP:
        if key not in bp:
            errors.append(f"missing {key}")
    if bp.get("schema_version") != "doodle.blueprint.v3":
        errors.append("schema_version must be doodle.blueprint.v3")
    conf = bp.get("confidence")
    if conf not in ("HIGH", "MEDIUM", "LOW"):
        errors.append(f"confidence invalid: {conf}")
    comps = bp.get("major_components") or []
    if not isinstance(comps, list) or not comps:
        errors.append("major_components empty")
    ids = set()
    for c in comps:
        for key in REQUIRED_COMPONENT:
            if key not in c:
                errors.append(f"component missing {key}")
        cid = c.get("id")
        if cid in ids:
            errors.append(f"duplicate component id {cid}")
        ids.add(cid)
        if "source_strokes" in c and not isinstance(c["source_strokes"], list):
            errors.append(f"{cid} source_strokes not a list")
        kind = c.get("kind")
        if kind in ("closed_volume", "disc") and not c.get("polygon"):
            errors.append(f"{cid} closed component has no polygon")
        if kind == "open_tube" and not c.get("path"):
            errors.append(f"{cid} tube has no path")
    for rel in bp.get("component_relationships") or []:
        if "type" not in rel:
            errors.append("relationship missing type")
    for bucket in (
        "features_must_preserve",
        "features_may_complete",
        "features_must_never_invent",
    ):
        if not isinstance(bp.get(bucket), list):
            errors.append(f"{bucket} must be a list")
    return errors
