"""
Solution Synthesis Node for Level 5.

Combines all partial solutions into an integrated final solution.
"""

from typing import Dict, Any, List
from ...schemas.state import Level5State, Solution


def synthesize_final_solution(state: Level5State) -> Level5State:
    """
    Combine all partial solutions into integrated final solution.

    Creates:
    1. Integrated solution combining all partial solutions
    2. Narrative explanation of complete solution
    3. Implementation plan with dependencies

    Args:
        state: Level5State with partial_solutions and gap_solutions

    Returns:
        Updated state with integrated_solution
    """
    partial_solutions = state.get("partial_solutions", {})
    gap_solutions = state.get("gap_solutions", {})
    integrated_subproblems = state.get("integrated_subproblems", [])
    subproblem_dependencies = state.get("subproblem_dependencies", {"nodes": [], "edges": []})
    original_problem = state.get("original_problem", "")
    solution_coverage_map = state.get("solution_coverage_map", {})
    resolution_summary = state.get("resolution_summary", {})

    # Combine partial solutions and gap solutions
    all_solutions = {**partial_solutions, **gap_solutions}

    # Create subproblem lookup map
    subproblem_map = {sp["id"]: sp for sp in integrated_subproblems}

    # Generate synthesis
    synthesis = generate_solution_synthesis(
        all_solutions,
        subproblem_map,
        subproblem_dependencies,
        original_problem,
        solution_coverage_map,
        resolution_summary
    )

    # Create integrated solution
    integrated_solution: Solution = {
        "content": synthesis["solution_content"],
        "reasoning": synthesis["solution_reasoning"],
        "confidence": synthesis["overall_confidence"],
        "metadata": {
            "synthesis_method": "topological_integration",
            "component_count": len(all_solutions),
            "coverage_percentage": solution_coverage_map.get("coverage_percentage", 0),
            "implementation_plan": synthesis["implementation_plan"],
            "integration_notes": synthesis["integration_notes"],
        }
    }

    return {
        **state,
        "integrated_solution": integrated_solution,
    }


def generate_solution_synthesis(
    all_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any],
    dependency_graph: Dict[str, Any],
    original_problem: str,
    coverage_map: Dict[str, Any],
    resolution_summary: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate the complete solution synthesis.

    Args:
        all_solutions: Combined partial and gap solutions
        subproblem_map: Map of subproblems
        dependency_graph: Dependency structure
        original_problem: Original problem statement
        coverage_map: Solution coverage information
        resolution_summary: Conflict resolution information

    Returns:
        Synthesis containing content, reasoning, confidence, and plan
    """
    # Sort solutions by dependency order
    sorted_solution_ids = topological_sort_solutions(
        list(all_solutions.keys()),
        subproblem_map,
        dependency_graph
    )

    # Build solution content
    solution_sections: List[str] = []
    solution_sections.append(f"# Integrated Solution for: {original_problem[:200]}")
    solution_sections.append("\n## Overview")
    solution_sections.append(generate_overview_section(
        all_solutions, coverage_map, resolution_summary
    ))

    # Add solutions grouped by paradigm
    solution_sections.append("\n## Solution Components")
    paradigm_groups = group_solutions_by_paradigm(sorted_solution_ids, subproblem_map)

    for paradigm, sp_ids in paradigm_groups.items():
        solution_sections.append(f"\n### {paradigm.title()} Components")
        for sp_id in sp_ids:
            if sp_id in all_solutions:
                solution = all_solutions[sp_id]
                subproblem = subproblem_map.get(sp_id, {})
                title = subproblem.get("title", sp_id)
                content = solution.get("content", "")
                solution_sections.append(f"\n**{title}**")
                solution_sections.append(content[:500])  # Truncate if too long

    # Generate implementation plan
    implementation_plan = generate_implementation_plan(
        sorted_solution_ids,
        all_solutions,
        subproblem_map,
        dependency_graph
    )

    # Build reasoning
    reasoning_parts: List[str] = []
    reasoning_parts.append(f"This integrated solution combines {len(all_solutions)} component solutions.")
    reasoning_parts.append(f"Coverage: {coverage_map.get('coverage_percentage', 0):.1f}% of subproblems solved.")

    if resolution_summary.get("total_conflicts", 0) > 0:
        reasoning_parts.append(
            f"Resolved {resolution_summary.get('resolved', 0)} of {resolution_summary.get('total_conflicts', 0)} conflicts."
        )

    reasoning_parts.append("Solutions are integrated following dependency order to ensure logical coherence.")

    # Calculate overall confidence
    overall_confidence = calculate_overall_confidence(all_solutions)

    # Generate integration notes
    integration_notes = generate_integration_notes(
        all_solutions, coverage_map, resolution_summary
    )

    return {
        "solution_content": "\n".join(solution_sections),
        "solution_reasoning": " ".join(reasoning_parts),
        "overall_confidence": overall_confidence,
        "implementation_plan": implementation_plan,
        "integration_notes": integration_notes,
    }


def topological_sort_solutions(
    solution_ids: List[str],
    subproblem_map: Dict[str, Any],
    dependency_graph: Dict[str, Any]
) -> List[str]:
    """
    Sort solutions in topological order based on dependencies.

    Args:
        solution_ids: List of solution IDs
        subproblem_map: Map of subproblems
        dependency_graph: Dependency structure

    Returns:
        Sorted list of solution IDs
    """
    # Build dependency map
    dependencies: Dict[str, List[str]] = {}
    for sp_id in solution_ids:
        subproblem = subproblem_map.get(sp_id, {})
        deps = subproblem.get("dependencies", [])
        # Only include dependencies that are in our solution set
        dependencies[sp_id] = [d for d in deps if d in solution_ids]

    # Kahn's algorithm for topological sort
    in_degree = {sp_id: 0 for sp_id in solution_ids}
    for sp_id, deps in dependencies.items():
        for dep in deps:
            if dep in in_degree:
                in_degree[sp_id] += 1

    queue = [sp_id for sp_id, degree in in_degree.items() if degree == 0]
    sorted_ids = []

    while queue:
        sp_id = queue.pop(0)
        sorted_ids.append(sp_id)

        # Reduce in-degree for dependents
        for other_id, deps in dependencies.items():
            if sp_id in deps and other_id not in sorted_ids:
                in_degree[other_id] -= 1
                if in_degree[other_id] == 0:
                    queue.append(other_id)

    # If we couldn't sort all (circular dependencies), append remaining
    remaining = set(solution_ids) - set(sorted_ids)
    sorted_ids.extend(remaining)

    return sorted_ids


def generate_overview_section(
    all_solutions: Dict[str, Solution],
    coverage_map: Dict[str, Any],
    resolution_summary: Dict[str, Any]
) -> str:
    """Generate overview section."""
    overview_parts = []

    overview_parts.append(
        f"This solution integrates {len(all_solutions)} components "
        f"covering {coverage_map.get('coverage_percentage', 0):.1f}% of identified subproblems."
    )

    total_conflicts = resolution_summary.get("total_conflicts", 0)
    if total_conflicts > 0:
        resolved = resolution_summary.get("resolved", 0)
        overview_parts.append(
            f"Conflict resolution: {resolved}/{total_conflicts} conflicts resolved automatically."
        )

    paradigm_coverage = coverage_map.get("coverage_by_paradigm", {})
    if paradigm_coverage:
        overview_parts.append(
            f"Solution spans {len(paradigm_coverage)} decomposition paradigms."
        )

    return " ".join(overview_parts)


def group_solutions_by_paradigm(
    solution_ids: List[str],
    subproblem_map: Dict[str, Any]
) -> Dict[str, List[str]]:
    """Group solutions by their paradigm."""
    groups: Dict[str, List[str]] = {}

    for sp_id in solution_ids:
        subproblem = subproblem_map.get(sp_id, {})
        paradigm = subproblem.get("paradigm", "general")

        if paradigm not in groups:
            groups[paradigm] = []
        groups[paradigm].append(sp_id)

    return groups


def generate_implementation_plan(
    sorted_solution_ids: List[str],
    all_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any],
    dependency_graph: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate implementation plan with dependencies.

    Args:
        sorted_solution_ids: Solutions in topological order
        all_solutions: All solutions
        subproblem_map: Map of subproblems
        dependency_graph: Dependency structure

    Returns:
        Implementation plan as list of steps
    """
    plan: List[Dict[str, Any]] = []

    # Group solutions into implementation phases
    phases = create_implementation_phases(
        sorted_solution_ids, subproblem_map, dependency_graph
    )

    for phase_num, sp_ids in enumerate(phases, start=1):
        phase_step = {
            "phase": phase_num,
            "name": f"Phase {phase_num}",
            "components": [],
            "can_parallelize": len(sp_ids) > 1,
        }

        for sp_id in sp_ids:
            subproblem = subproblem_map.get(sp_id, {})
            phase_step["components"].append({
                "id": sp_id,
                "title": subproblem.get("title", sp_id),
                "paradigm": subproblem.get("paradigm", ""),
            })

        plan.append(phase_step)

    return plan


def create_implementation_phases(
    sorted_solution_ids: List[str],
    subproblem_map: Dict[str, Any],
    dependency_graph: Dict[str, Any]
) -> List[List[str]]:
    """
    Create implementation phases based on dependencies.

    Args:
        sorted_solution_ids: Solutions in topological order
        subproblem_map: Map of subproblems
        dependency_graph: Dependency structure

    Returns:
        List of phases, each containing solution IDs that can run in parallel
    """
    # Track completion
    completed = set()
    phases: List[List[str]] = []

    remaining = set(sorted_solution_ids)

    while remaining:
        # Find all solutions whose dependencies are completed
        ready = []
        for sp_id in remaining:
            subproblem = subproblem_map.get(sp_id, {})
            deps = set(subproblem.get("dependencies", []))
            if deps.issubset(completed):
                ready.append(sp_id)

        if not ready:
            # No progress possible, add remaining as final phase
            phases.append(list(remaining))
            break

        phases.append(ready)
        completed.update(ready)
        remaining -= set(ready)

    return phases


def calculate_overall_confidence(all_solutions: Dict[str, Solution]) -> float:
    """
    Calculate overall confidence score.

    Args:
        all_solutions: All solutions

    Returns:
        Overall confidence (0-1)
    """
    if not all_solutions:
        return 0.0

    confidences = [sol.get("confidence", 0.5) for sol in all_solutions.values()]

    # Use weighted average, giving more weight to lower confidences (conservative)
    sorted_conf = sorted(confidences)
    if len(sorted_conf) == 1:
        return sorted_conf[0]

    # Weight: 50% average, 30% minimum, 20% median
    avg_conf = sum(confidences) / len(confidences)
    min_conf = min(confidences)
    median_conf = sorted_conf[len(sorted_conf) // 2]

    overall = 0.5 * avg_conf + 0.3 * min_conf + 0.2 * median_conf
    return round(overall, 3)


def generate_integration_notes(
    all_solutions: Dict[str, Solution],
    coverage_map: Dict[str, Any],
    resolution_summary: Dict[str, Any]
) -> List[str]:
    """Generate integration notes and considerations."""
    notes = []

    # Coverage notes
    coverage_pct = coverage_map.get("coverage_percentage", 0)
    if coverage_pct < 100:
        unsolved_count = len(coverage_map.get("unsolved_subproblems", []))
        notes.append(
            f"Note: {unsolved_count} subproblems have placeholder solutions and may require further attention."
        )

    # Conflict notes
    escalated_count = resolution_summary.get("escalated", 0)
    if escalated_count > 0:
        notes.append(
            f"Attention: {escalated_count} conflicts require manual review."
        )

    # Confidence notes
    low_confidence_solutions = [
        sp_id for sp_id, sol in all_solutions.items()
        if sol.get("confidence", 1.0) < 0.6
    ]
    if low_confidence_solutions:
        notes.append(
            f"Review recommended for {len(low_confidence_solutions)} low-confidence solutions."
        )

    return notes
