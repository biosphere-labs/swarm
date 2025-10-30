"""
Solution collection for Level 4.

Implements SolutionCollectionNode from brainstorm_1.md lines 489-494.
Gathers completed solutions and validates completeness.
"""

from typing import Dict, List
from ...schemas.state import Level4State, Solution, ValidationReport


def collect_and_validate_solutions(state: Level4State) -> Level4State:
    """
    Node function: Collect all partial solutions and validate completeness.

    Implements SolutionCollectionNode from brainstorm_1.md lines 489-494:
    - Gathers all partial solutions
    - Validates completeness (all subproblems solved)
    - Flags any failures for retry or escalation

    Args:
        state: Level4State with partial_solutions

    Returns:
        Updated state with validation results
    """
    integrated_subproblems = state.get("integrated_subproblems", [])
    partial_solutions = state.get("partial_solutions", {})
    failed_subproblems = state.get("failed_subproblems", [])

    # Validate completeness
    validation_report = validate_solution_completeness(
        integrated_subproblems,
        partial_solutions,
        failed_subproblems
    )

    # Identify solutions needing retry
    needs_retry = identify_retry_candidates(
        failed_subproblems,
        validation_report
    )

    return {
        **state,
        "validation_results": validation_report,
        "needs_retry": needs_retry,
    }


def validate_solution_completeness(
    subproblems: List[Dict],
    solutions: Dict[str, Solution],
    failed: List[str]
) -> ValidationReport:
    """
    Validate that all subproblems have been addressed.

    Args:
        subproblems: List of all subproblems
        solutions: Dictionary of solutions by subproblem ID
        failed: List of failed subproblem IDs

    Returns:
        ValidationReport with completeness assessment
    """
    total_subproblems = len(subproblems)
    solved_count = len(solutions)
    failed_count = len(failed)
    missing_count = total_subproblems - solved_count - failed_count

    # Check for critical failures
    has_critical_failures = failed_count > (total_subproblems * 0.2)  # >20% failed

    # Check for gaps (missing solutions)
    has_gaps = missing_count > 0

    # Check for conflicts (shouldn't happen at this stage, but verify)
    has_conflicts = False

    # Collect issues
    issues = []
    if missing_count > 0:
        issues.append(f"{missing_count} subproblems have no solution or failure record")

    if failed_count > 0:
        issues.append(f"{failed_count} subproblems failed to solve")

    if has_critical_failures:
        issues.append(f"Critical: >20% failure rate ({failed_count}/{total_subproblems})")

    # Collect recommendations
    recommendations = []
    if failed_count > 0:
        recommendations.append("Retry failed subproblems with different pools or larger models")

    if missing_count > 0:
        recommendations.append("Investigate missing subproblems and add to execution queue")

    if solved_count == total_subproblems:
        recommendations.append("All subproblems solved - ready for Level 5 integration")

    # Determine overall status
    if has_critical_failures:
        status = "invalid"
    elif has_gaps or failed_count > 0:
        status = "warning"
    else:
        status = "valid"

    validation_report: ValidationReport = {
        "status": status,
        "has_critical_failures": has_critical_failures,
        "has_gaps": has_gaps,
        "has_conflicts": has_conflicts,
        "issues": issues,
        "recommendations": recommendations,
        "metadata": {
            "total_subproblems": total_subproblems,
            "solved": solved_count,
            "failed": failed_count,
            "missing": missing_count,
            "success_rate": round(solved_count / total_subproblems * 100, 2) if total_subproblems > 0 else 0,
        }
    }

    return validation_report


def identify_retry_candidates(
    failed_subproblems: List[str],
    validation_report: ValidationReport
) -> List[Dict[str, str]]:
    """
    Identify which failed subproblems should be retried.

    Retry strategy:
    - Retry all failures if < 5 failures
    - Retry only non-critical failures if 5-10 failures
    - Escalate to human if > 10 failures

    Args:
        failed_subproblems: List of failed subproblem IDs
        validation_report: Validation results

    Returns:
        List of retry candidates with strategy
    """
    failed_count = len(failed_subproblems)

    if failed_count == 0:
        return []

    retry_candidates = []

    if failed_count <= 5:
        # Retry all with alternate pool
        for sp_id in failed_subproblems:
            retry_candidates.append({
                "subproblem_id": sp_id,
                "retry_strategy": "alternate_pool",
                "reason": "Initial attempt failed, trying different pool",
            })

    elif failed_count <= 10:
        # Retry with larger model
        for sp_id in failed_subproblems:
            retry_candidates.append({
                "subproblem_id": sp_id,
                "retry_strategy": "larger_model",
                "reason": "Multiple failures, escalating to GPT-4o",
            })

    else:
        # Too many failures - escalate to human
        for sp_id in failed_subproblems:
            retry_candidates.append({
                "subproblem_id": sp_id,
                "retry_strategy": "human_review",
                "reason": "Critical: Too many failures, requires human intervention",
            })

    return retry_candidates
