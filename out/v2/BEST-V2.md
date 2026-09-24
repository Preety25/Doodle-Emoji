# BEST-V2 — Doodle Emoji Stylization Lab

**Winning iteration:** `iter_03` (`out/v2/iter_03/`)  
**Commit SHA:** `e61387ce57ff087d7e2f9ff79bb33f2674c5419e` (`e61387c`)  
**Branch:** `stylization/v2-quality-pass` (tip may include abandon note `dc8505e`)  
**Transform / recipes:** `tx.v2.2` — `recipes/{gummy,clay,plush,glossy}.v2.json`  
**Blender:** 4.2.9 LTS via `xvfb-run -a`  
`BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender`

## What changed (vs V1 / vs iter_01–02)

1. **Orientation fix:** `face_toward_camera` **+90° X** (was −90°) — upright silhouette, inflate toward camera.
2. **Pillowy geometry:** thin `extrusion_wall` + bilateral midplane inflate + post-inflate unify remesh + smooth (not slab extrusion / voxel-melt default).
3. **Heuristic semantic plan** before style (`lab/semantic_plan.py`) — styles do not invent faces/parts.
4. **Material separation:** gummy transmission/SSS/candy_lift/bubbles; clay matte bump; plush sheen+fiber_fringe; glossy opaque PVC clearcoat.
5. **Camera:** front_perspective, low yaw/pitch, long lens — silhouette first.

## Why it won
- Largest visual jump: readable hearts/stars face-on with candy/clay materials vs inverted slabs in iter_01.
- Measurable rubric gain: holistic **~2 → ~6.0 → ~6.8**.
- iter_04 overshoot regressed plush; stopped on plateau.

## Benchmark results
- Golden-12 × {gummy, clay, plush, glossy} = **48/48 success**
- CSV: `out/v2/iter_03/benchmark.csv`
- Contacts: `out/v2/iter_03/contact_sheets/` and `out/v2/comparisons/`
- V1 baseline: `out/v2/v1_baseline/` (36/36)

## Remaining weaknesses
1. Residual horizontal ripple / softbox stripe on closed volumes  
2. Plush still under-differentiated from clay  
3. Small features (rocket fins, teddy ears) soften under unify remesh  
4. Gummy bubbles still weak vs recipe-PDF internal-air signature  
5. Complex multi-part depth below art-direction refs  

## Exact next recommended experiment
**Adaptive remesh / feature-aware voxel:** skip or shrink voxel on thin components; preserve fin/ear islands; OR replace unify remesh with normal-aware Laplacian smooth only on closed fills. Secondary: EEVEE volume scatter / bubble mesh boolean for true internal gummy air. Do **not** raise plush sheen further without a matte pile model.

## Ready to become new baseline?
**No — not yet.** Strong candidate quality-pass; keep V1 available until small-feature + plush signature improve.

## Visual pack
See `out/v2/comparisons/README.md` and `out/v2/EVALUATION.md`.
