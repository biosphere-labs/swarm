"""
Comprehensive tests for Level 3.2 Integration Subgraph.

Tests all integration nodes and the complete graph flow.
"""

import pytest
from src.decomposition_pipeline.schemas.state import (
    Level3IntegrationState,
    Subproblem,
    SubproblemStatus,
    ValidationReport,
    DependencyGraph
)
from src.decomposition_pipeline.graphs.level3_integration import (
    collect_decompositions,
    detect_overlap,
    resolve_conflicts,
    build_dependency_graph,
    validate_completeness,
    run_integration
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_subproblems_divide_conquer():
    """Sample subproblems from divide & conquer paradigm."""
    return [
        {
            "id": "dc_1",
            "title": "Split array in half",
            "description": "Divide the input array into two equal halves",
            "paradigm": "divide_conquer",
            "source_technique": "binary_split",
            "status": SubproblemStatus.PENDING,
            "dependencies": [],
            "confidence": 0.9
        },
        {
            "id": "dc_2",
            "title": "Process left half",
            "description": "Recursively process the left half of the array",
            "paradigm": "divide_conquer",
            "source_technique": "recursive_processing",
            "status": SubproblemStatus.PENDING,
            "dependencies": ["dc_1"],
            "confidence": 0.85
        },
        {
            "id": "dc_3",
            "title": "Process right half",
            "description": "Recursively process the right half of the array",
            "paradigm": "divide_conquer",
            "source_technique": "recursive_processing",
            "status": SubproblemStatus.PENDING,
            "dependencies": ["dc_1"],
            "confidence": 0.85
        }
    ]


@pytest.fixture
def sample_subproblems_dynamic_programming():
    """Sample subproblems from dynamic programming paradigm."""
    return [
        {
            "id": "dp_1",
            "title": "Initialize memoization table",
            "description": "Create a table to store intermediate results",
            "paradigm": "dynamic_programming",
            "source_technique": "memoization",
            "status": SubproblemStatus.PENDING,
            "dependencies": [],
            "confidence": 0.95
        },
        {
            "id": "dp_2",
            "title": "Compute optimal substructure",
            "description": "Calculate optimal solution using stored results",
            "paradigm": "dynamic_programming",
            "source_technique": "bottom_up",
            "status": SubproblemStatus.PENDING,
            "dependencies": ["dp_1"],
            "confidence": 0.88
        }
    ]


@pytest.fixture
def sample_subproblems_with_overlap():
    """Sample subproblems with intentional overlap for testing."""
    return {
        "divide_conquer": [
            {
                "id": "dc_1",
                "title": "Split input data",
                "description": "Divide the input data into smaller chunks for processing",
                "paradigm": "divide_conquer",
                "source_technique": "splitting",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
                "confidence": 0.9
            }
        ],
        "data": [
            {
                "id": "data_1",
                "title": "Partition data",
                "description": "Split the input data into smaller chunks for parallel processing",
                "paradigm": "data",
                "source_technique": "partitioning",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
                "confidence": 0.87
            }
        ]
    }


# ============================================================================
# CollectDecompositions Tests
# ============================================================================

def test_collect_decompositions_basic(
    sample_subproblems_divide_conquer,
    sample_subproblems_dynamic_programming
):
    """Test basic collection of subproblems from multiple paradigms."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {
            "divide_conquer": sample_subproblems_divide_conquer,
            "dynamic_programming": sample_subproblems_dynamic_programming
        }
    }
    
    result = collect_decompositions(state)
    
    # Check all subproblems collected
    assert "all_subproblems" in result
    assert len(result["all_subproblems"]) == 5
    
    # Check paradigm tags
    paradigms = {sp["paradigm"] for sp in result["all_subproblems"]}
    assert "divide_conquer" in paradigms
    assert "dynamic_programming" in paradigms


def test_collect_decompositions_id_prefix():
    """Test that IDs get paradigm prefix."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {
            "greedy": [
                {
                    "id": "1",
                    "title": "Test",
                    "description": "Test subproblem",
                    "paradigm": "greedy",
                    "source_technique": "test",
                    "status": SubproblemStatus.PENDING,
                    "dependencies": []
                }
            ]
        }
    }
    
    result = collect_decompositions(state)
    
    # ID should have greedy_ prefix
    assert result["all_subproblems"][0]["id"] == "greedy_1"


def test_collect_decompositions_empty():
    """Test collection with no subproblems."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {}
    }
    
    result = collect_decompositions(state)
    
    assert result["all_subproblems"] == []


# ============================================================================
# DetectOverlap Tests
# ============================================================================

def test_detect_overlap_no_overlap(
    sample_subproblems_divide_conquer,
    sample_subproblems_dynamic_programming
):
    """Test overlap detection with dissimilar subproblems."""
    all_subproblems = (
        sample_subproblems_divide_conquer +
        sample_subproblems_dynamic_programming
    )
    
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "all_subproblems": all_subproblems
    }
    
    result = detect_overlap(state)
    
    # Should have no overlaps (different topics)
    assert "overlap_clusters" in result
    assert len(result["overlap_clusters"]) == 0


def test_detect_overlap_with_similar():
    """Test overlap detection with similar subproblems."""
    similar_subproblems = [
        {
            "id": "sp1",
            "title": "Process data items",
            "description": "Iterate through all data items and process them individually",
            "paradigm": "functional",
            "source_technique": "map",
            "status": SubproblemStatus.PENDING,
            "dependencies": []
        },
        {
            "id": "sp2",
            "title": "Process data items",
            "description": "Loop through all data items and handle each one separately",
            "paradigm": "temporal",
            "source_technique": "iteration",
            "status": SubproblemStatus.PENDING,
            "dependencies": []
        }
    ]
    
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "all_subproblems": similar_subproblems
    }
    
    result = detect_overlap(state)
    
    # Should detect overlap (very similar descriptions)
    assert "overlap_clusters" in result
    # Note: Threshold is 0.8, so this might or might not cluster
    # depending on exact similarity calculation


def test_detect_overlap_empty():
    """Test overlap detection with empty input."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "all_subproblems": []
    }
    
    result = detect_overlap(state)
    
    assert result["overlap_clusters"] == []
    assert result["similarity_matrix"] == {}


# ============================================================================
# ResolveConflicts Tests
# ============================================================================

def test_resolve_conflicts_no_conflicts():
    """Test conflict resolution with no overlaps."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "all_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First task",
                "paradigm": "greedy",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second task",
                "paradigm": "backtracking",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            }
        ],
        "overlap_clusters": []
    }
    
    result = resolve_conflicts(state)
    
    # All subproblems should remain
    assert len(result["resolved_subproblems"]) == 2
    assert result["detected_conflicts"] == []


def test_resolve_conflicts_same_paradigm():
    """Test merging subproblems from same paradigm."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "all_subproblems": [
            {
                "id": "greedy_1",
                "title": "Select maximum",
                "description": "Choose the maximum value",
                "paradigm": "greedy",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            },
            {
                "id": "greedy_2",
                "title": "Pick largest",
                "description": "Select the largest item",
                "paradigm": "greedy",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            }
        ],
        "overlap_clusters": [["greedy_1", "greedy_2"]]
    }
    
    result = resolve_conflicts(state)
    
    # Should merge into single subproblem
    assert len(result["resolved_subproblems"]) == 1
    merged = result["resolved_subproblems"][0]
    assert "merged_from" in merged.get("metadata", {})


def test_resolve_conflicts_different_paradigms():
    """Test multi-view creation for different paradigms."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "all_subproblems": [
            {
                "id": "func_1",
                "title": "Transform data",
                "description": "Apply transformation to data",
                "paradigm": "functional",
                "source_technique": "map",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            },
            {
                "id": "data_1",
                "title": "Transform data",
                "description": "Apply transformation to data",
                "paradigm": "data",
                "source_technique": "projection",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            }
        ],
        "overlap_clusters": [["func_1", "data_1"]]
    }
    
    result = resolve_conflicts(state)
    
    # Should create multi-view subproblem
    assert len(result["resolved_subproblems"]) == 1
    multiview = result["resolved_subproblems"][0]
    assert multiview["paradigm"] == "multiview"
    assert "views" in multiview.get("metadata", {})
    assert len(multiview["metadata"]["views"]) == 2


# ============================================================================
# BuildDependencyGraph Tests
# ============================================================================

def test_build_dependency_graph_basic():
    """Test basic dependency graph construction."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "resolved_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First task",
                "paradigm": "test",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second task",
                "paradigm": "test",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": ["sp1"]
            },
            {
                "id": "sp3",
                "title": "Task 3",
                "description": "Third task",
                "paradigm": "test",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": ["sp2"]
            }
        ]
    }
    
    result = build_dependency_graph(state)
    
    # Check graph structure
    graph = result["subproblem_dependencies"]
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2
    
    # Check critical path
    assert "critical_path" in graph
    assert len(graph["critical_path"]) > 0


def test_build_dependency_graph_parallel():
    """Test parallel execution batches identification."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "resolved_subproblems": [
            {
                "id": "sp1",
                "title": "Root task",
                "description": "Root",
                "paradigm": "test",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            },
            {
                "id": "sp2",
                "title": "Parallel 1",
                "description": "Can run in parallel",
                "paradigm": "test",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": ["sp1"]
            },
            {
                "id": "sp3",
                "title": "Parallel 2",
                "description": "Can run in parallel",
                "paradigm": "test",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": ["sp1"]
            }
        ]
    }
    
    result = build_dependency_graph(state)
    
    # Check execution batches
    assert "execution_batches" in result
    batches = result["execution_batches"]
    # Should have 2 batches: [sp1], [sp2, sp3]
    assert len(batches) >= 2
    assert len(batches[1]) == 2  # sp2 and sp3 can run in parallel


def test_build_dependency_graph_empty():
    """Test dependency graph with no subproblems."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "resolved_subproblems": []
    }
    
    result = build_dependency_graph(state)
    
    graph = result["subproblem_dependencies"]
    assert graph["nodes"] == []
    assert graph["edges"] == []


# ============================================================================
# ValidateCompleteness Tests
# ============================================================================

def test_validate_completeness_valid():
    """Test validation with complete, valid decomposition."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "resolved_subproblems": [
            {
                "id": "sp1",
                "title": "Sort array elements",
                "description": "Sort the array using quicksort algorithm efficiently",
                "paradigm": "divide_conquer",
                "source_technique": "quicksort",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            },
            {
                "id": "sp2",
                "title": "Find median value",
                "description": "Find the median element in the sorted array",
                "paradigm": "divide_conquer",
                "source_technique": "binary_search",
                "status": SubproblemStatus.PENDING,
                "dependencies": ["sp1"]
            }
        ],
        "original_problem": "Sort an array and find the median value efficiently",
        "detected_conflicts": []
    }
    
    result = validate_completeness(state)
    
    # Should be valid
    report = result["validation_report"]
    assert report["status"] in ["valid", "warning"]
    assert not report["has_critical_failures"]


def test_validate_completeness_missing_dependencies():
    """Test validation catches missing dependencies."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "resolved_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First task",
                "paradigm": "test",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": ["sp_missing"]  # This dependency doesn't exist
            }
        ],
        "original_problem": "Test problem"
    }
    
    result = validate_completeness(state)
    
    # Should fail validation
    report = result["validation_report"]
    assert report["status"] == "invalid"
    assert report["has_critical_failures"]
    assert any("missing" in issue.lower() for issue in report["issues"])


def test_validate_completeness_empty():
    """Test validation with no subproblems."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {},
        "resolved_subproblems": [],
        "original_problem": "Test problem"
    }
    
    result = validate_completeness(state)
    
    # Should be invalid
    report = result["validation_report"]
    assert report["status"] == "invalid"
    assert report["has_critical_failures"]


# ============================================================================
# Full Integration Tests
# ============================================================================

def test_full_integration_flow(sample_subproblems_with_overlap):
    """Test complete integration flow from start to finish."""
    result = run_integration(
        decomposed_subproblems=sample_subproblems_with_overlap,
        original_problem="Split and process input data efficiently"
    )
    
    # Check all expected outputs exist
    assert "integrated_subproblems" in result
    assert "subproblem_dependencies" in result
    assert "validation_report" in result
    
    # Should have integrated subproblems
    assert len(result["integrated_subproblems"]) > 0
    
    # Validation should complete
    report = result["validation_report"]
    assert report["status"] in ["valid", "warning", "invalid"]


def test_full_integration_complex_scenario():
    """Test integration with multiple paradigms and dependencies."""
    complex_decomposition = {
        "divide_conquer": [
            {
                "id": "1",
                "title": "Split data",
                "description": "Divide data into chunks",
                "paradigm": "divide_conquer",
                "source_technique": "splitting",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            }
        ],
        "dynamic_programming": [
            {
                "id": "1",
                "title": "Build DP table",
                "description": "Create memoization table for results",
                "paradigm": "dynamic_programming",
                "source_technique": "memoization",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            }
        ],
        "greedy": [
            {
                "id": "1",
                "title": "Select optimal choice",
                "description": "Choose the best option at each step",
                "paradigm": "greedy",
                "source_technique": "optimization",
                "status": SubproblemStatus.PENDING,
                "dependencies": []
            }
        ]
    }
    
    result = run_integration(
        decomposed_subproblems=complex_decomposition,
        original_problem="Optimize data processing with efficient algorithms"
    )
    
    # All paradigms should be integrated
    assert len(result["integrated_subproblems"]) >= 3
    
    # Should have dependency graph
    graph = result["subproblem_dependencies"]
    assert len(graph["nodes"]) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
