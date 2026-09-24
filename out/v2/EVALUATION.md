# V2 Quality Pass — Evaluation Results

**BEST iteration:** `iter_03`  
**Commit:** `e61387c` (branch tip notes abandon iter_04 at `dc8505e`; recipes locked to iter_03)  
**Transform:** `tx.v2.2`  
**Blender:** 4.2.9 LTS (`BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender`)

## Rubric scores (Recognition-Assisted Polish vs docs/refs + recipe PDF language)

| Criterion | iter_01 | iter_02 | iter_03 (BEST) | Notes |
|-----------|---------|---------|----------------|-------|
| Semantic Recognition | 3 | 7 | 7.5 | Heart/star/face readable; rocket/teddy still simplified |
| Intent Preservation | 3 | 7 | 7.5 | Asymmetry/quirks kept |
| Authorship | 8 | 8 | 8 | Heuristic planner; no face invention |
| Wow / material | 2 | 5 | 6.5 | Gummy gloss+SSS; clay matte; plush softest but close to clay |
| Dimensional (not slab) | 2 | 6 | 7 | Face-on pillow; residual softbox stripe / mild ripples |
| Style fidelity | 2 | 5 | 6 | Gummy≠clay clearer; glossy≠gummy mild; plush weak |
| Legibility @ sticker | 4 | 7 | 7.5 | Size ladder readable to 128 |
| Spectrum compliance | 7 | 8 | 8 | LOW confidence stays faithful |
| **Holistic** | **~2** | **~6.0** | **~6.8** | |

## Failure taxonomy

| Failure class | Severity | Examples | Likely cause |
|---------------|----------|----------|--------------|
| Residual horizontal ripple / specular stripe | Med | heart, star closed volumes | Softbox highlight + remesh topology echo |
| Plush ≈ clay | Med | star/heart plush vs clay | EEVEE short-pile approx; fringe weak |
| Small-part melt | Med | rocket fins → capsule; teddy ears soft | unify_remesh voxel erodes thin features |
| Gummy bubbles as surface dots | Low | heart/star gummy | Sphere proxies not true volume scatter |
| Glossy ≈ gummy | Low–Med | side-by-side heroes | Shared inflate; glossy needs stronger opaque PVC contrast |
| Open/messy honest but plain | Low | 10/12 | Correct LOW-confidence path |

## V1 → V2 judgment
V2 upright silhouette + pillowy inflate is a clear win over V1 extrusion slabs for closed heroes (heart/star). Material wow still below recipe-PDF / batch2–3 references (especially layered gummy star + fiber plush teddy).

## Ready to become new baseline?
**Recommend: not yet.** Ship as quality-pass candidate on this branch; needs another pass on small-feature preservation + plush signature before replacing V1 as default product baseline.
