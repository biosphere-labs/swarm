"""
Tests for Level 4: Solution Generation Subgraph.

Tests all components including routing, parallel execution, monitoring, and collection.
"""

import pytest
from typing import List, Dict
from src.decomposition_pipeline.schemas.state import (
    Level4State,
    Subproblem,
    DependencyGraph,
    Solution,
    SubproblemStatus,
)
from src.decomposition_pipeline.graphs.level4_solution import (
    route_subproblems_to_pools,
    analyze_subproblem_requirements,
    create_execution_batches,
    CircularDependencyError,
    monitor_execution_progress,
    collect_and_validate_solutions,
    level4_graph,
)
from src.decomposition_pipeline.agents.pool import (
    AgentPoolManager,
    AgentPool,
    Agent,
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
            "description": "Design RESTful API endpoints for user management",
            "paradigm": "structural",
            "source_technique": "Component Extraction",
            "status": SubproblemStatus.PENDING,
            "dependencies": [],
            "estimated_complexity": "medium",
        },
        {
            "id": "sp2",
            "title": "Database Schema",
            "description": "Design database schema with proper indexing",
            "paradigm": "data",
            "source_technique": "Horizontal Partitioning",
            "status": SubproblemStatus.PENDING,
            "dependencies": [],
            "estimated_complexity": "low",
        },
        {
            "id": "sp3",
            "title": "Authentication Flow",
            "description": "Implement JWT-based authentication with security best practices",
            "paradigm": "functional",
            "source_technique": "Task Parallelism",
            "status": SubproblemStatus.PENDING,
            "dependencies": ["sp1", "sp2"],
            "estimated_complexity": "high",
        },
    ]


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
def sample_level4_state(
    sample_subproblems: List[Subproblem],
    sample_dependency_graph: DependencyGraph
) -> Level4State:
    """Create sample Level4State for testing."""
    return {
        "integrated_subproblems": sample_subproblems,
        "subproblem_dependencies": sample_dependency_graph,
    }


# ============================================================================
# Agent Pool Tests
# ============================================================================

def test_agent_pool_creation():
    """Test creating an agent pool."""
    pool = AgentPool(
        name="test_pool",
        specialization="testing",
        size=10
    )

    assert pool.name == "test_pool"
    assert pool.specialization == "testing"
    assert len(pool.agents) == 10
    assert all(agent.pool_name == "test_pool" for agent in pool.agents)


def test_agent_pool_load_balancing():
    """Test least-loaded agent selection."""
    pool = AgentPool(name="test_pool", specialization="test", size=5)

    # Assign work to some agents
    agent1 = pool.agents[0]
    agent1.assign_task("task1")
    agent1.current_workload = 2

    agent2 = pool.agents[1]
    agent2.assign_task("task2")
    agent2.current_workload = 1

    # Should select agent with lowest workload
    least_loaded = pool.get_least_loaded_agent()
    assert least_loaded is not None
    assert least_loaded.current_workload <= 1


def test_agent_pool_manager_initialization():
    """Test agent pool manager initializes all pools."""
    manager = AgentPoolManager()

    # Should have paradigm pools (8) - keys are paradigm names without _pool suffix
    assert "structural" in manager.pools
    assert "functional" in manager.pools
    assert "temporal" in manager.pools

    # Should have domain pools
    assert "api_design" in manager.pools
    assert "data_processing" in manager.pools

    # Should have general pool
    assert "general" in manager.pools


def test_pool_selection_strategy():
    """Test pool selection follows priority order."""
    manager = AgentPoolManager()

    # Should prefer paradigm pool
    pool_name = manager.select_pool_for_subproblem(
        paradigm="structural",
        domain=None,
        complexity="medium"
    )
    # Pool selection returns full pool name with _pool suffix from the actual pool
    assert "structural" in pool_name or pool_name == "structural_pool"

    # Should use domain pool if specified
    pool_name = manager.select_pool_for_subproblem(
        paradigm="unknown",
        domain="api_design",
        complexity="medium"
    )
    assert "api_design" in pool_name or pool_name == "api_design_pool"

    # Should use general pool for high complexity
    pool_name = manager.select_pool_for_subproblem(
        paradigm="unknown",
        domain=None,
        complexity="high"
    )
    assert "general" in pool_name or pool_name == "general_pool"


# ============================================================================
# Routing Tests
# ============================================================================

def test_analyze_subproblem_requirements():
    """Test subproblem analysis extracts correct requirements."""
    subproblem: Subproblem = {
        "id": "sp1",
        "title": "API Design",
        "description": "Design RESTful API with complex authentication",
        "paradigm": "structural",
        "source_technique": "Component Extraction",
        "status": SubproblemStatus.PENDING,
        "dependencies": ["sp2"],
        "estimated_complexity": "high",
    }

    analysis = analyze_subproblem_requirements(subproblem)

    assert analysis["complexity"] == "high"
    assert analysis["paradigm"] == "structural"
    assert analysis["has_dependencies"] is True
    assert "domain" in analysis


def test_complexity_estimation():
    """Test complexity estimation from description."""
    from src.decomposition_pipeline.graphs.level4_solution.route_to_pools import estimate_complexity

    # High complexity
    subproblem_high: Subproblem = {
        "id": "sp1",
        "title": "Complex Task",
        "description": "This is a very complex and sophisticated problem requiring advanced techniques. " * 10,
        "paradigm": "structural",
        "source_technique": "test",
        "status": SubproblemStatus.PENDING,
        "dependencies": ["sp2", "sp3", "sp4", "sp5"],
    }
    assert estimate_complexity(subproblem_high) == "high"

    # Low complexity
    subproblem_low: Subproblem = {
        "id": "sp2",
        "title": "Simple Task",
        "description": "Simple basic task",
        "paradigm": "structural",
        "source_technique": "test",
        "status": SubproblemStatus.PENDING,
        "dependencies": [],
    }
    assert estimate_complexity(subproblem_low) == "low"


def test_domain_detection():
    """Test domain detection from description."""
    from src.decomposition_pipeline.graphs.level4_solution.route_to_pools import detect_domain

    # API domain
    domain = detect_domain("Design REST API endpoints", {})
    assert domain == "api_design"

    # Database domain
    domain = detect_domain("Create SQL schema with indexes", {})
    assert domain == "database"

    # Security domain
    domain = detect_domain("Implement authentication and encryption", {})
    assert domain == "security"


def test_route_subproblems_to_pools(sample_level4_state: Level4State):
    """Test routing node assigns subproblems to pools."""
    result = route_subproblems_to_pools(sample_level4_state)

    assert "routing_decisions" in result
    assert "agent_assignments" in result
    assert "agent_pool_status" in result

    # Should have routing decision for each subproblem
    assert len(result["routing_decisions"]) == 3
    assert len(result["agent_assignments"]) == 3

    # Check specific assignments
    assert "sp1" in result["agent_assignments"]
    assert "sp2" in result["agent_assignments"]
    assert "sp3" in result["agent_assignments"]


# ============================================================================
# Execution Batching Tests
# ============================================================================

def test_create_execution_batches_no_dependencies():
    """Test batch creation with independent subproblems."""
    subproblems = [
        {"id": "sp1", "dependencies": []},
        {"id": "sp2", "dependencies": []},
        {"id": "sp3", "dependencies": []},
    ]

    dependency_graph = {
        "nodes": ["sp1", "sp2", "sp3"],
        "edges": [],
    }

    batches = create_execution_batches(subproblems, dependency_graph)

    # All should be in one batch since no dependencies
    assert len(batches) == 1
    assert set(batches[0]) == {"sp1", "sp2", "sp3"}


def test_create_execution_batches_with_dependencies():
    """Test batch creation respects dependencies."""
    subproblems = [
        {"id": "sp1", "dependencies": []},
        {"id": "sp2", "dependencies": []},
        {"id": "sp3", "dependencies": ["sp1", "sp2"]},
    ]

    dependency_graph = {
        "nodes": ["sp1", "sp2", "sp3"],
        "edges": [
            {"from": "sp1", "to": "sp3"},
            {"from": "sp2", "to": "sp3"},
        ],
    }

    batches = create_execution_batches(subproblems, dependency_graph)

    # Should have 2 batches
    assert len(batches) == 2

    # First batch: sp1 and sp2 (no dependencies)
    assert set(batches[0]) == {"sp1", "sp2"}

    # Second batch: sp3 (depends on sp1 and sp2)
    assert batches[1] == ["sp3"]


def test_create_execution_batches_chain():
    """Test batch creation with chain of dependencies."""
    subproblems = [
        {"id": "sp1", "dependencies": []},
        {"id": "sp2", "dependencies": ["sp1"]},
        {"id": "sp3", "dependencies": ["sp2"]},
    ]

    dependency_graph = {
        "nodes": ["sp1", "sp2", "sp3"],
        "edges": [
            {"from": "sp1", "to": "sp2"},
            {"from": "sp2", "to": "sp3"},
        ],
    }

    batches = create_execution_batches(subproblems, dependency_graph)

    # Should have 3 batches (sequential execution)
    assert len(batches) == 3
    assert batches[0] == ["sp1"]
    assert batches[1] == ["sp2"]
    assert batches[2] == ["sp3"]


def test_create_execution_batches_circular_dependency():
    """Test circular dependency detection."""
    subproblems = [
        {"id": "sp1", "dependencies": ["sp2"]},
        {"id": "sp2", "dependencies": ["sp1"]},
    ]

    dependency_graph = {
        "nodes": ["sp1", "sp2"],
        "edges": [
            {"from": "sp1", "to": "sp2"},
            {"from": "sp2", "to": "sp1"},
        ],
    }

    with pytest.raises(CircularDependencyError):
        create_execution_batches(subproblems, dependency_graph)


# ============================================================================
# Progress Monitoring Tests
# ============================================================================

def test_monitor_execution_progress():
    """Test progress monitoring calculates metrics correctly."""
    state: Level4State = {
        "integrated_subproblems": [
            {"id": "sp1"},
            {"id": "sp2"},
            {"id": "sp3"},
            {"id": "sp4"},
        ],
        "partial_solutions": {
            "sp1": {"content": "solution1"},
            "sp2": {"content": "solution2"},
        },
        "failed_subproblems": ["sp3"],
        "agent_pool_status": {},
    }

    result = monitor_execution_progress(state)

    progress = result["progress_tracking"]
    assert progress["total_subproblems"] == 4
    assert progress["completed"] == 2
    assert progress["failed"] == 1
    assert progress["pending"] == 1
    assert progress["completion_percentage"] == 50.0


# ============================================================================
# Solution Collection Tests
# ============================================================================

def test_collect_and_validate_solutions_complete():
    """Test solution collection with all subproblems solved."""
    state: Level4State = {
        "integrated_subproblems": [
            {"id": "sp1"},
            {"id": "sp2"},
        ],
        "partial_solutions": {
            "sp1": {"content": "solution1", "confidence": 0.9},
            "sp2": {"content": "solution2", "confidence": 0.85},
        },
        "failed_subproblems": [],
    }

    result = collect_and_validate_solutions(state)

    validation = result["validation_results"]
    assert validation["status"] == "valid"
    assert not validation["has_critical_failures"]
    assert not validation["has_gaps"]
    assert validation["metadata"]["success_rate"] == 100.0


def test_collect_and_validate_solutions_with_failures():
    """Test solution collection with some failures."""
    state: Level4State = {
        "integrated_subproblems": [
            {"id": "sp1"},
            {"id": "sp2"},
            {"id": "sp3"},
        ],
        "partial_solutions": {
            "sp1": {"content": "solution1"},
        },
        "failed_subproblems": ["sp2", "sp3"],
    }

    result = collect_and_validate_solutions(state)

    validation = result["validation_results"]
    assert validation["status"] in ["warning", "invalid"]
    assert len(validation["issues"]) > 0
    assert validation["metadata"]["failed"] == 2


def test_collect_and_validate_solutions_critical_failures():
    """Test validation detects critical failure rate."""
    state: Level4State = {
        "integrated_subproblems": [
            {"id": f"sp{i}"} for i in range(10)
        ],
        "partial_solutions": {
            "sp0": {"content": "solution0"},
            "sp1": {"content": "solution1"},
        },
        "failed_subproblems": [f"sp{i}" for i in range(2, 10)],  # 80% failure
    }

    result = collect_and_validate_solutions(state)

    validation = result["validation_results"]
    assert validation["has_critical_failures"] is True
    assert validation["status"] == "invalid"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_full_level4_execution(sample_level4_state: Level4State):
    """Test complete Level 4 graph execution."""
    # Note: This would need async support in the graph
    # For now, test each node individually

    # Step 1: Route to pools
    state = route_subproblems_to_pools(sample_level4_state)
    assert "agent_assignments" in state

    # Step 2: Would execute in parallel (tested separately)
    # Step 3: Monitor progress
    state["partial_solutions"] = {"sp1": {"content": "test"}}
    state["failed_subproblems"] = []
    state = monitor_execution_progress(state)
    assert "progress_tracking" in state

    # Step 4: Collect solutions
    state = collect_and_validate_solutions(state)
    assert "validation_results" in state


def test_retry_candidates_identification():
    """Test identification of retry candidates."""
    from src.decomposition_pipeline.graphs.level4_solution.collect_solutions import identify_retry_candidates

    # Few failures - retry with alternate pool
    failed = ["sp1", "sp2"]
    validation = {"metadata": {"failed": 2}}
    candidates = identify_retry_candidates(failed, validation)

    assert len(candidates) == 2
    assert all(c["retry_strategy"] == "alternate_pool" for c in candidates)

    # Many failures - retry with larger model
    failed = [f"sp{i}" for i in range(7)]
    validation = {"metadata": {"failed": 7}}
    candidates = identify_retry_candidates(failed, validation)

    assert len(candidates) == 7
    assert all(c["retry_strategy"] == "larger_model" for c in candidates)

    # Too many failures - escalate to human
    failed = [f"sp{i}" for i in range(15)]
    validation = {"metadata": {"failed": 15}}
    candidates = identify_retry_candidates(failed, validation)

    assert len(candidates) == 15
    assert all(c["retry_strategy"] == "human_review" for c in candidates)
