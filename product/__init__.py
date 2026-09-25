"""Dooji / Doodle Emoji production foundation.

Production transform boundary. Lab experiments under ``lab/`` stay untouched;
this package wraps reusable V4 capabilities behind a provider-agnostic API.
"""

TRANSFORM_VERSION = "product.mvp.v1"

__all__ = [
    "TRANSFORM_VERSION",
    "TransformRequest",
    "TransformResult",
    "TransformService",
]


def __getattr__(name: str):
    # Lazy exports avoid circular imports with transform.service
    if name == "TransformRequest":
        from product.transform.contracts import TransformRequest

        return TransformRequest
    if name == "TransformResult":
        from product.transform.contracts import TransformResult

        return TransformResult
    if name == "TransformService":
        from product.transform.service import TransformService

        return TransformService
    raise AttributeError(name)
