# Evaluation Report

**Rubric version:** lab_auto_v1 (heuristics) + inspected subset
**Note:** Scores are NOT collapsed to a single quality number.
**Caveat:** `silhouette_collapsed` from auto IoU proxy is often a false positive (2D source mask vs 3D camera projection). Prefer inspected silhouette scores for product calls.

## Dimensions (1–5)

silhouette_fidelity, recognition, quirk_preservation, material_quality, dimensionality, style_consistency, small_sticker_legibility, delight, shareability

## Failure class vocabulary

empty_or_invisible, silhouette_collapsed, over_smoothed_identity_loss, thin_features_lost, open_stroke_failed, component_merge_error, wrong_material_look, lighting_washout, framing_too_tight_or_loose, alpha_holes, self_intersect_artifacts, color_not_preserved, render_crash, legibility_fail_128

## Score table

| doodle | style | silhouette_fidelity | recognition | quirk_preservation | material_quality | dimensionality | style_consistency | small_sticker_legibility | delight | shareability | failures | source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01_blob | gummy | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | — | inspected |
| 01_blob | clay | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 01_blob | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 02_heart | gummy | 5 | 5 | 5 | 4 | 4 | 4 | 4 | 5 | 5 | — | inspected |
| 02_heart | clay | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 02_heart | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 03_cloud | gummy | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | lab_auto_v1 |
| 03_cloud | clay | 5 | 5 | 4 | 3 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 03_cloud | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 04_star | gummy | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | — | inspected |
| 04_star | clay | 5 | 5 | 4 | 4 | 3 | 4 | 4 | 3 | 4 | — | inspected |
| 04_star | plush | 4 | 5 | 3 | 4 | 5 | 4 | 4 | 4 | 4 | over_smoothed_identity_loss | inspected |
| 05_face | gummy | 4 | 5 | 5 | 4 | 4 | 4 | 4 | 5 | 4 | — | inspected |
| 05_face | clay | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 05_face | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 06_stick | gummy | 4 | 4 | 5 | 3 | 3 | 4 | 4 | 3 | 2 | thin_features_lost|legibility_fail_128 | inspected |
| 06_stick | clay | 2 | 2 | 4 | 4 | 3 | 4 | 3 | 3 | 4 | silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 06_stick | plush | 2 | 2 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 07_animal | gummy | 3 | 3 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | silhouette_collapsed | lab_auto_v1 |
| 07_animal | clay | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 07_animal | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 08_object | gummy | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | lab_auto_v1 |
| 08_object | clay | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 08_object | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 09_flower | gummy | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | lab_auto_v1 |
| 09_flower | clay | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 09_flower | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 10_open | gummy | 4 | 3 | 5 | 4 | 3 | 4 | 4 | 3 | 3 | open_stroke_failed | inspected |
| 10_open | clay | 2 | 2 | 4 | 3 | 3 | 4 | 4 | 3 | 4 | open_stroke_failed|thin_features_lost | lab_auto_v1 |
| 10_open | plush | 3 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | open_stroke_failed|thin_features_lost | lab_auto_v1 |
| 11_scribble | gummy | 2 | 2 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | open_stroke_failed|silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 11_scribble | clay | 2 | 2 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | open_stroke_failed|silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 11_scribble | plush | 2 | 2 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | open_stroke_failed|silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 12_multi | gummy | 3 | 3 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | inspected |
| 12_multi | clay | 2 | 2 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | — | lab_auto_v1 |
| 12_multi | plush | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | — | inspected |
| 13_overlap | gummy | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | lab_auto_v1 |
| 13_overlap | clay | 5 | 5 | 4 | 3 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 13_overlap | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 14_asym | gummy | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | lab_auto_v1 |
| 14_asym | clay | 5 | 5 | 4 | 3 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 14_asym | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 15_letter | gummy | 3 | 3 | 4 | 5 | 3 | 4 | 4 | 4 | 5 | silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 15_letter | clay | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 2 | 2 | thin_features_lost | inspected |
| 15_letter | plush | 3 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 16_number | gummy | 2 | 2 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 16_number | clay | 2 | 2 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 16_number | plush | 2 | 2 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed|thin_features_lost | lab_auto_v1 |
| 17_tiny | gummy | 2 | 2 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | — | lab_auto_v1 |
| 17_tiny | clay | 2 | 2 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | — | lab_auto_v1 |
| 17_tiny | plush | 2 | 2 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | — | lab_auto_v1 |
| 18_detailed | gummy | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | lab_auto_v1 |
| 18_detailed | clay | 3 | 3 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 18_detailed | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 19_messy | gummy | 5 | 5 | 4 | 5 | 4 | 4 | 4 | 4 | 5 | — | lab_auto_v1 |
| 19_messy | clay | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 19_messy | plush | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |
| 20_bad | gummy | 3 | 2 | 5 | 4 | 4 | 4 | 4 | 2 | 2 | self_intersect_artifacts | inspected |
| 20_bad | clay | 3 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | silhouette_collapsed | lab_auto_v1 |
| 20_bad | plush | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 5 | — | lab_auto_v1 |

## Per-style mean

### gummy

| dimension | mean |
|---|---|
| silhouette_fidelity | 3.95 |
| recognition | 3.95 |
| quirk_preservation | 4.25 |
| material_quality | 4.60 |
| dimensionality | 3.85 |
| style_consistency | 4.00 |
| small_sticker_legibility | 4.00 |
| delight | 3.95 |
| shareability | 4.35 |

### clay

| dimension | mean |
|---|---|
| silhouette_fidelity | 3.25 |
| recognition | 3.25 |
| quirk_preservation | 4.00 |
| material_quality | 3.30 |
| dimensionality | 3.80 |
| style_consistency | 4.00 |
| small_sticker_legibility | 3.95 |
| delight | 2.95 |
| shareability | 4.10 |

### plush

| dimension | mean |
|---|---|
| silhouette_fidelity | 4.05 |
| recognition | 4.10 |
| quirk_preservation | 4.00 |
| material_quality | 4.00 |
| dimensionality | 4.05 |
| style_consistency | 4.00 |
| small_sticker_legibility | 4.00 |
| delight | 3.10 |
| shareability | 4.55 |

## Failure class frequency

| class | count |
|---|---|
| silhouette_collapsed | 19 |
| thin_features_lost | 14 |
| open_stroke_failed | 6 |
| over_smoothed_identity_loss | 1 |
| legibility_fail_128 | 1 |
| self_intersect_artifacts | 1 |

## Inspected subset notes

- **01_blob / gummy:** Soft inflated coral blob; remesh preserves lumpiness; good glints
- **02_heart / gummy:** Asymmetric heart readable; excellent sticker candidate
- **04_star / gummy:** Wonky points preserved; soft tips; gold candy look
- **04_star / clay:** Matte clay star; flatter specular; solid identity
- **04_star / plush:** Plush remesh softens points more; still a star
- **05_face / gummy:** Head+eyes+smile as separate components; no invented features
- **06_stick / gummy:** Tubes OK at 1024; thin limbs weak as sticker
- **10_open / gummy:** Open arc as tube works; less "emoji" delight
- **12_multi / gummy:** iou_proxy=0.110; coverage=0.0629; mean_rgb=[179.1, 190.1, 163.1]
- **12_multi / plush:** Three blobs stay disconnected — good
- **15_letter / clay:** Letter A as tubes; matte; weak small
- **20_bad / gummy:** Bad polygon still renders; low recognition by design

CSV: `out/metrics/evaluation_scores.csv`
