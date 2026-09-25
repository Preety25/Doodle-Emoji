# V4.4 Failure Report

Pack status: **19/20** API successes (`edited.png` present).  
Approx cost: **~$1.14** (19 × ~$0.06). Expected band for 20 ≈ **$1.20**.

This report lists **API** failures and remaining **quality** failures (semantic / identity / style).

---

## API / infra

### 1. `u08/glossy` — missing output (attempt 20/20)

- **HTTP:** first attempt `403` — team credits / monthly spending limit exhausted  
- **Fallback attempt:** `422` — `image[0]: invalid type: map, expected a string` (alternate request shape; expected when primary shape is rejected for non-shape reasons)  
- **Impact:** cannot evaluate u08 glossy palette lock this pack  
- **Policy:** STOP after 20 gens — **no retry** (would be gen 21)  
- Artifacts present: `prompt.txt`, `semantic.json`, `stroke_roles.json`, `metadata.json`, `source_doodle.png` — no `edited.png`

---

## Critical / high (quality)

### 2. Identity collapse — `u07/clay`

- **Type:** semantic / identity / style-sheet bleed  
- **Expected:** person with wide-brim / floppy hat (locked recognition)  
- **Got:** personified flower / blossom reading (petal loops + stem + leaf-arms)  
- **Why hard:** doodle topology is flower-ambiguous; `sheet_clay.png` contains an explicit flower subject  
- **Impact:** same critical failure mode as V4.3 u07/clay — semantic lock text was not enough against clay sheet subject language  
- **Next:** stronger identity negatives in prompt (“NOT a flower, NOT petals, arms not leaves”) and/or clay sheet without flower subjects (still prefer semantic fix over more refs)

### 3. Partial identity ambiguity — `u07/gummy`, `u07/glossy`

- **Type:** semantic (mild)  
- Wide brim present but plant/flower reading remains available  
- Plush is the clearest hat-person of the four  

---

## Medium / watchlist

### 4. `u08/glossy` palette lock — untested

- Sibling styles (gummy/clay/plush) stayed coherent green — good sign  
- Cannot claim pass/fail on RGB sheet-palette import until a glossy gen lands  

### 5. Background void

- Many outputs white or black void instead of true alpha — allowed for R&D  

### 6. Mild liquid invent on mugs

- Some mug cells invent visible liquid surface — acceptable under elastic fidelity; not a forbidden addition in recognition  

---

## Fixed vs V4.3 (do not regress)

| V4.3 failure | V4.4 status |
|---|---|
| u06 treated as standalone zigzag ribbon | **Fixed** — mug + interior green surface mark, all 4 styles |
| u01/plush invented kawaii face | **Fixed** — no face |
| u03/glossy gray wire sculpture | **Fixed** — solid clearcoat volumetric head |
| u07/clay → flower | **Still failing** |
| u08/glossy RGB tops | **Untested** (API miss) |

---

## Non-failures

- HTTP success on cells 1–19: **19**  
- Semantic lock files written for all 5 doodles  
- Stroke-role fields present on all cells  
- V1/V2/V3/main not modified (verify at commit)  

---

## Stop rule

Exactly **20** generation attempts were made. No extra gens. No full 40 re-run.
