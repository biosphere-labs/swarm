"""
Error handling middleware for FastAPI.

Provides request tracking, error logging, and structured error responses.
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from decomposition_pipeline.errors import PipelineError, create_error_response

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for error handling and request tracking.

    Features:
    - Assigns unique request IDs
    - Logs request/response information
    - Tracks request duration
    - Provides structured error handling
    """

    def __init__(self, app: ASGIApp, enable_request_logging: bool = True):
        """
        Initialize error handling middleware.

        Args:
            app: ASGI application
            enable_request_logging: Whether to log all requests/responses
        """
        super().__init__(app)
        self.enable_request_logging = enable_request_logging

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle errors.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response object
        """
        # Generate request ID if not present
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Log incoming request
        if self.enable_request_logging:
            logger.info(
                f"Incoming request: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else None,
                },
            )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log response
            if self.enable_request_logging:
                logger.info(
                    f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                    extra={
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2),
                    },
                )

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "duration_ms": round(duration * 1000, 2),
                },
                exc_info=True,
            )

            # Re-raise to be handled by exception handlers
            raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request/response logging.

    Logs request body, response body, and headers in addition to basic info.
    Use with caution in production as it may log sensitive data.
    """

    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_response_body: bool = False,
        log_headers: bool = False,
    ):
        """
        Initialize request logging middleware.

        Args:
            app: ASGI application
            log_request_body: Whether to log request body
            log_response_body: Whether to log response body
            log_headers: Whether to log headers
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.log_headers = log_headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with detailed logging.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response object
        """
        request_id = getattr(request.state, "request_id", "unknown")

        # Log request details
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
        }

        if self.log_headers:
            log_data["headers"] = dict(request.headers)

        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                log_data["body"] = body.decode("utf-8") if body else None
            except Exception as e:
                log_data["body_error"] = str(e)

        logger.debug("Request details", extra=log_data)

        # Process request
        response = await call_next(request)

        # Log response details
        if self.log_response_body:
            response_log_data = {
                "request_id": request_id,
                "status_code": response.status_code,
            }
            if self.log_headers:
                response_log_data["headers"] = dict(response.headers)

            logger.debug("Response details", extra=response_log_data)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.

    This is a basic implementation. For production use, consider
    using a more robust solution with Redis or similar.
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        enabled: bool = False,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute per client
            enabled: Whether rate limiting is enabled
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.enabled = enabled
        self.request_counts = {}  # In-memory storage (not production-ready)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint

        Returns:
            Response object
        """
        if not self.enabled:
            return await call_next(request)

        # Get client identifier (IP address)
        client_host = request.client.host if request.client else "unknown"

        # Check rate limit (simplified implementation)
        current_time = time.time()
        minute_window = int(current_time / 60)

        key = f"{client_host}:{minute_window}"
        current_count = self.request_counts.get(key, 0)

        if current_count >= self.requests_per_minute:
            from fastapi.responses import JSONResponse
            from decomposition_pipeline.errors import RateLimitError

            error = RateLimitError(
                message="Rate limit exceeded",
                retry_after=60,
            )

            return JSONResponse(
                status_code=429,
                content=create_error_response(error),
                headers={"Retry-After": "60"},
            )

        # Increment counter
        self.request_counts[key] = current_count + 1

        # Clean old entries (keep last 2 minutes)
        keys_to_delete = [
            k for k in self.request_counts.keys()
            if int(k.split(":")[-1]) < minute_window - 1
        ]
        for k in keys_to_delete:
            del self.request_counts[k]

        return await call_next(request)
