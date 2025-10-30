"""
CollectDecompositionsNode - Gathers subproblems from all paradigm subgraphs.

This node implements the first step of the integration process by collecting
all decomposed subproblems from the 8 paradigm-specific subgraphs and creating
an initial combined list with proper tagging.
"""

from typing import List
from ...schemas.state import Level3IntegrationState, Subproblem


def collect_decompositions(state: Level3IntegrationState) -> Level3IntegrationState:
    """
    Collect all subproblems from paradigm subgraphs into a unified list.
    
    Algorithm:
    1. Iterate through all paradigm decompositions
    2. Tag each subproblem with its source paradigm (if not already tagged)
    3. Assign unique IDs to ensure no collisions
    4. Create flattened list of all subproblems
    
    Args:
        state: Integration state containing decomposed_subproblems from all paradigms
        
    Returns:
        Updated state with all_subproblems list populated
    """
    all_subproblems: List[Subproblem] = []
    
    # Collect subproblems from all paradigms
    decomposed = state.get("decomposed_subproblems", {})
    
    for paradigm, subproblems in decomposed.items():
        for subproblem in subproblems:
            # Ensure paradigm is tagged
            if not subproblem.get("paradigm"):
                subproblem["paradigm"] = paradigm
            
            # Ensure unique ID includes paradigm prefix
            if not subproblem["id"].startswith(f"{paradigm}_"):
                subproblem["id"] = f"{paradigm}_{subproblem['id']}"
            
            all_subproblems.append(subproblem)
    
    return {
        **state,
        "all_subproblems": all_subproblems
    }
