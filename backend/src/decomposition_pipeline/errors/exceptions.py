"""
Custom exception classes for the Decomposition Pipeline.

Defines a comprehensive hierarchy of exceptions for different
error categories and provides structured error information.
"""

from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the pipeline."""

    # Network errors (1xxx)
    NETWORK_CONNECTION_FAILED = "NETWORK_1001"
    NETWORK_TIMEOUT = "NETWORK_1002"
    NETWORK_DNS_FAILED = "NETWORK_1003"
    NETWORK_SSL_ERROR = "NETWORK_1004"

    # Validation errors (2xxx)
    VALIDATION_INVALID_INPUT = "VALIDATION_2001"
    VALIDATION_SCHEMA_MISMATCH = "VALIDATION_2002"
    VALIDATION_MISSING_FIELD = "VALIDATION_2003"
    VALIDATION_INVALID_FORMAT = "VALIDATION_2004"
    VALIDATION_CONSTRAINT_VIOLATION = "VALIDATION_2005"

    # LLM errors (3xxx)
    LLM_API_ERROR = "LLM_3001"
    LLM_RATE_LIMIT = "LLM_3002"
    LLM_QUOTA_EXCEEDED = "LLM_3003"
    LLM_INVALID_RESPONSE = "LLM_3004"
    LLM_TIMEOUT = "LLM_3005"
    LLM_MODEL_NOT_FOUND = "LLM_3006"
    LLM_CONTEXT_LENGTH_EXCEEDED = "LLM_3007"

    # Pipeline state errors (4xxx)
    PIPELINE_STATE_CORRUPTED = "PIPELINE_4001"
    PIPELINE_STATE_MISSING = "PIPELINE_4002"
    PIPELINE_INVALID_STAGE = "PIPELINE_4003"
    PIPELINE_DEPENDENCY_MISSING = "PIPELINE_4004"

    # Authentication errors (5xxx)
    AUTH_INVALID_TOKEN = "AUTH_5001"
    AUTH_EXPIRED_TOKEN = "AUTH_5002"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_5003"
    AUTH_INVALID_CREDENTIALS = "AUTH_5004"

    # Checkpoint errors (6xxx)
    CHECKPOINT_SAVE_FAILED = "CHECKPOINT_6001"
    CHECKPOINT_LOAD_FAILED = "CHECKPOINT_6002"
    CHECKPOINT_NOT_FOUND = "CHECKPOINT_6003"
    CHECKPOINT_CORRUPTED = "CHECKPOINT_6004"

    # Graph execution errors (7xxx)
    GRAPH_EXECUTION_FAILED = "GRAPH_7001"
    GRAPH_NODE_FAILED = "GRAPH_7002"
    GRAPH_CYCLE_DETECTED = "GRAPH_7003"
    GRAPH_DEADLOCK = "GRAPH_7004"

    # Agent pool errors (8xxx)
    AGENT_POOL_EXHAUSTED = "AGENT_8001"
    AGENT_CREATION_FAILED = "AGENT_8002"
    AGENT_TIMEOUT = "AGENT_8003"
    AGENT_EXECUTION_FAILED = "AGENT_8004"

    # Human approval errors (9xxx)
    APPROVAL_TIMEOUT = "APPROVAL_9001"
    APPROVAL_REJECTED = "APPROVAL_9002"
    APPROVAL_INVALID_RESPONSE = "APPROVAL_9003"

    # Configuration errors (10xxx)
    CONFIG_INVALID = "CONFIG_10001"
    CONFIG_MISSING = "CONFIG_10002"
    CONFIG_PARSE_ERROR = "CONFIG_10003"

    # Generic errors
    INTERNAL_ERROR = "INTERNAL_0001"
    UNKNOWN_ERROR = "UNKNOWN_0000"


class PipelineError(Exception):
    """
    Base exception class for all pipeline errors.

    Provides structured error information including error codes,
    context, and recovery suggestions.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize pipeline error.

        Args:
            message: Human-readable error message
            error_code: Standardized error code
            details: Additional context about the error
            recovery_suggestion: Suggested action to recover from error
            original_exception: Original exception if this wraps another error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.recovery_suggestion = recovery_suggestion
        self.original_exception = original_exception

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for serialization.

        Returns:
            Dictionary containing error information
        """
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code.value,
            "details": self.details,
        }

        if self.recovery_suggestion:
            result["recovery_suggestion"] = self.recovery_suggestion

        if self.original_exception:
            result["original_error"] = str(self.original_exception)

        return result

    def __str__(self) -> str:
        """String representation of the error."""
        return f"[{self.error_code.value}] {self.message}"


class NetworkError(PipelineError):
    """
    Raised when network-related errors occur.

    Examples: Connection failures, timeouts, DNS errors, SSL errors.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.NETWORK_CONNECTION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Check network connection and retry",
            original_exception=original_exception,
        )


class ValidationError(PipelineError):
    """
    Raised when input validation fails.

    Examples: Invalid schema, missing required fields, format errors.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.VALIDATION_INVALID_INPUT,
        details: Optional[Dict[str, Any]] = None,
        field_name: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if field_name:
            details["field_name"] = field_name

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Check input data and correct invalid fields",
            original_exception=original_exception,
        )


class LLMError(PipelineError):
    """
    Raised when LLM API calls fail.

    Examples: API errors, rate limits, quota exceeded, timeouts.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.LLM_API_ERROR,
        details: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Check LLM API credentials and retry",
            original_exception=original_exception,
        )


class RateLimitError(LLMError):
    """
    Raised when LLM API rate limit is exceeded.

    This is a specific type of LLM error that indicates temporary unavailability.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if retry_after:
            details["retry_after"] = retry_after

        super().__init__(
            message=message,
            error_code=ErrorCode.LLM_RATE_LIMIT,
            details=details,
            provider=provider,
            model=model,
            recovery_suggestion=f"Wait {retry_after or 60} seconds and retry" if retry_after else "Wait and retry",
            original_exception=original_exception,
        )


class QuotaExceededError(LLMError):
    """
    Raised when LLM API quota is exceeded.

    This indicates a hard limit has been reached and requires intervention.
    """

    def __init__(
        self,
        message: str = "API quota exceeded",
        details: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.LLM_QUOTA_EXCEEDED,
            details=details,
            provider=provider,
            model=model,
            recovery_suggestion="Check API usage limits and upgrade plan if necessary",
            original_exception=original_exception,
        )


class PipelineStateError(PipelineError):
    """
    Raised when pipeline state is corrupted or invalid.

    Examples: Missing state data, corrupted state, invalid stage transitions.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.PIPELINE_STATE_CORRUPTED,
        details: Optional[Dict[str, Any]] = None,
        stage: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if stage:
            details["stage"] = stage

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Restore from checkpoint or restart pipeline",
            original_exception=original_exception,
        )


class AuthenticationError(PipelineError):
    """
    Raised when authentication or authorization fails.

    Examples: Invalid tokens, expired sessions, insufficient permissions.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.AUTH_INVALID_TOKEN,
        details: Optional[Dict[str, Any]] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Check authentication credentials and re-authenticate",
            original_exception=original_exception,
        )


class CheckpointError(PipelineError):
    """
    Raised when checkpoint operations fail.

    Examples: Failed to save checkpoint, failed to load checkpoint, corrupted checkpoint.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.CHECKPOINT_SAVE_FAILED,
        details: Optional[Dict[str, Any]] = None,
        checkpoint_id: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if checkpoint_id:
            details["checkpoint_id"] = checkpoint_id

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Check database connectivity and storage",
            original_exception=original_exception,
        )


class GraphExecutionError(PipelineError):
    """
    Raised when graph execution fails.

    Examples: Node execution failure, cycle detection, deadlock.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.GRAPH_EXECUTION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        node_name: Optional[str] = None,
        graph_name: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if node_name:
            details["node_name"] = node_name
        if graph_name:
            details["graph_name"] = graph_name

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Check graph configuration and node implementations",
            original_exception=original_exception,
        )


class AgentPoolError(PipelineError):
    """
    Raised when agent pool operations fail.

    Examples: Pool exhausted, agent creation failure, agent timeout.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.AGENT_POOL_EXHAUSTED,
        details: Optional[Dict[str, Any]] = None,
        pool_name: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if pool_name:
            details["pool_name"] = pool_name

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Increase agent pool size or wait for agents to become available",
            original_exception=original_exception,
        )


class HumanApprovalError(PipelineError):
    """
    Raised when human approval operations fail.

    Examples: Approval timeout, rejection, invalid response.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.APPROVAL_TIMEOUT,
        details: Optional[Dict[str, Any]] = None,
        gate_name: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if gate_name:
            details["gate_name"] = gate_name

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Provide approval or modify rejection reason",
            original_exception=original_exception,
        )


class ConfigurationError(PipelineError):
    """
    Raised when configuration is invalid or missing.

    Examples: Invalid config format, missing required settings, parse errors.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.CONFIG_INVALID,
        details: Optional[Dict[str, Any]] = None,
        config_key: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Check configuration file and environment variables",
            original_exception=original_exception,
        )


class TimeoutError(PipelineError):
    """
    Raised when an operation times out.

    This can occur in various contexts including LLM calls, agent execution, etc.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.NETWORK_TIMEOUT,
        details: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
        operation: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        if details is None:
            details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            recovery_suggestion=recovery_suggestion or "Increase timeout or optimize operation",
            original_exception=original_exception,
        )
