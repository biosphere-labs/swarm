"""
Hierarchical Decomposition Subgraph (Level 3.1.5)

Applies hierarchical decomposition techniques like Multi-tier Architecture,
Pyramid Decomposition, or Recursive Hierarchies to break problems into layers.
"""

from typing import Any, Dict, List
from langgraph.graph import StateGraph, END
from decomposition_pipeline.schemas import HierarchicalState, Subproblem, SubproblemStatus
import uuid


def identify_levels(state: HierarchicalState) -> Dict[str, Any]:
    """
    Identify hierarchy levels in the problem.

    Discovers layers or tiers of abstraction.
    """
    problem = state["original_problem"]

    # Standard three-tier hierarchy
    levels = [
        {"id": "level_1", "name": "Presentation Layer", "depth": 1, "abstraction": "high"},
        {"id": "level_2", "name": "Business Logic Layer", "depth": 2, "abstraction": "medium"},
        {"id": "level_3", "name": "Data Access Layer", "depth": 3, "abstraction": "low"},
    ]

    return {"identified_levels": levels}


def extract_abstractions(state: HierarchicalState) -> Dict[str, Any]:
    """
    Create abstraction layers for each level.

    Defines what each layer abstracts and provides.
    """
    levels = state.get("identified_levels", [])

    abstractions = [
        {
            "level_id": level["id"],
            "provides": f"Abstraction for {level['name']}",
            "hides": "Implementation details",
            "interfaces": [f"{level['name']}_interface"]
        }
        for level in levels
    ]

    return {"abstraction_layers": abstractions}


def define_relationships(state: HierarchicalState) -> Dict[str, Any]:
    """
    Establish level relationships and dependencies.

    Defines how layers connect in the hierarchy.
    """
    levels = state.get("identified_levels", [])

    # Hierarchical dependencies (top-down)
    relationships = []
    for i in range(len(levels) - 1):
        relationships.append({
            "from": levels[i]["id"],
            "to": levels[i + 1]["id"],
            "type": "depends_on",
            "direction": "downward"
        })

    return {"level_relationships": relationships}


def create_subproblems(state: HierarchicalState) -> Dict[str, Any]:
    """
    Generate subproblems from hierarchy levels.

    Converts each level into a subproblem.
    """
    problem = state["original_problem"]
    levels = state.get("identified_levels", [])
    technique = state["selected_technique"]

    subproblems: List[Subproblem] = []

    # Process from bottom-up (lower levels first)
    for i, level in enumerate(reversed(levels)):
        subproblem_id = f"hierarchical_{i+1}_{str(uuid.uuid4())[:8]}"

        # Higher levels depend on lower levels
        dependencies = []
        if i > 0:
            dependencies.append(f"hierarchical_{i}_{str(uuid.uuid4())[:8]}")

        subproblem: Subproblem = {
            "id": subproblem_id,
            "title": f"Implement {level['name']}",
            "description": (
                f"Implement the {level['name']} (depth: {level['depth']}, "
                f"abstraction: {level['abstraction']}). "
                f"This layer provides well-defined interfaces and maintains "
                f"separation from other layers using {technique['name']}."
            ),
            "paradigm": "hierarchical",
            "source_technique": technique["name"],
            "status": SubproblemStatus.PENDING,
            "dependencies": dependencies,
            "estimated_complexity": "medium",
            "confidence": 0.89,
            "metadata": {
                "level_id": level["id"],
                "depth": level["depth"],
                "abstraction": level["abstraction"]
            }
        }
        subproblems.append(subproblem)

    return {"subproblems": subproblems}


def create_hierarchical_decomposition_graph() -> StateGraph:
    """
    Create the hierarchical decomposition subgraph.

    Returns:
        StateGraph configured for hierarchical decomposition
    """
    graph = StateGraph(HierarchicalState)

    graph.add_node("identify_levels", identify_levels)
    graph.add_node("extract_abstractions", extract_abstractions)
    graph.add_node("define_relationships", define_relationships)
    graph.add_node("create_subproblems", create_subproblems)

    graph.set_entry_point("identify_levels")
    graph.add_edge("identify_levels", "extract_abstractions")
    graph.add_edge("extract_abstractions", "define_relationships")
    graph.add_edge("define_relationships", "create_subproblems")
    graph.add_edge("create_subproblems", END)

    return graph.compile()
