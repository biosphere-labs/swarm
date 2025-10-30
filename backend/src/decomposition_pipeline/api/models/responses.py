"""
Pydantic response models for API endpoints.
"""

from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class PipelineRunResponse(BaseModel):
    """Response when starting a new pipeline run."""

    run_id: str = Field(
        ...,
        description="Unique identifier for this pipeline run (thread_id)",
    )

    status: str = Field(
        ...,
        description="Current status of the run",
    )

    current_stage: str = Field(
        ...,
        description="Current execution stage",
    )

    started_at: str = Field(
        ...,
        description="ISO timestamp when run started",
    )

    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for this run",
    )


class CheckpointInfo(BaseModel):
    """Information about a checkpoint."""

    checkpoint_id: str = Field(
        ...,
        description="Checkpoint identifier",
    )

    stage: str = Field(
        ...,
        description="Pipeline stage at this checkpoint",
    )

    timestamp: str = Field(
        ...,
        description="ISO timestamp of checkpoint creation",
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional checkpoint metadata",
    )


class ApprovalGateResponse(BaseModel):
    """Information about an active approval gate."""

    gate_name: str = Field(
        ...,
        description="Name of the approval gate",
    )

    stage: str = Field(
        ...,
        description="Pipeline stage where gate is active",
    )

    state_snapshot: Dict[str, Any] = Field(
        ...,
        description="Snapshot of relevant state for review",
    )

    options: List[str] = Field(
        default_factory=list,
        description="Available actions at this gate",
    )

    alternatives: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Alternative options if requested",
    )


class PipelineStateResponse(BaseModel):
    """Full pipeline state response."""

    run_id: str = Field(
        ...,
        description="Pipeline run identifier",
    )

    status: str = Field(
        ...,
        description="Current status",
    )

    current_stage: str = Field(
        ...,
        description="Current execution stage",
    )

    state: Dict[str, Any] = Field(
        ...,
        description="Full state object",
    )

    approval_required: bool = Field(
        default=False,
        description="Whether human approval is currently required",
    )

    current_gate: Optional[ApprovalGateResponse] = Field(
        default=None,
        description="Information about current approval gate if active",
    )

    started_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when run started",
    )

    updated_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp of last update",
    )


class PipelineHistoryResponse(BaseModel):
    """Pipeline execution history response."""

    run_id: str = Field(
        ...,
        description="Pipeline run identifier",
    )

    checkpoints: List[CheckpointInfo] = Field(
        default_factory=list,
        description="List of all checkpoints",
    )

    approvals: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of all approval decisions",
    )

    backtracks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of backtrack operations",
    )

    started_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when run started",
    )

    completed_at: Optional[str] = Field(
        default=None,
        description="ISO timestamp when run completed (if completed)",
    )

    duration_seconds: Optional[float] = Field(
        default=None,
        description="Total duration in seconds (if completed)",
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(
        ...,
        description="Error type or code",
    )

    message: str = Field(
        ...,
        description="Human-readable error message",
    )

    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details",
    )

    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="ISO timestamp of error",
    )


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = Field(
        default=True,
        description="Operation success status",
    )

    message: str = Field(
        ...,
        description="Success message",
    )

    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional response data",
    )
