"""
Comprehensive tests for the Technique Catalog.

Tests cover:
- Technique model validation
- Applicability rule evaluation
- Catalog retrieval and scoring
- All 8 paradigms
- Edge cases and error handling
"""

import pytest

from decomposition_pipeline.catalog import (
    ApplicabilityRule,
    Technique,
    TechniqueCatalog,
    get_default_catalog,
)


class TestApplicabilityRule:
    """Test ApplicabilityRule model and evaluation."""

    def test_rule_creation(self) -> None:
        """Test creating an applicability rule."""
        rule = ApplicabilityRule(
            condition="problem_size > 1000",
            score=0.8,
            description="Large problems benefit",
        )
        assert rule.condition == "problem_size > 1000"
        assert rule.score == 0.8
        assert rule.description == "Large problems benefit"

    def test_rule_evaluation_true(self) -> None:
        """Test rule evaluation when condition is met."""
        rule = ApplicabilityRule(
            condition="problem_size > 1000",
            score=0.8,
            description="Test",
        )
        characteristics = {"problem_size": 5000}
        met, score = rule.evaluate(characteristics)
        assert met is True
        assert score == 0.8

    def test_rule_evaluation_false(self) -> None:
        """Test rule evaluation when condition is not met."""
        rule = ApplicabilityRule(
            condition="problem_size > 1000",
            score=0.8,
            description="Test",
        )
        characteristics = {"problem_size": 500}
        met, score = rule.evaluate(characteristics)
        assert met is False
        assert score == 0.0

    def test_rule_evaluation_boolean(self) -> None:
        """Test rule evaluation with boolean conditions."""
        rule = ApplicabilityRule(
            condition="has_graph_structure == True",
            score=0.9,
            description="Test",
        )
        characteristics = {"has_graph_structure": True}
        met, score = rule.evaluate(characteristics)
        assert met is True
        assert score == 0.9

    def test_rule_evaluation_missing_characteristic(self) -> None:
        """Test rule evaluation when characteristic is missing."""
        rule = ApplicabilityRule(
            condition="problem_size > 1000",
            score=0.8,
            description="Test",
        )
        characteristics = {}
        met, score = rule.evaluate(characteristics)
        assert met is False
        assert score == 0.0

    def test_rule_validation_score_range(self) -> None:
        """Test that score must be between 0.0 and 1.0."""
        with pytest.raises(Exception):  # Pydantic validation error
            ApplicabilityRule(
                condition="test",
                score=1.5,  # Invalid score
                description="Test",
            )


class TestTechnique:
    """Test Technique model and methods."""

    def test_technique_creation(self) -> None:
        """Test creating a technique."""
        technique = Technique(
            name="Test Technique",
            paradigm="structural",
            formal_definition="Test definition",
            prerequisites=["prereq1", "prereq2"],
            complexity="O(n)",
            applicability_rules=[],
            literature_references=["Reference 1"],
            implementation_strategy="Test strategy",
        )
        assert technique.name == "Test Technique"
        assert technique.paradigm == "structural"
        assert len(technique.prerequisites) == 2

    def test_check_prerequisites_all_met(self) -> None:
        """Test prerequisite checking when all are met."""
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=["prereq1", "prereq2"],
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        characteristics = {"prereq1": True, "prereq2": True}
        assert technique.check_prerequisites(characteristics) is True

    def test_check_prerequisites_not_met(self) -> None:
        """Test prerequisite checking when some are not met."""
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=["prereq1", "prereq2"],
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        characteristics = {"prereq1": True, "prereq2": False}
        assert technique.check_prerequisites(characteristics) is False

    def test_check_prerequisites_missing(self) -> None:
        """Test prerequisite checking when characteristic is missing."""
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=["prereq1", "prereq2"],
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        characteristics = {"prereq1": True}  # prereq2 missing
        assert technique.check_prerequisites(characteristics) is False

    def test_score_applicability_no_rules(self) -> None:
        """Test scoring when no rules are defined."""
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            applicability_rules=[],
            literature_references=[],
            implementation_strategy="Test",
        )
        characteristics = {}
        score = technique.score_applicability(characteristics)
        assert score == 0.5  # Default score

    def test_score_applicability_with_rules(self) -> None:
        """Test scoring with multiple rules."""
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            applicability_rules=[
                ApplicabilityRule(
                    condition="problem_size > 1000",
                    score=0.8,
                    description="Test",
                ),
                ApplicabilityRule(
                    condition="has_structure == True",
                    score=0.9,
                    description="Test",
                ),
            ],
            literature_references=[],
            implementation_strategy="Test",
        )
        characteristics = {
            "problem_size": 5000,
            "has_structure": True,
        }
        score = technique.score_applicability(characteristics)
        assert score == pytest.approx(0.85)  # Average of 0.8 and 0.9

    def test_score_applicability_partial_match(self) -> None:
        """Test scoring when only some rules match."""
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            applicability_rules=[
                ApplicabilityRule(
                    condition="problem_size > 1000",
                    score=0.8,
                    description="Test",
                ),
                ApplicabilityRule(
                    condition="has_structure == True",
                    score=0.9,
                    description="Test",
                ),
            ],
            literature_references=[],
            implementation_strategy="Test",
        )
        characteristics = {
            "problem_size": 500,  # Doesn't meet first rule
            "has_structure": True,
        }
        score = technique.score_applicability(characteristics)
        assert score == 0.9  # Only second rule matches


class TestTechniqueCatalog:
    """Test TechniqueCatalog functionality."""

    def test_catalog_creation(self) -> None:
        """Test creating an empty catalog."""
        catalog = TechniqueCatalog()
        assert len(catalog.techniques) == 0
        assert catalog.version == "1.0.0"

    def test_add_technique(self) -> None:
        """Test adding a technique to the catalog."""
        catalog = TechniqueCatalog()
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        catalog.add_technique(technique)
        assert len(catalog.techniques["structural"]) == 1
        assert catalog.techniques["structural"][0].name == "Test"

    def test_get_paradigms(self) -> None:
        """Test getting list of paradigms."""
        catalog = TechniqueCatalog()
        technique1 = Technique(
            name="T1",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        technique2 = Technique(
            name="T2",
            paradigm="functional",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        catalog.add_technique(technique1)
        catalog.add_technique(technique2)
        paradigms = catalog.get_paradigms()
        assert set(paradigms) == {"structural", "functional"}

    def test_get_techniques_for_paradigm(self) -> None:
        """Test getting techniques for a specific paradigm."""
        catalog = TechniqueCatalog()
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        catalog.add_technique(technique)
        techniques = catalog.get_techniques_for_paradigm("structural")
        assert len(techniques) == 1
        assert techniques[0].name == "Test"

    def test_get_techniques_for_nonexistent_paradigm(self) -> None:
        """Test getting techniques for paradigm with no techniques."""
        catalog = TechniqueCatalog()
        techniques = catalog.get_techniques_for_paradigm("nonexistent")
        assert len(techniques) == 0

    def test_get_applicable_techniques(self) -> None:
        """Test getting applicable techniques sorted by score."""
        catalog = TechniqueCatalog()

        # Add two techniques with different applicability
        tech1 = Technique(
            name="Tech1",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=["prereq1"],
            complexity="O(n)",
            applicability_rules=[
                ApplicabilityRule(
                    condition="score_high == True",
                    score=0.9,
                    description="Test",
                ),
            ],
            literature_references=[],
            implementation_strategy="Test",
        )
        tech2 = Technique(
            name="Tech2",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=["prereq1"],
            complexity="O(n)",
            applicability_rules=[
                ApplicabilityRule(
                    condition="score_low == True",
                    score=0.5,
                    description="Test",
                ),
            ],
            literature_references=[],
            implementation_strategy="Test",
        )

        catalog.add_technique(tech1)
        catalog.add_technique(tech2)

        characteristics = {
            "prereq1": True,
            "score_high": True,
            "score_low": True,
        }

        results = catalog.get_applicable_techniques("structural", characteristics)
        assert len(results) == 2
        # Should be sorted by score descending
        assert results[0][0].name == "Tech1"
        assert results[0][1] == 0.9
        assert results[1][0].name == "Tech2"
        assert results[1][1] == 0.5

    def test_get_applicable_techniques_filters_by_prerequisites(self) -> None:
        """Test that techniques without met prerequisites are filtered."""
        catalog = TechniqueCatalog()

        tech = Technique(
            name="Tech",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=["missing_prereq"],
            complexity="O(n)",
            applicability_rules=[
                ApplicabilityRule(
                    condition="always_true == True",
                    score=0.9,
                    description="Test",
                ),
            ],
            literature_references=[],
            implementation_strategy="Test",
        )

        catalog.add_technique(tech)

        characteristics = {
            "always_true": True,
            # missing_prereq not provided
        }

        results = catalog.get_applicable_techniques("structural", characteristics)
        assert len(results) == 0  # Filtered due to unmet prerequisite

    def test_get_best_technique(self) -> None:
        """Test getting the single best technique."""
        catalog = TechniqueCatalog()

        tech1 = Technique(
            name="Best",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=[],
            complexity="O(n)",
            applicability_rules=[
                ApplicabilityRule(
                    condition="always_true == True",
                    score=0.95,
                    description="Test",
                ),
            ],
            literature_references=[],
            implementation_strategy="Test",
        )
        tech2 = Technique(
            name="Second",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=[],
            complexity="O(n)",
            applicability_rules=[
                ApplicabilityRule(
                    condition="always_true == True",
                    score=0.7,
                    description="Test",
                ),
            ],
            literature_references=[],
            implementation_strategy="Test",
        )

        catalog.add_technique(tech1)
        catalog.add_technique(tech2)

        characteristics = {"always_true": True}
        result = catalog.get_best_technique("structural", characteristics)

        assert result is not None
        technique, score = result
        assert technique.name == "Best"
        assert score == 0.95

    def test_get_best_technique_none_applicable(self) -> None:
        """Test getting best technique when none are applicable."""
        catalog = TechniqueCatalog()

        tech = Technique(
            name="Tech",
            paradigm="structural",
            formal_definition="Test",
            prerequisites=["missing"],
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )

        catalog.add_technique(tech)
        characteristics = {}
        result = catalog.get_best_technique("structural", characteristics)
        assert result is None

    def test_catalog_serialization(self) -> None:
        """Test converting catalog to dict and back."""
        catalog = TechniqueCatalog()
        technique = Technique(
            name="Test",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=["Ref1"],
            implementation_strategy="Test",
        )
        catalog.add_technique(technique)

        # Convert to dict
        data = catalog.to_dict()
        assert "version" in data
        assert "techniques" in data
        assert "structural" in data["techniques"]

        # Load from dict
        loaded = TechniqueCatalog.from_dict(data)
        assert loaded.version == catalog.version
        assert len(loaded.techniques["structural"]) == 1
        assert loaded.techniques["structural"][0].name == "Test"

    def test_get_statistics(self) -> None:
        """Test getting catalog statistics."""
        catalog = TechniqueCatalog()
        tech1 = Technique(
            name="T1",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        tech2 = Technique(
            name="T2",
            paradigm="structural",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )
        tech3 = Technique(
            name="T3",
            paradigm="functional",
            formal_definition="Test",
            complexity="O(n)",
            literature_references=[],
            implementation_strategy="Test",
        )

        catalog.add_technique(tech1)
        catalog.add_technique(tech2)
        catalog.add_technique(tech3)

        stats = catalog.get_statistics()
        assert stats["total_paradigms"] == 2
        assert stats["total_techniques"] == 3
        assert stats["techniques_per_paradigm"]["structural"] == 2
        assert stats["techniques_per_paradigm"]["functional"] == 1


class TestDefaultCatalog:
    """Test the default pre-populated catalog."""

    def test_default_catalog_creation(self) -> None:
        """Test that default catalog can be created."""
        catalog = get_default_catalog()
        assert isinstance(catalog, TechniqueCatalog)

    def test_all_paradigms_present(self) -> None:
        """Test that all 8 paradigms are present in default catalog."""
        catalog = get_default_catalog()
        paradigms = catalog.get_paradigms()

        expected_paradigms = {
            "structural",
            "functional",
            "temporal",
            "spatial",
            "hierarchical",
            "computational",
            "data",
            "dependency",
        }

        assert set(paradigms) == expected_paradigms

    def test_minimum_techniques_per_paradigm(self) -> None:
        """Test that each paradigm has at least 3 techniques."""
        catalog = get_default_catalog()
        stats = catalog.get_statistics()

        for paradigm, count in stats["techniques_per_paradigm"].items():
            assert count >= 3, f"Paradigm {paradigm} has only {count} techniques"

    def test_total_technique_count(self) -> None:
        """Test that catalog has at least 24 techniques total."""
        catalog = get_default_catalog()
        stats = catalog.get_statistics()
        assert stats["total_techniques"] >= 24

    def test_structural_techniques(self) -> None:
        """Test specific structural techniques are present."""
        catalog = get_default_catalog()
        techniques = catalog.get_techniques_for_paradigm("structural")
        names = {t.name for t in techniques}

        assert "Divide and Conquer" in names
        assert "Graph Partitioning" in names
        assert "Tree Decomposition" in names

    def test_functional_techniques(self) -> None:
        """Test specific functional techniques are present."""
        catalog = get_default_catalog()
        techniques = catalog.get_techniques_for_paradigm("functional")
        names = {t.name for t in techniques}

        assert "MapReduce" in names
        assert "Fork-Join Pattern" in names
        assert "Pipeline Decomposition" in names

    def test_all_techniques_have_references(self) -> None:
        """Test that all techniques have literature references."""
        catalog = get_default_catalog()
        for paradigm in catalog.get_paradigms():
            techniques = catalog.get_techniques_for_paradigm(paradigm)
            for technique in techniques:
                assert (
                    len(technique.literature_references) > 0
                ), f"Technique {technique.name} has no references"

    def test_all_techniques_have_complexity(self) -> None:
        """Test that all techniques have complexity analysis."""
        catalog = get_default_catalog()
        for paradigm in catalog.get_paradigms():
            techniques = catalog.get_techniques_for_paradigm(paradigm)
            for technique in techniques:
                assert (
                    technique.complexity
                ), f"Technique {technique.name} has no complexity"

    def test_all_techniques_have_formal_definition(self) -> None:
        """Test that all techniques have formal definitions."""
        catalog = get_default_catalog()
        for paradigm in catalog.get_paradigms():
            techniques = catalog.get_techniques_for_paradigm(paradigm)
            for technique in techniques:
                assert (
                    technique.formal_definition
                ), f"Technique {technique.name} has no formal definition"

    def test_divide_and_conquer_retrieval(self) -> None:
        """Test retrieving Divide and Conquer with appropriate characteristics."""
        catalog = get_default_catalog()

        characteristics = {
            "problem_is_divisible": True,
            "subproblems_independent": True,
            "subproblems_same_type": True,
            "problem_size": 10000,
            "has_recursive_structure": True,
        }

        results = catalog.get_applicable_techniques("structural", characteristics)
        names = [t[0].name for t in results]
        assert "Divide and Conquer" in names

        # Check that it scores highly
        for technique, score in results:
            if technique.name == "Divide and Conquer":
                assert score > 0.8

    def test_mapreduce_retrieval(self) -> None:
        """Test retrieving MapReduce with appropriate characteristics."""
        catalog = get_default_catalog()

        characteristics = {
            "operations_parallelizable": True,
            "associative_reduction": True,
            "large_dataset": True,
            "embarrassingly_parallel": True,
            "needs_aggregation": True,
        }

        results = catalog.get_applicable_techniques("functional", characteristics)
        names = [t[0].name for t in results]
        assert "MapReduce" in names

        # Check that it scores highly
        for technique, score in results:
            if technique.name == "MapReduce":
                assert score > 0.85

    def test_event_sourcing_retrieval(self) -> None:
        """Test retrieving Event Sourcing with appropriate characteristics."""
        catalog = get_default_catalog()

        characteristics = {
            "state_changes_trackable": True,
            "events_ordered": True,
            "immutable_events": True,
            "audit_trail_needed": True,
            "temporal_queries_required": True,
        }

        results = catalog.get_applicable_techniques("temporal", characteristics)
        names = [t[0].name for t in results]
        assert "Event Sourcing" in names

    def test_prerequisite_filtering(self) -> None:
        """Test that prerequisites properly filter techniques."""
        catalog = get_default_catalog()

        # Try to get Graph Partitioning without required prerequisites
        characteristics = {
            "problem_size": 10000,
            # Missing: problem_is_graph, nodes_identifiable, relationships_explicit
        }

        results = catalog.get_applicable_techniques("structural", characteristics)
        names = [t[0].name for t in results]

        # Graph Partitioning should be filtered out
        assert "Graph Partitioning" not in names


class TestIntegrationScenarios:
    """Integration tests for realistic usage scenarios."""

    def test_large_graph_problem(self) -> None:
        """Test technique selection for large graph problem."""
        catalog = get_default_catalog()

        characteristics = {
            "problem_is_graph": True,
            "nodes_identifiable": True,
            "relationships_explicit": True,
            "has_network_structure": True,
            "minimize_dependencies": True,
            "problem_size": 50000,
        }

        result = catalog.get_best_technique("structural", characteristics)
        assert result is not None
        technique, score = result
        assert technique.name == "Graph Partitioning"
        assert score > 0.8

    def test_parallel_data_processing(self) -> None:
        """Test technique selection for parallel data processing."""
        catalog = get_default_catalog()

        characteristics = {
            "operations_parallelizable": True,
            "associative_reduction": True,
            "large_dataset": True,
            "embarrassingly_parallel": True,
            "needs_aggregation": True,
        }

        result = catalog.get_best_technique("functional", characteristics)
        assert result is not None
        technique, score = result
        assert technique.name == "MapReduce"

    def test_real_time_streaming(self) -> None:
        """Test technique selection for real-time streaming."""
        catalog = get_default_catalog()

        characteristics = {
            "continuous_data_flow": True,
            "real_time_processing": True,
            "low_latency_required": True,
        }

        result = catalog.get_best_technique("temporal", characteristics)
        assert result is not None
        technique, score = result
        assert technique.name == "Stream Processing"

    def test_database_sharding(self) -> None:
        """Test technique selection for database sharding."""
        catalog = get_default_catalog()

        characteristics = {
            "tabular_data": True,
            "partition_key_exists": True,
            "large_dataset": True,
            "locality_of_access": True,
        }

        result = catalog.get_best_technique("data", characteristics)
        assert result is not None
        technique, score = result
        assert technique.name == "Horizontal Partitioning"

    def test_dependency_graph_scheduling(self) -> None:
        """Test technique selection for dependency graph scheduling."""
        catalog = get_default_catalog()

        characteristics = {
            "dependency_graph_is_dag": True,
            "dependencies_explicit": True,
            "task_durations_known": True,
            "optimize_makespan": True,
        }

        results = catalog.get_applicable_techniques("dependency", characteristics)
        names = [t[0].name for t in results]

        # Both techniques should be applicable
        assert "Topological Sort" in names
        assert "Critical Path Method" in names

        # Get the best technique (either is acceptable with these characteristics)
        result = catalog.get_best_technique("dependency", characteristics)
        assert result is not None
        technique, score = result
        # Both techniques are valid for DAG scheduling
        assert technique.name in ["Topological Sort", "Critical Path Method"]
        # Score should be high
        assert score >= 0.9
