"""
Tests for custom exception classes.
"""

import pytest

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


class TestPipelineError:
    """Tests for PipelineError base class."""

    def test_basic_error_creation(self):
        """Test creating a basic pipeline error."""
        error = PipelineError("Test error")
        assert str(error) == f"[{ErrorCode.INTERNAL_ERROR.value}] Test error"
        assert error.message == "Test error"
        assert error.error_code == ErrorCode.INTERNAL_ERROR
        assert error.details == {}
        assert error.recovery_suggestion is None
        assert error.original_exception is None

    def test_error_with_details(self):
        """Test creating error with details."""
        details = {"field": "value", "count": 42}
        error = PipelineError(
            "Test error",
            error_code=ErrorCode.VALIDATION_INVALID_INPUT,
            details=details,
            recovery_suggestion="Fix the input",
        )
        assert error.details == details
        assert error.recovery_suggestion == "Fix the input"
        assert error.error_code == ErrorCode.VALIDATION_INVALID_INPUT

    def test_error_with_original_exception(self):
        """Test wrapping original exception."""
        original = ValueError("Original error")
        error = PipelineError(
            "Wrapped error",
            original_exception=original,
        )
        assert error.original_exception == original

    def test_error_to_dict(self):
        """Test converting error to dictionary."""
        error = PipelineError(
            "Test error",
            error_code=ErrorCode.VALIDATION_INVALID_INPUT,
            details={"field": "test"},
            recovery_suggestion="Fix it",
        )
        error_dict = error.to_dict()

        assert error_dict["error"] == "PipelineError"
        assert error_dict["message"] == "Test error"
        assert error_dict["error_code"] == ErrorCode.VALIDATION_INVALID_INPUT.value
        assert error_dict["details"] == {"field": "test"}
        assert error_dict["recovery_suggestion"] == "Fix it"


class TestNetworkError:
    """Tests for NetworkError."""

    def test_network_error_creation(self):
        """Test creating network error."""
        error = NetworkError("Connection failed")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.NETWORK_CONNECTION_FAILED
        assert "network connection" in error.recovery_suggestion.lower()

    def test_network_timeout_error(self):
        """Test network timeout error."""
        error = NetworkError(
            "Request timeout",
            error_code=ErrorCode.NETWORK_TIMEOUT,
        )
        assert error.error_code == ErrorCode.NETWORK_TIMEOUT


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_creation(self):
        """Test creating validation error."""
        error = ValidationError("Invalid input")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.VALIDATION_INVALID_INPUT
        assert "input data" in error.recovery_suggestion.lower()

    def test_validation_error_with_field(self):
        """Test validation error with field name."""
        error = ValidationError(
            "Invalid email format",
            field_name="email",
        )
        assert error.details["field_name"] == "email"


class TestLLMError:
    """Tests for LLM errors."""

    def test_llm_error_creation(self):
        """Test creating LLM error."""
        error = LLMError("API call failed")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.LLM_API_ERROR

    def test_llm_error_with_provider(self):
        """Test LLM error with provider info."""
        error = LLMError(
            "API call failed",
            provider="openai",
            model="gpt-4",
        )
        assert error.details["provider"] == "openai"
        assert error.details["model"] == "gpt-4"

    def test_rate_limit_error(self):
        """Test rate limit error."""
        error = RateLimitError(retry_after=60)
        assert isinstance(error, LLMError)
        assert error.error_code == ErrorCode.LLM_RATE_LIMIT
        assert error.details["retry_after"] == 60
        assert "60" in error.recovery_suggestion

    def test_quota_exceeded_error(self):
        """Test quota exceeded error."""
        error = QuotaExceededError(provider="anthropic")
        assert isinstance(error, LLMError)
        assert error.error_code == ErrorCode.LLM_QUOTA_EXCEEDED
        assert error.details["provider"] == "anthropic"


class TestPipelineStateError:
    """Tests for PipelineStateError."""

    def test_pipeline_state_error_creation(self):
        """Test creating pipeline state error."""
        error = PipelineStateError("State corrupted")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.PIPELINE_STATE_CORRUPTED

    def test_pipeline_state_error_with_stage(self):
        """Test pipeline state error with stage."""
        error = PipelineStateError(
            "Invalid stage transition",
            stage="level2_technique",
        )
        assert error.details["stage"] == "level2_technique"


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_authentication_error_creation(self):
        """Test creating authentication error."""
        error = AuthenticationError("Invalid token")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.AUTH_INVALID_TOKEN


class TestCheckpointError:
    """Tests for CheckpointError."""

    def test_checkpoint_error_creation(self):
        """Test creating checkpoint error."""
        error = CheckpointError("Failed to save checkpoint")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.CHECKPOINT_SAVE_FAILED

    def test_checkpoint_error_with_id(self):
        """Test checkpoint error with ID."""
        error = CheckpointError(
            "Checkpoint not found",
            checkpoint_id="abc-123",
        )
        assert error.details["checkpoint_id"] == "abc-123"


class TestGraphExecutionError:
    """Tests for GraphExecutionError."""

    def test_graph_execution_error_creation(self):
        """Test creating graph execution error."""
        error = GraphExecutionError("Node execution failed")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.GRAPH_EXECUTION_FAILED

    def test_graph_execution_error_with_node(self):
        """Test graph execution error with node info."""
        error = GraphExecutionError(
            "Node failed",
            node_name="analyze_problem",
            graph_name="main_graph",
        )
        assert error.details["node_name"] == "analyze_problem"
        assert error.details["graph_name"] == "main_graph"


class TestAgentPoolError:
    """Tests for AgentPoolError."""

    def test_agent_pool_error_creation(self):
        """Test creating agent pool error."""
        error = AgentPoolError("Pool exhausted")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.AGENT_POOL_EXHAUSTED

    def test_agent_pool_error_with_pool_name(self):
        """Test agent pool error with pool name."""
        error = AgentPoolError(
            "No available agents",
            pool_name="functional_pool",
        )
        assert error.details["pool_name"] == "functional_pool"


class TestHumanApprovalError:
    """Tests for HumanApprovalError."""

    def test_human_approval_error_creation(self):
        """Test creating human approval error."""
        error = HumanApprovalError("Approval timeout")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.APPROVAL_TIMEOUT

    def test_human_approval_error_with_gate(self):
        """Test human approval error with gate name."""
        error = HumanApprovalError(
            "Approval rejected",
            gate_name="paradigm_gate",
        )
        assert error.details["gate_name"] == "paradigm_gate"


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_configuration_error_creation(self):
        """Test creating configuration error."""
        error = ConfigurationError("Invalid configuration")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.CONFIG_INVALID

    def test_configuration_error_with_key(self):
        """Test configuration error with key."""
        error = ConfigurationError(
            "Missing required config",
            config_key="api_key",
        )
        assert error.details["config_key"] == "api_key"


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_timeout_error_creation(self):
        """Test creating timeout error."""
        error = TimeoutError("Operation timeout")
        assert isinstance(error, PipelineError)
        assert error.error_code == ErrorCode.NETWORK_TIMEOUT

    def test_timeout_error_with_details(self):
        """Test timeout error with details."""
        error = TimeoutError(
            "LLM call timeout",
            timeout_seconds=30,
            operation="llm_call",
        )
        assert error.details["timeout_seconds"] == 30
        assert error.details["operation"] == "llm_call"


class TestErrorCode:
    """Tests for ErrorCode enum."""

    def test_error_code_values(self):
        """Test error code enum values."""
        assert ErrorCode.NETWORK_CONNECTION_FAILED.value == "NETWORK_1001"
        assert ErrorCode.VALIDATION_INVALID_INPUT.value == "VALIDATION_2001"
        assert ErrorCode.LLM_API_ERROR.value == "LLM_3001"
        assert ErrorCode.PIPELINE_STATE_CORRUPTED.value == "PIPELINE_4001"
        assert ErrorCode.AUTH_INVALID_TOKEN.value == "AUTH_5001"

    def test_error_code_categories(self):
        """Test error codes are properly categorized."""
        # Network errors start with NETWORK_
        assert ErrorCode.NETWORK_CONNECTION_FAILED.value.startswith("NETWORK_")
        assert ErrorCode.NETWORK_TIMEOUT.value.startswith("NETWORK_")

        # Validation errors start with VALIDATION_
        assert ErrorCode.VALIDATION_INVALID_INPUT.value.startswith("VALIDATION_")
        assert ErrorCode.VALIDATION_SCHEMA_MISMATCH.value.startswith("VALIDATION_")

        # LLM errors start with LLM_
        assert ErrorCode.LLM_API_ERROR.value.startswith("LLM_")
        assert ErrorCode.LLM_RATE_LIMIT.value.startswith("LLM_")
