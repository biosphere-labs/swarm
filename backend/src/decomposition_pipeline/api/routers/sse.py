"""
Server-Sent Events (SSE) endpoint for real-time pipeline updates.

Provides a streaming endpoint that sends real-time updates about pipeline
execution to connected clients.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from decomposition_pipeline.api.routers.pipeline import _active_runs

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/pipeline",
    tags=["sse", "pipeline"],
)


@router.get(
    "/{run_id}/stream",
    summary="Stream pipeline updates",
    description="Server-Sent Events endpoint for real-time pipeline state updates.",
)
async def stream_pipeline_updates(run_id: str):
    """
    Stream real-time updates for a pipeline run via SSE.

    Args:
        run_id: Pipeline run identifier

    Returns:
        EventSourceResponse with SSE stream

    Raises:
        HTTPException: If run not found
    """
    if run_id not in _active_runs:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline run {run_id} not found",
        )

    logger.info(f"Client connected to SSE stream for run {run_id}")

    async def event_generator() -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate SSE events for pipeline updates.

        Yields:
            Event dictionaries with update data
        """
        try:
            run_info = _active_runs.get(run_id)
            if not run_info:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": "Run not found"}),
                }
                return

            # Send initial state
            checkpointer = run_info.get("checkpointer")
            config = run_info.get("config")

            if checkpointer and config:
                checkpoint = checkpointer.get(config)
                if checkpoint:
                    state = checkpoint.get("channel_values", {})
                    yield {
                        "event": "state_update",
                        "data": json.dumps({
                            "run_id": run_id,
                            "status": run_info.get("status", "unknown"),
                            "current_stage": state.get("current_stage", "unknown"),
                            "timestamp": state.get("started_at"),
                        }),
                    }

            # Poll for updates
            last_stage = None
            last_status = None

            while True:
                # Check if run still exists
                run_info = _active_runs.get(run_id)
                if not run_info:
                    yield {
                        "event": "error",
                        "data": json.dumps({"error": "Run no longer exists"}),
                    }
                    break

                # Get current status
                current_status = run_info.get("status", "unknown")

                # Get current state
                checkpoint = checkpointer.get(config) if checkpointer and config else None
                state = checkpoint.get("channel_values", {}) if checkpoint else {}
                current_stage = state.get("current_stage", "unknown")

                # Check if status changed
                if current_status != last_status:
                    yield {
                        "event": "status_change",
                        "data": json.dumps({
                            "run_id": run_id,
                            "status": current_status,
                            "timestamp": state.get("updated_at"),
                        }),
                    }
                    last_status = current_status

                # Check if stage changed
                if current_stage != last_stage:
                    yield {
                        "event": "stage_change",
                        "data": json.dumps({
                            "run_id": run_id,
                            "stage": current_stage,
                            "timestamp": state.get("updated_at"),
                        }),
                    }
                    last_stage = current_stage

                # Check if approval is required
                if state.get("awaiting_approval", False):
                    yield {
                        "event": "approval_required",
                        "data": json.dumps({
                            "run_id": run_id,
                            "gate": state.get("current_gate", "unknown"),
                            "stage": current_stage,
                        }),
                    }

                # Check if completed or failed
                if current_status in ["completed", "failed", "cancelled"]:
                    yield {
                        "event": "pipeline_finished",
                        "data": json.dumps({
                            "run_id": run_id,
                            "status": current_status,
                            "completed_at": run_info.get("completed_at"),
                        }),
                    }
                    break

                # Send periodic heartbeat
                yield {
                    "event": "heartbeat",
                    "data": json.dumps({
                        "run_id": run_id,
                        "timestamp": state.get("updated_at"),
                    }),
                }

                # Wait before next poll
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for run {run_id}")
            raise
        except Exception as e:
            logger.error(f"Error in SSE stream for run {run_id}: {str(e)}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())
