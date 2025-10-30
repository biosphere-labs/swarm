"""
Node implementations for Level 2 Technique Selection Subgraph.

All technique selection uses rule-based methods from the catalog - no machine
learning or pattern discovery is used.
"""

from typing import Any

from decomposition_pipeline.catalog.models import Technique
from decomposition_pipeline.catalog.techniques import get_default_catalog
from decomposition_pipeline.graphs.level2_technique.utils import (
    generate_justification,
)
from decomposition_pipeline.schemas.state import Level2State


def retrieve_techniques(state: Level2State) -> Level2State:
    """
    Retrieve applicable techniques from catalog for each selected paradigm.

    For each paradigm in selected_paradigms:
    1. Query the technique catalog
    2. Filter techniques by prerequisites
    3. Return only techniques that meet problem requirements

    Args:
        state: Level2State containing problem characteristics and selected paradigms

    Returns:
        Updated state with candidate_techniques populated
    """
    catalog = get_default_catalog()
    problem_characteristics = state["problem_characteristics"]
    selected_paradigms = state["selected_paradigms"]

    candidate_techniques: dict[str, list[Technique]] = {}

    for paradigm in selected_paradigms:
        # Get all applicable techniques (already filtered by prerequisites)
        applicable = catalog.get_applicable_techniques(
            paradigm, problem_characteristics
        )

        # Convert to list of Technique objects (without scores for now)
        candidate_techniques[paradigm] = [tech for tech, _ in applicable]

    return {
        **state,
        "candidate_techniques": candidate_techniques,
    }


def score_techniques(state: Level2State) -> Level2State:
    """
    Score each candidate technique against problem characteristics.

    Uses rule-based scoring from the technique catalog:
    - Evaluates applicability rules for each technique
    - Computes weighted scores based on rule evaluation
    - Ranks techniques by score

    Args:
        state: Level2State with candidate_techniques populated

    Returns:
        Updated state with technique_scores populated
    """
    problem_characteristics = state["problem_characteristics"]
    candidate_techniques = state.get("candidate_techniques", {})

    technique_scores: dict[str, float] = {}

    for paradigm, techniques in candidate_techniques.items():
        for technique in techniques:
            # Generate unique key for this technique
            key = f"{paradigm}:{technique.name}"

            # Score using catalog's scoring method
            score = technique.score_applicability(problem_characteristics)
            technique_scores[key] = score

    return {
        **state,
        "technique_scores": technique_scores,
    }


def select_techniques(state: Level2State) -> Level2State:
    """
    Select the best technique for each paradigm.

    Selection process:
    1. For each paradigm, get the highest scoring technique
    2. Validate that prerequisites are met (should already be checked)
    3. Generate formal justification citing literature
    4. Return selected techniques with justifications

    Args:
        state: Level2State with candidate_techniques and technique_scores

    Returns:
        Updated state with selected_techniques and technique_justification
    """
    candidate_techniques = state.get("candidate_techniques", {})
    technique_scores = state.get("technique_scores", {})
    problem_characteristics = state["problem_characteristics"]
    original_problem = state["original_problem"]

    selected_techniques: dict[str, dict[str, Any]] = {}
    technique_justification: dict[str, str] = {}

    for paradigm, techniques in candidate_techniques.items():
        if not techniques:
            # No applicable techniques for this paradigm
            continue

        # Find best technique by score
        best_technique = None
        best_score = -1.0

        for technique in techniques:
            key = f"{paradigm}:{technique.name}"
            score = technique_scores.get(key, 0.0)

            if score > best_score:
                best_score = score
                best_technique = technique

        if best_technique is not None:
            # Convert Technique to dict for state storage
            technique_dict = {
                "name": best_technique.name,
                "paradigm": best_technique.paradigm,
                "formal_definition": best_technique.formal_definition,
                "prerequisites": best_technique.prerequisites,
                "complexity": best_technique.complexity,
                "applicability_rules": [
                    {
                        "condition": rule.condition,
                        "score": rule.score,
                        "description": rule.description,
                    }
                    for rule in best_technique.applicability_rules
                ],
                "literature_references": best_technique.literature_references,
                "implementation_strategy": best_technique.implementation_strategy,
                "score": best_score,
            }

            selected_techniques[paradigm] = technique_dict

            # Generate justification
            justification = generate_justification(
                technique=best_technique,
                score=best_score,
                problem_characteristics=problem_characteristics,
                original_problem=original_problem,
            )
            technique_justification[paradigm] = justification

    return {
        **state,
        "selected_techniques": selected_techniques,
        "technique_justification": technique_justification,
    }
