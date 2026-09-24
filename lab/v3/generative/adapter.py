"""Generative image-edit adapter.

Checks OPENAI_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY, REPLICATE_API_TOKEN.
If none are set, writes a BLOCKED_NO_API report and labeled stub cards.
Stubs are not fake renders of the doodle.
"""
from __future__ import annotations

import base64
import os
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from lab.v3.generative.prompts import build_request

ROOT = Path(__file__).resolve().parents[3]


def env_keys():
    return {
        "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
        "GEMINI_API_KEY": bool(os.environ.get("GEMINI_API_KEY")),
        "GOOGLE_API_KEY": bool(os.environ.get("GOOGLE_API_KEY")),
        "REPLICATE_API_TOKEN": bool(os.environ.get("REPLICATE_API_TOKEN")),
    }


def any_api(keys=None):
    keys = keys or env_keys()
    return any(keys.values())


def _font(size):
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def write_stub(path: Path, source_id: str, style: str):
    im = Image.new("RGBA", (1024, 1024), (246, 242, 236, 255))
    draw = ImageDraw.Draw(im)
    draw.rectangle([0, 0, 1024, 120], fill=(90, 40, 40, 255))
    draw.text((36, 28), "GENERATIVE PATH", font=_font(28), fill=(255, 255, 255, 255))
    draw.text((36, 70), "BLOCKED_NO_API", font=_font(32), fill=(255, 220, 160, 255))
    draw.text((48, 180), f"{source_id}   ·   {style}", font=_font(28), fill=(30, 30, 30, 255))
    body = (
        "No image API key was set, so this is not a model edit.\n"
        "The request JSON next to this card is the real prompt that\n"
        "would be sent: original doodle + blueprint summary + style,\n"
        "with hard constraints on silhouette, part count, placement,\n"
        "and user asymmetry.\n\n"
        "This stub is not a stylized doodle and must not be read as one."
    )
    y = 250
    for line in body.split("\n"):
        draw.text((48, y), line, font=_font(22), fill=(40, 40, 40, 255))
        y += 36
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def try_openai_edit(source_png: Path, prompt: str, out_png: Path) -> dict:
    t0 = time.time()
    try:
        from openai import OpenAI
    except ImportError:
        return {"ok": False, "error": "openai package not installed", "service": "openai"}
    client = OpenAI()
    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
    try:
        with source_png.open("rb") as f:
            result = client.images.edit(
                model=model,
                image=f,
                prompt=prompt,
                size="1024x1024",
            )
        b64 = result.data[0].b64_json
        out_png.write_bytes(base64.b64decode(b64))
        return {
            "ok": True,
            "service": "openai",
            "model": model,
            "latency_ms": int((time.time() - t0) * 1000),
        }
    except Exception as exc:
        return {"ok": False, "service": "openai", "error": str(exc), "latency_ms": int((time.time() - t0) * 1000)}


def try_gemini_edit(source_png: Path, prompt: str, out_png: Path) -> dict:
    """Best-effort Gemini image edit. SDK and model names vary; failures are reported."""
    t0 = time.time()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        return {"ok": False, "error": "no gemini key"}
    try:
        import google.generativeai as genai
    except ImportError:
        return {"ok": False, "service": "gemini", "error": "google-generativeai not installed"}
    try:
        genai.configure(api_key=key)
        model_name = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.0-flash-preview-image-generation")
        model = genai.GenerativeModel(model_name)
        img = Image.open(source_png)
        resp = model.generate_content([prompt, img])
        # pull first inline image if the SDK returned one
        parts = getattr(resp, "parts", None) or []
        for part in parts:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                out_png.write_bytes(inline.data)
                return {"ok": True, "service": "gemini", "model": model_name, "latency_ms": int((time.time() - t0) * 1000)}
        return {"ok": False, "service": "gemini", "error": "response had no image bytes", "latency_ms": int((time.time() - t0) * 1000)}
    except Exception as exc:
        return {"ok": False, "service": "gemini", "error": str(exc), "latency_ms": int((time.time() - t0) * 1000)}


def try_replicate(source_png: Path, prompt: str, out_png: Path) -> dict:
    t0 = time.time()
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        return {"ok": False, "error": "no replicate token"}
    try:
        import replicate
    except ImportError:
        return {"ok": False, "service": "replicate", "error": "replicate package not installed"}
    model = os.environ.get(
        "REPLICATE_IMAGE_MODEL",
        "black-forest-labs/flux-kontext-pro",
    )
    try:
        with source_png.open("rb") as f:
            output = replicate.run(
                model,
                input={"prompt": prompt, "input_image": f, "aspect_ratio": "1:1"},
            )
        # replicate often returns a URL or file-like
        data = output
        if isinstance(data, list):
            data = data[0]
        if hasattr(data, "read"):
            out_png.write_bytes(data.read())
        else:
            import urllib.request

            urllib.request.urlretrieve(str(data), out_png)
        return {"ok": True, "service": "replicate", "model": model, "latency_ms": int((time.time() - t0) * 1000)}
    except Exception as exc:
        return {"ok": False, "service": "replicate", "error": str(exc), "latency_ms": int((time.time() - t0) * 1000)}


def run_generative(examples: list[dict], out_dir: Path, styles: list[str]) -> dict:
    """examples: [{source_id, blueprint, doodle_png}]"""
    keys = env_keys()
    live = any_api(keys)
    out_dir.mkdir(parents=True, exist_ok=True)
    req_dir = out_dir / "requests"
    req_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for ex in examples:
        bp = ex["blueprint"]
        for style in styles:
            req = build_request(bp, style, ex["doodle_png"])
            req_path = req_dir / f"{ex['source_id']}__{style}.json"
            req_path.write_text(__import__("json").dumps(req, indent=2))
            row = {
                "source_id": ex["source_id"],
                "style": style,
                "request": str(req_path),
                "api_used": False,
                "blocked": not live,
                "output": None,
                "meta": None,
            }
            out_png = out_dir / f"{ex['source_id']}__{style}.png"
            if live:
                meta = {"ok": False, "error": "no matching client succeeded"}
                src = Path(ex["doodle_png"])
                if keys.get("OPENAI_API_KEY"):
                    meta = try_openai_edit(src, req["prompt"], out_png)
                elif keys.get("GEMINI_API_KEY") or keys.get("GOOGLE_API_KEY"):
                    meta = try_gemini_edit(src, req["prompt"], out_png)
                elif keys.get("REPLICATE_API_TOKEN"):
                    meta = try_replicate(src, req["prompt"], out_png)
                row["meta"] = meta
                if meta.get("ok"):
                    row["api_used"] = True
                    row["blocked"] = False
                    row["output"] = str(out_png)
                else:
                    # key was set but the call failed — still leave a visible card
                    write_stub(out_png, ex["source_id"], style)
                    row["output"] = str(out_png)
                    row["blocked"] = True
            else:
                write_stub(out_png, ex["source_id"], style)
                row["output"] = str(out_png)
            rows.append(row)

    status = "RAN_WITH_API" if any(r.get("api_used") for r in rows) else "BLOCKED_NO_API"
    if live and status == "BLOCKED_NO_API":
        status = "API_KEY_SET_BUT_CALLS_FAILED"
    report = _report(status, keys, rows, out_dir)
    report_path = out_dir / "BLOCKED_NO_API.md" if status != "RAN_WITH_API" else out_dir / "GENERATIVE_REPORT.md"
    # always keep the blocked filename when we did not get live images, and also a stable report name
    (out_dir / "GENERATIVE_REPORT.md").write_text(report)
    if status != "RAN_WITH_API":
        (out_dir / "BLOCKED_NO_API.md").write_text(report)
    (out_dir / "results.json").write_text(__import__("json").dumps({"status": status, "keys": keys, "rows": rows}, indent=2))
    return {"status": status, "report": str(out_dir / "GENERATIVE_REPORT.md"), "rows": rows}


def _report(status, keys, rows, out_dir: Path) -> str:
    lines = [
        "# V3 generative renderer",
        "",
        f"**Status:** {status}",
        "",
        "This path is an image-edit adapter. It is not the product architecture.",
        "Inputs, when a key is present: original doodle raster, semantic blueprint summary, style text.",
        "Hard constraints are in the prompt: subject identity, silhouette, part count and placement,",
        "distinctive proportions, user asymmetry. The prompt forbids a generic replacement, extra decor,",
        "invented faces, text, backgrounds, and ground planes.",
        "",
        "## Env vars checked",
        "",
    ]
    for k, present in keys.items():
        lines.append(f"- `{k}`: {'SET' if present else 'missing'}")
    lines += [
        "",
        "## How to run live",
        "",
        "Export one of the keys above, install the matching SDK (`openai`, `google-generativeai`, or `replicate`),",
        "then re-run `python3 scripts/run_v3.py --stage generative`.",
        "",
        "## Requests",
        "",
        f"Prompt JSON: `{out_dir / 'requests'}`",
        "",
        "| example | style | api | output |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['source_id']} | {r['style']} | {r.get('api_used')} | `{r.get('output')}` |"
        )
    lines.append("")
    return "\n".join(lines)
