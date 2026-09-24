"""Lightweight interpretation: open vs closed, components, basic stats."""
from __future__ import annotations

from typing import Any


def interpret_doodle(normalized: dict[str, Any]) -> dict[str, Any]:
    comps = normalized.get("normalized", {}).get("components") or []
    closed = [c for c in comps if c.get("closed")]
    open_ = [c for c in comps if not c.get("closed")]
    colors = [c.get("color") for c in comps if c.get("color")]
    return {
        "n_components": len(comps),
        "n_closed": len(closed),
        "n_open": len(open_),
        "has_multiple_disconnected": len(comps) > 1,
        "user_colors": colors,
        "invent_faces": False,  # never invent faces in v1
        "components": comps,
    }
