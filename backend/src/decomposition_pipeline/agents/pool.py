"""
Agent pool management for Level 4 solution generation.

This module implements the agent pool architecture described in brainstorm_1.md,
providing specialized agent pools for different paradigms and domains.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Status of an individual agent."""
    IDLE = "idle"
    WORKING = "working"
    STUCK = "stuck"
    FAILED = "failed"


@dataclass
class Agent:
    """
    Individual agent within a pool.

    Represents a single LLM instance that can solve subproblems.
    """
    id: str
    pool_name: str
    model: str = "gpt-4o-mini"
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[str] = None
    current_workload: int = 0
    total_completed: int = 0
    total_failed: int = 0
    avg_response_time: float = 0.0

    def assign_task(self, task_id: str) -> None:
        """Assign a task to this agent."""
        self.status = AgentStatus.WORKING
        self.current_task_id = task_id
        self.current_workload += 1

    def complete_task(self, response_time: float) -> None:
        """Mark task as completed and update metrics."""
        self.status = AgentStatus.IDLE
        self.current_task_id = None
        self.current_workload = max(0, self.current_workload - 1)
        self.total_completed += 1

        # Update running average
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (
                self.avg_response_time * 0.7 + response_time * 0.3
            )

    def fail_task(self) -> None:
        """Mark task as failed."""
        self.status = AgentStatus.FAILED
        self.current_task_id = None
        self.current_workload = max(0, self.current_workload - 1)
        self.total_failed += 1


@dataclass
class AgentPool:
    """
    Pool of specialized agents for a specific paradigm or domain.

    Based on architecture in brainstorm_1.md lines 758-846.
    Manages load balancing and health monitoring.
    """
    name: str
    specialization: str
    model: str = "gpt-4o-mini"
    size: int = 50
    agents: List[Agent] = field(default_factory=list)

    def __post_init__(self):
        """Initialize agents in the pool."""
        if not self.agents:
            self.agents = [
                Agent(
                    id=f"{self.name}-agent-{i:03d}",
                    pool_name=self.name,
                    model=self.model
                )
                for i in range(self.size)
            ]

    def get_least_loaded_agent(self) -> Optional[Agent]:
        """
        Find the agent with the lowest current workload.

        Implements load balancing strategy from brainstorm_1.md lines 831-845.
        """
        idle_agents = [a for a in self.agents if a.status == AgentStatus.IDLE]

        if idle_agents:
            # Prefer idle agents
            return min(idle_agents, key=lambda a: a.current_workload)

        # If all busy, find least loaded
        working_agents = [a for a in self.agents if a.status == AgentStatus.WORKING]

        if working_agents:
            return min(working_agents, key=lambda a: a.current_workload)

        # No available agents
        return None

    def get_pool_status(self) -> Dict[str, Any]:
        """Get current status and metrics for this pool."""
        active_agents = [a for a in self.agents if a.status == AgentStatus.WORKING]
        idle_agents = [a for a in self.agents if a.status == AgentStatus.IDLE]
        stuck_agents = [a for a in self.agents if a.status == AgentStatus.STUCK]
        failed_agents = [a for a in self.agents if a.status == AgentStatus.FAILED]

        total_completed = sum(a.total_completed for a in self.agents)
        total_failed = sum(a.total_failed for a in self.agents)

        avg_response_times = [a.avg_response_time for a in self.agents if a.avg_response_time > 0]
        avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0.0

        return {
            "name": self.name,
            "specialization": self.specialization,
            "total_agents": self.size,
            "active_agents": len(active_agents),
            "idle_agents": len(idle_agents),
            "stuck_agents": len(stuck_agents),
            "failed_agents": len(failed_agents),
            "utilization": len(active_agents) / self.size if self.size > 0 else 0,
            "total_completed": total_completed,
            "total_failed": total_failed,
            "avg_response_time": avg_response_time,
        }

    def assign_work(self, task_id: str) -> Optional[Agent]:
        """
        Assign work to least-loaded agent in pool.

        Returns assigned agent or None if pool is full.
        """
        agent = self.get_least_loaded_agent()
        if agent:
            agent.assign_task(task_id)
        return agent


class AgentPoolManager:
    """
    Manages all agent pools for the decomposition pipeline.

    Implements pool architecture from brainstorm_1.md lines 758-799.
    """

    def __init__(self):
        """Initialize all agent pools."""
        self.pools: Dict[str, AgentPool] = {}
        self._initialize_paradigm_pools()
        self._initialize_domain_pools()
        self._initialize_general_pool()

    def _initialize_paradigm_pools(self) -> None:
        """Create 8 paradigm-specific agent pools."""
        paradigm_pools = {
            "structural": "graph_analysis",
            "functional": "operation_decomposition",
            "temporal": "event_driven_systems",
            "spatial": "geographic_partitioning",
            "hierarchical": "layered_architectures",
            "computational": "resource_optimization",
            "data": "data_partitioning",
            "dependency": "dependency_analysis",
        }

        for paradigm, specialization in paradigm_pools.items():
            self.pools[paradigm] = AgentPool(
                name=f"{paradigm}_pool",
                specialization=specialization,
                model="gpt-4o-mini",
                size=50
            )

    def _initialize_domain_pools(self) -> None:
        """Create domain-specific agent pools."""
        domain_pools = {
            "api_design": 30,
            "data_processing": 30,
            "ml_modeling": 20,
            "security": 20,
            "frontend": 25,
            "backend": 25,
            "database": 20,
            "networking": 15,
        }

        for domain, size in domain_pools.items():
            self.pools[domain] = AgentPool(
                name=f"{domain}_pool",
                specialization=domain,
                model="gpt-4o-mini",
                size=size
            )

    def _initialize_general_pool(self) -> None:
        """Create general-purpose agent pool with larger model."""
        self.pools["general"] = AgentPool(
            name="general_pool",
            specialization="general_problem_solving",
            model="gpt-4o",  # Larger model for complex problems
            size=10
        )

    def get_pool(self, pool_name: str) -> Optional[AgentPool]:
        """Get a specific pool by name."""
        return self.pools.get(pool_name)

    def get_all_pool_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all pools."""
        return {
            pool_name: pool.get_pool_status()
            for pool_name, pool in self.pools.items()
        }

    def select_pool_for_subproblem(
        self,
        paradigm: str,
        domain: Optional[str] = None,
        complexity: str = "medium"
    ) -> str:
        """
        Select appropriate agent pool for a subproblem.

        Implements selection strategy from brainstorm_1.md lines 801-827.

        Priority order:
        1. Paradigm pool (if subproblem came from specific paradigm)
        2. Domain pool (if subproblem matches domain)
        3. General pool (fallback)

        Args:
            paradigm: Source paradigm of the subproblem
            domain: Optional domain specialization
            complexity: Complexity level ("low", "medium", "high")

        Returns:
            Name of selected pool
        """
        # Check paradigm pool first
        # Pool dict keys are just paradigm names without _pool suffix
        if paradigm in self.pools:
            pool = self.pools[paradigm]
            status = pool.get_pool_status()

            # If pool has capacity, use it
            if status["utilization"] < 0.9:  # Not overloaded
                return pool.name  # Return the actual pool name

        # Check domain pool if specified
        if domain:
            if domain in self.pools:
                pool = self.pools[domain]
                status = pool.get_pool_status()

                if status["utilization"] < 0.9:
                    return pool.name

        # For high complexity, prefer general pool with larger model
        if complexity == "high":
            return self.pools["general"].name

        # Fallback to paradigm or general pool
        if paradigm in self.pools:
            return self.pools[paradigm].name

        return self.pools["general"].name

    async def assign_work_to_pool(
        self,
        pool_name: str,
        task_id: str
    ) -> Optional[Agent]:
        """
        Assign work to an agent in the specified pool.

        Args:
            pool_name: Name of the pool to assign work to
            task_id: ID of the task/subproblem

        Returns:
            Assigned agent or None if pool is full
        """
        pool = self.get_pool(pool_name)
        if not pool:
            return None

        return pool.assign_work(task_id)

    def complete_task(self, agent_id: str, response_time: float) -> None:
        """Mark a task as completed by an agent."""
        for pool in self.pools.values():
            for agent in pool.agents:
                if agent.id == agent_id:
                    agent.complete_task(response_time)
                    return

    def fail_task(self, agent_id: str) -> None:
        """Mark a task as failed by an agent."""
        for pool in self.pools.values():
            for agent in pool.agents:
                if agent.id == agent_id:
                    agent.fail_task()
                    return
