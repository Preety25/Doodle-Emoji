"""One-shot smoke: 02_heart × gummy via xAI image edit.

Usage:
  python3 -m lab.v4.smoke_heart_gummy

Requires env XAI_API_KEY. Refuses to run (nonzero exit) if unset — no stub
fake success image. Does not print or write the API key.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from lab.v4.blueprint import doodle_path, load_blueprint
from lab.v4.generative.prompts import build_edit_prompt
from lab.v4.generative.xai_edit import (
    MODEL,
    DEFAULT_N,
    DEFAULT_QUALITY,
    DEFAULT_RESOLUTION,
    approx_cost_usd,
    edit_image,
    has_xai_key,
)

ROOT = Path(__file__).resolve().parents[2]

SOURCE_ID = "02_heart"
STYLE = "gummy"
STYLE_REF = ROOT / "docs" / "refs" / "ref2_gummy_star_gradient.png"

# Prefer gitignored smoke dir under the repo; also mirror path note for /workspace/v4-smoke.
OUT_DIR = ROOT / "out" / "v4" / "smoke" / "02_heart_gummy"
OUT_PNG = OUT_DIR / "edited.png"
OUT_META = OUT_DIR / "metadata.json"


def main() -> int:
    if not has_xai_key():
        print("success: false")
        print("error: XAI_API_KEY unset; refusing to run (no stub image).")
        print(f"image_path: ")
        print(f"approx_cost_usd: ")
        return 2

    doodle = doodle_path(SOURCE_ID, root=ROOT)
    try:
        bp = load_blueprint(SOURCE_ID, root=ROOT)
    except FileNotFoundError as exc:
        print("success: false")
        print(f"error: {exc}")
        print("image_path: ")
        print("approx_cost_usd: ")
        return 3

    missing = [p for p in (doodle, STYLE_REF) if not p.is_file()]
    if missing:
        print("success: false")
        print(f"error: missing required input(s): {', '.join(str(p) for p in missing)}")
        print("image_path: ")
        print("approx_cost_usd: ")
        return 3

    # Multi-image prompt (doodle = IMAGE_0, style ref = IMAGE_1)
    prompt = build_edit_prompt(bp, STYLE, multi_image=True)

    result = edit_image(
        doodle_path=doodle,
        style_ref_path=STYLE_REF,
        prompt=prompt,
        out_png=OUT_PNG,
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
        n=DEFAULT_N,
        prefer_multi_image=True,
    )

    # If multi-image failed and adapter fell through to single-image with the
    # multi prompt still naming IMAGE_1, retry once with a text-only style prompt
    # when the last successful path was not taken.
    if not result.get("ok"):
        # Adapter already tried single-image with the multi prompt. Retry cleanly
        # with a single-image style-described prompt.
        prompt_single = build_edit_prompt(bp, STYLE, multi_image=False)
        result = edit_image(
            doodle_path=doodle,
            style_ref_path=None,
            prompt=prompt_single,
            out_png=OUT_PNG,
            resolution=DEFAULT_RESOLUTION,
            quality=DEFAULT_QUALITY,
            n=DEFAULT_N,
            prefer_multi_image=False,
        )
        if result.get("ok"):
            result["fallback_single_image"] = True
            result["note"] = "multi-image failed; succeeded with doodle-only + style in prompt"

    cost_info = result.get("cost_estimate") or approx_cost_usd(
        n_input_images=1 if result.get("fallback_single_image") else 2,
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
    )

    meta = {
        "success": bool(result.get("ok")),
        "model": MODEL,
        "resolution": DEFAULT_RESOLUTION,
        "quality": DEFAULT_QUALITY,
        "n": DEFAULT_N,
        "prompt": result.get("prompt") or prompt,
        "input_doodle": str(doodle),
        "input_style_ref": str(STYLE_REF),
        "blueprint": str(ROOT / "out" / "v3" / SOURCE_ID / "blueprint.json"),
        "output_png": str(OUT_PNG) if result.get("ok") else None,
        "api": {
            "http_status": result.get("http_status"),
            "latency_ms": result.get("latency_ms"),
            "model_returned": result.get("model_returned"),
            "respect_moderation": result.get("respect_moderation"),
            "response_format_used": result.get("response_format_used"),
            "attempt_label": result.get("attempt_label"),
            "fallback_single_image": bool(result.get("fallback_single_image")),
            "attempts": result.get("attempts"),
        },
        "approx_cost_usd": result.get("approx_cost_usd"),
        "cost_estimate": cost_info,
        "error": None if result.get("ok") else result.get("error"),
    }
    # Never persist anything that could be a key
    assert "XAI_API_KEY" not in json.dumps(meta)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_META.write_text(json.dumps(meta, indent=2))

    print(f"success: {'true' if result.get('ok') else 'false'}")
    print(f"image_path: {OUT_PNG if result.get('ok') else ''}")
    print(f"approx_cost_usd: {result.get('approx_cost_usd') if result.get('ok') else cost_info.get('approx_cost_usd')}")
    if not result.get("ok"):
        print(f"error: {result.get('error')}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
