"""
Integration tests for Level 2 Technique Selection Graph.

Tests the complete subgraph execution using LangGraph.
"""

import pytest

from decomposition_pipeline.graphs.level2_technique.graph import create_level2_graph
from decomposition_pipeline.schemas.state import Level2State


class TestLevel2Graph:
    """Integration tests for the Level 2 graph."""

    def test_graph_creation(self):
        """Test that graph can be created and compiled."""
        graph = create_level2_graph()
        assert graph is not None

    def test_graph_execution_single_paradigm(self):
        """Test graph execution with a single paradigm."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Implement a sorting algorithm for large datasets",
            "problem_characteristics": {
                "problem_size": 100000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "has_recursive_structure": True,
            },
            "selected_paradigms": ["structural"],
        }

        result = graph.invoke(initial_state)

        # Verify output
        assert "selected_techniques" in result
        assert "technique_justification" in result
        assert "candidate_techniques" in result
        assert "technique_scores" in result

        # Should have selected structural technique
        assert "structural" in result["selected_techniques"]

        technique = result["selected_techniques"]["structural"]
        assert technique["name"] is not None
        assert technique["paradigm"] == "structural"
        assert "score" in technique

    def test_graph_execution_multiple_paradigms(self):
        """Test graph execution with multiple paradigms."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Build a real-time distributed data processing pipeline",
            "problem_characteristics": {
                "large_dataset": True,
                "operations_parallelizable": True,
                "embarrassingly_parallel": True,
                "associative_reduction": True,
                "real_time_processing": True,
                "continuous_data_flow": True,
                "low_latency_required": True,
                "uniform_operations": True,
                "independent_data_elements": True,
            },
            "selected_paradigms": ["functional", "temporal", "computational"],
        }

        result = graph.invoke(initial_state)

        # Should have selected techniques for all paradigms
        assert len(result["selected_techniques"]) == 3
        assert "functional" in result["selected_techniques"]
        assert "temporal" in result["selected_techniques"]
        assert "computational" in result["selected_techniques"]

        # Each should have justification
        assert len(result["technique_justification"]) == 3

    def test_graph_execution_with_database_problem(self):
        """Test graph with database partitioning problem."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Design a sharding strategy for a distributed database",
            "problem_characteristics": {
                "large_dataset": True,
                "tabular_data": True,
                "partition_key_exists": True,
                "locality_of_access": True,
                "uniform_distribution_desired": True,
                "point_queries_common": True,
                "hash_function_available": True,  # Add for spatial techniques
                "ordered_key_space": True,  # Add for range partitioning
                "range_identifiable": True,  # Add for range partitioning
            },
            "selected_paradigms": ["data", "spatial"],
        }

        result = graph.invoke(initial_state)

        # Should select at least data techniques
        assert "data" in result["selected_techniques"]
        # Spatial may or may not be selected depending on prerequisites

        # Check that selected techniques are appropriate
        data_technique = result["selected_techniques"]["data"]
        assert "Partitioning" in data_technique["name"] or "Sharding" in data_technique["name"]

    def test_graph_execution_with_hierarchical_problem(self):
        """Test graph with hierarchical decomposition problem."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Design a multi-tier web application architecture",
            "problem_characteristics": {
                "layer_separation_possible": True,
                "abstraction_levels_clear": True,
                "layer_independence": True,
                "has_hierarchical_structure": True,
                "supports_aggregation": True,
            },
            "selected_paradigms": ["hierarchical"],
        }

        result = graph.invoke(initial_state)

        assert "hierarchical" in result["selected_techniques"]

        technique = result["selected_techniques"]["hierarchical"]
        justification = result["technique_justification"]["hierarchical"]

        # Should mention architecture or layers
        assert any(
            word in technique["name"].lower()
            for word in ["tier", "layer", "architecture", "pyramid", "hierarchy"]
        )

    def test_graph_execution_with_dependency_problem(self):
        """Test graph with dependency-based problem."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Schedule tasks with dependencies for parallel execution",
            "problem_characteristics": {
                "dependency_graph_is_dag": True,
                "dependencies_explicit": True,
                "task_durations_known": True,
                "optimize_makespan": True,
            },
            "selected_paradigms": ["dependency"],
        }

        result = graph.invoke(initial_state)

        assert "dependency" in result["selected_techniques"]

        technique = result["selected_techniques"]["dependency"]

        # Should select topological sort or critical path
        assert any(
            word in technique["name"].lower()
            for word in ["topological", "critical", "path", "schedule"]
        )

    def test_graph_preserves_input_state(self):
        """Test that graph preserves original input fields."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Test problem preservation",
            "problem_characteristics": {
                "problem_size": 1000,
                "test_characteristic": True,
            },
            "selected_paradigms": ["structural"],
        }

        result = graph.invoke(initial_state)

        # Original fields should be preserved
        assert result["original_problem"] == initial_state["original_problem"]
        assert result["problem_characteristics"] == initial_state["problem_characteristics"]
        assert result["selected_paradigms"] == initial_state["selected_paradigms"]

    def test_graph_handles_no_paradigms(self):
        """Test graph behavior with no paradigms selected."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "No paradigms selected",
            "problem_characteristics": {"problem_size": 100},
            "selected_paradigms": [],
        }

        result = graph.invoke(initial_state)

        # Should complete without error
        assert "selected_techniques" in result
        assert len(result["selected_techniques"]) == 0

    def test_graph_handles_minimal_characteristics(self):
        """Test graph with minimal problem characteristics."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Minimal characteristics problem",
            "problem_characteristics": {
                # Very few characteristics
                "problem_size": 100,
            },
            "selected_paradigms": ["structural"],
        }

        result = graph.invoke(initial_state)

        # Should still select something, even with minimal info
        assert "selected_techniques" in result
        # May or may not have techniques depending on prerequisites
        # Just verify it doesn't crash

    def test_justification_quality(self):
        """Test that justifications are comprehensive."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Comprehensive justification test",
            "problem_characteristics": {
                "problem_size": 50000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "has_recursive_structure": True,
            },
            "selected_paradigms": ["structural"],
        }

        result = graph.invoke(initial_state)

        justification = result["technique_justification"]["structural"]

        # Check for key sections
        required_sections = [
            "Technique Selection:",
            "Applicability Score:",
            "Formal Definition",
            "Complexity",
            "Why This Technique Was Selected",
            "Prerequisites Met",
            "Implementation Strategy",
            "Literature References",
            "Application to Current Problem",
        ]

        for section in required_sections:
            assert section in justification, f"Missing section: {section}"

        # Should have actual content, not just headers
        assert len(justification) > 500  # Should be substantial

    def test_all_paradigms_coverage(self):
        """Test that graph can handle all 8 paradigms."""
        graph = create_level2_graph()

        all_paradigms = [
            "structural",
            "functional",
            "temporal",
            "spatial",
            "hierarchical",
            "computational",
            "data",
            "dependency",
        ]

        # Create characteristics that should work for most paradigms
        # We need to satisfy prerequisites for techniques to be selected
        initial_state: Level2State = {
            "original_problem": "Comprehensive multi-paradigm system",
            "problem_characteristics": {
                "problem_size": 100000,
                "large_dataset": True,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "operations_parallelizable": True,
                "associative_reduction": True,
                "real_time_processing": True,
                "continuous_data_flow": True,
                "has_hierarchical_structure": True,
                "layer_separation_possible": True,
                "abstraction_levels_clear": True,
                "uniform_distribution_desired": True,
                "hash_function_available": True,
                "uniform_operations": True,
                "independent_data_elements": True,
                "tabular_data": True,
                "partition_key_exists": True,
                "dependency_graph_is_dag": True,
                "dependencies_explicit": True,
            },
            "selected_paradigms": all_paradigms,
        }

        result = graph.invoke(initial_state)

        # Should have selected techniques for most/all paradigms
        selected_count = len(result["selected_techniques"])
        assert selected_count >= 4  # At least half should match

    def test_scores_are_reasonable(self):
        """Test that selected technique scores are in valid range."""
        graph = create_level2_graph()

        initial_state: Level2State = {
            "original_problem": "Score validation test",
            "problem_characteristics": {
                "problem_size": 10000,
                "large_dataset": True,
                "operations_parallelizable": True,
                "embarrassingly_parallel": True,
                "associative_reduction": True,
            },
            "selected_paradigms": ["functional", "computational"],
        }

        result = graph.invoke(initial_state)

        for paradigm, technique in result["selected_techniques"].items():
            score = technique["score"]
            assert 0.0 <= score <= 1.0, f"{paradigm} score {score} out of range"
            # Selected techniques should generally have decent scores
            assert score > 0.3, f"{paradigm} score {score} seems too low for selection"
