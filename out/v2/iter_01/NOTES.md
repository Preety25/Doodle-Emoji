# Iteration 01 — foundation visual baseline (partial)

## Status
Partial golden benchmark (~19/48 frames completed before quality gaps diagnosed).
Commit: `53bface` (code foundation); renders on disk under `out/v2/iter_01/renders/`.

## Visual gaps vs refs (highest impact)
1. **Silhouette orientation inverted / inflation away from camera** — `face_toward_camera` used −90° about X, flipping upright (+Y→−Z) and sending front inflate to +Y (away from camera). Hearts read upside-down or as dome/slab; side walls dominate.
2. **Extrusion-wall read still too strong** — `extrusion_wall` ~0.11–0.14 with modest inflation → cookie/slab rather than pillowy candy.
3. **Material signatures weak** — gummy lacks visible jelly/bubbles/rim glow; clay too flat/featureless; plush sheen/fuzz under-read; camera yaw still reveals walls.

## Judgment
Not acceptable vs recipe-PDF / batch2–3 refs. Treat as diagnostic baseline only.
