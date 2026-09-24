# VISUAL DECISION REPORT — Doodle Emoji Stylization Lab

**Lab path:** `/workspace/stylization-lab/`  
**Date:** 2026-09-22 (America/Toronto)  
**Blender:** 4.2.9 LTS (EEVEE Next, `film_transparent`)  
**transformation_version:** `tx.v1.0.0`  
**Benchmark:** 20 doodles × 3 styles = **60/60 success**

Evidence roots:
- Renders: `out/renders/`
- Derivatives: `out/derivatives/`
- Contact sheets: `out/contact_sheets/`
- Metrics: `out/metrics/benchmark.csv`
- Evaluation: `out/reports/evaluation.md`
- Legibility: `out/reports/legibility.md`
- AI compare: `out/reports/ai_compare.md`
- Visual language: `docs/visual_language.md` (Batch-1 + Batch-2)

---

## A. Visual system

### DOCUMENTED
- Principle **POLISH, DON'T REPLACE** encoded as: preserve components, asymmetry, open/closed; no invented faces.
- Constants: 1024 RGBA master, transparent void, mild ¾ camera, studio 3-point lights, versioned JSON recipes.
- Batch-1 refs (gloss blob, gradient gummy star, magenta gummy star, kawaii heart) → inflation, low roughness, SSS/transmission, blunt tips.
- Batch-2 refs (`docs/refs/batch2/`) expand spectrum: matte ceramic/tech, foil balloon, satin gummy, extruded toy icons, voxel toys, segmented latex balloon — synthesized in `docs/visual_language.md`.

### RECOMMENDATION
Lock the **shareable sticker language** as: soft inflated silhouette + recipe material + clean studio light. Defer foil/voxel/balloon as later recipes. Faces remain interpretation-gated.

---

## B. Procedural architecture

### DOCUMENTED
Pipeline (renderer-agnostic front; Blender back):

```
stroke JSON → parse → normalize (Y-flip, unit bbox, RDP) → interpret (open/closed, components)
    → bpy curves (2D fill closed | tube open) → solidify/bevel[/remesh/smooth]
    → recipe materials → fixed lights/camera → EEVEE RGBA PNG → derivatives
```

Modules under `lab/`; CLI `scripts/run_job.py` / `scripts/run_benchmark.py`.  
Headless requirement on this box: `libegl1` + `xvfb-run -a`.

### RECOMMENDATION
Keep stroke JSON as canonical source. Treat Blender as **hero server renderer / style lab**, not on-device runtime. Preserve modular recipe JSON so mobile preview can approximate the same parameters later.

---

## C. Style recipes

| Recipe | Intent | Key defaults (v1) | Evidence |
|--------|--------|-------------------|----------|
| **gummy.v1** | Soft inflated glossy candy | roughness 0.06, clearcoat 1.0, transmission 0.12, sss 0.4, extrude 0.28, remesh+smooth | Contact `contact_gummy.png`; star/heart/blob inspected |
| **clay.v1** | Matte handmade | roughness 0.70, sss 0.5, bump 0.02, softer lights | `contact_clay.png`; Batch-2 ceramic/tech affinity |
| **plush.v1** | Cuddly thick SSS | roughness 0.88, specular 0.05, sss 0.75, thicker bevel | `contact_plush.png`; most forgiving at small size |

Tuning log: `docs/recipe_tuning_notes.md`.

---

## D. Benchmark results

### DOCUMENTED
| Metric | Value |
|--------|-------|
| Success | **60 / 60** |
| Median render_time_ms | **7617** |
| p95 render_time_ms | **9170** |
| Mean render_time_ms | **~7600** |
| Samples | 32 EEVEE TAA (software Mesa GL via Xvfb) |
| Derivatives | 180 PNGs (512/256/128 × 60) |
| Contact sheets | `contact_{gummy,clay,plush}.png`, `contact_all_styles.png` |

CSV: `out/metrics/benchmark.csv`.

Qualitative (inspected subset): closed blob/heart/star/cloud delight high; stick/letter/open weaker shareability; multi-component preserved; face head OK but eye discs undersized vs head after normalize+framing.

---

## E. Failure taxonomy

### DOCUMENTED (lab_auto_v1 + inspected)
Top observed classes (counts after enrichment):

| Class | Count | Notes |
|-------|------:|-------|
| silhouette_collapsed | ~19 | **Mostly IoU proxy false positives** (2D source vs 3D camera). Do not over-weight. |
| thin_features_lost | ~14 | Stick/letter/number/open at small sizes |
| open_stroke_failed | ~6 | Tubes work structurally but weak as “emoji” |
| over_smoothed_identity_loss | ~1 | Plush remesh softens star points |
| legibility_fail_128 | ~1+ | Stick/letter class |
| self_intersect_artifacts | ~1 | Deliberately bad doodle |

Other vocabulary ready but rare this run: empty_or_invisible, component_merge_error, wrong_material_look, lighting_washout, framing_*, alpha_holes, color_not_preserved, render_crash.

### RECOMMENDATION
Replace IoU-proxy silhouette scoring with **camera-projected mask IoU** or human contact-sheet review for gating. Add min feature thickness guard for open strokes.

---

## F. Procedural vs AI vs hybrid

### DOCUMENTED
| Path | Status | Artifact |
|------|--------|----------|
| **A Procedural** | Complete 60/60 | `out/renders/` |
| **B AI image-conditioned** | **BLOCKED_NO_API** | Need `OPENAI_API_KEY` / `GEMINI_API_KEY` / `REPLICATE_API_TOKEN` |
| **C Hybrid** | Design + **pseudo-hybrid stubs only** (NOT real AI) | `out/derivatives/ai_compare/*__pseudo_hybrid.png` |

Report: `out/reports/ai_compare.md`. Scaffolding in `scripts/ai_compare.py` implements: rasterize source → (optional API) → composite AI RGB with **procedural alpha hard mask**.

### RECOMMENDATION
Default production path: **procedural hero** for brand control + reproducibility. Add hybrid AI material enrichment only after API bake-off on same 20 doodles. Never let AI redraw silhouette without alpha constraint.

---

## G. Latency

### DOCUMENTED
- Per job median **~7.6 s**, p95 **~9.2 s** on this CPU/software-GL lab box (32 samples).
- Includes Blender startup + remesh; production GPU EEVEE expected substantially faster.
- AI latency: N/A (blocked).

### RECOMMENDATION
Target UX: optimistic on-device 2D preview &lt;300ms; server hero &lt;3s on GPU. Lab numbers are **upper bound**, not product SLA.

---

## H. Cost

### DOCUMENTED
- Procedural: compute only (Blender LTS binary; no per-render license fee for this POC).
- AI: $0 this run; scaffold estimates ~$0.04/image if OpenAI image edit used (verify current pricing before commit).

### RECOMMENDATION
Procedural scales with CPU/GPU fleet; AI adds marginal cost + variance. Hybrid = procedural always + AI optional paid tier.

---

## I. Production recommendation

### DOCUMENTED RESULTS vs RECOMMENDATION

**Results:** Procedural Blender recipes already produce recognizable, shareable stickers for closed doodles with consistent brand look across 20×3. Open/thin doodles need thickening. AI not compared empirically this run.

**Recommendation (honest):**
1. **Proceed with procedural 3D foundation + versioned recipes** as the controllable core of Draw → Polish → Share.
2. Treat **gummy** as primary delight hero; clay/plush as first-party alternates.
3. Gate AI as **optional enrichment** (materials/character) behind hybrid alpha lock — unblock with API key and re-run `ai_compare.py` before any AI architecture bet.
4. Do **not** pick a final production renderer from aesthetics alone until AI/hybrid scores exist on the same rubric.

---

## J. Mobile implications

### DOCUMENTED / IMPLICATIONS
- Blender stays **server-side / lab**.
- Mobile: capture strokes → upload canonical JSON → return PNG derivatives; optional local Skia preview approximating extrude+flat shading.
- Recipe JSON should drive both server EEVEE and on-device preview approximations.
- 512 sticker + 128 tray rules from legibility study should inform client export presets.
- Batch-2 foil/voxel are GPU/shader heavier conceptually — preview approximates, server heroes.

---

## K. Next implementation task in Cursor

**Suggested next POC:**  
`Stroke JSON → on-device preview approximation (React Native Skia or R3F) matching gummy.v1 geometry params (extrude/bevel proxies) + server render parity test`  

Plus, in parallel if keys available: **unblock AI compare** (`OPENAI_API_KEY`) on the same 20 doodles with hybrid alpha lock and fill section F with real scores.

Secondary hardening: min tube radius / silhouette thicken for open strokes; face-component scale floor; camera-space silhouette metric.

---

## Appendix — key paths for parent

| Item | Path |
|------|------|
| Decision report | `out/reports/VISUAL_DECISION_REPORT.md` |
| Contact sheets | `out/contact_sheets/` |
| Metrics CSV | `out/metrics/benchmark.csv` |
| Evaluation | `out/reports/evaluation.md` |
| Legibility | `out/reports/legibility.md` |
| AI compare | `out/reports/ai_compare.md` |
| Visual language (+Batch-2) | `docs/visual_language.md` |
| Blender bin | `/workspace/tools/blender/blender-4.2.9-linux-x64/blender` |

---

## Appendix — Batch-3 style variants (2026-09-22)

Refs in `docs/refs/batch3/` folded into `docs/visual_language.md`. New recipes (parents unchanged as benchmark heroes):

| Recipe | Parent | Approximation |
|--------|--------|---------------|
| `gummy_sugar.v1` | gummy.v1 | Translucent jelly + high-freq bump sugar crust |
| `clay_claymorph.v1` | clay.v1 | Pillowy chalky claymorph, large bevels |
| `plush_fiber.v1` | plush.v1 | Sheen + fine bump velvet pile (not particle fur) |

Sample proof renders (9/9): `out/renders_variants/` · contact: `out/contact_sheets/contact_batch3_variants.png`.

**Honesty:** Fiber fur and crystal sugar are EEVEE shader proxies. True hair/particles remain a future offline bake path. Heroes for the 60-run benchmark stay `gummy/clay/plush.v1`.
