"""SQLite-based checkpoint saver for LangGraph.

This module provides async SQLite checkpoint persistence using aiosqlite.
Checkpoints are stored per thread_id for state isolation.
"""

import asyncio
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, AsyncContextManager

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


def create_checkpointer(
    db_path: str | Path = "checkpoints.db",
) -> AsyncContextManager[AsyncSqliteSaver]:
    """Create an async SQLite checkpointer.

    Args:
        db_path: Path to SQLite database file. Defaults to "checkpoints.db"
                in the current directory.

    Returns:
        AsyncContextManager that yields AsyncSqliteSaver configured for checkpoint persistence.

    Example:
        >>> async with create_checkpointer("pipeline.db") as checkpointer:
        ...     graph = graph.compile(checkpointer=checkpointer)
        ...     result = await graph.ainvoke(...)
    """
    db_path = Path(db_path)

    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # AsyncSqliteSaver.from_conn_string returns an async context manager
    return AsyncSqliteSaver.from_conn_string(str(db_path))


async def get_thread_checkpoints(
    checkpointer: AsyncSqliteSaver,
    thread_id: str,
    limit: Optional[int] = None,
) -> list[dict]:
    """Get all checkpoints for a specific thread.

    Args:
        checkpointer: The checkpointer to query.
        thread_id: Thread ID to get checkpoints for.
        limit: Maximum number of checkpoints to return (most recent first).
               None returns all checkpoints.

    Returns:
        List of checkpoint metadata dictionaries, sorted by most recent first.
    """
    checkpoints = []

    config = {"configurable": {"thread_id": thread_id}}

    # Use alist to get checkpoint tuples
    try:
        async for checkpoint_tuple in checkpointer.alist(config):
            checkpoints.append(
                {
                    "checkpoint_id": checkpoint_tuple.checkpoint["id"],
                    "thread_id": thread_id,
                    "parent_checkpoint_id": (
                        checkpoint_tuple.parent_config["configurable"].get("checkpoint_id")
                        if checkpoint_tuple.parent_config
                        else None
                    ),
                    "metadata": checkpoint_tuple.metadata,
                    "pending_writes": checkpoint_tuple.pending_writes if hasattr(checkpoint_tuple, 'pending_writes') else [],
                }
            )

            if limit and len(checkpoints) >= limit:
                break
    except Exception:
        # If alist fails, return empty list
        pass

    return checkpoints


async def get_latest_checkpoint(
    checkpointer: AsyncSqliteSaver,
    thread_id: str,
) -> Optional[dict]:
    """Get the most recent checkpoint for a thread.

    Args:
        checkpointer: The checkpointer to query.
        thread_id: Thread ID to get checkpoint for.

    Returns:
        Checkpoint metadata dict or None if no checkpoints exist.
    """
    checkpoints = await get_thread_checkpoints(checkpointer, thread_id, limit=1)
    return checkpoints[0] if checkpoints else None


async def delete_thread_checkpoints(
    checkpointer: AsyncSqliteSaver,
    thread_id: str,
    db_path: str | Path,
) -> int:
    """Delete all checkpoints for a specific thread.

    Args:
        checkpointer: The checkpointer to operate on (unused, kept for API compatibility).
        thread_id: Thread ID to delete checkpoints for.
        db_path: Path to the database file.

    Returns:
        Number of checkpoints deleted.

    Note:
        This is a destructive operation and cannot be undone.
    """
    import aiosqlite

    # Direct database access to delete checkpoints
    async with aiosqlite.connect(db_path) as db:
        try:
            # First count
            async with db.execute(
                "SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?",
                (thread_id,),
            ) as cursor:
                row = await cursor.fetchone()
                count = row[0] if row else 0

            # Then delete
            if count > 0:
                await db.execute(
                    "DELETE FROM checkpoints WHERE thread_id = ?",
                    (thread_id,),
                )
                await db.commit()

            return count
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return 0


async def optimize_database(db_path: str | Path) -> None:
    """Optimize the SQLite database.

    Runs VACUUM and ANALYZE to reclaim space and update statistics.

    Args:
        db_path: Path to the SQLite database file.
    """
    import aiosqlite

    async with aiosqlite.connect(db_path) as db:
        await db.execute("VACUUM")
        await db.execute("ANALYZE")
        await db.commit()
