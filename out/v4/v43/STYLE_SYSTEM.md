# V4.3 Multi-Style Doodle Transform System

**North star:** "Draw something messy. We understand what you meant and make *your* version beautiful."

**Branch tip (docs authored against):** `stylization/v4-ai-rendering`  
**Canonical style sheets:**
- `docs/refs/style_sheets/sheet_clay.png`
- `docs/refs/style_sheets/sheet_gummy.png` (symlinked as `sheet_gummy_a/b`)
- `docs/refs/style_sheets/sheet_plush.png`
- `docs/refs/style_sheets/sheet_glossy.png`

**Semantics source:** `out/v4/v42/unseen/recognition/uXX_recognition.json` (reuse; do **not** re-interpret per style)

---

## Shared family (all styles)

Every output is a **premium stylized 3D sticker / designer toy / soft sculpture / candy illustration**:

- Dimensional, plump, charming — soft volume and material richness
- Isolated subject on transparent (or empty void) background
- No scene, floor, ground plane, drop shadow, environment, or text
- **NOT** photoreal food/product photography
- **NOT** mechanical CAD extrusion / flat 2.5D bevel slab
- **NOT** a generic category replacement for the user's doodle

**Semantics = WHAT** (identity, silhouette, parts, quirks from recognition + doodle).  
**Style = HOW** (material, surface, lighting language).  
**Style sheets = visual language ONLY** — never copy sheet objects, poses, faces, or silhouettes.

---

## Elastic fidelity

Improve execution aggressively; preserve idea conservatively.

| OK (push hard) | NOT OK |
|---|---|
| Smooth contours; improve symmetry/proportion/alignment/spacing/curvature | Replace with a generic category object |
| Clean noise / wobble; close tiny gaps | Invent major unsupported parts (extra fins/windows/limbs/faces/accessories) |
| Make dimensional / plump / toy-like | Change identity or component count |
| Material delight (highlights, fuzz, translucency, clearcoat) | Copy style-sheet subjects |
| Soften junctions; round forms within observed topology | Add scenery, text, logos, second subjects |

Recognition fields are binding for all four styles:

- `subject_hypothesis` + `observed_components` → must preserve
- `inferred_components` → volume/material hints only (not invent permission)
- `allowed_completion` → tight cleanup only
- `forbidden_additions` → hard bans

---

## Style definitions

### 1. Gummy (`gummy`)

**Look:** Juicy soft inflated translucent gelatin; internal color depth; suspended micro-bubbles; wet rounded highlights; luminous edges.

**Refs (primary):**  
`docs/refs/style_sheets/sheet_gummy.png` (also available as symlinks `sheet_gummy_a.png` / `sheet_gummy_b.png` → same file).  
Older jelly object refs (`docs/refs/jelly_gummy/*`) are secondary / optional for gummy only.

**Not:** glass/acrylic, photoreal food, hard opaque resin, clay, plush.

### 2. Clay (`clay`)

**Look:** Soft-sculpted matte polymer clay; puffy handmade; subtle surface variation; restrained warm diffuse highlights.

**Refs:** `docs/refs/style_sheets/sheet_clay.png`

**Not:** translucent gummy, dirty/crumbly earth clay photo, ceramic glaze photo, plush fuzz, clearcoat plastic.

### 3. Plush (`plush`)

**Look:** Stuffed fuzzy short-pile soft toy; visible nap/fuzz; soft compression; cozy fabric feel. Subtle seams only if natural.

**Refs:** `docs/refs/style_sheets/sheet_plush.png`

**Not:** smooth clay, glossy plastic, translucent jelly, hard vinyl.

### 4. Glossy (`glossy`)

**Look:** Solid (not deeply translucent) polished resin / lacquered vinyl / hard-candy toy; rich saturated color; crisp clearcoat speculars.

**Refs:** `docs/refs/style_sheets/sheet_glossy.png` (canonical glossy sheet — solid polished resin/vinyl/hard-candy with sharp speculars; **NOT** translucent gummy).  
Pass **doodle + sheet_glossy.png** (same multi-image pattern as clay/plush).

**Not:** translucent gummy/jelly, metal/glass/ceramic product photo, matte clay, fuzzy plush.

---

## Differentiation test (must pass visually)

Given the same doodle × recognition, the four outputs must be separable at a glance:

| Cue | Gummy | Clay | Plush | Glossy |
|---|---|---|---|---|
| Surface | Translucent gelatin, bubbles | Matte soft clay | Visible short-pile fuzz | Opaque clearcoat shine |
| Highlights | Wet rounded candy | Soft diffuse restrained | Soft fabric roll-off | Crisp specular clearcoat |
| Edge feel | Luminous soft rim | Soft sculpted lip | Fuzzy silhouette fringe | Hard polished rim |
| Volume | Inflated jelly | Puffy handmade clay | Stuffed compression | Hard-toy plump resin |

If two styles look interchangeable (e.g. clay≈plush, or glossy≈gummy), that is a **style-separation failure**.

---

## Prompt / API contract (v4.3 runner)

- Model: `grok-imagine-image-2.0`, resolution `1k`, quality `low`, `n=1`
- Adapter: `lab/v4/generative/xai_edit.py` (`images[]` preferred)
- Recognition loaded **once** per doodle; same semantics for all styles
- Image plans:
  - **gummy:** doodle + `sheet_gummy.png`
  - **clay:** doodle + `sheet_clay.png`
  - **plush:** doodle + `sheet_plush.png`
  - **glossy:** doodle + `sheet_glossy.png`

Background: prefer transparent; white/black void acceptable for R&D (note in metadata).

Stop at exactly 40 generations (10 doodles × 4 styles). No retries except recoverable API shape errors handled inside the adapter.
