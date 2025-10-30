"""
Tests for agent types and pool data structures.
"""

import pytest
from datetime import datetime, timedelta

from decomposition_pipeline.agents.agent_types import (
    Agent,
    AgentPool,
    AgentPoolConfig,
    AgentStatus,
    PoolType,
    PARADIGM_POOL_CONFIGS,
    DOMAIN_POOL_CONFIGS,
    GENERAL_POOL_CONFIG,
)


class TestAgent:
    """Tests for Agent class."""

    def test_agent_initialization(self):
        """Test agent is initialized with correct defaults."""
        agent = Agent(pool="test_pool")

        assert agent.id is not None
        assert agent.pool == "test_pool"
        assert agent.status == AgentStatus.IDLE
        assert agent.current_workload == 0
        assert agent.total_tasks_completed == 0
        assert agent.average_response_time == 0.0
        assert agent.last_activity is None
        assert agent.current_task_id is None

    def test_assign_task(self):
        """Test task assignment updates agent state."""
        agent = Agent(pool="test_pool")
        task_id = "task-001"

        agent.assign_task(task_id)

        assert agent.status == AgentStatus.WORKING
        assert agent.current_workload == 1
        assert agent.current_task_id == task_id
        assert agent.last_activity is not None

    def test_complete_task(self):
        """Test task completion updates metrics."""
        agent = Agent(pool="test_pool")
        agent.assign_task("task-001")

        response_time = 2.5
        agent.complete_task(response_time)

        assert agent.status == AgentStatus.IDLE
        assert agent.current_workload == 0
        assert agent.total_tasks_completed == 1
        assert agent.average_response_time == response_time
        assert agent.current_task_id is None

    def test_average_response_time_calculation(self):
        """Test exponential moving average for response time."""
        agent = Agent(pool="test_pool")

        # First task
        agent.assign_task("task-001")
        agent.complete_task(2.0)
        assert agent.average_response_time == 2.0

        # Second task - should use EMA
        agent.assign_task("task-002")
        agent.complete_task(4.0)

        # EMA: 0.3 * 4.0 + 0.7 * 2.0 = 2.6
        assert abs(agent.average_response_time - 2.6) < 0.01

    def test_multiple_concurrent_tasks(self):
        """Test agent can handle multiple concurrent tasks."""
        agent = Agent(pool="test_pool")

        agent.assign_task("task-001")
        agent.assign_task("task-002")

        assert agent.current_workload == 2
        assert agent.status == AgentStatus.WORKING

        agent.complete_task(1.0)
        assert agent.current_workload == 1
        assert agent.status == AgentStatus.WORKING

        agent.complete_task(1.5)
        assert agent.current_workload == 0
        assert agent.status == AgentStatus.IDLE

    def test_mark_stuck(self):
        """Test marking agent as stuck."""
        agent = Agent(pool="test_pool")
        agent.assign_task("task-001")

        agent.mark_stuck()

        assert agent.status == AgentStatus.STUCK
        assert agent.last_activity is not None

    def test_reset(self):
        """Test resetting agent to idle state."""
        agent = Agent(pool="test_pool")
        agent.assign_task("task-001")
        agent.assign_task("task-002")
        agent.mark_stuck()

        agent.reset()

        assert agent.status == AgentStatus.IDLE
        assert agent.current_workload == 0
        assert agent.current_task_id is None
        assert agent.last_activity is not None


class TestAgentPoolConfig:
    """Tests for AgentPoolConfig."""

    def test_config_initialization(self):
        """Test pool config initializes correctly."""
        config = AgentPoolConfig(
            name="test_pool",
            size=10,
            model="gpt-4o-mini",
            specialization="testing"
        )

        assert config.name == "test_pool"
        assert config.size == 10
        assert config.model == "gpt-4o-mini"
        assert config.specialization == "testing"
        assert config.max_concurrent == 10  # Defaults to size
        assert config.timeout_seconds == 300.0

    def test_config_with_custom_max_concurrent(self):
        """Test config with explicit max_concurrent."""
        config = AgentPoolConfig(
            name="test_pool",
            size=20,
            model="gpt-4o-mini",
            specialization="testing",
            max_concurrent=15
        )

        assert config.max_concurrent == 15


class TestAgentPool:
    """Tests for AgentPool class."""

    def test_pool_initialization(self):
        """Test pool initializes with correct agents."""
        config = AgentPoolConfig(
            name="test_pool",
            size=5,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        assert len(pool.agents) == 5
        assert all(agent.pool == "test_pool" for agent in pool.agents)
        assert len(pool.task_queue) == 0

    def test_get_least_loaded_agent(self):
        """Test getting least loaded agent."""
        config = AgentPoolConfig(
            name="test_pool",
            size=3,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        # All agents idle - should return first
        agent = pool.get_least_loaded_agent()
        assert agent is not None
        assert agent.current_workload == 0

        # Assign some work
        pool.agents[0].assign_task("task-001")
        pool.agents[0].assign_task("task-002")  # 2 tasks
        pool.agents[1].assign_task("task-003")  # 1 task

        # Should return agents[2] (0 tasks)
        agent = pool.get_least_loaded_agent()
        assert agent == pool.agents[2]

    def test_get_least_loaded_agent_at_limit(self):
        """Test returns None when at concurrent limit."""
        config = AgentPoolConfig(
            name="test_pool",
            size=3,
            model="gpt-4o-mini",
            specialization="testing",
            max_concurrent=2
        )
        pool = AgentPool(config=config)

        # Assign to max_concurrent agents
        pool.agents[0].assign_task("task-001")
        pool.agents[1].assign_task("task-002")

        # Should return None (at limit)
        agent = pool.get_least_loaded_agent()
        assert agent is None

    def test_get_least_loaded_agent_skips_stuck(self):
        """Test skips stuck agents."""
        config = AgentPoolConfig(
            name="test_pool",
            size=3,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        pool.agents[0].mark_stuck()
        pool.agents[1].assign_task("task-001")

        # Should return agents[2]
        agent = pool.get_least_loaded_agent()
        assert agent == pool.agents[2]

    def test_get_agent_by_id(self):
        """Test finding agent by ID."""
        config = AgentPoolConfig(
            name="test_pool",
            size=3,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        target_agent = pool.agents[1]
        found_agent = pool.get_agent_by_id(target_agent.id)

        assert found_agent == target_agent

    def test_get_metrics(self):
        """Test pool metrics collection."""
        config = AgentPoolConfig(
            name="test_pool",
            size=5,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        # Set up some state
        pool.agents[0].assign_task("task-001")
        pool.agents[1].assign_task("task-002")
        pool.agents[2].mark_stuck()
        pool.add_to_queue("task-003")

        metrics = pool.get_metrics()

        assert metrics.pool_name == "test_pool"
        assert metrics.total_agents == 5
        assert metrics.active_agents == 2
        assert metrics.idle_agents == 2
        assert metrics.stuck_agents == 1
        assert metrics.current_queue_size == 1

    def test_queue_operations(self):
        """Test task queue operations."""
        config = AgentPoolConfig(
            name="test_pool",
            size=2,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        # Add to queue
        pool.add_to_queue("task-001")
        pool.add_to_queue("task-002")

        assert len(pool.task_queue) == 2

        # Pop from queue
        task_id = pool.pop_from_queue()
        assert task_id == "task-001"
        assert len(pool.task_queue) == 1

        task_id = pool.pop_from_queue()
        assert task_id == "task-002"
        assert len(pool.task_queue) == 0

        # Pop from empty queue
        task_id = pool.pop_from_queue()
        assert task_id is None

    def test_scale_up(self):
        """Test scaling pool up."""
        config = AgentPoolConfig(
            name="test_pool",
            size=3,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        pool.scale(5)

        assert len(pool.agents) == 5
        assert pool.config.size == 5
        assert all(agent.pool == "test_pool" for agent in pool.agents)

    def test_scale_down(self):
        """Test scaling pool down removes idle agents."""
        config = AgentPoolConfig(
            name="test_pool",
            size=5,
            model="gpt-4o-mini",
            specialization="testing"
        )
        pool = AgentPool(config=config)

        # Mark some agents as working
        pool.agents[0].assign_task("task-001")
        pool.agents[1].assign_task("task-002")

        pool.scale(3)

        assert len(pool.agents) == 3
        assert pool.config.size == 3

        # Working agents should still be present
        assert pool.agents[0].status == AgentStatus.WORKING
        assert pool.agents[1].status == AgentStatus.WORKING


class TestPredefinedConfigs:
    """Tests for predefined pool configurations."""

    def test_paradigm_configs_complete(self):
        """Test all 8 paradigm pools defined."""
        expected_paradigms = [
            "structural", "functional", "temporal", "spatial",
            "hierarchical", "computational", "data", "dependency"
        ]

        for paradigm in expected_paradigms:
            assert paradigm in PARADIGM_POOL_CONFIGS
            config = PARADIGM_POOL_CONFIGS[paradigm]
            assert config.size == 50
            assert config.model == "gpt-4o-mini"
            assert config.pool_type == PoolType.PARADIGM

    def test_domain_configs_complete(self):
        """Test domain pool configs defined."""
        expected_domains = [
            "api_design", "data_processing", "ml_modeling", "security"
        ]

        for domain in expected_domains:
            assert domain in DOMAIN_POOL_CONFIGS
            config = DOMAIN_POOL_CONFIGS[domain]
            assert config.model == "gpt-4o-mini"
            assert config.pool_type == PoolType.DOMAIN

    def test_general_config(self):
        """Test general pool config."""
        assert GENERAL_POOL_CONFIG.name == "general"
        assert GENERAL_POOL_CONFIG.size == 10
        assert GENERAL_POOL_CONFIG.model == "gpt-4o"  # Uses larger model
        assert GENERAL_POOL_CONFIG.pool_type == PoolType.GENERAL
