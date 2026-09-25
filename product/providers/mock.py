"""Mock / dry-run image provider for CI-safe smoke tests (no API credits)."""
from __future__ import annotations

import struct
import zlib

from product.providers.base import (
    ProviderGenerateRequest,
    ProviderGenerateResult,
)


def _minimal_png(width: int = 64, height: int = 64, rgba: tuple[int, int, int, int] = (255, 120, 160, 255)) -> bytes:
    """Tiny valid RGBA PNG without Pillow (CI-safe)."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b""
    r, g, b, a = rgba
    row = bytes([0]) + bytes([r, g, b, a]) * width
    raw = row * height
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


class MockImageProvider:
    """Returns a small placeholder PNG. Never calls external APIs."""

    name = "mock"
    model = "mock-passthrough-v1"

    def __init__(self, *, echo_doodle: bool = False) -> None:
        self.echo_doodle = echo_doodle

    def generate(self, request: ProviderGenerateRequest) -> ProviderGenerateResult:
        if self.echo_doodle and request.doodle_png:
            image = request.doodle_png
        else:
            image = _minimal_png()
        return ProviderGenerateResult(
            ok=True,
            image_bytes=image,
            provider=self.name,
            model=self.model,
            metadata={
                "dry_run": True,
                "prompt_len": len(request.prompt or ""),
                "n_style_refs": len(request.style_ref_pngs),
                "doodle_bytes": len(request.doodle_png or b""),
            },
        )
