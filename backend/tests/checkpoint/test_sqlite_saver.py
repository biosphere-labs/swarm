"""Tests for SQLite checkpoint saver."""

import pytest
from pathlib import Path
import tempfile
import shutil

from decomposition_pipeline.checkpoint.sqlite_saver import (
    create_checkpointer,
    get_thread_checkpoints,
    get_latest_checkpoint,
    delete_thread_checkpoints,
    optimize_database,
)


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test.db"

    yield db_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
async def checkpointer(temp_db):
    """Create a test checkpointer."""
    async with create_checkpointer(temp_db) as cp:
        yield cp


@pytest.mark.asyncio
async def test_create_checkpointer(temp_db):
    """Test creating a checkpointer."""
    async with create_checkpointer(temp_db) as checkpointer:
        assert checkpointer is not None
        assert temp_db.exists()


@pytest.mark.asyncio
async def test_create_checkpointer_creates_parent_dir():
    """Test that create_checkpointer creates parent directories."""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "subdir" / "another" / "test.db"

    try:
        async with create_checkpointer(db_path) as checkpointer:
            assert checkpointer is not None
            assert db_path.exists()
            assert db_path.parent.exists()
    finally:
        shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_get_thread_checkpoints_empty(checkpointer):
    """Test getting checkpoints for a thread with no checkpoints."""
    checkpoints = await get_thread_checkpoints(checkpointer, "test_thread")

    assert checkpoints == []


@pytest.mark.asyncio
async def test_get_latest_checkpoint_none(checkpointer):
    """Test getting latest checkpoint when none exist."""
    latest = await get_latest_checkpoint(checkpointer, "test_thread")

    assert latest is None


@pytest.mark.asyncio
async def test_delete_thread_checkpoints_empty(checkpointer, temp_db):
    """Test deleting checkpoints for a thread with no checkpoints."""
    count = await delete_thread_checkpoints(checkpointer, "test_thread", temp_db)

    assert count == 0


@pytest.mark.asyncio
async def test_optimize_database(temp_db):
    """Test database optimization."""
    async with create_checkpointer(temp_db) as checkpointer:
        pass  # Just create the database

    # Should not raise an error
    await optimize_database(temp_db)

    # Database should still exist
    assert temp_db.exists()


@pytest.mark.asyncio
async def test_checkpointer_with_graph(checkpointer):
    """Test using checkpointer with a simple LangGraph."""
    from langgraph.graph import StateGraph
    from typing import TypedDict

    class State(TypedDict):
        value: int

    def increment(state: State) -> State:
        return {"value": state["value"] + 1}

    # Create a simple graph
    graph = StateGraph(State)
    graph.add_node("increment", increment)
    graph.set_entry_point("increment")
    graph.set_finish_point("increment")

    # Compile with checkpointer
    compiled = graph.compile(checkpointer=checkpointer)

    # Run the graph
    thread_id = "test_graph_thread"
    config = {"configurable": {"thread_id": thread_id}}

    result = await compiled.ainvoke({"value": 0}, config=config)

    assert result["value"] == 1

    # Verify checkpoint was created
    checkpoints = await get_thread_checkpoints(checkpointer, thread_id)
    assert len(checkpoints) > 0


@pytest.mark.asyncio
async def test_checkpoint_isolation(checkpointer):
    """Test that checkpoints are isolated by thread_id."""
    from langgraph.graph import StateGraph
    from typing import TypedDict

    class State(TypedDict):
        value: int

    def increment(state: State) -> State:
        return {"value": state["value"] + 1}

    graph = StateGraph(State)
    graph.add_node("increment", increment)
    graph.set_entry_point("increment")
    graph.set_finish_point("increment")

    compiled = graph.compile(checkpointer=checkpointer)

    # Run with two different threads
    result1 = await compiled.ainvoke(
        {"value": 0},
        config={"configurable": {"thread_id": "thread1"}},
    )
    result2 = await compiled.ainvoke(
        {"value": 100},
        config={"configurable": {"thread_id": "thread2"}},
    )

    assert result1["value"] == 1
    assert result2["value"] == 101

    # Verify each thread has its own checkpoints
    checkpoints1 = await get_thread_checkpoints(checkpointer, "thread1")
    checkpoints2 = await get_thread_checkpoints(checkpointer, "thread2")

    assert len(checkpoints1) > 0
    assert len(checkpoints2) > 0
