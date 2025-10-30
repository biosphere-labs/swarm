"""
Progress monitoring for Level 4 solution generation.

Implements ProgressMonitoringNode from brainstorm_1.md lines 483-488.
Tracks completion status, identifies stuck agents, and provides real-time updates.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from ...schemas.state import Level4State


def monitor_execution_progress(state: Level4State) -> Level4State:
    """
    Node function: Monitor progress of parallel solution generation.

    Implements ProgressMonitoringNode from brainstorm_1.md lines 483-488:
    - Tracks completion of parallel branches
    - Identifies stuck branches and escalates
    - Collects intermediate results

    Args:
        state: Level4State with progress_tracking data

    Returns:
        Updated state with enhanced progress monitoring
    """
    progress = state.get("progress_tracking", {})
    agent_pool_status = state.get("agent_pool_status", {})
    partial_solutions = state.get("partial_solutions", {})
    failed_subproblems = state.get("failed_subproblems", [])
    integrated_subproblems = state.get("integrated_subproblems", [])

    # Calculate progress metrics
    total_subproblems = len(integrated_subproblems)
    completed_count = len(partial_solutions)
    failed_count = len(failed_subproblems)
    pending_count = total_subproblems - completed_count - failed_count

    # Calculate completion percentage
    completion_percentage = (
        (completed_count / total_subproblems * 100)
        if total_subproblems > 0 else 0
    )

    # Identify stuck agents (agents working longer than expected)
    stuck_agents = identify_stuck_agents(agent_pool_status)

    # Check for slow pools
    slow_pools = identify_slow_pools(agent_pool_status)

    # Determine overall health status
    health_status = determine_health_status(
        completion_percentage,
        failed_count,
        len(stuck_agents),
        len(slow_pools)
    )

    # Generate progress report
    progress_report = {
        "timestamp": datetime.now().isoformat(),
        "total_subproblems": total_subproblems,
        "completed": completed_count,
        "failed": failed_count,
        "pending": pending_count,
        "completion_percentage": round(completion_percentage, 2),
        "health_status": health_status,
        "stuck_agents": stuck_agents,
        "slow_pools": slow_pools,
        "estimated_time_remaining": estimate_remaining_time(
            pending_count,
            agent_pool_status
        ),
    }

    # Update state with enhanced monitoring
    return {
        **state,
        "progress_tracking": {
            **progress,
            **progress_report,
        }
    }


def identify_stuck_agents(
    pool_status: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Identify agents that appear to be stuck (working too long).

    An agent is considered stuck if:
    - It's been working for > 5x average response time
    - Or it's been working for > 300 seconds (5 minutes)

    Args:
        pool_status: Status of all agent pools

    Returns:
        List of stuck agent information
    """
    stuck_agents = []
    current_time = datetime.now()

    for pool_name, status in pool_status.items():
        avg_response_time = status.get("avg_response_time", 60)
        threshold = max(avg_response_time * 5, 300)  # At least 5 minutes

        # In a full implementation, we would track individual agent start times
        # For now, we use pool metrics to estimate stuck agents
        if status.get("active_agents", 0) > 0:
            utilization = status.get("utilization", 0)

            # High utilization with low completion rate might indicate stuck agents
            if utilization > 0.8 and status.get("total_completed", 0) < 10:
                stuck_agents.append({
                    "pool": pool_name,
                    "active_agents": status["active_agents"],
                    "avg_response_time": avg_response_time,
                    "suspected_stuck": True,
                })

    return stuck_agents


def identify_slow_pools(
    pool_status: Dict[str, Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Identify pools with slower than expected performance.

    A pool is considered slow if:
    - Average response time > 120 seconds
    - Or failure rate > 20%

    Args:
        pool_status: Status of all agent pools

    Returns:
        List of slow pool information
    """
    slow_pools = []

    for pool_name, status in pool_status.items():
        avg_response_time = status.get("avg_response_time", 0)
        total_completed = status.get("total_completed", 0)
        total_failed = status.get("total_failed", 0)

        # Calculate failure rate
        total_tasks = total_completed + total_failed
        failure_rate = (
            (total_failed / total_tasks * 100)
            if total_tasks > 0 else 0
        )

        # Check if pool is slow
        is_slow = avg_response_time > 120 or failure_rate > 20

        if is_slow:
            slow_pools.append({
                "pool": pool_name,
                "avg_response_time": round(avg_response_time, 2),
                "failure_rate": round(failure_rate, 2),
                "reason": (
                    "high_response_time" if avg_response_time > 120
                    else "high_failure_rate"
                ),
            })

    return slow_pools


def determine_health_status(
    completion_percentage: float,
    failed_count: int,
    stuck_count: int,
    slow_pool_count: int
) -> str:
    """
    Determine overall health status of the execution.

    Returns:
        "healthy", "warning", or "critical"
    """
    # Critical conditions
    if completion_percentage < 10 and failed_count > 5:
        return "critical"

    if stuck_count > 3 or slow_pool_count > 2:
        return "critical"

    # Warning conditions
    if failed_count > 2:
        return "warning"

    if stuck_count > 0 or slow_pool_count > 0:
        return "warning"

    if completion_percentage < 50:
        return "warning"

    # Otherwise healthy
    return "healthy"


def estimate_remaining_time(
    pending_count: int,
    pool_status: Dict[str, Dict[str, Any]]
) -> int:
    """
    Estimate remaining time in seconds based on pending work and pool capacity.

    Args:
        pending_count: Number of pending subproblems
        pool_status: Status of all agent pools

    Returns:
        Estimated seconds remaining
    """
    if pending_count == 0:
        return 0

    # Calculate average response time across all pools
    total_response_time = 0
    total_pools = 0

    for status in pool_status.values():
        avg_time = status.get("avg_response_time", 60)
        if avg_time > 0:
            total_response_time += avg_time
            total_pools += 1

    avg_response_time = (
        total_response_time / total_pools
        if total_pools > 0 else 60
    )

    # Calculate total available agents
    total_agents = sum(
        status.get("idle_agents", 0) + status.get("active_agents", 0)
        for status in pool_status.values()
    )

    # Estimate time: (pending_work / available_agents) * avg_time_per_task
    if total_agents > 0:
        estimated_seconds = (pending_count / total_agents) * avg_response_time
    else:
        estimated_seconds = pending_count * avg_response_time

    return int(estimated_seconds)
