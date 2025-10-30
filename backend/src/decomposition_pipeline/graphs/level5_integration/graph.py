"""
Level 5: Solution Integration Subgraph.

Implements the complete Level 5 architecture from brainstorm_1.md lines 519-595.
Merges partial solutions from Level 4 into a coherent, validated final solution.
"""

from langgraph.graph import StateGraph, END
from ...schemas.state import Level5State
from .map_solutions import map_solutions_to_problem
from .detect_conflicts import detect_solution_conflicts
from .resolve_conflicts import resolve_solution_conflicts
from .fill_gaps import fill_solution_gaps
from .synthesize_final import synthesize_final_solution
from .validate_solution import validate_integrated_solution


def create_level5_graph() -> StateGraph:
    """
    Create the Level 5 Solution Integration subgraph.

    Graph structure:
    1. map_solutions - Map solutions to problem structure and identify coverage
    2. detect_conflicts - Identify conflicts between solutions
    3. resolve_conflicts - Resolve detected conflicts
    4. fill_gaps - Identify and fill solution gaps
    5. synthesize_final - Combine into integrated solution
    6. validate_solution - Validate final solution
    7. END

    Returns:
        StateGraph for Level 5
    """
    # Create graph
    graph = StateGraph(Level5State)

    # Add nodes
    graph.add_node("map_solutions", map_solutions_to_problem)
    graph.add_node("detect_conflicts", detect_solution_conflicts)
    graph.add_node("resolve_conflicts", resolve_solution_conflicts)
    graph.add_node("fill_gaps", fill_solution_gaps)
    graph.add_node("synthesize_final", synthesize_final_solution)
    graph.add_node("validate_solution", validate_integrated_solution)

    # Define edges (linear flow for Level 5)
    graph.set_entry_point("map_solutions")
    graph.add_edge("map_solutions", "detect_conflicts")
    graph.add_edge("detect_conflicts", "resolve_conflicts")
    graph.add_edge("resolve_conflicts", "fill_gaps")
    graph.add_edge("fill_gaps", "synthesize_final")
    graph.add_edge("synthesize_final", "validate_solution")
    graph.add_edge("validate_solution", END)

    return graph


def compile_level5_graph() -> StateGraph:
    """
    Compile the Level 5 graph for execution.

    Returns:
        Compiled graph ready for invocation
    """
    graph = create_level5_graph()
    return graph.compile()


# Export the compiled graph
level5_graph = compile_level5_graph()
