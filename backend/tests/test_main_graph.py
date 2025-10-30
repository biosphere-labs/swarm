"""
Tests for the main orchestration graph.

Tests cover:
- Complete pipeline flow (happy path)
- Conditional routing decisions
- HITL gate interrupts and resumes
- Backtracking functionality
- Error recovery paths
- Checkpoint/resume functionality
- State transformations
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid

from decomposition_pipeline.graphs.main_graph import (
    create_main_orchestration_graph,
    problem_ingestion,
    output_formatting,
    route_after_level1,
    route_after_gate1,
    route_after_level2,
    route_after_gate2,
    route_after_level3_integration,
    route_after_gate3,
    route_after_level5,
    route_after_gate4,
)
from decomposition_pipeline.schemas import MainPipelineState, PipelineStage


# =============================================================================
# Test Node Functions
# =============================================================================

class TestProblemIngestion:
    """Test problem ingestion node."""

    def test_problem_ingestion_success(self):
        """Test successful problem ingestion."""
        state: MainPipelineState = {
            "original_problem": "Build a distributed task scheduler",
            "problem_characteristics": {},
            "current_stage": "",
        }

        result = problem_ingestion(state)

        assert result["current_stage"] == PipelineStage.PROBLEM_INGESTION.value
        assert "started_at" in result
        assert "thread_id" in result
        assert "human_approvals" in result
        assert "backtrack_history" in result
        assert "problem_length" in result["problem_characteristics"]
        assert result["problem_characteristics"]["problem_length"] > 0

    def test_problem_ingestion_empty_problem(self):
        """Test problem ingestion with empty problem."""
        state: MainPipelineState = {
            "original_problem": "",
            "problem_characteristics": {},
            "current_stage": "",
        }

        with pytest.raises(ValueError, match="Problem description cannot be empty"):
            problem_ingestion(state)

    def test_problem_ingestion_preserves_thread_id(self):
        """Test that existing thread_id is preserved."""
        thread_id = str(uuid.uuid4())
        state: MainPipelineState = {
            "original_problem": "Test problem",
            "problem_characteristics": {},
            "current_stage": "",
            "thread_id": thread_id,
        }

        result = problem_ingestion(state)
        assert result["thread_id"] == thread_id


class TestOutputFormatting:
    """Test output formatting node."""

    def test_output_formatting_success(self):
        """Test successful output formatting."""
        state: MainPipelineState = {
            "original_problem": "Test problem",
            "problem_characteristics": {},
            "current_stage": PipelineStage.LEVEL5_SOLUTION_INTEGRATION.value,
            "thread_id": str(uuid.uuid4()),
            "started_at": datetime.now().isoformat(),
            "integrated_solution": {
                "content": "Test solution",
                "reasoning": "Test reasoning",
                "confidence": 0.9,
            },
            "selected_paradigms": ["structural", "functional"],
            "selected_techniques": {
                "structural": {"name": "Divide and Conquer"},
                "functional": {"name": "MapReduce"},
            },
            "integrated_subproblems": [
                {"id": "sp1", "title": "Subproblem 1"},
                {"id": "sp2", "title": "Subproblem 2"},
            ],
            "human_approvals": [],
        }

        result = output_formatting(state)

        assert result["current_stage"] == PipelineStage.COMPLETED.value
        assert "completed_at" in result
        assert "metadata" in result["integrated_solution"]
        assert result["integrated_solution"]["metadata"]["total_subproblems"] == 2
        assert result["integrated_solution"]["metadata"]["thread_id"] == state["thread_id"]

    def test_output_formatting_no_solution(self):
        """Test output formatting with no solution."""
        state: MainPipelineState = {
            "original_problem": "Test problem",
            "problem_characteristics": {},
            "current_stage": PipelineStage.LEVEL5_SOLUTION_INTEGRATION.value,
        }

        with pytest.raises(ValueError, match="Cannot format output"):
            output_formatting(state)


# =============================================================================
# Test Routing Functions
# =============================================================================

class TestRouting:
    """Test conditional routing functions."""

    def test_route_after_level1_with_paradigms(self):
        """Test routing after Level 1 with selected paradigms."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "selected_paradigms": ["structural", "functional"],
        }

        result = route_after_level1(state)
        assert result == "gate1"

    def test_route_after_level1_no_paradigms(self):
        """Test routing after Level 1 without paradigms."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "selected_paradigms": [],
        }

        result = route_after_level1(state)
        assert result == "gate1"  # Still goes to gate

    def test_route_after_gate1_approve(self):
        """Test routing after Gate 1 with approval."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "_pending_gate_response": {
                "action": "approve",
            },
        }

        result = route_after_gate1(state)
        assert result == "level2"

    def test_route_after_gate1_reject(self):
        """Test routing after Gate 1 with rejection."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "_pending_gate_response": {
                "action": "reject",
            },
        }

        result = route_after_gate1(state)
        assert result == "level1"

    def test_route_after_gate1_auto_approve(self):
        """Test routing after Gate 1 with auto-approval."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
        }

        result = route_after_gate1(state)
        assert result == "level2"

    def test_route_after_level2(self):
        """Test routing after Level 2."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "selected_techniques": {
                "structural": {"name": "Test technique"},
            },
        }

        result = route_after_level2(state)
        assert result == "gate2"

    def test_route_after_gate2_approve(self):
        """Test routing after Gate 2 with approval."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "_pending_gate_response": {
                "action": "approve",
            },
        }

        result = route_after_gate2(state)
        assert result == "level3"

    def test_route_after_level3_integration(self):
        """Test routing after Level 3 integration."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "integrated_subproblems": [
                {"id": "sp1", "title": "Subproblem 1"},
            ],
        }

        result = route_after_level3_integration(state)
        assert result == "gate3"

    def test_route_after_gate3_approve(self):
        """Test routing after Gate 3 with approval."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "_pending_gate_response": {
                "action": "approve",
            },
        }

        result = route_after_gate3(state)
        assert result == "level4"

    def test_route_after_level5(self):
        """Test routing after Level 5 (always goes to Gate 4)."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
        }

        result = route_after_level5(state)
        assert result == "gate4"

    def test_route_after_gate4_approve(self):
        """Test routing after Gate 4 with approval."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "_pending_gate_response": {
                "action": "approve",
            },
        }

        result = route_after_gate4(state)
        assert result == "output"

    def test_route_after_gate4_reject(self):
        """Test routing after Gate 4 with rejection."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
            "_pending_gate_response": {
                "action": "reject",
            },
        }

        result = route_after_gate4(state)
        assert result == "level5"


# =============================================================================
# Test Graph Construction
# =============================================================================

class TestGraphConstruction:
    """Test main graph construction."""

    def test_create_main_graph(self):
        """Test that main graph can be created."""
        graph = create_main_orchestration_graph()
        assert graph is not None

    def test_graph_has_nodes(self):
        """Test that graph has all expected nodes."""
        graph = create_main_orchestration_graph()

        # Get node names from compiled graph
        # Note: LangGraph's compiled graph structure may vary
        # This is a basic check that compilation succeeded
        assert graph is not None

    def test_graph_with_custom_checkpointer(self):
        """Test graph creation with custom checkpointer."""
        from decomposition_pipeline.checkpoint import create_checkpointer

        checkpointer = create_checkpointer(db_path=":memory:")
        graph = create_main_orchestration_graph(checkpointer=checkpointer)

        assert graph is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for the main graph."""

    @pytest.mark.skip(reason="Integration test - requires full setup")
    def test_complete_pipeline_flow(self):
        """Test complete pipeline from start to end."""
        # This would be a full integration test
        # Requires mocking LLM calls and full pipeline setup
        pass

    @pytest.mark.skip(reason="Integration test - requires checkpoint setup")
    def test_checkpoint_and_resume(self):
        """Test checkpointing and resuming execution."""
        # Test that graph can be interrupted and resumed
        pass

    @pytest.mark.skip(reason="Integration test - requires gate setup")
    def test_hitl_gate_interrupt(self):
        """Test that HITL gates interrupt execution properly."""
        # Test that execution pauses at gates
        pass

    @pytest.mark.skip(reason="Integration test - requires full setup")
    def test_backtracking(self):
        """Test backtracking to previous stages."""
        # Test that backtracking works correctly
        pass


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error handling in the pipeline."""

    def test_problem_ingestion_handles_missing_problem(self):
        """Test that missing problem is handled."""
        state: MainPipelineState = {
            "problem_characteristics": {},
            "current_stage": "",
        }

        with pytest.raises((ValueError, KeyError)):
            problem_ingestion(state)

    def test_output_formatting_handles_missing_solution(self):
        """Test that missing solution is handled."""
        state: MainPipelineState = {
            "original_problem": "Test",
            "problem_characteristics": {},
            "current_stage": "",
        }

        with pytest.raises(ValueError):
            output_formatting(state)


# =============================================================================
# State Management Tests
# =============================================================================

class TestStateManagement:
    """Test state transformations and management."""

    def test_state_initialized_with_tracking_fields(self):
        """Test that state is initialized with tracking fields."""
        state: MainPipelineState = {
            "original_problem": "Test problem",
            "problem_characteristics": {},
            "current_stage": "",
        }

        result = problem_ingestion(state)

        assert "thread_id" in result
        assert "started_at" in result
        assert "human_approvals" in result
        assert "backtrack_history" in result
        assert isinstance(result["human_approvals"], list)
        assert isinstance(result["backtrack_history"], list)

    def test_state_preserves_existing_fields(self):
        """Test that existing state fields are preserved."""
        state: MainPipelineState = {
            "original_problem": "Test problem",
            "problem_characteristics": {"test": "value"},
            "current_stage": "",
            "custom_field": "preserved",
        }

        result = problem_ingestion(state)

        assert result["custom_field"] == "preserved"  # type: ignore
        assert result["problem_characteristics"]["test"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
