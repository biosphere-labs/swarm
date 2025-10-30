"""
Tests for error handlers.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from unittest.mock import Mock, MagicMock

from decomposition_pipeline.errors.exceptions import (
    PipelineError,
    NetworkError,
    ValidationError,
    LLMError,
    RateLimitError,
    ErrorCode,
)
from decomposition_pipeline.errors.handlers import (
    get_http_status,
    get_error_code,
    create_error_response,
    pipeline_error_handler,
    validation_error_handler,
    http_exception_handler,
    general_exception_handler,
    register_error_handlers,
)
from fastapi import status


class TestGetHttpStatus:
    """Tests for get_http_status function."""

    def test_validation_error_status(self):
        """Test HTTP status for validation error."""
        error = ValidationError("Invalid input")
        assert get_http_status(error) == status.HTTP_400_BAD_REQUEST

    def test_rate_limit_error_status(self):
        """Test HTTP status for rate limit error."""
        error = RateLimitError()
        assert get_http_status(error) == status.HTTP_429_TOO_MANY_REQUESTS

    def test_network_error_status(self):
        """Test HTTP status for network error."""
        error = NetworkError("Connection failed")
        assert get_http_status(error) == status.HTTP_502_BAD_GATEWAY

    def test_generic_pipeline_error_status(self):
        """Test HTTP status for generic pipeline error."""
        error = PipelineError("Something went wrong")
        assert get_http_status(error) == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_unknown_error_status(self):
        """Test HTTP status for unknown error."""
        error = Exception("Unknown error")
        assert get_http_status(error) == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestGetErrorCode:
    """Tests for get_error_code function."""

    def test_pipeline_error_code(self):
        """Test extracting error code from pipeline error."""
        error = ValidationError("Invalid input")
        code = get_error_code(error)
        assert code == ErrorCode.VALIDATION_INVALID_INPUT.value

    def test_unknown_error_code(self):
        """Test error code for unknown error."""
        error = Exception("Unknown error")
        code = get_error_code(error)
        assert code == ErrorCode.UNKNOWN_ERROR.value


class TestCreateErrorResponse:
    """Tests for create_error_response function."""

    def test_basic_error_response(self):
        """Test creating basic error response."""
        error = PipelineError("Test error")
        response = create_error_response(error)

        assert response["success"] is False
        assert response["error"]["type"] == "PipelineError"
        assert response["error"]["message"] == "Test error"
        assert response["error"]["code"] == ErrorCode.INTERNAL_ERROR.value

    def test_error_response_with_details(self):
        """Test error response with details."""
        error = ValidationError(
            "Invalid input",
            details={"field": "email"},
            recovery_suggestion="Use valid email format",
        )
        response = create_error_response(error)

        assert response["error"]["details"] == {"field": "email"}
        assert response["error"]["recovery_suggestion"] == "Use valid email format"

    def test_error_response_with_request_id(self):
        """Test error response with request ID."""
        error = PipelineError("Test error")
        response = create_error_response(error, request_id="req-123")

        assert response["request_id"] == "req-123"

    def test_error_response_with_traceback(self):
        """Test error response with traceback in debug mode."""
        error = PipelineError("Test error")
        response = create_error_response(error, include_traceback=True)

        assert "traceback" in response["error"]

    def test_unknown_error_response(self):
        """Test creating response for unknown error."""
        error = ValueError("Unknown error")
        response = create_error_response(error)

        assert response["success"] is False
        assert response["error"]["type"] == "ValueError"
        assert response["error"]["message"] == "Unknown error"


@pytest.mark.asyncio
class TestErrorHandlers:
    """Tests for async error handlers."""

    async def test_pipeline_error_handler(self):
        """Test pipeline error handler."""
        error = PipelineError("Test error")
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.headers.get.return_value = "req-123"

        response = await pipeline_error_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_validation_error_handler(self):
        """Test validation error handler."""
        # Create a mock validation error
        validation_error = RequestValidationError(
            errors=[{"loc": ["body", "email"], "msg": "invalid email", "type": "value_error"}]
        )
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.headers.get.return_value = "req-123"

        response = await validation_error_handler(request, validation_error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_http_exception_handler(self):
        """Test HTTP exception handler."""
        error = StarletteHTTPException(status_code=404, detail="Not found")
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.headers.get.return_value = "req-123"

        response = await http_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404

    async def test_general_exception_handler(self):
        """Test general exception handler."""
        error = ValueError("Unexpected error")
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.headers.get.return_value = "req-123"

        response = await general_exception_handler(request, error)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestRegisterErrorHandlers:
    """Tests for register_error_handlers function."""

    def test_register_error_handlers(self):
        """Test registering error handlers with FastAPI app."""
        app = FastAPI()

        # Mock the add_exception_handler method
        app.add_exception_handler = Mock()

        register_error_handlers(app)

        # Verify handlers were registered
        assert app.add_exception_handler.call_count >= 4


class TestErrorHandlerIntegration:
    """Integration tests for error handlers."""

    def test_pipeline_error_serialization(self):
        """Test complete pipeline error serialization."""
        original_error = ValueError("Original issue")
        pipeline_error = LLMError(
            "API call failed",
            error_code=ErrorCode.LLM_API_ERROR,
            details={"provider": "openai", "model": "gpt-4"},
            recovery_suggestion="Check API credentials",
            original_exception=original_error,
        )

        response = create_error_response(pipeline_error, request_id="req-123")

        assert response["success"] is False
        assert response["request_id"] == "req-123"
        assert response["error"]["type"] == "LLMError"
        assert response["error"]["message"] == "API call failed"
        assert response["error"]["code"] == ErrorCode.LLM_API_ERROR.value
        assert response["error"]["details"]["provider"] == "openai"
        assert response["error"]["details"]["model"] == "gpt-4"
        assert response["error"]["recovery_suggestion"] == "Check API credentials"
        assert response["error"]["original_error"] == "Original issue"

    def test_error_code_to_http_status_mapping(self):
        """Test mapping of error codes to HTTP status codes."""
        test_cases = [
            (ValidationError("Invalid"), status.HTTP_400_BAD_REQUEST),
            (RateLimitError(), status.HTTP_429_TOO_MANY_REQUESTS),
            (NetworkError("Failed"), status.HTTP_502_BAD_GATEWAY),
            (PipelineError("Error"), status.HTTP_500_INTERNAL_SERVER_ERROR),
        ]

        for error, expected_status in test_cases:
            assert get_http_status(error) == expected_status
