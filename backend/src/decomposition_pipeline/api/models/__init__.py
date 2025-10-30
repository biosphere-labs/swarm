"""
Pydantic models for API requests and responses.
"""

from decomposition_pipeline.api.models.requests import (
    StartPipelineRequest,
    ApproveRequest,
    RejectRequest,
    ModifyStateRequest,
    BacktrackRequest,
    AddContextRequest,
    RequestAlternativesRequest,
)

from decomposition_pipeline.api.models.responses import (
    PipelineRunResponse,
    PipelineStateResponse,
    PipelineHistoryResponse,
    CheckpointInfo,
    ApprovalGateResponse,
    ErrorResponse,
    SuccessResponse,
)

__all__ = [
    # Requests
    "StartPipelineRequest",
    "ApproveRequest",
    "RejectRequest",
    "ModifyStateRequest",
    "BacktrackRequest",
    "AddContextRequest",
    "RequestAlternativesRequest",
    # Responses
    "PipelineRunResponse",
    "PipelineStateResponse",
    "PipelineHistoryResponse",
    "CheckpointInfo",
    "ApprovalGateResponse",
    "ErrorResponse",
    "SuccessResponse",
]
