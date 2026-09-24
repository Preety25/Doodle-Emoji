# Doodle Emoji — Stylization Lab POC

**Principle:** POLISH, DON'T REPLACE.  
**transformation_version:** `tx.v1.0.0`  
**Blender pin:** **4.2.9 LTS** (`BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender`)

Canonical doodle = stroke JSON. PNG renders are derived, reproducible from doodle + style recipe + versions + seed.

## Install Blender (already done on this box)

```bash
# Official LTS tarball extracted to:
#   /workspace/tools/blender/blender-4.2.9-linux-x64/
export BLENDER_BIN=/workspace/tools/blender/blender-4.2.9-linux-x64/blender
export PATH="/workspace/bin:$PATH"
# Headless EEVEE needs EGL + a virtual display:
#   sudo apt-get install -y libegl1 xvfb
$BLENDER_BIN --version
```

## One job (doodle × style)

```bash
cd /workspace/stylization-lab
xvfb-run -a $BLENDER_BIN --background --python scripts/run_job.py -- \
  --doodle corpus/doodles/04_star.json \
  --style gummy --style-version v1 --seed 1 \
  --out out/renders/04_star__gummy__v1__s1.png \
  --doodle-id 04_star
```

Outputs: 1024×1024 RGBA PNG + sidecar `.json` metadata.

## Full benchmark (20 × 3 = 60)

```bash
cd /workspace/stylization-lab
python3 scripts/run_benchmark.py
# then (if not auto-run):
python3 scripts/make_contact_sheets.py
python3 scripts/evaluate.py
python3 scripts/make_legibility_report.py
python3 scripts/ai_compare.py
```

Artifacts:
- `out/renders/{doodle}__{style}__v{ver}__s{seed}.png`
- `out/derivatives/..._{512,256,128}.png`
- `out/metrics/benchmark.csv`
- `out/contact_sheets/`
- `out/reports/` (evaluation, legibility, ai_compare, VISUAL_DECISION_REPORT)

## Regenerate corpus

```bash
python3 scripts/generate_corpus.py
```

## Styles

| style_id | recipe |
|----------|--------|
| gummy | `recipes/gummy.v1.json` |
| clay | `recipes/clay.v1.json` |
| plush | `recipes/plush.v1.json` |

## Package layout

See `docs/VERSION.md`, `docs/visual_language.md`, `docs/Product_v2.md`.

## Style variants (Batch-3)

| Recipe | Parent | Look |
|--------|--------|------|
| `gummy_sugar.v1` | gummy | Sugar-crusted translucent jelly |
| `clay_claymorph.v1` | clay | Pillowy chalky claymorph |
| `plush_fiber.v1` | plush | Velvet/fiber-pile approximation |

```bash
xvfb-run -a $BLENDER_BIN --background --python scripts/run_job.py -- \
  --doodle corpus/doodles/04_star.json \
  --style gummy_sugar --style-version v1 --seed 1 \
  --out out/renders_variants/04_star__gummy_sugar__v1__s1.png \
  --doodle-id 04_star
```

Refs: `docs/refs/batch3/`. Notes: `docs/visual_language.md` (Batch-3 section).
