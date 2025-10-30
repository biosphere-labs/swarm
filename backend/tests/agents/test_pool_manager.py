"""
Tests for AgentPoolManager.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from decomposition_pipeline.agents.pool_manager import AgentPoolManager
from decomposition_pipeline.agents.agent_types import (
    AgentPoolConfig,
    AgentStatus,
    PoolType,
)


class TestAgentPoolManager:
    """Tests for AgentPoolManager class."""

    def test_initialization(self):
        """Test manager initializes with all default pools."""
        manager = AgentPoolManager()

        # Check paradigm pools
        paradigms = [
            "structural", "functional", "temporal", "spatial",
            "hierarchical", "computational", "data", "dependency"
        ]
        for paradigm in paradigms:
            assert paradigm in manager.pools
            pool = manager.pools[paradigm]
            assert len(pool.agents) == 50

        # Check domain pools
        domains = ["api_design", "data_processing", "ml_modeling", "security"]
        for domain in domains:
            assert domain in manager.pools

        # Check general pool
        assert "general" in manager.pools
        assert len(manager.pools["general"].agents) == 10

    def test_create_custom_pool(self):
        """Test creating custom pool."""
        manager = AgentPoolManager()

        config = AgentPoolConfig(
            name="custom_pool",
            size=15,
            model="gpt-4o-mini",
            specialization="custom_tasks"
        )

        pool = manager.create_pool(config)

        assert pool.config.name == "custom_pool"
        assert len(pool.agents) == 15
        assert "custom_pool" in manager.pools

    def test_create_duplicate_pool_raises_error(self):
        """Test creating pool with duplicate name raises error."""
        manager = AgentPoolManager()

        config = AgentPoolConfig(
            name="structural",  # Already exists
            size=10,
            model="gpt-4o-mini",
            specialization="test"
        )

        with pytest.raises(ValueError, match="already exists"):
            manager.create_pool(config)

    def test_get_pool(self):
        """Test getting pool by name."""
        manager = AgentPoolManager()

        pool = manager.get_pool("structural")
        assert pool is not None
        assert pool.config.name == "structural"

        pool = manager.get_pool("nonexistent")
        assert pool is None

    @patch("decomposition_pipeline.agents.pool_manager.select_pool_for_subproblem")
    def test_assign_work(self, mock_select_pool):
        """Test work assignment to agent."""
        manager = AgentPoolManager()
        mock_select_pool.return_value = "structural"

        subproblem = {
            "id": "sp-001",
            "title": "Test subproblem",
            "source_paradigm": "structural"
        }

        agent = manager.assign_work(subproblem)

        assert agent is not None
        assert agent.status == AgentStatus.WORKING
        assert agent.current_task_id == "sp-001"
        mock_select_pool.assert_called_once()

    @patch("decomposition_pipeline.agents.pool_manager.select_pool_for_subproblem")
    def test_assign_work_with_preferred_pool(self, mock_select_pool):
        """Test work assignment with preferred pool."""
        manager = AgentPoolManager()

        subproblem = {"id": "sp-001"}
        agent = manager.assign_work(subproblem, preferred_pool="functional")

        assert agent is not None
        # Should not call routing when preferred_pool specified
        mock_select_pool.assert_not_called()

    @patch("decomposition_pipeline.agents.pool_manager.select_pool_for_subproblem")
    def test_assign_work_queues_when_no_agents(self, mock_select_pool):
        """Test task is queued when no agents available."""
        manager = AgentPoolManager()
        mock_select_pool.return_value = "general"

        # Assign to all agents in general pool (10 agents)
        for i in range(10):
            subproblem = {"id": f"sp-{i:03d}"}
            manager.assign_work(subproblem)

        # Next assignment should queue
        subproblem = {"id": "sp-queued"}
        agent = manager.assign_work(subproblem)

        assert agent is None
        pool = manager.get_pool("general")
        assert "sp-queued" in pool.task_queue

    def test_release_agent(self):
        """Test releasing agent after task completion."""
        manager = AgentPoolManager()

        # Assign work
        subproblem = {"id": "sp-001"}
        agent = manager.assign_work(subproblem, preferred_pool="structural")
        agent_id = agent.id

        # Release agent
        manager.release_agent(agent_id, "structural", response_time=2.5)

        released_agent = manager.get_pool("structural").get_agent_by_id(agent_id)
        assert released_agent.status == AgentStatus.IDLE
        assert released_agent.total_tasks_completed == 1
        assert released_agent.average_response_time == 2.5

    def test_release_agent_assigns_queued_task(self):
        """Test releasing agent assigns queued task."""
        manager = AgentPoolManager()
        pool = manager.get_pool("general")

        # Assign all agents
        for i in range(10):
            subproblem = {"id": f"sp-{i:03d}"}
            manager.assign_work(subproblem, preferred_pool="general")

        # Queue a task
        pool.add_to_queue("sp-queued")
        assert len(pool.task_queue) == 1

        # Release an agent
        first_agent = pool.agents[0]
        manager.release_agent(first_agent.id, "general", response_time=1.0)

        # Queued task should be assigned
        assert len(pool.task_queue) == 0
        assert first_agent.status == AgentStatus.WORKING
        assert first_agent.current_task_id == "sp-queued"

    def test_mark_agent_stuck(self):
        """Test marking agent as stuck."""
        manager = AgentPoolManager()

        # Assign work
        subproblem = {"id": "sp-001"}
        agent = manager.assign_work(subproblem, preferred_pool="structural")

        # Mark stuck
        manager.mark_agent_stuck(agent.id, "structural")

        assert agent.status == AgentStatus.STUCK

    def test_reset_agent(self):
        """Test resetting stuck agent."""
        manager = AgentPoolManager()

        # Assign work and mark stuck
        subproblem = {"id": "sp-001"}
        agent = manager.assign_work(subproblem, preferred_pool="structural")
        manager.mark_agent_stuck(agent.id, "structural")

        # Reset
        manager.reset_agent(agent.id, "structural")

        assert agent.status == AgentStatus.IDLE
        assert agent.current_workload == 0

    def test_get_pool_status(self):
        """Test getting pool status."""
        manager = AgentPoolManager()

        # Assign some work
        for i in range(5):
            subproblem = {"id": f"sp-{i:03d}"}
            manager.assign_work(subproblem, preferred_pool="structural")

        metrics = manager.get_pool_status("structural")

        assert metrics is not None
        assert metrics.pool_name == "structural"
        assert metrics.active_agents == 5
        assert metrics.idle_agents == 45

    def test_get_all_pool_metrics(self):
        """Test getting metrics for all pools."""
        manager = AgentPoolManager()

        metrics = manager.get_all_pool_metrics()

        assert len(metrics) > 0
        assert "structural" in metrics
        assert "general" in metrics

    def test_scale_pool(self):
        """Test scaling pool."""
        manager = AgentPoolManager()

        manager.scale_pool("structural", 75)

        pool = manager.get_pool("structural")
        assert pool.config.size == 75
        assert len(pool.agents) == 75

    def test_scale_pool_invalid_size_raises_error(self):
        """Test scaling with invalid size raises error."""
        manager = AgentPoolManager()

        with pytest.raises(ValueError, match="must be positive"):
            manager.scale_pool("structural", 0)

        with pytest.raises(ValueError, match="must be positive"):
            manager.scale_pool("structural", -10)

    def test_scale_pool_nonexistent_raises_error(self):
        """Test scaling nonexistent pool raises error."""
        manager = AgentPoolManager()

        with pytest.raises(ValueError, match="not found"):
            manager.scale_pool("nonexistent", 20)

    def test_get_stuck_agents(self):
        """Test finding stuck agents."""
        manager = AgentPoolManager()

        # Assign work and backdate activity
        subproblem = {"id": "sp-001"}
        agent = manager.assign_work(subproblem, preferred_pool="structural")

        # Simulate old activity (stuck)
        agent.last_activity = datetime.now() - timedelta(seconds=400)

        # Find stuck agents (default timeout 300s)
        stuck = manager.get_stuck_agents()

        assert len(stuck) == 1
        assert stuck[0] == ("structural", agent.id)

    def test_get_stuck_agents_with_custom_timeout(self):
        """Test finding stuck agents with custom timeout."""
        manager = AgentPoolManager()

        subproblem = {"id": "sp-001"}
        agent = manager.assign_work(subproblem, preferred_pool="structural")
        agent.last_activity = datetime.now() - timedelta(seconds=100)

        # With default timeout (300s), not stuck
        stuck = manager.get_stuck_agents()
        assert len(stuck) == 0

        # With custom timeout (50s), is stuck
        stuck = manager.get_stuck_agents(timeout_seconds=50)
        assert len(stuck) == 1

    def test_health_check_healthy(self):
        """Test health check with healthy system."""
        manager = AgentPoolManager()

        health = manager.health_check()

        assert health["overall_status"] == "healthy"
        assert health["total_stuck"] == 0

    def test_health_check_degraded(self):
        """Test health check with stuck agents."""
        manager = AgentPoolManager()

        # Mark some agents as stuck
        pool = manager.get_pool("structural")
        pool.agents[0].mark_stuck()

        health = manager.health_check()

        assert health["overall_status"] == "degraded"
        assert health["total_stuck"] == 1

    def test_health_check_unhealthy(self):
        """Test health check with many stuck agents."""
        manager = AgentPoolManager()

        # Mark >30% of agents as stuck in one pool
        pool = manager.get_pool("general")  # 10 agents
        for i in range(4):  # 40%
            pool.agents[i].mark_stuck()

        health = manager.health_check()

        assert health["overall_status"] == "unhealthy"
        assert health["pools"]["general"]["status"] == "unhealthy"

    def test_health_check_overloaded(self):
        """Test health check with overloaded queue."""
        manager = AgentPoolManager()

        pool = manager.get_pool("general")
        # Add many tasks to queue (> 2x pool size)
        for i in range(25):
            pool.add_to_queue(f"task-{i}")

        health = manager.health_check()

        assert health["pools"]["general"]["status"] == "overloaded"

    def test_shutdown(self):
        """Test shutdown resets all agents and clears queues."""
        manager = AgentPoolManager()

        # Assign some work
        for i in range(5):
            subproblem = {"id": f"sp-{i:03d}"}
            manager.assign_work(subproblem, preferred_pool="structural")

        # Add to queue
        pool = manager.get_pool("structural")
        pool.add_to_queue("queued-task")

        # Shutdown
        manager.shutdown()

        # Check all agents reset
        for agent in pool.agents:
            assert agent.status == AgentStatus.IDLE
            assert agent.current_workload == 0

        # Check queue cleared
        assert len(pool.task_queue) == 0

    def test_get_summary(self):
        """Test getting summary statistics."""
        manager = AgentPoolManager()

        # Assign some work across pools
        for i in range(10):
            subproblem = {"id": f"sp-{i:03d}"}
            manager.assign_work(subproblem, preferred_pool="structural")

        for i in range(5):
            subproblem = {"id": f"sp-f-{i:03d}"}
            manager.assign_work(subproblem, preferred_pool="functional")

        summary = manager.get_summary()

        assert summary["total_pools"] > 0
        assert summary["total_agents"] > 0
        assert summary["active_agents"] == 15
        assert summary["utilization"] > 0


class TestAgentPoolManagerAsync:
    """Tests for async operations."""

    @pytest.mark.asyncio
    async def test_monitor_and_recover(self):
        """Test monitor detects and handles stuck agents."""
        manager = AgentPoolManager()

        # Assign work and backdate
        subproblem = {"id": "sp-001"}
        agent = manager.assign_work(subproblem, preferred_pool="structural")
        agent.last_activity = datetime.now() - timedelta(seconds=400)

        # Run one iteration of monitor
        import asyncio

        async def run_once():
            await asyncio.sleep(0)  # Yield control
            stuck = manager.get_stuck_agents()
            for pool_name, agent_id in stuck:
                manager.mark_agent_stuck(agent_id, pool_name)

        await run_once()

        # Agent should be marked stuck
        assert agent.status == AgentStatus.STUCK
