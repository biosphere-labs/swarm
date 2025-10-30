"""
Error handlers and utilities for FastAPI.

Provides global exception handlers, error response formatting,
and HTTP status code mapping.
"""

import logging
import traceback
from typing import Any, Dict, Optional, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from decomposition_pipeline.errors.exceptions import (
    PipelineError,
    NetworkError,
    ValidationError,
    LLMError,
    PipelineStateError,
    AuthenticationError,
    CheckpointError,
    GraphExecutionError,
    AgentPoolError,
    HumanApprovalError,
    ConfigurationError,
    TimeoutError,
    RateLimitError,
    QuotaExceededError,
    ErrorCode,
)

logger = logging.getLogger(__name__)


def get_http_status(error: Union[PipelineError, Exception]) -> int:
    """
    Map exception type to appropriate HTTP status code.

    Args:
        error: Exception instance

    Returns:
        HTTP status code
    """
    if isinstance(error, ValidationError):
        return status.HTTP_400_BAD_REQUEST
    elif isinstance(error, AuthenticationError):
        return status.HTTP_401_UNAUTHORIZED
    elif isinstance(error, HumanApprovalError):
        return status.HTTP_403_FORBIDDEN
    elif isinstance(error, (CheckpointError, PipelineStateError)):
        return status.HTTP_404_NOT_FOUND
    elif isinstance(error, RateLimitError):
        return status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(error, TimeoutError):
        return status.HTTP_504_GATEWAY_TIMEOUT
    elif isinstance(error, (NetworkError, LLMError, QuotaExceededError)):
        return status.HTTP_502_BAD_GATEWAY
    elif isinstance(error, ConfigurationError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(error, (GraphExecutionError, AgentPoolError)):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(error, PipelineError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR


def get_error_code(error: Union[PipelineError, Exception]) -> str:
    """
    Extract error code from exception.

    Args:
        error: Exception instance

    Returns:
        Error code string
    """
    if isinstance(error, PipelineError):
        return error.error_code.value
    else:
        return ErrorCode.UNKNOWN_ERROR.value


def create_error_response(
    error: Union[PipelineError, Exception],
    include_traceback: bool = False,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create standardized error response.

    Args:
        error: Exception instance
        include_traceback: Whether to include traceback in response
        request_id: Optional request ID for tracking

    Returns:
        Dictionary containing error response
    """
    response: Dict[str, Any] = {
        "success": False,
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
            "code": get_error_code(error),
        },
    }

    # Add pipeline error details
    if isinstance(error, PipelineError):
        if error.details:
            response["error"]["details"] = error.details
        if error.recovery_suggestion:
            response["error"]["recovery_suggestion"] = error.recovery_suggestion
        if error.original_exception:
            response["error"]["original_error"] = str(error.original_exception)

    # Add request ID if provided
    if request_id:
        response["request_id"] = request_id

    # Add traceback in debug mode
    if include_traceback:
        response["error"]["traceback"] = traceback.format_exc()

    return response


async def pipeline_error_handler(request: Request, exc: PipelineError) -> JSONResponse:
    """
    Handle PipelineError exceptions.

    Args:
        request: FastAPI request object
        exc: PipelineError instance

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"Pipeline error occurred: {exc}",
        extra={
            "error_code": exc.error_code.value,
            "details": exc.details,
            "path": request.url.path,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=get_http_status(exc),
        content=create_error_response(
            exc,
            include_traceback=False,
            request_id=request.headers.get("X-Request-ID"),
        ),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle FastAPI validation errors.

    Args:
        request: FastAPI request object
        exc: RequestValidationError instance

    Returns:
        JSONResponse with validation error details
    """
    logger.warning(
        f"Validation error occurred: {exc}",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )

    # Convert to our ValidationError format
    validation_error = ValidationError(
        message="Request validation failed",
        error_code=ErrorCode.VALIDATION_INVALID_INPUT,
        details={
            "errors": exc.errors(),
            "body": str(exc.body) if hasattr(exc, "body") else None,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            validation_error,
            include_traceback=False,
            request_id=request.headers.get("X-Request-ID"),
        ),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions from FastAPI/Starlette.

    Args:
        request: FastAPI request object
        exc: HTTPException instance

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        f"HTTP exception occurred: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "code": f"HTTP_{exc.status_code}",
            },
            "request_id": request.headers.get("X-Request-ID"),
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with error details
    """
    logger.error(
        f"Unhandled exception occurred: {exc}",
        extra={
            "path": request.url.path,
            "exception_type": type(exc).__name__,
        },
        exc_info=True,
    )

    # Wrap in generic PipelineError
    pipeline_error = PipelineError(
        message="An unexpected error occurred",
        error_code=ErrorCode.INTERNAL_ERROR,
        details={"original_error": str(exc)},
        original_exception=exc,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            pipeline_error,
            include_traceback=False,
            request_id=request.headers.get("X-Request-ID"),
        ),
    )


def register_error_handlers(app: Any) -> None:
    """
    Register all error handlers with FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(PipelineError, pipeline_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Error handlers registered successfully")
