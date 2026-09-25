"""V4.4 semantic lock — recognize each doodle once; reuse across all styles.

Loads V4.2 recognition under out/v4/v42/unseen/recognition/, enriches with
stroke-role fields for the V4.4 regression set, and writes updated JSONs
back into the recognition directory (same semantic identity for all styles).
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from lab.v4.stroke_roles import (
    PRIORITY_HIERARCHY,
    ROLE_ATTACHMENT,
    ROLE_BOUNDARY,
    ROLE_BROKEN_CONTOUR,
    ROLE_INDEPENDENT,
    ROLE_INTERIOR_MARK,
    ROLE_OPEN_STROKE,
    validate_stroke_roles,
)

ROOT = Path(__file__).resolve().parents[2]
RECOG_DIR = ROOT / "out" / "v4" / "v42" / "unseen" / "recognition"

# Exactly the V4.4 regression doodles
V44_CASE_IDS = ("u01", "u03", "u06", "u07", "u08")


def _sr(
    sid: str,
    role: str,
    description: str,
    *,
    parent_region: str | None = None,
    kind: str | None = None,
    auto_close: bool | None = None,
    close_and_smooth: bool | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    d: dict[str, Any] = {
        "id": sid,
        "role": role,
        "description": description,
    }
    if parent_region is not None:
        d["parent_region"] = parent_region
    if kind is not None:
        d["kind"] = kind
    if auto_close is not None:
        d["auto_close"] = auto_close
    if close_and_smooth is not None:
        d["close_and_smooth"] = close_and_smooth
    if notes is not None:
        d["notes"] = notes
    return d


# --- Per-doodle enrichment (stroke roles + face/color locks) ---------------

ENRICHMENTS: dict[str, dict[str, Any]] = {
    "u01": {
        "subject_hypothesis": "mug / cup with steam",
        "confidence": 0.9,
        "observed_components": [
            "cup body",
            "rim opening",
            "handle on right",
            "three steam wisps",
        ],
        "inferred_components": [
            "interior cavity",
            "handle thickness",
            "liquid surface implied by rim",
        ],
        "allowed_completion": [
            "round cup body",
            "close tiny rim gaps (broken contour)",
            "soft-volume steam as open wisps — do not close into loops",
        ],
        "forbidden_additions": [
            "saucer",
            "spoon",
            "face on mug",
            "eyes",
            "mouth",
            "cheeks",
            "blush",
            "table",
            "logo/text",
            "extra handles",
            "coffee beans",
            "decorative stickers not drawn",
        ],
        "faces_observed": False,
        "face_policy": "NO faces — doodle has no eyes/mouth/cheeks/blush; do not invent.",
        "color_lock": {
            "present": False,
            "notes": "monochrome black line doodle; may enrich depth/saturation of a single body color, but do not import style-sheet rainbow/multicolor palettes",
            "preserve_relationships": [],
        },
        "stroke_roles": [
            _sr("mug_body", ROLE_BOUNDARY, "U-shaped cup body silhouette"),
            _sr(
                "rim",
                ROLE_BROKEN_CONTOUR,
                "elliptical rim; tiny gaps at body junctions",
                close_and_smooth=True,
            ),
            _sr("handle", ROLE_ATTACHMENT, "C-shaped handle attached on right"),
            _sr(
                "steam_1",
                ROLE_OPEN_STROKE,
                "left steam wisp",
                kind="steam",
                auto_close=False,
            ),
            _sr(
                "steam_2",
                ROLE_OPEN_STROKE,
                "center steam wisp",
                kind="steam",
                auto_close=False,
            ),
            _sr(
                "steam_3",
                ROLE_OPEN_STROKE,
                "right steam wisp",
                kind="steam",
                auto_close=False,
            ),
        ],
    },
    "u03": {
        "subject_hypothesis": "character head / face with bangs",
        "confidence": 0.9,
        "observed_components": [
            "round head / hair mass outline",
            "zigzag bangs / hairline",
            "two eyes",
            "smiling mouth",
        ],
        "inferred_components": [
            "hair mass above bangs",
            "soft cheek volume (volume only — no painted blush unless drawn)",
        ],
        "allowed_completion": [
            "round head into solid volume",
            "keep bang zigzag peak count similar",
            "fill closed head region → volumetric (esp. glossy)",
        ],
        "forbidden_additions": [
            "body/neck",
            "hat",
            "ears not drawn",
            "glasses",
            "extra facial features beyond observed eyes+mouth",
            "invented blush/cheeks marks if not drawn",
            "text",
            "background scene",
        ],
        "faces_observed": True,
        "face_policy": (
            "Faces ARE observed (two eyes + smile). Preserve eyes and mouth. "
            "Do not invent extra features (blush/cheeks marks) unless drawn."
        ),
        "color_lock": {
            "present": False,
            "notes": "monochrome black line doodle; single-family body color OK; no sheet palette import",
            "preserve_relationships": [],
        },
        "stroke_roles": [
            _sr(
                "head_outline",
                ROLE_BOUNDARY,
                "outer head/hair silhouette (closed or near-closed)",
            ),
            _sr(
                "bangs_zigzag",
                ROLE_INTERIOR_MARK,
                "zigzag bangs/hairline inside head region",
                parent_region="head_outline",
                kind="hairline",
                notes="interior surface mark on head — not an independent ribbon",
            ),
            _sr(
                "eye_left",
                ROLE_INDEPENDENT,
                "left eye (observed face mark)",
                kind="eye",
            ),
            _sr(
                "eye_right",
                ROLE_INDEPENDENT,
                "right eye (observed face mark)",
                kind="eye",
            ),
            _sr(
                "mouth",
                ROLE_OPEN_STROKE,
                "smiling mouth curve",
                kind="smile",
                auto_close=False,
            ),
        ],
        "glossy_construction": (
            "HARD: fully reconstruct as SOLID opaque polished resin/vinyl head — "
            "fill closed regions → volumetric → clearcoat. NEVER wireframe/outline/"
            "line sculpture/gray extruded line/hollow contour/tube drawing."
        ),
    },
    "u06": {
        # CRITICAL fix vs V4.2: was wrongly "zigzag line / grassy squiggle"
        "subject_hypothesis": "mug / cup with steam and interior green zigzag surface mark",
        "confidence": 0.92,
        "observed_components": [
            "cup body",
            "rim opening",
            "handle on right",
            "three steam wisps",
            "green zigzag stroke inside mug body (~4 peaks)",
        ],
        "inferred_components": [
            "interior cavity",
            "handle thickness",
            "zigzag as painted/molded surface decoration on mug body (NOT independent object)",
        ],
        "allowed_completion": [
            "round cup body",
            "close tiny rim gaps",
            "keep zigzag peak count ~4 as surface mark on mug",
            "steam as open wisps — do not close",
        ],
        "forbidden_additions": [
            "treating zigzag as independent floating ribbon/tube/snake/grass",
            "saucer",
            "spoon",
            "face on mug",
            "eyes",
            "mouth",
            "cheeks",
            "blush",
            "table",
            "logo/text",
            "extra handles",
            "flowers",
            "ground scene",
            "turning zigzag into a creature",
        ],
        "faces_observed": False,
        "face_policy": "NO faces — doodle has no eyes/mouth/cheeks/blush; do not invent.",
        "color_lock": {
            "present": True,
            "notes": (
                "preserve important color relationship: structural mug strokes are black; "
                "interior zigzag is muted green. Enrich saturation/depth OK; do NOT import "
                "style-sheet rainbow/multicolor palettes onto the zigzag or mug."
            ),
            "preserve_relationships": [
                "mug body/handle/steam stay in dark/neutral family (or single enriched body color)",
                "zigzag stays green family",
            ],
        },
        "stroke_roles": [
            _sr("mug_body", ROLE_BOUNDARY, "U-shaped cup body silhouette"),
            _sr(
                "rim",
                ROLE_BROKEN_CONTOUR,
                "elliptical rim; tiny gaps at body junctions",
                close_and_smooth=True,
            ),
            _sr("handle", ROLE_ATTACHMENT, "C-shaped handle attached on right"),
            _sr(
                "interior_zigzag",
                ROLE_INTERIOR_MARK,
                "green zigzag (~4 peaks) substantially INSIDE mug body",
                parent_region="mug_body",
                kind="surface_decoration",
                notes=(
                    "CRITICAL: this is an INTERIOR SURFACE MARK on the mug — "
                    "NEVER an independent green ribbon/tube/grass blade"
                ),
            ),
            _sr(
                "steam_1",
                ROLE_OPEN_STROKE,
                "left steam wisp",
                kind="steam",
                auto_close=False,
            ),
            _sr(
                "steam_2",
                ROLE_OPEN_STROKE,
                "center steam wisp",
                kind="steam",
                auto_close=False,
            ),
            _sr(
                "steam_3",
                ROLE_OPEN_STROKE,
                "right steam wisp",
                kind="steam",
                auto_close=False,
            ),
        ],
        "v42_correction": (
            "V4.2 wrongly labeled this as standalone zigzag/grass. "
            "V4.4 semantic lock: mug + interior zigzag surface mark."
        ),
    },
    "u07": {
        "subject_hypothesis": "person with wide-brim / floppy hat (hat-person)",
        "confidence": 0.9,
        "observed_components": [
            "round head / face disk",
            "interior face marks (eyes / smile marks)",
            "wide hat with multiple brim/petal-like loops around head",
            "pill / stem-like torso",
            "two arm / side loops",
            "leg / lower taper",
        ],
        "inferred_components": [
            "hat crown volume on head",
            "limb softness",
            "face volume",
        ],
        "allowed_completion": [
            "round head/torso into soft volumes",
            "close small gaps in hat-brim loops (broken contours)",
            "keep hat as wide brim around head — still a PERSON wearing a hat",
        ],
        "forbidden_additions": [
            "reinterpreting as a flower / plant / blossom (HARD BAN — clay sheet has flowers)",
            "extra accessories not drawn",
            "shoes details not drawn",
            "background scene",
            "text",
            "second person",
            "replacing limbs with leaves-only plant reading",
        ],
        "faces_observed": True,
        "face_policy": (
            "Faces ARE observed (marks inside head disk). Preserve as person face. "
            "Identity LOCK: hat-person — NEVER flower."
        ),
        "identity_lock": (
            "HARD IDENTITY LOCK: this is a PERSON WITH A HAT, not a flower. "
            "Clay/plush/glossy/gummy style sheets that contain flowers must NOT "
            "change subject identity. Wide loops = hat brim; torso+arms+legs = body."
        ),
        "color_lock": {
            "present": False,
            "notes": "monochrome; single-family enrichment OK; no sheet palette takeover",
            "preserve_relationships": [],
        },
        "stroke_roles": [
            _sr("head", ROLE_BOUNDARY, "round head / face disk"),
            _sr(
                "face_marks",
                ROLE_INTERIOR_MARK,
                "small marks inside head (eyes/smile)",
                parent_region="head",
                kind="face",
            ),
            _sr(
                "hat_brim_loops",
                ROLE_BOUNDARY,
                "wide hat brim loops around head (may look petal-like but are HAT)",
                notes="do not reinterpret as flower petals",
            ),
            _sr(
                "hat_loop_gaps",
                ROLE_BROKEN_CONTOUR,
                "small gaps in some hat brim loops",
                close_and_smooth=True,
            ),
            _sr("torso", ROLE_BOUNDARY, "pill / stem-like torso under head"),
            _sr("arm_left", ROLE_ATTACHMENT, "left arm / side loop on torso"),
            _sr("arm_right", ROLE_ATTACHMENT, "right arm / side loop on torso"),
            _sr(
                "legs",
                ROLE_BOUNDARY,
                "lower taper / legs",
            ),
        ],
    },
    "u08": {
        "subject_hypothesis": "three-pronged plant / sapling with three round tops",
        "confidence": 0.9,
        "observed_components": [
            "vertical stem",
            "left branch with round top",
            "right branch with round top",
            "center stem with round top",
        ],
        "inferred_components": [
            "stem tube thickness",
            "round canopy / fruit / bud spheres",
        ],
        "allowed_completion": [
            "round the three tops into soft spheres",
            "soften branch junctions",
            "keep exactly three tops",
        ],
        "forbidden_additions": [
            "extra branches/tops",
            "pot",
            "ground scene",
            "face on tops",
            "eyes",
            "mouth",
            "cheeks",
            "blush",
            "text",
            "more than three tops",
            "importing rainbow / RGB / multicolor style-sheet palette onto the three tops",
        ],
        "faces_observed": False,
        "face_policy": "NO faces on tops — doodle has none; do not invent.",
        "color_lock": {
            "present": False,
            "notes": (
                "monochrome doodle. Enrich depth/saturation of a coherent plant palette OK "
                "(e.g. greens), but HARD BAN on importing glossy-sheet rainbow/RGB/"
                "multicolor candy palette (pink/yellow/blue/etc.) onto the three tops."
            ),
            "preserve_relationships": [
                "three tops should share a coherent family — not RGB primaries from sheet",
            ],
        },
        "stroke_roles": [
            _sr("stem", ROLE_BOUNDARY, "vertical main stem"),
            _sr(
                "branch_left",
                ROLE_ATTACHMENT,
                "left branch connector to left top",
            ),
            _sr(
                "branch_right",
                ROLE_ATTACHMENT,
                "right branch connector to right top",
            ),
            _sr(
                "top_left",
                ROLE_INDEPENDENT,
                "left round top / canopy / bud",
            ),
            _sr(
                "top_center",
                ROLE_INDEPENDENT,
                "center round top / canopy / bud",
            ),
            _sr(
                "top_right",
                ROLE_INDEPENDENT,
                "right round top / canopy / bud",
            ),
        ],
    },
}


def load_base_recognition(uid: str, recog_dir: Path | None = None) -> dict:
    path = (recog_dir or RECOG_DIR) / f"{uid}_recognition.json"
    return json.loads(path.read_text())


def build_locked_recognition(uid: str, recog_dir: Path | None = None) -> dict:
    """Merge V4.2 base + V4.4 enrichment into a single locked recognition dict."""
    if uid not in ENRICHMENTS:
        raise KeyError(f"{uid} not in V4.4 enrichment set {V44_CASE_IDS}")
    base = load_base_recognition(uid, recog_dir)
    enrich = ENRICHMENTS[uid]
    locked = deepcopy(base)
    locked.update(deepcopy(enrich))
    locked["id"] = uid
    locked["semantic_lock_version"] = "v4.4"
    locked["priority_hierarchy"] = list(PRIORITY_HIERARCHY)
    locked["same_semantics_all_styles"] = True
    warnings = validate_stroke_roles(locked.get("stroke_roles") or [])
    locked["stroke_role_validation_warnings"] = warnings
    return locked


def write_locked_recognition(
    uid: str,
    *,
    recog_dir: Path | None = None,
    also_copy_to: Path | None = None,
) -> dict:
    """Update recognition JSON in-place under v42 recognition dir; optional copy."""
    recog_dir = recog_dir or RECOG_DIR
    locked = build_locked_recognition(uid, recog_dir)
    out_path = recog_dir / f"{uid}_recognition.json"
    out_path.write_text(json.dumps(locked, indent=2) + "\n")
    if also_copy_to is not None:
        also_copy_to.parent.mkdir(parents=True, exist_ok=True)
        also_copy_to.write_text(json.dumps(locked, indent=2) + "\n")
    return locked


def update_index(recog_dir: Path | None = None) -> dict:
    """Refresh INDEX.json hypotheses for enriched ids (leave others intact)."""
    recog_dir = recog_dir or RECOG_DIR
    index_path = recog_dir / "INDEX.json"
    index = json.loads(index_path.read_text()) if index_path.is_file() else {}
    for uid in V44_CASE_IDS:
        locked = build_locked_recognition(uid, recog_dir)
        index[uid] = {
            "hypothesis": locked.get("subject_hypothesis"),
            "confidence": locked.get("confidence"),
            "semantic_lock_version": "v4.4",
            "faces_observed": locked.get("faces_observed"),
        }
    index_path.write_text(json.dumps(index, indent=2) + "\n")
    return index


def ensure_v44_locks(recog_dir: Path | None = None) -> dict[str, dict]:
    """Write all five locked recognitions + update index. Return map uid→locked."""
    out: dict[str, dict] = {}
    for uid in V44_CASE_IDS:
        out[uid] = write_locked_recognition(uid, recog_dir=recog_dir)
    update_index(recog_dir)
    return out
