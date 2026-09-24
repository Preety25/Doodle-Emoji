# V3 summary

Semantic reconstruction, then a style. Not a global remesh with four shaders.

## Architecture

1. **Recognition** — category handler, selected by the corpus hint. Not a general classifier.
2. **Blueprint** — `doodle.blueprint.v3` JSON: hypothesis, confidence, orientation, components with source strokes, relationships, must-preserve / may-complete / never-invent.
3. **Reconstruction** — one mesh per component. Thickness comes from that component's own span. Eyes, the window, and the spiral are capped so they don't swell into the parent.
4. **Style** — material + light + micro-geometry.
   - Gummy: transmission, subsurface, interior bubble spheres, broader light.
   - Clay: matte, low-frequency 3D dents (not a function of Y), large soft key.
   - Plush: fiber shells pushed slightly outward, stitch seam, sheen, very soft light. Not clay with a roughness tweak.
   - Glossy: less inflate, clearcoat, small key for one controlled highlight.
5. **Render** — Blender 4.2.9 EEVEE, transparent film, 2048, premultiplied downsample to 1024 and 512. Camera profile per subject.
6. **Generative** — prompt builder + adapter. **Did not run live.** Status `BLOCKED_NO_API`. Stubs are labeled cards, not fake stickers.

V1/V2 code in `lab/` is untouched and is not called for these renders.

## Category-specific vs general

Specific: heart cleft pinning, rocket nose split + separate fins + optional flame, teddy part map with no invented snout, plant pot/stem/leaves, rose bloom + spiral cord, messy low-confidence refusal.

General: stroke normalize (Y-up), polygon/tube mesher, dome inflate from distance-to-boundary, style multipliers, contact sheets.

## How to re-run

```bash
export BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender
# install once if needed: Blender 4.2.9 under that path, plus pillow/numpy, xvfb, libegl1
python3 scripts/run_v3.py --stage all --res 2048 --samples 24
# or: --stage blueprints | render | sheets | generative | metrics
#     --only 02_heart,06_rocket
```

Set `OPENAI_API_KEY` or `GEMINI_API_KEY` / `GOOGLE_API_KEY` or `REPLICATE_API_TOKEN` and re-run `--stage generative` for live edits. The prompt is the doodle plus the blueprint summary plus the preserve constraints.

## Generative

**BLOCKED_NO_API.** Keys checked: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `REPLICATE_API_TOKEN`. All missing.

Report: `out/v3/generative/BLOCKED_NO_API.md`  
Requests (real prompts): `out/v3/generative/requests/`

## Paths

| What | Where |
|---|---|
| Per example A–F, blueprint, strip | `out/v3/02_heart/`, `06_rocket/`, `07_teddy/`, `05_plant/`, `09_rose/`, `12_messy_incomplete/` |
| Panels | `A_original.png` `B_blueprint.png` `C_gummy.png` `D_clay.png` `E_plush.png` `F_glossy.png` |
| High-res | `out/v3/<id>/renders_2048/` (gitignored) |
| All-examples sheet | `out/v3/contact_sheets/all_examples_AF.png` |
| Per-example strip | `out/v3/<id>/contact_sheet.png` |
| This note | `out/v3/SUMMARY.md` |
| Failure split | `out/v3/FAILURE_REPORT.md` |
| Longer architecture | `docs/v3/ARCHITECTURE.md` and `V3-POC.md` |

PNGs are gitignored and are on disk. JSON blueprints and these reports are committed.

## Quality, short

All six examples have A–F on disk. Rocket fins and teddy ears are separate meshes, not a V2 unify-remesh melt. Styles are distinguishable; plush vs clay is the closest pair, especially small. The rocket flame is a declared completion, not a traced stroke. Details and the things that still fail are in `FAILURE_REPORT.md`.
