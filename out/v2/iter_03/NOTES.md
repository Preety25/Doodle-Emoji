# Iteration 03 — bilateral pillow + style separation

## Changes
1. Bilateral midplane inflate (outward both sides) to reduce remesh waist/mid-groove
2. Thinner walls + finer voxel; `tx.v2.2`
3. Gummy: candy_lift, higher transmission/SSS/rim
4. Plush: fiber_fringe displace + stronger sheen/bump
5. Glossy: opaque PVC (transmission 0) vs gummy jelly

## Benchmark
48/48 success. Contact sheets in `out/v2/iter_03/contact_sheets/`.

## Eval vs refs
| Criterion | Score /10 | Notes |
|-----------|-----------|-------|
| Semantic Recognition | 7.5 | Heart/star/face clear; complex multi-part softer |
| Intent Preservation | 7.5 | Doodle asymmetry kept |
| Wow / material | 6.5 | Gummy gloss+SSS better; clay matte OK; plush still close to clay |
| Dimensional | 7 | Pillowy face-on; residual softbox stripe / mild ripples |
| Style fidelity | 6 | Gummy≠clay clearer; glossy≠gummy mild; plush weak |
| Legibility | 7.5 | Good at sticker scale |

**Holistic ~6.8/10** (iter_02 ~6.0). Clear win over iter_02.

## Remaining gaps
1. Residual horizontal ripple/banding on some volumes (solidify topology limit)
2. Plush still under-differentiated vs clay
3. Gummy internal bubbles subtle; candy glow vs refs still short of recipe-PDF punch
