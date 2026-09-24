"""V4 strict blueprint adapter: map V3 blueprint.json → four explicit fields.

Does NOT write into V3 files. Output is a new dict (and optionally written under
out/v4/ only by callers). Replaces permissive features_may_complete guidance
with observed / inferred / allowed_completion / forbidden_additions.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Soft subject labels only — never a license to invent geometry.
_SUBJECT_INFERRED: dict[str, list[str]] = {
    "06_rocket": ["subject hypothesis: rocket (label only)"],
    "07_teddy": ["subject hypothesis: teddy bear (label only)"],
}

# Extra hard bans when those parts were not observed in the doodle.
_SOURCE_EXTRA_FORBIDDEN: dict[str, list[str]] = {
    "06_rocket": [
        "flame",
        "exhaust",
        "exhaust flame",
        "fire plume",
        "thruster flame",
    ],
    "07_teddy": [
        "limbs",
        "arms",
        "legs",
        "mouth",
        "snout",
        "nose/snout not drawn",
        "smile",
    ],
}


def _component_label(c: dict) -> str:
    cid = c.get("id") or c.get("name") or "component"
    name = c.get("name") or cid
    role = c.get("role") or ""
    strokes = c.get("source_strokes") or []
    stroke_s = ",".join(strokes) if strokes else "none"
    return f"{cid} ({name}; role={role}; strokes={stroke_s})"


def _is_observed_component(c: dict) -> bool:
    """Observed = present in the doodle via source strokes, not a completed invention."""
    strokes = c.get("source_strokes") or []
    if c.get("completed") is True and not strokes:
        return False
    if not strokes:
        return False
    return True


def _mentions_unobserved_addition(item: str, observed_ids: set[str], observed_text: str) -> bool:
    """True if a may_complete item invents geometry not present in observed doodle parts."""
    low = item.lower()
    # Explicit "not drawn" / completed invention language
    if "not drawn" in low or "completed" in low and "not drawn" in low:
        return True
    # Flame / exhaust never observed on rocket
    if any(tok in low for tok in ("flame", "exhaust", "fire", "plume")):
        if "flame" not in observed_ids and "exhaust" not in observed_ids:
            return True
    # Limb / face inventing for teddy
    if any(tok in low for tok in ("arm", "leg", "limb", "mouth", "snout", "smile")):
        # if the token isn't already in observed component text, treat as addition
        if not any(tok in observed_text for tok in ("arm", "leg", "limb", "mouth", "snout")):
            return True
    # Pure polish of existing strokes is NOT an unobserved addition
    polish_markers = (
        "smooth",
        "soften",
        "puff",
        "corner",
        "silhouette wobble",
        "slightly",
    )
    if any(m in low for m in polish_markers) and "not drawn" not in low:
        return False
    return False


def _is_tight_structural_completion(item: str) -> bool:
    """Only allow polish already implied by observed strokes — never new parts."""
    low = item.lower()
    if "not drawn" in low:
        return False
    if any(tok in low for tok in ("flame", "exhaust", "arm", "leg", "limb", "mouth", "snout", "smile")):
        return False
    allow_markers = (
        "smooth",
        "soften",
        "corner",
        "silhouette wobble",
        "puff each part",
        "close",
        "nearly-closed",
        "nearly closed",
    )
    return any(m in low for m in allow_markers)


def v3_to_strict(bp: dict, *, source_id: str | None = None) -> dict[str, Any]:
    """Map a V3 blueprint dict to the four V4.1 strict fields (+ light provenance)."""
    sid = source_id or str(bp.get("source_id") or "")
    majors = list(bp.get("major_components") or [])
    preserve = list(bp.get("features_must_preserve") or [])
    may_complete = list(bp.get("features_may_complete") or [])
    never_invent = list(bp.get("features_must_never_invent") or [])

    observed_comps = [c for c in majors if _is_observed_component(c)]
    observed_ids = {str(c.get("id") or "") for c in observed_comps}
    observed_labels = [_component_label(c) for c in observed_comps]
    # Preserve lines that describe observed doodle structure also count as observed cues
    observed_from_preserve = list(preserve)

    observed_text = " ".join(observed_labels + observed_from_preserve).lower()

    # Soft hypotheses only (labels) — not geometry
    inferred = list(_SUBJECT_INFERRED.get(sid, []))
    hyp = bp.get("subject_hypothesis")
    if hyp and not any(str(hyp) in x for x in inferred):
        inferred.append(f"subject hypothesis: {hyp} (label only)")

    allowed: list[str] = []
    forbidden: list[str] = []

    # Never-invent always forbidden
    for item in never_invent:
        if item not in forbidden:
            forbidden.append(item)

    # may_complete items that were NOT observed → forbidden; tight polish → allowed
    for item in may_complete:
        if _mentions_unobserved_addition(item, observed_ids, observed_text):
            if item not in forbidden:
                forbidden.append(item)
        elif _is_tight_structural_completion(item):
            if item not in allowed:
                allowed.append(item)
        else:
            # Default conservative: if unclear, forbid rather than allow invention
            if item not in forbidden:
                forbidden.append(item)

    # Source-specific hard bans
    for extra in _SOURCE_EXTRA_FORBIDDEN.get(sid, []):
        # Avoid exact dupes; still add the short token so prompts are explicit
        if not any(extra.lower() == f.lower() for f in forbidden):
            # If a longer forbidden already covers it, still keep a crisp token
            forbidden.append(f"do not add: {extra}")

    # Rocket: flame in major_components with completed=True / empty strokes → forbid
    if sid == "06_rocket":
        for c in majors:
            if (c.get("id") or "").lower() in ("flame", "exhaust") or (c.get("role") or "").lower() in (
                "flame",
                "exhaust",
            ):
                if not _is_observed_component(c):
                    label = f"completed-but-not-drawn component: {_component_label(c)}"
                    if label not in forbidden:
                        forbidden.append(label)

    # Teddy: limbs/mouth/snout forbidden if not observed (always for this doodle)
    if sid == "07_teddy":
        if not any(tok in observed_ids for tok in ("arm_l", "arm_r", "arm", "leg_l", "leg_r", "leg", "limb")):
            for phrase in (
                "do not invent limbs/arms/legs (not observed in doodle)",
                "do not invent mouth or snout (not observed in doodle)",
            ):
                if phrase not in forbidden:
                    forbidden.append(phrase)

    strict = {
        "schema_version": "doodle.strict_blueprint.v4",
        "source_id": sid,
        "subject_hypothesis": bp.get("subject_hypothesis"),
        "confidence": bp.get("confidence"),
        "orientation": bp.get("orientation"),
        "observed_components": observed_labels,
        "observed_preserve_cues": observed_from_preserve,
        "inferred_components": inferred,
        "allowed_completion": allowed,  # empty or very tight by default
        "forbidden_additions": forbidden,
        "provenance": {
            "from_v3_blueprint": True,
            "v3_features_may_complete_discarded_as_permissive": True,
            "note": (
                "inferred_components are soft labels only — not a license to invent geometry. "
                "allowed_completion is empty or tight structural polish of observed strokes only."
            ),
        },
    }
    return strict


def load_v3_and_adapt(source_id: str, *, root: Path | None = None) -> dict[str, Any]:
    from lab.v4.blueprint import load_blueprint

    bp = load_blueprint(source_id, root=root)
    return v3_to_strict(bp, source_id=source_id)


def write_strict_blueprint(strict: dict, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(strict, indent=2) + "\n")
    return path


def strict_summary_for_prompt(strict: dict) -> str:
    """Format the four fields for prompt injection (no features_may_complete)."""
    lines = [
        f"subject_hypothesis: {strict.get('subject_hypothesis')} (label only)",
        f"confidence: {strict.get('confidence')}",
        f"orientation: {strict.get('orientation')}",
        "",
        "observed_components (MUST preserve — present in the doodle):",
    ]
    for item in strict.get("observed_components") or []:
        lines.append(f"- {item}")
    cues = strict.get("observed_preserve_cues") or []
    if cues:
        lines.append("observed_preserve_cues:")
        for item in cues:
            lines.append(f"- {item}")
    lines.append("")
    lines.append(
        "inferred_components (SOFT LABELS ONLY — do NOT invent geometry from these):"
    )
    inferred = strict.get("inferred_components") or []
    if not inferred:
        lines.append("- (none)")
    else:
        for item in inferred:
            lines.append(f"- {item}")
    lines.append("")
    lines.append(
        "allowed_completion (ONLY these; empty/tight — no new parts beyond observed strokes):"
    )
    allowed = strict.get("allowed_completion") or []
    if not allowed:
        lines.append("- (none — do not complete or invent any missing parts)")
    else:
        for item in allowed:
            lines.append(f"- {item}")
    lines.append("")
    lines.append("forbidden_additions (HARD BAN — never invent or add):")
    for item in strict.get("forbidden_additions") or []:
        lines.append(f"- {item}")
    return "\n".join(lines)
