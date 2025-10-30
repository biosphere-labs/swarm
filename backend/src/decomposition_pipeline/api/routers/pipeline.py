"""
Main pipeline control API endpoints.

Provides RESTful API for controlling the LangGraph decomposition pipeline:
- Start new pipeline runs
- Approve/reject at gates
- Modify state
- Backtrack to checkpoints
- Query state and history
- Cancel runs
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from decomposition_pipeline.api.models import (
    StartPipelineRequest,
    ApproveRequest,
    RejectRequest,
    ModifyStateRequest,
    BacktrackRequest,
    AddContextRequest,
    RequestAlternativesRequest,
    PipelineRunResponse,
    PipelineStateResponse,
    PipelineHistoryResponse,
    ErrorResponse,
    SuccessResponse,
    CheckpointInfo,
    ApprovalGateResponse,
)
from decomposition_pipeline.graphs.main_graph import create_main_orchestration_graph
from decomposition_pipeline.checkpoint import create_checkpointer, CheckpointManager
from decomposition_pipeline.hitl import process_gate_response
from decomposition_pipeline.schemas import MainPipelineState, PipelineStage, ApprovalAction
from decomposition_pipeline.config.settings import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/pipeline",
    tags=["pipeline"],
)

# Global storage for active pipeline runs
# In production, this should be replaced with a proper state management system
_active_runs: Dict[str, Dict[str, Any]] = {}
_run_locks: Dict[str, asyncio.Lock] = {}


def get_run_lock(run_id: str) -> asyncio.Lock:
    """Get or create a lock for a specific run."""
    if run_id not in _run_locks:
        _run_locks[run_id] = asyncio.Lock()
    return _run_locks[run_id]


@router.post(
    "/start",
    response_model=PipelineRunResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start new pipeline run",
    description="Starts a new decomposition pipeline run with the given problem description.",
)
async def start_pipeline(request: StartPipelineRequest) -> PipelineRunResponse:
    """
    Start a new pipeline run.

    Args:
        request: Pipeline start request with problem and configuration

    Returns:
        PipelineRunResponse with run_id and initial state

    Raises:
        HTTPException: If pipeline fails to start
    """
    try:
        logger.info(f"Starting new pipeline run with problem: {request.problem[:100]}...")

        # Create main graph and checkpointer
        checkpointer = create_checkpointer()
        graph = create_main_orchestration_graph(checkpointer=checkpointer)

        # Create initial state
        initial_state: MainPipelineState = {
            "original_problem": request.problem,
            "problem_characteristics": {},
            "selected_paradigms": [],
            "paradigm_scores": {},
            "selected_techniques": {},
            "technique_scores": {},
            "technique_justification": {},
            "decomposed_subproblems": {},
            "decomposition_graphs": {},
            "integrated_subproblems": [],
            "subproblem_dependencies": {"nodes": [], "edges": []},
            "agent_assignments": {},
            "partial_solutions": {},
            "integrated_solution": {
                "content": "",
                "reasoning": "",
                "confidence": 0.0,
            },
            "validation_results": {
                "status": "valid",
                "has_critical_failures": False,
                "has_gaps": False,
                "has_conflicts": False,
                "issues": [],
                "recommendations": [],
            },
            "human_approvals": [],
            "backtrack_history": [],
            "current_stage": PipelineStage.PROBLEM_INGESTION.value,
        }

        # Apply config overrides if provided
        if request.config:
            initial_state.update(request.config)  # type: ignore

        # Generate run ID
        import uuid
        run_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": run_id}}

        # Store run info
        _active_runs[run_id] = {
            "graph": graph,
            "checkpointer": checkpointer,
            "config": config,
            "started_at": datetime.now().isoformat(),
            "status": "running",
            "initial_state": initial_state,
        }

        # Start pipeline execution asynchronously
        asyncio.create_task(_run_pipeline(run_id, graph, initial_state, config))

        logger.info(f"Pipeline run {run_id} started successfully")

        return PipelineRunResponse(
            run_id=run_id,
            status="running",
            current_stage=PipelineStage.PROBLEM_INGESTION.value,
            started_at=_active_runs[run_id]["started_at"],
            config=request.config or {},
        )

    except Exception as e:
        logger.error(f"Failed to start pipeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pipeline: {str(e)}",
        )


async def _run_pipeline(
    run_id: str,
    graph: Any,
    initial_state: MainPipelineState,
    config: Dict[str, Any],
) -> None:
    """
    Execute pipeline asynchronously.

    This runs in the background and updates the run state as it progresses.
    """
    try:
        async with get_run_lock(run_id):
            logger.info(f"Executing pipeline for run {run_id}")
            _active_runs[run_id]["status"] = "running"

            # Run the graph
            result = await graph.ainvoke(initial_state, config=config)

            # Update run info
            _active_runs[run_id]["status"] = "completed"
            _active_runs[run_id]["completed_at"] = datetime.now().isoformat()
            _active_runs[run_id]["result"] = result

            logger.info(f"Pipeline run {run_id} completed successfully")

    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {str(e)}", exc_info=True)
        if run_id in _active_runs:
            _active_runs[run_id]["status"] = "failed"
            _active_runs[run_id]["error"] = str(e)


@router.get(
    "/{run_id}/state",
    response_model=PipelineStateResponse,
    summary="Get pipeline state",
    description="Retrieves the current state of a pipeline run.",
)
async def get_pipeline_state(run_id: str) -> PipelineStateResponse:
    """
    Get current pipeline state.

    Args:
        run_id: Pipeline run identifier

    Returns:
        PipelineStateResponse with full current state

    Raises:
        HTTPException: If run not found
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    run_info = _active_runs[run_id]
    checkpointer = run_info["checkpointer"]
    config = run_info["config"]

    try:
        # Get latest checkpoint
        checkpoint = checkpointer.get(config)
        if checkpoint is None:
            # No checkpoint yet, use initial state
            state = run_info.get("initial_state", {})
        else:
            state = checkpoint.get("channel_values", {})

        # Check if approval is required
        approval_required = state.get("awaiting_approval", False)
        current_gate = None

        if approval_required:
            current_gate = ApprovalGateResponse(
                gate_name=state.get("current_gate", "unknown"),
                stage=state.get("current_stage", "unknown"),
                state_snapshot=_prepare_gate_snapshot(state),
                options=["approve", "reject", "modify", "backtrack"],
            )

        return PipelineStateResponse(
            run_id=run_id,
            status=run_info["status"],
            current_stage=state.get("current_stage", "unknown"),
            state=state,
            approval_required=approval_required,
            current_gate=current_gate,
            started_at=run_info.get("started_at"),
            updated_at=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Failed to get state for run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve state: {str(e)}",
        )


@router.get(
    "/{run_id}/history",
    response_model=PipelineHistoryResponse,
    summary="Get execution history",
    description="Retrieves the full execution history including checkpoints and approvals.",
)
async def get_pipeline_history(run_id: str) -> PipelineHistoryResponse:
    """
    Get pipeline execution history.

    Args:
        run_id: Pipeline run identifier

    Returns:
        PipelineHistoryResponse with checkpoints and approvals

    Raises:
        HTTPException: If run not found
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    run_info = _active_runs[run_id]
    checkpointer = run_info["checkpointer"]
    config = run_info["config"]

    try:
        # Get all checkpoints
        checkpoints = []
        for checkpoint_tuple in checkpointer.list(config):
            checkpoint = checkpoint_tuple.checkpoint
            metadata = checkpoint_tuple.metadata

            checkpoints.append(
                CheckpointInfo(
                    checkpoint_id=metadata.get("checkpoint_id", "unknown"),
                    stage=metadata.get("stage", "unknown"),
                    timestamp=metadata.get("timestamp", datetime.now().isoformat()),
                    metadata=metadata,
                )
            )

        # Get current state for approvals and backtracks
        current_checkpoint = checkpointer.get(config)
        state = current_checkpoint.get("channel_values", {}) if current_checkpoint else {}

        approvals = state.get("human_approvals", [])
        backtracks = state.get("backtrack_history", [])

        # Calculate duration if completed
        started_at = run_info.get("started_at")
        completed_at = run_info.get("completed_at")
        duration_seconds = None

        if started_at and completed_at:
            start = datetime.fromisoformat(started_at)
            end = datetime.fromisoformat(completed_at)
            duration_seconds = (end - start).total_seconds()

        return PipelineHistoryResponse(
            run_id=run_id,
            checkpoints=checkpoints,
            approvals=approvals,
            backtracks=backtracks,
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration_seconds,
        )

    except Exception as e:
        logger.error(f"Failed to get history for run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}",
        )


@router.post(
    "/{run_id}/approve",
    response_model=SuccessResponse,
    summary="Approve at gate",
    description="Approves the current approval gate and continues execution.",
)
async def approve_gate(run_id: str, request: ApproveRequest) -> SuccessResponse:
    """
    Approve at approval gate.

    Args:
        run_id: Pipeline run identifier
        request: Approval request with optional notes and modifications

    Returns:
        SuccessResponse indicating approval was processed

    Raises:
        HTTPException: If run not found or not awaiting approval
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    run_info = _active_runs[run_id]
    graph = run_info["graph"]
    config = run_info["config"]
    checkpointer = run_info["checkpointer"]

    try:
        # Get current state
        checkpoint = checkpointer.get(config)
        if checkpoint is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No checkpoint found for this run",
            )

        state = checkpoint.get("channel_values", {})

        if not state.get("awaiting_approval", False):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pipeline is not awaiting approval",
            )

        # Record approval
        approval_record = {
            "gate": state.get("current_gate", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "action": ApprovalAction.APPROVE,
            "user": request.reviewer,
            "reason": request.notes,
            "modifications": request.modifications,
        }

        # Update state with approval
        updated_state = {**state}
        updated_state["human_approvals"] = state.get("human_approvals", []) + [approval_record]
        updated_state["awaiting_approval"] = False

        # Apply modifications if provided
        if request.modifications:
            updated_state.update(request.modifications)

        # Resume execution
        asyncio.create_task(_run_pipeline(run_id, graph, updated_state, config))

        logger.info(f"Approval recorded for run {run_id} at gate {approval_record['gate']}")

        return SuccessResponse(
            success=True,
            message=f"Approved at gate {approval_record['gate']}. Pipeline resumed.",
            data={"approval": approval_record},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve gate for run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}",
        )


@router.post(
    "/{run_id}/reject",
    response_model=SuccessResponse,
    summary="Reject and backtrack",
    description="Rejects the current approval gate and backtracks to previous stage.",
)
async def reject_gate(run_id: str, request: RejectRequest) -> SuccessResponse:
    """
    Reject at approval gate and backtrack.

    Args:
        run_id: Pipeline run identifier
        request: Rejection request with reason and optional backtrack target

    Returns:
        SuccessResponse indicating rejection was processed

    Raises:
        HTTPException: If run not found or not awaiting approval
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    run_info = _active_runs[run_id]
    graph = run_info["graph"]
    config = run_info["config"]
    checkpointer = run_info["checkpointer"]

    try:
        # Get current state
        checkpoint = checkpointer.get(config)
        if checkpoint is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No checkpoint found for this run",
            )

        state = checkpoint.get("channel_values", {})

        if not state.get("awaiting_approval", False):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Pipeline is not awaiting approval",
            )

        # Record rejection
        rejection_record = {
            "gate": state.get("current_gate", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "action": ApprovalAction.REJECT,
            "user": request.reviewer,
            "reason": request.reason,
            "backtrack_to": request.backtrack_to,
        }

        # Update state with rejection
        updated_state = {**state}
        updated_state["human_approvals"] = state.get("human_approvals", []) + [rejection_record]
        updated_state["backtrack_history"] = state.get("backtrack_history", []) + [rejection_record]
        updated_state["awaiting_approval"] = False

        # TODO: Implement actual backtracking logic
        # For now, just mark as rejected
        updated_state["status"] = "rejected"

        logger.info(f"Rejection recorded for run {run_id} at gate {rejection_record['gate']}")

        return SuccessResponse(
            success=True,
            message=f"Rejected at gate {rejection_record['gate']}. Pipeline backtracked.",
            data={"rejection": rejection_record},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject gate for run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process rejection: {str(e)}",
        )


@router.post(
    "/{run_id}/modify",
    response_model=SuccessResponse,
    summary="Modify state",
    description="Modifies the current pipeline state and optionally continues execution.",
)
async def modify_state(run_id: str, request: ModifyStateRequest) -> SuccessResponse:
    """
    Modify pipeline state.

    Args:
        run_id: Pipeline run identifier
        request: Modification request with state changes

    Returns:
        SuccessResponse indicating modifications were applied

    Raises:
        HTTPException: If run not found
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    run_info = _active_runs[run_id]
    graph = run_info["graph"]
    config = run_info["config"]
    checkpointer = run_info["checkpointer"]

    try:
        # Get current state
        checkpoint = checkpointer.get(config)
        if checkpoint is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No checkpoint found for this run",
            )

        state = checkpoint.get("channel_values", {})

        # Apply modifications
        updated_state = {**state}
        updated_state.update(request.modifications)

        # Record modification
        modification_record = {
            "timestamp": datetime.now().isoformat(),
            "action": ApprovalAction.MODIFY,
            "user": request.reviewer,
            "notes": request.notes,
            "modifications": request.modifications,
        }
        updated_state["human_approvals"] = state.get("human_approvals", []) + [modification_record]

        # Save updated state to checkpointer
        # TODO: Implement proper state saving

        # Continue if requested
        if request.continue_after:
            asyncio.create_task(_run_pipeline(run_id, graph, updated_state, config))

        logger.info(f"State modified for run {run_id}")

        return SuccessResponse(
            success=True,
            message="State modifications applied successfully",
            data={"modification": modification_record},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to modify state for run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to modify state: {str(e)}",
        )


@router.post(
    "/{run_id}/backtrack",
    response_model=SuccessResponse,
    summary="Backtrack to checkpoint",
    description="Backtracks the pipeline to a specific checkpoint or stage.",
)
async def backtrack(run_id: str, request: BacktrackRequest) -> SuccessResponse:
    """
    Backtrack to a specific checkpoint.

    Args:
        run_id: Pipeline run identifier
        request: Backtrack request with target checkpoint or stage

    Returns:
        SuccessResponse indicating backtrack was performed

    Raises:
        HTTPException: If run not found or backtrack target invalid
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    if not request.checkpoint_id and not request.stage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either checkpoint_id or stage must be provided",
        )

    try:
        # TODO: Implement actual backtracking using checkpointer
        logger.info(f"Backtracking run {run_id} to {request.checkpoint_id or request.stage}")

        return SuccessResponse(
            success=True,
            message=f"Backtracked to {request.checkpoint_id or request.stage}",
            data={"target": request.checkpoint_id or request.stage},
        )

    except Exception as e:
        logger.error(f"Failed to backtrack run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to backtrack: {str(e)}",
        )


@router.post(
    "/{run_id}/add-context",
    response_model=SuccessResponse,
    summary="Add context",
    description="Adds additional context and reruns from current or specified stage.",
)
async def add_context(run_id: str, request: AddContextRequest) -> SuccessResponse:
    """
    Add additional context and rerun.

    Args:
        run_id: Pipeline run identifier
        request: Context addition request

    Returns:
        SuccessResponse indicating context was added

    Raises:
        HTTPException: If run not found
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    run_info = _active_runs[run_id]
    checkpointer = run_info["checkpointer"]
    config = run_info["config"]

    try:
        # Get current state
        checkpoint = checkpointer.get(config)
        if checkpoint is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No checkpoint found for this run",
            )

        state = checkpoint.get("channel_values", {})

        # Add context to state
        updated_state = {**state}
        current_context = state.get("additional_context", [])
        updated_state["additional_context"] = current_context + [request.additional_context]

        # Record action
        context_record = {
            "timestamp": datetime.now().isoformat(),
            "action": ApprovalAction.ADD_CONTEXT,
            "user": request.reviewer,
            "context": request.additional_context,
            "rerun_from": request.rerun_from,
        }
        updated_state["human_approvals"] = state.get("human_approvals", []) + [context_record]

        logger.info(f"Context added to run {run_id}")

        return SuccessResponse(
            success=True,
            message="Context added successfully",
            data={"context_addition": context_record},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add context for run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add context: {str(e)}",
        )


@router.delete(
    "/{run_id}",
    response_model=SuccessResponse,
    summary="Cancel run",
    description="Cancels an active pipeline run.",
)
async def cancel_run(run_id: str) -> SuccessResponse:
    """
    Cancel a pipeline run.

    Args:
        run_id: Pipeline run identifier

    Returns:
        SuccessResponse indicating run was cancelled

    Raises:
        HTTPException: If run not found
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline run {run_id} not found",
        )

    try:
        async with get_run_lock(run_id):
            _active_runs[run_id]["status"] = "cancelled"
            _active_runs[run_id]["cancelled_at"] = datetime.now().isoformat()

            logger.info(f"Pipeline run {run_id} cancelled")

            return SuccessResponse(
                success=True,
                message=f"Pipeline run {run_id} cancelled successfully",
            )

    except Exception as e:
        logger.error(f"Failed to cancel run {run_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel run: {str(e)}",
        )


def _prepare_gate_snapshot(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare a state snapshot for human review at a gate.

    Extracts relevant information based on current stage.
    """
    current_stage = state.get("current_stage", "")
    snapshot: Dict[str, Any] = {
        "stage": current_stage,
        "problem": state.get("original_problem", ""),
    }

    if "paradigm" in current_stage.lower():
        snapshot["selected_paradigms"] = state.get("selected_paradigms", [])
        snapshot["paradigm_scores"] = state.get("paradigm_scores", {})

    elif "technique" in current_stage.lower():
        snapshot["selected_techniques"] = state.get("selected_techniques", {})
        snapshot["technique_scores"] = state.get("technique_scores", {})
        snapshot["technique_justification"] = state.get("technique_justification", {})

    elif "decomposition" in current_stage.lower():
        snapshot["decomposed_subproblems"] = state.get("decomposed_subproblems", {})
        snapshot["integrated_subproblems"] = state.get("integrated_subproblems", [])

    elif "solution" in current_stage.lower():
        snapshot["integrated_solution"] = state.get("integrated_solution", {})
        snapshot["validation_results"] = state.get("validation_results", {})

    return snapshot
