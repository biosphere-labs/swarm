"""
Solution Validation Node for Level 5.

Validates the integrated solution for logical consistency and completeness.
"""

from typing import Dict, Any, List
from ...schemas.state import Level5State, ValidationReport


def validate_integrated_solution(state: Level5State) -> Level5State:
    """
    Validate logical consistency of integrated solution.

    Checks:
    1. Logical consistency
    2. Whether solution actually solves original problem
    3. Completeness of coverage
    4. Quality metrics

    Args:
        state: Level5State with integrated_solution

    Returns:
        Updated state with validation_results
    """
    integrated_solution = state.get("integrated_solution")
    original_problem = state.get("original_problem", "")
    solution_coverage_map = state.get("solution_coverage_map", {})
    detected_conflicts = state.get("detected_conflicts", [])
    resolution_summary = state.get("resolution_summary", {})
    gap_metrics = state.get("gap_metrics", {})

    # Initialize validation report
    issues: List[str] = []
    recommendations: List[str] = []
    has_critical_failures = False
    has_gaps = False
    has_conflicts = False

    # 1. Check if integrated solution exists
    if not integrated_solution:
        issues.append("No integrated solution was generated")
        has_critical_failures = True
    else:
        # Validate solution content
        content = integrated_solution.get("content", "")
        if len(content) < 100:
            issues.append("Integrated solution is too short (< 100 characters)")
            has_critical_failures = True

        confidence = integrated_solution.get("confidence", 0.0)
        if confidence < 0.5:
            issues.append(f"Overall confidence is low ({confidence:.2f})")
            recommendations.append("Review and improve low-confidence components")

    # 2. Check coverage
    coverage_pct = solution_coverage_map.get("coverage_percentage", 0)
    if coverage_pct < 80:
        issues.append(f"Low solution coverage: {coverage_pct:.1f}%")
        has_gaps = True
        recommendations.append("Address unsolved subproblems to improve coverage")
    elif coverage_pct < 100:
        recommendations.append(f"Coverage at {coverage_pct:.1f}%, consider addressing remaining gaps")

    # 3. Check for unresolved conflicts
    unresolved_conflicts = resolution_summary.get("escalated", 0)
    if unresolved_conflicts > 0:
        issues.append(f"{unresolved_conflicts} conflicts require manual resolution")
        has_conflicts = True
        recommendations.append("Review and resolve escalated conflicts")

    # 4. Check for critical gaps
    critical_gaps = gap_metrics.get("critical_gaps", [])
    if len(critical_gaps) > 0:
        issues.append(f"{len(critical_gaps)} critical gaps identified")
        has_gaps = True

    # 5. Validate problem alignment
    if integrated_solution and original_problem:
        alignment_check = validate_problem_alignment(
            integrated_solution, original_problem
        )
        if not alignment_check["is_aligned"]:
            issues.extend(alignment_check["issues"])
            recommendations.extend(alignment_check["recommendations"])

    # 6. Check logical consistency
    if integrated_solution:
        consistency_check = validate_logical_consistency(
            integrated_solution, state
        )
        if not consistency_check["is_consistent"]:
            issues.extend(consistency_check["issues"])
            recommendations.extend(consistency_check["recommendations"])

    # 7. Check completeness
    completeness_check = validate_completeness(
        solution_coverage_map, gap_metrics
    )
    if not completeness_check["is_complete"]:
        issues.extend(completeness_check["issues"])
        recommendations.extend(completeness_check["recommendations"])
        has_gaps = True

    # Determine overall status
    if has_critical_failures:
        status = "invalid"
    elif has_conflicts or (has_gaps and coverage_pct < 70):
        status = "warning"
    else:
        status = "valid"

    # Create validation report
    validation_report: ValidationReport = {
        "status": status,
        "has_critical_failures": has_critical_failures,
        "has_gaps": has_gaps,
        "has_conflicts": has_conflicts,
        "issues": issues,
        "recommendations": recommendations,
        "metadata": {
            "coverage_percentage": coverage_pct,
            "confidence": integrated_solution.get("confidence", 0.0) if integrated_solution else 0.0,
            "unresolved_conflicts": unresolved_conflicts,
            "critical_gaps": len(critical_gaps),
            "total_issues": len(issues),
        }
    }

    return {
        **state,
        "validation_results": validation_report,
    }


def validate_problem_alignment(
    integrated_solution: Dict[str, Any],
    original_problem: str
) -> Dict[str, Any]:
    """
    Validate that solution addresses the original problem.

    Args:
        integrated_solution: The integrated solution
        original_problem: Original problem statement

    Returns:
        Alignment validation result
    """
    issues = []
    recommendations = []

    content = integrated_solution.get("content", "").lower()
    problem_lower = original_problem.lower()

    # Extract key terms from problem
    problem_words = set(word for word in problem_lower.split() if len(word) > 4)

    # Check if key terms appear in solution
    content_words = set(word for word in content.split() if len(word) > 4)

    overlap = problem_words & content_words
    overlap_ratio = len(overlap) / len(problem_words) if problem_words else 0

    is_aligned = overlap_ratio > 0.3

    if overlap_ratio < 0.2:
        issues.append("Solution may not address the original problem (low term overlap)")
        recommendations.append("Verify that solution actually solves the stated problem")
    elif overlap_ratio < 0.4:
        recommendations.append("Consider adding more explicit references to problem requirements")

    return {
        "is_aligned": is_aligned,
        "overlap_ratio": overlap_ratio,
        "issues": issues,
        "recommendations": recommendations,
    }


def validate_logical_consistency(
    integrated_solution: Dict[str, Any],
    state: Level5State
) -> Dict[str, Any]:
    """
    Validate logical consistency of the solution.

    Args:
        integrated_solution: The integrated solution
        state: Full Level5 state

    Returns:
        Consistency validation result
    """
    issues = []
    recommendations = []

    # Check for contradictory terms in the integrated solution itself
    content = integrated_solution.get("content", "").lower()

    contradiction_pairs = [
        ("must", "must not"),
        ("always", "never"),
        ("required", "optional"),
        ("include", "exclude"),
    ]

    found_contradictions = []
    for pos, neg in contradiction_pairs:
        if pos in content and neg in content:
            found_contradictions.append((pos, neg))

    if found_contradictions:
        issues.append(f"Potential contradictions found: {', '.join(f'{p}/{n}' for p, n in found_contradictions)}")
        recommendations.append("Review solution for internal contradictions")

    is_consistent = len(found_contradictions) == 0

    return {
        "is_consistent": is_consistent,
        "issues": issues,
        "recommendations": recommendations,
    }


def validate_completeness(
    coverage_map: Dict[str, Any],
    gap_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate completeness of the solution.

    Args:
        coverage_map: Solution coverage information
        gap_metrics: Gap analysis metrics

    Returns:
        Completeness validation result
    """
    issues = []
    recommendations = []

    coverage_pct = coverage_map.get("coverage_percentage", 0)
    total_gaps = gap_metrics.get("total_gaps", 0)
    critical_gaps = gap_metrics.get("critical_gaps", [])

    # Completeness criteria
    is_complete = coverage_pct >= 90 and len(critical_gaps) == 0

    if coverage_pct < 70:
        issues.append(f"Low coverage: Only {coverage_pct:.1f}% of subproblems addressed")
    elif coverage_pct < 90:
        recommendations.append(f"Good coverage ({coverage_pct:.1f}%), consider filling remaining gaps")

    if len(critical_gaps) > 0:
        issues.append(f"{len(critical_gaps)} critical gaps remain")
        recommendations.append("Address critical gaps before finalizing solution")

    if total_gaps > 10:
        recommendations.append(f"{total_gaps} total gaps identified, prioritize the most important ones")

    return {
        "is_complete": is_complete,
        "issues": issues,
        "recommendations": recommendations,
    }
