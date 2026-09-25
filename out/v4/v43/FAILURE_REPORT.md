# V4.3 Failure Report

Pack status: **40/40** API successes (edited.png present).  
This report lists **quality** failures (semantic / identity / style / render / artifact / style-separation), not HTTP failures.

Approx cost (final pack metadata sum): **~$2.45**.  
Including 4 discarded early doodle-only glossy gens: **~$2.65**.  
(Expected band ~$2.80.)

---

## Critical / high

### 1. Identity collapse — `u07/clay`
- **Type:** semantic / identity / style-sheet bleed
- **Expected:** person with wide-brim hat (recognition)
- **Got:** flower on stem (clay-sheet subject language won over doodle+text)
- **Impact:** breaks north star for this cell

### 2. Style under-transform — `u03/glossy`
- **Type:** style fidelity / render
- **Expected:** solid polished resin/vinyl head with clearcoat speculars
- **Got:** gray extruded “wire doodle” / line sculpture; barely glossy-toy
- **Impact:** fails glossy definition; weak style separation vs others on this row

### 3. Forbidden face invention — `u01/plush`
- **Type:** semantic / identity (forbidden addition)
- **Expected:** mug + steam only (no face on mug)
- **Got:** kawaii face + blush on plush mug
- **Impact:** delight overrode elastic fidelity / forbidden list

---

## Medium

### 4. Style-sheet palette / object bleed (glossy)
- **Cells:** `u02/glossy` (rainbow petals), `u08/glossy` (RGB sphere tops), `u07/glossy` (primary toy colors)
- **Type:** style fidelity / mild identity tint
- **Note:** topology often OK; color/part language from `sheet_glossy` leaks into subject

### 5. Plush face / feature creep (watchlist)
- **Cells:** possible soft-toy faces on subjects that already have faces (OK) vs inventing on objects (not OK)
- **u01/plush** confirmed; spot-check other non-face subjects in future packs

### 6. Clay ↔ plush proximity
- **Type:** style-separation (mild)
- When plush fuzz is subtle, clay and plush can read similarly matte-soft
- Counterexamples (u05/u10 plush) show good fuzz when it lands

---

## Low / R&D notes

### 7. Background void
- Many outputs white or black void instead of true alpha — allowed for R&D; noted in metadata policy

### 8. Early glossy path (corrected)
- u01–u04 glossy first ran **doodle-only**; re-run with `sheet_glossy.png`
- Final pack glossy cells all reference `sheet_glossy`

### 9. Gummy dual-ref on early cells
- u01–u05 gummy used `sheet_gummy_a` + `sheet_gummy_b` (symlinks → same `sheet_gummy.png`)
- Later cells use single `sheet_gummy.png` — functionally fine, slightly higher input cost on early five

---

## Style-separation failures (explicit)
| Pair | Issue | Cells |
|---|---|---|
| glossy vs “line art” | under-transform | u03/glossy |
| clay vs recognition subject | wrong object | u07/clay |
| plush inventing faces | not separation but fidelity | u01/plush |

No systematic gummy↔glossy jelly bleed observed after glossy sheet fix.

---

## Non-failures (API)
- HTTP failures: **0**
- Missing edited.png: **0**
- V3 tip untouched check: run at commit time
