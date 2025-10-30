"""
Pydantic request models for API endpoints.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class StartPipelineRequest(BaseModel):
    """Request to start a new pipeline run."""

    problem: str = Field(
        ...,
        description="The problem description to decompose",
        min_length=10,
    )

    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional configuration overrides for this run",
    )

    approval_gates: Optional[Dict[str, bool]] = Field(
        default=None,
        description="Override which approval gates are enabled",
        json_schema_extra={
            "example": {
                "paradigm": True,
                "technique": False,
                "decomposition": True,
                "solution": True,
            }
        }
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata to attach to this run",
    )


class ApproveRequest(BaseModel):
    """Request to approve at an approval gate."""

    reviewer: str = Field(
        default="user",
        description="Identifier of the reviewer",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional notes about the approval decision",
    )

    modifications: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional modifications to apply before continuing",
    )


class RejectRequest(BaseModel):
    """Request to reject and backtrack."""

    reviewer: str = Field(
        default="user",
        description="Identifier of the reviewer",
    )

    reason: str = Field(
        ...,
        description="Reason for rejection",
        min_length=1,
    )

    backtrack_to: Optional[str] = Field(
        default=None,
        description="Optional: specific stage to backtrack to. If not provided, backtracks to previous stage.",
    )


class ModifyStateRequest(BaseModel):
    """Request to modify the current state."""

    reviewer: str = Field(
        default="user",
        description="Identifier of the reviewer making modifications",
    )

    modifications: Dict[str, Any] = Field(
        ...,
        description="State modifications to apply",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional notes about the modifications",
    )

    continue_after: bool = Field(
        default=True,
        description="Whether to continue execution after modifying state",
    )


class BacktrackRequest(BaseModel):
    """Request to backtrack to a specific checkpoint."""

    reviewer: str = Field(
        default="user",
        description="Identifier of the reviewer",
    )

    checkpoint_id: Optional[str] = Field(
        default=None,
        description="Checkpoint ID to backtrack to",
    )

    stage: Optional[str] = Field(
        default=None,
        description="Stage name to backtrack to (alternative to checkpoint_id)",
    )

    reason: Optional[str] = Field(
        default=None,
        description="Reason for backtracking",
    )


class AddContextRequest(BaseModel):
    """Request to add additional context and re-run."""

    reviewer: str = Field(
        default="user",
        description="Identifier of the reviewer",
    )

    additional_context: str = Field(
        ...,
        description="Additional context to add",
        min_length=1,
    )

    rerun_from: Optional[str] = Field(
        default=None,
        description="Optional: stage to rerun from. If not provided, reruns current stage.",
    )


class RequestAlternativesRequest(BaseModel):
    """Request to generate alternative options."""

    reviewer: str = Field(
        default="user",
        description="Identifier of the reviewer",
    )

    count: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of alternatives to generate",
    )

    notes: Optional[str] = Field(
        default=None,
        description="Optional notes about what alternatives are needed",
    )
