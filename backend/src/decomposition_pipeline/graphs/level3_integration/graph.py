"""
Level 3.2: Integration Subgraph

LangGraph implementation that combines all integration nodes into a unified
subgraph for merging paradigm decompositions.
"""

from langgraph.graph import StateGraph, END
from ...schemas.state import Level3IntegrationState
from .collect_decompositions import collect_decompositions
from .detect_overlap import detect_overlap
from .resolve_conflicts import resolve_conflicts
from .build_dependency_graph import build_dependency_graph
from .validate_completeness import validate_completeness


def create_integration_graph() -> StateGraph:
    """
    Create the Level 3.2 Integration subgraph.
    
    Flow:
    1. CollectDecompositions: Gather all subproblems from paradigm subgraphs
    2. DetectOverlap: Find overlapping subproblems using similarity metrics
    3. ResolveConflicts: Merge or create multi-view subproblems
    4. BuildDependencyGraph: Construct dependency DAG
    5. ValidateCompleteness: Check coverage and consistency
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph
    graph = StateGraph(Level3IntegrationState)
    
    # Add nodes
    graph.add_node("collect_decompositions", collect_decompositions)
    graph.add_node("detect_overlap", detect_overlap)
    graph.add_node("resolve_conflicts", resolve_conflicts)
    graph.add_node("build_dependency_graph", build_dependency_graph)
    graph.add_node("validate_completeness", validate_completeness)
    
    # Define edges (linear flow)
    graph.set_entry_point("collect_decompositions")
    graph.add_edge("collect_decompositions", "detect_overlap")
    graph.add_edge("detect_overlap", "resolve_conflicts")
    graph.add_edge("resolve_conflicts", "build_dependency_graph")
    graph.add_edge("build_dependency_graph", "validate_completeness")
    graph.add_edge("validate_completeness", END)
    
    return graph.compile()


# Export convenience function
def run_integration(decomposed_subproblems: dict, original_problem: str = "") -> dict:
    """
    Convenience function to run integration on decomposed subproblems.
    
    Args:
        decomposed_subproblems: Dict mapping paradigm name to list of subproblems
        original_problem: Original problem text for validation
        
    Returns:
        Integration results with integrated_subproblems and validation_report
    """
    graph = create_integration_graph()
    
    initial_state: Level3IntegrationState = {
        "decomposed_subproblems": decomposed_subproblems,
        "original_problem": original_problem  # type: ignore
    }
    
    result = graph.invoke(initial_state)
    
    return result
