"""
Agent pool management for the decomposition pipeline.

This package provides:
- Agent and pool type definitions
- Pool manager for coordinating all agent pools
- Routing logic for selecting optimal pools for subproblems
"""

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

from .pool_manager import AgentPoolManager

from .routing import (
    select_pool_for_subproblem,
    score_domain_match,
    should_use_general_pool,
    get_routing_explanation,
    batch_route_subproblems,
    recommend_pool_scaling,
)

__all__ = [
    # Types
    "Agent",
    "AgentPool",
    "AgentPoolConfig",
    "AgentStatus",
    "PoolMetrics",
    "PoolType",
    # Configs
    "PARADIGM_POOL_CONFIGS",
    "DOMAIN_POOL_CONFIGS",
    "GENERAL_POOL_CONFIG",
    # Manager
    "AgentPoolManager",
    # Routing
    "select_pool_for_subproblem",
    "score_domain_match",
    "should_use_general_pool",
    "get_routing_explanation",
    "batch_route_subproblems",
    "recommend_pool_scaling",
]
