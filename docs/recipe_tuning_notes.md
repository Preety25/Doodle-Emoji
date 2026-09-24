# Recipe Tuning Notes

**Date:** 2026-09-22 (America/Toronto)  
**Blender:** 4.2.9 LTS EEVEE Next via `xvfb-run` (software Mesa GL)

## Method
1. Render `01_blob`, `02_heart`, `04_star` across gummy/clay/plush.
2. Inspect RGBA (mean RGB on alpha mask, silhouette coverage).
3. Adjust geometry bevel/extrusion, lighting energies, material roughness/SSS.
4. Lock values into `recipes/*.v1.json`.

## Issues found & fixes
| Issue | Fix |
|-------|-----|
| Closed curves extruded as hollow walls | Switch to 2D filled curve → mesh → Solidify |
| Heart nearly flat (bad parametric scale) | Re-scale classic heart by max extent |
| Soft silhouette lacking | Bevel ALL edges + Subsurf levels=2 |
| Underexposed under software GL | Raise light energies + view exposure +0.4; Standard view transform |
| `fill_mode=BOTH` invalid on 3D curves | Use 2D `BOTH` for closed; `FULL` for open tubes |
| Missing libEGL abort | Install `libegl1` + run under `xvfb-run -a` |

## Chosen defaults (see recipes + visual_language.md)
- **Gummy:** roughness 0.06, clearcoat 1.0, transmission 0.12, sss 0.4, extrude 0.28, bevel 0.12
- **Clay:** roughness 0.70, sss 0.5, bump 0.02, extrude 0.22, bevel 0.09, smooth_iters 2
- **Plush:** roughness 0.88, specular 0.05, sss 0.75, extrude 0.32, bevel 0.14

## Samples
Lab uses **32** EEVEE TAA samples for throughput (~8–15s/job on this box). Production may raise to 64–128.

## Batch-3 variants (2026-09-22)

| Recipe | Parent | Key deltas vs parent |
|--------|--------|----------------------|
| `gummy_sugar.v1` | gummy.v1 | roughness 0.22; transmission 0.28; bump_strength 0.45 @ scale 120; clearcoat 0.35 |
| `clay_claymorph.v1` | clay.v1 | bevel 0.16; smooth_iters 14; roughness 0.82; softer larger lights |
| `plush_fiber.v1` | plush.v1 | sheen_weight 0.85; bump_strength 0.28 @ scale 85; roughness 0.92 |

**Honesty:** Fiber and sugar are **shader approximations** under EEVEE. Particle hair / crystal meshes are out of scope for this lab pass.
