"""
Tests for Level 1: Paradigm Selection Subgraph.

Tests cover:
- Individual node functionality
- Graph integration
- Edge cases and error handling
- Conditional routing logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from decomposition_pipeline.graphs.level1_paradigm import (
    level1_paradigm_graph,
    characterize_problem,
    score_paradigms,
    select_paradigms,
    request_more_context,
)
from decomposition_pipeline.graphs.level1_paradigm.graph import should_request_more_context
from decomposition_pipeline.schemas import Level1State, ParadigmType


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_problem_state() -> Level1State:
    """Sample state with a problem description."""
    return Level1State(
        original_problem="Build a real-time collaborative text editor with conflict resolution",
        problem_characteristics={},
    )


@pytest.fixture
def characterized_state() -> Level1State:
    """State after characterization."""
    return Level1State(
        original_problem="Build a real-time collaborative text editor with conflict resolution",
        problem_characteristics={
            "problem_size": "large",
            "has_graph_structure": False,
            "has_hierarchy": True,
            "has_sequence": True,
            "parallelizable": True,
            "compute_intensive": False,
            "real_time": True,
            "distributed": True,
            "data_volume": "medium",
        },
    )


@pytest.fixture
def scored_state_high_scores() -> Level1State:
    """State with high paradigm scores."""
    return Level1State(
        original_problem="Build a real-time collaborative text editor",
        problem_characteristics={"real_time": True},
        paradigm_scores={
            "temporal": 0.85,
            "functional": 0.78,
            "data": 0.72,
            "structural": 0.45,
            "hierarchical": 0.35,
            "computational": 0.25,
            "spatial": 0.15,
            "dependency": 0.40,
        },
        candidate_paradigms=[
            {"paradigm": "temporal", "score": 0.85, "reasoning": "Real-time aspects", "key_indicators": []},
            {"paradigm": "functional", "score": 0.78, "reasoning": "Editor operations", "key_indicators": []},
            {"paradigm": "data", "score": 0.72, "reasoning": "Document storage", "key_indicators": []},
        ],
        paradigm_reasoning={
            "temporal": "Real-time synchronization needed",
            "functional": "Clear operations",
            "data": "Document storage requirements",
        },
    )


@pytest.fixture
def scored_state_low_scores() -> Level1State:
    """State with all low paradigm scores."""
    return Level1State(
        original_problem="Vague problem description",
        problem_characteristics={"problem_size": "unknown"},
        paradigm_scores={
            "temporal": 0.25,
            "functional": 0.22,
            "data": 0.18,
            "structural": 0.20,
            "hierarchical": 0.15,
            "computational": 0.12,
            "spatial": 0.10,
            "dependency": 0.19,
        },
        candidate_paradigms=[],
    )


# ============================================================================
# Node Tests
# ============================================================================

class TestCharacterizeProblem:
    """Tests for the characterize_problem node."""

    @patch("decomposition_pipeline.graphs.level1_paradigm.nodes.client")
    def test_successful_characterization(self, mock_client, sample_problem_state):
        """Test successful problem characterization."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"problem_size": "large", "has_graph_structure": false, "real_time": true}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        # Run characterization
        result = characterize_problem(sample_problem_state)

        # Verify characteristics were extracted
        assert "problem_characteristics" in result
        assert result["problem_characteristics"]["problem_size"] == "large"
        assert result["problem_characteristics"]["real_time"] is True

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

    @patch("decomposition_pipeline.graphs.level1_paradigm.nodes.client")
    def test_characterization_error_handling(self, mock_client, sample_problem_state):
        """Test error handling in characterization."""
        # Mock OpenAI error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Run characterization
        result = characterize_problem(sample_problem_state)

        # Verify default characteristics returned
        assert "problem_characteristics" in result
        assert "error" in result["problem_characteristics"]


class TestScoreParadigms:
    """Tests for the score_paradigms node."""

    @patch("decomposition_pipeline.graphs.level1_paradigm.nodes.client")
    def test_successful_scoring(self, mock_client, characterized_state):
        """Test successful paradigm scoring."""
        # Mock OpenAI responses for each paradigm
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content='{"score": 0.85, "reasoning": "Good fit", "key_indicators": ["real-time"]}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        # Run scoring
        result = score_paradigms(characterized_state)

        # Verify all paradigms were scored
        assert "paradigm_scores" in result
        assert len(result["paradigm_scores"]) == 8  # All 8 paradigms

        # Verify candidate paradigms are sorted
        assert "candidate_paradigms" in result
        assert len(result["candidate_paradigms"]) == 8

        # Verify reasoning was captured
        assert "paradigm_reasoning" in result

    @patch("decomposition_pipeline.graphs.level1_paradigm.nodes.client")
    def test_scoring_partial_failure(self, mock_client, characterized_state):
        """Test scoring when some paradigms fail."""
        # Mock successful and failed responses
        call_count = 0

        def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 4:
                # First 4 calls succeed
                mock_resp = Mock()
                mock_resp.choices = [
                    Mock(message=Mock(content='{"score": 0.7, "reasoning": "OK", "key_indicators": []}'))
                ]
                return mock_resp
            else:
                # Remaining calls fail
                raise Exception("API Error")

        mock_client.chat.completions.create.side_effect = mock_create

        # Run scoring
        result = score_paradigms(characterized_state)

        # Verify all paradigms have scores (even if 0.0 for failures)
        assert len(result["paradigm_scores"]) == 8
        assert "paradigm_reasoning" in result


class TestSelectParadigms:
    """Tests for the select_paradigms node."""

    def test_select_single_paradigm(self, scored_state_high_scores):
        """Test selecting a single high-scoring paradigm."""
        # Modify state to have only one paradigm above threshold
        state = {
            **scored_state_high_scores,
            "paradigm_scores": {
                "temporal": 0.85,
                "functional": 0.55,
                "data": 0.45,
                "structural": 0.30,
                "hierarchical": 0.25,
                "computational": 0.20,
                "spatial": 0.15,
                "dependency": 0.35,
            },
            "candidate_paradigms": [
                {"paradigm": "temporal", "score": 0.85, "reasoning": "Best fit", "key_indicators": []},
                {"paradigm": "functional", "score": 0.55, "reasoning": "Below threshold", "key_indicators": []},
            ],
        }

        result = select_paradigms(state)

        assert "selected_paradigms" in result
        assert len(result["selected_paradigms"]) == 1
        assert "temporal" in result["selected_paradigms"]

    def test_select_multiple_paradigms(self, scored_state_high_scores):
        """Test selecting multiple paradigms above threshold."""
        result = select_paradigms(scored_state_high_scores)

        assert "selected_paradigms" in result
        assert len(result["selected_paradigms"]) == 3  # temporal, functional, data
        assert "temporal" in result["selected_paradigms"]
        assert "functional" in result["selected_paradigms"]
        assert "data" in result["selected_paradigms"]

    def test_select_no_paradigms(self, scored_state_low_scores):
        """Test when no paradigms meet the threshold."""
        result = select_paradigms(scored_state_low_scores)

        assert "selected_paradigms" in result
        assert len(result["selected_paradigms"]) == 0

    def test_max_paradigms_limit(self):
        """Test that at most 3 paradigms are selected."""
        # Create state with 5 paradigms above threshold
        state = Level1State(
            original_problem="Complex problem",
            problem_characteristics={},
            paradigm_scores={
                "temporal": 0.95,
                "functional": 0.90,
                "data": 0.85,
                "structural": 0.80,
                "hierarchical": 0.75,
                "computational": 0.70,
                "spatial": 0.65,
                "dependency": 0.60,
            },
            candidate_paradigms=[
                {"paradigm": "temporal", "score": 0.95, "reasoning": "", "key_indicators": []},
                {"paradigm": "functional", "score": 0.90, "reasoning": "", "key_indicators": []},
                {"paradigm": "data", "score": 0.85, "reasoning": "", "key_indicators": []},
                {"paradigm": "structural", "score": 0.80, "reasoning": "", "key_indicators": []},
                {"paradigm": "hierarchical", "score": 0.75, "reasoning": "", "key_indicators": []},
            ],
        )

        result = select_paradigms(state)

        # Should select top 3 only
        assert len(result["selected_paradigms"]) == 3
        assert "temporal" in result["selected_paradigms"]
        assert "functional" in result["selected_paradigms"]
        assert "data" in result["selected_paradigms"]


class TestRequestMoreContext:
    """Tests for the request_more_context node."""

    def test_request_more_context(self, scored_state_low_scores):
        """Test requesting more context when scores are low."""
        result = request_more_context(scored_state_low_scores)

        assert "selected_paradigms" in result
        assert len(result["selected_paradigms"]) == 0

        assert "paradigm_reasoning" in result
        assert "_system_message" in result["paradigm_reasoning"]
        assert "more details" in result["paradigm_reasoning"]["_system_message"].lower()


# ============================================================================
# Conditional Routing Tests
# ============================================================================

class TestConditionalRouting:
    """Tests for the should_request_more_context routing function."""

    def test_route_to_select(self, scored_state_high_scores):
        """Test routing to select_paradigms when scores are sufficient."""
        result = should_request_more_context(scored_state_high_scores)
        assert result == "select"

    def test_route_to_request_context(self, scored_state_low_scores):
        """Test routing to request_more_context when scores are low."""
        result = should_request_more_context(scored_state_low_scores)
        assert result == "request_context"

    def test_route_with_no_scores(self):
        """Test routing when no scores are available."""
        state = Level1State(
            original_problem="Problem",
            problem_characteristics={},
        )
        result = should_request_more_context(state)
        assert result == "request_context"

    def test_route_boundary_score(self):
        """Test routing at the boundary (0.3 threshold)."""
        # Score exactly at 0.3 should go to select
        state = Level1State(
            original_problem="Problem",
            problem_characteristics={},
            paradigm_scores={"temporal": 0.3, "functional": 0.2},
        )
        result = should_request_more_context(state)
        assert result == "select"

        # Score just below 0.3 should request context
        state["paradigm_scores"] = {"temporal": 0.29, "functional": 0.2}
        result = should_request_more_context(state)
        assert result == "request_context"


# ============================================================================
# Graph Integration Tests
# ============================================================================

class TestGraphIntegration:
    """Integration tests for the full graph."""

    @patch("decomposition_pipeline.graphs.level1_paradigm.nodes.client")
    def test_full_graph_execution_success(self, mock_client):
        """Test full graph execution with successful paradigm selection."""
        # Mock characterization response
        char_response = Mock()
        char_response.choices = [
            Mock(message=Mock(content='{"problem_size": "large", "real_time": true, "parallelizable": true}'))
        ]

        # Mock scoring responses (high scores)
        score_response = Mock()
        score_response.choices = [
            Mock(message=Mock(content='{"score": 0.85, "reasoning": "Good fit", "key_indicators": ["real-time"]}'))
        ]

        # Alternate between responses
        mock_client.chat.completions.create.side_effect = [char_response] + [score_response] * 8

        # Initial state
        initial_state = Level1State(
            original_problem="Build a real-time collaborative text editor",
            problem_characteristics={},
        )

        # Execute graph
        result = level1_paradigm_graph.invoke(initial_state)

        # Verify final state
        assert "problem_characteristics" in result
        assert "paradigm_scores" in result
        assert "selected_paradigms" in result
        assert len(result["selected_paradigms"]) > 0

    @patch("decomposition_pipeline.graphs.level1_paradigm.nodes.client")
    def test_full_graph_execution_low_scores(self, mock_client):
        """Test full graph execution when scores are low."""
        # Mock characterization response
        char_response = Mock()
        char_response.choices = [
            Mock(message=Mock(content='{"problem_size": "unknown"}'))
        ]

        # Mock scoring responses (low scores)
        score_response = Mock()
        score_response.choices = [
            Mock(message=Mock(content='{"score": 0.2, "reasoning": "Poor fit", "key_indicators": []}'))
        ]

        mock_client.chat.completions.create.side_effect = [char_response] + [score_response] * 8

        # Initial state
        initial_state = Level1State(
            original_problem="Vague problem",
            problem_characteristics={},
        )

        # Execute graph
        result = level1_paradigm_graph.invoke(initial_state)

        # Verify request for more context
        assert "selected_paradigms" in result
        assert len(result["selected_paradigms"]) == 0
        assert "_system_message" in result.get("paradigm_reasoning", {})


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error scenarios."""

    def test_empty_problem(self):
        """Test handling of empty problem description."""
        state = Level1State(
            original_problem="",
            problem_characteristics={},
        )

        # Should not crash
        result = select_paradigms(state)
        assert "selected_paradigms" in result

    def test_missing_paradigm_scores(self):
        """Test selection when paradigm_scores is missing."""
        state = Level1State(
            original_problem="Problem",
            problem_characteristics={},
        )

        result = select_paradigms(state)
        assert "selected_paradigms" in result
        assert len(result["selected_paradigms"]) == 0

    @patch("decomposition_pipeline.graphs.level1_paradigm.nodes.client")
    def test_malformed_json_response(self, mock_client):
        """Test handling of malformed JSON from OpenAI."""
        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="invalid json"))]
        mock_client.chat.completions.create.return_value = mock_response

        state = Level1State(
            original_problem="Problem",
            problem_characteristics={},
        )

        # Should handle error gracefully
        result = characterize_problem(state)
        assert "problem_characteristics" in result
        assert "error" in result["problem_characteristics"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
