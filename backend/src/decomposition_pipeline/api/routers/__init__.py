"""
API routers for decomposition pipeline endpoints.
"""

from decomposition_pipeline.api.routers.pipeline import router as pipeline_router
from decomposition_pipeline.api.routers.sse import router as sse_router

__all__ = [
    "pipeline_router",
    "sse_router",
]
