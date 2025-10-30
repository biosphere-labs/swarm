"""
Tests for Human-in-the-Loop approval gate implementation.
"""

import pytest
from unittest.mock import Mock, patch
from backend.src.decomposition_pipeline.hitl.approval_gate import (
    HumanApprovalGate,
    create_approval_gates
)
from backend.src.decomposition_pipeline.hitl.types import ApprovalRecord


class TestHumanApprovalGate:
    """Test suite for HumanApprovalGate class."""

    def test_init(self):
        """Test gate initialization."""
        gate = HumanApprovalGate(
            gate_name="test_gate",
            gate_level=1,
            required=True,
            description="Test gate"
        )

        assert gate.gate_name == "test_gate"
        assert gate.gate_level == 1
        assert gate.required is True
        assert gate.description == "Test gate"

    def test_should_request_approval_required_gate(self):
        """Test that required gates always request approval."""
        gate = HumanApprovalGate(
            gate_name="final_solution",
            gate_level=4,
            required=True
        )

        state = {"paradigm_scores": {"structural": 0.99}}
        config = {}

        assert gate.should_request_approval(state, config) is True

    def test_should_request_approval_disabled_gate(self):
        """Test that disabled gates skip approval."""
        gate = HumanApprovalGate(
            gate_name="paradigm_selection",
            gate_level=1,
            required=False
        )

        state = {"paradigm_scores": {"structural": 0.5}}
        config = {
            "approval_gates": {
                "paradigm_selection": {
                    "enabled": False
                }
            }
        }

        assert gate.should_request_approval(state, config) is False

    def test_should_request_approval_high_confidence(self):
        """Test auto-approval with high confidence scores."""
        gate = HumanApprovalGate(
            gate_name="paradigm_selection",
            gate_level=1,
            required=False
        )

        state = {"paradigm_scores": {"structural": 0.98}}
        config = {
            "approval_gates": {
                "paradigm_selection": {
                    "enabled": True,
                    "auto_approve_threshold": 0.95
                }
            }
        }

        assert gate.should_request_approval(state, config) is False

    def test_should_request_approval_low_confidence(self):
        """Test that low confidence triggers approval request."""
        gate = HumanApprovalGate(
            gate_name="paradigm_selection",
            gate_level=1,
            required=False
        )

        state = {"paradigm_scores": {"structural": 0.6}}
        config = {
            "approval_gates": {
                "paradigm_selection": {
                    "enabled": True,
                    "auto_approve_threshold": 0.95
                }
            }
        }

        assert gate.should_request_approval(state, config) is True

    def test_prepare_review_data_level_1(self):
        """Test review data preparation for Level 1 (paradigm selection)."""
        gate = HumanApprovalGate(
            gate_name="paradigm_selection",
            gate_level=1
        )

        state = {
            "selected_paradigms": ["structural", "functional"],
            "paradigm_scores": {
                "structural": 0.85,
                "functional": 0.78,
                "temporal": 0.45
            },
            "paradigm_reasoning": {
                "structural": "Clear component structure",
                "functional": "Well-defined operations"
            },
            "problem_characteristics": {
                "complexity": "high",
                "size": "large"
            }
        }

        review_data = gate.prepare_review_data(state)

        assert review_data["gate"] == "paradigm_selection"
        assert review_data["stage"] == "Level 1"
        assert "approve" in review_data["options"]
        assert "selected_paradigms" in review_data["state_snapshot"]
        assert review_data["state_snapshot"]["selected_paradigms"] == ["structural", "functional"]
        assert "temporal" in review_data["state_snapshot"]["rejected_paradigms"]

    def test_prepare_review_data_level_2(self):
        """Test review data preparation for Level 2 (technique selection)."""
        gate = HumanApprovalGate(
            gate_name="technique_selection",
            gate_level=2
        )

        state = {
            "selected_techniques": {
                "structural": {"name": "Divide and Conquer", "score": 0.91}
            },
            "technique_scores": {"structural": 0.91},
            "technique_justification": {
                "structural": "Problem is divisible with independent subproblems"
            },
            "selected_paradigms": ["structural"]
        }

        review_data = gate.prepare_review_data(state)

        assert review_data["gate"] == "technique_selection"
        assert "selected_techniques" in review_data["state_snapshot"]
        assert "technique_justification" in review_data["state_snapshot"]

    def test_prepare_review_data_level_3(self):
        """Test review data preparation for Level 3 (decomposition review)."""
        gate = HumanApprovalGate(
            gate_name="decomposition_review",
            gate_level=3
        )

        state = {
            "integrated_subproblems": [
                {"id": "sp1", "title": "Subproblem 1"},
                {"id": "sp2", "title": "Subproblem 2"}
            ],
            "subproblem_dependencies": {"sp2": ["sp1"]},
            "validation_results": {"completeness_score": 0.95}
        }

        review_data = gate.prepare_review_data(state)

        assert review_data["gate"] == "decomposition_review"
        assert len(review_data["state_snapshot"]["integrated_subproblems"]) == 2
        assert "validation_results" in review_data["state_snapshot"]

    def test_prepare_review_data_level_4(self):
        """Test review data preparation for Level 4 (final solution)."""
        gate = HumanApprovalGate(
            gate_name="final_solution",
            gate_level=4
        )

        state = {
            "integrated_solution": {"description": "Final solution"},
            "validation_results": {"coherence": 0.98},
            "partial_solutions": {"sp1": "Solution 1"}
        }

        review_data = gate.prepare_review_data(state)

        assert review_data["gate"] == "final_solution"
        assert "integrated_solution" in review_data["state_snapshot"]

    @patch('backend.src.decomposition_pipeline.hitl.approval_gate.interrupt')
    def test_call_auto_approve(self, mock_interrupt):
        """Test gate execution with auto-approval."""
        gate = HumanApprovalGate(
            gate_name="paradigm_selection",
            gate_level=1,
            required=False
        )

        state = {"paradigm_scores": {"structural": 0.98}}
        config = {
            "approval_gates": {
                "paradigm_selection": {
                    "enabled": True,
                    "auto_approve_threshold": 0.95
                }
            }
        }

        result = gate(state, config)

        # Should not interrupt
        mock_interrupt.assert_not_called()

        # Should add approval record
        assert "human_approvals" in result
        assert len(result["human_approvals"]) == 1
        assert result["human_approvals"][0]["action"] == "approve"
        assert result["human_approvals"][0]["reviewer"] == "system"

    @patch('backend.src.decomposition_pipeline.hitl.approval_gate.interrupt')
    def test_call_request_approval(self, mock_interrupt):
        """Test gate execution that requests approval."""
        mock_interrupt.return_value = {
            "action": "approve",
            "reviewer": "test_user",
            "notes": "Looks good"
        }

        gate = HumanApprovalGate(
            gate_name="paradigm_selection",
            gate_level=1,
            required=False
        )

        state = {"paradigm_scores": {"structural": 0.6}}
        config = {
            "approval_gates": {
                "paradigm_selection": {
                    "enabled": True,
                    "auto_approve_threshold": 0.95
                }
            }
        }

        result = gate(state, config)

        # Should interrupt
        mock_interrupt.assert_called_once()

        # Should add approval record from response
        assert "human_approvals" in result
        assert len(result["human_approvals"]) == 1
        assert result["human_approvals"][0]["action"] == "approve"
        assert result["human_approvals"][0]["reviewer"] == "test_user"

    @patch('backend.src.decomposition_pipeline.hitl.approval_gate.interrupt')
    def test_call_with_reject_response(self, mock_interrupt):
        """Test gate execution with reject response."""
        mock_interrupt.return_value = {
            "action": "reject",
            "reviewer": "test_user",
            "notes": "Please reconsider",
            "modifications": None
        }

        gate = HumanApprovalGate(
            gate_name="technique_selection",
            gate_level=2,
            required=True
        )

        state = {"technique_scores": {"structural": 0.5}}
        config = {}

        result = gate(state, config)

        # Should have pending response
        assert "_pending_gate_response" in result
        assert result["_pending_gate_response"]["action"] == "reject"


class TestCreateApprovalGates:
    """Test suite for gate factory function."""

    def test_create_approval_gates(self):
        """Test creation of all approval gates."""
        gates = create_approval_gates()

        assert len(gates) == 4
        assert "paradigm_selection" in gates
        assert "technique_selection" in gates
        assert "decomposition_review" in gates
        assert "final_solution" in gates

    def test_gate_levels(self):
        """Test that gates have correct levels."""
        gates = create_approval_gates()

        assert gates["paradigm_selection"].gate_level == 1
        assert gates["technique_selection"].gate_level == 2
        assert gates["decomposition_review"].gate_level == 3
        assert gates["final_solution"].gate_level == 4

    def test_required_gates(self):
        """Test that final solution gate is required."""
        gates = create_approval_gates()

        assert gates["paradigm_selection"].required is False
        assert gates["technique_selection"].required is False
        assert gates["decomposition_review"].required is False
        assert gates["final_solution"].required is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
