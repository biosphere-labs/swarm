"""
Gate Manager for coordinating Human-in-the-Loop approval gates across the pipeline.
"""

from typing import Dict, Any, List, Optional
from .types import GateConfig, ApprovalRecord
from .approval_gate import HumanApprovalGate, create_approval_gates


class GateManager:
    """
    Manages lifecycle and coordination of approval gates across the decomposition pipeline.

    Responsibilities:
    - Track gate activation history
    - Coordinate with pipeline checkpointer
    - Provide gate status queries
    - Manage gate configuration
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize gate manager.

        Args:
            config: Configuration dictionary with approval gate settings
        """
        self.config = config or {}
        self.gates = create_approval_gates()
        self.activation_history: List[Dict[str, Any]] = []

    def get_gate(self, gate_name: str) -> Optional[HumanApprovalGate]:
        """
        Get gate instance by name.

        Args:
            gate_name: Name of the gate

        Returns:
            Gate instance or None if not found
        """
        return self.gates.get(gate_name)

    def get_gate_config(self, gate_name: str) -> GateConfig:
        """
        Get configuration for a specific gate.

        Args:
            gate_name: Name of the gate

        Returns:
            Gate configuration
        """
        gate = self.gates.get(gate_name)
        if not gate:
            raise ValueError(f"Unknown gate: {gate_name}")

        gate_settings = self.config.get("approval_gates", {}).get(gate_name, {})

        return GateConfig(
            name=gate_name,
            enabled=gate_settings.get("enabled", gate.required),
            required=gate.required,
            level=gate.gate_level,
            description=gate.description
        )

    def get_all_gate_configs(self) -> List[GateConfig]:
        """
        Get configuration for all gates.

        Returns:
            List of gate configurations
        """
        return [self.get_gate_config(name) for name in self.gates.keys()]

    def is_gate_enabled(self, gate_name: str) -> bool:
        """
        Check if a gate is enabled.

        Args:
            gate_name: Name of the gate

        Returns:
            True if enabled, False otherwise
        """
        config = self.get_gate_config(gate_name)
        return config["enabled"]

    def record_gate_activation(
        self,
        gate_name: str,
        state: Dict[str, Any],
        timestamp: float
    ):
        """
        Record when a gate was activated.

        Args:
            gate_name: Name of the activated gate
            state: Pipeline state at activation
            timestamp: Activation timestamp
        """
        activation_record = {
            "gate_name": gate_name,
            "timestamp": timestamp,
            "state_snapshot": {
                "current_stage": state.get("current_stage"),
                "selected_paradigms": state.get("selected_paradigms"),
                "subproblems_count": len(state.get("integrated_subproblems", []))
            }
        }
        self.activation_history.append(activation_record)

    def get_activation_history(self, gate_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get activation history for gates.

        Args:
            gate_name: Optional gate name to filter by

        Returns:
            List of activation records
        """
        if gate_name:
            return [
                record for record in self.activation_history
                if record["gate_name"] == gate_name
            ]
        return self.activation_history

    def get_approval_history(self, state: Dict[str, Any]) -> List[ApprovalRecord]:
        """
        Get approval history from state.

        Args:
            state: Pipeline state containing approval records

        Returns:
            List of approval records
        """
        return state.get("human_approvals", [])

    def get_gate_status(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current status of all gates.

        Args:
            state: Current pipeline state

        Returns:
            Dictionary with gate status information
        """
        approvals = self.get_approval_history(state)
        current_stage = state.get("current_stage", "unknown")

        status = {
            "current_stage": current_stage,
            "gates": {},
            "total_approvals": len(approvals),
            "last_approval": approvals[-1] if approvals else None
        }

        for gate_name, gate in self.gates.items():
            gate_approvals = [a for a in approvals if a["gate_name"] == gate_name]

            status["gates"][gate_name] = {
                "enabled": self.is_gate_enabled(gate_name),
                "required": gate.required,
                "level": gate.gate_level,
                "approval_count": len(gate_approvals),
                "last_action": gate_approvals[-1]["action"] if gate_approvals else None,
                "last_timestamp": gate_approvals[-1]["timestamp"] if gate_approvals else None
            }

        return status

    def validate_gate_sequence(self, state: Dict[str, Any]) -> bool:
        """
        Validate that gates were activated in correct sequence.

        Args:
            state: Pipeline state with approval history

        Returns:
            True if sequence is valid
        """
        approvals = self.get_approval_history(state)

        # Extract gate levels from approval history
        gate_levels = []
        for approval in approvals:
            gate_name = approval["gate_name"]
            gate = self.gates.get(gate_name)
            if gate:
                gate_levels.append(gate.gate_level)

        # Check that levels are in ascending order (allowing duplicates)
        for i in range(len(gate_levels) - 1):
            if gate_levels[i] > gate_levels[i + 1]:
                return False

        return True

    def get_next_gate(self, current_level: int) -> Optional[str]:
        """
        Determine the next gate based on current pipeline level.

        Args:
            current_level: Current pipeline level (1-5)

        Returns:
            Name of next gate or None if no more gates
        """
        # Map levels to gates
        level_gates = {
            1: "paradigm_selection",
            2: "technique_selection",
            3: "decomposition_review",
            4: "final_solution"
        }

        # Find next enabled gate at or after current level
        for level in range(current_level, 5):
            gate_name = level_gates.get(level)
            if gate_name and self.is_gate_enabled(gate_name):
                return gate_name

        return None

    def should_gate_activate(
        self,
        gate_name: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Determine if a gate should activate based on current state.

        Args:
            gate_name: Name of the gate
            state: Current pipeline state

        Returns:
            True if gate should activate
        """
        gate = self.get_gate(gate_name)
        if not gate:
            return False

        # Check if gate is enabled
        if not self.is_gate_enabled(gate_name):
            return False

        # Check if gate should request approval
        return gate.should_request_approval(state, self.config)

    def update_config(self, new_config: Dict[str, Any]):
        """
        Update gate configuration.

        Args:
            new_config: New configuration dictionary
        """
        self.config = new_config

    def reset(self):
        """Reset gate manager state (for testing)."""
        self.activation_history = []
