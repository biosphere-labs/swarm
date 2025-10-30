"""
Level 5: Solution Integration Subgraph.

Merges partial solutions from Level 4 into a coherent final solution.
"""

from .map_solutions import map_solutions_to_problem
from .detect_conflicts import detect_solution_conflicts
from .resolve_conflicts import resolve_solution_conflicts
from .fill_gaps import fill_solution_gaps
from .synthesize_final import synthesize_final_solution
from .validate_solution import validate_integrated_solution
from .graph import create_level5_graph, compile_level5_graph, level5_graph

__all__ = [
    "map_solutions_to_problem",
    "detect_solution_conflicts",
    "resolve_solution_conflicts",
    "fill_solution_gaps",
    "synthesize_final_solution",
    "validate_integrated_solution",
    "create_level5_graph",
    "compile_level5_graph",
    "level5_graph",
]
