"""
Human-in-the-Loop approval gate implementation using LangGraph interrupt mechanism.
"""

from typing import Dict, Any, Optional, Callable
from langgraph.types import interrupt
from .types import GateConfig, GateReviewData, ApprovalRecord
import time


class HumanApprovalGate:
    """
    Approval gate node that interrupts pipeline execution for human review.

    Based on brainstorm_1.md section on HITL Gates (lines 620-695).
    Uses LangGraph's interrupt mechanism to pause execution and wait for human input.
    """

    def __init__(
        self,
        gate_name: str,
        gate_level: int,
        required: bool = False,
        description: str = ""
    ):
        """
        Initialize approval gate.

        Args:
            gate_name: Unique identifier for this gate (e.g., "paradigm_selection")
            gate_level: Pipeline level (1-4)
            required: Whether this gate cannot be bypassed
            description: Human-readable description of gate purpose
        """
        self.gate_name = gate_name
        self.gate_level = gate_level
        self.required = required
        self.description = description

    def should_request_approval(self, state: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """
        Determine if approval should be requested based on configuration and state.

        Args:
            state: Current pipeline state
            config: Gate configuration from settings

        Returns:
            True if approval should be requested, False to auto-approve
        """
        # Gate 4 (final review) is always required
        if self.gate_level == 4 or self.required:
            return True

        # Check if gate is enabled in configuration
        gate_settings = config.get("approval_gates", {})
        gate_config = gate_settings.get(self.gate_name, {})

        if not gate_config.get("enabled", False):
            return False

        # Check confidence thresholds for auto-approval
        confidence_threshold = gate_config.get("auto_approve_threshold", 0.95)

        # Level-specific confidence checks
        if self.gate_level == 1:  # Paradigm selection
            max_score = max(state.get("paradigm_scores", {}).values(), default=0)
            if max_score >= confidence_threshold:
                return False

        elif self.gate_level == 2:  # Technique selection
            avg_score = sum(state.get("technique_scores", {}).values()) / max(len(state.get("technique_scores", {})), 1)
            if avg_score >= confidence_threshold:
                return False

        elif self.gate_level == 3:  # Decomposition review
            validation = state.get("validation_results", {})
            if validation.get("completeness_score", 0) >= confidence_threshold:
                return False

        return True

    def prepare_review_data(self, state: Dict[str, Any]) -> GateReviewData:
        """
        Format state data for human review based on gate type.

        Args:
            state: Current pipeline state

        Returns:
            Structured data for review interface
        """
        review_data: GateReviewData = {
            "gate": self.gate_name,
            "stage": f"Level {self.gate_level}",
            "options": ["approve", "reject", "modify", "backtrack", "add_context", "request_alternatives"],
            "alternatives": None,
            "context": {
                "description": self.description,
                "level": self.gate_level,
                "required": self.required
            },
            "state_snapshot": {}
        }

        # Level-specific review data preparation
        if self.gate_level == 1:  # Paradigm Selection Gate
            review_data["state_snapshot"] = {
                "selected_paradigms": state.get("selected_paradigms", []),
                "paradigm_scores": state.get("paradigm_scores", {}),
                "paradigm_reasoning": state.get("paradigm_reasoning", {}),
                "problem_characteristics": state.get("problem_characteristics", {}),
                "rejected_paradigms": {
                    k: v for k, v in state.get("paradigm_scores", {}).items()
                    if k not in state.get("selected_paradigms", [])
                }
            }
            review_data["context"]["stage_description"] = (
                "Review selected decomposition paradigms. "
                "The system has analyzed the problem and selected the most applicable paradigms."
            )

        elif self.gate_level == 2:  # Technique Selection Gate
            review_data["state_snapshot"] = {
                "selected_techniques": state.get("selected_techniques", {}),
                "technique_scores": state.get("technique_scores", {}),
                "technique_justification": state.get("technique_justification", {}),
                "selected_paradigms": state.get("selected_paradigms", []),
                "technique_prerequisites": state.get("technique_prerequisites", {})
            }
            review_data["context"]["stage_description"] = (
                "Review selected algorithmic techniques for each paradigm. "
                "Each technique has formal justification from computer science literature."
            )

        elif self.gate_level == 3:  # Decomposition Review Gate
            review_data["state_snapshot"] = {
                "integrated_subproblems": state.get("integrated_subproblems", []),
                "subproblem_dependencies": state.get("subproblem_dependencies", {}),
                "decomposition_graphs": state.get("decomposition_graphs", {}),
                "validation_results": state.get("validation_results", {}),
                "detected_conflicts": state.get("detected_conflicts", []),
                "coverage_analysis": state.get("coverage_analysis", {})
            }
            review_data["context"]["stage_description"] = (
                "Review the complete decomposition structure. "
                "Verify that all subproblems are well-defined and dependencies are correct."
            )

        elif self.gate_level == 4:  # Final Solution Gate
            review_data["state_snapshot"] = {
                "integrated_solution": state.get("integrated_solution", {}),
                "validation_results": state.get("validation_results", {}),
                "partial_solutions": state.get("partial_solutions", {}),
                "coherence_report": state.get("coherence_report", {}),
                "implementation_plan": state.get("implementation_plan", {})
            }
            review_data["context"]["stage_description"] = (
                "Final review of integrated solution. "
                "This is the last checkpoint before output delivery."
            )

        return review_data

    def __call__(self, state: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute approval gate - main node function.

        Args:
            state: Current pipeline state
            config: Configuration including approval gate settings

        Returns:
            Updated state (may include interrupt data)
        """
        if config is None:
            config = {}

        # Check if approval is needed
        if not self.should_request_approval(state, config):
            # Auto-approve: add approval record and continue
            approval_record: ApprovalRecord = {
                "gate_name": self.gate_name,
                "timestamp": time.time(),
                "action": "approve",
                "reviewer": "system",
                "notes": "Auto-approved based on confidence threshold",
                "modifications": None
            }

            state.setdefault("human_approvals", []).append(approval_record)
            return state

        # Prepare review data
        review_data = self.prepare_review_data(state)

        # Interrupt execution and wait for human input
        # The interrupt() function suspends graph execution
        # Resume will happen when human provides input through API
        response = interrupt(review_data)

        # When resumed, response contains the human's decision
        # This part executes after human provides input
        if response:
            # Record the approval decision
            approval_record: ApprovalRecord = {
                "gate_name": self.gate_name,
                "timestamp": time.time(),
                "action": response.get("action", "approve"),
                "reviewer": response.get("reviewer", "unknown"),
                "notes": response.get("notes"),
                "modifications": response.get("modifications")
            }

            state.setdefault("human_approvals", []).append(approval_record)

            # Store response for action handler to process
            state["_pending_gate_response"] = response

        return state


def create_approval_gates() -> Dict[str, HumanApprovalGate]:
    """
    Create all approval gates for the pipeline.

    Returns:
        Dictionary mapping gate names to gate instances
    """
    gates = {
        "paradigm_selection": HumanApprovalGate(
            gate_name="paradigm_selection",
            gate_level=1,
            required=False,
            description="Review paradigm selection after Level 1 analysis"
        ),
        "technique_selection": HumanApprovalGate(
            gate_name="technique_selection",
            gate_level=2,
            required=False,
            description="Review technique selection from catalog"
        ),
        "decomposition_review": HumanApprovalGate(
            gate_name="decomposition_review",
            gate_level=3,
            required=False,
            description="Review complete decomposition structure"
        ),
        "final_solution": HumanApprovalGate(
            gate_name="final_solution",
            gate_level=4,
            required=True,
            description="Final review before solution delivery"
        )
    }

    return gates
