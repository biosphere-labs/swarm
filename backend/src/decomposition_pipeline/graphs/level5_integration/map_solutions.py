"""
Solution Mapping Node for Level 5.

Maps each partial solution back to the original problem structure
and identifies coverage.
"""

from typing import Dict, Any, List
from ...schemas.state import Level5State, Solution, Subproblem


def map_solutions_to_problem(state: Level5State) -> Level5State:
    """
    Map each partial solution back to original problem structure.

    Analyzes which parts of the original problem are addressed by each
    partial solution and creates a coverage map.

    Args:
        state: Level5State with partial_solutions and integrated_subproblems

    Returns:
        Updated state with solution_coverage_map
    """
    partial_solutions = state.get("partial_solutions", {})
    integrated_subproblems = state.get("integrated_subproblems", [])
    subproblem_dependencies = state.get("subproblem_dependencies", {"nodes": [], "edges": []})

    # Create a map of subproblem_id -> subproblem for quick lookup
    subproblem_map = {sp["id"]: sp for sp in integrated_subproblems}

    # Build coverage map
    coverage_map: Dict[str, Any] = {
        "total_subproblems": len(integrated_subproblems),
        "solved_subproblems": len(partial_solutions),
        "unsolved_subproblems": [],
        "coverage_by_paradigm": {},
        "coverage_by_dependency_level": {},
        "solution_details": {},
    }

    # Identify unsolved subproblems
    solved_ids = set(partial_solutions.keys())
    all_ids = {sp["id"] for sp in integrated_subproblems}
    unsolved_ids = all_ids - solved_ids
    coverage_map["unsolved_subproblems"] = list(unsolved_ids)

    # Group coverage by paradigm
    paradigm_coverage: Dict[str, Dict[str, int]] = {}
    for sp in integrated_subproblems:
        paradigm = sp.get("paradigm", "unknown")
        if paradigm not in paradigm_coverage:
            paradigm_coverage[paradigm] = {"total": 0, "solved": 0}
        paradigm_coverage[paradigm]["total"] += 1
        if sp["id"] in solved_ids:
            paradigm_coverage[paradigm]["solved"] += 1

    coverage_map["coverage_by_paradigm"] = paradigm_coverage

    # Analyze dependency levels (topological layers)
    dependency_levels = calculate_dependency_levels(
        integrated_subproblems, subproblem_dependencies
    )
    coverage_map["coverage_by_dependency_level"] = analyze_dependency_level_coverage(
        dependency_levels, solved_ids
    )

    # Create detailed solution mapping
    for sp_id, solution in partial_solutions.items():
        subproblem = subproblem_map.get(sp_id)
        if subproblem:
            coverage_map["solution_details"][sp_id] = {
                "subproblem_title": subproblem.get("title", ""),
                "subproblem_description": subproblem.get("description", ""),
                "paradigm": subproblem.get("paradigm", ""),
                "dependencies": subproblem.get("dependencies", []),
                "confidence": solution.get("confidence", 0.0),
                "agent_pool": solution.get("agent_pool", "unknown"),
                "solution_length": len(solution.get("content", "")),
            }

    # Calculate overall coverage percentage
    if coverage_map["total_subproblems"] > 0:
        coverage_map["coverage_percentage"] = (
            coverage_map["solved_subproblems"] / coverage_map["total_subproblems"]
        ) * 100
    else:
        coverage_map["coverage_percentage"] = 0.0

    return {
        **state,
        "solution_coverage_map": coverage_map,
    }


def calculate_dependency_levels(
    subproblems: List[Subproblem],
    dependency_graph: Dict[str, Any]
) -> Dict[str, int]:
    """
    Calculate the dependency level for each subproblem.

    Level 0 = no dependencies
    Level 1 = depends only on level 0
    Level n = depends on at most level n-1

    Args:
        subproblems: List of subproblems
        dependency_graph: Dependency graph structure

    Returns:
        Dict mapping subproblem_id to dependency level
    """
    # Build dependency map
    dependencies_map: Dict[str, List[str]] = {}
    for sp in subproblems:
        dependencies_map[sp["id"]] = sp.get("dependencies", [])

    # Calculate levels using BFS
    levels: Dict[str, int] = {}
    unprocessed = set(sp["id"] for sp in subproblems)

    current_level = 0
    while unprocessed:
        # Find all nodes with no unprocessed dependencies
        ready = []
        for sp_id in unprocessed:
            deps = dependencies_map.get(sp_id, [])
            if all(dep in levels or dep not in unprocessed for dep in deps):
                # Calculate level based on max dependency level
                if deps:
                    max_dep_level = max(
                        levels.get(dep, 0) for dep in deps if dep in levels
                    )
                    ready.append((sp_id, max_dep_level + 1))
                else:
                    ready.append((sp_id, 0))

        if not ready:
            # Circular dependency or isolated nodes
            for sp_id in unprocessed:
                levels[sp_id] = current_level
            break

        for sp_id, level in ready:
            levels[sp_id] = level
            unprocessed.remove(sp_id)

        current_level += 1

    return levels


def analyze_dependency_level_coverage(
    dependency_levels: Dict[str, int],
    solved_ids: set
) -> Dict[int, Dict[str, int]]:
    """
    Analyze coverage at each dependency level.

    Args:
        dependency_levels: Map of subproblem_id to level
        solved_ids: Set of solved subproblem IDs

    Returns:
        Dict mapping level to coverage statistics
    """
    level_coverage: Dict[int, Dict[str, int]] = {}

    for sp_id, level in dependency_levels.items():
        if level not in level_coverage:
            level_coverage[level] = {"total": 0, "solved": 0}
        level_coverage[level]["total"] += 1
        if sp_id in solved_ids:
            level_coverage[level]["solved"] += 1

    # Calculate percentages
    for level, stats in level_coverage.items():
        if stats["total"] > 0:
            stats["percentage"] = (stats["solved"] / stats["total"]) * 100
        else:
            stats["percentage"] = 0.0

    return level_coverage
