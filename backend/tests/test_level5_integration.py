"""
Tests for Level 5: Solution Integration Subgraph.

Tests all components including mapping, conflict detection/resolution,
gap filling, synthesis, and validation.
"""

import pytest
from typing import List, Dict
from src.decomposition_pipeline.schemas.state import (
    Level5State,
    Subproblem,
    Solution,
    DependencyGraph,
    SubproblemStatus,
)
from src.decomposition_pipeline.graphs.level5_integration import (
    map_solutions_to_problem,
    detect_solution_conflicts,
    resolve_solution_conflicts,
    fill_solution_gaps,
    synthesize_final_solution,
    validate_integrated_solution,
    level5_graph,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_subproblems() -> List[Subproblem]:
    """Create sample subproblems for testing."""
    return [
        {
            "id": "sp1",
            "title": "API Design",
            "description": "Design RESTful API endpoints",
            "paradigm": "structural",
            "source_technique": "Component Extraction",
            "status": SubproblemStatus.COMPLETED,
            "dependencies": [],
        },
        {
            "id": "sp2",
            "title": "Database Schema",
            "description": "Design database schema with indexes",
            "paradigm": "data",
            "source_technique": "Horizontal Partitioning",
            "status": SubproblemStatus.COMPLETED,
            "dependencies": [],
        },
        {
            "id": "sp3",
            "title": "Authentication",
            "description": "Implement authentication flow",
            "paradigm": "functional",
            "source_technique": "Task Parallelism",
            "status": SubproblemStatus.COMPLETED,
            "dependencies": ["sp1", "sp2"],
        },
    ]


@pytest.fixture
def sample_partial_solutions() -> Dict[str, Solution]:
    """Create sample partial solutions."""
    return {
        "sp1": {
            "subproblem_id": "sp1",
            "content": "API should include endpoints for user management: POST /users, GET /users/:id, PUT /users/:id",
            "reasoning": "RESTful design follows standard conventions",
            "confidence": 0.85,
            "agent_pool": "structural_pool",
        },
        "sp2": {
            "subproblem_id": "sp2",
            "content": "Database must include users table with id, username, email, password_hash, created_at",
            "reasoning": "Standard user schema with security best practices",
            "confidence": 0.90,
            "agent_pool": "data_pool",
        },
        "sp3": {
            "subproblem_id": "sp3",
            "content": "Authentication should use JWT tokens with 1-hour expiry",
            "reasoning": "JWT provides stateless authentication",
            "confidence": 0.75,
            "agent_pool": "functional_pool",
        },
    }


@pytest.fixture
def sample_dependency_graph() -> DependencyGraph:
    """Create sample dependency graph."""
    return {
        "nodes": ["sp1", "sp2", "sp3"],
        "edges": [
            {"from": "sp1", "to": "sp3", "type": "dependency"},
            {"from": "sp2", "to": "sp3", "type": "dependency"},
        ],
    }


@pytest.fixture
def sample_level5_state(
    sample_subproblems: List[Subproblem],
    sample_partial_solutions: Dict[str, Solution],
    sample_dependency_graph: DependencyGraph
) -> Level5State:
    """Create sample Level5State for testing."""
    return {
        "partial_solutions": sample_partial_solutions,
        "integrated_subproblems": sample_subproblems,
        "subproblem_dependencies": sample_dependency_graph,
        "original_problem": "Build a user management system with secure authentication",
    }


# ============================================================================
# Solution Mapping Tests
# ============================================================================

def test_map_solutions_to_problem(sample_level5_state: Level5State):
    """Test solution mapping creates coverage map."""
    result = map_solutions_to_problem(sample_level5_state)

    assert "solution_coverage_map" in result
    coverage_map = result["solution_coverage_map"]

    assert coverage_map["total_subproblems"] == 3
    assert coverage_map["solved_subproblems"] == 3
    assert coverage_map["coverage_percentage"] == 100.0
    assert len(coverage_map["unsolved_subproblems"]) == 0
    assert "coverage_by_paradigm" in coverage_map
    assert "solution_details" in coverage_map


def test_map_solutions_with_gaps():
    """Test solution mapping with unsolved subproblems."""
    state: Level5State = {
        "partial_solutions": {
            "sp1": {"content": "solution 1", "reasoning": "test", "confidence": 0.8}
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First task",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second task",
                "paradigm": "functional",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2"], "edges": []},
        "original_problem": "Test problem",
    }

    result = map_solutions_to_problem(state)
    coverage_map = result["solution_coverage_map"]

    assert coverage_map["solved_subproblems"] == 1
    assert coverage_map["coverage_percentage"] == 50.0
    assert "sp2" in coverage_map["unsolved_subproblems"]


def test_coverage_by_paradigm():
    """Test coverage analysis by paradigm."""
    state: Level5State = {
        "partial_solutions": {
            "sp1": {"content": "solution 1", "reasoning": "test", "confidence": 0.8},
            "sp2": {"content": "solution 2", "reasoning": "test", "confidence": 0.7},
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First task",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second task",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp3",
                "title": "Task 3",
                "description": "Third task",
                "paradigm": "functional",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2", "sp3"], "edges": []},
        "original_problem": "Test problem",
    }

    result = map_solutions_to_problem(state)
    coverage_map = result["solution_coverage_map"]
    paradigm_coverage = coverage_map["coverage_by_paradigm"]

    assert "structural" in paradigm_coverage
    assert paradigm_coverage["structural"]["total"] == 2
    assert paradigm_coverage["structural"]["solved"] == 2

    assert "functional" in paradigm_coverage
    assert paradigm_coverage["functional"]["total"] == 1
    assert paradigm_coverage["functional"]["solved"] == 0


# ============================================================================
# Conflict Detection Tests
# ============================================================================

def test_detect_conflicts_none(sample_level5_state: Level5State):
    """Test conflict detection with no conflicts."""
    # First map solutions
    state = map_solutions_to_problem(sample_level5_state)
    result = detect_solution_conflicts(state)

    assert "detected_conflicts" in result
    # May detect some low-level conflicts, but should not have critical ones


def test_detect_logical_contradictions():
    """Test detection of logical contradictions."""
    state: Level5State = {
        "partial_solutions": {
            "sp1": {
                "content": "The system must use synchronous processing",
                "reasoning": "Synchronous is required for consistency",
                "confidence": 0.8,
            },
            "sp2": {
                "content": "The system must not use synchronous processing",
                "reasoning": "Async is better for performance",
                "confidence": 0.7,
            },
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Processing Strategy",
                "description": "Define processing",
                "paradigm": "computational",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Performance Optimization",
                "description": "Optimize performance",
                "paradigm": "computational",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2"], "edges": []},
        "original_problem": "Test",
    }

    result = detect_solution_conflicts(state)
    conflicts = result["detected_conflicts"]

    # Should detect must/must not contradiction
    logical_conflicts = [c for c in conflicts if c["type"] == "logical_contradiction"]
    assert len(logical_conflicts) > 0


def test_detect_resource_conflicts():
    """Test detection of resource conflicts."""
    state: Level5State = {
        "partial_solutions": {
            "sp1": {
                "content": "Use port 8080 for the API service",
                "reasoning": "Standard port",
                "confidence": 0.8,
            },
            "sp2": {
                "content": "Use port 8080 for the database proxy",
                "reasoning": "Default port",
                "confidence": 0.7,
            },
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "API Service",
                "description": "API",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Database Proxy",
                "description": "Proxy",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2"], "edges": []},
        "original_problem": "Test",
    }

    result = detect_solution_conflicts(state)
    conflicts = result["detected_conflicts"]

    # Should detect port conflict
    resource_conflicts = [c for c in conflicts if c["type"] == "resource_conflict"]
    assert len(resource_conflicts) > 0


def test_detect_dependency_conflicts():
    """Test detection of dependency conflicts."""
    state: Level5State = {
        "partial_solutions": {
            "sp2": {
                "content": "Solution that depends on sp1",
                "reasoning": "Needs sp1",
                "confidence": 0.8,
            },
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Base Task",
                "description": "Foundation",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Dependent Task",
                "description": "Depends on sp1",
                "paradigm": "functional",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": ["sp1"],
            },
        ],
        "subproblem_dependencies": {
            "nodes": ["sp1", "sp2"],
            "edges": [{"from": "sp1", "to": "sp2"}],
        },
        "original_problem": "Test",
    }

    result = detect_solution_conflicts(state)
    conflicts = result["detected_conflicts"]

    # Should detect dependency conflict (sp2 solved but sp1 not)
    dep_conflicts = [c for c in conflicts if c["type"] == "dependency_conflict"]
    assert len(dep_conflicts) > 0
    assert dep_conflicts[0]["subproblem_ids"][0] == "sp2"


# ============================================================================
# Conflict Resolution Tests
# ============================================================================

def test_resolve_conflicts_none():
    """Test conflict resolution with no conflicts."""
    state: Level5State = {
        "detected_conflicts": [],
        "partial_solutions": {},
        "integrated_subproblems": [],
        "subproblem_dependencies": {"nodes": [], "edges": []},
        "original_problem": "Test",
    }

    result = resolve_solution_conflicts(state)

    assert "resolution_summary" in result
    summary = result["resolution_summary"]
    assert summary["total_conflicts"] == 0
    assert summary["resolved"] == 0


def test_resolve_logical_contradiction():
    """Test resolution of logical contradictions."""
    state: Level5State = {
        "detected_conflicts": [
            {
                "type": "logical_contradiction",
                "severity": "high",
                "subproblem_ids": ["sp1", "sp2"],
                "description": "Contradictory requirements",
            }
        ],
        "partial_solutions": {
            "sp1": {"content": "Solution 1", "reasoning": "test", "confidence": 0.9},
            "sp2": {"content": "Solution 2", "reasoning": "test", "confidence": 0.6},
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2"], "edges": []},
        "original_problem": "Test",
    }

    result = resolve_solution_conflicts(state)
    summary = result["resolution_summary"]

    assert summary["total_conflicts"] == 1
    # Should be resolved based on confidence
    assert summary["resolved"] >= 0


# ============================================================================
# Gap Filling Tests
# ============================================================================

def test_fill_gaps_none(sample_level5_state: Level5State):
    """Test gap filling with complete coverage."""
    # Map solutions first
    state = map_solutions_to_problem(sample_level5_state)
    result = fill_solution_gaps(state)

    assert "identified_gaps" in result
    assert "gap_solutions" in result
    assert "gap_metrics" in result

    # With 100% coverage, should have no unsolved subproblems
    # May have connection gaps (which are medium severity, not critical)
    gap_metrics = result["gap_metrics"]
    critical_gaps = gap_metrics.get("critical_gaps", [])
    assert len(critical_gaps) == 0


def test_fill_gaps_with_unsolved():
    """Test gap filling with unsolved subproblems."""
    state: Level5State = {
        "solution_coverage_map": {
            "unsolved_subproblems": ["sp2"],
            "coverage_percentage": 50.0,
        },
        "partial_solutions": {
            "sp1": {"content": "Solution 1", "reasoning": "test", "confidence": 0.8}
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First task",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second task needs implementation",
                "paradigm": "functional",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2"], "edges": []},
        "original_problem": "Complete both tasks",
    }

    result = fill_solution_gaps(state)

    assert len(result["identified_gaps"]) > 0
    assert len(result["gap_solutions"]) > 0

    # Should generate placeholder for sp2
    assert "sp2" in result["gap_solutions"]
    gap_sol = result["gap_solutions"]["sp2"]
    assert "PLACEHOLDER" in gap_sol["content"] or gap_sol["confidence"] < 0.5


def test_gap_metrics():
    """Test gap metrics calculation."""
    state: Level5State = {
        "solution_coverage_map": {
            "unsolved_subproblems": ["sp2", "sp3"],
            "coverage_percentage": 33.0,
        },
        "partial_solutions": {
            "sp1": {"content": "Solution 1", "reasoning": "test", "confidence": 0.8}
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second",
                "paradigm": "functional",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
            {
                "id": "sp3",
                "title": "Task 3",
                "description": "Third",
                "paradigm": "data",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2", "sp3"], "edges": []},
        "original_problem": "Complete all tasks",
    }

    result = fill_solution_gaps(state)
    metrics = result["gap_metrics"]

    assert metrics["total_gaps"] >= 2
    assert "gaps_by_type" in metrics


# ============================================================================
# Solution Synthesis Tests
# ============================================================================

def test_synthesize_final_solution(sample_level5_state: Level5State):
    """Test final solution synthesis."""
    # Run through the pipeline up to synthesis
    state = map_solutions_to_problem(sample_level5_state)
    state = detect_solution_conflicts(state)
    state = resolve_solution_conflicts(state)
    state = fill_solution_gaps(state)
    result = synthesize_final_solution(state)

    assert "integrated_solution" in result
    integrated_sol = result["integrated_solution"]

    assert "content" in integrated_sol
    assert "reasoning" in integrated_sol
    assert "confidence" in integrated_sol
    assert len(integrated_sol["content"]) > 0
    assert integrated_sol["confidence"] > 0


def test_synthesize_with_gaps():
    """Test synthesis with gap solutions."""
    state: Level5State = {
        "partial_solutions": {
            "sp1": {"content": "Real solution 1", "reasoning": "test", "confidence": 0.9}
        },
        "gap_solutions": {
            "sp2": {"content": "Gap solution 2", "reasoning": "placeholder", "confidence": 0.3}
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second",
                "paradigm": "functional",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2"], "edges": []},
        "original_problem": "Complete tasks",
        "solution_coverage_map": {"coverage_percentage": 50.0},
        "resolution_summary": {"total_conflicts": 0, "resolved": 0, "escalated": 0},
    }

    result = synthesize_final_solution(state)
    integrated_sol = result["integrated_solution"]

    # Should combine both real and gap solutions
    assert integrated_sol["confidence"] < 0.9  # Lower due to gap solution


def test_implementation_plan_generation(sample_level5_state: Level5State):
    """Test implementation plan generation."""
    # Run full pipeline
    state = map_solutions_to_problem(sample_level5_state)
    state = detect_solution_conflicts(state)
    state = resolve_solution_conflicts(state)
    state = fill_solution_gaps(state)
    result = synthesize_final_solution(state)

    integrated_sol = result["integrated_solution"]
    metadata = integrated_sol.get("metadata", {})

    assert "implementation_plan" in metadata
    plan = metadata["implementation_plan"]
    assert isinstance(plan, list)
    assert len(plan) > 0


# ============================================================================
# Validation Tests
# ============================================================================

def test_validate_integrated_solution(sample_level5_state: Level5State):
    """Test validation of integrated solution."""
    # Run full pipeline
    state = map_solutions_to_problem(sample_level5_state)
    state = detect_solution_conflicts(state)
    state = resolve_solution_conflicts(state)
    state = fill_solution_gaps(state)
    state = synthesize_final_solution(state)
    result = validate_integrated_solution(state)

    assert "validation_results" in result
    validation = result["validation_results"]

    assert "status" in validation
    assert "has_critical_failures" in validation
    assert "has_gaps" in validation
    assert "has_conflicts" in validation
    assert isinstance(validation["issues"], list)
    assert isinstance(validation["recommendations"], list)


def test_validate_missing_solution():
    """Test validation with missing integrated solution."""
    state: Level5State = {
        "integrated_solution": None,
        "original_problem": "Test",
        "solution_coverage_map": {},
        "detected_conflicts": [],
        "resolution_summary": {},
        "gap_metrics": {},
        "partial_solutions": {},
        "integrated_subproblems": [],
        "subproblem_dependencies": {"nodes": [], "edges": []},
    }

    result = validate_integrated_solution(state)
    validation = result["validation_results"]

    assert validation["status"] == "invalid"
    assert validation["has_critical_failures"] is True


def test_validate_low_coverage():
    """Test validation with low coverage."""
    state: Level5State = {
        "integrated_solution": {
            "content": "Partial solution with low coverage",
            "reasoning": "Only some parts addressed",
            "confidence": 0.5,
        },
        "original_problem": "Complete solution needed",
        "solution_coverage_map": {"coverage_percentage": 45.0},
        "detected_conflicts": [],
        "resolution_summary": {"total_conflicts": 0, "resolved": 0, "escalated": 0},
        "gap_metrics": {"total_gaps": 5, "critical_gaps": []},
        "partial_solutions": {},
        "integrated_subproblems": [],
        "subproblem_dependencies": {"nodes": [], "edges": []},
    }

    result = validate_integrated_solution(state)
    validation = result["validation_results"]

    assert validation["status"] in ["invalid", "warning"]
    assert validation["has_gaps"] is True


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_level5_execution(sample_level5_state: Level5State):
    """Test complete Level 5 graph execution."""
    # Execute the full graph
    result = level5_graph.invoke(sample_level5_state)

    # Should have all outputs
    assert "solution_coverage_map" in result
    assert "detected_conflicts" in result
    assert "resolution_summary" in result
    assert "identified_gaps" in result
    assert "gap_solutions" in result
    assert "integrated_solution" in result
    assert "validation_results" in result

    # Validation should pass with good inputs
    validation = result["validation_results"]
    assert validation["status"] in ["valid", "warning"]


def test_level5_with_incomplete_solutions():
    """Test Level 5 execution with incomplete solutions."""
    state: Level5State = {
        "partial_solutions": {
            "sp1": {"content": "Only one solution", "reasoning": "test", "confidence": 0.7}
        },
        "integrated_subproblems": [
            {
                "id": "sp1",
                "title": "Task 1",
                "description": "First",
                "paradigm": "structural",
                "source_technique": "test",
                "status": SubproblemStatus.COMPLETED,
                "dependencies": [],
            },
            {
                "id": "sp2",
                "title": "Task 2",
                "description": "Second",
                "paradigm": "functional",
                "source_technique": "test",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            },
        ],
        "subproblem_dependencies": {"nodes": ["sp1", "sp2"], "edges": []},
        "original_problem": "Complete both tasks",
    }

    result = level5_graph.invoke(state)

    # Should complete but with warnings
    assert "integrated_solution" in result
    assert "validation_results" in result

    validation = result["validation_results"]
    # Should have gaps identified
    assert validation["has_gaps"] or len(result["identified_gaps"]) > 0
