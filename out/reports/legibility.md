# Legibility Study

**Date:** 2026-09-22 (America/Toronto)
**Representative doodles:** 01_blob, 02_heart, 04_star, 06_stick, 15_letter
**Derivatives:** 1024 master → 512 / 256 / 128 (LANCZOS + pad)

## Coverage table (alpha fraction)

### gummy

| doodle | 1024 | 512 | 256 | 128 |
|---|---:|---:|---:|---:|
| 01_blob | 0.085 | 0.084 | 0.085 | 0.086 |
| 02_heart | 0.081 | 0.081 | 0.081 | 0.082 |
| 04_star | 0.076 | 0.076 | 0.076 | 0.077 |
| 06_stick | 0.027 | 0.027 | 0.027 | 0.028 |
| 15_letter | 0.029 | 0.028 | 0.029 | 0.030 |

### clay

| doodle | 1024 | 512 | 256 | 128 |
|---|---:|---:|---:|---:|
| 01_blob | 0.065 | 0.065 | 0.065 | 0.066 |
| 02_heart | 0.061 | 0.060 | 0.061 | 0.061 |
| 04_star | 0.055 | 0.055 | 0.055 | 0.057 |
| 06_stick | 0.023 | 0.023 | 0.023 | 0.024 |
| 15_letter | 0.029 | 0.029 | 0.029 | 0.030 |

### plush

| doodle | 1024 | 512 | 256 | 128 |
|---|---:|---:|---:|---:|
| 01_blob | 0.092 | 0.092 | 0.092 | 0.093 |
| 02_heart | 0.087 | 0.087 | 0.088 | 0.088 |
| 04_star | 0.083 | 0.083 | 0.083 | 0.084 |
| 06_stick | 0.032 | 0.032 | 0.032 | 0.033 |
| 15_letter | 0.036 | 0.036 | 0.036 | 0.037 |

## Questions

### 1. Does the style stay recognizable at ~128px?
- **Closed thick shapes (blob, heart, star):** Yes for all three styles — color mass + silhouette survive.
- **Stick figure / letter:** Marginal. Limbs and crossbars become hard to parse; recognition drops to “abstract tubes.”

### 2. Where does detail die first?
- Open thin tubes (stick limbs, letter strokes) between **256 → 128**.
- Specular glints (gummy) disappear by 128; material reads as flat candy color.
- Multi-component spacing collapses visually when components are small (face eyes already tiny at 1024 in this corpus).

### 3. Recommended export sizes
| Use | Size | Notes |
|-----|------|-------|
| Hero / share sheet | 1024 | Master RGBA |
| Sticker pack cell | 512 | Best balance |
| Chat preview | 256 | Still OK for closed shapes |
| Emoji tray | 128 | Only if silhouette thick; avoid stick/letter as tray icons without thickening pass |

### 4. Style differences at small size
- **Plush:** Thickest bevel → most forgiving at 128.
- **Gummy:** Color + mass OK; gloss identity lost at 128.
- **Clay:** Stable matte readout; less “wow” but readable.

### 5. Product implication
Ship a **silhouette thicken** pass (or min tube radius bump) before 128 exports for open-stroke doodles. Do not rely on raw procedural tubes for emoji-tray size.
