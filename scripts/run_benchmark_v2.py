"""Golden-12 × V2 styles benchmark + contact sheets for one iteration."""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
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
DEFAULT_STYLES = [("gummy", "v2"), ("clay", "v2"), ("plush", "v2"), ("glossy", "v2")]
SEED = 1


def load_golden():
    man = ROOT / "corpus" / "golden" / "manifest.json"
    with man.open() as f:
        return json.load(f)


def run_one(doodle_id, doodle_path, style_id, style_version, seed, out_dir: Path) -> dict:
    stem = f"{doodle_id}__{style_id}__{style_version}__s{seed}"
    out_png = out_dir / "renders" / f"{stem}.png"
    meta_path = out_dir / "renders" / f"{stem}.json"
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "xvfb-run", "-a",
        BLENDER,
        "--background",
        "--python",
        str(ROOT / "scripts" / "run_job.py"),
        "--",
        "--doodle", str(doodle_path),
        "--style", style_id,
        "--style-version", style_version,
        "--seed", str(seed),
        "--out", str(out_png),
        "--doodle-id", doodle_id,
        "--meta", str(meta_path),
    ]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    wall_ms = int((time.time() - t0) * 1000)
    meta = {
        "doodle_id": doodle_id,
        "style_id": style_id,
        "style_version": style_version,
        "seed": seed,
        "success": False,
        "render_time_ms": wall_ms,
        "output_path": str(out_png),
        "returncode": proc.returncode,
    }
    if meta_path.exists():
        try:
            meta.update(json.loads(meta_path.read_text()))
        except Exception as e:
            meta["error"] = f"meta read: {e}"
    if out_png.exists() and meta.get("success"):
        deriv = make_derivatives_pillow(out_png, out_dir / "derivatives", stem)
        meta["derivatives"] = deriv
    else:
        if not meta.get("error"):
            meta["error"] = (proc.stderr or proc.stdout or "")[-4000:]
        meta["success"] = False
    log_path = out_dir / "logs" / f"{stem}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text((proc.stdout or "")[-8000:] + "\n---STDERR---\n" + (proc.stderr or "")[-8000:])
    return meta


def make_contact_sheets(out_dir: Path, styles, doodle_ids):
    from PIL import Image, ImageDraw

    cs = out_dir / "contact_sheets"
    cs.mkdir(parents=True, exist_ok=True)
    cell, pad = 180, 8
    # per-style grids
    for style_id, style_version in styles:
        cols = 4
        rows = (len(doodle_ids) + cols - 1) // cols
        label_h = 20
        W = cols * cell + (cols + 1) * pad
        H = 36 + rows * (cell + label_h + pad) + pad
        canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
        draw = ImageDraw.Draw(canvas)
        draw.text((pad, 10), f"{style_id}.{style_version} golden-12", fill=(30, 30, 40, 255))
        for i, did in enumerate(doodle_ids):
            r, c = divmod(i, cols)
            x = pad + c * (cell + pad)
            y = 36 + pad + r * (cell + label_h + pad)
            p = out_dir / "renders" / f"{did}__{style_id}__{style_version}__s{SEED}.png"
            slot = Image.new("RGBA", (cell, cell), (255, 255, 255, 255))
            if p.exists():
                im = Image.open(p).convert("RGBA")
                im.thumbnail((cell, cell))
                ox = (cell - im.width) // 2
                oy = (cell - im.height) // 2
                slot.paste(im, (ox, oy), im)
            canvas.paste(slot, (x, y))
            draw.text((x, y + cell + 2), did, fill=(40, 40, 50, 255))
        canvas.save(cs / f"contact_{style_id}.png")

    # all-styles grid
    style_ids = [s[0] for s in styles]
    cols = 1 + len(style_ids)
    rows = len(doodle_ids)
    thumb = 120
    label_w = 130
    W = label_w + len(style_ids) * (thumb + pad) + pad
    H = 40 + rows * (thumb + pad) + pad
    canvas = Image.new("RGBA", (W, H), (245, 245, 248, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 8), "golden × styles", fill=(20, 20, 30, 255))
    for c, s in enumerate(style_ids):
        draw.text((label_w + c * (thumb + pad), 22), s, fill=(0, 0, 0, 255))
    for r, did in enumerate(doodle_ids):
        y = 40 + r * (thumb + pad)
        draw.text((pad, y + thumb // 2 - 6), did, fill=(20, 20, 30, 255))
        for c, (style_id, style_version) in enumerate(styles):
            x = label_w + c * (thumb + pad)
            p = out_dir / "renders" / f"{did}__{style_id}__{style_version}__s{SEED}.png"
            slot = Image.new("RGBA", (thumb, thumb), (255, 255, 255, 255))
            if p.exists():
                im = Image.open(p).convert("RGBA")
                im.thumbnail((thumb, thumb))
                slot.paste(im, ((thumb - im.width) // 2, (thumb - im.height) // 2), im)
            canvas.paste(slot, (x, y))
    canvas.save(cs / "contact_all_styles.png")
    return cs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", type=int, default=1)
    ap.add_argument("--styles", default="gummy,clay,plush,glossy")
    ap.add_argument("--hero-only-extra", action="store_true",
                    help="If set with fewer styles, still ok")
    ap.add_argument("--doodles", default="all", help="comma ids or all")
    args = ap.parse_args()

    iter_name = f"iter_{args.iter:02d}"
    out_dir = ROOT / "out" / "v2" / iter_name
    out_dir.mkdir(parents=True, exist_ok=True)

    styles = [(s.strip(), "v2") for s in args.styles.split(",") if s.strip()]
    man = load_golden()
    doodles = man["doodles"]
    if args.doodles != "all":
        want = set(args.doodles.split(","))
        doodles = [d for d in doodles if d["id"] in want]

    rows = []
    total = len(doodles) * len(styles)
    i = 0
    for d in doodles:
        dpath = ROOT / d["path"]
        for style_id, style_version in styles:
            i += 1
            print(f"[{i}/{total}] {d['id']} × {style_id}.{style_version} ...", flush=True)
            row = run_one(d["id"], dpath, style_id, style_version, SEED, out_dir)
            rows.append(row)
            print(f"  -> {'OK' if row.get('success') else 'FAIL'} {row.get('render_time_ms')}ms", flush=True)

    csv_path = out_dir / "benchmark.csv"
    fields = [
        "doodle_id", "style_id", "style_version", "transform_version", "seed",
        "success", "render_time_ms", "subject", "confidence", "completion_budget",
        "output_path", "error",
    ]
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            err = r.get("error")
            if err and len(str(err)) > 200:
                r = {**r, "error": str(err)[:200].replace("\n", " ")}
            w.writerow(r)

    ok = sum(1 for r in rows if r.get("success"))
    print(f"Done: {ok}/{len(rows)} success. CSV: {csv_path}")
    make_contact_sheets(out_dir, styles, [d["id"] for d in doodles])
    print(f"Contact sheets: {out_dir / 'contact_sheets'}")


if __name__ == "__main__":
    main()
