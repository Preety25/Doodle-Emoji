# V3 generative renderer

**Status:** BLOCKED_NO_API

This path is an image-edit adapter. It is not the product architecture.
Inputs, when a key is present: original doodle raster, semantic blueprint summary, style text.
Hard constraints are in the prompt: subject identity, silhouette, part count and placement,
distinctive proportions, user asymmetry. The prompt forbids a generic replacement, extra decor,
invented faces, text, backgrounds, and ground planes.

## Env vars checked

- `OPENAI_API_KEY`: missing
- `GEMINI_API_KEY`: missing
- `GOOGLE_API_KEY`: missing
- `REPLICATE_API_TOKEN`: missing

## How to run live

Export one of the keys above, install the matching SDK (`openai`, `google-generativeai`, or `replicate`),
then re-run `python3 scripts/run_v3.py --stage generative`.

## Requests

Prompt JSON: `/workspace/out/v3/generative/requests`

| example | style | api | output |
|---|---|---|---|
| 02_heart | gummy | False | `/workspace/out/v3/generative/02_heart__gummy.png` |
| 02_heart | clay | False | `/workspace/out/v3/generative/02_heart__clay.png` |
| 02_heart | plush | False | `/workspace/out/v3/generative/02_heart__plush.png` |
| 02_heart | glossy | False | `/workspace/out/v3/generative/02_heart__glossy.png` |
| 06_rocket | gummy | False | `/workspace/out/v3/generative/06_rocket__gummy.png` |
| 06_rocket | clay | False | `/workspace/out/v3/generative/06_rocket__clay.png` |
| 06_rocket | plush | False | `/workspace/out/v3/generative/06_rocket__plush.png` |
| 06_rocket | glossy | False | `/workspace/out/v3/generative/06_rocket__glossy.png` |
| 07_teddy | gummy | False | `/workspace/out/v3/generative/07_teddy__gummy.png` |
| 07_teddy | clay | False | `/workspace/out/v3/generative/07_teddy__clay.png` |
| 07_teddy | plush | False | `/workspace/out/v3/generative/07_teddy__plush.png` |
| 07_teddy | glossy | False | `/workspace/out/v3/generative/07_teddy__glossy.png` |
| 05_plant | gummy | False | `/workspace/out/v3/generative/05_plant__gummy.png` |
| 05_plant | clay | False | `/workspace/out/v3/generative/05_plant__clay.png` |
| 05_plant | plush | False | `/workspace/out/v3/generative/05_plant__plush.png` |
| 05_plant | glossy | False | `/workspace/out/v3/generative/05_plant__glossy.png` |
| 09_rose | gummy | False | `/workspace/out/v3/generative/09_rose__gummy.png` |
| 09_rose | clay | False | `/workspace/out/v3/generative/09_rose__clay.png` |
| 09_rose | plush | False | `/workspace/out/v3/generative/09_rose__plush.png` |
| 09_rose | glossy | False | `/workspace/out/v3/generative/09_rose__glossy.png` |
| 12_messy_incomplete | gummy | False | `/workspace/out/v3/generative/12_messy_incomplete__gummy.png` |
| 12_messy_incomplete | clay | False | `/workspace/out/v3/generative/12_messy_incomplete__clay.png` |
| 12_messy_incomplete | plush | False | `/workspace/out/v3/generative/12_messy_incomplete__plush.png` |
| 12_messy_incomplete | glossy | False | `/workspace/out/v3/generative/12_messy_incomplete__glossy.png` |
