"""Controlled doodle-fidelity experiment: 6 xAI image edits (3 doodles × A/B).

Variants per doodle id:
  A — RAW DOODLE + GUMMY STYLE REFERENCE (no blueprint text)
  B — RAW DOODLE + V3 SEMANTIC BLUEPRINT (text) + GUMMY STYLE REFERENCE

PRIMARY image is always the raw doodle. Blueprint is never sent as an image.
Stops after exactly 6 generation attempts (shape-error retries only inside adapter).

Usage:
  python3 -m lab.v4.doodle_fidelity_test

Requires env XAI_API_KEY. Exit 2 if unset. Does not print or write the key.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from lab.v4.blueprint import blueprint_path, doodle_path, load_blueprint
from lab.v4.generative.prompts import build_fidelity_prompt
from lab.v4.generative.xai_edit import (
    DEFAULT_N,
    DEFAULT_QUALITY,
    DEFAULT_RESOLUTION,
    MODEL,
    approx_cost_usd,
    edit_image,
    has_xai_key,
)

ROOT = Path(__file__).resolve().parents[2]

STYLE_REF = ROOT / "docs" / "refs" / "ref2_gummy_star_gradient.png"
OUT_ROOT = ROOT / "out" / "v4" / "tests"

CASES = (
    "06_rocket",
    "07_teddy",
    "09_rose",
)
VARIANTS = ("A", "B")
VARIANT_DIRS = {
    "A": "A_raw_gummy",
    "B": "B_raw_blueprint_gummy",
}


def _write_meta(path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Never persist anything that could be a key
    blob = json.dumps(meta, indent=2)
    assert "XAI_API_KEY" not in blob
    assert "Bearer " not in blob or "Bearer [REDACTED]" in blob
    path.write_text(blob)


def run_one(source_id: str, variant: str) -> dict:
    variant = variant.upper()
    vdir = VARIANT_DIRS[variant]
    out_dir = OUT_ROOT / source_id / vdir
    out_dir.mkdir(parents=True, exist_ok=True)

    doodle = doodle_path(source_id, root=ROOT)
    bp_path = blueprint_path(source_id, root=ROOT)
    bp = load_blueprint(source_id, root=ROOT) if variant == "B" else None

    # Copy artifacts into output layout
    src_copy = out_dir / "source_doodle.png"
    shutil.copy2(doodle, src_copy)
    style_copy = out_dir / "style_ref.png"
    shutil.copy2(STYLE_REF, style_copy)
    if variant == "B":
        bp_copy = out_dir / "blueprint.json"
        shutil.copy2(bp_path, bp_copy)
    else:
        bp_copy = None

    prompt = build_fidelity_prompt(
        source_id=source_id,
        variant=variant,
        blueprint=bp,
        multi_image=True,
    )
    (out_dir / "prompt.txt").write_text(prompt)

    out_png = out_dir / "edited.png"
    result = edit_image(
        doodle_path=doodle,
        style_ref_path=STYLE_REF,
        prompt=prompt,
        out_png=out_png,
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
        n=DEFAULT_N,
        prefer_multi_image=True,
        allow_single_fallback=False,  # fidelity test: no extra single-image generation
    )

    # If adapter fell through to single-image, that still counts as the generation
    # for this config; we do not re-call.
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
        "variant": variant,
        "source_id": source_id,
        "source_doodle": {
            "path": str(doodle),
            "filename": doodle.name,
            "copied_as": src_copy.name,
        },
        "style_ref": {
            "path": str(STYLE_REF),
            "filename": STYLE_REF.name,
            "copied_as": style_copy.name,
        },
        "blueprint": (
            {
                "path": str(bp_path),
                "filename": bp_path.name,
                "copied_as": bp_copy.name if bp_copy else None,
            }
            if variant == "B"
            else None
        ),
        "prompt": prompt,
        "http_status": result.get("http_status"),
        "latency_ms": result.get("latency_ms"),
        "approx_cost_usd": result.get("approx_cost_usd"),
        "cost_estimate": cost_info,
        "api_response": {
            "model_returned": result.get("model_returned"),
            "respect_moderation": result.get("respect_moderation"),
            "response_format_used": result.get("response_format_used"),
            "attempt_label": result.get("attempt_label"),
            "fallback_single_image": bool(result.get("fallback_single_image")),
            "attempts": result.get("attempts"),
            "output_bytes": result.get("output_bytes"),
        },
        "output_png": str(out_png) if result.get("ok") else None,
        "error": None if result.get("ok") else result.get("error"),
    }
    _write_meta(out_dir / "metadata.json", meta)

    summary = {
        "source_id": source_id,
        "variant": variant,
        "success": meta["success"],
        "image_path": str(out_png) if meta["success"] else None,
        "approx_cost_usd": meta["approx_cost_usd"] or cost_info.get("approx_cost_usd"),
        "http_status": meta["http_status"],
        "error": meta["error"],
        "out_dir": str(out_dir),
        "attempt_label": (meta.get("api_response") or {}).get("attempt_label"),
        "fallback_single_image": (meta.get("api_response") or {}).get("fallback_single_image"),
    }
    return summary


def main() -> int:
    if not has_xai_key():
        print("error: XAI_API_KEY unset; refusing to run (exit 2).", file=sys.stderr)
        return 2

    missing = [p for p in (STYLE_REF,) if not p.is_file()]
    for sid in CASES:
        d = doodle_path(sid, root=ROOT)
        b = blueprint_path(sid, root=ROOT)
        if not d.is_file():
            missing.append(d)
        if not b.is_file():
            missing.append(b)
    if missing:
        print(f"error: missing inputs: {', '.join(str(p) for p in missing)}", file=sys.stderr)
        return 3

    results: list[dict] = []
    # Exactly 6 configs, sequential. No extras beyond adapter-internal shape retry.
    for sid in CASES:
        for variant in VARIANTS:
            print(f"=== running {sid} variant {variant} ===", flush=True)
            summary = run_one(sid, variant)
            results.append(summary)
            print(
                f"  success={summary['success']} http={summary['http_status']} "
                f"cost={summary['approx_cost_usd']} attempt={summary.get('attempt_label')}",
                flush=True,
            )
            if summary.get("error"):
                print(f"  error={summary['error']}", flush=True)

    report = {
        "total": len(results),
        "success_count": sum(1 for r in results if r["success"]),
        "failure_count": sum(1 for r in results if not r["success"]),
        "results": results,
        "approx_total_cost_usd": round(
            sum(float(r["approx_cost_usd"] or 0) for r in results if r["success"]), 4
        ),
    }
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "run_summary.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["success_count"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
