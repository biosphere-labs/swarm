"""
Agent pool manager for coordinating work across all agent pools.

This module provides the main AgentPoolManager class that:
- Creates and manages all agent pools (paradigm, domain, general)
- Assigns work to appropriate agents based on pool selection
- Tracks agent status and pool metrics
- Handles load balancing and resource limits
- Provides health monitoring and observability
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from .agent_types import (
    Agent,
    AgentPool,
    AgentPoolConfig,
    AgentStatus,
    PoolMetrics,
    PoolType,
    PARADIGM_POOL_CONFIGS,
    DOMAIN_POOL_CONFIGS,
    GENERAL_POOL_CONFIG,
)
from .routing import select_pool_for_subproblem

logger = logging.getLogger(__name__)


class AgentPoolManager:
    """
    Main manager for all agent pools.

    Coordinates work assignment, tracks metrics, and manages pool lifecycle.
    """

    def __init__(self):
        """Initialize pool manager with all default pools."""
        self.pools: Dict[str, AgentPool] = {}
        self._initialize_default_pools()

    def _initialize_default_pools(self) -> None:
        """Create all default pools (8 paradigm + domain + general)."""
        # Create paradigm pools
        for name, config in PARADIGM_POOL_CONFIGS.items():
            self.pools[name] = AgentPool(config=config)
            logger.info(f"Created paradigm pool: {name} with {config.size} agents")

        # Create domain pools
        for name, config in DOMAIN_POOL_CONFIGS.items():
            self.pools[name] = AgentPool(config=config)
            logger.info(f"Created domain pool: {name} with {config.size} agents")

        # Create general pool
        self.pools[GENERAL_POOL_CONFIG.name] = AgentPool(config=GENERAL_POOL_CONFIG)
        logger.info(f"Created general pool with {GENERAL_POOL_CONFIG.size} agents")

    def create_pool(self, config: AgentPoolConfig) -> AgentPool:
        """
        Create a new custom pool.

        Args:
            config: Pool configuration

        Returns:
            Created AgentPool instance

        Raises:
            ValueError: If pool with same name already exists
        """
        if config.name in self.pools:
            raise ValueError(f"Pool '{config.name}' already exists")

        pool = AgentPool(config=config)
        self.pools[config.name] = pool
        logger.info(f"Created custom pool: {config.name} with {config.size} agents")
        return pool

    def get_pool(self, pool_name: str) -> Optional[AgentPool]:
        """Get pool by name."""
        return self.pools.get(pool_name)

    def assign_work(
        self,
        subproblem: Dict[str, Any],
        preferred_pool: Optional[str] = None
    ) -> Optional[Agent]:
        """
        Assign work to an agent.

        Args:
            subproblem: Subproblem dictionary with id, paradigm, domain info
            preferred_pool: Optional pool name to try first

        Returns:
            Assigned agent or None if no agents available
        """
        # Select pool using routing logic
        if preferred_pool:
            pool_name = preferred_pool
        else:
            pool_name = select_pool_for_subproblem(subproblem, self.pools)

        pool = self.pools.get(pool_name)
        if not pool:
            logger.error(f"Pool '{pool_name}' not found")
            return None

        # Get least loaded agent
        agent = pool.get_least_loaded_agent()

        if agent:
            # Assign task to agent
            task_id = subproblem.get("id", "unknown")
            agent.assign_task(task_id)
            logger.info(
                f"Assigned task {task_id} to agent {agent.id} in pool {pool_name}"
            )
            return agent
        else:
            # Queue task if no agents available
            task_id = subproblem.get("id", "unknown")
            pool.add_to_queue(task_id)
            logger.warning(
                f"No agents available in pool {pool_name}, queued task {task_id}"
            )
            return None

    def release_agent(
        self,
        agent_id: str,
        pool_name: str,
        response_time: float
    ) -> None:
        """
        Release an agent after task completion.

        Args:
            agent_id: Agent identifier
            pool_name: Pool containing the agent
            response_time: Task completion time in seconds
        """
        pool = self.pools.get(pool_name)
        if not pool:
            logger.error(f"Pool '{pool_name}' not found")
            return

        agent = pool.get_agent_by_id(agent_id)
        if not agent:
            logger.error(f"Agent '{agent_id}' not found in pool '{pool_name}'")
            return

        agent.complete_task(response_time)
        logger.info(
            f"Released agent {agent_id} from pool {pool_name} "
            f"(response_time: {response_time:.2f}s)"
        )

        # Check if there are queued tasks
        queued_task = pool.pop_from_queue()
        if queued_task and agent.status == AgentStatus.IDLE:
            # Assign queued task to now-idle agent
            agent.assign_task(queued_task)
            logger.info(
                f"Assigned queued task {queued_task} to agent {agent_id}"
            )

    def mark_agent_stuck(self, agent_id: str, pool_name: str) -> None:
        """
        Mark an agent as stuck (timeout or error).

        Args:
            agent_id: Agent identifier
            pool_name: Pool containing the agent
        """
        pool = self.pools.get(pool_name)
        if not pool:
            logger.error(f"Pool '{pool_name}' not found")
            return

        agent = pool.get_agent_by_id(agent_id)
        if not agent:
            logger.error(f"Agent '{agent_id}' not found in pool '{pool_name}'")
            return

        agent.mark_stuck()
        logger.warning(f"Marked agent {agent_id} in pool {pool_name} as stuck")

    def reset_agent(self, agent_id: str, pool_name: str) -> None:
        """
        Reset a stuck agent back to idle.

        Args:
            agent_id: Agent identifier
            pool_name: Pool containing the agent
        """
        pool = self.pools.get(pool_name)
        if not pool:
            logger.error(f"Pool '{pool_name}' not found")
            return

        agent = pool.get_agent_by_id(agent_id)
        if not agent:
            logger.error(f"Agent '{agent_id}' not found in pool '{pool_name}'")
            return

        agent.reset()
        logger.info(f"Reset agent {agent_id} in pool {pool_name} to idle")

    def get_pool_status(self, pool_name: str) -> Optional[PoolMetrics]:
        """
        Get current status and metrics for a pool.

        Args:
            pool_name: Name of the pool

        Returns:
            PoolMetrics or None if pool not found
        """
        pool = self.pools.get(pool_name)
        if not pool:
            return None
        return pool.get_metrics()

    def get_all_pool_metrics(self) -> Dict[str, PoolMetrics]:
        """
        Get metrics for all pools.

        Returns:
            Dictionary mapping pool name to metrics
        """
        metrics = {}
        for name, pool in self.pools.items():
            metrics[name] = pool.get_metrics()
        return metrics

    def scale_pool(self, pool_name: str, new_size: int) -> None:
        """
        Scale a pool to a new size.

        Args:
            pool_name: Name of the pool to scale
            new_size: New pool size

        Raises:
            ValueError: If pool not found or invalid size
        """
        if new_size <= 0:
            raise ValueError("Pool size must be positive")

        pool = self.pools.get(pool_name)
        if not pool:
            raise ValueError(f"Pool '{pool_name}' not found")

        old_size = pool.config.size
        pool.scale(new_size)
        logger.info(f"Scaled pool {pool_name} from {old_size} to {new_size} agents")

    def get_stuck_agents(self, timeout_seconds: Optional[float] = None) -> List[tuple]:
        """
        Find agents that have been working too long (stuck).

        Args:
            timeout_seconds: Override default timeout. If None, uses pool config.

        Returns:
            List of (pool_name, agent_id) tuples for stuck agents
        """
        stuck = []
        now = datetime.now()

        for pool_name, pool in self.pools.items():
            timeout = timeout_seconds or pool.config.timeout_seconds

            for agent in pool.agents:
                if agent.status == AgentStatus.WORKING and agent.last_activity:
                    elapsed = (now - agent.last_activity).total_seconds()
                    if elapsed > timeout:
                        stuck.append((pool_name, agent.id))
                        logger.warning(
                            f"Agent {agent.id} in pool {pool_name} "
                            f"has been working for {elapsed:.1f}s (timeout: {timeout}s)"
                        )

        return stuck

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all pools.

        Returns:
            Health status dictionary with overall status and per-pool details
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "pools": {},
            "total_agents": 0,
            "total_active": 0,
            "total_idle": 0,
            "total_stuck": 0,
        }

        for pool_name, pool in self.pools.items():
            metrics = pool.get_metrics()

            pool_health = {
                "status": "healthy",
                "total_agents": metrics.total_agents,
                "active_agents": metrics.active_agents,
                "idle_agents": metrics.idle_agents,
                "stuck_agents": metrics.stuck_agents,
                "queue_size": metrics.current_queue_size,
                "avg_response_time": metrics.average_response_time,
            }

            # Check for issues
            if metrics.stuck_agents > 0:
                pool_health["status"] = "degraded"
                health["overall_status"] = "degraded"

            if metrics.stuck_agents > metrics.total_agents * 0.3:
                pool_health["status"] = "unhealthy"
                health["overall_status"] = "unhealthy"

            if metrics.current_queue_size > metrics.total_agents * 2:
                pool_health["status"] = "overloaded"
                if health["overall_status"] == "healthy":
                    health["overall_status"] = "overloaded"

            health["pools"][pool_name] = pool_health
            health["total_agents"] += metrics.total_agents
            health["total_active"] += metrics.active_agents
            health["total_idle"] += metrics.idle_agents
            health["total_stuck"] += metrics.stuck_agents

        return health

    async def monitor_and_recover(self, check_interval: float = 30.0) -> None:
        """
        Background task to monitor agent health and recover stuck agents.

        Args:
            check_interval: Seconds between health checks
        """
        logger.info(f"Starting agent monitor (interval: {check_interval}s)")

        while True:
            try:
                await asyncio.sleep(check_interval)

                # Find stuck agents
                stuck_agents = self.get_stuck_agents()

                # Reset stuck agents
                for pool_name, agent_id in stuck_agents:
                    self.mark_agent_stuck(agent_id, pool_name)
                    # Optionally reset after marking
                    # self.reset_agent(agent_id, pool_name)

                # Log health status
                health = self.health_check()
                if health["overall_status"] != "healthy":
                    logger.warning(
                        f"System health: {health['overall_status']} - "
                        f"Stuck agents: {health['total_stuck']}"
                    )

            except Exception as e:
                logger.error(f"Error in monitor_and_recover: {e}", exc_info=True)

    def shutdown(self) -> None:
        """Shutdown all pools and cleanup resources."""
        logger.info("Shutting down agent pool manager")

        for pool_name, pool in self.pools.items():
            # Reset all agents
            for agent in pool.agents:
                if agent.status != AgentStatus.IDLE:
                    agent.reset()

            # Clear queues
            pool.task_queue.clear()

        logger.info("Agent pool manager shutdown complete")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics across all pools.

        Returns:
            Summary dictionary with aggregate statistics
        """
        metrics = self.get_all_pool_metrics()

        total_agents = sum(m.total_agents for m in metrics.values())
        total_active = sum(m.active_agents for m in metrics.values())
        total_idle = sum(m.idle_agents for m in metrics.values())
        total_stuck = sum(m.stuck_agents for m in metrics.values())
        total_completed = sum(m.total_tasks_completed for m in metrics.values())
        total_queued = sum(m.current_queue_size for m in metrics.values())

        # Calculate weighted average response time
        if total_completed > 0:
            weighted_avg_response = sum(
                m.average_response_time * m.total_tasks_completed
                for m in metrics.values()
            ) / total_completed
        else:
            weighted_avg_response = 0.0

        return {
            "timestamp": datetime.now().isoformat(),
            "total_pools": len(self.pools),
            "total_agents": total_agents,
            "active_agents": total_active,
            "idle_agents": total_idle,
            "stuck_agents": total_stuck,
            "total_tasks_completed": total_completed,
            "total_queued_tasks": total_queued,
            "average_response_time": weighted_avg_response,
            "utilization": total_active / total_agents if total_agents > 0 else 0.0,
        }
