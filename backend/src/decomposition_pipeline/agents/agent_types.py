"""
Agent types and pool configurations for the decomposition pipeline.

This module defines the core data structures for agent pool management including:
- Agent status tracking
- Individual agent definitions
- Pool configurations
- Pool management structures
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    WORKING = "working"
    STUCK = "stuck"


class PoolType(Enum):
    """Type of agent pool."""
    PARADIGM = "paradigm"
    DOMAIN = "domain"
    GENERAL = "general"


@dataclass
class Agent:
    """
    Individual agent within a pool.

    Tracks workload, status, and performance metrics.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    pool: str = ""
    status: AgentStatus = AgentStatus.IDLE
    current_workload: int = 0
    total_tasks_completed: int = 0
    average_response_time: float = 0.0  # In seconds
    last_activity: Optional[datetime] = None
    current_task_id: Optional[str] = None

    def assign_task(self, task_id: str) -> None:
        """Assign a task to this agent."""
        self.status = AgentStatus.WORKING
        self.current_workload += 1
        self.current_task_id = task_id
        self.last_activity = datetime.now()

    def complete_task(self, response_time: float) -> None:
        """Mark task as complete and update metrics."""
        self.current_workload -= 1
        self.total_tasks_completed += 1

        # Update rolling average response time
        if self.average_response_time == 0.0:
            self.average_response_time = response_time
        else:
            # Exponential moving average
            alpha = 0.3
            self.average_response_time = (
                alpha * response_time + (1 - alpha) * self.average_response_time
            )

        if self.current_workload == 0:
            self.status = AgentStatus.IDLE
            self.current_task_id = None

        self.last_activity = datetime.now()

    def mark_stuck(self) -> None:
        """Mark agent as stuck (timeout or error)."""
        self.status = AgentStatus.STUCK
        self.last_activity = datetime.now()

    def reset(self) -> None:
        """Reset agent to idle state."""
        self.status = AgentStatus.IDLE
        self.current_workload = 0
        self.current_task_id = None
        self.last_activity = datetime.now()


@dataclass
class AgentPoolConfig:
    """
    Configuration for an agent pool.

    Defines pool size, model, specialization, and resource limits.
    """
    name: str
    size: int
    model: str
    specialization: str
    pool_type: PoolType = PoolType.DOMAIN
    max_concurrent: Optional[int] = None  # If None, defaults to size
    timeout_seconds: float = 300.0  # 5 minute timeout

    def __post_init__(self):
        """Set default max_concurrent if not specified."""
        if self.max_concurrent is None:
            self.max_concurrent = self.size


@dataclass
class PoolMetrics:
    """
    Metrics for monitoring pool health and performance.
    """
    pool_name: str
    total_agents: int
    active_agents: int
    idle_agents: int
    stuck_agents: int
    total_tasks_completed: int
    average_response_time: float
    current_queue_size: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentPool:
    """
    A pool of agents with load balancing and status tracking.

    Manages agent lifecycle, work assignment, and metrics collection.
    """
    config: AgentPoolConfig
    agents: List[Agent] = field(default_factory=list)
    task_queue: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize agents based on pool configuration."""
        if not self.agents:
            self.agents = [
                Agent(id=f"{self.config.name}-{i:03d}", pool=self.config.name)
                for i in range(self.config.size)
            ]

    def get_least_loaded_agent(self) -> Optional[Agent]:
        """
        Get the agent with the lowest workload.

        Returns None if no idle agents and at max_concurrent limit.
        """
        # Filter to available agents (not stuck)
        available_agents = [
            agent for agent in self.agents
            if agent.status != AgentStatus.STUCK
        ]

        if not available_agents:
            return None

        # Check if we're at concurrent execution limit
        active_count = sum(
            1 for agent in available_agents
            if agent.status == AgentStatus.WORKING
        )

        if active_count >= self.config.max_concurrent:
            return None

        # Return agent with minimum workload
        return min(available_agents, key=lambda a: a.current_workload)

    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Find agent by ID."""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None

    def get_metrics(self) -> PoolMetrics:
        """Collect current pool metrics."""
        idle_count = sum(1 for a in self.agents if a.status == AgentStatus.IDLE)
        active_count = sum(1 for a in self.agents if a.status == AgentStatus.WORKING)
        stuck_count = sum(1 for a in self.agents if a.status == AgentStatus.STUCK)

        total_completed = sum(a.total_tasks_completed for a in self.agents)

        # Calculate average response time across all agents
        agents_with_tasks = [a for a in self.agents if a.total_tasks_completed > 0]
        avg_response = (
            sum(a.average_response_time for a in agents_with_tasks) / len(agents_with_tasks)
            if agents_with_tasks else 0.0
        )

        return PoolMetrics(
            pool_name=self.config.name,
            total_agents=len(self.agents),
            active_agents=active_count,
            idle_agents=idle_count,
            stuck_agents=stuck_count,
            total_tasks_completed=total_completed,
            average_response_time=avg_response,
            current_queue_size=len(self.task_queue)
        )

    def add_to_queue(self, task_id: str) -> None:
        """Add task to queue when no agents available."""
        self.task_queue.append(task_id)

    def pop_from_queue(self) -> Optional[str]:
        """Remove and return next task from queue."""
        if self.task_queue:
            return self.task_queue.pop(0)
        return None

    def scale(self, new_size: int) -> None:
        """
        Scale pool to new size.

        If increasing, add new agents.
        If decreasing, mark excess agents for removal (only idle ones).
        """
        current_size = len(self.agents)

        if new_size > current_size:
            # Add new agents
            for i in range(current_size, new_size):
                agent = Agent(
                    id=f"{self.config.name}-{i:03d}",
                    pool=self.config.name
                )
                self.agents.append(agent)

        elif new_size < current_size:
            # Remove idle agents first
            idle_agents = [a for a in self.agents if a.status == AgentStatus.IDLE]
            to_remove = current_size - new_size

            for agent in idle_agents[:to_remove]:
                self.agents.remove(agent)

        self.config.size = new_size
        self.config.max_concurrent = min(self.config.max_concurrent, new_size)


# Predefined pool configurations
PARADIGM_POOL_CONFIGS: Dict[str, AgentPoolConfig] = {
    "structural": AgentPoolConfig(
        name="structural",
        size=50,
        model="gpt-4o-mini",
        specialization="graph_analysis",
        pool_type=PoolType.PARADIGM
    ),
    "functional": AgentPoolConfig(
        name="functional",
        size=50,
        model="gpt-4o-mini",
        specialization="operation_decomposition",
        pool_type=PoolType.PARADIGM
    ),
    "temporal": AgentPoolConfig(
        name="temporal",
        size=50,
        model="gpt-4o-mini",
        specialization="temporal_analysis",
        pool_type=PoolType.PARADIGM
    ),
    "spatial": AgentPoolConfig(
        name="spatial",
        size=50,
        model="gpt-4o-mini",
        specialization="spatial_decomposition",
        pool_type=PoolType.PARADIGM
    ),
    "hierarchical": AgentPoolConfig(
        name="hierarchical",
        size=50,
        model="gpt-4o-mini",
        specialization="hierarchical_analysis",
        pool_type=PoolType.PARADIGM
    ),
    "computational": AgentPoolConfig(
        name="computational",
        size=50,
        model="gpt-4o-mini",
        specialization="computational_decomposition",
        pool_type=PoolType.PARADIGM
    ),
    "data": AgentPoolConfig(
        name="data",
        size=50,
        model="gpt-4o-mini",
        specialization="data_partitioning",
        pool_type=PoolType.PARADIGM
    ),
    "dependency": AgentPoolConfig(
        name="dependency",
        size=50,
        model="gpt-4o-mini",
        specialization="dependency_analysis",
        pool_type=PoolType.PARADIGM
    ),
}

DOMAIN_POOL_CONFIGS: Dict[str, AgentPoolConfig] = {
    "api_design": AgentPoolConfig(
        name="api_design",
        size=30,
        model="gpt-4o-mini",
        specialization="api_architecture",
        pool_type=PoolType.DOMAIN
    ),
    "data_processing": AgentPoolConfig(
        name="data_processing",
        size=30,
        model="gpt-4o-mini",
        specialization="data_pipelines",
        pool_type=PoolType.DOMAIN
    ),
    "ml_modeling": AgentPoolConfig(
        name="ml_modeling",
        size=20,
        model="gpt-4o-mini",
        specialization="machine_learning",
        pool_type=PoolType.DOMAIN
    ),
    "security": AgentPoolConfig(
        name="security",
        size=20,
        model="gpt-4o-mini",
        specialization="security_analysis",
        pool_type=PoolType.DOMAIN
    ),
}

GENERAL_POOL_CONFIG = AgentPoolConfig(
    name="general",
    size=10,
    model="gpt-4o",  # Larger model for complex/novel problems
    specialization="general_problem_solving",
    pool_type=PoolType.GENERAL
)
