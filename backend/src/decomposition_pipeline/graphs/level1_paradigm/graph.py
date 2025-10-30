"""
Level 1: Paradigm Selection StateGraph.

This graph analyzes a problem and selects the most applicable decomposition
paradigm(s) from the 8 available options.

Graph Flow:
    START -> characterize_problem -> score_paradigms -> check_scores
           -> (if max_score >= 0.3) select_paradigms -> END
           -> (if max_score < 0.3) request_more_context -> END
"""

import logging
from typing import Literal

from langgraph.graph import END, StateGraph

from decomposition_pipeline.schemas import Level1State

from .nodes import (
    characterize_problem,
    request_more_context,
    score_paradigms,
    select_paradigms,
)

logger = logging.getLogger(__name__)


def should_request_more_context(state: Level1State) -> Literal["select", "request_context"]:
    """
    Conditional routing function to determine if we should request more context.

    If all paradigm scores are < 0.3, we need more context.
    Otherwise, proceed to selection.

    Args:
        state: Level1State with paradigm_scores

    Returns:
        "request_context" if max score < 0.3, "select" otherwise
    """
    paradigm_scores = state.get("paradigm_scores", {})

    if not paradigm_scores:
        logger.warning("No paradigm scores available")
        return "request_context"

    max_score = max(paradigm_scores.values())

    if max_score < 0.3:
        logger.warning(f"Max paradigm score ({max_score:.2f}) below threshold, requesting context")
        return "request_context"

    logger.info(f"Max paradigm score ({max_score:.2f}) sufficient, proceeding to selection")
    return "select"


def create_level1_paradigm_graph() -> StateGraph:
    """
    Create and compile the Level 1 Paradigm Selection graph.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph
    graph = StateGraph(Level1State)

    # Add nodes
    graph.add_node("characterize_problem", characterize_problem)
    graph.add_node("score_paradigms", score_paradigms)
    graph.add_node("select_paradigms", select_paradigms)
    graph.add_node("request_more_context", request_more_context)

    # Define edges
    graph.set_entry_point("characterize_problem")

    # Linear flow from characterize to score
    graph.add_edge("characterize_problem", "score_paradigms")

    # Conditional routing after scoring
    graph.add_conditional_edges(
        "score_paradigms",
        should_request_more_context,
        {
            "select": "select_paradigms",
            "request_context": "request_more_context",
        },
    )

    # Both selection and context request end the graph
    graph.add_edge("select_paradigms", END)
    graph.add_edge("request_more_context", END)

    # Compile and return
    logger.info("Level 1 Paradigm Selection graph created successfully")
    return graph.compile()


# Create the compiled graph instance
level1_paradigm_graph = create_level1_paradigm_graph()
