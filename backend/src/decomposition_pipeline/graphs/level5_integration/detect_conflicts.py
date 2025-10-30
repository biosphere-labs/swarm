"""
Conflict Detection Node for Level 5.

Detects contradictions and conflicts between partial solutions.
"""

from typing import Dict, Any, List
from ...schemas.state import Level5State, Solution


def detect_solution_conflicts(state: Level5State) -> Level5State:
    """
    Check for contradictions between partial solutions.

    Types of conflicts detected:
    - Logical contradictions
    - Incompatible assumptions
    - Resource conflicts
    - Timing conflicts

    Args:
        state: Level5State with partial_solutions and solution_coverage_map

    Returns:
        Updated state with detected_conflicts list
    """
    partial_solutions = state.get("partial_solutions", {})
    integrated_subproblems = state.get("integrated_subproblems", [])
    subproblem_dependencies = state.get("subproblem_dependencies", {"nodes": [], "edges": []})

    # Create subproblem lookup map
    subproblem_map = {sp["id"]: sp for sp in integrated_subproblems}

    detected_conflicts: List[Dict[str, Any]] = []

    # 1. Check for logical contradictions
    logical_conflicts = detect_logical_contradictions(
        partial_solutions, subproblem_map
    )
    detected_conflicts.extend(logical_conflicts)

    # 2. Check for incompatible assumptions
    assumption_conflicts = detect_incompatible_assumptions(
        partial_solutions, subproblem_map
    )
    detected_conflicts.extend(assumption_conflicts)

    # 3. Check for resource conflicts
    resource_conflicts = detect_resource_conflicts(
        partial_solutions, subproblem_map
    )
    detected_conflicts.extend(resource_conflicts)

    # 4. Check for timing conflicts
    timing_conflicts = detect_timing_conflicts(
        partial_solutions, subproblem_map, subproblem_dependencies
    )
    detected_conflicts.extend(timing_conflicts)

    # 5. Check for dependency conflicts
    dependency_conflicts = detect_dependency_conflicts(
        partial_solutions, subproblem_map, subproblem_dependencies
    )
    detected_conflicts.extend(dependency_conflicts)

    return {
        **state,
        "detected_conflicts": detected_conflicts,
    }


def detect_logical_contradictions(
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Detect logical contradictions between solutions.

    Looks for explicit contradictory statements or opposing conclusions.

    Args:
        partial_solutions: Map of subproblem_id to solution
        subproblem_map: Map of subproblem_id to subproblem

    Returns:
        List of detected logical conflicts
    """
    conflicts = []

    # Keywords that might indicate contradictions
    contradiction_keywords = [
        ("must", "must not"),
        ("should", "should not"),
        ("required", "forbidden"),
        ("always", "never"),
        ("include", "exclude"),
        ("allow", "deny"),
    ]

    solution_list = list(partial_solutions.items())

    for i, (sp_id_a, sol_a) in enumerate(solution_list):
        content_a = sol_a.get("content", "").lower()
        reasoning_a = sol_a.get("reasoning", "").lower()
        text_a = content_a + " " + reasoning_a

        for j, (sp_id_b, sol_b) in enumerate(solution_list[i+1:], start=i+1):
            content_b = sol_b.get("content", "").lower()
            reasoning_b = sol_b.get("reasoning", "").lower()
            text_b = content_b + " " + reasoning_b

            # Check for contradictory keywords
            for positive, negative in contradiction_keywords:
                if positive in text_a and negative in text_b:
                    # Found potential contradiction
                    conflicts.append({
                        "type": "logical_contradiction",
                        "severity": "high",
                        "subproblem_ids": [sp_id_a, sp_id_b],
                        "description": f"Potential contradiction: Solution {sp_id_a} uses '{positive}' while solution {sp_id_b} uses '{negative}'",
                        "keywords": [positive, negative],
                    })
                elif negative in text_a and positive in text_b:
                    conflicts.append({
                        "type": "logical_contradiction",
                        "severity": "high",
                        "subproblem_ids": [sp_id_a, sp_id_b],
                        "description": f"Potential contradiction: Solution {sp_id_a} uses '{negative}' while solution {sp_id_b} uses '{positive}'",
                        "keywords": [negative, positive],
                    })

    return conflicts


def detect_incompatible_assumptions(
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Detect incompatible assumptions between solutions.

    Args:
        partial_solutions: Map of subproblem_id to solution
        subproblem_map: Map of subproblem_id to subproblem

    Returns:
        List of detected assumption conflicts
    """
    conflicts = []

    # Keywords indicating assumptions
    assumption_keywords = ["assume", "assuming", "given that", "provided that", "if"]

    # Extract assumptions from each solution
    assumptions: Dict[str, List[str]] = {}
    for sp_id, solution in partial_solutions.items():
        reasoning = solution.get("reasoning", "").lower()
        solution_assumptions = []
        for keyword in assumption_keywords:
            if keyword in reasoning:
                # Extract sentences containing assumption keywords
                sentences = reasoning.split(".")
                for sentence in sentences:
                    if keyword in sentence:
                        solution_assumptions.append(sentence.strip())
        if solution_assumptions:
            assumptions[sp_id] = solution_assumptions

    # Check for conflicting assumptions (simplified heuristic)
    solution_ids = list(assumptions.keys())
    for i, sp_id_a in enumerate(solution_ids):
        for sp_id_b in solution_ids[i+1:]:
            # If both have assumptions, flag for review
            if assumptions[sp_id_a] and assumptions[sp_id_b]:
                conflicts.append({
                    "type": "incompatible_assumptions",
                    "severity": "medium",
                    "subproblem_ids": [sp_id_a, sp_id_b],
                    "description": f"Solutions {sp_id_a} and {sp_id_b} contain assumptions that should be verified for compatibility",
                    "assumptions": {
                        sp_id_a: assumptions[sp_id_a][:2],  # First 2 assumptions
                        sp_id_b: assumptions[sp_id_b][:2],
                    },
                })

    return conflicts


def detect_resource_conflicts(
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Detect resource conflicts between solutions.

    Args:
        partial_solutions: Map of subproblem_id to solution
        subproblem_map: Map of subproblem_id to subproblem

    Returns:
        List of detected resource conflicts
    """
    conflicts = []

    # Keywords indicating resource usage
    resource_keywords = [
        "database", "api", "port", "memory", "cpu", "storage",
        "file", "directory", "endpoint", "service", "queue"
    ]

    # Extract resource mentions from each solution
    resource_usage: Dict[str, List[str]] = {}
    for sp_id, solution in partial_solutions.items():
        content = solution.get("content", "").lower()
        mentioned_resources = [kw for kw in resource_keywords if kw in content]
        if mentioned_resources:
            resource_usage[sp_id] = mentioned_resources

    # Check for overlapping resource usage
    solution_ids = list(resource_usage.keys())
    for i, sp_id_a in enumerate(solution_ids):
        for sp_id_b in solution_ids[i+1:]:
            shared_resources = set(resource_usage[sp_id_a]) & set(resource_usage[sp_id_b])
            if shared_resources:
                conflicts.append({
                    "type": "resource_conflict",
                    "severity": "medium",
                    "subproblem_ids": [sp_id_a, sp_id_b],
                    "description": f"Solutions {sp_id_a} and {sp_id_b} both reference: {', '.join(shared_resources)}",
                    "shared_resources": list(shared_resources),
                })

    return conflicts


def detect_timing_conflicts(
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any],
    dependency_graph: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Detect timing conflicts between solutions.

    Args:
        partial_solutions: Map of subproblem_id to solution
        subproblem_map: Map of subproblem_id to subproblem
        dependency_graph: Dependency structure

    Returns:
        List of detected timing conflicts
    """
    conflicts = []

    # Keywords indicating temporal requirements
    temporal_keywords = [
        "before", "after", "first", "last", "simultaneously",
        "sequential", "parallel", "concurrent"
    ]

    # Extract temporal requirements
    temporal_requirements: Dict[str, List[str]] = {}
    for sp_id, solution in partial_solutions.items():
        content = solution.get("content", "").lower()
        reasoning = solution.get("reasoning", "").lower()
        text = content + " " + reasoning
        mentioned_temporal = [kw for kw in temporal_keywords if kw in text]
        if mentioned_temporal:
            temporal_requirements[sp_id] = mentioned_temporal

    # Check for conflicting temporal requirements
    solution_ids = list(temporal_requirements.keys())
    for i, sp_id_a in enumerate(solution_ids):
        for sp_id_b in solution_ids[i+1:]:
            req_a = temporal_requirements[sp_id_a]
            req_b = temporal_requirements[sp_id_b]

            # Check for explicit conflicts
            if ("before" in req_a and "after" in req_b) or ("after" in req_a and "before" in req_b):
                conflicts.append({
                    "type": "timing_conflict",
                    "severity": "high",
                    "subproblem_ids": [sp_id_a, sp_id_b],
                    "description": f"Solutions {sp_id_a} and {sp_id_b} have conflicting temporal requirements",
                    "requirements": {sp_id_a: req_a, sp_id_b: req_b},
                })

    return conflicts


def detect_dependency_conflicts(
    partial_solutions: Dict[str, Solution],
    subproblem_map: Dict[str, Any],
    dependency_graph: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Detect conflicts where dependencies are not satisfied.

    Args:
        partial_solutions: Map of subproblem_id to solution
        subproblem_map: Map of subproblem_id to subproblem
        dependency_graph: Dependency structure

    Returns:
        List of detected dependency conflicts
    """
    conflicts = []

    # Check each solution's dependencies
    for sp_id, solution in partial_solutions.items():
        subproblem = subproblem_map.get(sp_id)
        if not subproblem:
            continue

        dependencies = subproblem.get("dependencies", [])
        unsolved_dependencies = [dep for dep in dependencies if dep not in partial_solutions]

        if unsolved_dependencies:
            conflicts.append({
                "type": "dependency_conflict",
                "severity": "high",
                "subproblem_ids": [sp_id] + unsolved_dependencies,
                "description": f"Solution {sp_id} depends on unsolved subproblems: {', '.join(unsolved_dependencies)}",
                "unsolved_dependencies": unsolved_dependencies,
            })

    return conflicts
