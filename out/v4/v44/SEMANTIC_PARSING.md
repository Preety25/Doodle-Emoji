# V4.4 — Semantic Parsing + Style Guardrails

**Branch:** `stylization/v4-ai-rendering`  
**Regression pack:** exactly 20 gens — u01, u03, u06, u07, u08 × gummy, clay, plush, glossy  
**North star:** Draw something messy → we understand what you meant → make *your* version beautiful.

V4.3 showed styles work but exposed **semantic failures** (interior mark → floating ribbon, clay-sheet flower bleed on hat-person, glossy gray wire head, invented plush faces, glossy rainbow palette import). V4.4 fixes this with a **stronger semantic parsing layer before styling** — not primarily more visual refs.

---

## Priority hierarchy (binding)

Lower never overrides higher:

1. **Original doodle** — visual source of truth  
2. **Stroke-role analysis** — what each stroke *does*  
3. **Semantic recognition** — locked identity (once per doodle)  
4. **Transform rules** — close broken contours, embed interior marks, keep opens open  
5. **Style reference** — material / lighting / surface / dimensionality / personality ONLY  
6. **Generative creativity** — delight within the above bounds  

---

## Stroke roles (A–G)

Every meaningful stroke/group gets exactly one role:

| Code | Role | Meaning |
|---|---|---|
| **A** | Boundary / silhouette | Outer structural contour of a region/object |
| **B** | Interior surface mark | Stroke substantially inside a recognized region |
| **C** | Attachment / connector | Handle, branch, limb join, etc. |
| **D** | Meaningful open stroke | Steam, string, whisker, tail, hair, smile, antenna, spiral, gesture |
| **E** | Broken structural contour | Near-closed structural gap (finger-draw miss) |
| **F** | Independent component | Separate part (eye disk, canopy sphere, etc.) |
| **G** | Ambiguous | Needs conservative handling |

### Role rules

**INTERIOR MARK (B):**  
Stroke substantially inside a recognized region → **surface mark**. Inherits parent material:

- gummy → embedded / translucent inlay  
- clay → painted or embossed  
- plush → stitch / applique  
- glossy → molded-in or inset  

**NEVER** a floating standalone ribbon (esp. **u06** green zigzag inside mug).

**BROKEN CONTOUR (E):**  
Close + smooth when endpoints are close, directions align, same contour, and closure is coherent. Do not leave finger-draw gaps as intentional openings.

**OPEN STROKE (D):**  
Do **NOT** auto-close steam / string / whisker / tail / hair / smile / antenna / spiral / gesture.

---

## Semantic lock

- Recognize each doodle **ONCE**.  
- Same semantic identity feeds all 4 styles.  
- Recognition lives under `out/v4/v42/unseen/recognition/` (enriched in place with stroke-role fields for the 5 test doodles).  
- Per-cell copies: `out/v4/v44/uXX/{style}/semantic.json` + `stroke_roles.json`.

### V4.2 → V4.4 correction (critical)

| ID | V4.2 hypothesis | V4.4 locked hypothesis |
|---|---|---|
| u01 | mug / cup with steam | mug / cup with steam *(+ explicit no-face)* |
| u03 | character head / face with bangs | character head / face with bangs *(+ glossy solid volume)* |
| **u06** | ~~zigzag line / grassy squiggle~~ | **mug / cup with steam and interior green zigzag surface mark** |
| u07 | person with wide-brim hat | person with wide-brim / floppy hat (**identity lock vs flower**) |
| u08 | three-pronged plant | three-pronged plant *(+ no RGB sheet palette)* |

---

## Style sheets teach ONLY

Form language · material · lighting · surface · dimensionality · personality of the **finish**.

**NEVER:** subject identity · component count · pose · faces · palette assignment · decorative objects.

Prompt anti-copy line (binding):

> Style sheet is MATERIAL ONLY; do not copy any subject/object/colors from the reference sheet.

Canonical sheets:

- `docs/refs/style_sheets/sheet_gummy.png`
- `docs/refs/style_sheets/sheet_clay.png`
- `docs/refs/style_sheets/sheet_plush.png`
- `docs/refs/style_sheets/sheet_glossy.png`

---

## Face guardrail (semantic, not style)

Invent eyes / mouth / cheeks / blush **ONLY if the doodle has them**.

- `faces_observed: false` → hard ban (u01, u06, u08)  
- `faces_observed: true` → preserve observed marks only (u03, u07); no extra blush unless drawn  

---

## Color lock

- Preserve the user’s **important color relationships**.  
- Enriching saturation / depth is OK.  
- Do **NOT** import style-sheet palettes (no rainbow from glossy sheet).  
- When doodle has a color mark (u06 green zigzag), keep that family on the corresponding surface mark.

---

## Glossy HARD RULE

Always fully reconstruct as a **SOLID opaque polished resin/vinyl object**.

Pipeline: **fill closed regions → volumetric → clearcoat**.

**NEVER:** wireframe / outline / line sculpture / gray extruded line / hollow contour / tube drawing.

Especially binding for **u03/glossy**.

---

## Elastic fidelity

Improve execution aggressively; preserve intent conservatively.

| Push hard | Do not |
|---|---|
| Smooth contours, proportions, alignment | Replace with generic category object |
| Close broken structural gaps | Invent unsupported parts / faces |
| Dimensional / plump / toy-like | Change identity or component count |
| Material delight | Copy sheet subjects / palettes |
| Embed interior marks into parent material | Float interior marks as independent objects |

---

## Acceptance questions (A–L)

Answer **per cell** (doodle × style) in `REGRESSION_REVIEW.md`.

| # | Question |
|---|---|
| **A** | Is the locked `subject_hypothesis` still the subject (no identity swap)? |
| **B** | Is component count / topology preserved (no extra/missing major parts)? |
| **C** | Are interior surface marks (role B) embedded on the parent — not floating ribbons? |
| **D** | Are meaningful open strokes (role D) left open (not auto-closed)? |
| **E** | Are broken structural contours (role E) closed/smoothed appropriately? |
| **F** | Faces: invented only if `faces_observed`? (no invented face when false) |
| **G** | Color relationships preserved? No style-sheet palette import? |
| **H** | Style signature correct and separable (gummy/clay/plush/glossy)? |
| **I** | Glossy cells: solid opaque volumetric clearcoat (not wire/outline/tube)? |
| **J** | Style sheet used as material only (no subject/pose/face/object copy)? |
| **K** | Forbidden additions absent (per recognition hard bans)? |
| **L** | Same semantic identity as the other 3 styles for this doodle (semantic lock)? |

### Special attentions (must call out)

1. **u06 zigzag** → interior surface mark ON mug, not independent green ribbon  
2. **u07/clay** → MUST stay hat-person (clay sheet must not change identity to flower)  
3. **u03/glossy** → MUST solid polished volumetric head — no gray wire  
4. **u01/plush** → MUST NOT invent face  
5. **u08/glossy** → MUST NOT import RGB/multicolor sheet palette  

---

## Implementation map

| Piece | Path |
|---|---|
| Stroke roles | `lab/v4/stroke_roles.py` |
| Semantic lock | `lab/v4/semantic_lock.py` |
| Prompts | `lab/v4/generative/prompts.py` → `build_v44_semantic_prompt` |
| Runner | `lab/v4/v44_semantic_regression.py` |
| CLI | `scripts/v4_v44_semantic_regression.py` |
| Outputs | `out/v4/v44/` |

API: xAI edits `grok-imagine-image-2.0`, resolution `1k`, quality `low`, `n=1`.  
`images[]` = doodle + matching style sheet.

---

## What this pass does / does not do

**Does:** stronger parsing, stroke roles, face/color/glossy guardrails, 20-cell regression, reviews.  
**Does not:** modify V1/V2/V3/main; open a PR; re-run the full 40-cell V4.3 pack; add extra gens beyond 20.
