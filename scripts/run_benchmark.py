"""Orchestrate 20×3=60 Blender renders + derivatives + metrics CSV + contact sheets."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab.export import make_derivatives_pillow

BLENDER = os.environ.get(
    "BLENDER_BIN",
    "/workspace/tools/blender/blender-4.2.9-linux-x64/blender",
)
STYLES = [("gummy", "v1"), ("clay", "v1"), ("plush", "v1")]
SEED = 1


def load_manifest():
    with (ROOT / "corpus" / "manifest.json").open() as f:
        return json.load(f)


def run_one(doodle_id: str, doodle_path: Path, style_id: str, style_version: str, seed: int) -> dict:
    stem = f"{doodle_id}__{style_id}__{style_version}__s{seed}"
    out_png = ROOT / "out" / "renders" / f"{stem}.png"
    meta_path = ROOT / "out" / "renders" / f"{stem}.json"
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "xvfb-run", "-a",
        BLENDER,
        "--background",
        "--python",
        str(ROOT / "scripts" / "run_job.py"),
        "--",
        "--doodle",
        str(doodle_path),
        "--style",
        style_id,
        "--style-version",
        style_version,
        "--seed",
        str(seed),
        "--out",
        str(out_png),
        "--doodle-id",
        doodle_id,
        "--meta",
        str(meta_path),
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    wall_ms = int((time.time() - t0) * 1000)
    meta = {
        "doodle_id": doodle_id,
        "style_id": style_id,
        "style_version": style_version,
        "transformation_version": "tx.v1.0.0",
        "seed": seed,
        "success": False,
        "render_time_ms": wall_ms,
        "width": 1024,
        "height": 1024,
        "file_size_bytes": 0,
        "has_alpha": False,
        "output_path": str(out_png),
        "returncode": proc.returncode,
    }
    if meta_path.exists():
        try:
            with meta_path.open() as f:
                m = json.load(f)
            meta.update(m)
        except Exception as e:
            meta["error"] = f"meta read: {e}"
    if out_png.exists() and meta.get("success"):
        meta["file_size_bytes"] = out_png.stat().st_size
        meta["has_alpha"] = True
        deriv = make_derivatives_pillow(out_png, ROOT / "out" / "derivatives", stem)
        meta["derivatives"] = deriv
    else:
        if not meta.get("error"):
            meta["error"] = (proc.stderr or proc.stdout or "")[-4000:]
        meta["success"] = False
    # always keep logs snippet
    log_path = ROOT / "out" / "metrics" / "logs" / f"{stem}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text((proc.stdout or "")[-8000:] + "\n---STDERR---\n" + (proc.stderr or "")[-8000:])
    return meta


def write_csv(rows, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "doodle_id", "style_id", "style_version", "transformation_version", "seed",
        "success", "render_time_ms", "width", "height", "file_size_bytes", "has_alpha",
        "output_path", "error",
    ]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            err = r.get("error")
            if err and len(str(err)) > 200:
                r = {**r, "error": str(err)[:200].replace("\n", " ")}
            w.writerow(r)


def main():
    # ensure pillow
    try:
        import PIL  # noqa
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "Pillow"])

    man = load_manifest()
    rows = []
    total = len(man["doodles"]) * len(STYLES)
    i = 0
    for d in man["doodles"]:
        dpath = ROOT / d["path"]
        for style_id, style_version in STYLES:
            i += 1
            print(f"[{i}/{total}] {d['id']} × {style_id} ...", flush=True)
            row = run_one(d["id"], dpath, style_id, style_version, SEED)
            rows.append(row)
            print(f"  -> {'OK' if row.get('success') else 'FAIL'} {row.get('render_time_ms')}ms", flush=True)

    csv_path = ROOT / "out" / "metrics" / "benchmark.csv"
    write_csv(rows, csv_path)
    ok = sum(1 for r in rows if r.get("success"))
    print(f"Done: {ok}/{len(rows)} success. CSV: {csv_path}")

    # contact sheets
    try:
        from scripts.make_contact_sheets import make_all
        make_all()
    except Exception as e:
        print(f"contact sheets deferred: {e}")
        # try importing as module path
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import make_contact_sheets
            make_contact_sheets.make_all()
        except Exception as e2:
            print(f"contact sheets failed: {e2}")


if __name__ == "__main__":
    main()
