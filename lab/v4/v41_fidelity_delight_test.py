"""V4.1 AI Fidelity + Delight Pass: exactly 4 xAI edits (rocket/teddy × A/B).

Variants:
  A — RAW DOODLE + Jelly-Gummy style refs only (NO semantic blueprint text)
  B — RAW DOODLE + STRICT four-field constraints + Jelly-Gummy style refs

PRIMARY image is always the raw doodle. Stops after exactly 4 generation attempts
(shape-error retries only inside the xai_edit adapter).

Usage:
  python3 -m lab.v4.v41_fidelity_delight_test
  # or: python3 scripts/v4_v41_fidelity_delight_test.py

Requires env XAI_API_KEY. Exit 2 if unset. Does not print or write the key.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lab.v4.blueprint import blueprint_path, doodle_path, load_blueprint
from lab.v4.generative.prompts import build_fidelity_v41_prompt
from lab.v4.generative.xai_edit import (
    DEFAULT_N,
    DEFAULT_QUALITY,
    DEFAULT_RESOLUTION,
    MODEL,
    approx_cost_usd,
    edit_image,
    has_xai_key,
)
from lab.v4.strict_blueprint import v3_to_strict, write_strict_blueprint

ROOT = Path(__file__).resolve().parents[2]

STYLE_ROCKET = ROOT / "docs" / "refs" / "jelly_gummy" / "ref_jelly_gummy_rocket.png"
STYLE_FLOWER = ROOT / "docs" / "refs" / "jelly_gummy" / "ref_jelly_gummy_flower.png"
# Prefer BOTH style refs; adapter falls back to first-only on 422.
STYLE_REFS_BOTH = [STYLE_ROCKET, STYLE_FLOWER]
# Per-source preferred first ref if API accepts only 2 images total
STYLE_PRIMARY_FOR = {
    "06_rocket": STYLE_ROCKET,
    "07_teddy": STYLE_FLOWER,
}

OUT_ROOT = ROOT / "out" / "v4" / "v41"

CASES = ("06_rocket", "07_teddy")
VARIANTS = ("A", "B")
VARIANT_DIRS = {
    "A": "A_raw_jelly",
    "B": "B_strict_jelly",
}


def _write_meta(path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(meta, indent=2)
    assert "XAI_API_KEY" not in blob
    assert "Bearer " not in blob or "Bearer [REDACTED]" in blob
    path.write_text(blob + "\n")


def _style_paths_for(source_id: str) -> list[Path]:
    """Order style refs: preferred primary first, then the other — try both."""
    primary = STYLE_PRIMARY_FOR[source_id]
    other = STYLE_FLOWER if primary == STYLE_ROCKET else STYLE_ROCKET
    return [primary, other]


def run_one(source_id: str, variant: str) -> dict:
    variant = variant.upper()
    vdir = VARIANT_DIRS[variant]
    out_dir = OUT_ROOT / source_id / vdir
    out_dir.mkdir(parents=True, exist_ok=True)

    doodle = doodle_path(source_id, root=ROOT)
    bp_path = blueprint_path(source_id, root=ROOT)
    style_paths = _style_paths_for(source_id)

    src_copy = out_dir / "source_doodle.png"
    shutil.copy2(doodle, src_copy)

    # Copy style refs into out dir for provenance (paths also recorded in meta)
    style_copies = []
    for i, sp in enumerate(style_paths):
        dest = out_dir / f"style_ref_{i}_{sp.name}"
        shutil.copy2(sp, dest)
        style_copies.append(dest)

    strict = None
    strict_path = None
    if variant == "B":
        v3_bp = load_blueprint(source_id, root=ROOT)
        strict = v3_to_strict(v3_bp, source_id=source_id)
        strict_path = out_dir / "strict_blueprint.json"
        write_strict_blueprint(strict, strict_path)

    # Build prompt assuming both style refs; if adapter falls back to 1, prompt
    # still mentions IMAGE_1 which remains correct (IMAGE_2 unused but harmless).
    # Prefer documenting actual n_style_refs from result afterward in meta.
    prompt = build_fidelity_v41_prompt(
        variant=variant,
        source_id=source_id,
        strict_bp=strict,
        multi_image=True,
        n_style_refs=2,
    )
    (out_dir / "prompt.txt").write_text(prompt)

    out_png = out_dir / "edited.png"
    result = edit_image(
        doodle_path=doodle,
        style_ref_paths=style_paths,
        prompt=prompt,
        out_png=out_png,
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
        n=DEFAULT_N,
        prefer_multi_image=True,
        allow_single_fallback=False,  # fidelity test: no extra single-image generation
    )

    n_in = result.get("n_input_images")
    if n_in is None:
        refs_used = result.get("input_style_refs") or []
        n_in = 1 + len(refs_used) if result.get("ok") else 3
    cost_info = result.get("cost_estimate") or approx_cost_usd(
        n_input_images=int(n_in),
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
    )

    refs_used = result.get("input_style_refs") or [str(p) for p in style_paths]
    # Document which refs actually went to the API
    style_mode = "both_jelly_refs"
    if result.get("ok") and int(n_in or 0) == 2:
        style_mode = f"doodle_plus_primary_only ({Path(refs_used[0]).name if refs_used else 'unknown'})"
    elif result.get("ok") and int(n_in or 0) >= 3:
        style_mode = "doodle_plus_both_jelly_refs"

    meta = {
        "success": bool(result.get("ok")),
        "model": MODEL,
        "resolution": DEFAULT_RESOLUTION,
        "quality": DEFAULT_QUALITY,
        "n": DEFAULT_N,
        "variant": variant,
        "variant_dir": vdir,
        "source_id": source_id,
        "source_doodle": {
            "path": str(doodle),
            "filename": doodle.name,
            "copied_as": src_copy.name,
        },
        "style_refs": {
            "requested": [str(p) for p in style_paths],
            "used": refs_used,
            "mode": style_mode,
            "copied_as": [p.name for p in style_copies],
            "primary_for_source": str(STYLE_PRIMARY_FOR[source_id]),
            "note": (
                "Prefer BOTH jelly refs via images[]. If API accepts only 2 images total, "
                "adapter falls back to doodle + primary (rocket→jelly rocket, teddy→jelly flower)."
            ),
        },
        "strict_blueprint": (
            {
                "path": str(strict_path),
                "filename": strict_path.name if strict_path else None,
                "fields": [
                    "observed_components",
                    "inferred_components",
                    "allowed_completion",
                    "forbidden_additions",
                ],
            }
            if variant == "B"
            else None
        ),
        "v3_blueprint_read_only": str(bp_path),
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
            "n_input_images": n_in,
            "fallback_single_image": bool(result.get("fallback_single_image")),
            "attempts": result.get("attempts"),
            "output_bytes": result.get("output_bytes"),
        },
        "output_png": str(out_png) if result.get("ok") else None,
        "error": None if result.get("ok") else result.get("error"),
    }
    _write_meta(out_dir / "metadata.json", meta)

    return {
        "source_id": source_id,
        "variant": variant,
        "success": meta["success"],
        "image_path": str(out_png) if meta["success"] else None,
        "approx_cost_usd": meta["approx_cost_usd"] or cost_info.get("approx_cost_usd"),
        "http_status": meta["http_status"],
        "error": meta["error"],
        "out_dir": str(out_dir),
        "attempt_label": (meta.get("api_response") or {}).get("attempt_label"),
        "style_mode": style_mode,
        "n_input_images": n_in,
    }


def _thumb(im: Image.Image, size: int) -> Image.Image:
    out = im.convert("RGBA")
    out.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    x = (size - out.width) // 2
    y = (size - out.height) // 2
    canvas.paste(out, (x, y), out if out.mode == "RGBA" else None)
    return canvas


def build_contact_sheet(summaries: list[dict], out_path: Path) -> Path:
    """Rows: rocket, teddy. Cols: doodle | A | B. Small style-ref strip on top."""
    cell = 280
    label_h = 28
    pad = 12
    strip_h = 120
    cols = 3
    rows = len(CASES)

    # Style strip
    style_imgs = []
    for p in (STYLE_ROCKET, STYLE_FLOWER):
        if p.is_file():
            style_imgs.append((p.name, _thumb(Image.open(p), strip_h - 24)))

    width = pad * 2 + cols * cell + (cols - 1) * pad
    height = (
        pad
        + (strip_h + pad if style_imgs else 0)
        + rows * (label_h + cell + pad)
        + pad
    )
    sheet = Image.new("RGB", (width, height), (245, 245, 248))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font

    y = pad
    if style_imgs:
        draw.text((pad, y), "Jelly-Gummy style refs", fill=(40, 40, 50), font=font)
        y += 18
        x = pad
        for name, im in style_imgs:
            sheet.paste(im.convert("RGB"), (x, y))
            draw.text((x, y + im.height + 2), name[:40], fill=(80, 80, 90), font=font_sm)
            x += im.width + pad
        y = pad + strip_h + pad

    col_titles = ("doodle (raw)", "A raw_jelly", "B strict_jelly")
    by_key = {(s["source_id"], s["variant"]): s for s in summaries}

    for sid in CASES:
        draw.text((pad, y), sid, fill=(20, 20, 30), font=font)
        y += label_h
        # column headers
        for ci, title in enumerate(col_titles):
            draw.text((pad + ci * (cell + pad), y - 16), title, fill=(90, 90, 100), font=font_sm)

        paths = [
            doodle_path(sid, root=ROOT),
            OUT_ROOT / sid / "A_raw_jelly" / "edited.png",
            OUT_ROOT / sid / "B_strict_jelly" / "edited.png",
        ]
        for ci, p in enumerate(paths):
            x = pad + ci * (cell + pad)
            if p.is_file():
                thumb = _thumb(Image.open(p), cell)
                sheet.paste(thumb.convert("RGB"), (x, y))
            else:
                draw.rectangle([x, y, x + cell, y + cell], outline=(180, 80, 80), width=2)
                draw.text((x + 8, y + cell // 2), "missing", fill=(180, 80, 80), font=font)
        y += cell + pad

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path


def main() -> int:
    if not has_xai_key():
        print("error: XAI_API_KEY unset; refusing to run (exit 2).", file=sys.stderr)
        return 2

    missing = [p for p in (STYLE_ROCKET, STYLE_FLOWER) if not p.is_file()]
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

    # Quick sanity: strict adapter produces required fields / rocket flame ban
    for sid in CASES:
        strict = v3_to_strict(load_blueprint(sid, root=ROOT), source_id=sid)
        for k in (
            "observed_components",
            "inferred_components",
            "allowed_completion",
            "forbidden_additions",
        ):
            assert k in strict, k
        forbid_blob = " ".join(strict["forbidden_additions"]).lower()
        if sid == "06_rocket":
            assert "flame" in forbid_blob or "exhaust" in forbid_blob, strict["forbidden_additions"]
        if sid == "07_teddy":
            assert any(t in forbid_blob for t in ("limb", "arm", "mouth", "snout")), forbid_blob

    results: list[dict] = []
    # Exactly 4 configs, sequential. No extras beyond adapter-internal shape retry.
    for sid in CASES:
        for variant in VARIANTS:
            print(f"=== running {sid} variant {variant} ===", flush=True)
            summary = run_one(sid, variant)
            results.append(summary)
            print(
                f"  success={summary['success']} http={summary['http_status']} "
                f"cost={summary['approx_cost_usd']} attempt={summary.get('attempt_label')} "
                f"style={summary.get('style_mode')}",
                flush=True,
            )
            if summary.get("error"):
                print(f"  error={summary['error']}", flush=True)

    contact = OUT_ROOT / "contact_sheet.png"
    try:
        build_contact_sheet(results, contact)
        contact_path = str(contact)
    except Exception as exc:
        contact_path = None
        print(f"contact_sheet_error={type(exc).__name__}: {exc}", flush=True)

    report = {
        "total": len(results),
        "success_count": sum(1 for r in results if r["success"]),
        "failure_count": sum(1 for r in results if not r["success"]),
        "results": results,
        "approx_total_cost_usd": round(
            sum(float(r["approx_cost_usd"] or 0) for r in results if r["success"]), 4
        ),
        "contact_sheet": contact_path,
        "out_root": str(OUT_ROOT),
    }
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["success_count"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
