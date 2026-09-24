# V3 architecture — semantic reconstruction + render

V3 does not continue the V2 remesh / inflate path. V1 and V2 stay in `lab/` for comparison. The V3 entry point is `scripts/run_v3.py`. Blender is one experimental renderer behind a job JSON, not the product architecture.

## Pipeline

1. **Semantic recognition** (`lab/v3/recognize.py` + `lab/v3/handlers/`)
   - Category-specific handlers for heart, rocket, teddy, plant, rose, and messy/incomplete.
   - The corpus category hint selects the handler. This POC does not claim general recognition.
   - Output is a blueprint JSON (`doodle.blueprint.v3`).

2. **Structural reconstruction** (`lab/v3/reconstruct.py`)
   - Each blueprint component becomes its own primitive (closed volume or open tube).
   - Thickness, inflate, and crease are computed from that component's span.
   - Small parts (eyes, window, spiral) are capped so they are not given the body's thickness.
   - No global voxel remesh. No boolean union. Fins, ears, leaves, and the spiral stay separate meshes.

3. **Stylization** (`lab/v3/styles.py`)
   - Gummy, clay, plush, and glossy change material, light, and micro-geometry together.
   - Gummy: transmission, subsurface, interior bubble spheres.
   - Clay: matte roughness, low-frequency 3D dents (not a Y-axis wave).
   - Plush: fiber pile shells pushed slightly past the silhouette, plus a stitch seam. Not a clay shader with the roughness turned up.
   - Glossy: low roughness, clearcoat, a small key light for a crisp highlight, less inflate.

4. **Rendering** (`lab/v3/procedural/blender_render.py`)
   - Blender 4.2.9 EEVEE, transparent film.
   - High-res still (default 2048), then premultiplied downsample to 1024 and 512.
   - Camera yaw, pitch, lens, and margin come from the subject profile. Rocket is more three-quarter than the heart; the messy gesture is nearly orthographic.
   - Lights are square area lights. No wide horizontal strips, no ground plane.

5. **Generative adapter** (`lab/v3/generative/`)
   - Builds an edit prompt from the doodle plus the blueprint summary and the preserve / complete / never-invent lists.
   - Calls OpenAI, Gemini, or Replicate only when a key is set.
   - Otherwise writes `BLOCKED_NO_API` and a labeled stub card. The stub is not a render.

## Blueprint

Required fields: `subject_hypothesis`, `confidence`, `orientation`, `major_components` (id, name, source strokes), `component_relationships`, `features_must_preserve`, `features_may_complete`, `features_must_never_invent`.

What is category-specific:

| Handler | What it knows |
|---|---|
| `heart_v3` | one contour, cleft + bottom point pinned, no mirror |
| `rocket_v3` | splits the taper into nose + body, keeps fins and window as separate meshes, may complete a small flame |
| `teddy_v3` | head, body, two ears, two eyes; does not invent a snout |
| `plant_v3` | pot, stem tube, two leaves |
| `rose_v3` | bloom volume, spiral as its own cord, stem, one leaf |
| `messy_v3` | LOW confidence. Polishes strokes. Refuses to close them into a star |

What is general: stroke loading, Y-up normalization (shared with `lab/normalize.py`), 2D geometry helpers, the volume/tube mesher, style application, contact sheets.

## What V3 deliberately does not do

- Global remesh of the whole doodle.
- One pillowy slab per closed contour with the same thickness.
- One camera for every subject.
- Style as a shader swap on a single mesh.
- Horizontal ripple displacement.
- A mobile app, or edits to product scope docs.

## Re-run

```bash
export BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender
python3 scripts/run_v3.py --stage all --res 2048 --samples 24
```

Panels land in `out/v3/<id>/` as `A_original.png` … `F_glossy.png`, plus `blueprint.json`. PNGs are gitignored. Blueprints and the reports are not.
