"""
Tests for approval action handlers.
"""

import pytest
from backend.src.decomposition_pipeline.hitl.actions import (
    ApprovalActionHandler,
    process_gate_response
)
from backend.src.decomposition_pipeline.hitl.types import GateResponse
import time


class TestApprovalActionHandler:
    """Test suite for ApprovalActionHandler class."""

    def test_init(self):
        """Test handler initialization."""
        handler = ApprovalActionHandler()
        assert handler.checkpointer is None

        mock_checkpointer = object()
        handler = ApprovalActionHandler(checkpointer=mock_checkpointer)
        assert handler.checkpointer is mock_checkpointer

    def test_handle_approve(self):
        """Test approve action handling."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "approve",
            "reviewer": "test_user",
            "notes": "Looks good",
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {"current_stage": "level_1"}
        result = handler.handle_approve(response, state)

        # State should be unchanged
        assert result == state

    def test_handle_reject(self):
        """Test reject action handling."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "reject",
            "reviewer": "test_user",
            "notes": "Please reconsider",
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {"current_stage": "level_2_technique_selection"}
        result = handler.handle_reject(response, state)

        assert result["_backtrack_requested"] is True
        assert result["_backtrack_reason"] == "Please reconsider"
        assert result["_backtrack_to_stage"] == "level_1_paradigm_selection"

    def test_handle_modify(self):
        """Test modify action handling."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "modify",
            "reviewer": "test_user",
            "notes": "Changed paradigm",
            "modifications": {
                "selected_paradigms": ["temporal", "functional"],
                "paradigm_scores.temporal": 0.9
            },
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {
            "selected_paradigms": ["structural"],
            "paradigm_scores": {"structural": 0.8}
        }

        result = handler.handle_modify(response, state)

        assert result["selected_paradigms"] == ["temporal", "functional"]
        assert result["paradigm_scores"]["temporal"] == 0.9
        assert "_modification_history" in result
        assert len(result["_modification_history"]) == 1

    def test_handle_modify_no_modifications(self):
        """Test modify action with no modifications (treats as approve)."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "modify",
            "reviewer": "test_user",
            "notes": None,
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {"current_stage": "level_1"}
        result = handler.handle_modify(response, state)

        # Should be same as approve
        assert result == state

    def test_handle_backtrack(self):
        """Test backtrack action handling."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "backtrack",
            "reviewer": "test_user",
            "notes": "Go back to problem ingestion",
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": "problem_ingestion"
        }

        state = {"current_stage": "level_3_decomposition"}
        result = handler.handle_backtrack(response, state)

        assert result["_backtrack_requested"] is True
        assert result["_backtrack_to_stage"] == "problem_ingestion"
        assert result["_backtrack_reason"] == "Go back to problem ingestion"

    def test_handle_backtrack_no_target(self):
        """Test backtrack without specific target (goes to previous)."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "backtrack",
            "reviewer": "test_user",
            "notes": "Go back",
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {"current_stage": "level_2_technique_selection"}
        result = handler.handle_backtrack(response, state)

        assert result["_backtrack_requested"] is True
        # Should backtrack to previous stage
        assert result["_backtrack_to_stage"] == "level_1_paradigm_selection"

    def test_handle_add_context(self):
        """Test add_context action handling."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "add_context",
            "reviewer": "test_user",
            "notes": "Adding domain knowledge",
            "modifications": None,
            "selected_alternative": None,
            "additional_context": "The system must handle real-time constraints",
            "backtrack_to": None
        }

        state = {
            "current_stage": "level_1_paradigm_selection",
            "problem_characteristics": {}
        }

        result = handler.handle_add_context(response, state)

        assert "human_context" in result
        assert len(result["human_context"]) == 1
        assert result["human_context"][0]["context"] == "The system must handle real-time constraints"
        assert result["_rerun_current_stage"] is True

        # Context should also be added to problem characteristics
        assert "human_insights" in result["problem_characteristics"]

    def test_handle_add_context_no_context(self):
        """Test add_context with no context (treats as approve)."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "add_context",
            "reviewer": "test_user",
            "notes": None,
            "modifications": None,
            "selected_alternative": None,
            "additional_context": "",
            "backtrack_to": None
        }

        state = {"current_stage": "level_1"}
        result = handler.handle_add_context(response, state)

        assert result == state

    def test_handle_request_alternatives(self):
        """Test request_alternatives action handling."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "request_alternatives",
            "reviewer": "test_user",
            "notes": "Want to see more options",
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {
            "current_stage": "level_1_paradigm_selection",
            "selected_paradigms": ["structural"]
        }

        result = handler.handle_request_alternatives(response, state)

        assert result["_generate_alternatives"] is True
        assert result["_alternative_count"] == 3  # default
        assert result["_primary_paradigms"] == ["structural"]

    def test_handle_action_dispatch(self):
        """Test action dispatching."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "approve",
            "reviewer": "test_user",
            "notes": None,
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {"current_stage": "level_1"}
        result = handler.handle_action("approve", response, state)

        assert result == state

    def test_handle_action_unknown(self):
        """Test handling unknown action."""
        handler = ApprovalActionHandler()

        response: GateResponse = {
            "action": "unknown_action",
            "reviewer": "test_user",
            "notes": None,
            "modifications": None,
            "selected_alternative": None,
            "additional_context": None,
            "backtrack_to": None
        }

        state = {"current_stage": "level_1"}

        with pytest.raises(ValueError, match="Unknown approval action"):
            handler.handle_action("unknown_action", response, state)

    def test_get_previous_stage(self):
        """Test previous stage determination."""
        handler = ApprovalActionHandler()

        assert handler._get_previous_stage("level_2_technique_selection") == "level_1_paradigm_selection"
        assert handler._get_previous_stage("level_3_decomposition") == "level_2_technique_selection"
        assert handler._get_previous_stage("problem_ingestion") == "problem_ingestion"
        assert handler._get_previous_stage("unknown_stage") == "problem_ingestion"

    def test_set_nested_value(self):
        """Test setting nested values in state."""
        handler = ApprovalActionHandler()

        state = {"paradigm_scores": {"structural": 0.5}}

        handler._set_nested_value(state, "paradigm_scores.temporal", 0.9)
        assert state["paradigm_scores"]["temporal"] == 0.9

        handler._set_nested_value(state, "new_key.nested.deep", "value")
        assert state["new_key"]["nested"]["deep"] == "value"

    def test_create_approval_summary(self):
        """Test creating approval summary."""
        handler = ApprovalActionHandler()

        state = {
            "human_approvals": [
                {
                    "gate_name": "paradigm_selection",
                    "timestamp": 1.0,
                    "action": "approve",
                    "reviewer": "user1",
                    "notes": None,
                    "modifications": None
                },
                {
                    "gate_name": "technique_selection",
                    "timestamp": 2.0,
                    "action": "modify",
                    "reviewer": "user2",
                    "notes": "Changed technique",
                    "modifications": {"technique": "new"}
                },
                {
                    "gate_name": "decomposition_review",
                    "timestamp": 3.0,
                    "action": "reject",
                    "reviewer": "user1",
                    "notes": "Rejected",
                    "modifications": None
                }
            ]
        }

        summary = handler.create_approval_summary(state)

        assert summary["total_approvals"] == 3
        assert summary["actions_by_type"]["approve"] == 1
        assert summary["actions_by_type"]["modify"] == 1
        assert summary["actions_by_type"]["reject"] == 1
        assert "user1" in summary["reviewers"]
        assert "user2" in summary["reviewers"]
        assert "paradigm_selection" in summary["gates_activated"]
        assert summary["modifications_count"] == 1
        assert summary["backtrack_count"] == 1
        assert len(summary["timeline"]) == 3


class TestProcessGateResponse:
    """Test suite for process_gate_response function."""

    def test_process_gate_response(self):
        """Test processing gate response from state."""
        state = {
            "current_stage": "level_1",
            "_pending_gate_response": {
                "action": "approve",
                "reviewer": "test_user",
                "notes": None,
                "modifications": None,
                "selected_alternative": None,
                "additional_context": None,
                "backtrack_to": None
            }
        }

        result = process_gate_response(state)

        # Pending response should be removed
        assert "_pending_gate_response" not in result

    def test_process_gate_response_no_pending(self):
        """Test processing when no pending response."""
        state = {"current_stage": "level_1"}

        result = process_gate_response(state)

        # State should be unchanged
        assert result == state

    def test_process_gate_response_with_modifications(self):
        """Test processing response with modifications."""
        state = {
            "current_stage": "level_1",
            "selected_paradigms": ["structural"],
            "_pending_gate_response": {
                "action": "modify",
                "reviewer": "test_user",
                "notes": "Changed",
                "modifications": {
                    "selected_paradigms": ["temporal"]
                },
                "selected_alternative": None,
                "additional_context": None,
                "backtrack_to": None
            }
        }

        result = process_gate_response(state)

        assert result["selected_paradigms"] == ["temporal"]
        assert "_modification_history" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
