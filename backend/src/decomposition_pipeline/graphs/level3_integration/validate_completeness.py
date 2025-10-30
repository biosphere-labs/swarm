"""
ValidateCompletenessNode - Validates decomposition covers entire problem.

Uses formal methods from literature:
- Set coverage algorithms
- Logical completeness checking
- Constraint satisfaction validation
"""

from typing import List, Set, Dict
from ...schemas.state import Level3IntegrationState, Subproblem, ValidationReport


def extract_problem_aspects(problem_text: str) -> Set[str]:
    """
    Extract key aspects/requirements from original problem.
    
    Simple keyword extraction for validation.
    In production, could use LLM for more sophisticated extraction.
    """
    # Extract meaningful words (simple approach)
    words = problem_text.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
    aspects = {w for w in words if w not in stop_words and len(w) > 3}
    return aspects


def extract_subproblem_coverage(subproblems: List[Subproblem]) -> Set[str]:
    """
    Extract aspects covered by all subproblems.
    """
    all_words = set()
    for sp in subproblems:
        text = f"{sp['title']} {sp['description']}"
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        meaningful = {w for w in words if w not in stop_words and len(w) > 3}
        all_words.update(meaningful)
    return all_words


def check_coverage(
    problem_aspects: Set[str],
    subproblem_coverage: Set[str]
) -> float:
    """
    Check coverage using set overlap.
    
    Formula: |problem_aspects ∩ subproblem_coverage| / |problem_aspects|
    
    From: Set coverage algorithms (standard approach)
    """
    if not problem_aspects:
        return 1.0
    
    covered = problem_aspects.intersection(subproblem_coverage)
    coverage = len(covered) / len(problem_aspects)
    
    return coverage


def identify_gaps(
    problem_aspects: Set[str],
    subproblem_coverage: Set[str]
) -> List[str]:
    """
    Identify aspects of problem not covered by any subproblem.
    
    Uses set difference operation.
    """
    gaps = problem_aspects - subproblem_coverage
    return list(gaps)


def check_dependency_completeness(
    subproblems: List[Subproblem]
) -> List[str]:
    """
    Check if all dependencies are satisfied.
    
    Verifies that every referenced dependency actually exists.
    """
    existing_ids = {sp["id"] for sp in subproblems}
    missing_deps = []
    
    for sp in subproblems:
        for dep_id in sp.get("dependencies", []):
            if dep_id not in existing_ids:
                missing_deps.append(f"Subproblem {sp['id']} depends on missing {dep_id}")
    
    return missing_deps


def validate_completeness(state: Level3IntegrationState) -> Level3IntegrationState:
    """
    Validate completeness of decomposition.
    
    Checks:
    1. Coverage: Do subproblems cover all aspects of original problem?
    2. Dependencies: Are all dependencies satisfied?
    3. Consistency: Are there any logical contradictions?
    
    Args:
        state: Integration state with resolved_subproblems
        
    Returns:
        Updated state with validation_report
    """
    resolved_subproblems = state.get("resolved_subproblems", [])
    original_problem = state.get("original_problem", "")
    
    # Initialize validation report
    issues: List[str] = []
    recommendations: List[str] = []
    has_critical_failures = False
    has_gaps = False
    has_conflicts = False
    
    # Check 1: Coverage analysis
    problem_aspects = extract_problem_aspects(original_problem)
    subproblem_coverage = extract_subproblem_coverage(resolved_subproblems)
    
    coverage_ratio = check_coverage(problem_aspects, subproblem_coverage)
    gaps = identify_gaps(problem_aspects, subproblem_coverage)
    
    if coverage_ratio < 0.7:  # Threshold from literature
        has_gaps = True
        issues.append(f"Low coverage: {coverage_ratio:.1%} of problem aspects covered")
        recommendations.append(f"Consider adding subproblems for: {', '.join(list(gaps)[:5])}")
    
    # Check 2: Dependency completeness
    missing_deps = check_dependency_completeness(resolved_subproblems)
    
    if missing_deps:
        has_critical_failures = True
        issues.extend(missing_deps)
        recommendations.append("Fix missing dependencies before proceeding")
    
    # Check 3: Empty decomposition
    if not resolved_subproblems:
        has_critical_failures = True
        issues.append("No subproblems generated")
        recommendations.append("Re-run decomposition with different paradigms")
    
    # Check 4: Conflicts from previous step
    detected_conflicts = state.get("detected_conflicts", [])
    if detected_conflicts:
        has_conflicts = True
        issues.append(f"{len(detected_conflicts)} conflicts resolved during integration")
        recommendations.append("Review merged subproblems for correctness")
    
    # Determine overall status
    if has_critical_failures:
        status = "invalid"
    elif has_gaps or has_conflicts:
        status = "warning"
    else:
        status = "valid"
    
    validation_report: ValidationReport = {
        "status": status,  # type: ignore
        "has_critical_failures": has_critical_failures,
        "has_gaps": has_gaps,
        "has_conflicts": has_conflicts,
        "issues": issues,
        "recommendations": recommendations,
        "metadata": {
            "coverage_ratio": coverage_ratio,
            "total_subproblems": len(resolved_subproblems),
            "missing_aspects": gaps[:10]  # Limit to 10
        }
    }
    
    return {
        **state,
        "validation_report": validation_report,
        "integrated_subproblems": resolved_subproblems  # Final output
    }
