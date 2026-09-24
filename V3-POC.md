# STYLIZATION LAB V3 — semantic reconstruction + render

Proof of concept: understand the doodle, then polish **that** drawing. The pipeline is recognition, then structural reconstruction, then stylization, then rendering. Blender is one experimental renderer. It is not the product architecture.

Branch: `stylization/v3-semantic-render` (from `stylization/v2-quality-pass`). No pull request. V1/V2 code is left in place and is not the V3 geometry path.

## What was built

- `lab/v3/handlers/` — category handlers for heart, rocket, teddy, plant, rose, messy/incomplete. General recognition is **not** solved. The corpus category selects the handler. Each handler still checks the strokes and can drop confidence.
- `lab/v3/schema.py` — blueprint: subject, confidence, orientation, components (ids, names, source strokes), relationships, must-preserve / may-complete / never-invent.
- `lab/v3/reconstruct.py` + `lab/v3/procedural/blender_render.py` — separate mesh per component, local dome from distance-to-boundary, no global remesh, no boolean union, no horizontal wave.
- Styles differ by material, light, and micro-geometry: gummy bubbles, clay dents, plush fiber + stitch, glossy clearcoat and a small key.
- Cameras differ by subject (rocket more three-quarter, messy nearly flat, rose pulled back so the spiral and stem fit).
- `lab/v3/generative/` — edit adapter and prompt builder. **Live calls did not run** (`BLOCKED_NO_API`). The request JSON is real.

## Golden set

| Doodle | Corpus | Blueprint subject | Confidence |
|---|---|---|---|
| heart | `corpus/golden/02_heart.json` | heart | HIGH |
| rocket | `corpus/golden/06_rocket.json` | rocket | HIGH (flame is a completion) |
| teddy | `corpus/golden/07_teddy.json` | teddy | HIGH |
| plant | `corpus/golden/05_plant.json` | potted_plant | HIGH |
| rose | `corpus/golden/09_rose.json` | rose | HIGH |
| messy | `corpus/golden/12_messy_incomplete.json` | unresolved_gesture | LOW |

Each folder `out/v3/<id>/` has `A_original.png` through `F_glossy.png`, `blueprint.json`, and `contact_sheet.png`. All six are on the sheet `out/v3/contact_sheets/all_examples_AF.png`.

Rocket fins and teddy ears are their own meshes. The messy path does not close the strokes into a star.

## Re-run

```bash
export BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender
python3 scripts/run_v3.py --stage all --res 2048 --samples 24
```

Blender used: **4.2.9 LTS** (`a10f621e649a`), EEVEE, transparent film, 2048 then downsample.

## Generative

`BLOCKED_NO_API`. See `out/v3/generative/BLOCKED_NO_API.md`. To run live, export `OPENAI_API_KEY`, `GEMINI_API_KEY` / `GOOGLE_API_KEY`, or `REPLICATE_API_TOKEN` and re-run `--stage generative`.

## Read next

- `docs/v3/ARCHITECTURE.md` — what is category-specific vs shared
- `out/v3/SUMMARY.md` — paths and how the styles differ
- `out/v3/FAILURE_REPORT.md` — recognition, reconstruction, rendering, and style, kept separate

PNGs are gitignored. They are on disk under `out/v3/`.
