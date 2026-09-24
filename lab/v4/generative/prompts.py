"""Preserve-constraint prompts for the V4 generative renderer.

Ported from lab/v3/generative/prompts.py patterns. The model is asked to
polish the user's doodle, not replace it. When a style-reference image is
also sent, the prompt names it as IMAGE_1.
"""
from __future__ import annotations

import json


STYLE_COPY = {
    "gummy": (
        "soft inflated gelatin candy, translucent depth, internal volume, "
        "juicy rounded highlights, a few subtle bubbles trapped inside. "
        "Not glass, not metal, not fur."
    ),
    "clay": (
        "matte polymer clay / play-doh, softly sculpted, slight handmade imperfection, "
        "restrained highlights, no gloss coat. Not fur, not glass, not gummy."
    ),
    "plush": (
        "stuffed plush toy with a soft fiber pile and a tactile stitched feel. "
        "Puffy but clearly fabric, not smooth clay and not plastic."
    ),
    "glossy": (
        "smooth hard candy / resin / PVC, crisp controlled highlights, clean premium finish. "
        "Opaque, not translucent gummy, not matte clay, not fur."
    ),
}


def blueprint_summary(bp: dict) -> str:
    lines = [
        f"subject_hypothesis: {bp.get('subject_hypothesis')}",
        f"confidence: {bp.get('confidence')}",
        f"orientation: {bp.get('orientation')}",
        "components:",
    ]
    for c in bp.get("major_components") or []:
        strokes = ",".join(c.get("source_strokes") or []) or "none"
        flag = " completed" if c.get("completed") else ""
        lines.append(f"- {c['id']} ({c.get('name')}): role={c.get('role')} strokes={strokes}{flag}")
    lines.append("relationships:")
    for rel in bp.get("component_relationships") or []:
        if "a" in rel:
            lines.append(f"- {rel.get('type')}: {rel.get('a')} -> {rel.get('b')}. {rel.get('detail','')}")
        else:
            lines.append(f"- {rel.get('type')}: {rel.get('detail','')}")
    lines.append("features_must_preserve:")
    for item in bp.get("features_must_preserve") or []:
        lines.append(f"- {item}")
    lines.append("features_may_complete:")
    for item in bp.get("features_may_complete") or []:
        lines.append(f"- {item}")
    lines.append("features_must_never_invent:")
    for item in bp.get("features_must_never_invent") or []:
        lines.append(f"- {item}")
    return "\n".join(lines)


def build_edit_prompt(bp: dict, style: str, *, multi_image: bool = True) -> str:
    summary = blueprint_summary(bp)
    style_line = STYLE_COPY.get(style, style)
    if multi_image:
        style_block = (
            f"Style: {style}. Match the look of <IMAGE_1> (style reference): {style_line}\n"
            "Use <IMAGE_0> as the doodle to polish; transfer material/look cues from <IMAGE_1> "
            "without copying <IMAGE_1>'s subject silhouette."
        )
    else:
        style_block = f"Style: {style}. {style_line}"
    return (
        "POLISH THE USER'S DOODLE. Do not replace it with a generic object.\n"
        "Edit the provided doodle image into a single centered sticker on a transparent background.\n"
        f"{style_block}\n"
        "\n"
        "Hard preserve constraints:\n"
        "- Keep the subject identity implied by the doodle and the semantic blueprint.\n"
        "- Keep the silhouette, major part count, and part placement.\n"
        "- Keep distinctive proportions and the user's asymmetry. Do not mirror.\n"
        "- Do not remove a meaningful doodle feature.\n"
        "- Do not add arbitrary decoration, text, a background scene, a ground plane, "
        "or a drop shadow.\n"
        "- Do not invent a face, eyes, or a mouth unless the blueprint says those strokes exist.\n"
        "- If confidence is LOW, only clean up the existing strokes. Do not decide they are a star, "
        "animal, or any other object.\n"
        "\n"
        "Semantic blueprint:\n"
        f"{summary}\n"
    )


def build_request(
    bp: dict,
    style: str,
    doodle_png: str,
    *,
    style_ref_png: str | None = None,
    multi_image: bool = True,
) -> dict:
    use_multi = bool(multi_image and style_ref_png)
    prompt = build_edit_prompt(bp, style, multi_image=use_multi)
    req = {
        "style": style,
        "source_id": bp.get("source_id"),
        "doodle_png": doodle_png,
        "style_ref_png": style_ref_png,
        "multi_image": use_multi,
        "prompt": prompt,
        "blueprint_summary": blueprint_summary(bp),
        "negative": [
            "generic replacement object",
            "extra parts not in the blueprint",
            "text",
            "background",
            "ground plane",
            "invented face",
            "melted or fused fins/ears",
        ],
    }
    return req


def dumps_request(req: dict) -> str:
    return json.dumps(req, indent=2)


GUMMY_FIDELITY_STYLE = (
    "Premium soft gummy/gelatin candy material: translucent depth, soft inflated volume, "
    "rich saturated color, subtle internal bubbles, wet controlled highlights, smooth polished "
    "edges, soft studio lighting. "
    "NO ground plane, NO cast shadow, NO background scene, NO visible hard extrusion, "
    "NO plastic toy look, NO jagged edges."
)

SUBJECT_FIDELITY_LINES = {
    "06_rocket": (
        "Subject cue (light naming only): rocket. "
        "Preserve the doodle's actual body, pointed nose, separate left/right fins, and window "
        "placement/count. Polish the user's rocket — do not redesign into a generic NASA rocket."
    ),
    "07_teddy": (
        "Subject cue (light naming only): teddy bear. "
        "Preserve the doodle's actual head, separate ears, body, and any drawn face marks "
        "(eyes only if present). Polish the user's teddy — do not invent snout/mouth/clothing "
        "or replace with a generic teddy."
    ),
    "09_rose": (
        "Subject cue (light naming only): rose/flower. "
        "Interpret as a flower while preserving the user's bloom silhouette, drawn spiral/swirl, "
        "stem, and leaf. Not a photorealistic generic rose petal stack."
    ),
}


def build_fidelity_prompt(
    *,
    source_id: str,
    variant: str,
    blueprint: dict | None = None,
    multi_image: bool = True,
) -> str:
    """Build a doodle-fidelity edit prompt for variant A (raw+gummy) or B (+blueprint text).

    PRIMARY visual source is always the raw doodle (IMAGE_0). Style ref is IMAGE_1 when
    multi_image. Blueprint (variant B) is textual guidance only — never an image.
    """
    variant = variant.upper().strip()
    if variant not in ("A", "B"):
        raise ValueError(f"variant must be A or B, got {variant!r}")

    subject_line = SUBJECT_FIDELITY_LINES.get(
        source_id,
        f"Subject cue from doodle id {source_id}: polish the user's drawing, do not redesign.",
    )

    if multi_image:
        style_block = (
            f"Material / look: match <IMAGE_1> (gummy style reference). {GUMMY_FIDELITY_STYLE}\n"
            "Use <IMAGE_0> as the PRIMARY visual source (the user's raw doodle). "
            "Transfer only material/look cues from <IMAGE_1>; do NOT copy <IMAGE_1>'s "
            "subject silhouette or star shape."
        )
    else:
        style_block = f"Material / look (text-described gummy): {GUMMY_FIDELITY_STYLE}"

    preserve_block = (
        "Product goal: the result must feel like \"my doodle, polished beautifully\" — "
        "NOT a generic AI object.\n"
        "Hard preserve:\n"
        "- Overall silhouette and distinctive proportions from the doodle.\n"
        "- Meaningful component relationships and user-specific asymmetry (do not mirror).\n"
        "- Important features that exist in the original doodle.\n"
        "- Clean up roughness; do not redesign.\n"
        "Do NOT invent:\n"
        "- Decorative elements, text, scenery, unrelated accessories, extra components.\n"
        "- Arbitrary facial features not present in the doodle.\n"
        "- Background scene, ground plane, or cast/drop shadow.\n"
    )

    parts = [
        "POLISH THE USER'S DOODLE. Do not replace it with a generic object.",
        "Edit into a single centered sticker on a transparent / empty studio background.",
        style_block,
        "",
        subject_line,
        "",
        preserve_block,
    ]

    if variant == "B":
        if blueprint is None:
            raise ValueError("variant B requires blueprint dict for textual guidance")
        summary = blueprint_summary(blueprint)
        parts.extend(
            [
                "",
                "Semantic blueprint (TEXT guidance only — structure hints; the doodle remains "
                "the visual source of truth):\n"
                f"{summary}",
            ]
        )
    # Variant A: explicitly no blueprint summary
    return "\n".join(parts).rstrip() + "\n"
