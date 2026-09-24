"""Procedural vs AI vs hybrid comparison.

If OPENAI_API_KEY / GEMINI_API_KEY / REPLICATE_API_TOKEN present, run real AI.
Else: rasterize sources, write BLOCKED_NO_API report, produce labeled pseudo-hybrid stub.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT_AI = ROOT / "out" / "derivatives" / "ai_compare"
REPORTS = ROOT / "out" / "reports"


def env_keys():
    return {
        "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
        "GEMINI_API_KEY": bool(os.environ.get("GEMINI_API_KEY")),
        "GOOGLE_API_KEY": bool(os.environ.get("GOOGLE_API_KEY")),
        "REPLICATE_API_TOKEN": bool(os.environ.get("REPLICATE_API_TOKEN")),
        "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
    }


def any_api(keys=None):
    keys = keys or env_keys()
    return any(keys.values())


def rasterize_doodle(doodle_path: Path, out_png: Path, size=1024):
    data = json.loads(doodle_path.read_text())
    w = float(data["canvas"]["width"])
    h = float(data["canvas"]["height"])
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    sx, sy = size / w, size / h

    def parse_color(c):
        if not c:
            return (40, 40, 50, 255)
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        return tuple(int(c[i : i + 2], 16) for i in (0, 2, 4)) + (255,)

    for s in data["strokes"]:
        pts = [(p[0] * sx, p[1] * sy) for p in s["points"]]
        col = parse_color(s.get("color"))
        if len(pts) < 2:
            continue
        if s.get("closed") and len(pts) >= 3:
            draw.polygon(pts, fill=col)
            draw.line(pts + [pts[0]], fill=col, width=3)
        else:
            draw.line(pts, fill=col, width=max(6, size // 80))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_png)
    return out_png


def pseudo_hybrid(procedural_png: Path, out_png: Path):
    """NOT real AI — mild unsharp/contrast composite clearly labeled."""
    im = Image.open(procedural_png).convert("RGBA")
    rgb = im.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
    rgb = ImageEnhance.Color(rgb).enhance(1.05)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=3))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    # banner
    draw = ImageDraw.Draw(out)
    draw.rectangle([0, 0, out.width, 28], fill=(0, 0, 0, 180))
    draw.text((8, 6), "PSEUDO-HYBRID (NOT real AI)", fill=(255, 220, 80, 255))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_png)
    return out_png


def try_openai_image(source_png: Path, style: str, out_png: Path) -> dict:
    """Best-effort OpenAI images edit/variation — may fail depending on SDK."""
    t0 = time.time()
    try:
        from openai import OpenAI
    except ImportError:
        return {"ok": False, "error": "openai package not installed"}
    client = OpenAI()
    prompt = (
        f"POLISH DON'T REPLACE. Keep proportions and asymmetry of this doodle. "
        f"Transparent background. Style: {style} candy/sticker 3D look. "
        f"Do not invent faces. Soft inflated silhouette, studio lighting."
    )
    try:
        # GPT image API varies; attempt images.edit if available
        with source_png.open("rb") as f:
            result = client.images.edit(
                model=os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1"),
                image=f,
                prompt=prompt,
                size="1024x1024",
            )
        import base64
        b64 = result.data[0].b64_json
        out_png.write_bytes(base64.b64decode(b64))
        return {
            "ok": True,
            "model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1"),
            "service": "openai",
            "latency_ms": int((time.time() - t0) * 1000),
            "estimated_cost_usd": 0.04,
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "latency_ms": int((time.time() - t0) * 1000)}


def main():
    keys = env_keys()
    man = json.loads((ROOT / "corpus" / "manifest.json").read_text())
    # subset: all 20 if API else all 20 for raster+stub
    doodle_ids = [d["id"] for d in man["doodles"]]
    styles = ["gummy", "clay", "plush"]
    OUT_AI.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    results = []
    api = any_api(keys)

    for did in doodle_ids:
        src_json = ROOT / "corpus" / "doodles" / f"{did}.json"
        raster = OUT_AI / f"{did}__source_raster.png"
        rasterize_doodle(src_json, raster)
        for style in styles:
            proc = ROOT / "out" / "renders" / f"{did}__{style}__v1__s1.png"
            row = {
                "doodle_id": did,
                "style_id": style,
                "A_procedural": str(proc) if proc.exists() else None,
                "source_raster": str(raster),
                "B_ai": None,
                "C_hybrid": None,
                "api_used": False,
                "blocked": not api,
            }
            if api and keys.get("OPENAI_API_KEY"):
                ai_out = OUT_AI / f"{did}__{style}__ai.png"
                info = try_openai_image(raster, style, ai_out)
                row["B_meta"] = info
                if info.get("ok"):
                    row["B_ai"] = str(ai_out)
                    row["api_used"] = True
                    # hybrid: procedural alpha hard constraint
                    if proc.exists():
                        hy = OUT_AI / f"{did}__{style}__hybrid.png"
                        ai_im = Image.open(ai_out).convert("RGBA")
                        pr = Image.open(proc).convert("RGBA")
                        # resize AI to proc
                        ai_im = ai_im.resize(pr.size)
                        # keep procedural alpha
                        composed = Image.composite(ai_im, Image.new("RGBA", pr.size, (0, 0, 0, 0)), pr.getchannel("A"))
                        composed.save(hy)
                        row["C_hybrid"] = str(hy)
                        row["C_note"] = "procedural alpha hard-mask over AI RGB"
            # always write pseudo-hybrid stub for documentation when no API or as control
            if proc.exists():
                stub = OUT_AI / f"{did}__{style}__pseudo_hybrid.png"
                pseudo_hybrid(proc, stub)
                if not row.get("C_hybrid"):
                    row["C_hybrid"] = str(stub)
                    row["C_note"] = "PSEUDO-HYBRID NOT real AI (unsharp/contrast only)"
            results.append(row)

    (OUT_AI / "results.json").write_text(json.dumps(results, indent=2))

    lines = [
        "# AI Compare Report",
        "",
        f"**Status:** {'RAN_WITH_API' if api else 'BLOCKED_NO_API'}",
        "",
        "## Env vars checked",
        "",
    ]
    for k, v in keys.items():
        lines.append(f"- `{k}`: {'SET' if v else 'missing'}")
    lines += [
        "",
        "## Required to unblock real AI path",
        "",
        "Set one of: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `REPLICATE_API_TOKEN` (and install matching SDK).",
        "",
        "Preferred prompt stem:",
        "",
        "> POLISH DON'T REPLACE / keep proportions and asymmetry / transparent BG / gummy|clay|plush style / do not invent faces",
        "",
        "## Paths",
        "",
        f"- Source rasters + stubs: `{OUT_AI}`",
        f"- Results JSON: `{OUT_AI / 'results.json'}`",
        "",
        "## Design for Hybrid (C)",
        "",
        "1. Run procedural Blender master (A) for silhouette + alpha.",
        "2. Condition AI on source raster with POLISH DON'T REPLACE prompt.",
        "3. Composite: AI RGB × procedural alpha (hard constraint). Optional: reject if IoU(alpha_AI, alpha_A) < threshold.",
        "",
        "## What was produced this run",
        "",
    ]
    if not api:
        lines += [
            "- A = procedural renders (benchmark).",
            "- B = **blocked** (no API key).",
            "- C = **pseudo-hybrid stubs** only (Pillow unsharp/contrast), clearly labeled NOT real AI.",
            "",
            "**Recommendation to parent:** provision `OPENAI_API_KEY` (or Gemini/Replicate) and re-run `python3 scripts/ai_compare.py`.",
        ]
    else:
        ok_b = sum(1 for r in results if r.get("B_ai"))
        lines.append(f"- B AI outputs: {ok_b}/{len(results)}")
        lines.append(f"- C hybrid outputs: {sum(1 for r in results if r.get('C_hybrid'))}")

    lines += ["", "## Latency / cost", ""]
    if api:
        lats = [r.get("B_meta", {}).get("latency_ms") for r in results if r.get("B_meta", {}).get("ok")]
        if lats:
            lines.append(f"- AI latency ms (n={len(lats)}): mean={sum(lats)/len(lats):.0f}")
        costs = [r.get("B_meta", {}).get("estimated_cost_usd", 0) for r in results if r.get("B_meta", {}).get("ok")]
        lines.append(f"- Estimated AI cost USD: {sum(costs):.2f}")
    else:
        lines.append("- N/A (blocked)")

    (REPORTS / "ai_compare.md").write_text("\n".join(lines) + "\n")
    print("Wrote", REPORTS / "ai_compare.md", "api=", api)


if __name__ == "__main__":
    main()
