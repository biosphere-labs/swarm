"""
Utility functions for Level 2 Technique Selection.

Provides helper functions for generating formal justifications and
formatting technique information.
"""

from typing import Any

from decomposition_pipeline.catalog.models import Technique


def generate_justification(
    technique: Technique,
    score: float,
    problem_characteristics: dict[str, Any],
    original_problem: str,
) -> str:
    """
    Generate formal justification for technique selection.

    Creates a structured justification that includes:
    - Why this technique was chosen (score and matching rules)
    - Which problem characteristics matched
    - Formal definition and complexity
    - Literature references
    - Implementation strategy

    Args:
        technique: The selected Technique
        score: The computed applicability score
        problem_characteristics: Dict of problem characteristics
        original_problem: Original problem description

    Returns:
        Formatted justification string with formal reasoning
    """
    justification_parts = [
        f"# Technique Selection: {technique.name}",
        "",
        f"## Applicability Score: {score:.2f}",
        "",
        "## Formal Definition",
        f"{technique.formal_definition}",
        "",
        "## Complexity",
        f"{technique.complexity}",
        "",
        "## Why This Technique Was Selected",
        "",
    ]

    # Add matching rules
    matching_rules = []
    for rule in technique.applicability_rules:
        matched, rule_score = rule.evaluate(problem_characteristics)
        if matched:
            matching_rules.append(
                f"- **{rule.description}** (score: {rule_score:.2f})"
            )
            matching_rules.append(f"  - Condition: `{rule.condition}`")

    if matching_rules:
        justification_parts.append("### Matching Applicability Rules")
        justification_parts.extend(matching_rules)
        justification_parts.append("")

    # Add prerequisites
    justification_parts.extend(
        [
            "## Prerequisites Met",
            "",
        ]
    )

    for prereq in technique.prerequisites:
        status = "✓" if problem_characteristics.get(prereq, False) else "✗"
        justification_parts.append(f"- {status} {prereq}")

    justification_parts.append("")

    # Add implementation strategy
    justification_parts.extend(
        [
            "## Implementation Strategy",
            f"{technique.implementation_strategy}",
            "",
        ]
    )

    # Add literature references
    if technique.literature_references:
        justification_parts.extend(
            [
                "## Literature References",
                "",
            ]
        )
        for ref in technique.literature_references:
            justification_parts.append(f"- {ref}")
        justification_parts.append("")

    # Add problem-specific reasoning
    justification_parts.extend(
        [
            "## Application to Current Problem",
            "",
            f"Given the problem: *{original_problem[:200]}{'...' if len(original_problem) > 200 else ''}*",
            "",
            f"This technique from the {technique.paradigm} paradigm is well-suited because:",
        ]
    )

    # Generate specific reasoning based on characteristics
    reasoning_points = _generate_problem_specific_reasoning(
        technique, problem_characteristics
    )
    for point in reasoning_points:
        justification_parts.append(f"- {point}")

    return "\n".join(justification_parts)


def _generate_problem_specific_reasoning(
    technique: Technique,
    characteristics: dict[str, Any],
) -> list[str]:
    """
    Generate problem-specific reasoning points.

    Args:
        technique: The selected technique
        characteristics: Problem characteristics

    Returns:
        List of reasoning points specific to the problem
    """
    reasoning = []

    # Check for size-related characteristics
    problem_size = characteristics.get("problem_size", "unknown")
    if problem_size != "unknown":
        reasoning.append(
            f"The problem size ({problem_size}) aligns with the technique's complexity characteristics"
        )

    # Check for structure-related characteristics
    structural_traits = [
        "has_recursive_structure",
        "has_network_structure",
        "has_hierarchical_structure",
        "tree_like_relationships",
    ]
    for trait in structural_traits:
        if characteristics.get(trait, False):
            trait_name = trait.replace("_", " ").replace("has ", "")
            reasoning.append(f"The problem exhibits {trait_name}, which this technique explicitly handles")

    # Check for parallelization characteristics
    parallel_traits = [
        "operations_parallelizable",
        "embarrassingly_parallel",
        "tasks_independent",
    ]
    for trait in parallel_traits:
        if characteristics.get(trait, False):
            reasoning.append(
                "The problem allows for parallel decomposition, maximizing the technique's efficiency"
            )
            break

    # Check for real-time/temporal characteristics
    temporal_traits = [
        "real_time_processing",
        "continuous_data_flow",
        "sequential_stages_identifiable",
    ]
    for trait in temporal_traits:
        if characteristics.get(trait, False):
            reasoning.append(
                "Temporal characteristics align with the technique's event/time-based approach"
            )
            break

    # Check for data characteristics
    if characteristics.get("large_dataset", False):
        reasoning.append(
            "The large dataset justifies the overhead of applying this decomposition technique"
        )

    # If no specific reasoning generated, add generic statement
    if not reasoning:
        reasoning.append(
            "The technique's formal properties match the problem's structural requirements"
        )

    # Add complexity justification
    reasoning.append(
        f"The technique's {technique.complexity} complexity is appropriate for this problem's scale"
    )

    return reasoning


def format_technique_summary(technique: Technique, score: float) -> str:
    """
    Format a brief summary of a technique.

    Args:
        technique: The technique to summarize
        score: The applicability score

    Returns:
        Brief formatted summary
    """
    return (
        f"{technique.name} (Score: {score:.2f})\n"
        f"  {technique.formal_definition}\n"
        f"  Complexity: {technique.complexity}"
    )
