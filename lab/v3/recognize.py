"""Dispatch a doodle to a category handler.

The corpus category is an input to this POC. Handlers still check geometry and
can lower confidence. This is not a general recognizer.
"""
from __future__ import annotations

import json
from pathlib import Path

from lab.normalize import normalize_doodle
from lab.v3.handlers import HANDLERS
from lab.v3.schema import validate_blueprint


def load_doodle(path: str | Path) -> dict:
    path = Path(path)
    data = json.loads(path.read_text())
    data["_path"] = str(path)
    data["_source_id"] = path.stem
    return data


def recognize_doodle(path: str | Path) -> dict:
    data = load_doodle(path)
    norm = normalize_doodle(data)
    components = norm["normalized"]["components"]
    meta = data.get("meta") or {}
    category = (meta.get("category") or "").strip().lower()
    source_id = data["_source_id"]
    handler = HANDLERS.get(category)
    if handler is None:
        from lab.v3.handlers.messy import handle_messy

        bp = handle_messy(source_id, meta, components)
        bp["confidence"] = "LOW"
        bp["notes"] = (
            f"No category handler for {category!r}. Fell through to the low-confidence messy path. "
            + bp.get("notes", "")
        )
        bp["handler"] = "fallback_low_confidence"
    else:
        bp = handler(source_id, meta, components)
    bp["source_category_hint"] = category
    bp["source_path"] = data["_path"]
    bp["recognition_scope"] = (
        "category-specific handler selected from the corpus category hint; "
        "general recognition is not solved"
    )
    errors = validate_blueprint(bp)
    bp["schema_errors"] = errors
    if errors:
        raise ValueError(f"blueprint schema errors for {source_id}: {errors}")
    return bp
