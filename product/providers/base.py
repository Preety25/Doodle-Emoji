"""Image provider abstraction — no xAI (or any vendor) assumptions in the API contract."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class ProviderGenerateRequest:
    """Provider-facing request. Prompt is already compiled server-side."""

    doodle_png: bytes
    prompt: str
    style_ref_pngs: list[bytes] = field(default_factory=list)
    resolution: str = "1k"
    quality: str = "low"
    n: int = 1
    # Scratch dir for adapters that still speak filesystem (lab xAI adapter).
    work_dir: str | None = None


@dataclass
class ProviderGenerateResult:
    ok: bool
    image_bytes: bytes | None = None
    provider: str = ""
    model: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class ImageProvider(Protocol):
    """Replaceable image backend (xAI today; Gemini/OpenAI/… later)."""

    name: str

    def generate(self, request: ProviderGenerateRequest) -> ProviderGenerateResult:
        ...
