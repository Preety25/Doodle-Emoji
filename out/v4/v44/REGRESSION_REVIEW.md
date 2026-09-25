# V4.4 Regression Review — Semantic Parsing Pack (5 × 4)

**Pack:** 19/20 API successes (u08/glossy blocked by xAI spend limit / shape fallback).  
**Cost (approx):** **~$1.14** for 19 successful cells @ ~$0.06 each (1k/low, 2 input images).  
**Contact sheet:** `out/v4/v44/contact_sheet.png`  
**Semantic lock:** recognition enriched under `out/v4/v42/unseen/recognition/` (u06 corrected to mug+interior zigzag).

Legend: **Y** = yes / pass · **N** = no / fail · **P** = partial · **—** = N/A (missing output)

Acceptance questions A–L are defined in `SEMANTIC_PARSING.md`.

---

## Special attentions (headline)

| Check | Result | Notes |
|---|---|---|
| **u06 zigzag = interior surface mark ON mug** | **PASS** (all 4 styles) | Zigzag embossed/embedded/stitched/inset on mug body — not a floating green ribbon |
| **u07/clay stays hat-person (not flower)** | **FAIL** | Clay output still reads as personified flower / blossom; sheet identity bleed persists |
| **u03/glossy solid polished volumetric** | **PASS** | Opaque brown/tan resin head with clearcoat; not gray wire / extruded outline |
| **u01/plush no invented face** | **PASS** | Fuzzy orange mug + steam only; no eyes/mouth/blush |
| **u08/glossy no RGB sheet palette** | **N/A (API miss)** | Cell missing — credits exhausted on attempt 20 (see FAILURE_REPORT) |

---

## Per-cell A–L matrix

### u01 — mug / cup with steam (`faces_observed=false`)

| Style | A id | B parts | C interior | D opens | E broken | F faces | G color | H style | I glossy-solid | J sheet-mat | K forbid | L lock |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gummy | Y | Y | — | Y steam open | Y | Y no face | Y | Y jelly | — | Y | Y | Y |
| clay | Y | Y | — | Y | Y | Y | Y | Y matte | — | Y | Y | Y |
| plush | Y | Y | — | Y | Y | **Y** | Y | Y fuzz | — | Y | Y | Y |
| glossy | Y | Y | — | Y | Y | Y | Y | Y resin | Y solid | Y | Y | Y |

Notes: V4.3 plush face invention **fixed**. Steam stays open wisps. Liquid invent mild (OK under elastic fidelity).

### u03 — character head / face with bangs (`faces_observed=true`)

| Style | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gummy | Y | Y | Y bangs on head | Y smile open | Y | Y eyes+mouth | Y | Y | — | Y | Y | Y |
| clay | Y | Y | Y | Y | Y | Y | Y | Y | — | Y | Y | Y |
| plush | Y | Y | Y | Y | Y | Y | Y | Y | — | Y | Y | Y |
| glossy | Y | Y | Y | Y | Y | Y | Y | Y | **Y solid** | Y | Y | Y |

Notes: V4.3 glossy gray-wire failure **fixed** — solid clearcoat head.

### u06 — mug + interior green zigzag (`faces_observed=false`) — **V4.2 hypothesis corrected**

| Style | A | B | C zigzag | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gummy | Y mug | Y | **Y embedded** | Y | Y | Y no face | Y green kept | Y | — | Y | Y | Y |
| clay | Y | Y | **Y painted/embossed** | Y | Y | Y | Y | Y | — | Y | Y | Y |
| plush | Y | Y | **Y stitch/applique** | Y | Y | Y | Y | Y | — | Y | Y | Y |
| glossy | Y | Y | **Y molded/inset** | Y | Y | Y | Y | Y | Y | Y | Y | Y |

Notes: Semantic lock flip (zigzag→mug+mark) is the main V4.4 win. All styles keep green family on the mark.

### u07 — hat-person (`faces_observed=true`, identity lock vs flower)

| Style | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gummy | **P** hat↔flower | Y | — | — | Y | Y marks | Y | Y | — | **P** | P | P |
| clay | **N flower** | Y | — | — | Y | Y | Y | Y clay | — | **N** subject bleed | N | **N** |
| plush | **Y hat-person** | Y | — | — | Y | Y | Y | Y | — | Y | Y | Y |
| glossy | **P** hat↔flower | Y | — | — | Y | Y | Y red mono | Y | Y | P | P | P |

Notes: Ambiguous doodle (petal-like brim). Plush reads clearest as hat-person. Clay collapses to flower (same failure mode as V4.3). Gummy/glossy sit in between — wide brim present but plant reading remains available.

### u08 — three-pronged plant (`faces_observed=false`)

| Style | A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gummy | Y | Y 3 tops | — | — | Y | Y no face | Y green mono | Y | — | Y | Y | Y |
| clay | Y | Y | — | — | Y | Y | Y green | Y | — | Y | Y | Y |
| plush | Y | Y | — | — | Y | Y | Y green | Y | — | Y | Y | Y |
| glossy | — | — | — | — | — | — | — | — | — | — | — | — |

Notes: Coherent green family on gummy/clay/plush (good color lock rehearsal for the missing glossy cell). Glossy cell not generated.

---

## Cross-pack style separation

| Style | Signature read | Separable? |
|---|---|---|
| Gummy | Translucent gelatin, bubbles, wet highlights | Yes |
| Clay | Matte polymer, soft diffuse | Yes vs gummy/glossy |
| Plush | Short-pile fuzz | Yes when fuzz lands (strong on u01/u06/u07) |
| Glossy | Solid opaque clearcoat | Yes on generated cells (u03 fixed) |

---

## Semantic-lock integrity

Same recognition JSON fed all styles per doodle. u06 hypothesis corrected in-place under `out/v4/v42/unseen/recognition/u06_recognition.json`. Per-cell `semantic.json` / `stroke_roles.json` mirror the lock.

---

## Verdict

V4.4 semantic layer **materially improves** the V4.3 failure modes it targeted:

- u06 zigzag role → **fixed**  
- u01/plush face → **fixed**  
- u03/glossy wire → **fixed**  
- u07/clay identity → **still failing** (hardest; doodle is flower-ambiguous + clay sheet has flowers)  
- u08/glossy palette → **untested** (API credits)

Recommend next pass: stronger negative visual language for u07 (explicit “NOT a flower / NOT petals / limbs are arms not leaves”) and/or a clay sheet without flower subjects — still semantic-first, not more style refs of random objects.
