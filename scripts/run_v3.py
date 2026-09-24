#!/usr/bin/env python3
"""Run the V3 semantic reconstruction + render prototype.

Examples:
  python3 scripts/run_v3.py --stage blueprints
  python3 scripts/run_v3.py --stage render --only 02_heart,06_rocket --res 1024 --samples 16
  python3 scripts/run_v3.py --stage all --res 2048 --samples 32
  python3 scripts/run_v3.py --stage generative
  python3 scripts/run_v3.py --stage sheets

Does not call the V2 remesh/inflate renderer.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.v3.contacts import downsample_png, example_strip, multi_sheet
from lab.v3.generative.adapter import run_generative
from lab.v3.quality import judge_example
from lab.v3.raster import rasterize_doodle
from lab.v3.recognize import recognize_doodle
from lab.v3.reconstruct import build_job
from lab.v3.styles import STYLE_ORDER
from lab.v3.viz import render_blueprint

EXAMPLES = [
    ("02_heart", ROOT / "corpus" / "golden" / "02_heart.json"),
    ("06_rocket", ROOT / "corpus" / "golden" / "06_rocket.json"),
    ("07_teddy", ROOT / "corpus" / "golden" / "07_teddy.json"),
    ("05_plant", ROOT / "corpus" / "golden" / "05_plant.json"),
    ("09_rose", ROOT / "corpus" / "golden" / "09_rose.json"),
    ("12_messy_incomplete", ROOT / "corpus" / "golden" / "12_messy_incomplete.json"),
]

PANEL = {
    "gummy": "C_gummy.png",
    "clay": "D_clay.png",
    "plush": "E_plush.png",
    "glossy": "F_glossy.png",
}

BLENDER = Path(os.environ.get("BLENDER_BIN", "/workspace/tools/blender/blender-4.2.9-linux-x64/blender"))
RENDER_PY = ROOT / "lab" / "v3" / "procedural" / "blender_render.py"


def out_root() -> Path:
    p = ROOT / "out" / "v3"
    p.mkdir(parents=True, exist_ok=True)
    return p


def log(msg: str):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    log_path = out_root() / "logs" / "run.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as f:
        f.write(line + "\n")


def selected(only: str | None):
    if not only:
        return EXAMPLES
    want = {x.strip() for x in only.split(",") if x.strip()}
    return [e for e in EXAMPLES if e[0] in want]


def stage_blueprints(examples):
    written = []
    for source_id, path in examples:
        bp = recognize_doodle(path)
        folder = out_root() / source_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "blueprint.json").write_text(json.dumps(bp, indent=2))
        rasterize_doodle(path, folder / "A_original.png", size=1024)
        render_blueprint(bp, str(folder / "B_blueprint.png"), size=1280)
        comps = ", ".join(c["id"] for c in bp["major_components"])
        log(f"blueprint {source_id} {bp['subject_hypothesis']} {bp['confidence']} [{comps}]")
        written.append(bp)
    return written


def stage_render(examples, res: int, samples: int):
    if not BLENDER.exists():
        raise SystemExit(f"Blender not found at {BLENDER}")
    for source_id, path in examples:
        folder = out_root() / source_id
        bp_path = folder / "blueprint.json"
        if not bp_path.exists():
            stage_blueprints([(source_id, path)])
        bp = json.loads(bp_path.read_text())
        seed = int(json.loads(path.read_text()).get("seed") or 1)
        for style in STYLE_ORDER:
            hi = folder / "renders_2048" / PANEL[style]
            job = build_job(bp, style, str(hi), seed=seed, resolution=res, samples=samples)
            job_path = folder / "jobs" / f"{style}.json"
            job_path.parent.mkdir(parents=True, exist_ok=True)
            job_path.write_text(json.dumps(job))
            log(f"render {source_id} {style} {res}px samples={samples}")
            cmd = [
                "xvfb-run",
                "-a",
                str(BLENDER),
                "--background",
                "--python",
                str(RENDER_PY),
                "--",
                str(job_path),
            ]
            t0 = time.time()
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
            (folder / "logs").mkdir(parents=True, exist_ok=True)
            (folder / "logs" / f"{style}.log").write_text((proc.stdout or "") + "\n" + (proc.stderr or ""))
            dt = time.time() - t0
            if proc.returncode != 0 or not hi.exists():
                log(f"FAIL {source_id} {style} in {dt:.1f}s code={proc.returncode}")
                tail = (proc.stderr or proc.stdout or "")[-1500:]
                log(tail)
                continue
            downsample_png(hi, folder / PANEL[style], size=1024)
            sticker = folder / "stickers" / PANEL[style]
            sticker.parent.mkdir(parents=True, exist_ok=True)
            downsample_png(hi, sticker, size=512)
            log(f"OK {source_id} {style} {dt:.1f}s -> {folder / PANEL[style]}")


def stage_sheets(examples):
    rows = []
    for source_id, _path in examples:
        folder = out_root() / source_id
        example_strip(folder, source_id, folder / "contact_sheet.png", cell=320)
        rows.append((source_id, folder))
        log(f"strip {folder / 'contact_sheet.png'}")
    multi = out_root() / "contact_sheets" / "all_examples_AF.png"
    multi_sheet(rows, multi, cell=260)
    log(f"sheet {multi}")
    # style-only grid (C–F) is the same sheet; the all-examples sheet is the multi view
    return multi


def stage_generative(examples):
    payload = []
    for source_id, _path in examples:
        folder = out_root() / source_id
        bp_path = folder / "blueprint.json"
        if not bp_path.exists():
            stage_blueprints([(source_id, _path)])
        payload.append(
            {
                "source_id": source_id,
                "blueprint": json.loads((folder / "blueprint.json").read_text()),
                "doodle_png": str(folder / "A_original.png"),
            }
        )
    result = run_generative(payload, out_root() / "generative", list(STYLE_ORDER))
    log(f"generative {result['status']} {result['report']}")
    return result


def stage_metrics(examples):
    rows = []
    for source_id, _path in examples:
        folder = out_root() / source_id
        stats = judge_example(folder)
        (folder / "quality.json").write_text(json.dumps(stats, indent=2))
        rows.append({"source_id": source_id, **stats})
        log(
            f"quality {source_id} band={stats.get('max_band_score')} "
            f"plush-clay fill={stats.get('plush_fill_minus_clay')}"
        )
    (out_root() / "quality.json").write_text(json.dumps(rows, indent=2))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["blueprints", "render", "sheets", "generative", "metrics", "all"])
    ap.add_argument("--only", default="", help="comma-separated source ids")
    ap.add_argument("--res", type=int, default=2048)
    ap.add_argument("--samples", type=int, default=32)
    args = ap.parse_args()
    examples = selected(args.only)
    if not examples:
        raise SystemExit(f"no examples matched {args.only}")
    if args.stage in ("blueprints", "all"):
        stage_blueprints(examples)
    if args.stage in ("render", "all"):
        stage_render(examples, args.res, args.samples)
    if args.stage in ("sheets", "all"):
        stage_sheets(examples)
    if args.stage in ("generative", "all"):
        stage_generative(examples)
    if args.stage in ("metrics", "all"):
        stage_metrics(examples)


if __name__ == "__main__":
    main()
