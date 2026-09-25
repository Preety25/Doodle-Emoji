# V4.3 Transform Review — Multi-Style Pack (10 × 4)

**North star:** Draw something messy → we understand what you meant → make *your* version beautiful.  
**Pack:** 40/40 successful API gens. Glossy uses `sheet_glossy.png` (4 early doodle-only glossies re-run).  
**Contact sheets:** `contact_all.png`, `contact_gummy.png`, `contact_clay.png`, `contact_plush.png`, `contact_glossy.png`.

Legend: notes are qualitative (not a single score). Styles should be separable at a glance.

---

## Cross-pack style separation (summary)

| Style | Signature read | Separable? |
|---|---|---|
| **Gummy** | Translucent gelatin, internal bubbles, wet rounded highlights, luminous edges | Yes — strongest material signature |
| **Clay** | Opaque matte polymer, soft diffuse light, handmade puff | Yes vs gummy/glossy; closest to plush when fuzz is weak |
| **Plush** | Short-pile fuzz / flock, soft compression, fabric nap | Yes when fuzz reads; occasional face invention hurts fidelity |
| **Glossy** | Solid opaque resin/vinyl, crisp clearcoat speculars | Yes when fully transformed; fails when left as extruded line-art |

**Verdict:** Styles are **visually separable** on most cells. Main confusion risks: clay↔plush (matte soft), glossy↔gummy (if translucency leaks — mostly avoided after sheet_glossy fix).

---

## Per-doodle × style notes

### u01 — mug / cup with steam
| Style | Recognition | Intent | Identity | Structure | Signature features | Stylized dim | Polish | Delight | Style fidelity | Style separation | Edges | Artifacts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gummy | mug+steam clear | polish doodle | held | handle R, 3 wisps | steam as jelly ribbons | plump inflated | high | high (bubbles) | strong jelly | distinct | clean soft | none serious |
| clay | mug+steam | polish | held | rim/handle/steam | matte orange body | chunky toy | high | medium | strong matte clay | distinct from gummy | soft sculpted | liquid invent OK-ish |
| plush | mug | polish→toy | **face invented** | handle+steam kept | flock texture | stuffed volume | high | high but wrong | strong plush | distinct | fuzzy | **forbidden face/blush** |
| glossy | mug+steam | polish | held | 3 solid steam forms | crisp speculars, opaque | hard-toy plump | high | high | strong resin | distinct | hard polished | none |

### u02 — flower on stem, two leaves
| Style | Notes |
|---|---|
| gummy | Identity OK; juicy translucent petals; good dim; bubbles; separable. |
| clay | Matte petals/stem; handmade; good structure; may simplify speckles. |
| plush | Excellent fuzz + soft seams; center dots preserved as soft studs; high delight; separable. |
| glossy | Multicolor hard-candy petals (sheet color language bleed); solid opaque; sharp speculars; identity OK. |

### u03 — character head / face with bangs
| Style | Notes |
|---|---|
| gummy | Head+bangs readable; translucent orange; bubbles; face grooves; strong gummy. |
| clay | Soft matte head; bang zigzag softened; identity OK. |
| plush | Fuzz present; face soft-toy; watch extra ear invent. |
| glossy | **WEAK:** reads as extruded gray wire doodle, not solid clearcoat resin. Identity preserved; **style fidelity failure**. |

### u04 — flying saucer / UFO
| Style | Notes |
|---|---|
| gummy | Disc+dome+antennas; jelly glow; good. |
| clay | Matte gray saucer; volume OK; restrained highlights. |
| plush | Fabric UFO; seams; cozy; separable. |
| glossy | Chrome/resin saucer + blue accents; sharp speculars; strong glossy; slight metal-photo risk but still toy. |

### u05 — upright mouse / rodent
| Style | Notes |
|---|---|
| gummy | Full body+tail+whiskers; translucent; good dim. |
| clay | Matte tan rodent; parts preserved; soft sculpt. |
| plush | Fuzzy flock; whiskers as cord; eyes/muzzle kept; strong plush; good separation from clay. |
| glossy | Opaque polished tan toy; crisp highlights; identity OK. |

### u06 — zigzag / grassy squiggle (green)
| Style | Notes |
|---|---|
| gummy | Green tubular jelly zigzag; bubbles; **did not** become snake/dragon; low-conf rule held. |
| clay | Matte green ribbon; path preserved. |
| plush | Fuzzy green tube; still a squiggle not a creature. |
| glossy | Solid green polished tube; sharp highlights; opaque. |

### u07 — person with wide-brim hat
| Style | Notes |
|---|---|
| gummy | Hat person as jelly figure; identity OK; face simplified. |
| clay | **FAILURE:** output is a **flower**, not hat-person — likely clay-sheet subject bleed / identity collapse. |
| plush | Hat figure as soft toy (when present); check limbs vs doodle. |
| glossy | Primary-color hard toy figure + yellow brim hat; solid glossy; good separation; colors invented. |

### u08 — three-pronged plant / sapling
| Style | Notes |
|---|---|
| gummy | Three round tops + stem; jelly; good. |
| clay | Matte green plant; three tops; OK. |
| plush | Soft fuzzy canopies; separable. |
| glossy | RGB sphere tops on green stand — **style-sheet palette bleed** but topology matches; strong glossy finish. |

### u09 — UFO (purple)
| Style | Notes |
|---|---|
| all | Purple family preserved across styles; gummy translucent purple vs clay matte vs plush fuzz vs glossy hard purple resin — **excellent separation demo**. |

### u10 — mouse (pink)
| Style | Notes |
|---|---|
| all | Pink family held; structure (ears, whiskers, tail) generally kept; styles separable; plush fuzz vs glossy hard pink resin clear. |

---

## What worked
- Elastic fidelity on low-confidence u06 (stayed a green zigzag).
- Gummy translucency + bubbles consistently different from glossy opacity.
- Color-family preservation on u06/u09/u10.
- Glossy after `sheet_glossy` fix mostly solid resin (not jelly bleed).
- Stylized dimensionality (toy/sticker) dominant over photoreal.

## What hurt
- Plush sometimes **invents faces** (u01) — delight over fidelity.
- Clay **u07 identity collapse** to flower (sheet object bleed).
- Glossy **u03 under-transform** (line extrusion).
- Glossy multicolor invent (u02/u08) from sheet language.
- Backgrounds often white/black void (OK for R&D per policy).
