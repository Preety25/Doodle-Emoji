"""V4.3 Multi-Style Doodle Transform — gummy / clay / plush / glossy × u01–u10.

Exactly 40 xAI edits. Recognition loaded once per doodle (shared across styles).
Glossy uses doodle-only + strong written style language (no glossy sheet provided).

Usage:
  python3 -m lab.v4.v43_multi_style_transform
  # or: python3 scripts/v4_v43_multi_style_transform.py

Requires env XAI_API_KEY. Exit 2 if unset. Does not print or write the key.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lab.v4.generative.prompts import build_v43_multi_style_prompt
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

SHEETS = ROOT / "docs" / "refs" / "style_sheets"
SHEET_GUMMY = SHEETS / "sheet_gummy.png"
SHEET_CLAY = SHEETS / "sheet_clay.png"
SHEET_PLUSH = SHEETS / "sheet_plush.png"
SHEET_GLOSSY = SHEETS / "sheet_glossy.png"

INPUTS_API = ROOT / "out" / "v4" / "v42" / "unseen" / "inputs_api"
RECOG_DIR = ROOT / "out" / "v4" / "v42" / "unseen" / "recognition"
OUT_ROOT = ROOT / "out" / "v4" / "v43"

CASE_IDS = tuple(f"u{i:02d}" for i in range(1, 11))
STYLES = ("gummy", "clay", "plush", "glossy")

# Glossy: doodle + sheet_glossy.png (canonical solid resin/vinyl sheet).
GLOSSY_REF_MODE = "doodle_plus_glossy_sheet"


def _write_meta(path: Path, meta: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(meta, indent=2)
    assert "XAI_API_KEY" not in blob
    assert "Bearer " not in blob or "Bearer [REDACTED]" in blob
    path.write_text(blob + "\n")



def needs_run(uid: str, style: str) -> bool:
    """True if this cell must be generated (missing, failed, or stale glossy)."""
    meta_path = OUT_ROOT / uid / style / "metadata.json"
    edited = OUT_ROOT / uid / style / "edited.png"
    if not meta_path.is_file() or not edited.is_file():
        return True
    try:
        meta = json.loads(meta_path.read_text())
    except Exception:
        return True
    if not meta.get("success"):
        return True
    mode = ((meta.get("style_refs") or {}).get("mode")) or ""
    # Re-run glossy gens that used the old doodle-only path
    if style == "glossy" and mode == "doodle_only_strong_text":
        return True
    if style == "glossy":
        used = (meta.get("style_refs") or {}).get("used") or []
        if not any("sheet_glossy" in str(u) for u in used):
            return True
    return False

def load_recognition(uid: str) -> dict:
    path = RECOG_DIR / f"{uid}_recognition.json"
    return json.loads(path.read_text())


def style_refs_for(style: str) -> list[Path]:
    if style == "gummy":
        return [SHEET_GUMMY]
    if style == "clay":
        return [SHEET_CLAY]
    if style == "plush":
        return [SHEET_PLUSH]
    if style == "glossy":
        return [SHEET_GLOSSY]
    raise ValueError(style)


def run_one(uid: str, style: str, recog: dict) -> dict:
    out_dir = OUT_ROOT / uid / style
    out_dir.mkdir(parents=True, exist_ok=True)

    doodle = INPUTS_API / f"{uid}.png"
    src_copy = out_dir / "source_doodle.png"
    shutil.copy2(doodle, src_copy)

    style_paths = style_refs_for(style)
    multi = bool(style_paths)
    n_refs = len(style_paths)

    prompt = build_v43_multi_style_prompt(
        recog, style, multi_image=multi, n_style_refs=n_refs
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
    if result.get("ok") and style == "glossy":
        style_mode = GLOSSY_REF_MODE
    elif result.get("ok") and style == "gummy":
        style_mode = "doodle_plus_gummy_sheet"
    elif result.get("ok"):
        style_mode = f"doodle_plus_{style}_sheet"
    else:
        style_mode = "failed"

    n_in = result.get("n_input_images")
    refs_used = result.get("input_style_refs") or []
    if n_in is None:
        n_in = 1 + len(refs_used) if result.get("ok") else (1 + n_refs if n_refs else 1)

    cost_info = result.get("cost_estimate") or approx_cost_usd(
        n_input_images=int(n_in),
        resolution=DEFAULT_RESOLUTION,
        quality=DEFAULT_QUALITY,
    )

    bg_note = (
        "Prefer transparent; white/black void OK for R&D. No scenes/floors/text."
    )

    meta = {
        "success": bool(result.get("ok")),
        "model": MODEL,
        "resolution": DEFAULT_RESOLUTION,
        "quality": DEFAULT_QUALITY,
        "n": DEFAULT_N,
        "uid": uid,
        "style": style,
        "subject_hypothesis": recog.get("subject_hypothesis"),
        "confidence": recog.get("confidence"),
        "source_doodle": {
            "path": str(doodle),
            "filename": doodle.name,
            "copied_as": src_copy.name,
        },
        "recognition": {
            "source": str(RECOG_DIR / f"{uid}_recognition.json"),
            "fields": [
                "subject_hypothesis",
                "confidence",
                "observed_components",
                "inferred_components",
                "allowed_completion",
                "forbidden_additions",
            ],
            "note": "Loaded once per doodle; same semantics for all 4 styles.",
        },
        "style_refs": {
            "requested": [str(p) for p in style_paths],
            "used": refs_used,
            "mode": style_mode,
            "glossy_choice": GLOSSY_REF_MODE if style == "glossy" else None,
            "note": (
                "Gummy: doodle + sheet_gummy.png. "
                "Clay/plush/glossy: doodle + matching style sheet "
                "(sheet_clay / sheet_plush / sheet_glossy)."
            ),
        },
        "background_policy": bg_note,
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
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font
    return font, font_sm


def build_contact_all(out_path: Path) -> Path:
    """Rows u01–u10; cols doodle | gummy | clay | plush | glossy."""
    cell = 180
    label_h = 28
    pad = 8
    col_titles = ("doodle", "gummy", "clay", "plush", "glossy")
    cols = len(col_titles)
    rows = len(CASE_IDS)
    font, font_sm = _fonts()

    width = pad * 2 + cols * cell + (cols - 1) * pad
    height = pad + rows * (label_h + cell + pad) + pad
    sheet = Image.new("RGB", (width, height), (245, 245, 248))
    draw = ImageDraw.Draw(sheet)

    y = pad
    for uid in CASE_IDS:
        hyp_path = RECOG_DIR / f"{uid}_recognition.json"
        hyp = ""
        if hyp_path.is_file():
            hyp = json.loads(hyp_path.read_text()).get("subject_hypothesis", "")
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
                draw.rectangle([x, y, x + cell, y + cell], outline=(180, 80, 80), width=2)
                draw.text((x + 8, y + cell // 2), "missing", fill=(180, 80, 80), font=font)
        y += cell + pad

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return out_path


def build_contact_style(style: str, out_path: Path) -> Path:
    """Rows u01–u10; cols doodle | style."""
    cell = 220
    label_h = 26
    pad = 10
    cols = 2
    rows = len(CASE_IDS)
    font, font_sm = _fonts()

    width = pad * 2 + cols * cell + (cols - 1) * pad
    height = pad + rows * (label_h + cell + pad) + pad
    sheet = Image.new("RGB", (width, height), (245, 245, 248))
    draw = ImageDraw.Draw(sheet)

    y = pad
    for uid in CASE_IDS:
        hyp_path = RECOG_DIR / f"{uid}_recognition.json"
        hyp = ""
        if hyp_path.is_file():
            hyp = json.loads(hyp_path.read_text()).get("subject_hypothesis", "")
        draw.text((pad, y), f"{uid}  {hyp}", fill=(20, 20, 30), font=font)
        y += label_h
        for ci, title in enumerate(("doodle", style)):
            draw.text(
                (pad + ci * (cell + pad), y - 14),
                title,
                fill=(90, 90, 100),
                font=font_sm,
            )
        paths = [
            INPUTS_API / f"{uid}.png",
            OUT_ROOT / uid / style / "edited.png",
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

    missing: list[Path] = []
    for p in (SHEET_GUMMY, SHEET_CLAY, SHEET_PLUSH, SHEET_GLOSSY):
        if not p.is_file():
            missing.append(p)
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

    # Preload recognition once per doodle
    recognitions = {uid: load_recognition(uid) for uid in CASE_IDS}

    results: list[dict] = []
    gen_count = 0
    skip_count = 0
    planned = [(uid, style) for uid in CASE_IDS for style in STYLES]
    to_run = [(uid, style) for uid, style in planned if needs_run(uid, style)]
    print(
        f"plan: {len(to_run)} to generate/re-run, {len(planned) - len(to_run)} keep existing",
        flush=True,
    )
    for uid, style in planned:
        recog = recognitions[uid]
        if not needs_run(uid, style):
            skip_count += 1
            meta = json.loads((OUT_ROOT / uid / style / "metadata.json").read_text())
            summary = {
                "uid": uid,
                "style": style,
                "success": True,
                "image_path": str(OUT_ROOT / uid / style / "edited.png"),
                "approx_cost_usd": meta.get("approx_cost_usd") or 0,
                "http_status": meta.get("http_status"),
                "error": None,
                "out_dir": str(OUT_ROOT / uid / style),
                "attempt_label": (meta.get("api_response") or {}).get("attempt_label"),
                "style_mode": (meta.get("style_refs") or {}).get("mode"),
                "n_input_images": (meta.get("api_response") or {}).get("n_input_images"),
                "subject_hypothesis": recog.get("subject_hypothesis"),
                "confidence": recog.get("confidence"),
                "skipped_existing": True,
            }
            results.append(summary)
            print(f"=== keep {uid}/{style} mode={summary['style_mode']} ===", flush=True)
            continue
        gen_count += 1
        print(
            f"=== [{gen_count}/{len(to_run)}] {uid}/{style}  hyp={recog.get('subject_hypothesis')} ===",
            flush=True,
        )
        summary = run_one(uid, style, recog)
        summary["skipped_existing"] = False
        results.append(summary)
        print(
            f"  success={summary['success']} http={summary['http_status']} "
            f"cost={summary['approx_cost_usd']} attempt={summary.get('attempt_label')} "
            f"mode={summary.get('style_mode')}",
            flush=True,
        )
        if summary.get("error"):
            print(f"  error={summary['error']}", flush=True)

    print(f"generated={gen_count} kept={skip_count} total_cells={len(results)}", flush=True)

    contact_paths: dict[str, str | None] = {}
    try:
        p = build_contact_all(OUT_ROOT / "contact_all.png")
        contact_paths["contact_all"] = str(p)
        print(f"wrote {p}", flush=True)
    except Exception as exc:
        contact_paths["contact_all"] = None
        print(f"contact_all_error={type(exc).__name__}: {exc}", flush=True)

    for style in STYLES:
        try:
            p = build_contact_style(style, OUT_ROOT / f"contact_{style}.png")
            contact_paths[f"contact_{style}"] = str(p)
            print(f"wrote {p}", flush=True)
        except Exception as exc:
            contact_paths[f"contact_{style}"] = None
            print(f"contact_{style}_error={type(exc).__name__}: {exc}", flush=True)

    report = {
        "total": len(results),
        "success_count": sum(1 for r in results if r["success"]),
        "failure_count": sum(1 for r in results if not r["success"]),
        "styles": list(STYLES),
        "glossy_ref_mode": GLOSSY_REF_MODE,
        "results": results,
        "approx_total_cost_usd": round(
            sum(float(r["approx_cost_usd"] or 0) for r in results if r["success"]), 4
        ),
        "approx_new_gens_cost_usd": round(
            sum(
                float(r["approx_cost_usd"] or 0)
                for r in results
                if r["success"] and not r.get("skipped_existing")
            ),
            4,
        ),
        "generated_this_run": gen_count,
        "kept_existing": skip_count,
        "contact_sheets": contact_paths,
        "out_root": str(OUT_ROOT),
        "note": (
            "Final pack = 40 cells (10×4). Resume may re-run stale glossy (doodle-only) "
            "and finish incomplete cells. No other retries except adapter shape errors."
        ),
    }
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "run_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    print(f"success={report['success_count']}/40 cost≈{report['approx_total_cost_usd']}")
    return 0 if report["success_count"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
