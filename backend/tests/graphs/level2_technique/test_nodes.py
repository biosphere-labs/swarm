"""
Unit tests for Level 2 Technique Selection nodes.

Tests each node in isolation to verify correct behavior.
"""

import pytest

from decomposition_pipeline.graphs.level2_technique.nodes import (
    retrieve_techniques,
    score_techniques,
    select_techniques,
)
from decomposition_pipeline.schemas.state import Level2State


class TestRetrieveTechniques:
    """Tests for the retrieve_techniques node."""

    def test_retrieve_for_single_paradigm(self):
        """Test retrieval for a single paradigm."""
        state: Level2State = {
            "original_problem": "Build a sorting algorithm for large datasets",
            "problem_characteristics": {
                "problem_size": 10000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "has_recursive_structure": True,
            },
            "selected_paradigms": ["structural"],
        }

        result = retrieve_techniques(state)

        assert "candidate_techniques" in result
        assert "structural" in result["candidate_techniques"]
        assert len(result["candidate_techniques"]["structural"]) > 0

        # Check that we got Technique objects
        techniques = result["candidate_techniques"]["structural"]
        assert all(hasattr(t, "name") for t in techniques)
        assert all(hasattr(t, "paradigm") for t in techniques)

    def test_retrieve_for_multiple_paradigms(self):
        """Test retrieval for multiple paradigms."""
        state: Level2State = {
            "original_problem": "Build a real-time data processing system",
            "problem_characteristics": {
                "large_dataset": True,
                "real_time_processing": True,
                "continuous_data_flow": True,
                "operations_parallelizable": True,
                "associative_reduction": True,
            },
            "selected_paradigms": ["functional", "temporal"],
        }

        result = retrieve_techniques(state)

        assert "candidate_techniques" in result
        assert "functional" in result["candidate_techniques"]
        assert "temporal" in result["candidate_techniques"]
        assert len(result["candidate_techniques"]["functional"]) > 0
        assert len(result["candidate_techniques"]["temporal"]) > 0

    def test_retrieve_with_no_prerequisites_met(self):
        """Test retrieval when no prerequisites are met."""
        state: Level2State = {
            "original_problem": "A simple problem",
            "problem_characteristics": {
                # Minimal characteristics - many prerequisites won't be met
                "problem_size": 100,
            },
            "selected_paradigms": ["structural"],
        }

        result = retrieve_techniques(state)

        # Should still return a result, but may have fewer techniques
        assert "candidate_techniques" in result
        assert "structural" in result["candidate_techniques"]

    def test_retrieve_empty_paradigms(self):
        """Test retrieval with no paradigms selected."""
        state: Level2State = {
            "original_problem": "A problem",
            "problem_characteristics": {"problem_size": 1000},
            "selected_paradigms": [],
        }

        result = retrieve_techniques(state)

        assert "candidate_techniques" in result
        assert len(result["candidate_techniques"]) == 0


class TestScoreTechniques:
    """Tests for the score_techniques node."""

    def test_score_single_paradigm(self):
        """Test scoring techniques for a single paradigm."""
        # First retrieve techniques
        state: Level2State = {
            "original_problem": "Sorting problem",
            "problem_characteristics": {
                "problem_size": 10000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "has_recursive_structure": True,
            },
            "selected_paradigms": ["structural"],
        }

        state = retrieve_techniques(state)

        # Now score
        result = score_techniques(state)

        assert "technique_scores" in result
        assert len(result["technique_scores"]) > 0

        # Check score format
        for key, score in result["technique_scores"].items():
            assert ":" in key  # Should be "paradigm:technique_name"
            assert 0.0 <= score <= 1.0  # Scores should be normalized

    def test_score_multiple_paradigms(self):
        """Test scoring techniques across multiple paradigms."""
        state: Level2State = {
            "original_problem": "Data processing system",
            "problem_characteristics": {
                "large_dataset": True,
                "operations_parallelizable": True,
                "embarrassingly_parallel": True,
                "associative_reduction": True,
                "needs_aggregation": True,
                "uniform_operations": True,  # Add for computational techniques
                "independent_data_elements": True,  # Add for computational techniques
            },
            "selected_paradigms": ["functional", "computational"],
        }

        state = retrieve_techniques(state)
        result = score_techniques(state)

        assert "technique_scores" in result

        # Should have scores for at least functional paradigm
        functional_scores = [
            k for k in result["technique_scores"].keys() if k.startswith("functional:")
        ]

        assert len(functional_scores) > 0
        # Computational may or may not have matches depending on prerequisites

    def test_score_with_high_matching_characteristics(self):
        """Test that matching characteristics result in higher scores."""
        state: Level2State = {
            "original_problem": "MapReduce problem",
            "problem_characteristics": {
                # Perfect match for MapReduce
                "operations_parallelizable": True,
                "large_dataset": True,
                "embarrassingly_parallel": True,
                "associative_reduction": True,
                "needs_aggregation": True,
            },
            "selected_paradigms": ["functional"],
        }

        state = retrieve_techniques(state)
        result = score_techniques(state)

        # Find MapReduce score
        mapreduce_score = None
        for key, score in result["technique_scores"].items():
            if "MapReduce" in key:
                mapreduce_score = score
                break

        assert mapreduce_score is not None
        assert mapreduce_score > 0.7  # Should have high score with perfect match

    def test_score_empty_candidates(self):
        """Test scoring with no candidate techniques."""
        state: Level2State = {
            "original_problem": "Problem",
            "problem_characteristics": {"problem_size": 100},
            "selected_paradigms": [],
            "candidate_techniques": {},
        }

        result = score_techniques(state)

        assert "technique_scores" in result
        assert len(result["technique_scores"]) == 0


class TestSelectTechniques:
    """Tests for the select_techniques node."""

    def test_select_best_technique(self):
        """Test selection of best technique per paradigm."""
        state: Level2State = {
            "original_problem": "Build a divide-and-conquer algorithm",
            "problem_characteristics": {
                "problem_size": 10000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "has_recursive_structure": True,
            },
            "selected_paradigms": ["structural"],
        }

        # Run through pipeline
        state = retrieve_techniques(state)
        state = score_techniques(state)
        result = select_techniques(state)

        assert "selected_techniques" in result
        assert "technique_justification" in result
        assert "structural" in result["selected_techniques"]

        # Check technique structure
        technique = result["selected_techniques"]["structural"]
        assert "name" in technique
        assert "paradigm" in technique
        assert "formal_definition" in technique
        assert "complexity" in technique
        assert "implementation_strategy" in technique
        assert "score" in technique

        # Check justification
        justification = result["technique_justification"]["structural"]
        assert len(justification) > 0
        assert "Technique Selection:" in justification
        assert "Formal Definition" in justification
        assert "Literature References" in justification

    def test_select_for_multiple_paradigms(self):
        """Test selection for multiple paradigms."""
        state: Level2State = {
            "original_problem": "Real-time parallel data processing",
            "problem_characteristics": {
                "large_dataset": True,
                "operations_parallelizable": True,
                "real_time_processing": True,
                "continuous_data_flow": True,
                "embarrassingly_parallel": True,
                "associative_reduction": True,
            },
            "selected_paradigms": ["functional", "temporal"],
        }

        state = retrieve_techniques(state)
        state = score_techniques(state)
        result = select_techniques(state)

        assert "selected_techniques" in result
        assert "functional" in result["selected_techniques"]
        assert "temporal" in result["selected_techniques"]

        # Both should have justifications
        assert "functional" in result["technique_justification"]
        assert "temporal" in result["technique_justification"]

    def test_select_handles_empty_candidates(self):
        """Test selection when no candidates exist."""
        state: Level2State = {
            "original_problem": "Problem",
            "problem_characteristics": {"problem_size": 100},
            "selected_paradigms": [],
            "candidate_techniques": {},
            "technique_scores": {},
        }

        result = select_techniques(state)

        assert "selected_techniques" in result
        assert "technique_justification" in result
        assert len(result["selected_techniques"]) == 0
        assert len(result["technique_justification"]) == 0

    def test_justification_includes_references(self):
        """Test that justifications include literature references."""
        state: Level2State = {
            "original_problem": "Sorting algorithm",
            "problem_characteristics": {
                "problem_size": 10000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "has_recursive_structure": True,
            },
            "selected_paradigms": ["structural"],
        }

        state = retrieve_techniques(state)
        state = score_techniques(state)
        result = select_techniques(state)

        justification = result["technique_justification"]["structural"]

        # Should contain literature section
        assert "Literature References" in justification
        # Should cite at least one paper/book
        assert any(
            ref in justification
            for ref in ["CLRS", "1970", "1980", "1990", "2000", "2010"]
        )

    def test_justification_includes_complexity(self):
        """Test that justifications include complexity analysis."""
        state: Level2State = {
            "original_problem": "Algorithm design",
            "problem_characteristics": {
                "problem_size": 5000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
            },
            "selected_paradigms": ["structural"],
        }

        state = retrieve_techniques(state)
        state = score_techniques(state)
        result = select_techniques(state)

        justification = result["technique_justification"]["structural"]

        # Should include complexity section
        assert "Complexity" in justification
        # Should mention Big-O notation
        assert "O(" in justification

    def test_selected_technique_has_score(self):
        """Test that selected techniques include their scores."""
        state: Level2State = {
            "original_problem": "Problem",
            "problem_characteristics": {
                "problem_size": 1000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
            },
            "selected_paradigms": ["structural"],
        }

        state = retrieve_techniques(state)
        state = score_techniques(state)
        result = select_techniques(state)

        technique = result["selected_techniques"]["structural"]
        assert "score" in technique
        assert isinstance(technique["score"], (int, float))
        assert 0.0 <= technique["score"] <= 1.0


class TestEndToEndPipeline:
    """Integration tests for the complete Level 2 pipeline."""

    def test_full_pipeline_single_paradigm(self):
        """Test complete pipeline with single paradigm."""
        state: Level2State = {
            "original_problem": "Design a sorting algorithm for 1 million records",
            "problem_characteristics": {
                "problem_size": 1_000_000,
                "problem_is_divisible": True,
                "subproblems_independent": True,
                "subproblems_same_type": True,
                "has_recursive_structure": True,
            },
            "selected_paradigms": ["structural"],
        }

        # Run full pipeline
        state = retrieve_techniques(state)
        assert "candidate_techniques" in state

        state = score_techniques(state)
        assert "technique_scores" in state

        state = select_techniques(state)
        assert "selected_techniques" in state
        assert "technique_justification" in state

        # Verify output structure
        assert len(state["selected_techniques"]) == 1
        assert "structural" in state["selected_techniques"]

    def test_full_pipeline_multiple_paradigms(self):
        """Test complete pipeline with multiple paradigms."""
        state: Level2State = {
            "original_problem": "Build a distributed data processing system with real-time analytics",
            "problem_characteristics": {
                "large_dataset": True,
                "operations_parallelizable": True,
                "embarrassingly_parallel": True,
                "real_time_processing": True,
                "continuous_data_flow": True,
                "associative_reduction": True,
                "needs_aggregation": True,
            },
            "selected_paradigms": ["functional", "temporal", "computational"],
        }

        # Run full pipeline
        state = retrieve_techniques(state)
        state = score_techniques(state)
        state = select_techniques(state)

        # Should have selected techniques for at least 2 paradigms
        assert len(state["selected_techniques"]) >= 2
        assert "functional" in state["selected_techniques"]
        assert "temporal" in state["selected_techniques"]

        # Each selected should have justification
        assert len(state["technique_justification"]) == len(state["selected_techniques"])

    def test_state_accumulation(self):
        """Test that state accumulates correctly through pipeline."""
        initial_state: Level2State = {
            "original_problem": "Test problem",
            "problem_characteristics": {
                "problem_size": 1000,
                "large_dataset": True,
            },
            "selected_paradigms": ["data"],
        }

        # Each step should preserve previous state
        state1 = retrieve_techniques(initial_state)
        assert state1["original_problem"] == initial_state["original_problem"]
        assert "candidate_techniques" in state1

        state2 = score_techniques(state1)
        assert "candidate_techniques" in state2
        assert "technique_scores" in state2

        state3 = select_techniques(state2)
        assert "candidate_techniques" in state3
        assert "technique_scores" in state3
        assert "selected_techniques" in state3
        assert "technique_justification" in state3
