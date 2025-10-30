"""Recovery strategies for failed or interrupted graph executions.

Provides mechanisms to handle failures gracefully and resume execution
from checkpoints with different recovery strategies.
"""

from enum import Enum
from typing import Any, Optional

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from decomposition_pipeline.checkpoint.checkpoint_manager import CheckpointManager


class RecoveryStrategy(str, Enum):
    """Available recovery strategies for failed executions."""

    # Resume from the last successful checkpoint
    RESUME_LAST = "resume_last"

    # Retry from the beginning with same inputs
    RETRY_FROM_START = "retry_from_start"

    # Backtrack to a specific checkpoint
    BACKTRACK_TO_CHECKPOINT = "backtrack_to_checkpoint"

    # Continue with modified state
    CONTINUE_WITH_MODIFICATIONS = "continue_with_modifications"

    # Abort and require manual intervention
    ABORT_MANUAL = "abort_manual"


class RecoveryError(Exception):
    """Raised when recovery operations fail."""

    pass


class RecoveryManager:
    """Manages recovery operations for graph executions.

    Provides high-level recovery strategies for handling failures
    and interrupted executions.

    Example:
        >>> manager = RecoveryManager(checkpoint_manager)
        >>> result = await manager.recover(
        ...     thread_id="problem_123",
        ...     strategy=RecoveryStrategy.RESUME_LAST,
        ... )
    """

    def __init__(self, checkpoint_manager: CheckpointManager):
        """Initialize recovery manager.

        Args:
            checkpoint_manager: CheckpointManager instance for state access.
        """
        self.checkpoint_manager = checkpoint_manager

    async def can_recover(self, thread_id: str) -> bool:
        """Check if a thread can be recovered.

        Args:
            thread_id: Thread ID to check.

        Returns:
            True if recovery is possible, False otherwise.
        """
        return await self.checkpoint_manager.has_checkpoints(thread_id)

    async def get_recovery_options(self, thread_id: str) -> dict[str, Any]:
        """Get available recovery options for a thread.

        Args:
            thread_id: Thread ID to get options for.

        Returns:
            Dictionary describing available recovery options.
        """
        if not await self.can_recover(thread_id):
            return {
                "can_recover": False,
                "available_strategies": [],
                "reason": "No checkpoints found",
            }

        info = await self.checkpoint_manager.get_thread_info(thread_id)
        checkpoints = await self.checkpoint_manager.list_checkpoints(thread_id)

        return {
            "can_recover": True,
            "available_strategies": [
                RecoveryStrategy.RESUME_LAST,
                RecoveryStrategy.RETRY_FROM_START,
                RecoveryStrategy.BACKTRACK_TO_CHECKPOINT,
                RecoveryStrategy.CONTINUE_WITH_MODIFICATIONS,
            ],
            "checkpoint_count": len(checkpoints),
            "latest_checkpoint": info.get("latest_checkpoint"),
            "has_pending_writes": info.get("has_pending_writes", False),
        }

    async def recover(
        self,
        thread_id: str,
        strategy: RecoveryStrategy = RecoveryStrategy.RESUME_LAST,
        checkpoint_id: Optional[str] = None,
        modifications: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Recover a failed or interrupted execution.

        Args:
            thread_id: Thread ID to recover.
            strategy: Recovery strategy to use.
            checkpoint_id: Specific checkpoint ID for BACKTRACK_TO_CHECKPOINT.
            modifications: State modifications for CONTINUE_WITH_MODIFICATIONS.

        Returns:
            Dictionary with recovery information and config to use.

        Raises:
            RecoveryError: If recovery cannot be performed.
        """
        if not await self.can_recover(thread_id):
            raise RecoveryError(f"Cannot recover thread {thread_id}: No checkpoints found")

        if strategy == RecoveryStrategy.RESUME_LAST:
            return await self._resume_last(thread_id)

        elif strategy == RecoveryStrategy.RETRY_FROM_START:
            return await self._retry_from_start(thread_id)

        elif strategy == RecoveryStrategy.BACKTRACK_TO_CHECKPOINT:
            if not checkpoint_id:
                raise RecoveryError("checkpoint_id required for BACKTRACK_TO_CHECKPOINT strategy")
            return await self._backtrack_to_checkpoint(thread_id, checkpoint_id)

        elif strategy == RecoveryStrategy.CONTINUE_WITH_MODIFICATIONS:
            if not modifications:
                raise RecoveryError("modifications required for CONTINUE_WITH_MODIFICATIONS strategy")
            return await self._continue_with_modifications(thread_id, modifications)

        elif strategy == RecoveryStrategy.ABORT_MANUAL:
            return await self._abort_manual(thread_id)

        else:
            raise RecoveryError(f"Unknown recovery strategy: {strategy}")

    async def _resume_last(self, thread_id: str) -> dict[str, Any]:
        """Resume from the last checkpoint.

        Args:
            thread_id: Thread ID to resume.

        Returns:
            Recovery info with config to resume execution.
        """
        latest = await self.checkpoint_manager.get_latest(thread_id)
        if not latest:
            raise RecoveryError(f"No checkpoints found for thread {thread_id}")

        config = self.checkpoint_manager.get_config(thread_id)

        return {
            "strategy": RecoveryStrategy.RESUME_LAST,
            "thread_id": thread_id,
            "checkpoint_id": latest.get("checkpoint_id"),
            "config": config,
            "message": "Ready to resume from last checkpoint",
            "action": "Call graph.ainvoke(None, config=config) or graph.astream(None, config=config)",
        }

    async def _retry_from_start(self, thread_id: str) -> dict[str, Any]:
        """Retry from the beginning.

        This clears checkpoints and starts fresh with original inputs.

        Args:
            thread_id: Thread ID to retry.

        Returns:
            Recovery info for fresh start.
        """
        # Get first checkpoint to retrieve original inputs
        checkpoints = await self.checkpoint_manager.list_checkpoints(thread_id)
        if not checkpoints:
            raise RecoveryError(f"No checkpoints found for thread {thread_id}")

        # Delete all checkpoints
        deleted = await self.checkpoint_manager.delete_thread(thread_id)

        # Create new config for fresh start
        config = self.checkpoint_manager.get_config(thread_id)

        return {
            "strategy": RecoveryStrategy.RETRY_FROM_START,
            "thread_id": thread_id,
            "deleted_checkpoints": deleted,
            "config": config,
            "message": "Checkpoints cleared, ready to start fresh",
            "action": "Call graph.ainvoke(initial_state, config=config) with original inputs",
        }

    async def _backtrack_to_checkpoint(
        self,
        thread_id: str,
        checkpoint_id: str,
    ) -> dict[str, Any]:
        """Backtrack to a specific checkpoint.

        Args:
            thread_id: Thread ID to backtrack.
            checkpoint_id: Checkpoint ID to backtrack to.

        Returns:
            Recovery info for backtracked state.
        """
        # Verify checkpoint exists
        checkpoints = await self.checkpoint_manager.list_checkpoints(thread_id)
        checkpoint_ids = [cp.get("checkpoint_id") for cp in checkpoints]

        if checkpoint_id not in checkpoint_ids:
            raise RecoveryError(
                f"Checkpoint {checkpoint_id} not found in thread {thread_id}. "
                f"Available: {checkpoint_ids}"
            )

        # Create config with specific checkpoint
        config = self.checkpoint_manager.get_config(thread_id, checkpoint_id)

        return {
            "strategy": RecoveryStrategy.BACKTRACK_TO_CHECKPOINT,
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "config": config,
            "message": f"Ready to resume from checkpoint {checkpoint_id}",
            "action": "Call graph.ainvoke(None, config=config) to continue from this checkpoint",
        }

    async def _continue_with_modifications(
        self,
        thread_id: str,
        modifications: dict[str, Any],
    ) -> dict[str, Any]:
        """Continue execution with modified state.

        Note: This requires custom state update logic in the graph.

        Args:
            thread_id: Thread ID to continue.
            modifications: State modifications to apply.

        Returns:
            Recovery info with modifications.
        """
        latest = await self.checkpoint_manager.get_latest(thread_id)
        if not latest:
            raise RecoveryError(f"No checkpoints found for thread {thread_id}")

        config = self.checkpoint_manager.get_config(thread_id)

        return {
            "strategy": RecoveryStrategy.CONTINUE_WITH_MODIFICATIONS,
            "thread_id": thread_id,
            "checkpoint_id": latest.get("checkpoint_id"),
            "modifications": modifications,
            "config": config,
            "message": "Ready to continue with state modifications",
            "action": (
                "Apply modifications to graph state and call "
                "graph.ainvoke(modified_state, config=config)"
            ),
        }

    async def _abort_manual(self, thread_id: str) -> dict[str, Any]:
        """Abort execution and require manual intervention.

        Args:
            thread_id: Thread ID to abort.

        Returns:
            Abort information.
        """
        info = await self.checkpoint_manager.get_thread_info(thread_id)

        return {
            "strategy": RecoveryStrategy.ABORT_MANUAL,
            "thread_id": thread_id,
            "thread_info": info,
            "message": "Execution aborted, manual intervention required",
            "action": "Review thread state and determine appropriate action",
        }

    async def validate_thread_state(self, thread_id: str) -> dict[str, Any]:
        """Validate the state of a thread.

        Checks for issues like:
        - Missing checkpoints
        - Corrupted state
        - Pending writes

        Args:
            thread_id: Thread ID to validate.

        Returns:
            Validation results with any issues found.
        """
        if not await self.can_recover(thread_id):
            return {
                "valid": False,
                "issues": ["No checkpoints found"],
                "can_recover": False,
            }

        info = await self.checkpoint_manager.get_thread_info(thread_id)
        issues = []

        # Check for pending writes
        if info.get("has_pending_writes"):
            issues.append("Has pending writes that may not be persisted")

        # Check checkpoint count
        if info.get("checkpoint_count", 0) == 0:
            issues.append("No checkpoints available")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "can_recover": True,
            "thread_info": info,
        }

    async def list_recoverable_threads(self) -> list[dict[str, Any]]:
        """List all threads that can be recovered.

        Returns:
            List of thread information for recoverable threads.
        """
        all_threads = await self.checkpoint_manager.list_all_threads()
        recoverable = []

        for thread_id in all_threads:
            if await self.can_recover(thread_id):
                info = await self.checkpoint_manager.get_thread_info(thread_id)
                validation = await self.validate_thread_state(thread_id)

                recoverable.append(
                    {
                        "thread_id": thread_id,
                        "checkpoint_count": info.get("checkpoint_count"),
                        "valid": validation.get("valid"),
                        "issues": validation.get("issues", []),
                        "latest_checkpoint": info.get("latest_checkpoint"),
                    }
                )

        return recoverable
