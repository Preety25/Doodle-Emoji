"""V4.4 Semantic Parsing regression — 5 doodles × 4 styles = exactly 20 gens.

Stronger semantic parsing layer before styling. Reuses/updates V4.2 recognition
with stroke-role fields. Style sheets = material only.

Usage:
  python3 -m lab.v4.v44_semantic_regression
  # or: python3 scripts/v4_v44_semantic_regression.py

Requires env XAI_API_KEY. Exit 2 if unset. Does not print or write the key.
STOP after 20. No extra gens. No full 40 re-run.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lab.v4.generative.prompts import build_v44_semantic_prompt
from lab.v4.generative.xai_edit import (
    DEFAULT_N,
    DEFAULT_QUALITY,
    DEFAULT_RESOLUTION,
    MODEL,
    approx_cost_usd,
    edit_image,
    has_xai_key,
)
from lab.v4.semantic_lock import (
    RECOG_DIR,
    V44_CASE_IDS,
    ensure_v44_locks,
)

ROOT = Path(__file__).resolve().parents[2]

SHEETS = ROOT / "docs" / "refs" / "style_sheets"
SHEET_PATHS = {
    "gummy": SHEETS / "sheet_gummy.png",
    "clay": SHEETS / "sheet_clay.png",
    "plush": SHEETS / "sheet_plush.png",
    "glossy": SHEETS / "sheet_glossy.png",
}

INPUTS_API = ROOT / "out" / "v4" / "v42" / "unseen" / "inputs_api"
OUT_ROOT = ROOT / "out" / "v4" / "v44"

STYLES = ("gummy", "clay", "plush", "glossy")
MAX_GENS = 20  # hard stop


def _write_meta(path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(meta, indent=2)
    assert "XAI_API_KEY" not in blob
    assert "Bearer " not in blob or "Bearer [REDACTED]" in blob
    path.write_text(blob + "\n")


def style_refs_for(style: str) -> list[Path]:
    return [SHEET_PATHS[style]]


def run_one(uid: str, style: str, recog: dict) -> dict:
    out_dir = OUT_ROOT / uid / style
    out_dir.mkdir(parents=True, exist_ok=True)

    doodle = INPUTS_API / f"{uid}.png"
    src_copy = out_dir / "source_doodle.png"
    shutil.copy2(doodle, src_copy)

    # Per-cell semantic + stroke-role dumps
    semantic_path = out_dir / "semantic.json"
    stroke_path = out_dir / "stroke_roles.json"
    semantic_path.write_text(json.dumps(recog, indent=2) + "\n")
    stroke_path.write_text(
        json.dumps(
            {
                "uid": uid,
                "style": style,
                "subject_hypothesis": recog.get("subject_hypothesis"),
                "faces_observed": recog.get("faces_observed"),
                "stroke_roles": recog.get("stroke_roles"),
                "color_lock": recog.get("color_lock"),
                "identity_lock": recog.get("identity_lock"),
                "face_policy": recog.get("face_policy"),
            },
            indent=2,
        )
        + "\n"
    )

    style_paths = style_refs_for(style)
    n_refs = len(style_paths)
    prompt = build_v44_semantic_prompt(
        recog, style, multi_image=True, n_style_refs=n_refs
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
        n_in = 1 + len(refs_used) if result.get("ok") else (1 + n_refs)

    cost_info = result.get("cost_estimate") or approx_cost_usd(
        n_input_images=int(n_in),
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
    )

    style_mode = (
        f"doodle_plus_{style}_sheet" if result.get("ok") else "failed"
    )

    meta = {
        "success": bool(result.get("ok")),
        "model": MODEL,
        "resolution": DEFAULT_RESOLUTION,
        "quality": DEFAULT_QUALITY,
        "n": DEFAULT_N,
        "uid": uid,
        "style": style,
        "version": "v4.4",
        "subject_hypothesis": recog.get("subject_hypothesis"),
        "confidence": recog.get("confidence"),
        "faces_observed": recog.get("faces_observed"),
        "source_doodle": {
            "path": str(doodle),
            "filename": doodle.name,
            "copied_as": src_copy.name,
        },
        "recognition": {
            "source": str(RECOG_DIR / f"{uid}_recognition.json"),
            "semantic_lock_version": recog.get("semantic_lock_version"),
            "note": "Loaded once per doodle; same semantics for all 4 styles.",
        },
        "style_refs": {
            "requested": [str(p) for p in style_paths],
            "used": refs_used,
            "mode": style_mode,
            "note": "Style sheet = MATERIAL ONLY; anti-copy enforced in prompt.",
        },
        "background_policy": (
            "Prefer transparent; white/black void OK for R&D. No scenes/floors/text."
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
        "style": style,
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


def _fonts():
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13
        )
        font_sm = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11
        )
    except Exception:
        font = ImageFont.load_default()
        font_sm = font
    return font, font_sm


def build_contact_sheet(out_path: Path, recognitions: dict) -> Path:
    """Rows = 5 doodles; cols = doodle | gummy | clay | plush | glossy."""
    cell = 180
    label_h = 28
    pad = 8
    col_titles = ("doodle", "gummy", "clay", "plush", "glossy")
    cols = len(col_titles)
    rows = len(V44_CASE_IDS)
    font, font_sm = _fonts()

    width = pad * 2 + cols * cell + (cols - 1) * pad
    height = pad + rows * (label_h + cell + pad) + pad
    sheet = Image.new("RGB", (width, height), (245, 245, 248))
    draw = ImageDraw.Draw(sheet)

    y = pad
    for uid in V44_CASE_IDS:
        hyp = (recognitions.get(uid) or {}).get("subject_hypothesis", "")
        draw.text((pad, y), f"{uid}  {hyp}", fill=(20, 20, 30), font=font)
        y += label_h
        for ci, title in enumerate(col_titles):
            draw.text(
                (pad + ci * (cell + pad), y - 14),
                title,
                fill=(90, 90, 100),
                font=font_sm,
            )
        paths = [INPUTS_API / f"{uid}.png"] + [
            OUT_ROOT / uid / st / "edited.png" for st in STYLES
        ]
        for ci, p in enumerate(paths):
            x = pad + ci * (cell + pad)
            if p.is_file():
                thumb = _thumb(Image.open(p), cell)
                sheet.paste(thumb.convert("RGB"), (x, y))
            else:
                draw.rectangle(
                    [x, y, x + cell, y + cell], outline=(180, 80, 80), width=2
                )
                draw.text(
                    (x + 8, y + cell // 2),
                    "missing",
                    fill=(180, 80, 80),
                    font=font,
                )
        y += cell + pad

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path


def main() -> int:
    if not has_xai_key():
        print(
            "error: XAI_API_KEY unset; refusing to run (exit 2).",
            file=sys.stderr,
        )
        return 2

    missing: list[Path] = []
    for p in SHEET_PATHS.values():
        if not p.is_file():
            missing.append(p)
    for uid in V44_CASE_IDS:
        d = INPUTS_API / f"{uid}.png"
        if not d.is_file():
            missing.append(d)
    if missing:
        print(
            f"error: missing inputs: {', '.join(str(p) for p in missing)}",
            file=sys.stderr,
        )
        return 3

    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Semantic lock: enrich recognition once, then reuse for all styles
    print("=== ensuring V4.4 semantic locks (stroke roles) ===", flush=True)
    recognitions = ensure_v44_locks()
    for uid, rec in recognitions.items():
        print(
            f"  {uid}: {rec.get('subject_hypothesis')} "
            f"faces={rec.get('faces_observed')} "
            f"roles={len(rec.get('stroke_roles') or [])}",
            flush=True,
        )

    planned = [(uid, style) for uid in V44_CASE_IDS for style in STYLES]
    assert len(planned) == MAX_GENS, f"expected {MAX_GENS} cells, got {len(planned)}"

    # Skip cells that already succeeded (resume-safe) but never exceed 20 gens
    to_run: list[tuple[str, str]] = []
    for uid, style in planned:
        meta_path = OUT_ROOT / uid / style / "metadata.json"
        edited = OUT_ROOT / uid / style / "edited.png"
        if meta_path.is_file() and edited.is_file():
            try:
                meta = json.loads(meta_path.read_text())
                if meta.get("success"):
                    continue
            except Exception:
                pass
        to_run.append((uid, style))

    if len(to_run) > MAX_GENS:
        print(
            f"error: refusing to run {len(to_run)} gens (cap={MAX_GENS})",
            file=sys.stderr,
        )
        return 4

    print(
        f"plan: {len(to_run)} to generate, "
        f"{len(planned) - len(to_run)} keep existing (cap={MAX_GENS})",
        flush=True,
    )

    results: list[dict] = []
    gen_count = 0
    skip_count = 0

    for uid, style in planned:
        recog = recognitions[uid]
        if (uid, style) not in to_run:
            skip_count += 1
            meta = json.loads(
                (OUT_ROOT / uid / style / "metadata.json").read_text()
            )
            results.append(
                {
                    "uid": uid,
                    "style": style,
                    "success": True,
                    "image_path": str(OUT_ROOT / uid / style / "edited.png"),
                    "approx_cost_usd": meta.get("approx_cost_usd") or 0,
                    "http_status": meta.get("http_status"),
                    "error": None,
                    "out_dir": str(OUT_ROOT / uid / style),
                    "attempt_label": (meta.get("api_response") or {}).get(
                        "attempt_label"
                    ),
                    "style_mode": (meta.get("style_refs") or {}).get("mode"),
                    "n_input_images": (meta.get("api_response") or {}).get(
                        "n_input_images"
                    ),
                    "subject_hypothesis": recog.get("subject_hypothesis"),
                    "confidence": recog.get("confidence"),
                    "skipped_existing": True,
                }
            )
            print(f"=== keep {uid}/{style} ===", flush=True)
            continue

        gen_count += 1
        if gen_count > MAX_GENS:
            print("HARD STOP: gen_count exceeded MAX_GENS", file=sys.stderr)
            break
        print(
            f"=== [{gen_count}/{len(to_run)}] {uid}/{style}  "
            f"hyp={recog.get('subject_hypothesis')} ===",
            flush=True,
        )
        summary = run_one(uid, style, recog)
        summary["skipped_existing"] = False
        results.append(summary)
        print(
            f"  success={summary['success']} http={summary['http_status']} "
            f"cost={summary['approx_cost_usd']} "
            f"attempt={summary.get('attempt_label')}",
            flush=True,
        )
        if summary.get("error"):
            print(f"  error={summary['error']}", flush=True)

    print(
        f"generated={gen_count} kept={skip_count} total_cells={len(results)}",
        flush=True,
    )

    contact_path = None
    try:
        contact_path = str(
            build_contact_sheet(OUT_ROOT / "contact_sheet.png", recognitions)
        )
        print(f"wrote {contact_path}", flush=True)
    except Exception as exc:
        print(f"contact_sheet_error={type(exc).__name__}: {exc}", flush=True)

    report = {
        "version": "v4.4",
        "total": len(results),
        "success_count": sum(1 for r in results if r["success"]),
        "failure_count": sum(1 for r in results if not r["success"]),
        "styles": list(STYLES),
        "case_ids": list(V44_CASE_IDS),
        "max_gens": MAX_GENS,
        "generated_this_run": gen_count,
        "kept_existing": skip_count,
        "results": results,
        "approx_total_cost_usd": round(
            sum(float(r["approx_cost_usd"] or 0) for r in results if r["success"]),
            4,
        ),
        "approx_new_gens_cost_usd": round(
            sum(
                float(r["approx_cost_usd"] or 0)
                for r in results
                if r["success"] and not r.get("skipped_existing")
            ),
            4,
        ),
        "contact_sheet": contact_path,
        "out_root": str(OUT_ROOT),
        "note": "Exactly 20 cells (5×4). Semantic lock shared across styles. No extra gens.",
    }
    (OUT_ROOT / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    print(
        f"success={report['success_count']}/{report['total']} "
        f"cost≈{report['approx_total_cost_usd']}"
    )
    return 0 if report["success_count"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
