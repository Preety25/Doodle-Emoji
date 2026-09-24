"""V4 generative image-edit adapters (xAI Imagine). Live calls only when XAI_API_KEY is set."""

from lab.v4.generative.prompts import build_edit_prompt, build_request, blueprint_summary
from lab.v4.generative.xai_edit import (
    MODEL,
    XAI_EDITS_URL,
    approx_cost_usd,
    edit_image,
    has_xai_key,
)

__all__ = [
    "MODEL",
    "XAI_EDITS_URL",
    "approx_cost_usd",
    "blueprint_summary",
    "build_edit_prompt",
    "build_request",
    "edit_image",
    "has_xai_key",
]
