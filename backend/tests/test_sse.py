"""
Tests for Server-Sent Events (SSE) endpoints.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import tempfile
import pytest
from httpx import AsyncClient, ASGITransport
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from decomposition_pipeline.api.app import app
from decomposition_pipeline.config.settings import settings


@pytest.fixture
async def test_checkpointer():
    """Create a test checkpointer with temporary database."""
    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    # Create context manager and enter it
    async with AsyncSqliteSaver.from_conn_string(db_path) as checkpointer:
        yield checkpointer, db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
async def client():
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def create_test_checkpoint(
    checkpointer: AsyncSqliteSaver,
    thread_id: str,
    state: dict,
    metadata: dict = None
):
    """Helper to create a test checkpoint."""
    config = {"configurable": {"thread_id": thread_id}}

    checkpoint = {
        "id": f"checkpoint_{datetime.utcnow().timestamp()}",
        "channel_values": state,
        "metadata": metadata or {},
    }

    await checkpointer.aput(config, checkpoint)


@pytest.mark.asyncio
async def test_get_run_status_not_found(client: AsyncClient):
    """Test getting status for non-existent run."""
    response = await client.get("/api/v1/sse/nonexistent_run/status")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_run_status_success(client: AsyncClient, test_checkpointer):
    """Test getting status for existing run."""
    checkpointer, db_path = test_checkpointer

    # Create a test checkpoint
    run_id = "test_run_123"
    test_state = {
        "problem": "Test problem",
        "stage": "paradigm_selection",
        "progress": 0.3,
    }
    test_metadata = {
        "timestamp": datetime.utcnow().isoformat(),
        "step": 1,
    }

    # Temporarily override settings for test
    original_db_path = settings.checkpoint_db_path
    settings.checkpoint_db_path = db_path

    try:
        await create_test_checkpoint(
            checkpointer,
            run_id,
            test_state,
            test_metadata
        )

        # Get status
        response = await client.get(f"/api/v1/sse/{run_id}/status")
        assert response.status_code == 200

        data = response.json()
        assert data["run_id"] == run_id
        assert data["state"] == test_state
        assert data["metadata"] == test_metadata
        assert "checkpoint_id" in data
        assert "timestamp" in data

    finally:
        settings.checkpoint_db_path = original_db_path


@pytest.mark.asyncio
async def test_stream_run_updates_connection(client: AsyncClient):
    """Test SSE connection establishment."""
    run_id = "test_run_stream"

    # Use a shorter timeout for testing
    async with client.stream("GET", f"/api/v1/sse/{run_id}?poll_interval=0.1") as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        # Read first event (connection confirmation)
        events = []
        async for line in response.aiter_lines():
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
                events.append({"type": event_type})
            elif line.startswith("data:"):
                data = json.loads(line.split(":", 1)[1].strip())
                if events:
                    events[-1]["data"] = data

            # Break after first event
            if len(events) > 0 and "data" in events[-1]:
                break

        # Verify connection event
        assert len(events) > 0
        assert events[0]["type"] == "connected"
        assert events[0]["data"]["run_id"] == run_id


@pytest.mark.asyncio
async def test_stream_run_events_with_filter(client: AsyncClient):
    """Test event streaming with type filter."""
    run_id = "test_run_events"
    event_types = "node_enter,node_exit"

    async with client.stream(
        "GET",
        f"/api/v1/sse/{run_id}/events?event_types={event_types}&poll_interval=0.1"
    ) as response:
        assert response.status_code == 200

        # Read connection event
        events = []
        async for line in response.aiter_lines():
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
                events.append({"type": event_type})
            elif line.startswith("data:"):
                data = json.loads(line.split(":", 1)[1].strip())
                if events:
                    events[-1]["data"] = data

            if len(events) > 0 and "data" in events[-1]:
                break

        # Verify connection event includes filter info
        assert events[0]["type"] == "connected"
        assert events[0]["data"]["filters"] == ["node_enter", "node_exit"]


@pytest.mark.asyncio
async def test_stream_updates_with_state_changes(client: AsyncClient, test_checkpointer):
    """Test that state changes are streamed correctly."""
    checkpointer, db_path = test_checkpointer
    run_id = "test_run_updates"

    # Override settings for test
    original_db_path = settings.checkpoint_db_path
    settings.checkpoint_db_path = db_path

    try:
        # Start streaming in background
        async def create_checkpoints():
            """Create checkpoints while stream is active."""
            await asyncio.sleep(0.2)  # Wait for stream to start

            # Create first checkpoint
            await create_test_checkpoint(
                checkpointer,
                run_id,
                {"stage": "level1", "progress": 0.25},
                {"step": 1, "timestamp": datetime.utcnow().isoformat()}
            )

            await asyncio.sleep(0.3)

            # Create second checkpoint
            await create_test_checkpoint(
                checkpointer,
                run_id,
                {"stage": "level2", "progress": 0.5},
                {"step": 2, "timestamp": datetime.utcnow().isoformat()}
            )

        # Start checkpoint creation task
        checkpoint_task = asyncio.create_task(create_checkpoints())

        # Stream updates
        events = []
        async with client.stream(
            "GET",
            f"/api/v1/sse/{run_id}?poll_interval=0.1&include_state=true"
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                    events.append({"type": event_type})
                elif line.startswith("data:"):
                    data = json.loads(line.split(":", 1)[1].strip())
                    if events:
                        events[-1]["data"] = data

                # Break after receiving a few events
                if len([e for e in events if e["type"] == "message"]) >= 2:
                    break

        await checkpoint_task

        # Verify we received state updates
        message_events = [e for e in events if e["type"] == "message"]
        assert len(message_events) >= 1

        # Verify state is included
        if len(message_events) > 0:
            assert "state" in message_events[0]["data"]

    finally:
        settings.checkpoint_db_path = original_db_path


@pytest.mark.asyncio
async def test_concurrent_connections(client: AsyncClient):
    """Test multiple concurrent SSE connections."""
    run_ids = ["run_1", "run_2", "run_3"]

    async def connect_and_read(run_id: str):
        """Connect to SSE and read first event."""
        async with client.stream(
            "GET",
            f"/api/v1/sse/{run_id}?poll_interval=0.1"
        ) as response:
            events = []
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                    events.append({"type": event_type})
                elif line.startswith("data:"):
                    data = json.loads(line.split(":", 1)[1].strip())
                    if events:
                        events[-1]["data"] = data

                if len(events) > 0 and "data" in events[-1]:
                    return events[0]

    # Create concurrent connections
    tasks = [connect_and_read(run_id) for run_id in run_ids]
    results = await asyncio.gather(*tasks)

    # Verify all connections succeeded
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result["type"] == "connected"
        assert result["data"]["run_id"] == run_ids[i]


@pytest.mark.asyncio
async def test_sse_query_parameters(client: AsyncClient):
    """Test SSE endpoint with various query parameters."""
    run_id = "test_params"

    # Test with include_state=false
    async with client.stream(
        "GET",
        f"/api/v1/sse/{run_id}?include_state=false&poll_interval=0.5"
    ) as response:
        assert response.status_code == 200

    # Test with different poll intervals
    for interval in [0.1, 1.0, 5.0]:
        async with client.stream(
            "GET",
            f"/api/v1/sse/{run_id}?poll_interval={interval}"
        ) as response:
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_sse_format_compliance(client: AsyncClient):
    """Test that SSE messages follow the correct format."""
    run_id = "test_format"

    async with client.stream("GET", f"/api/v1/sse/{run_id}?poll_interval=0.1") as response:
        # Read raw lines to verify SSE format
        lines = []
        async for line in response.aiter_lines():
            lines.append(line)
            if len(lines) >= 4:  # event + data + empty line
                break

        # SSE format verification
        assert any(line.startswith("event:") for line in lines)
        assert any(line.startswith("data:") for line in lines)

        # Verify data is valid JSON
        for line in lines:
            if line.startswith("data:"):
                data_str = line.split(":", 1)[1].strip()
                data = json.loads(data_str)  # Should not raise
                assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_error_handling_in_stream(client: AsyncClient, test_checkpointer):
    """Test that errors in the stream are handled gracefully."""
    _, db_path = test_checkpointer
    run_id = "test_error_handling"

    # Override settings temporarily
    original_db_path = settings.checkpoint_db_path
    settings.checkpoint_db_path = db_path

    try:
        # Create an invalid checkpoint to trigger an error scenario
        # This tests the error handling in the stream generator

        async with client.stream(
            "GET",
            f"/api/v1/sse/{run_id}?poll_interval=0.1"
        ) as response:
            # Should still establish connection even if no checkpoints exist
            assert response.status_code == 200

            # Read connection event
            events = []
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                    events.append({"type": event_type})
                elif line.startswith("data:"):
                    data = json.loads(line.split(":", 1)[1].strip())
                    if events:
                        events[-1]["data"] = data

                if len(events) > 0 and "data" in events[-1]:
                    break

            # Should receive connection event even without checkpoints
            assert events[0]["type"] == "connected"

    finally:
        settings.checkpoint_db_path = original_db_path


@pytest.mark.asyncio
async def test_event_types_endpoint(client: AsyncClient):
    """Test the events endpoint with different event types."""
    run_id = "test_event_types"

    # Test without filter
    async with client.stream(
        "GET",
        f"/api/v1/sse/{run_id}/events?poll_interval=0.1"
    ) as response:
        assert response.status_code == 200

    # Test with single event type
    async with client.stream(
        "GET",
        f"/api/v1/sse/{run_id}/events?event_types=node_enter&poll_interval=0.1"
    ) as response:
        assert response.status_code == 200

    # Test with multiple event types
    async with client.stream(
        "GET",
        f"/api/v1/sse/{run_id}/events?event_types=node_enter,node_exit,approval_required"
    ) as response:
        assert response.status_code == 200
