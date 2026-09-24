"""
Blender -P entry: one doodle × one style.

Usage:
  blender --background --python scripts/run_job.py -- \
    --doodle corpus/doodles/01_blob.json \
    --style gummy --style-version v1 --seed 1 \
    --out out/renders/01_blob__gummy__v1__s1.png \
    --doodle-id 01_blob
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure lab package importable when run via Blender -P
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args(argv=None):
    # Blender passes args after "--"
    if argv is None:
        argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = argv[1:]
    p = argparse.ArgumentParser(description="Render one doodle with one style")
    p.add_argument("--doodle", required=True)
    p.add_argument("--style", required=True)
    p.add_argument("--style-version", default="v1")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", required=True)
    p.add_argument("--doodle-id", default=None)
    p.add_argument("--meta", default=None)
    return p.parse_args(argv)


def main():
    args = parse_args()
    from lab.pipeline import run_pipeline

    meta = run_pipeline(
        doodle_path=args.doodle,
        style_id=args.style,
        style_version=args.style_version,
        seed=args.seed,
        output_png=args.out,
        metadata_path=args.meta,
        doodle_id=args.doodle_id,
    )
    status = "OK" if meta.get("success") else "FAIL"
    print(f"[run_job] {status} {meta.get('doodle_id')} {meta.get('style_id')} {meta.get('render_time_ms')}ms")
    if not meta.get("success"):
        print(meta.get("error"))
        sys.exit(1)


if __name__ == "__main__":
    main()
