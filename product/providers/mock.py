"""Mock / dry-run image provider for CI-safe smoke tests (no API credits).

When practical, returns curated V4-era style sample PNGs from docs/refs
(jelly gummy / clay / plush / glossy art-direction assets). Falls back to a
tiny generated PNG if samples are missing. Same ImageProvider interface.
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

from product.providers.base import (
    ProviderGenerateRequest,
    ProviderGenerateResult,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Prefer tracked art-direction refs that approximate V4 style outputs.
# Live V4.x edited.png artifacts are gitignored; these stand in for mock demos.
_STYLE_SAMPLES: dict[str, list[Path]] = {
    "gummy": [
        _REPO_ROOT / "docs/refs/jelly_gummy/ref_jelly_gummy_flower.png",
        _REPO_ROOT / "docs/refs/jelly_gummy/ref_jelly_gummy_rocket.png",
        _REPO_ROOT / "docs/refs/ref2_gummy_star_gradient.png",
        _REPO_ROOT / "docs/refs/ref3_gummy_star_magenta.png",
    ],
    "clay": [
        _REPO_ROOT / "docs/refs/batch3/clay_claymorph_figure.png",
        _REPO_ROOT / "docs/refs/batch2/01_matte_ceramic_character_pot.png",
    ],
    "plush": [
        _REPO_ROOT / "docs/refs/batch3/plush_fiber_pile.png",
        _REPO_ROOT / "docs/refs/ref4_kawaii_heart.png",
    ],
    "glossy": [
        _REPO_ROOT / "docs/refs/ref1_glossy_blob.png",
        _REPO_ROOT / "docs/refs/batch2/02_gold_foil_balloon_star.png",
    ],
}

_VARIATION = 0


def _minimal_png(
    width: int = 64,
    height: int = 64,
    rgba: tuple[int, int, int, int] = (255, 120, 160, 255),
) -> bytes:
    """Tiny valid RGBA PNG without Pillow (CI-safe)."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    r, g, b, a = rgba
    row = bytes([0]) + bytes([r, g, b, a]) * width
    raw = row * height
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def _infer_style(prompt: str) -> str:
    lower = (prompt or "").lower()
    for style in ("gummy", "clay", "plush", "glossy"):
        if style in lower:
            return style
    return "gummy"


def _load_style_sample(style: str) -> tuple[bytes | None, str | None]:
    global _VARIATION
    paths = _STYLE_SAMPLES.get(style) or _STYLE_SAMPLES["gummy"]
    existing = [p for p in paths if p.is_file()]
    if not existing:
        return None, None
    chosen = existing[_VARIATION % len(existing)]
    _VARIATION += 1
    return chosen.read_bytes(), str(chosen.relative_to(_REPO_ROOT))


class MockImageProvider:
    """Returns a real style sample PNG when available. Never calls external APIs."""

    name = "mock"
    model = "mock-v4-samples"

    def __init__(self, *, echo_doodle: bool = False) -> None:
        self.echo_doodle = echo_doodle

    def generate(self, request: ProviderGenerateRequest) -> ProviderGenerateResult:
        if self.echo_doodle and request.doodle_png:
            image = request.doodle_png
            sample_path = None
        else:
            style = _infer_style(request.prompt)
            image, sample_path = _load_style_sample(style)
            if image is None:
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
                "sample_path": sample_path,
            },
        )
