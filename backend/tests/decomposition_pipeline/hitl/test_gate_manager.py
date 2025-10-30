"""
Tests for GateManager.
"""

import pytest
from backend.src.decomposition_pipeline.hitl.gate_manager import GateManager
from backend.src.decomposition_pipeline.hitl.types import ApprovalRecord
import time


class TestGateManager:
    """Test suite for GateManager class."""

    def test_init(self):
        """Test manager initialization."""
        config = {
            "approval_gates": {
                "paradigm_selection": {"enabled": True}
            }
        }

        manager = GateManager(config)

        assert manager.config == config
        assert len(manager.gates) == 4
        assert len(manager.activation_history) == 0

    def test_get_gate(self):
        """Test retrieving gate by name."""
        manager = GateManager()

        gate = manager.get_gate("paradigm_selection")
        assert gate is not None
        assert gate.gate_name == "paradigm_selection"

        gate = manager.get_gate("nonexistent")
        assert gate is None

    def test_get_gate_config(self):
        """Test getting gate configuration."""
        config = {
            "approval_gates": {
                "paradigm_selection": {
                    "enabled": True,
                    "auto_approve_threshold": 0.9
                }
            }
        }

        manager = GateManager(config)
        gate_config = manager.get_gate_config("paradigm_selection")

        assert gate_config["name"] == "paradigm_selection"
        assert gate_config["enabled"] is True
        assert gate_config["level"] == 1
        assert gate_config["required"] is False

    def test_get_gate_config_required_gate(self):
        """Test configuration for required gate."""
        manager = GateManager()
        gate_config = manager.get_gate_config("final_solution")

        assert gate_config["required"] is True
        assert gate_config["enabled"] is True  # Required gates are always enabled

    def test_get_all_gate_configs(self):
        """Test getting all gate configurations."""
        manager = GateManager()
        configs = manager.get_all_gate_configs()

        assert len(configs) == 4
        gate_names = [c["name"] for c in configs]
        assert "paradigm_selection" in gate_names
        assert "final_solution" in gate_names

    def test_is_gate_enabled(self):
        """Test checking if gate is enabled."""
        config = {
            "approval_gates": {
                "paradigm_selection": {"enabled": True},
                "technique_selection": {"enabled": False}
            }
        }

        manager = GateManager(config)

        assert manager.is_gate_enabled("paradigm_selection") is True
        assert manager.is_gate_enabled("technique_selection") is False
        assert manager.is_gate_enabled("final_solution") is True  # Required

    def test_record_gate_activation(self):
        """Test recording gate activation."""
        manager = GateManager()

        state = {
            "current_stage": "level_1_paradigm_selection",
            "selected_paradigms": ["structural"],
            "integrated_subproblems": []
        }

        timestamp = time.time()
        manager.record_gate_activation("paradigm_selection", state, timestamp)

        assert len(manager.activation_history) == 1
        record = manager.activation_history[0]
        assert record["gate_name"] == "paradigm_selection"
        assert record["timestamp"] == timestamp
        assert record["state_snapshot"]["current_stage"] == "level_1_paradigm_selection"

    def test_get_activation_history(self):
        """Test retrieving activation history."""
        manager = GateManager()

        state1 = {"current_stage": "level_1"}
        state2 = {"current_stage": "level_2"}

        manager.record_gate_activation("paradigm_selection", state1, 1.0)
        manager.record_gate_activation("technique_selection", state2, 2.0)

        # Get all history
        all_history = manager.get_activation_history()
        assert len(all_history) == 2

        # Get filtered history
        paradigm_history = manager.get_activation_history("paradigm_selection")
        assert len(paradigm_history) == 1
        assert paradigm_history[0]["gate_name"] == "paradigm_selection"

    def test_get_approval_history(self):
        """Test retrieving approval history from state."""
        manager = GateManager()

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
                }
            ]
        }

        history = manager.get_approval_history(state)
        assert len(history) == 2
        assert history[0]["action"] == "approve"
        assert history[1]["action"] == "modify"

    def test_get_gate_status(self):
        """Test getting gate status."""
        manager = GateManager()

        state = {
            "current_stage": "level_2_technique_selection",
            "human_approvals": [
                {
                    "gate_name": "paradigm_selection",
                    "timestamp": 1.0,
                    "action": "approve",
                    "reviewer": "user1",
                    "notes": None,
                    "modifications": None
                }
            ]
        }

        status = manager.get_gate_status(state)

        assert status["current_stage"] == "level_2_technique_selection"
        assert status["total_approvals"] == 1
        assert status["last_approval"]["action"] == "approve"

        # Check gate-specific status
        paradigm_status = status["gates"]["paradigm_selection"]
        assert paradigm_status["approval_count"] == 1
        assert paradigm_status["last_action"] == "approve"
        assert paradigm_status["last_timestamp"] == 1.0

        technique_status = status["gates"]["technique_selection"]
        assert technique_status["approval_count"] == 0
        assert technique_status["last_action"] is None

    def test_validate_gate_sequence_valid(self):
        """Test validation of valid gate sequence."""
        manager = GateManager()

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
                    "action": "approve",
                    "reviewer": "user1",
                    "notes": None,
                    "modifications": None
                },
                {
                    "gate_name": "final_solution",
                    "timestamp": 3.0,
                    "action": "approve",
                    "reviewer": "user1",
                    "notes": None,
                    "modifications": None
                }
            ]
        }

        assert manager.validate_gate_sequence(state) is True

    def test_validate_gate_sequence_invalid(self):
        """Test validation of invalid gate sequence."""
        manager = GateManager()

        state = {
            "human_approvals": [
                {
                    "gate_name": "technique_selection",  # Level 2
                    "timestamp": 1.0,
                    "action": "approve",
                    "reviewer": "user1",
                    "notes": None,
                    "modifications": None
                },
                {
                    "gate_name": "paradigm_selection",  # Level 1 (out of order!)
                    "timestamp": 2.0,
                    "action": "approve",
                    "reviewer": "user1",
                    "notes": None,
                    "modifications": None
                }
            ]
        }

        assert manager.validate_gate_sequence(state) is False

    def test_get_next_gate(self):
        """Test determining next gate."""
        config = {
            "approval_gates": {
                "paradigm_selection": {"enabled": True},
                "technique_selection": {"enabled": False},
                "decomposition_review": {"enabled": True},
                "final_solution": {"enabled": True}
            }
        }

        manager = GateManager(config)

        # From level 1, next is paradigm_selection
        assert manager.get_next_gate(1) == "paradigm_selection"

        # From level 2, technique_selection is disabled, skip to decomposition_review
        assert manager.get_next_gate(2) == "decomposition_review"

        # From level 3, next is decomposition_review
        assert manager.get_next_gate(3) == "decomposition_review"

        # From level 4, next is final_solution
        assert manager.get_next_gate(4) == "final_solution"

    def test_should_gate_activate(self):
        """Test determining if gate should activate."""
        config = {
            "approval_gates": {
                "paradigm_selection": {
                    "enabled": True,
                    "auto_approve_threshold": 0.95
                }
            }
        }

        manager = GateManager(config)

        # Low confidence - should activate
        state1 = {"paradigm_scores": {"structural": 0.6}}
        assert manager.should_gate_activate("paradigm_selection", state1) is True

        # High confidence - should not activate
        state2 = {"paradigm_scores": {"structural": 0.98}}
        assert manager.should_gate_activate("paradigm_selection", state2) is False

        # Required gate - always activates
        state3 = {"paradigm_scores": {"structural": 0.99}}
        assert manager.should_gate_activate("final_solution", state3) is True

    def test_update_config(self):
        """Test updating configuration."""
        manager = GateManager()

        new_config = {
            "approval_gates": {
                "paradigm_selection": {"enabled": True}
            }
        }

        manager.update_config(new_config)
        assert manager.config == new_config

    def test_reset(self):
        """Test resetting manager state."""
        manager = GateManager()

        state = {"current_stage": "level_1"}
        manager.record_gate_activation("paradigm_selection", state, 1.0)

        assert len(manager.activation_history) == 1

        manager.reset()
        assert len(manager.activation_history) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
