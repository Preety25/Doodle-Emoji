# Visual Language Spec — Doodle Emoji Stylization Lab

**Principle:** POLISH, DON'T REPLACE. Preserve silhouette, proportions, asymmetry, quirks. Never auto-fix imperfect drawings. Do not invent faces unless the doodle already has them.

**Sources:** Four art-direction references reverse-engineered in `docs/refs/` (do not copy assets; encode traits).

---

## Per-reference analysis

### Ref 1 — Glossy marbled organic blob (`ref1_glossy_blob.png`)
- **Form:** Soft inflated amorphous volume; bean/teardrop asymmetry preserved; no sharp points; large continuous bevel.
- **Material:** Near-zero roughness; mirror-like specular; fluid color bands (marbling as style variable, not identity).
- **Lighting:** High-contrast studio; sharp white glints on curvature peaks; subtle contact shadow optional.
- **Framing:** Centered on white/void BG; sticker-safe padding.
- **Encode as:** High inflation + very low roughness + clearcoat + optional procedural color swirl (style variable).

### Ref 2 — Soft multi-gradient gummy star (`ref2_gummy_star_gradient.png`)
- **Form:** Five-point star with blunt rounded points; nested outer rim + inner face (layered depth); slight ¾ view.
- **Material:** Candy gloss; SSS/transmission at edges; vertical multi-stop gradient (style variable).
- **Lighting:** Soft key + rim; highlights on upper-left rounded edges.
- **Encode as:** Large bevel, moderate extrusion, roughness ~0.05–0.12, SSS weight moderate, optional layer offset (interpretation).

### Ref 3 — Magenta/pink layered gummy star (`ref3_gummy_star_magenta.png`)
- **Form:** Same inflated star language; hot magenta outer + milky pink inner; deep soft valley between layers.
- **Material:** High gloss, milky SSS, sharp clearcoat glints.
- **Encode as:** Confirms gummy defaults (roughness low, clearcoat on, candy SDS colors from stroke or recipe fallback).

### Ref 4 — Kawaii glossy pink heart with face (`ref4_kawaii_heart.png`)
- **Form:** Extremely inflated heart; smooth silhouette; cheeks as separate raised volumes.
- **Material:** Bubblegum pink plastic/gummy; low roughness; edge SSS glow.
- **Face:** Eyes/mouth/cheeks present in *this* reference — treat as **interpretation variable**, NOT a constant. Lab must NOT invent faces for faceless doodles.
- **Encode as:** Geometry inflation + glossy material only; face generation gated off unless doodle strokes include facial marks.

---

## Constants (always apply)

| Constant | Value | Rationale |
|----------|-------|-----------|
| Output master size | 1024×1024 RGBA | Shareable hero |
| Film transparent | true | Sticker compositing |
| Camera FOV | ~35–40° mild perspective | Toy product feel without extreme distortion |
| Framing padding | ~12–18% of frame | Sticker safe margin |
| BG | Transparent void (no ground plane in master) | Shareability |
| Preserve components | Keep disconnected strokes separate | Authorship |
| No auto face invent | Off by default | Polish ≠ reinterpret character |
| No auto symmetry | Off | Quirk preservation |
| Y convention | Canvas Y-down → Blender Y-up flip at normalize | Coordinate contract |
| Renderer (lab) | EEVEE Next (4.2) | Fast transparent stills |

---

## Style variables (per recipe)

Geometry: `extrusion`, `bevel_depth`, `bevel_resolution`, `curve_resolution`, `tube_radius` (open), `remesh`/`smooth` (off or light only).  
Material: `base_color`, `roughness`, `specular`, `metallic`, `clearcoat`, `clearcoat_roughness`, `transmission`, `ior`, `sss_weight`, `sss_radius`, `sss_color`.  
Lighting: key/fill/rim intensities, colors, softness, positions.  
Camera: location, rotation, ortho_scale/lens, padding.

---

## User-owned (must preserve)

- Stroke topology / number of components
- Approximate silhouette & proportions
- Asymmetry and wonky points
- User stroke colors when provided
- Open vs closed classification (after careful close detection)
- Presence/absence of facial marks (do not invent)

---

## Interpretation variables (optional, gated)

- Nested layer / inset face (star-in-star) — **off** in v1 procedural unless recipe `layers.enabled`
- Face features — **only** if doodle contains eye/mouth-like closed regions and recipe allows
- Marbling / candy gradient — style recipe only
- Slight squash/stretch — seed-driven micro variation ≤2% if recipe allows (v1: off)

---

## Implementable numeric defaults

### Gummy.v1
| Param | Default |
|-------|---------|
| extrusion | 0.22 |
| bevel_depth | 0.08 |
| bevel_resolution | 4 |
| curve_resolution_u | 24 |
| tube_radius (open) | 0.045 |
| remesh | false |
| smooth_iters | 0 |
| roughness | 0.08 |
| specular | 0.65 |
| clearcoat | 1.0 |
| clearcoat_roughness | 0.03 |
| transmission | 0.15 |
| ior | 1.4 |
| sss_weight | 0.35 |
| sss_radius | [0.12, 0.06, 0.04] |
| metallic | 0.0 |
| key_energy | 80 |
| fill_energy | 25 |
| rim_energy | 55 |
| camera_pitch_deg | 12 |
| camera_yaw_deg | 18 |
| padding | 0.15 |

### Clay.v1
| Param | Default |
|-------|---------|
| extrusion | 0.18 |
| bevel_depth | 0.055 |
| bevel_resolution | 3 |
| tube_radius | 0.05 |
| remesh | false |
| smooth_iters | 1 (very light) |
| roughness | 0.65 |
| specular | 0.2 |
| clearcoat | 0.0 |
| transmission | 0.0 |
| sss_weight | 0.45 |
| sss_radius | [0.2, 0.1, 0.08] |
| sss_color | warm peach bias |
| key_energy | 55 (softer) |
| fill_energy | 35 |
| rim_energy | 20 |
| camera_pitch_deg | 8 |
| camera_yaw_deg | 10 |
| padding | 0.14 |
| surface_noise | optional tiny bump strength 0.02 |

### Plush.v1
| Param | Default |
|-------|---------|
| extrusion | 0.26 |
| bevel_depth | 0.11 |
| bevel_resolution | 5 |
| tube_radius | 0.06 |
| remesh | false |
| smooth_iters | 0 |
| roughness | 0.85 |
| specular | 0.08 |
| clearcoat | 0.0 |
| transmission | 0.0 |
| sss_weight | 0.7 |
| sss_radius | [0.35, 0.2, 0.15] |
| key_energy | 45 |
| fill_energy | 40 |
| rim_energy | 30 (soft wrap) |
| camera_pitch_deg | 10 |
| camera_yaw_deg | 14 |
| padding | 0.16 |
| silhouette_bias | slightly thicker bevel vs gummy |

---

## Premium / playful / shareable encoding

- **Premium** = clean 3-point lighting + material fidelity (low roughness or honest matte, correct SSS).
- **Playful** = squashy inflated form + candy/pastel colors + soft silhouette.
- **Shareable** = thick readable silhouette at ~128px; high alpha contrast; centered framing.

---

## Batch-2 reference synthesis (`docs/refs/batch2/`)

Additional art-direction refs reverse-engineered 2026-09-22. Do not copy assets; encode traits into style variables / future recipes.

### Per-ref notes

| Ref | Traits to encode | Maps nearest to | Do NOT treat as constant |
|-----|------------------|-----------------|---------------------------|
| `01_matte_ceramic_character_pot` | Strict matte, fine grain, soft diffused light, color-blocked zones, handmade scalloped edges | **Clay.v1** (matte + warm SSS lite) + optional future “ceramic” recipe | Painted face — interpretation variable only |
| `02_gold_foil_balloon_star` | Inflated Mylar, metallic high gloss, perimeter seam/pinch, micro-wrinkles, blunt star tips | Future **foil/balloon** recipe; geometry inflation like Plush/Gummy | Face + blush — interpretation variable |
| `03_yellow_gummy_star` | Hyper-rounded points, bulbous center, satin–soft sheen (not chrome), edge SSS glow, warm AO | **Gummy.v1** (confirm soft glints + SSS; allow satin not only wet-gloss) | Face/blush — gated |
| `04_toy_hands_extruded_icons` | Chunky extrusion, soft chamfers, saturated matte toy plastic, clean icon borders | Extrude+bevel language shared by all heroes; matte finish → Clay / future “toy plastic” | Multi-object scenes are composition refs, not single-doodle obligation |
| `05_matte_tech_voxel_toys` | Soft-touch matte zero-spec, rounded chunky devices + intentional voxel blockiness | Matte path like Clay; voxel = **optional interpretation** (quantize), not default polish | Logos/UI text — out of scope for doodle polish |
| `06_purple_balloon_unicorn` | Segmented sausage balloons, constrictions, high latex gloss, soft translucency at edges | Future **balloon** recipe; segment joins ≈ disconnected components preserved | Unicorn semantics invented from parts — do not invent species features |

### Cross-cutting Batch-2 synthesis

**Geometry spectrum (preserve silhouette always):**
1. **Soft inflated continuous** (gummy/foil stars, ceramic pot body) — large bevel / light remesh+smooth.
2. **Chunky extruded icons** (toy hands set) — solidify + chamfer; flatter top OK.
3. **Segmented balloon** (unicorn) — keep components separate; constrictions = authorship.
4. **Voxel/block** (tech toys) — opt-in quantize; never default (destroys doodle quirk unless user asks).

**Material spectrum:**
| Cluster | Roughness | Spec/Coat | SSS/Transmission | Notes |
|---------|-----------|-----------|------------------|-------|
| Matte ceramic / soft-touch tech | 0.65–0.9 | very low | warm low–mid SSS | Clay.v1 home |
| Toy extruded plastic | 0.45–0.7 | low | low | Between clay & plush |
| Satin gummy | 0.12–0.25 | mid + small glints | mid SSS | Soften Gummy if “wet chrome” too strong |
| Wet gummy / latex balloon | 0.05–0.12 | high clearcoat | mid SSS + slight transmission | Gummy.v1 / future balloon |
| Foil Mylar | roughness ~0.05–0.15 + **metallic ~0.85–1.0** | env reflections | low SSS | New recipe later; poor at 128px if pure chrome |

**Lighting:** Soft studio / high-key remains constant. Matte refs use larger area lights & higher world fill; foil/gummy need sharper key for readable glints. Transparent or clean void BG still preferred for stickers (Batch-2 product shots sometimes use soft gradients — treat gradient as *presentation*, not master asset).

**Faces / character paint:** Batch-2 heavily features faces. Lab rule unchanged: **never invent faces**; only preserve marks present in the doodle.

**Implications for hero recipes (v1 locked for this benchmark):**
- **Gummy.v1** — validated by yellow gummy star + earlier magenta stars; allow satin variant later (`roughness` 0.18).
- **Clay.v1** — validated by ceramic pot + matte toy/tech cluster.
- **Plush.v1** — closest to inflated soft volume of foil/gummy stars but with high SSS / low specular (cuddly, not Mylar).
- **Deferred recipes:** `foil.v1`, `balloon.v1`, `toy_plastic.v1`, `voxel.v1` (opt-in).

**Shareability reminder from Batch-2:** Thick silhouettes and blunt tips win; foil micro-wrinkles and voxel detail are delight-at-1024, liability-at-128.

---

## Batch-3 style variants (`docs/refs/batch3/`)

Added 2026-09-22. These refine the three hero families; they do **not** replace gummy/clay/plush.v1 as the locked benchmark heroes.

| Ref file | Style family | Variant recipe | Encoded traits | EEVEE approximation | Deferred / not v1 |
|----------|--------------|----------------|----------------|---------------------|-------------------|
| `plush_fiber_pile.png` | Plush | `plush_fiber.v1` | Dense short fibers, velvet anisotropy, saturated multi-hue tubes, soft contact shadow | Principled **Sheen** + fine noise bump + high roughness + SSS | True hair/particle fur; anisotropic tangent maps; bake atlas for mobile |
| `clay_claymorph_figure.png` | Clay | `clay_claymorph.v1` | Pillowy primitive limbs, chalky matte, warm soft SSS, oversized mitten hands, pastel set | Higher bevel/smooth, roughness ~0.82, large area lights, low specular | Invented faces/props (only preserve if in doodle); character rigs |
| `gummy_sugar_crust.png` | Gummy | `gummy_sugar.v1` | Translucent jelly cubes, edge glow, white crystalline sanding, slight bevel | Transmission↑ + SSS↑ + **high-frequency bump** (sugar sparkle proxy), mid clearcoat | Real crystal particles / micro-displacement; stacked multi-mesh candy piles |

### Variant constants (still hold)
- Preserve silhouette / asymmetry / open vs closed.
- Transparent void master.
- No invented faces (claymorph ref has a face — **interpretation-gated**).

### When to use which
| Intent | Recipe |
|--------|--------|
| Default candy delight | `gummy.v1` |
| Sanded fruit-jelly / sparkle candy | `gummy_sugar.v1` |
| Handmade matte | `clay.v1` |
| Soft UI / claymorph toy figure | `clay_claymorph.v1` |
| Soft toy volume | `plush.v1` |
| Fuzzy/velvet pile read | `plush_fiber.v1` (preview); true fur = future bake |

### Mobile note
Fiber and sugar microdetail die at 128px. Export thicken + prefer `plush.v1` / `gummy.v1` for tray; use fiber/sugar for 512–1024 share sheets.
