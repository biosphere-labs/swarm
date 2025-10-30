"""
Middleware components for the Decomposition Pipeline.

Provides middleware for error handling, logging, and request tracking.
"""

from decomposition_pipeline.middleware.error_middleware import ErrorHandlingMiddleware

__all__ = ["ErrorHandlingMiddleware"]
