"""
Gap Filling Node for Level 5.

Identifies and fills gaps in the solution coverage.
"""

from typing import Dict, Any, List
from ...schemas.state import Level5State, Solution


def fill_solution_gaps(state: Level5State) -> Level5State:
    """
    Find and fill gaps in solution coverage.

    Identifies:
    1. Aspects of original problem not addressed
    2. Missing connections between solutions
    3. Logical completeness issues

    Args:
        state: Level5State with solution_coverage_map

    Returns:
        Updated state with identified_gaps and gap_solutions
    """
    solution_coverage_map = state.get("solution_coverage_map", {})
    partial_solutions = state.get("partial_solutions", {})
    integrated_subproblems = state.get("integrated_subproblems", [])
    subproblem_dependencies = state.get("subproblem_dependencies", {"nodes": [], "edges": []})
    original_problem = state.get("original_problem", "")

    # Create subproblem lookup map
    subproblem_map = {sp["id"]: sp for sp in integrated_subproblems}

    # Identify gaps
    identified_gaps: List[Dict[str, Any]] = []

    # 1. Identify unsolved subproblems (coverage gaps)
    unsolved_subproblems = solution_coverage_map.get("unsolved_subproblems", [])
    for sp_id in unsolved_subproblems:
        subproblem = subproblem_map.get(sp_id)
        if subproblem:
            identified_gaps.append({
                "type": "unsolved_subproblem",
                "severity": "high",
                "subproblem_id": sp_id,
                "description": f"No solution provided for subproblem: {subproblem.get('title', sp_id)}",
                "subproblem": subproblem,
            })

    # 2. Identify connection gaps (solutions that don't reference their dependencies)
    connection_gaps = identify_connection_gaps(
        partial_solutions, subproblem_map, subproblem_dependencies
    )
    identified_gaps.extend(connection_gaps)

    # 3. Identify logical completeness gaps
    completeness_gaps = identify_completeness_gaps(
        partial_solutions, subproblem_map, original_problem
    )
    identified_gaps.extend(completeness_gaps)

    # Generate gap solutions
    gap_solutions: Dict[str, Solution] = {}

    for gap in identified_gaps:
        gap_type = gap.get("type")

        if gap_type == "unsolved_subproblem":
            # Generate placeholder/fallback solution for unsolved subproblem
            sp_id = gap.get("subproblem_id")
            subproblem = gap.get("subproblem", {})
            gap_solution = generate_placeholder_solution(subproblem)
            gap_solutions[sp_id] = gap_solution

        elif gap_type == "connection_gap":
            # Generate connection/glue solution
            connection_solution = generate_connection_solution(gap, partial_solutions)
            gap_id = gap.get("gap_id", f"connection_{len(gap_solutions)}")
            gap_solutions[gap_id] = connection_solution

        elif gap_type == "completeness_gap":
            # Generate completeness solution
            completeness_solution = generate_completeness_solution(gap)
            gap_id = gap.get("gap_id", f"completeness_{len(gap_solutions)}")
            gap_solutions[gap_id] = completeness_solution

    # Calculate gap metrics
    gap_metrics = {
        "total_gaps": len(identified_gaps),
        "gaps_by_type": {},
        "critical_gaps": [],
    }

    for gap in identified_gaps:
        gap_type = gap.get("type", "unknown")
        gap_metrics["gaps_by_type"][gap_type] = gap_metrics["gaps_by_type"].get(gap_type, 0) + 1
        if gap.get("severity") == "high":
            gap_metrics["critical_gaps"].append(gap)

    return {
        **state,
        "identified_gaps": identified_gaps,
        "gap_solutions": gap_solutions,
        "gap_metrics": gap_metrics,
    }


def identify_connection_gaps(
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any],
    dependency_graph: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Identify gaps in connections between solutions.

    Args:
        partial_solutions: Map of solutions
        subproblem_map: Map of subproblems
        dependency_graph: Dependency structure

    Returns:
        List of connection gaps
    """
    gaps = []

    # Check if solutions reference their dependencies
    for sp_id, solution in partial_solutions.items():
        subproblem = subproblem_map.get(sp_id)
        if not subproblem:
            continue

        dependencies = subproblem.get("dependencies", [])
        if not dependencies:
            continue

        content = solution.get("content", "").lower()
        reasoning = solution.get("reasoning", "").lower()
        text = content + " " + reasoning

        # Check if dependencies are mentioned in the solution
        for dep_id in dependencies:
            dep_subproblem = subproblem_map.get(dep_id)
            if not dep_subproblem:
                continue

            dep_title = dep_subproblem.get("title", "").lower()
            dep_keywords = dep_title.split()

            # Check if any keyword from dependency is mentioned
            referenced = any(keyword in text for keyword in dep_keywords if len(keyword) > 3)

            if not referenced and dep_id in partial_solutions:
                gaps.append({
                    "type": "connection_gap",
                    "severity": "medium",
                    "gap_id": f"connection_{sp_id}_{dep_id}",
                    "description": f"Solution {sp_id} does not explicitly reference dependency {dep_id}",
                    "source_subproblem": sp_id,
                    "dependency_subproblem": dep_id,
                })

    return gaps


def identify_completeness_gaps(
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any],
    original_problem: str
) -> List[Dict[str, Any]]:
    """
    Identify logical completeness gaps.

    Args:
        partial_solutions: Map of solutions
        subproblem_map: Map of subproblems
        original_problem: Original problem statement

    Returns:
        List of completeness gaps
    """
    gaps = []

    # Extract key requirements from original problem
    problem_keywords = extract_key_requirements(original_problem)

    # Check if all key requirements are addressed
    all_solution_text = " ".join(
        sol.get("content", "").lower() for sol in partial_solutions.values()
    )

    for keyword in problem_keywords:
        if keyword not in all_solution_text:
            gaps.append({
                "type": "completeness_gap",
                "severity": "medium",
                "gap_id": f"completeness_{keyword}",
                "description": f"Original problem mentions '{keyword}' but it's not addressed in solutions",
                "missing_requirement": keyword,
            })

    return gaps


def extract_key_requirements(problem_text: str) -> List[str]:
    """
    Extract key requirements from problem text.

    Args:
        problem_text: Original problem statement

    Returns:
        List of key requirement keywords
    """
    # Keywords that often indicate requirements
    requirement_indicators = [
        "must", "should", "required", "need", "implement",
        "create", "build", "design", "develop"
    ]

    keywords = []
    text_lower = problem_text.lower()

    # Simple extraction: look for nouns following requirement indicators
    words = text_lower.split()
    for i, word in enumerate(words):
        if word in requirement_indicators and i + 1 < len(words):
            next_word = words[i + 1]
            if len(next_word) > 3 and next_word.isalpha():
                keywords.append(next_word)

    return list(set(keywords))[:10]  # Return up to 10 unique keywords


def generate_placeholder_solution(subproblem: Dict[str, Any]) -> Solution:
    """
    Generate a placeholder solution for an unsolved subproblem.

    Args:
        subproblem: The unsolved subproblem

    Returns:
        Placeholder solution
    """
    sp_id = subproblem.get("id", "unknown")
    title = subproblem.get("title", "Unknown")
    description = subproblem.get("description", "")

    return {
        "subproblem_id": sp_id,
        "content": f"[PLACEHOLDER] Solution for {title}: This subproblem requires further analysis. "
                   f"Consider: {description[:200]}",
        "reasoning": "This is a placeholder solution generated during gap filling. "
                     "Manual implementation or further decomposition may be required.",
        "confidence": 0.3,
        "metadata": {
            "generated_by": "gap_filling_node",
            "is_placeholder": True,
        }
    }


def generate_connection_solution(
    gap: Dict[str, Any],
    partial_solutions: Dict[str, Solution]
) -> Solution:
    """
    Generate a connection/glue solution.

    Args:
        gap: Connection gap details
        partial_solutions: Existing solutions

    Returns:
        Connection solution
    """
    source_sp = gap.get("source_subproblem", "")
    dep_sp = gap.get("dependency_subproblem", "")

    return {
        "content": f"Integration bridge between {source_sp} and {dep_sp}: "
                   f"Ensure that output from {dep_sp} is properly formatted and passed to {source_sp}. "
                   f"Implement necessary adapters or transformations.",
        "reasoning": "This connection solution bridges identified gap between dependent solutions.",
        "confidence": 0.6,
        "metadata": {
            "generated_by": "gap_filling_node",
            "is_connection": True,
            "connects": [source_sp, dep_sp],
        }
    }


def generate_completeness_solution(gap: Dict[str, Any]) -> Solution:
    """
    Generate a completeness solution.

    Args:
        gap: Completeness gap details

    Returns:
        Completeness solution
    """
    missing_req = gap.get("missing_requirement", "unknown")

    return {
        "content": f"Additional consideration for '{missing_req}': "
                   f"Ensure that this aspect mentioned in the original problem is addressed. "
                   f"Review existing solutions and add necessary implementation.",
        "reasoning": "This addresses a requirement from the original problem that was not explicitly covered.",
        "confidence": 0.5,
        "metadata": {
            "generated_by": "gap_filling_node",
            "is_completeness": True,
            "addresses_requirement": missing_req,
        }
    }
