"""
Level 4: Solution Generation Subgraph.

Implements the complete Level 4 architecture from brainstorm_1.md lines 448-518.
Routes subproblems to agent pools and executes them in parallel with dependency management.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from ...schemas.state import Level4State
from .route_to_pools import route_subproblems_to_pools
from .execute_parallel import execute_parallel_solutions
from .monitor_progress import monitor_execution_progress
from .collect_solutions import collect_and_validate_solutions


def should_retry(state: Level4State) -> Literal["retry", "complete"]:
    """
    Conditional routing: Determine if we should retry failed subproblems.

    Args:
        state: Current Level4State

    Returns:
        "retry" if there are failed subproblems that should be retried,
        "complete" if all done or too many failures
    """
    needs_retry = state.get("needs_retry", [])
    failed_subproblems = state.get("failed_subproblems", [])

    # If no failures, we're done
    if not failed_subproblems:
        return "complete"

    # If too many failures (>10), escalate to human instead of retrying
    if len(failed_subproblems) > 10:
        return "complete"

    # If we have retry candidates, retry
    if needs_retry:
        # Check if we've already retried (prevent infinite loops)
        retry_count = state.get("retry_count", 0)
        if retry_count >= 2:  # Max 2 retries
            return "complete"
        return "retry"

    return "complete"


def retry_failed_subproblems(state: Level4State) -> Level4State:
    """
    Node function: Retry failed subproblems with alternative strategies.

    Updates routing decisions and agent assignments for failed subproblems,
    then re-executes them.

    Args:
        state: Level4State with needs_retry information

    Returns:
        Updated state ready for re-execution
    """
    needs_retry = state.get("needs_retry", [])
    failed_subproblems = state.get("failed_subproblems", [])
    agent_assignments = state.get("agent_assignments", {})
    retry_count = state.get("retry_count", 0)

    # Update agent assignments based on retry strategy
    for retry_candidate in needs_retry:
        sp_id = retry_candidate["subproblem_id"]
        strategy = retry_candidate["retry_strategy"]

        if strategy == "alternate_pool":
            # Try general pool if not already using it
            current_pool = agent_assignments.get(sp_id, "")
            if "general" not in current_pool:
                agent_assignments[sp_id] = "general_pool"

        elif strategy == "larger_model":
            # Force use of general pool with larger model
            agent_assignments[sp_id] = "general_pool"

    # Remove retried subproblems from failed list
    retry_ids = {r["subproblem_id"] for r in needs_retry}
    updated_failed = [sp_id for sp_id in failed_subproblems if sp_id not in retry_ids]

    return {
        **state,
        "agent_assignments": agent_assignments,
        "failed_subproblems": updated_failed,
        "retry_count": retry_count + 1,
        "needs_retry": [],  # Clear retry list
    }


def create_level4_graph() -> StateGraph:
    """
    Create the Level 4 Solution Generation subgraph.

    Graph structure:
    1. route_to_pools - Analyze and route subproblems to agent pools
    2. execute_parallel - Execute subproblems in parallel batches
    3. monitor_progress - Track execution progress
    4. collect_solutions - Gather and validate solutions
    5. [conditional] retry_failed - Retry failures with alternate strategies
    6. END

    Returns:
        Compiled StateGraph for Level 4
    """
    # Create graph
    graph = StateGraph(Level4State)

    # Add nodes
    graph.add_node("route_to_pools", route_subproblems_to_pools)
    graph.add_node("execute_parallel", execute_parallel_solutions)
    graph.add_node("monitor_progress", monitor_execution_progress)
    graph.add_node("collect_solutions", collect_and_validate_solutions)
    graph.add_node("retry_failed", retry_failed_subproblems)

    # Define edges
    graph.set_entry_point("route_to_pools")
    graph.add_edge("route_to_pools", "execute_parallel")
    graph.add_edge("execute_parallel", "monitor_progress")
    graph.add_edge("monitor_progress", "collect_solutions")

    # Conditional routing after collection
    graph.add_conditional_edges(
        "collect_solutions",
        should_retry,
        {
            "retry": "retry_failed",
            "complete": END,
        }
    )

    # If retrying, go back to execution
    graph.add_edge("retry_failed", "execute_parallel")

    return graph


def compile_level4_graph() -> StateGraph:
    """
    Compile the Level 4 graph for execution.

    Returns:
        Compiled graph ready for invocation
    """
    graph = create_level4_graph()
    return graph.compile()


# Export the compiled graph
level4_graph = compile_level4_graph()
