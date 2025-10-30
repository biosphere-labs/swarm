"""
Level 3.1: Paradigm Specialist Decomposition Subgraphs

This package contains 8 specialized subgraphs, one for each decomposition paradigm.
Each subgraph applies paradigm-specific techniques to break problems into subproblems.
"""

from decomposition_pipeline.graphs.level3_decomposition.structural import (
    create_structural_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_decomposition.functional import (
    create_functional_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_decomposition.temporal import (
    create_temporal_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_decomposition.spatial import (
    create_spatial_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_decomposition.hierarchical import (
    create_hierarchical_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_decomposition.computational import (
    create_computational_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_decomposition.data import (
    create_data_decomposition_graph,
)
from decomposition_pipeline.graphs.level3_decomposition.dependency import (
    create_dependency_decomposition_graph,
)

__all__ = [
    "create_structural_decomposition_graph",
    "create_functional_decomposition_graph",
    "create_temporal_decomposition_graph",
    "create_spatial_decomposition_graph",
    "create_hierarchical_decomposition_graph",
    "create_computational_decomposition_graph",
    "create_data_decomposition_graph",
    "create_dependency_decomposition_graph",
]
