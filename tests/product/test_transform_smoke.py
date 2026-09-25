"""CI-safe production smoke: doodle → TransformService → mock provider → result.

Default: no API credits (MockImageProvider).

Optional live check (spends credits — do not use in CI):
  IMAGE_PROVIDER=xai XAI_API_KEY=... DOOJI_LIVE=1 python3 -m tests.product.test_transform_smoke
"""
from __future__ import annotations

import base64
import os
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from product.api.app import handle_transform
from product.providers.mock import MockImageProvider
from product.providers.xai import XAIImageProvider
from product.transform.contracts import TransformOptions, TransformRequest
from product.transform.prompt_compiler import compile_prompt, default_recognition
from product.transform.service import TransformService
from product.transform.styles import load_style, list_styles


def _tiny_png() -> bytes:
    """1×1 red RGBA PNG."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    raw = bytes([0, 255, 0, 0, 255])
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def test_styles_as_data() -> None:
    ids = list_styles()
    assert set(ids) == {"gummy", "clay", "plush", "glossy"}
    g = load_style("gummy")
    assert g.material_language
    assert "translucent" in g.look_line.lower() or "gelatin" in g.look_line.lower()


def test_prompt_compiler_no_special_hardcodes() -> None:
    style = load_style("gummy")
    rec = default_recognition(client_doodle_id="u07")
    prompt = compile_prompt(style=style, recognition=rec, multi_image=False, n_style_refs=0)
    assert "SPECIAL (u07)" not in prompt
    assert "POLISH THE USER'S DOODLE" in prompt
    assert "GUMMY" in prompt.upper()


def test_transform_mock_smoke() -> None:
    doodle = _tiny_png()
    svc = TransformService(provider=MockImageProvider())
    result = svc.transform(
        TransformRequest(
            style="gummy",
            doodle_png=doodle,
            client_doodle_id="smoke_test",
            options=TransformOptions(size=64, dry_run=True),
        )
    )
    assert result.status in ("ok", "dry_run")
    assert result.provider == "mock"
    assert result.image_base64
    raw = base64.b64decode(result.image_base64)
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    assert result.metadata.get("prompt_len", 0) > 100
    # Prompt must not leak into client result
    assert "prompt" not in result.metadata or isinstance(result.metadata.get("prompt"), type(None))
    blob = str(result.to_dict())
    assert "POLISH THE USER" not in blob


def test_api_handler_dry_run() -> None:
    body = handle_transform(
        {
            "style": "clay",
            "doodle_base64": base64.b64encode(_tiny_png()).decode("ascii"),
            "client_doodle_id": "api_smoke",
            "options": {"dry_run": True, "size": 64},
        }
    )
    assert body["status"] in ("ok", "dry_run")
    assert body["style"] == "clay"
    assert body.get("image_base64")
    assert "XAI_API_KEY" not in str(body)


def test_xai_provider_skips_without_key() -> None:
    """Live path must fail closed when key unset — no network, no credit spend."""
    prev = os.environ.pop("XAI_API_KEY", None)
    try:
        provider = XAIImageProvider()
        from product.providers.base import ProviderGenerateRequest

        res = provider.generate(
            ProviderGenerateRequest(doodle_png=_tiny_png(), prompt="test")
        )
        assert res.ok is False
        assert "XAI_API_KEY" in (res.error or "")
    finally:
        if prev is not None:
            os.environ["XAI_API_KEY"] = prev


def optional_live() -> None:
    """Only when DOOJI_LIVE=1 and XAI_API_KEY set."""
    if os.environ.get("DOOJI_LIVE") != "1":
        print("skip live: set DOOJI_LIVE=1 to spend credits")
        return
    if not os.environ.get("XAI_API_KEY"):
        print("skip live: XAI_API_KEY unset")
        return
    # Prefer a real tiny doodle from lab pack if present
    candidates = [
        ROOT / "out" / "v4" / "v42" / "unseen" / "inputs_api" / "u01.png",
        ROOT / "docs" / "refs" / "ref4_kawaii_heart.png",
    ]
    doodle = None
    for c in candidates:
        if c.is_file():
            doodle = c.read_bytes()
            break
    if doodle is None:
        doodle = _tiny_png()
    svc = TransformService(provider=XAIImageProvider())
    result = svc.transform(
        TransformRequest(
            style="gummy",
            doodle_png=doodle,
            client_doodle_id="live_smoke",
            options=TransformOptions(size=512),
        )
    )
    print("live_status=", result.status, "provider=", result.provider, "error=", result.error)
    assert result.status == "ok", result.error


def main() -> int:
    test_styles_as_data()
    print("ok styles")
    test_prompt_compiler_no_special_hardcodes()
    print("ok prompt")
    test_transform_mock_smoke()
    print("ok transform mock")
    test_api_handler_dry_run()
    print("ok api dry-run")
    test_xai_provider_skips_without_key()
    print("ok xai skip-without-key")
    optional_live()
    print("ALL SMOKE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
