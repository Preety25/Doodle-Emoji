"""Preserve-constraint prompts for the generative renderer.

The model is asked to polish the user's doodle, not replace it.
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


def build_edit_prompt(bp: dict, style: str) -> str:
    summary = blueprint_summary(bp)
    style_line = STYLE_COPY.get(style, style)
    return (
        "POLISH THE USER'S DOODLE. Do not replace it with a generic object.\n"
        "Edit the provided doodle image into a single centered sticker on a transparent background.\n"
        f"Style: {style}. {style_line}\n"
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


def build_request(bp: dict, style: str, doodle_png: str) -> dict:
    prompt = build_edit_prompt(bp, style)
    return {
        "style": style,
        "source_id": bp.get("source_id"),
        "doodle_png": doodle_png,
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


def dumps_request(req: dict) -> str:
    return json.dumps(req, indent=2)
