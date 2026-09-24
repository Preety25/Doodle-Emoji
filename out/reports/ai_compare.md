# AI Compare Report

**Status:** BLOCKED_NO_API

## Env vars checked

- `OPENAI_API_KEY`: missing
- `GEMINI_API_KEY`: missing
- `GOOGLE_API_KEY`: missing
- `REPLICATE_API_TOKEN`: missing
- `ANTHROPIC_API_KEY`: missing

## Required to unblock real AI path

Set one of: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `REPLICATE_API_TOKEN` (and install matching SDK).

Preferred prompt stem:

> POLISH DON'T REPLACE / keep proportions and asymmetry / transparent BG / gummy|clay|plush style / do not invent faces

## Paths

- Source rasters + stubs: `/workspace/stylization-lab/out/derivatives/ai_compare`
- Results JSON: `/workspace/stylization-lab/out/derivatives/ai_compare/results.json`

## Design for Hybrid (C)

1. Run procedural Blender master (A) for silhouette + alpha.
2. Condition AI on source raster with POLISH DON'T REPLACE prompt.
3. Composite: AI RGB × procedural alpha (hard constraint). Optional: reject if IoU(alpha_AI, alpha_A) < threshold.

## What was produced this run

- A = procedural renders (benchmark).
- B = **blocked** (no API key).
- C = **pseudo-hybrid stubs** only (Pillow unsharp/contrast), clearly labeled NOT real AI.

**Recommendation to parent:** provision `OPENAI_API_KEY` (or Gemini/Replicate) and re-run `python3 scripts/ai_compare.py`.

## Latency / cost

- N/A (blocked)
