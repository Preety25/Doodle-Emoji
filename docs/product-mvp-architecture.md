# Product MVP Architecture — Dooji / Doodle Emoji

**Branch:** `product/mvp` (based on `stylization/v4-ai-rendering` @ v4.4)  
**Scope:** Production transform foundation only. No Expo app, auth, analytics, payments, or DB.

---

## 1. V4 lab today

The stylization lab under `lab/v4/` is an **experiment tree**:

| Area | Role |
|---|---|
| `lab/v4/generative/xai_edit.py` | Live xAI Imagine edits client (`grok-imagine-image-2.0`) |
| `lab/v4/generative/prompts.py` | Prompt builders through V4.4 |
| `lab/v4/stroke_roles.py` | Role taxonomy A–G + prompt serialization |
| `lab/v4/strict_blueprint.py` | Recognition field model (observed / inferred / allowed / forbidden) |
| `lab/v4/semantic_lock.py` | Hand enrichments for five test doodles |
| `lab/v4/v4*_*.py` + `scripts/v4_*.py` | Runners, contact sheets, spend caps, regression packs |
| `out/v4/**` | Run artifacts / reviews |

Product doctrine from V4.4: *Draw something messy → understand intent → make YOUR version beautiful.* Style sheets teach **material only**; semantics lock identity across styles.

Lab code on this branch is **preserved untouched**. Production does not delete, move, or rewrite experiment runners.

---

## 2. What is extracted into production

New package: **`product/`** — thin wrappers + data configs over reusable V4 pieces.

| Production module | Wraps / owns |
|---|---|
| `product/providers/xai.py` | `lab.v4.generative.xai_edit.edit_image` behind `ImageProvider` |
| `product/transform/prompt_compiler.py` | V4.4 doctrine constants + `stroke_roles` helpers; **no** lab `SPECIAL(uid)` hardcodes |
| `product/styles/*.json` | gummy / clay / plush / glossy as **data** |
| `product/transform/raster.py` | Optional `lab.v3.raster.rasterize_doodle` when client sends stroke JSON |
| `product/transform/postprocess.py` | Stub pipeline seam (bg → alpha → crop/normalize) |
| `product/transform/service.py` | Orchestration: ingest → prompt → provider → postprocess |
| `product/api/app.py` | Minimal `POST /v1/transform` (stdlib HTTP) |

**Not shipped on the production path:** experiment runners, hand `ENRICHMENTS`, golden-test hacks, Blender, research scripts, hardcoded doodle handlers, `out/` artifacts.

---

## 3. API boundary

```http
POST /v1/transform
Content-Type: application/json

{
  "style": "gummy" | "clay" | "plush" | "glossy",
  "doodle_base64": "<png bytes>",
  "strokes": { ... } | null,
  "doodle_path": null,
  "client_doodle_id": "optional",
  "options": { "size": 1024, "dry_run": false }
}
```

**Response (shape):**

```json
{
  "status": "ok" | "dry_run" | "error",
  "style": "gummy",
  "transform_version": "product.mvp.v1",
  "provider": "xai" | "mock",
  "model": "grok-imagine-image-2.0",
  "image_path": null,
  "image_url": null,
  "image_base64": "<final png>",
  "error": null,
  "metadata": {
    "prompt_len": 1234,
    "style_sheet": "...",
    "postprocess": { "steps": [] },
    "provider": { }
  }
}
```

**Contract rules:**

- No provider names required from the client.
- Prompts, style sheets, and API keys stay server-side (never in response body as full prompt text).
- `GET /health` / `GET /v1/health` for liveness.

Core types: `TransformRequest` / `TransformResult` in `product/transform/contracts.py`.  
Handler: `product.api.app.handle_transform`.

---

## 4. Provider abstraction

```text
ImageProvider.generate(ProviderGenerateRequest) → ProviderGenerateResult
```

- `ProviderGenerateRequest`: doodle PNG bytes, compiled prompt, optional style-ref PNG bytes, resolution/quality.
- Implementations:
  - **`XAIImageProvider`** (`product/providers/xai.py`) — current live backend
  - **`MockImageProvider`** (`product/providers/mock.py`) — CI / dry-run, zero credits
- Factory: `product.providers.get_provider()` via `IMAGE_PROVIDER=xai|mock`
- Swapping to Gemini/OpenAI later = new adapter class + env; **TransformRequest / mobile contract unchanged**.

---

## 5. Style abstraction

Styles live as JSON under `product/styles/`:

- `sheet` + `sheet_fallbacks`
- `description`, `form_language`, `material_language`, `lighting_language`
- `forbidden[]`
- `prompt_fragments` (look / hard_rule / extra)

Canonical sheet paths: `docs/refs/style_sheets/sheet_{gummy,clay,plush,glossy}.png`  
**Gap:** those files were missing on the V4 branch tip; fallbacks use older tracked refs where available (gummy/glossy). Commit real material-only boards before quality gates.

---

## 6. Secrets

| Variable | Where | Notes |
|---|---|---|
| `XAI_API_KEY` | Server only | Required for live xAI; never print/log/commit |
| `IMAGE_PROVIDER` | Server | `xai` \| `mock` |
| `DOOJI_OUT` | Server optional | Persist finals under this dir |
| `DOOJI_HOST` / `DOOJI_PORT` | Server optional | HTTP stub bind |

See `.env.example` (placeholders only). `.env` is gitignored.

---

## 7. Post-processing

Stub pipeline in `product/transform/postprocess.py`:

```text
generated → bg_removal (stub) → alpha/edge (RGBA ensure) → crop/normalize (square) → final PNG
```

Pillow recommended (`requirements-product.txt`). Real matting / edge cleanup is a follow-up; the seam exists so providers stay swap-friendly.

---

## 8. Mobile communication

```text
Expo app (future)
   │  POST doodle PNG (+ optional stroke JSON) + style
   ▼
product/api  POST /v1/transform
   ▼
TransformService → prompt compiler → ImageProvider → postprocess
   ▼
final PNG (base64 / later URL) → app save/share
```

App must **not** embed prompts, style sheets, or provider SDKs/keys.

---

## 9. Switching providers

1. Implement `ImageProvider` (same `generate` signature).
2. Register in `product/providers/get_provider`.
3. Set `IMAGE_PROVIDER=…` + provider-specific secrets.
4. Keep prompt compiler + style packs + recognition schema unchanged.
5. Gate with mock smoke + a small live golden subset when credits allow.

---

## 10. How to run smoke tests

```bash
# CI-safe (default — mock provider, no credits)
python3 -m tests.product.test_transform_smoke

# Optional live (spends xAI credits — not for CI)
IMAGE_PROVIDER=xai DOOJI_LIVE=1 XAI_API_KEY=... python3 -m tests.product.test_transform_smoke

# Optional HTTP stub
IMAGE_PROVIDER=mock python3 -m product.api.app
```

---

## 11. Remaining before Expo can start

1. Version and commit canonical style sheets.
2. Lightweight recognition (VLM or heuristics) replacing default empty lock.
3. Real background removal / sticker alpha finish.
4. Auth + rate limits + durable image storage (URLs).
5. Hosted deploy of `POST /v1/transform`.
6. Then: Expo canvas + four style chips + result screen calling the API.
