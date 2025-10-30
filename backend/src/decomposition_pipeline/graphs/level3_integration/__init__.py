"""
Level 3.2: Integration Subgraph

Combines decompositions from multiple paradigm subgraphs into a coherent whole
using established integration algorithms from literature.
"""

from .graph import create_integration_graph, run_integration
from .collect_decompositions import collect_decompositions
from .detect_overlap import detect_overlap
from .resolve_conflicts import resolve_conflicts
from .build_dependency_graph import build_dependency_graph
from .validate_completeness import validate_completeness

__all__ = [
    "create_integration_graph",
    "run_integration",
    "collect_decompositions",
    "detect_overlap",
    "resolve_conflicts",
    "build_dependency_graph",
    "validate_completeness",
]
