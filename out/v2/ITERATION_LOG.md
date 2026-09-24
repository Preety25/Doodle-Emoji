# V2 Quality Pass — Iteration Log

Branch: `stylization/v2-quality-pass`  
Transform: `tx.v2.0` → `tx.v2.1` (from iter 02)  
Blender: 4.2.9 LTS via `xvfb-run -a` (`BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender`)

## Foundation (pre-iter commits)

- Golden-12 corpus under `corpus/golden/`
- Heuristic `lab/semantic_plan.py` (no neural nets)
- Geometry V2: thin wall + bevel + subsurf (not voxel remesh) + front inflate + chaikin
- Camera V2: front_perspective / subtle_34, low yaw
- Recipes: `glossy|gummy|clay|plush.v2.json`
- Pipeline records subject/confidence/completion_budget/transform_version

## Iteration notes

### iter_01 (53bface) — diagnostic baseline
- Partial renders (~19/48). See `out/v2/iter_01/NOTES.md`.
- **Gaps:** (1) −90° face rotation inverted silhouette + inflate away from camera; (2) extrusion walls dominate; (3) weak material signatures.
- **Score (holistic vs refs):** ~2/10 Wow, silhouette often fail for heart.

### iter_02 — orientation + pillowy + material punch
- Fix `face_toward_camera` to **+90° X**.
- Recipes → `tx.v2.1`: thinner walls, higher inflation, stronger bevel, flatter camera, stronger SSS/bubbles/bump/sheen/rim.
- Broader inflate falloff; post-inflate unify_remesh + smooth.
- Benchmark: **48/48 OK**. Holistic ~6/10 vs refs (was ~2/10).
- Remaining: mid-groove, plush≈clay, gummy bubble/translucency.
- Details: `out/v2/iter_02/NOTES.md`
