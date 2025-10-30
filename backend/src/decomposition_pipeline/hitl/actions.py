"""
Action handlers for Human-in-the-Loop approval gate responses.
"""

from typing import Dict, Any, Optional, List
from .types import GateResponse, ApprovalRecord, ApprovalAction
import copy
import time


class ApprovalActionHandler:
    """
    Handles approval actions from human reviewers at approval gates.

    Supports:
    - approve: Continue to next stage
    - reject: Backtrack to previous stage
    - modify: Edit state and continue
    - backtrack: Jump to specific checkpoint
    - add_context: Provide additional info and re-run
    - request_alternatives: Generate more options
    """

    def __init__(self, checkpointer=None):
        """
        Initialize action handler.

        Args:
            checkpointer: Optional LangGraph checkpointer for state management
        """
        self.checkpointer = checkpointer

    def handle_action(
        self,
        action: ApprovalAction,
        response: GateResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dispatch action to appropriate handler.

        Args:
            action: Type of approval action
            response: Full response from human reviewer
            state: Current pipeline state

        Returns:
            Updated state after action processing
        """
        handlers = {
            "approve": self.handle_approve,
            "reject": self.handle_reject,
            "modify": self.handle_modify,
            "backtrack": self.handle_backtrack,
            "add_context": self.handle_add_context,
            "request_alternatives": self.handle_request_alternatives
        }

        handler = handlers.get(action)
        if not handler:
            raise ValueError(f"Unknown approval action: {action}")

        return handler(response, state)

    def handle_approve(
        self,
        response: GateResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle approve action - continue to next stage.

        Args:
            response: Reviewer response
            state: Current state

        Returns:
            Updated state (continues without modification)
        """
        # Simply continue - no state changes needed
        # The approval record is already added by the gate
        return state

    def handle_reject(
        self,
        response: GateResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle reject action - backtrack to previous stage.

        Args:
            response: Reviewer response with rejection reason
            state: Current state

        Returns:
            State configured to backtrack to previous stage
        """
        # Set flag to trigger backtracking
        state["_backtrack_requested"] = True
        state["_backtrack_reason"] = response.get("notes", "Rejected by reviewer")

        # Determine previous stage based on current stage
        current_stage = state.get("current_stage", "unknown")
        previous_stage = self._get_previous_stage(current_stage)

        state["_backtrack_to_stage"] = previous_stage

        return state

    def handle_modify(
        self,
        response: GateResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle modify action - apply modifications and continue.

        Args:
            response: Reviewer response with modifications
            state: Current state

        Returns:
            State with modifications applied
        """
        modifications = response.get("modifications", {})

        if not modifications:
            # No modifications provided, treat as approve
            return self.handle_approve(response, state)

        # Apply modifications to state
        for key, value in modifications.items():
            # Support nested key paths like "paradigm_scores.structural"
            if "." in key:
                self._set_nested_value(state, key, value)
            else:
                state[key] = value

        # Track what was modified
        state.setdefault("_modification_history", []).append({
            "timestamp": time.time(),
            "reviewer": response.get("reviewer", "unknown"),
            "modifications": modifications,
            "notes": response.get("notes")
        })

        return state

    def handle_backtrack(
        self,
        response: GateResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle backtrack action - jump to specific checkpoint.

        Args:
            response: Reviewer response with target checkpoint
            state: Current state

        Returns:
            State configured to backtrack to specific checkpoint
        """
        backtrack_to = response.get("backtrack_to")

        if not backtrack_to:
            # No target specified, backtrack to previous stage
            return self.handle_reject(response, state)

        state["_backtrack_requested"] = True
        state["_backtrack_to_stage"] = backtrack_to
        state["_backtrack_reason"] = response.get("notes", "Manual backtrack requested")

        return state

    def handle_add_context(
        self,
        response: GateResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle add_context action - add human insight and re-run.

        Args:
            response: Reviewer response with additional context
            state: Current state

        Returns:
            State with added context, configured to re-run current stage
        """
        additional_context = response.get("additional_context", "")

        if not additional_context:
            # No context provided, treat as approve
            return self.handle_approve(response, state)

        # Add to accumulated human context
        state.setdefault("human_context", []).append({
            "timestamp": time.time(),
            "reviewer": response.get("reviewer", "unknown"),
            "context": additional_context,
            "stage": state.get("current_stage"),
            "notes": response.get("notes")
        })

        # Also add to problem characteristics for consideration
        problem_characteristics = state.get("problem_characteristics", {})
        problem_characteristics.setdefault("human_insights", []).append(additional_context)
        state["problem_characteristics"] = problem_characteristics

        # Flag to re-run current stage with new context
        state["_rerun_current_stage"] = True

        return state

    def handle_request_alternatives(
        self,
        response: GateResponse,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle request_alternatives action - generate more options.

        Args:
            response: Reviewer response requesting alternatives
            state: Current state

        Returns:
            State configured to generate alternative options
        """
        # Number of alternatives to generate (default 3)
        alternative_count = response.get("alternative_count", 3)

        # Flag to generate alternatives
        state["_generate_alternatives"] = True
        state["_alternative_count"] = alternative_count

        # Store current selections as "primary" for comparison
        current_stage = state.get("current_stage", "unknown")

        if "level_1" in current_stage.lower() or "paradigm" in current_stage.lower():
            state["_primary_paradigms"] = state.get("selected_paradigms", [])

        elif "level_2" in current_stage.lower() or "technique" in current_stage.lower():
            state["_primary_techniques"] = state.get("selected_techniques", {})

        elif "level_3" in current_stage.lower() or "decomposition" in current_stage.lower():
            state["_primary_decomposition"] = state.get("integrated_subproblems", [])

        return state

    def _get_previous_stage(self, current_stage: str) -> str:
        """
        Determine previous stage based on current stage.

        Args:
            current_stage: Current pipeline stage

        Returns:
            Previous stage name
        """
        stage_sequence = [
            "problem_ingestion",
            "level_1_paradigm_selection",
            "level_2_technique_selection",
            "level_3_decomposition",
            "level_4_solution_generation",
            "level_5_integration"
        ]

        try:
            current_idx = stage_sequence.index(current_stage)
            if current_idx > 0:
                return stage_sequence[current_idx - 1]
        except ValueError:
            pass

        # Default to problem ingestion if unknown stage
        return "problem_ingestion"

    def _set_nested_value(self, state: Dict[str, Any], key_path: str, value: Any):
        """
        Set a nested value in state using dot notation.

        Args:
            state: State dictionary
            key_path: Dot-separated key path (e.g., "paradigm_scores.structural")
            value: Value to set
        """
        keys = key_path.split(".")
        current = state

        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final value
        current[keys[-1]] = value

    def create_approval_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create summary of all approval actions taken.

        Args:
            state: Pipeline state with approval history

        Returns:
            Summary of approval activity
        """
        approvals = state.get("human_approvals", [])

        summary = {
            "total_approvals": len(approvals),
            "actions_by_type": {},
            "reviewers": set(),
            "gates_activated": set(),
            "modifications_count": 0,
            "backtrack_count": 0,
            "timeline": []
        }

        for approval in approvals:
            action = approval["action"]
            summary["actions_by_type"][action] = summary["actions_by_type"].get(action, 0) + 1
            summary["reviewers"].add(approval["reviewer"])
            summary["gates_activated"].add(approval["gate_name"])

            if approval.get("modifications"):
                summary["modifications_count"] += 1

            if action in ("reject", "backtrack"):
                summary["backtrack_count"] += 1

            summary["timeline"].append({
                "timestamp": approval["timestamp"],
                "gate": approval["gate_name"],
                "action": action,
                "reviewer": approval["reviewer"]
            })

        # Convert sets to lists for JSON serialization
        summary["reviewers"] = list(summary["reviewers"])
        summary["gates_activated"] = list(summary["gates_activated"])

        return summary


def process_gate_response(
    state: Dict[str, Any],
    handler: Optional[ApprovalActionHandler] = None
) -> Dict[str, Any]:
    """
    Process pending gate response from state.

    This function should be called after a gate interrupt is resumed.

    Args:
        state: Pipeline state with pending gate response
        handler: Optional action handler instance

    Returns:
        Updated state after processing response
    """
    if handler is None:
        handler = ApprovalActionHandler()

    # Check for pending response
    response = state.pop("_pending_gate_response", None)

    if not response:
        # No pending response, nothing to do
        return state

    # Extract action
    action = response.get("action", "approve")

    # Handle the action
    state = handler.handle_action(action, response, state)

    return state
