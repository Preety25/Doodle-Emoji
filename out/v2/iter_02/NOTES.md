# Iteration 02 — orientation + pillowy unify

## Changes
1. `face_toward_camera`: −90° → **+90° X** (upright silhouette; inflate toward camera)
2. Recipes `tx.v2.1`: thinner walls, higher inflation, flatter camera, stronger SSS/bump/sheen/rim
3. Geometry: post-inflate **unify_remesh** + stronger smooth (kill solidify ring banding); early subsurf off
4. Gummy bubbles: glassier + tighter interior placement

## Benchmark
- 48/48 success (golden-12 × gummy/clay/plush/glossy)
- Contact sheets under `out/v2/iter_02/contact_sheets/`

## Eval vs refs (written)
| Criterion | Score /10 | Notes |
|-----------|-----------|-------|
| Semantic Recognition | 7 | Heart/star/face/plant readable; messy/open honest |
| Intent Preservation | 7 | Asymmetry / doodle quirks kept |
| Wow / material | 5 | Glossy/gummy speculars OK; clay matte OK; plush≈clay |
| Dimensional (not slab) | 6 | Much better face-on pillow; residual mid-groove |
| Style fidelity | 5 | Gummy vs clay distinguishable; plush weak; glossy≈gummy |
| Legibility @ sticker | 7 | Silhouettes clear |

**Holistic ~6/10** — big jump from iter_01 (~2/10).

## Top remaining gaps (for iter_03)
1. **Mid horizontal crease/groove** on closed volumes (solidify sandwich → remesh waist)
2. **Plush under-differentiated** from clay (need fuzz fringe / stronger sheen+bump)
3. **Gummy candy read incomplete** — translucency/rim glow mild; bubbles still read as surface dots vs internal air
