"""Post-processing boundary: generated → bg removal → alpha/edge → crop/normalize → PNG.

MVP ships stubs that pass through (or lightly normalize) so the pipeline seam exists.
Swap implementations without touching the provider or API contract.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PostProcessResult:
    image_bytes: bytes
    steps: list[str]
    notes: list[str]


def _has_pillow() -> bool:
    try:
        import PIL  # noqa: F401

        return True
    except ImportError:
        return False


def remove_background(image_bytes: bytes) -> tuple[bytes, str]:
    """Stub: no real matting yet. Pass-through with note."""
    return image_bytes, "bg_removal:stub_passthrough"


def ensure_alpha_edges(image_bytes: bytes) -> tuple[bytes, str]:
    """If Pillow available, ensure RGBA. No edge feathering yet."""
    if not _has_pillow():
        return image_bytes, "alpha_edge:skipped_no_pillow"
    from PIL import Image

    im = Image.open(io.BytesIO(image_bytes))
    if im.mode != "RGBA":
        im = im.convert("RGBA")
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        return buf.getvalue(), "alpha_edge:converted_rgba"
    return image_bytes, "alpha_edge:already_rgba"


def crop_and_normalize(
    image_bytes: bytes,
    *,
    size: int = 1024,
) -> tuple[bytes, str]:
    """Square letterbox/normalize to ``size`` when Pillow is available."""
    if not _has_pillow():
        return image_bytes, "crop_normalize:skipped_no_pillow"
    from PIL import Image

    im = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    # Tight bbox on non-transparent (or non-near-white) pixels when possible
    alpha = im.split()[-1]
    bbox = alpha.getbbox()
    if bbox:
        im = im.crop(bbox)
    # Fit into square canvas
    w, h = im.size
    scale = min(size / max(w, 1), size / max(h, 1))
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(im, ((size - nw) // 2, (size - nh) // 2), im)
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue(), f"crop_normalize:square_{size}"


def run_postprocess(
    image_bytes: bytes,
    *,
    size: int = 1024,
    skip: bool = False,
) -> PostProcessResult:
    """Full stub pipeline. ``skip=True`` returns bytes unchanged (dry-run / mock)."""
    if skip:
        return PostProcessResult(
            image_bytes=image_bytes,
            steps=["skipped"],
            notes=["postprocess skipped"],
        )
    steps: list[str] = []
    notes: list[str] = [
        "MVP stubs: real bg-removal / edge cleanup still TODO.",
    ]
    out, step = remove_background(image_bytes)
    steps.append(step)
    out, step = ensure_alpha_edges(out)
    steps.append(step)
    out, step = crop_and_normalize(out, size=size)
    steps.append(step)
    return PostProcessResult(image_bytes=out, steps=steps, notes=notes)


def write_png(image_bytes: bytes, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image_bytes)
    return path


def postprocess_meta(result: PostProcessResult) -> dict[str, Any]:
    return {"steps": result.steps, "notes": result.notes}
