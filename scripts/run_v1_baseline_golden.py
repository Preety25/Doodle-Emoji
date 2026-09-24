"""Render golden-12 with V1 recipes into out/v2/v1_baseline/ for V1→V2 sheets."""
from __future__ import annotations
import csv, json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.export import make_derivatives_pillow
BLENDER = os.environ.get("BLENDER_BIN", "/workspace/tools/blender/blender-4.2.9-linux-x64/blender")
STYLES = [("gummy","v1"),("clay","v1"),("plush","v1")]
SEED = 1

def main():
    out_dir = ROOT / "out" / "v2" / "v1_baseline"
    out_dir.mkdir(parents=True, exist_ok=True)
    man = json.loads((ROOT / "corpus" / "golden" / "manifest.json").read_text())
    rows = []
    total = len(man["doodles"]) * len(STYLES)
    i = 0
    for d in man["doodles"]:
        for style_id, style_version in STYLES:
            i += 1
            stem = f"{d['id']}__{style_id}__{style_version}__s{SEED}"
            out_png = out_dir / "renders" / f"{stem}.png"
            meta_path = out_dir / "renders" / f"{stem}.json"
            out_png.parent.mkdir(parents=True, exist_ok=True)
            if out_png.exists() and meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text())
                    if meta.get("success"):
                        print(f"[{i}/{total}] skip {stem}")
                        rows.append(meta)
                        continue
                except Exception:
                    pass
            print(f"[{i}/{total}] {stem} ...", flush=True)
            cmd = ["xvfb-run","-a",BLENDER,"--background","--python",str(ROOT/"scripts"/"run_job.py"),"--",
                   "--doodle", str(ROOT/d["path"]), "--style", style_id, "--style-version", style_version,
                   "--seed", str(SEED), "--out", str(out_png), "--doodle-id", d["id"], "--meta", str(meta_path)]
            t0 = time.time()
            proc = subprocess.run(cmd, capture_output=True, text=True)
            meta = {"doodle_id": d["id"], "style_id": style_id, "style_version": style_version, "seed": SEED,
                    "success": False, "render_time_ms": int((time.time()-t0)*1000), "output_path": str(out_png),
                    "returncode": proc.returncode}
            if meta_path.exists():
                try: meta.update(json.loads(meta_path.read_text()))
                except Exception as e: meta["error"] = str(e)
            if out_png.exists() and meta.get("success"):
                make_derivatives_pillow(out_png, out_dir/"derivatives", stem)
            else:
                meta["success"] = False
                meta["error"] = (meta.get("error") or proc.stderr or proc.stdout or "")[-2000:]
            rows.append(meta)
            print(f"  -> {'OK' if meta.get('success') else 'FAIL'} {meta.get('render_time_ms')}ms", flush=True)
    csv_path = out_dir / "benchmark.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["doodle_id","style_id","style_version","success","render_time_ms","output_path","error"], extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"Done {sum(1 for r in rows if r.get('success'))}/{len(rows)} -> {csv_path}")

if __name__ == "__main__":
    main()
