"""
Tests for Level 2 utility functions.
"""

import pytest

from decomposition_pipeline.catalog.models import Technique, ApplicabilityRule
from decomposition_pipeline.graphs.level2_technique.utils import (
    generate_justification,
    format_technique_summary,
)


class TestGenerateJustification:
    """Tests for justification generation."""

    @pytest.fixture
    def sample_technique(self):
        """Create a sample technique for testing."""
        return Technique(
            name="Divide and Conquer",
            paradigm="structural",
            formal_definition="T(n) = aT(n/b) + f(n)",
            prerequisites=["problem_is_divisible", "subproblems_independent"],
            complexity="O(n log n) typical",
            applicability_rules=[
                ApplicabilityRule(
                    condition="problem_size > 1000",
                    score=0.8,
                    description="Large problems benefit from recursive division",
                ),
                ApplicabilityRule(
                    condition="has_recursive_structure == True",
                    score=0.9,
                    description="Recursive structure is ideal",
                ),
            ],
            literature_references=["CLRS Chapter 4", "Bentley 1986"],
            implementation_strategy="Recursively split, solve, merge",
        )

    def test_justification_structure(self, sample_technique):
        """Test that justification has correct structure."""
        characteristics = {
            "problem_size": 5000,
            "has_recursive_structure": True,
            "problem_is_divisible": True,
            "subproblems_independent": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.85,
            problem_characteristics=characteristics,
            original_problem="Test problem",
        )

        # Check for main sections
        assert "# Technique Selection: Divide and Conquer" in justification
        assert "## Applicability Score: 0.85" in justification
        assert "## Formal Definition" in justification
        assert "T(n) = aT(n/b) + f(n)" in justification
        assert "## Complexity" in justification
        assert "O(n log n)" in justification
        assert "## Why This Technique Was Selected" in justification
        assert "## Prerequisites Met" in justification
        assert "## Implementation Strategy" in justification
        assert "## Literature References" in justification
        assert "## Application to Current Problem" in justification

    def test_justification_includes_matching_rules(self, sample_technique):
        """Test that matching rules are included in justification."""
        characteristics = {
            "problem_size": 5000,  # Matches > 1000 rule
            "has_recursive_structure": True,  # Matches recursive rule
            "problem_is_divisible": True,
            "subproblems_independent": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.85,
            problem_characteristics=characteristics,
            original_problem="Test problem",
        )

        # Both rules should be mentioned
        assert "Large problems benefit from recursive division" in justification
        assert "Recursive structure is ideal" in justification
        assert "problem_size > 1000" in justification

    def test_justification_shows_prerequisites(self, sample_technique):
        """Test that prerequisites are shown with status."""
        characteristics = {
            "problem_size": 5000,
            "problem_is_divisible": True,
            "subproblems_independent": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.85,
            problem_characteristics=characteristics,
            original_problem="Test problem",
        )

        # Prerequisites should be listed
        assert "problem_is_divisible" in justification
        assert "subproblems_independent" in justification
        # Should show checkmarks for met prerequisites
        assert "✓" in justification

    def test_justification_includes_references(self, sample_technique):
        """Test that literature references are included."""
        characteristics = {
            "problem_size": 5000,
            "problem_is_divisible": True,
            "subproblems_independent": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.85,
            problem_characteristics=characteristics,
            original_problem="Test problem",
        )

        # References should be listed
        assert "CLRS Chapter 4" in justification
        assert "Bentley 1986" in justification

    def test_justification_includes_implementation_strategy(self, sample_technique):
        """Test that implementation strategy is included."""
        characteristics = {
            "problem_size": 5000,
            "problem_is_divisible": True,
            "subproblems_independent": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.85,
            problem_characteristics=characteristics,
            original_problem="Test problem",
        )

        assert "Recursively split, solve, merge" in justification

    def test_justification_problem_specific_reasoning(self, sample_technique):
        """Test that problem-specific reasoning is generated."""
        characteristics = {
            "problem_size": 5000,
            "problem_is_divisible": True,
            "subproblems_independent": True,
            "has_recursive_structure": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.85,
            problem_characteristics=characteristics,
            original_problem="Sort 5000 items efficiently",
        )

        # Should include problem-specific reasoning
        assert "Application to Current Problem" in justification
        # Should mention the problem
        assert "Sort 5000 items" in justification

    def test_justification_with_no_matching_rules(self, sample_technique):
        """Test justification when no rules match."""
        characteristics = {
            "problem_size": 100,  # Too small, doesn't match > 1000
            "has_recursive_structure": False,  # Doesn't match
            "problem_is_divisible": True,
            "subproblems_independent": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.0,
            problem_characteristics=characteristics,
            original_problem="Small problem",
        )

        # Should still generate justification
        assert len(justification) > 0
        assert "Technique Selection:" in justification

    def test_justification_handles_long_problem(self, sample_technique):
        """Test that long problems are truncated in justification."""
        long_problem = "A" * 500  # Very long problem description

        characteristics = {
            "problem_size": 5000,
            "problem_is_divisible": True,
            "subproblems_independent": True,
        }

        justification = generate_justification(
            technique=sample_technique,
            score=0.85,
            problem_characteristics=characteristics,
            original_problem=long_problem,
        )

        # Problem should be truncated
        assert "..." in justification
        # But justification should still be complete
        assert "Technique Selection:" in justification


class TestFormatTechniqueSummary:
    """Tests for technique summary formatting."""

    def test_format_summary(self):
        """Test basic summary formatting."""
        technique = Technique(
            name="MapReduce",
            paradigm="functional",
            formal_definition="map: (k1,v1) → list(k2,v2)",
            prerequisites=["large_dataset"],
            complexity="O(n/p) with p processors",
            applicability_rules=[],
            literature_references=["Dean & Ghemawat 2004"],
            implementation_strategy="Define map and reduce functions",
        )

        summary = format_technique_summary(technique, 0.92)

        assert "MapReduce" in summary
        assert "0.92" in summary
        assert "map: (k1,v1) → list(k2,v2)" in summary
        assert "O(n/p)" in summary

    def test_format_summary_structure(self):
        """Test that summary has expected structure."""
        technique = Technique(
            name="Test Technique",
            paradigm="test",
            formal_definition="Test definition",
            prerequisites=[],
            complexity="O(n)",
            applicability_rules=[],
            literature_references=[],
            implementation_strategy="Test strategy",
        )

        summary = format_technique_summary(technique, 0.75)

        # Should have name with score
        assert "Test Technique" in summary
        assert "Score: 0.75" in summary
        # Should have definition
        assert "Test definition" in summary
        # Should have complexity
        assert "Complexity: O(n)" in summary

    def test_format_summary_with_zero_score(self):
        """Test summary formatting with zero score."""
        technique = Technique(
            name="Low Score Technique",
            paradigm="test",
            formal_definition="Definition",
            prerequisites=[],
            complexity="O(1)",
            applicability_rules=[],
            literature_references=[],
            implementation_strategy="Strategy",
        )

        summary = format_technique_summary(technique, 0.0)

        assert "0.00" in summary or "0.0" in summary

    def test_format_summary_with_perfect_score(self):
        """Test summary formatting with perfect score."""
        technique = Technique(
            name="Perfect Technique",
            paradigm="test",
            formal_definition="Definition",
            prerequisites=[],
            complexity="O(1)",
            applicability_rules=[],
            literature_references=[],
            implementation_strategy="Strategy",
        )

        summary = format_technique_summary(technique, 1.0)

        assert "1.00" in summary or "1.0" in summary
