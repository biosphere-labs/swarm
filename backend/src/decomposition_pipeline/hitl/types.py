"""
Type definitions for Human-in-the-Loop approval gates.
"""

from typing import TypedDict, Literal, Optional, Dict, Any, List
from datetime import datetime


ApprovalAction = Literal[
    "approve",
    "reject",
    "modify",
    "backtrack",
    "add_context",
    "request_alternatives"
]


class ApprovalRecord(TypedDict):
    """Record of a human approval decision."""
    gate_name: str
    timestamp: float
    action: ApprovalAction
    reviewer: str
    notes: Optional[str]
    modifications: Optional[Dict[str, Any]]


class GateConfig(TypedDict):
    """Configuration for an approval gate."""
    name: str
    enabled: bool
    required: bool
    level: int
    description: str


class GateReviewData(TypedDict):
    """Data prepared for human review at a gate."""
    gate: str
    stage: str
    state_snapshot: Dict[str, Any]
    options: List[str]
    alternatives: Optional[List[Dict[str, Any]]]
    context: Dict[str, Any]


class GateResponse(TypedDict):
    """Response from human at approval gate."""
    action: ApprovalAction
    reviewer: str
    notes: Optional[str]
    modifications: Optional[Dict[str, Any]]
    selected_alternative: Optional[int]
    additional_context: Optional[str]
    backtrack_to: Optional[str]
