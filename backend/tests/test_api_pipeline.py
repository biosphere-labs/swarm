"""
Tests for pipeline API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

from decomposition_pipeline.api.app import app
from decomposition_pipeline.schemas import PipelineStage


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_graph():
    """Mock LangGraph graph."""
    mock = Mock()
    mock.ainvoke = AsyncMock(return_value={
        "current_stage": PipelineStage.COMPLETED.value,
        "status": "completed",
    })
    return mock


@pytest.fixture
def mock_checkpointer():
    """Mock checkpointer."""
    mock = Mock()
    mock.get = Mock(return_value={
        "channel_values": {
            "current_stage": PipelineStage.PROBLEM_INGESTION.value,
            "original_problem": "Test problem",
            "awaiting_approval": False,
        }
    })
    mock.list = Mock(return_value=[])
    return mock


class TestStartPipeline:
    """Tests for POST /api/v1/pipeline/start"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_start_pipeline_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test successfully starting a pipeline."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        response = client.post(
            "/api/v1/pipeline/start",
            json={
                "problem": "Build a real-time chat application",
                "config": {},
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "running"
        assert data["current_stage"] == PipelineStage.PROBLEM_INGESTION.value
        assert "started_at" in data

    def test_start_pipeline_empty_problem(self, client):
        """Test starting pipeline with empty problem."""
        response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_start_pipeline_short_problem(self, client):
        """Test starting pipeline with too short problem."""
        response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "short"}
        )

        assert response.status_code == 422  # Validation error

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_start_pipeline_with_config(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test starting pipeline with custom config."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        response = client.post(
            "/api/v1/pipeline/start",
            json={
                "problem": "Build a microservices architecture",
                "config": {"max_paradigms": 2},
                "approval_gates": {
                    "paradigm": True,
                    "technique": False,
                }
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "run_id" in data


class TestGetPipelineState:
    """Tests for GET /api/v1/pipeline/{run_id}/state"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_get_state_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test getting pipeline state."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline first
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for state retrieval"}
        )
        run_id = start_response.json()["run_id"]

        # Get state
        response = client.get(f"/api/v1/pipeline/{run_id}/state")

        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == run_id
        assert "status" in data
        assert "current_stage" in data
        assert "state" in data
        assert "approval_required" in data

    def test_get_state_not_found(self, client):
        """Test getting state for non-existent run."""
        response = client.get("/api/v1/pipeline/nonexistent-run-id/state")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetPipelineHistory:
    """Tests for GET /api/v1/pipeline/{run_id}/history"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_get_history_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test getting pipeline history."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline first
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for history"}
        )
        run_id = start_response.json()["run_id"]

        # Get history
        response = client.get(f"/api/v1/pipeline/{run_id}/history")

        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == run_id
        assert "checkpoints" in data
        assert "approvals" in data
        assert "backtracks" in data

    def test_get_history_not_found(self, client):
        """Test getting history for non-existent run."""
        response = client.get("/api/v1/pipeline/nonexistent-run-id/history")

        assert response.status_code == 404


class TestApproveGate:
    """Tests for POST /api/v1/pipeline/{run_id}/approve"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_approve_gate_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test approving at gate."""
        # Setup mock to simulate awaiting approval
        mock_checkpointer.get = Mock(return_value={
            "channel_values": {
                "current_stage": PipelineStage.GATE1_PARADIGM_APPROVAL.value,
                "awaiting_approval": True,
                "current_gate": "paradigm",
                "human_approvals": [],
            }
        })
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for approval"}
        )
        run_id = start_response.json()["run_id"]

        # Approve
        response = client.post(
            f"/api/v1/pipeline/{run_id}/approve",
            json={
                "reviewer": "test_user",
                "notes": "Looks good!",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "approval" in data.get("data", {})

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_approve_gate_not_awaiting(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test approving when not awaiting approval."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem"}
        )
        run_id = start_response.json()["run_id"]

        # Try to approve when not awaiting
        response = client.post(
            f"/api/v1/pipeline/{run_id}/approve",
            json={"reviewer": "test_user"}
        )

        assert response.status_code == 409


class TestRejectGate:
    """Tests for POST /api/v1/pipeline/{run_id}/reject"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_reject_gate_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test rejecting at gate."""
        # Setup mock to simulate awaiting approval
        mock_checkpointer.get = Mock(return_value={
            "channel_values": {
                "current_stage": PipelineStage.GATE1_PARADIGM_APPROVAL.value,
                "awaiting_approval": True,
                "current_gate": "paradigm",
                "human_approvals": [],
                "backtrack_history": [],
            }
        })
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for rejection"}
        )
        run_id = start_response.json()["run_id"]

        # Reject
        response = client.post(
            f"/api/v1/pipeline/{run_id}/reject",
            json={
                "reviewer": "test_user",
                "reason": "Selected paradigms are not appropriate",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestModifyState:
    """Tests for POST /api/v1/pipeline/{run_id}/modify"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_modify_state_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test modifying pipeline state."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for modification"}
        )
        run_id = start_response.json()["run_id"]

        # Modify state
        response = client.post(
            f"/api/v1/pipeline/{run_id}/modify",
            json={
                "reviewer": "test_user",
                "modifications": {
                    "selected_paradigms": ["structural", "functional"]
                },
                "notes": "Manually adjusted paradigms",
                "continue_after": False,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestBacktrack:
    """Tests for POST /api/v1/pipeline/{run_id}/backtrack"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_backtrack_by_checkpoint(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test backtracking to checkpoint."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for backtrack"}
        )
        run_id = start_response.json()["run_id"]

        # Backtrack
        response = client.post(
            f"/api/v1/pipeline/{run_id}/backtrack",
            json={
                "reviewer": "test_user",
                "checkpoint_id": "checkpoint-123",
                "reason": "Need to revise earlier decision",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_backtrack_no_target(self, client):
        """Test backtrack without target."""
        response = client.post(
            "/api/v1/pipeline/fake-run-id/backtrack",
            json={"reviewer": "test_user"}
        )

        # Should fail validation or give 404
        assert response.status_code in [400, 404]


class TestAddContext:
    """Tests for POST /api/v1/pipeline/{run_id}/add-context"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_add_context_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test adding context."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for context"}
        )
        run_id = start_response.json()["run_id"]

        # Add context
        response = client.post(
            f"/api/v1/pipeline/{run_id}/add-context",
            json={
                "reviewer": "test_user",
                "additional_context": "This should use microservices architecture",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestCancelRun:
    """Tests for DELETE /api/v1/pipeline/{run_id}"""

    @patch("decomposition_pipeline.api.routers.pipeline.create_main_orchestration_graph")
    @patch("decomposition_pipeline.api.routers.pipeline.create_checkpointer")
    def test_cancel_run_success(self, mock_create_checkpointer, mock_create_graph, client, mock_graph, mock_checkpointer):
        """Test cancelling a run."""
        mock_create_graph.return_value = mock_graph
        mock_create_checkpointer.return_value = mock_checkpointer

        # Start a pipeline
        start_response = client.post(
            "/api/v1/pipeline/start",
            json={"problem": "Test problem for cancellation"}
        )
        run_id = start_response.json()["run_id"]

        # Cancel
        response = client.delete(f"/api/v1/pipeline/{run_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cancelled" in data["message"].lower()

    def test_cancel_nonexistent_run(self, client):
        """Test cancelling non-existent run."""
        response = client.delete("/api/v1/pipeline/nonexistent-run-id")

        assert response.status_code == 404


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["status"] == "running"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_status(self, client):
        """Test API status endpoint."""
        response = client.get("/api/v1/status")

        assert response.status_code == 200
        data = response.json()
        assert "api_version" in data
        assert "approval_gates" in data
        assert "limits" in data
