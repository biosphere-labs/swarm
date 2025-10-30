"""
Tests for Level 3.1: Paradigm Specialist Decomposition Subgraphs

Tests all 8 paradigm-specific decomposition subgraphs to ensure they
properly analyze problems and generate appropriate subproblems.
"""

import pytest
from decomposition_pipeline.schemas import (
    StructuralState,
    FunctionalState,
    TemporalState,
    SpatialState,
    HierarchicalState,
    ComputationalState,
    DataState,
    DependencyDecompositionState,
    Technique,
    SubproblemStatus,
)
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


# Sample problem description for testing
SAMPLE_PROBLEM = "Build a distributed e-commerce system with real-time inventory management"


# Sample techniques for each paradigm
def get_sample_technique(paradigm: str) -> Technique:
    """Create a sample technique for testing."""
    techniques = {
        "structural": Technique(
            name="Graph Partitioning",
            paradigm="structural",
            formal_definition="Partition graph G into subgraphs",
            prerequisites=["problem_is_graph"],
            complexity="O(|E| log |V|)",
            applicability_rules=[],
            literature_references=["METIS"],
            implementation_strategy="Apply partitioning algorithm"
        ),
        "functional": Technique(
            name="MapReduce",
            paradigm="functional",
            formal_definition="map and reduce operations",
            prerequisites=["operations_parallelizable"],
            complexity="O(n/p)",
            applicability_rules=[],
            literature_references=["Dean & Ghemawat 2004"],
            implementation_strategy="Define map and reduce functions"
        ),
        "temporal": Technique(
            name="Pipeline Stages",
            paradigm="temporal",
            formal_definition="Sequential stages with queues",
            prerequisites=["sequential_stages"],
            complexity="O(n)",
            applicability_rules=[],
            literature_references=["SEDA"],
            implementation_strategy="Define stages and boundaries"
        ),
        "spatial": Technique(
            name="Hash Partitioning",
            paradigm="spatial",
            formal_definition="Hash-based partitioning",
            prerequisites=["uniform_distribution"],
            complexity="O(1)",
            applicability_rules=[],
            literature_references=["Consistent Hashing"],
            implementation_strategy="Choose hash function"
        ),
        "hierarchical": Technique(
            name="Multi-tier Architecture",
            paradigm="hierarchical",
            formal_definition="Layered architecture",
            prerequisites=["layer_separation"],
            complexity="Depends on layers",
            applicability_rules=[],
            literature_references=["Buschmann 1996"],
            implementation_strategy="Define layer boundaries"
        ),
        "computational": Technique(
            name="Data Parallelism",
            paradigm="computational",
            formal_definition="Parallel data processing",
            prerequisites=["uniform_operations"],
            complexity="O(n/p)",
            applicability_rules=[],
            literature_references=["Flynn 1972"],
            implementation_strategy="Partition data across workers"
        ),
        "data": Technique(
            name="Horizontal Partitioning",
            paradigm="data",
            formal_definition="Row-based partitioning",
            prerequisites=["tabular_data"],
            complexity="O(1)",
            applicability_rules=[],
            literature_references=["Database sharding"],
            implementation_strategy="Choose partition key"
        ),
        "dependency": Technique(
            name="Topological Sort",
            paradigm="dependency",
            formal_definition="DAG ordering",
            prerequisites=["dependency_graph_is_dag"],
            complexity="O(V + E)",
            applicability_rules=[],
            literature_references=["CLRS"],
            implementation_strategy="Run topological sort"
        ),
    }
    return techniques[paradigm]


class TestStructuralDecomposition:
    """Test structural decomposition subgraph."""

    def test_structural_decomposition_creates_subproblems(self):
        """Test that structural decomposition generates subproblems."""
        graph = create_structural_decomposition_graph()

        initial_state: StructuralState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("structural"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "structural" for sp in result["subproblems"])
        assert all(sp["status"] == SubproblemStatus.PENDING for sp in result["subproblems"])

    def test_structural_identifies_components(self):
        """Test component identification."""
        graph = create_structural_decomposition_graph()

        initial_state: StructuralState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("structural"),
        }

        result = graph.invoke(initial_state)

        assert "identified_components" in result
        assert len(result["identified_components"]) >= 3


class TestFunctionalDecomposition:
    """Test functional decomposition subgraph."""

    def test_functional_decomposition_creates_subproblems(self):
        """Test that functional decomposition generates subproblems."""
        graph = create_functional_decomposition_graph()

        initial_state: FunctionalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("functional"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "functional" for sp in result["subproblems"])

    def test_functional_identifies_operations(self):
        """Test operation identification."""
        graph = create_functional_decomposition_graph()

        initial_state: FunctionalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("functional"),
        }

        result = graph.invoke(initial_state)

        assert "identified_operations" in result
        assert len(result["identified_operations"]) >= 3


class TestTemporalDecomposition:
    """Test temporal decomposition subgraph."""

    def test_temporal_decomposition_creates_subproblems(self):
        """Test that temporal decomposition generates subproblems."""
        graph = create_temporal_decomposition_graph()

        initial_state: TemporalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("temporal"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "temporal" for sp in result["subproblems"])

    def test_temporal_creates_timeline(self):
        """Test timeline extraction."""
        graph = create_temporal_decomposition_graph()

        initial_state: TemporalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("temporal"),
        }

        result = graph.invoke(initial_state)

        assert "timeline" in result
        assert "phases" in result["timeline"]


class TestSpatialDecomposition:
    """Test spatial decomposition subgraph."""

    def test_spatial_decomposition_creates_subproblems(self):
        """Test that spatial decomposition generates subproblems."""
        graph = create_spatial_decomposition_graph()

        initial_state: SpatialState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("spatial"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "spatial" for sp in result["subproblems"])

    def test_spatial_identifies_regions(self):
        """Test region identification."""
        graph = create_spatial_decomposition_graph()

        initial_state: SpatialState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("spatial"),
        }

        result = graph.invoke(initial_state)

        assert "identified_regions" in result
        assert len(result["identified_regions"]) >= 2


class TestHierarchicalDecomposition:
    """Test hierarchical decomposition subgraph."""

    def test_hierarchical_decomposition_creates_subproblems(self):
        """Test that hierarchical decomposition generates subproblems."""
        graph = create_hierarchical_decomposition_graph()

        initial_state: HierarchicalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("hierarchical"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "hierarchical" for sp in result["subproblems"])

    def test_hierarchical_identifies_levels(self):
        """Test level identification."""
        graph = create_hierarchical_decomposition_graph()

        initial_state: HierarchicalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("hierarchical"),
        }

        result = graph.invoke(initial_state)

        assert "identified_levels" in result
        assert len(result["identified_levels"]) >= 3


class TestComputationalDecomposition:
    """Test computational decomposition subgraph."""

    def test_computational_decomposition_creates_subproblems(self):
        """Test that computational decomposition generates subproblems."""
        graph = create_computational_decomposition_graph()

        initial_state: ComputationalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("computational"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "computational" for sp in result["subproblems"])

    def test_computational_profiles_resources(self):
        """Test resource profiling."""
        graph = create_computational_decomposition_graph()

        initial_state: ComputationalState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("computational"),
        }

        result = graph.invoke(initial_state)

        assert "resource_profile" in result
        assert "workload_analysis" in result


class TestDataDecomposition:
    """Test data decomposition subgraph."""

    def test_data_decomposition_creates_subproblems(self):
        """Test that data decomposition generates subproblems."""
        graph = create_data_decomposition_graph()

        initial_state: DataState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("data"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "data" for sp in result["subproblems"])

    def test_data_analyzes_schema(self):
        """Test schema analysis."""
        graph = create_data_decomposition_graph()

        initial_state: DataState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("data"),
        }

        result = graph.invoke(initial_state)

        assert "schema_analysis" in result
        assert "partition_keys" in result


class TestDependencyDecomposition:
    """Test dependency decomposition subgraph."""

    def test_dependency_decomposition_creates_subproblems(self):
        """Test that dependency decomposition generates subproblems."""
        graph = create_dependency_decomposition_graph()

        initial_state: DependencyDecompositionState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("dependency"),
        }

        result = graph.invoke(initial_state)

        assert "subproblems" in result
        assert len(result["subproblems"]) >= 2
        assert all(sp["paradigm"] == "dependency" for sp in result["subproblems"])

    def test_dependency_builds_graph(self):
        """Test dependency graph construction."""
        graph = create_dependency_decomposition_graph()

        initial_state: DependencyDecompositionState = {
            "original_problem": SAMPLE_PROBLEM,
            "selected_technique": get_sample_technique("dependency"),
        }

        result = graph.invoke(initial_state)

        assert "dependency_graph" in result
        assert "nodes" in result["dependency_graph"]
        assert "edges" in result["dependency_graph"]


class TestSubproblemQuality:
    """Test quality of generated subproblems across all paradigms."""

    @pytest.mark.parametrize("paradigm,graph_factory,state_class", [
        ("structural", create_structural_decomposition_graph, StructuralState),
        ("functional", create_functional_decomposition_graph, FunctionalState),
        ("temporal", create_temporal_decomposition_graph, TemporalState),
        ("spatial", create_spatial_decomposition_graph, SpatialState),
        ("hierarchical", create_hierarchical_decomposition_graph, HierarchicalState),
        ("computational", create_computational_decomposition_graph, ComputationalState),
        ("data", create_data_decomposition_graph, DataState),
        ("dependency", create_dependency_decomposition_graph, DependencyDecompositionState),
    ])
    def test_subproblem_has_required_fields(self, paradigm, graph_factory, state_class):
        """Test that all subproblems have required fields."""
        graph = graph_factory()

        initial_state = state_class(
            original_problem=SAMPLE_PROBLEM,
            selected_technique=get_sample_technique(paradigm),
        )

        result = graph.invoke(initial_state)
        subproblems = result.get("subproblems", [])

        for sp in subproblems:
            assert "id" in sp
            assert "title" in sp
            assert "description" in sp
            assert "paradigm" in sp
            assert "source_technique" in sp
            assert "status" in sp
            assert "dependencies" in sp
            assert sp["paradigm"] == paradigm

    @pytest.mark.parametrize("paradigm,graph_factory,state_class", [
        ("structural", create_structural_decomposition_graph, StructuralState),
        ("functional", create_functional_decomposition_graph, FunctionalState),
        ("temporal", create_temporal_decomposition_graph, TemporalState),
        ("spatial", create_spatial_decomposition_graph, SpatialState),
        ("hierarchical", create_hierarchical_decomposition_graph, HierarchicalState),
        ("computational", create_computational_decomposition_graph, ComputationalState),
        ("data", create_data_decomposition_graph, DataState),
        ("dependency", create_dependency_decomposition_graph, DependencyDecompositionState),
    ])
    def test_subproblem_descriptions_are_meaningful(self, paradigm, graph_factory, state_class):
        """Test that subproblem descriptions are not empty and meaningful."""
        graph = graph_factory()

        initial_state = state_class(
            original_problem=SAMPLE_PROBLEM,
            selected_technique=get_sample_technique(paradigm),
        )

        result = graph.invoke(initial_state)
        subproblems = result.get("subproblems", [])

        for sp in subproblems:
            assert len(sp["description"]) > 50  # Meaningful description
            assert sp["title"] != ""
            assert sp["confidence"] > 0.0
            assert sp["confidence"] <= 1.0
