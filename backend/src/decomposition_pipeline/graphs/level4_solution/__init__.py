"""
Level 4: Solution Generation Subgraph.

Routes subproblems to specialized agent pools and executes them in parallel
with proper dependency management.
"""

from .graph import (
    create_level4_graph,
    compile_level4_graph,
    level4_graph,
)
from .route_to_pools import (
    route_subproblems_to_pools,
    analyze_subproblem_requirements,
)
from .execute_parallel import (
    execute_parallel_solutions,
    create_execution_batches,
    CircularDependencyError,
)
from .monitor_progress import monitor_execution_progress
from .collect_solutions import collect_and_validate_solutions

__all__ = [
    # Graph
    "create_level4_graph",
    "compile_level4_graph",
    "level4_graph",
    # Routing
    "route_subproblems_to_pools",
    "analyze_subproblem_requirements",
    # Execution
    "execute_parallel_solutions",
    "create_execution_batches",
    "CircularDependencyError",
    # Monitoring
    "monitor_execution_progress",
    # Collection
    "collect_and_validate_solutions",
]
