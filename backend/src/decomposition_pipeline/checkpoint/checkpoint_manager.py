"""High-level checkpoint management API.

Provides a convenient interface for managing checkpoints across
multiple threads and graph executions.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from decomposition_pipeline.checkpoint.sqlite_saver import (
    create_checkpointer,
    delete_thread_checkpoints,
    get_latest_checkpoint,
    get_thread_checkpoints,
    optimize_database,
)


class CheckpointManager:
    """Manages checkpoints for LangGraph executions.

    Provides high-level operations for checkpoint management including:
    - Creating and configuring checkpointers
    - Querying checkpoint metadata
    - Managing thread state
    - Database maintenance

    Example:
        >>> manager = await CheckpointManager.create("pipeline.db")
        >>> checkpoints = await manager.list_checkpoints("problem_123")
        >>> await manager.resume_thread("problem_123")
    """

    def __init__(self, checkpointer: AsyncSqliteSaver, db_path: Path):
        """Initialize checkpoint manager.

        Args:
            checkpointer: Configured AsyncSqliteSaver instance.
            db_path: Path to the SQLite database.
        """
        self.checkpointer = checkpointer
        self.db_path = db_path

    @classmethod
    async def create(
        cls,
        db_path: str | Path = "checkpoints.db",
    ) -> "CheckpointManager":
        """Create a new checkpoint manager.

        Args:
            db_path: Path to SQLite database file.

        Returns:
            Initialized CheckpointManager instance.

        Note:
            The checkpointer must be used within an async context manager.
            Prefer using CheckpointManager.open() context manager instead.
        """
        db_path = Path(db_path)
        checkpointer_cm = create_checkpointer(db_path)
        # Enter the context manager
        checkpointer = await checkpointer_cm.__aenter__()
        manager = cls(checkpointer, db_path)
        manager._checkpointer_cm = checkpointer_cm  # Store for cleanup
        return manager

    @classmethod
    @asynccontextmanager
    async def open(
        cls,
        db_path: str | Path = "checkpoints.db",
    ) -> "CheckpointManager":
        """Open a checkpoint manager as an async context manager.

        Args:
            db_path: Path to SQLite database file.

        Yields:
            Initialized CheckpointManager instance.

        Example:
            >>> async with CheckpointManager.open("pipeline.db") as manager:
            ...     checkpoints = await manager.list_checkpoints("thread_123")
        """
        db_path = Path(db_path)
        async with create_checkpointer(db_path) as checkpointer:
            yield cls(checkpointer, db_path)

    async def list_checkpoints(
        self,
        thread_id: str,
        limit: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """List all checkpoints for a thread.

        Args:
            thread_id: Thread ID to list checkpoints for.
            limit: Maximum number of checkpoints to return.

        Returns:
            List of checkpoint metadata dictionaries.
        """
        return await get_thread_checkpoints(self.checkpointer, thread_id, limit)

    async def get_latest(self, thread_id: str) -> Optional[dict[str, Any]]:
        """Get the most recent checkpoint for a thread.

        Args:
            thread_id: Thread ID to get checkpoint for.

        Returns:
            Checkpoint metadata dict or None.
        """
        return await get_latest_checkpoint(self.checkpointer, thread_id)

    async def has_checkpoints(self, thread_id: str) -> bool:
        """Check if a thread has any checkpoints.

        Args:
            thread_id: Thread ID to check.

        Returns:
            True if checkpoints exist, False otherwise.
        """
        latest = await self.get_latest(thread_id)
        return latest is not None

    async def delete_thread(self, thread_id: str) -> int:
        """Delete all checkpoints for a thread.

        Args:
            thread_id: Thread ID to delete checkpoints for.

        Returns:
            Number of checkpoints deleted.
        """
        return await delete_thread_checkpoints(self.checkpointer, thread_id, self.db_path)

    async def get_thread_info(self, thread_id: str) -> dict[str, Any]:
        """Get summary information about a thread.

        Args:
            thread_id: Thread ID to get info for.

        Returns:
            Dictionary with thread information including:
            - thread_id: The thread identifier
            - checkpoint_count: Number of checkpoints
            - latest_checkpoint: Most recent checkpoint metadata
            - has_pending_writes: Whether there are pending writes
        """
        checkpoints = await self.list_checkpoints(thread_id)
        latest = checkpoints[0] if checkpoints else None

        return {
            "thread_id": thread_id,
            "checkpoint_count": len(checkpoints),
            "latest_checkpoint": latest,
            "has_pending_writes": bool(latest and latest.get("pending_writes")) if latest else False,
        }

    async def optimize(self) -> None:
        """Optimize the checkpoint database.

        Runs VACUUM and ANALYZE to reclaim space and update statistics.
        Should be run periodically for better performance.
        """
        await optimize_database(self.db_path)

    def get_config(self, thread_id: str, checkpoint_id: Optional[str] = None) -> dict[str, Any]:
        """Get LangGraph config for a thread.

        Args:
            thread_id: Thread ID for the execution.
            checkpoint_id: Optional specific checkpoint to resume from.

        Returns:
            Configuration dict for LangGraph graph.invoke() or graph.astream().
        """
        config: dict[str, Any] = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        if checkpoint_id:
            config["configurable"]["checkpoint_id"] = checkpoint_id

        return config

    async def list_all_threads(self) -> list[str]:
        """List all thread IDs that have checkpoints.

        Returns:
            List of thread IDs.

        Note:
            This requires direct database access and may be slow
            for databases with many checkpoints.
        """
        import aiosqlite
        import sqlite3

        threads = []
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT DISTINCT thread_id FROM checkpoints") as cursor:
                    async for row in cursor:
                        threads.append(row[0])
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            pass

        return threads

    async def get_checkpoint_count(self) -> int:
        """Get total number of checkpoints in the database.

        Returns:
            Total checkpoint count across all threads.
        """
        import aiosqlite
        import sqlite3

        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("SELECT COUNT(*) FROM checkpoints") as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return 0

    async def get_database_size(self) -> int:
        """Get the size of the checkpoint database in bytes.

        Returns:
            Database file size in bytes. Returns 0 if database doesn't exist.
        """
        try:
            return self.db_path.stat().st_size if self.db_path.exists() else 0
        except (OSError, FileNotFoundError):
            return 0

    async def cleanup_old_checkpoints(
        self,
        thread_id: str,
        keep_count: int = 10,
    ) -> int:
        """Keep only the N most recent checkpoints for a thread.

        Args:
            thread_id: Thread ID to cleanup.
            keep_count: Number of recent checkpoints to keep.

        Returns:
            Number of checkpoints deleted.

        Note:
            This is useful for preventing unbounded checkpoint growth.
        """
        # Get all checkpoints
        checkpoints = await self.list_checkpoints(thread_id)

        if len(checkpoints) <= keep_count:
            return 0

        # Checkpoints to delete (older than keep_count)
        to_delete = checkpoints[keep_count:]

        # Delete each checkpoint
        # Note: This is a simplified implementation
        # In practice, you'd want to delete by checkpoint_id
        deleted = 0
        import aiosqlite

        async with aiosqlite.connect(self.db_path) as db:
            for checkpoint in to_delete:
                checkpoint_id = checkpoint.get("checkpoint_id")
                if checkpoint_id:
                    await db.execute(
                        "DELETE FROM checkpoints WHERE checkpoint_id = ?",
                        (checkpoint_id,),
                    )
                    deleted += 1
            await db.commit()

        return deleted

    async def export_thread_state(self, thread_id: str) -> dict[str, Any]:
        """Export complete state for a thread.

        Args:
            thread_id: Thread ID to export.

        Returns:
            Dictionary containing thread metadata and all checkpoints.
        """
        info = await self.get_thread_info(thread_id)
        checkpoints = await self.list_checkpoints(thread_id)

        return {
            "thread_id": thread_id,
            "exported_at": datetime.now().isoformat(),
            "metadata": info,
            "checkpoints": checkpoints,
        }

    async def close(self) -> None:
        """Close the checkpoint manager and cleanup resources."""
        # AsyncSqliteSaver will handle cleanup automatically
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
