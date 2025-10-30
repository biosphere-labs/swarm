"""
Level 2 Technique Selection Subgraph.

This subgraph implements the technique selection workflow:
1. Retrieve applicable techniques from catalog for each paradigm
2. Score techniques using rule-based criteria
3. Select best technique per paradigm with formal justification

All selection is based on pre-defined algorithmic techniques from computer
science literature - no machine learning is used.
"""

from langgraph.graph import StateGraph, END

from decomposition_pipeline.graphs.level2_technique.nodes import (
    retrieve_techniques,
    score_techniques,
    select_techniques,
)
from decomposition_pipeline.schemas.state import Level2State


def create_level2_graph() -> StateGraph:
    """
    Create the Level 2 Technique Selection subgraph.

    Graph structure:
        START → retrieve_techniques → score_techniques → select_techniques → END

    This is a linear workflow with no conditional branching.
    Each node transforms the state sequentially.

    Returns:
        Compiled StateGraph for Level 2 technique selection
    """
    # Initialize graph with Level2State schema
    graph = StateGraph(Level2State)

    # Add nodes
    graph.add_node("retrieve_techniques", retrieve_techniques)
    graph.add_node("score_techniques", score_techniques)
    graph.add_node("select_techniques", select_techniques)

    # Define linear flow
    graph.set_entry_point("retrieve_techniques")
    graph.add_edge("retrieve_techniques", "score_techniques")
    graph.add_edge("score_techniques", "select_techniques")
    graph.add_edge("select_techniques", END)

    # Compile and return
    return graph.compile()
