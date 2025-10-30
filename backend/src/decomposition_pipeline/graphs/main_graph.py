"""
Main Orchestration Graph for the Decomposition Pipeline.

This is the top-level graph that connects all 5 levels with conditional routing,
HITL approval gates, error handling, and checkpointing.

Architecture based on brainstorm_1.md lines 52-106.

Graph Structure:
    START
    └─> problem_ingestion
        └─> level1_paradigm_subgraph
            └─> gate1_paradigm_approval (optional)
                └─> handle_gate1_response
                    └─> level2_technique_subgraph
                        └─> gate2_technique_approval (optional)
                            └─> handle_gate2_response
                                └─> level3_decomposition (parallel paradigm subgraphs)
                                    └─> level3_integration
                                        └─> gate3_decomposition_approval (optional)
                                            └─> handle_gate3_response
                                                └─> level4_solution_generation
                                                    └─> level5_solution_integration
                                                        └─> gate4_final_approval (required)
                                                            └─> handle_gate4_response
                                                                └─> output_formatting
                                                                    └─> END
"""

import logging
from typing import Dict, Any, Literal
from datetime import datetime
import uuid

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

from decomposition_pipeline.schemas import MainPipelineState, PipelineStage
from decomposition_pipeline.hitl import HumanApprovalGate, create_approval_gates, process_gate_response
from decomposition_pipeline.checkpoint import create_checkpointer
from decomposition_pipeline.graphs.level1_paradigm import create_level1_paradigm_graph
from decomposition_pipeline.graphs.level2_technique.graph import create_level2_graph
from decomposition_pipeline.graphs.level3_decomposition import (
    create_structural_decomposition_graph,
    create_functional_decomposition_graph,
    create_temporal_decomposition_graph,
    create_spatial_decomposition_graph,
    create_hierarchical_decomposition_graph,
    create_computational_decomposition_graph,
    create_data_decomposition_graph,
    create_dependency_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_integration.graph import create_integration_graph
from decomposition_pipeline.graphs.level4_solution.graph import create_level4_graph
# from decomposition_pipeline.graphs.level5_integration.graph import create_level5_graph

logger = logging.getLogger(__name__)


# =============================================================================
# Main Pipeline Nodes
# =============================================================================

def problem_ingestion(state: MainPipelineState) -> MainPipelineState:
    """
    Ingest and validate the problem input.

    This is the entry point of the pipeline. It validates the problem description
    and extracts initial characteristics.

    Args:
        state: Initial state with original_problem

    Returns:
        Updated state with validated problem and initial characteristics
    """
    logger.info("Starting problem ingestion")

    # Validate problem exists
    original_problem = state.get("original_problem", "")
    if not original_problem or not original_problem.strip():
        raise ValueError("Problem description cannot be empty")

    # Initialize state fields
    state["current_stage"] = PipelineStage.PROBLEM_INGESTION.value
    state["started_at"] = datetime.now().isoformat()

    # Generate thread ID if not present
    if "thread_id" not in state:
        state["thread_id"] = str(uuid.uuid4())

    # Initialize tracking fields
    if "human_approvals" not in state:
        state["human_approvals"] = []
    if "backtrack_history" not in state:
        state["backtrack_history"] = []

    # Basic problem characteristics (will be refined in Level 1)
    if "problem_characteristics" not in state or not state["problem_characteristics"]:
        state["problem_characteristics"] = {}

    # Always set basic characteristics
    state["problem_characteristics"]["problem_length"] = len(original_problem)
    state["problem_characteristics"]["has_technical_terms"] = any(
        term in original_problem.lower()
        for term in ["api", "database", "system", "algorithm", "data"]
    )

    logger.info(f"Problem ingestion complete for thread {state['thread_id']}")
    return state


def output_formatting(state: MainPipelineState) -> MainPipelineState:
    """
    Format the final solution for delivery.

    Takes the integrated solution from Level 5 and formats it for presentation.

    Args:
        state: State with integrated_solution

    Returns:
        State with formatted output
    """
    logger.info("Formatting final output")

    state["current_stage"] = PipelineStage.OUTPUT_FORMATTING.value

    integrated_solution = state.get("integrated_solution", {})
    if not integrated_solution:
        logger.error("No integrated solution found")
        raise ValueError("Cannot format output: no solution available")

    # Add metadata to solution
    solution_metadata = {
        "pipeline_version": "1.0",
        "thread_id": state.get("thread_id"),
        "started_at": state.get("started_at"),
        "completed_at": datetime.now().isoformat(),
        "selected_paradigms": state.get("selected_paradigms", []),
        "selected_techniques": list(state.get("selected_techniques", {}).keys()),
        "total_subproblems": len(state.get("integrated_subproblems", [])),
        "human_approvals_count": len(state.get("human_approvals", [])),
    }

    # Add metadata to solution
    if "metadata" not in integrated_solution:
        integrated_solution["metadata"] = {}
    integrated_solution["metadata"].update(solution_metadata)

    state["integrated_solution"] = integrated_solution
    state["current_stage"] = PipelineStage.COMPLETED.value
    state["completed_at"] = datetime.now().isoformat()

    logger.info("Output formatting complete")
    return state


# =============================================================================
# Conditional Routing Functions
# =============================================================================

def route_after_level1(state: MainPipelineState) -> Literal["gate1", "level2"]:
    """
    Route after Level 1 paradigm selection.

    Determines whether to go to approval gate or proceed directly to Level 2.

    Args:
        state: State after Level 1 completion

    Returns:
        "gate1" if gate is enabled, "level2" otherwise
    """
    # Check if gate is required/enabled
    # For now, always go through gate if paradigms selected
    selected_paradigms = state.get("selected_paradigms", [])

    if not selected_paradigms:
        logger.warning("No paradigms selected, proceeding to Level 2 anyway")

    logger.info(f"Routing after Level 1: {len(selected_paradigms)} paradigms selected")
    return "gate1"


def route_after_gate1(state: MainPipelineState) -> Literal["level2", "level1", "end"]:
    """
    Route after Gate 1 (paradigm approval).

    Handles the response from human approval gate.

    Args:
        state: State with gate response

    Returns:
        Next destination based on approval action
    """
    gate_response = state.get("_pending_gate_response")

    if not gate_response:
        # No response means auto-approved, proceed
        return "level2"

    action = gate_response.get("action", "approve")

    if action == "approve":
        return "level2"
    elif action == "reject":
        return "level1"  # Go back to Level 1
    elif action == "backtrack":
        # Handle backtracking
        return "level1"
    else:
        # For modify, add_context, request_alternatives, proceed with modifications
        return "level2"


def route_after_level2(state: MainPipelineState) -> Literal["gate2", "level3"]:
    """
    Route after Level 2 technique selection.

    Args:
        state: State after Level 2 completion

    Returns:
        Destination node
    """
    selected_techniques = state.get("selected_techniques", {})
    logger.info(f"Routing after Level 2: {len(selected_techniques)} techniques selected")
    return "gate2"


def route_after_gate2(state: MainPipelineState) -> Literal["level3", "level2", "end"]:
    """
    Route after Gate 2 (technique approval).

    Args:
        state: State with gate response

    Returns:
        Next destination based on approval action
    """
    gate_response = state.get("_pending_gate_response")

    if not gate_response:
        return "level3"

    action = gate_response.get("action", "approve")

    if action == "approve":
        return "level3"
    elif action == "reject":
        return "level2"
    else:
        return "level3"


def route_after_level3_integration(state: MainPipelineState) -> Literal["gate3", "level4"]:
    """
    Route after Level 3 integration.

    Args:
        state: State after Level 3.2 completion

    Returns:
        Destination node
    """
    integrated_subproblems = state.get("integrated_subproblems", [])
    logger.info(f"Routing after Level 3: {len(integrated_subproblems)} integrated subproblems")
    return "gate3"


def route_after_gate3(state: MainPipelineState) -> Literal["level4", "level3", "end"]:
    """
    Route after Gate 3 (decomposition approval).

    Args:
        state: State with gate response

    Returns:
        Next destination based on approval action
    """
    gate_response = state.get("_pending_gate_response")

    if not gate_response:
        return "level4"

    action = gate_response.get("action", "approve")

    if action == "approve":
        return "level4"
    elif action == "reject":
        return "level3"
    else:
        return "level4"


def route_after_level5(state: MainPipelineState) -> Literal["gate4"]:
    """
    Route after Level 5 solution integration.

    Gate 4 is always required, so always route there.

    Args:
        state: State after Level 5 completion

    Returns:
        "gate4" always
    """
    logger.info("Routing to Gate 4 (required final approval)")
    return "gate4"


def route_after_gate4(state: MainPipelineState) -> Literal["output", "level5", "end"]:
    """
    Route after Gate 4 (final approval).

    Args:
        state: State with gate response

    Returns:
        Next destination based on approval action
    """
    gate_response = state.get("_pending_gate_response")

    if not gate_response:
        # Should not happen as Gate 4 is required
        logger.warning("Gate 4 response missing but continuing")
        return "output"

    action = gate_response.get("action", "approve")

    if action == "approve":
        return "output"
    elif action == "reject":
        return "level5"
    else:
        return "output"


# =============================================================================
# Graph Construction
# =============================================================================

def create_main_orchestration_graph(
    checkpointer: SqliteSaver | None = None,
) -> StateGraph:
    """
    Create and compile the main orchestration graph.

    This is the top-level graph that orchestrates the entire decomposition pipeline
    by connecting all 5 levels with approval gates and conditional routing.

    Args:
        checkpointer: Optional SqliteSaver for state persistence

    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Creating main orchestration graph")

    # Create the main graph
    graph = StateGraph(MainPipelineState)

    # Create approval gates
    gates = create_approval_gates()

    # =========================================================================
    # Add Nodes
    # =========================================================================

    # Main pipeline nodes
    graph.add_node("problem_ingestion", problem_ingestion)
    graph.add_node("output_formatting", output_formatting)

    # Level subgraphs (these will be added as subgraphs)
    # For now, add placeholder nodes - we'll replace with actual subgraphs
    graph.add_node("level1", lambda s: {**s, "current_stage": PipelineStage.LEVEL1_PARADIGM_SELECTION.value})
    graph.add_node("level2", lambda s: {**s, "current_stage": PipelineStage.LEVEL2_TECHNIQUE_SELECTION.value})
    graph.add_node("level3", lambda s: {**s, "current_stage": PipelineStage.LEVEL3_DECOMPOSITION.value})
    graph.add_node("level3_integration", lambda s: {**s, "current_stage": PipelineStage.LEVEL3_INTEGRATION.value})
    graph.add_node("level4", lambda s: {**s, "current_stage": PipelineStage.LEVEL4_SOLUTION_GENERATION.value})
    graph.add_node("level5", lambda s: {**s, "current_stage": PipelineStage.LEVEL5_SOLUTION_INTEGRATION.value})

    # Approval gates
    graph.add_node("gate1", gates["paradigm_selection"])
    graph.add_node("gate2", gates["technique_selection"])
    graph.add_node("gate3", gates["decomposition_review"])
    graph.add_node("gate4", gates["final_solution"])

    # =========================================================================
    # Define Edges
    # =========================================================================

    # Entry point
    graph.set_entry_point("problem_ingestion")

    # Main flow
    graph.add_edge("problem_ingestion", "level1")

    # After Level 1 -> Gate 1
    graph.add_conditional_edges(
        "level1",
        route_after_level1,
        {
            "gate1": "gate1",
            "level2": "level2",
        }
    )

    # After Gate 1 -> Level 2 or back to Level 1
    graph.add_conditional_edges(
        "gate1",
        route_after_gate1,
        {
            "level2": "level2",
            "level1": "level1",
            "end": END,
        }
    )

    # After Level 2 -> Gate 2
    graph.add_conditional_edges(
        "level2",
        route_after_level2,
        {
            "gate2": "gate2",
            "level3": "level3",
        }
    )

    # After Gate 2 -> Level 3 or back to Level 2
    graph.add_conditional_edges(
        "gate2",
        route_after_gate2,
        {
            "level3": "level3",
            "level2": "level2",
            "end": END,
        }
    )

    # After Level 3 -> Level 3 Integration
    graph.add_edge("level3", "level3_integration")

    # After Level 3 Integration -> Gate 3
    graph.add_conditional_edges(
        "level3_integration",
        route_after_level3_integration,
        {
            "gate3": "gate3",
            "level4": "level4",
        }
    )

    # After Gate 3 -> Level 4 or back to Level 3
    graph.add_conditional_edges(
        "gate3",
        route_after_gate3,
        {
            "level4": "level4",
            "level3": "level3",
            "end": END,
        }
    )

    # After Level 4 -> Level 5
    graph.add_edge("level4", "level5")

    # After Level 5 -> Gate 4 (required)
    graph.add_conditional_edges(
        "level5",
        route_after_level5,
        {
            "gate4": "gate4",
        }
    )

    # After Gate 4 -> Output or back to Level 5
    graph.add_conditional_edges(
        "gate4",
        route_after_gate4,
        {
            "output": "output_formatting",
            "level5": "level5",
            "end": END,
        }
    )

    # After output formatting -> END
    graph.add_edge("output_formatting", END)

    # =========================================================================
    # Compile Graph
    # =========================================================================

    # If no checkpointer provided, create one
    if checkpointer is None:
        checkpointer = create_checkpointer()

    logger.info("Compiling main orchestration graph with checkpointing")
    compiled_graph = graph.compile(checkpointer=checkpointer)

    logger.info("Main orchestration graph created successfully")
    return compiled_graph


# Create the main graph instance
# This can be imported and used throughout the application
def get_main_graph() -> StateGraph:
    """
    Get a fresh instance of the main orchestration graph.

    Returns:
        Compiled main graph with checkpointing
    """
    return create_main_orchestration_graph()
