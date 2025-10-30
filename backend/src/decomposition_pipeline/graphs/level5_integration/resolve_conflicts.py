"""
Conflict Resolution Node for Level 5.

Resolves conflicts detected between partial solutions.
"""

from typing import Dict, Any, List
from ...schemas.state import Level5State, Solution


def resolve_solution_conflicts(state: Level5State) -> Level5State:
    """
    Resolve conflicts between partial solutions.

    Resolution strategies:
    1. Prioritize solutions from more confident agents
    2. Use voting if multiple solutions for same subproblem
    3. Escalate to larger model for complex conflicts
    4. Flag for human review if unresolvable

    Args:
        state: Level5State with detected_conflicts

    Returns:
        Updated state with resolved conflicts and updated partial_solutions
    """
    detected_conflicts = state.get("detected_conflicts", [])
    partial_solutions = state.get("partial_solutions", {})
    integrated_subproblems = state.get("integrated_subproblems", [])

    # If no conflicts, nothing to resolve
    if not detected_conflicts:
        return {
            **state,
            "resolution_summary": {
                "total_conflicts": 0,
                "resolved": 0,
                "escalated": 0,
                "resolutions": [],
            }
        }

    # Create subproblem lookup map
    subproblem_map = {sp["id"]: sp for sp in integrated_subproblems}

    resolutions: List[Dict[str, Any]] = []
    escalated_conflicts: List[Dict[str, Any]] = []
    resolved_count = 0

    # Process each conflict
    for conflict in detected_conflicts:
        conflict_type = conflict.get("type")
        severity = conflict.get("severity", "medium")
        subproblem_ids = conflict.get("subproblem_ids", [])

        if conflict_type == "logical_contradiction":
            resolution = resolve_logical_contradiction(
                conflict, partial_solutions, subproblem_map
            )
        elif conflict_type == "incompatible_assumptions":
            resolution = resolve_incompatible_assumptions(
                conflict, partial_solutions, subproblem_map
            )
        elif conflict_type == "resource_conflict":
            resolution = resolve_resource_conflict(
                conflict, partial_solutions, subproblem_map
            )
        elif conflict_type == "timing_conflict":
            resolution = resolve_timing_conflict(
                conflict, partial_solutions, subproblem_map
            )
        elif conflict_type == "dependency_conflict":
            resolution = resolve_dependency_conflict(
                conflict, partial_solutions, subproblem_map
            )
        else:
            resolution = {
                "status": "escalated",
                "reason": f"Unknown conflict type: {conflict_type}",
            }

        if resolution["status"] == "resolved":
            resolved_count += 1
            resolutions.append({
                "conflict": conflict,
                "resolution": resolution,
            })
        else:
            escalated_conflicts.append({
                "conflict": conflict,
                "reason": resolution.get("reason", "Unable to resolve automatically"),
            })

    # Create resolution summary
    resolution_summary = {
        "total_conflicts": len(detected_conflicts),
        "resolved": resolved_count,
        "escalated": len(escalated_conflicts),
        "resolutions": resolutions,
        "escalated_conflicts": escalated_conflicts,
    }

    return {
        **state,
        "resolution_summary": resolution_summary,
    }


def resolve_logical_contradiction(
    conflict: Dict[str, Any],
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve logical contradictions by prioritizing higher confidence solutions.

    Args:
        conflict: Conflict details
        partial_solutions: Map of solutions
        subproblem_map: Map of subproblems

    Returns:
        Resolution result
    """
    subproblem_ids = conflict.get("subproblem_ids", [])

    if len(subproblem_ids) != 2:
        return {"status": "escalated", "reason": "Multiple contradictions detected"}

    sp_id_a, sp_id_b = subproblem_ids
    sol_a = partial_solutions.get(sp_id_a, {})
    sol_b = partial_solutions.get(sp_id_b, {})

    confidence_a = sol_a.get("confidence", 0.5)
    confidence_b = sol_b.get("confidence", 0.5)

    # If confidence difference is significant, prioritize higher confidence
    if abs(confidence_a - confidence_b) > 0.15:
        preferred = sp_id_a if confidence_a > confidence_b else sp_id_b
        return {
            "status": "resolved",
            "strategy": "confidence_prioritization",
            "preferred_solution": preferred,
            "reason": f"Prioritized solution with higher confidence ({max(confidence_a, confidence_b):.2f})",
        }
    else:
        # Confidence too similar, escalate
        return {
            "status": "escalated",
            "reason": f"Similar confidence levels ({confidence_a:.2f} vs {confidence_b:.2f}), requires manual review",
        }


def resolve_incompatible_assumptions(
    conflict: Dict[str, Any],
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve incompatible assumptions.

    Args:
        conflict: Conflict details
        partial_solutions: Map of solutions
        subproblem_map: Map of subproblems

    Returns:
        Resolution result
    """
    # Assumptions typically need human review or further analysis
    # For now, we flag them but don't auto-resolve
    return {
        "status": "escalated",
        "reason": "Assumption conflicts require domain expertise to resolve",
        "recommendation": "Review assumptions and validate compatibility",
    }


def resolve_resource_conflict(
    conflict: Dict[str, Any],
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve resource conflicts.

    Args:
        conflict: Conflict details
        partial_solutions: Map of solutions
        subproblem_map: Map of subproblems

    Returns:
        Resolution result
    """
    shared_resources = conflict.get("shared_resources", [])
    subproblem_ids = conflict.get("subproblem_ids", [])

    # Resource conflicts can often coexist if properly coordinated
    return {
        "status": "resolved",
        "strategy": "resource_coordination",
        "reason": f"Shared resources ({', '.join(shared_resources)}) can be coordinated through proper interfaces",
        "recommendation": f"Ensure solutions {', '.join(subproblem_ids)} coordinate access to shared resources",
    }


def resolve_timing_conflict(
    conflict: Dict[str, Any],
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve timing conflicts.

    Args:
        conflict: Conflict details
        partial_solutions: Map of solutions
        subproblem_map: Map of subproblems

    Returns:
        Resolution result
    """
    subproblem_ids = conflict.get("subproblem_ids", [])

    # Check if there's a dependency relationship
    dependencies_exist = False
    for sp_id in subproblem_ids:
        subproblem = subproblem_map.get(sp_id, {})
        deps = subproblem.get("dependencies", [])
        if any(dep in subproblem_ids for dep in deps):
            dependencies_exist = True
            break

    if dependencies_exist:
        return {
            "status": "resolved",
            "strategy": "dependency_ordering",
            "reason": "Timing can be resolved through dependency graph execution order",
        }
    else:
        return {
            "status": "escalated",
            "reason": "Timing conflict without clear dependency relationship",
            "recommendation": "Establish explicit execution order or timing constraints",
        }


def resolve_dependency_conflict(
    conflict: Dict[str, Any],
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resolve dependency conflicts (missing dependencies).

    Args:
        conflict: Conflict details
        partial_solutions: Map of solutions
        subproblem_map: Map of subproblems

    Returns:
        Resolution result
    """
    unsolved_dependencies = conflict.get("unsolved_dependencies", [])

    # Dependency conflicts indicate gaps that need to be filled
    # This will be handled by the gap filling node
    return {
        "status": "deferred",
        "reason": "Dependency conflicts will be addressed in gap filling phase",
        "unsolved_dependencies": unsolved_dependencies,
    }
