"""V4.2 first unseen pack — GUMMY ONLY (stylized dimensionality).

Exactly 10 xAI edits: u01–u10. PRIMARY = API-ready doodle; style refs =
Jelly-Gummy form/material only. Strict recognition fields in every prompt.

Usage:
  python3 -m lab.v4.v42_unseen_gummy_test
  # or: python3 scripts/v4_v42_unseen_gummy_test.py

Requires env XAI_API_KEY. Exit 2 if unset. Does not print or write the key.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lab.v4.generative.prompts import build_v42_unseen_gummy_prompt
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

STYLE_ROCKET = ROOT / "docs" / "refs" / "jelly_gummy" / "ref_jelly_gummy_rocket.png"
STYLE_FLOWER = ROOT / "docs" / "refs" / "jelly_gummy" / "ref_jelly_gummy_flower.png"
# Flower first so n2 fallback = doodle + flower (per mission).
STYLE_REFS = [STYLE_FLOWER, STYLE_ROCKET]

OUT_ROOT = ROOT / "out" / "v4" / "v42" / "unseen"
INPUTS_API = OUT_ROOT / "inputs_api"
RECOG_DIR = OUT_ROOT / "recognition"

CASE_IDS = tuple(f"u{i:02d}" for i in range(1, 11))
VARIANT = "gummy_stylized_dim"


def _write_meta(path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(meta, indent=2)
    assert "XAI_API_KEY" not in blob
    assert "Bearer " not in blob or "Bearer [REDACTED]" in blob
    path.write_text(blob + "\n")


def load_recognition(uid: str) -> dict:
    path = RECOG_DIR / f"{uid}_recognition.json"
    return json.loads(path.read_text())


def run_one(uid: str) -> dict:
    out_dir = OUT_ROOT / uid
    out_dir.mkdir(parents=True, exist_ok=True)

    doodle = INPUTS_API / f"{uid}.png"
    recog = load_recognition(uid)
    recog_out = out_dir / "recognition.json"
    recog_out.write_text(json.dumps(recog, indent=2) + "\n")

    src_copy = out_dir / "source_doodle.png"
    shutil.copy2(doodle, src_copy)

    # Prefer BOTH jelly refs; flower first for n2 fallback.
    style_paths = list(STYLE_REFS)
    style_copies = []
    for i, sp in enumerate(style_paths):
        dest = out_dir / f"style_ref_{i}_{sp.name}"
        shutil.copy2(sp, dest)
        style_copies.append(dest)

    prompt = build_v42_unseen_gummy_prompt(
        recog, multi_image=True, n_style_refs=2
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
        allow_single_fallback=False,
    )

    n_in = result.get("n_input_images")
    refs_used = result.get("input_style_refs") or []
    if n_in is None:
        n_in = 1 + len(refs_used) if result.get("ok") else 3
    cost_info = result.get("cost_estimate") or approx_cost_usd(
        n_input_images=int(n_in),
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
    )

    if result.get("ok") and int(n_in or 0) >= 3:
        style_mode = "doodle_plus_both_jelly_refs"
    elif result.get("ok") and int(n_in or 0) == 2:
        primary_name = Path(refs_used[0]).name if refs_used else "unknown"
        style_mode = f"doodle_plus_flower_only ({primary_name})"
    else:
        style_mode = "failed"

    meta = {
        "success": bool(result.get("ok")),
        "model": MODEL,
        "resolution": DEFAULT_RESOLUTION,
        "quality": DEFAULT_QUALITY,
        "n": DEFAULT_N,
        "variant": VARIANT,
        "uid": uid,
        "subject_hypothesis": recog.get("subject_hypothesis"),
        "confidence": recog.get("confidence"),
        "source_doodle": {
            "path": str(doodle),
            "filename": doodle.name,
            "copied_as": src_copy.name,
        },
        "recognition": {
            "path": str(recog_out),
            "fields": [
                "subject_hypothesis",
                "confidence",
                "observed_components",
                "inferred_components",
                "allowed_completion",
                "forbidden_additions",
            ],
        },
        "style_refs": {
            "requested": [str(p) for p in style_paths],
            "used": refs_used,
            "mode": style_mode,
            "copied_as": [p.name for p in style_copies],
            "note": (
                "Prefer BOTH jelly refs via images[] (flower first, then rocket). "
                "If API accepts only 2 images total, adapter falls back to doodle + flower."
            ),
        },
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
        "uid": uid,
        "success": meta["success"],
        "image_path": str(out_png) if meta["success"] else None,
        "approx_cost_usd": meta["approx_cost_usd"] or cost_info.get("approx_cost_usd"),
        "http_status": meta["http_status"],
        "error": meta["error"],
        "out_dir": str(out_dir),
        "attempt_label": (meta.get("api_response") or {}).get("attempt_label"),
        "style_mode": style_mode,
        "n_input_images": n_in,
        "subject_hypothesis": recog.get("subject_hypothesis"),
        "confidence": recog.get("confidence"),
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
    """Rows: u01–u10. Cols: doodle | gummy."""
    cell = 220
    label_h = 26
    pad = 10
    cols = 2
    rows = len(CASE_IDS)

    width = pad * 2 + cols * cell + (cols - 1) * pad
    height = pad + rows * (label_h + cell + pad) + pad
    sheet = Image.new("RGB", (width, height), (245, 245, 248))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font

    y = pad
    for uid in CASE_IDS:
        hyp = next((s.get("subject_hypothesis") for s in summaries if s["uid"] == uid), "")
        draw.text((pad, y), f"{uid}  {hyp}", fill=(20, 20, 30), font=font)
        y += label_h
        for ci, title in enumerate(("doodle", "gummy")):
            draw.text(
                (pad + ci * (cell + pad), y - 14),
                title,
                fill=(90, 90, 100),
                font=font_sm,
            )
        paths = [
            INPUTS_API / f"{uid}.png",
            OUT_ROOT / uid / "edited.png",
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

    missing = [p for p in STYLE_REFS if not p.is_file()]
    for uid in CASE_IDS:
        d = INPUTS_API / f"{uid}.png"
        r = RECOG_DIR / f"{uid}_recognition.json"
        if not d.is_file():
            missing.append(d)
        if not r.is_file():
            missing.append(r)
    if missing:
        print(f"error: missing inputs: {', '.join(str(p) for p in missing)}", file=sys.stderr)
        return 3

    results: list[dict] = []
    for uid in CASE_IDS:
        print(f"=== running {uid} gummy_stylized_dim ===", flush=True)
        summary = run_one(uid)
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
        "variant": VARIANT,
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
