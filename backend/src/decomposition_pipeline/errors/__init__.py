"""
Error handling module for the Decomposition Pipeline.

This module provides custom exception classes, error handlers,
and utilities for managing errors throughout the application.
"""

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
)
from decomposition_pipeline.errors.handlers import (
    create_error_response,
    get_error_code,
    get_http_status,
)

__all__ = [
    # Exceptions
    "PipelineError",
    "NetworkError",
    "ValidationError",
    "LLMError",
    "PipelineStateError",
    "AuthenticationError",
    "CheckpointError",
    "GraphExecutionError",
    "AgentPoolError",
    "HumanApprovalError",
    "ConfigurationError",
    "TimeoutError",
    "RateLimitError",
    "QuotaExceededError",
    # Handlers
    "create_error_response",
    "get_error_code",
    "get_http_status",
]
