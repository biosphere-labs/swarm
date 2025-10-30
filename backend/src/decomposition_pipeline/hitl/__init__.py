"""
Human-in-the-Loop (HITL) approval gates for the decomposition pipeline.

This module provides approval gates that use LangGraph's interrupt mechanism
to pause pipeline execution and wait for human review at critical decision points.

Key Components:
- HumanApprovalGate: Main gate implementation using interrupt()
- GateManager: Coordinates gates across pipeline
- ApprovalActionHandler: Handles human responses (approve, reject, modify, etc.)

Usage:
    from decomposition_pipeline.hitl import HumanApprovalGate, GateManager

    # Create gates
    gates = create_approval_gates()

    # Add to graph
    graph.add_node("review_paradigms", gates["paradigm_selection"])

    # Manage gates
    manager = GateManager(config)
    status = manager.get_gate_status(state)
"""

from .approval_gate import HumanApprovalGate, create_approval_gates
from .gate_manager import GateManager
from .actions import ApprovalActionHandler, process_gate_response
from .types import (
    ApprovalAction,
    ApprovalRecord,
    GateConfig,
    GateReviewData,
    GateResponse
)

__all__ = [
    # Main classes
    "HumanApprovalGate",
    "GateManager",
    "ApprovalActionHandler",

    # Factory functions
    "create_approval_gates",
    "process_gate_response",

    # Types
    "ApprovalAction",
    "ApprovalRecord",
    "GateConfig",
    "GateReviewData",
    "GateResponse",
]
