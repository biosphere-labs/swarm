"""Tests for checkpoint manager."""

import pytest
from pathlib import Path
import tempfile
import shutil

from decomposition_pipeline.checkpoint.checkpoint_manager import CheckpointManager


@pytest.fixture
async def temp_db():
    """Create a temporary database for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "test.db"

    yield db_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
async def manager(temp_db):
    """Create a test checkpoint manager."""
    async with CheckpointManager.open(temp_db) as mgr:
        yield mgr


@pytest.mark.asyncio
async def test_create_manager(temp_db):
    """Test creating a checkpoint manager."""
    async with CheckpointManager.open(temp_db) as manager:
        assert manager is not None
        assert manager.db_path == temp_db


@pytest.mark.asyncio
async def test_list_checkpoints_empty(manager):
    """Test listing checkpoints when none exist."""
    checkpoints = await manager.list_checkpoints("test_thread")

    assert checkpoints == []


@pytest.mark.asyncio
async def test_get_latest_none(manager):
    """Test getting latest checkpoint when none exist."""
    latest = await manager.get_latest("test_thread")

    assert latest is None


@pytest.mark.asyncio
async def test_has_checkpoints_false(manager):
    """Test has_checkpoints when none exist."""
    has_checkpoints = await manager.has_checkpoints("test_thread")

    assert has_checkpoints is False


@pytest.mark.asyncio
async def test_get_thread_info_empty(manager):
    """Test getting thread info when no checkpoints exist."""
    info = await manager.get_thread_info("test_thread")

    assert info["thread_id"] == "test_thread"
    assert info["checkpoint_count"] == 0
    assert info["latest_checkpoint"] is None
    assert info["has_pending_writes"] is False


@pytest.mark.asyncio
async def test_get_config(manager):
    """Test getting LangGraph config."""
    config = manager.get_config("test_thread")

    assert config["configurable"]["thread_id"] == "test_thread"
    assert "checkpoint_id" not in config["configurable"]


@pytest.mark.asyncio
async def test_get_config_with_checkpoint(manager):
    """Test getting LangGraph config with specific checkpoint."""
    config = manager.get_config("test_thread", "checkpoint_123")

    assert config["configurable"]["thread_id"] == "test_thread"
    assert config["configurable"]["checkpoint_id"] == "checkpoint_123"


@pytest.mark.asyncio
async def test_list_all_threads_empty(manager):
    """Test listing all threads when none exist."""
    threads = await manager.list_all_threads()

    assert threads == []


@pytest.mark.asyncio
async def test_get_checkpoint_count_zero(manager):
    """Test getting checkpoint count when none exist."""
    count = await manager.get_checkpoint_count()

    assert count == 0


@pytest.mark.asyncio
async def test_get_database_size(manager):
    """Test getting database size."""
    size = await manager.get_database_size()

    # Database should exist and have some size (or 0 if just created)
    assert size >= 0


@pytest.mark.asyncio
async def test_context_manager(temp_db):
    """Test using CheckpointManager as async context manager."""
    async with CheckpointManager.open(temp_db) as manager:
        assert manager is not None
        info = await manager.get_thread_info("test")
        assert info["thread_id"] == "test"


@pytest.mark.asyncio
async def test_manager_with_graph(manager):
    """Test using manager with a LangGraph."""
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

    compiled = graph.compile(checkpointer=manager.checkpointer)

    # Run the graph
    thread_id = "test_thread"
    config = manager.get_config(thread_id)

    result = await compiled.ainvoke({"value": 0}, config=config)

    assert result["value"] == 1

    # Verify checkpoint was created
    assert await manager.has_checkpoints(thread_id)
    checkpoints = await manager.list_checkpoints(thread_id)
    assert len(checkpoints) > 0

    info = await manager.get_thread_info(thread_id)
    assert info["checkpoint_count"] > 0


@pytest.mark.asyncio
async def test_delete_thread(manager):
    """Test deleting a thread's checkpoints."""
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

    compiled = graph.compile(checkpointer=manager.checkpointer)

    # Create some checkpoints
    thread_id = "delete_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Verify checkpoints exist
    assert await manager.has_checkpoints(thread_id)

    # Delete
    deleted = await manager.delete_thread(thread_id)
    assert deleted > 0

    # Verify gone
    assert not await manager.has_checkpoints(thread_id)


@pytest.mark.asyncio
async def test_export_thread_state(manager):
    """Test exporting thread state."""
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

    compiled = graph.compile(checkpointer=manager.checkpointer)

    # Create checkpoint
    thread_id = "export_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Export
    exported = await manager.export_thread_state(thread_id)

    assert exported["thread_id"] == thread_id
    assert "exported_at" in exported
    assert "metadata" in exported
    assert "checkpoints" in exported
    assert len(exported["checkpoints"]) > 0


@pytest.mark.asyncio
async def test_optimize(manager):
    """Test database optimization."""
    # Should not raise an error
    await manager.optimize()


@pytest.mark.asyncio
async def test_cleanup_old_checkpoints(manager):
    """Test cleaning up old checkpoints."""
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

    compiled = graph.compile(checkpointer=manager.checkpointer)

    # Create multiple checkpoints
    thread_id = "cleanup_test_thread"
    config = manager.get_config(thread_id)

    for i in range(5):
        await compiled.ainvoke({"value": i}, config=config)

    # Verify we have checkpoints
    checkpoints = await manager.list_checkpoints(thread_id)
    initial_count = len(checkpoints)
    assert initial_count > 0

    # Cleanup, keeping only 2
    deleted = await manager.cleanup_old_checkpoints(thread_id, keep_count=2)

    # Should have deleted some (if we had more than 2)
    if initial_count > 2:
        assert deleted == initial_count - 2

        # Verify only 2 remain
        remaining = await manager.list_checkpoints(thread_id)
        assert len(remaining) == 2
