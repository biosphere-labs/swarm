"""Tests for recovery strategies."""

import pytest
from pathlib import Path
import tempfile
import shutil

from decomposition_pipeline.checkpoint.checkpoint_manager import CheckpointManager
from decomposition_pipeline.checkpoint.recovery import (
    RecoveryStrategy,
    RecoveryManager,
    RecoveryError,
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
async def manager(temp_db):
    """Create a test checkpoint manager."""
    async with CheckpointManager.open(temp_db) as mgr:
        yield mgr


@pytest.fixture
async def recovery_manager(manager):
    """Create a test recovery manager."""
    return RecoveryManager(manager)


@pytest.mark.asyncio
async def test_can_recover_false(recovery_manager):
    """Test can_recover returns False when no checkpoints exist."""
    can_recover = await recovery_manager.can_recover("test_thread")

    assert can_recover is False


@pytest.mark.asyncio
async def test_get_recovery_options_no_checkpoints(recovery_manager):
    """Test getting recovery options when no checkpoints exist."""
    options = await recovery_manager.get_recovery_options("test_thread")

    assert options["can_recover"] is False
    assert options["available_strategies"] == []
    assert "reason" in options


@pytest.mark.asyncio
async def test_recover_no_checkpoints_fails(recovery_manager):
    """Test that recovery fails when no checkpoints exist."""
    with pytest.raises(RecoveryError):
        await recovery_manager.recover("test_thread")


@pytest.mark.asyncio
async def test_validate_thread_state_no_checkpoints(recovery_manager):
    """Test validating thread state when no checkpoints exist."""
    validation = await recovery_manager.validate_thread_state("test_thread")

    assert validation["valid"] is False
    assert "No checkpoints found" in validation["issues"]
    assert validation["can_recover"] is False


@pytest.mark.asyncio
async def test_list_recoverable_threads_empty(recovery_manager):
    """Test listing recoverable threads when none exist."""
    threads = await recovery_manager.list_recoverable_threads()

    assert threads == []


@pytest.mark.asyncio
async def test_recovery_with_graph(recovery_manager, manager):
    """Test recovery strategies with a simple graph."""
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

    # Run the graph to create checkpoints
    thread_id = "recovery_test_thread"
    config = manager.get_config(thread_id)
    result = await compiled.ainvoke({"value": 0}, config=config)

    assert result["value"] == 1

    # Now test recovery
    can_recover = await recovery_manager.can_recover(thread_id)
    assert can_recover is True


@pytest.mark.asyncio
async def test_resume_last_strategy(recovery_manager, manager):
    """Test RESUME_LAST recovery strategy."""
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

    # Create checkpoints
    thread_id = "resume_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Test resume
    recovery_info = await recovery_manager.recover(
        thread_id,
        strategy=RecoveryStrategy.RESUME_LAST,
    )

    assert recovery_info["strategy"] == RecoveryStrategy.RESUME_LAST
    assert recovery_info["thread_id"] == thread_id
    assert "config" in recovery_info
    assert "message" in recovery_info


@pytest.mark.asyncio
async def test_retry_from_start_strategy(recovery_manager, manager):
    """Test RETRY_FROM_START recovery strategy."""
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

    # Create checkpoints
    thread_id = "retry_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Verify checkpoints exist
    assert await manager.has_checkpoints(thread_id)

    # Test retry from start
    recovery_info = await recovery_manager.recover(
        thread_id,
        strategy=RecoveryStrategy.RETRY_FROM_START,
    )

    assert recovery_info["strategy"] == RecoveryStrategy.RETRY_FROM_START
    assert recovery_info["deleted_checkpoints"] > 0

    # Verify checkpoints were deleted
    assert not await manager.has_checkpoints(thread_id)


@pytest.mark.asyncio
async def test_backtrack_to_checkpoint_strategy(recovery_manager, manager):
    """Test BACKTRACK_TO_CHECKPOINT recovery strategy."""
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

    # Create checkpoints
    thread_id = "backtrack_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Get checkpoint to backtrack to
    checkpoints = await manager.list_checkpoints(thread_id)
    assert len(checkpoints) > 0
    checkpoint_id = checkpoints[0]["checkpoint_id"]

    # Test backtrack
    recovery_info = await recovery_manager.recover(
        thread_id,
        strategy=RecoveryStrategy.BACKTRACK_TO_CHECKPOINT,
        checkpoint_id=checkpoint_id,
    )

    assert recovery_info["strategy"] == RecoveryStrategy.BACKTRACK_TO_CHECKPOINT
    assert recovery_info["checkpoint_id"] == checkpoint_id


@pytest.mark.asyncio
async def test_backtrack_without_checkpoint_id_fails(recovery_manager, manager):
    """Test that backtrack fails without checkpoint_id."""
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

    thread_id = "backtrack_fail_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Try backtrack without checkpoint_id
    with pytest.raises(RecoveryError, match="checkpoint_id required"):
        await recovery_manager.recover(
            thread_id,
            strategy=RecoveryStrategy.BACKTRACK_TO_CHECKPOINT,
        )


@pytest.mark.asyncio
async def test_backtrack_invalid_checkpoint_fails(recovery_manager, manager):
    """Test that backtrack fails with invalid checkpoint_id."""
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

    thread_id = "invalid_checkpoint_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Try backtrack with invalid checkpoint_id
    with pytest.raises(RecoveryError, match="not found"):
        await recovery_manager.recover(
            thread_id,
            strategy=RecoveryStrategy.BACKTRACK_TO_CHECKPOINT,
            checkpoint_id="invalid_checkpoint_123",
        )


@pytest.mark.asyncio
async def test_continue_with_modifications_strategy(recovery_manager, manager):
    """Test CONTINUE_WITH_MODIFICATIONS recovery strategy."""
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

    thread_id = "modify_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Test continue with modifications
    modifications = {"value": 100}
    recovery_info = await recovery_manager.recover(
        thread_id,
        strategy=RecoveryStrategy.CONTINUE_WITH_MODIFICATIONS,
        modifications=modifications,
    )

    assert recovery_info["strategy"] == RecoveryStrategy.CONTINUE_WITH_MODIFICATIONS
    assert recovery_info["modifications"] == modifications


@pytest.mark.asyncio
async def test_continue_without_modifications_fails(recovery_manager, manager):
    """Test that continue fails without modifications."""
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

    thread_id = "modify_fail_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Try continue without modifications
    with pytest.raises(RecoveryError, match="modifications required"):
        await recovery_manager.recover(
            thread_id,
            strategy=RecoveryStrategy.CONTINUE_WITH_MODIFICATIONS,
        )


@pytest.mark.asyncio
async def test_abort_manual_strategy(recovery_manager, manager):
    """Test ABORT_MANUAL recovery strategy."""
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

    thread_id = "abort_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Test abort
    recovery_info = await recovery_manager.recover(
        thread_id,
        strategy=RecoveryStrategy.ABORT_MANUAL,
    )

    assert recovery_info["strategy"] == RecoveryStrategy.ABORT_MANUAL
    assert "thread_info" in recovery_info


@pytest.mark.asyncio
async def test_get_recovery_options_with_checkpoints(recovery_manager, manager):
    """Test getting recovery options when checkpoints exist."""
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

    thread_id = "options_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Get recovery options
    options = await recovery_manager.get_recovery_options(thread_id)

    assert options["can_recover"] is True
    assert len(options["available_strategies"]) > 0
    assert options["checkpoint_count"] > 0


@pytest.mark.asyncio
async def test_validate_thread_state_valid(recovery_manager, manager):
    """Test validating valid thread state."""
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

    thread_id = "validate_test_thread"
    config = manager.get_config(thread_id)
    await compiled.ainvoke({"value": 0}, config=config)

    # Validate
    validation = await recovery_manager.validate_thread_state(thread_id)

    assert validation["can_recover"] is True
    assert "thread_info" in validation


@pytest.mark.asyncio
async def test_list_recoverable_threads(recovery_manager, manager):
    """Test listing recoverable threads."""
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

    # Create checkpoints for multiple threads
    for i in range(3):
        thread_id = f"recoverable_thread_{i}"
        config = manager.get_config(thread_id)
        await compiled.ainvoke({"value": i}, config=config)

    # List recoverable threads
    threads = await recovery_manager.list_recoverable_threads()

    assert len(threads) == 3
    for thread in threads:
        assert "thread_id" in thread
        assert "checkpoint_count" in thread
        assert thread["checkpoint_count"] > 0
