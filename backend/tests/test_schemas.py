"""
Tests for state schemas.

Validates state schema definitions, type checking, and serialization.
"""

import pytest
from typing import get_type_hints
from decomposition_pipeline.schemas import (
    # Enums
    ParadigmType,
    SubproblemStatus,
    ApprovalAction,
    PipelineStage,

    # Supporting Models
    Technique,
    Subproblem,
    Solution,
    ApprovalRecord,
    ValidationReport,
    DependencyGraph,

    # Main State
    MainPipelineState,

    # Level States
    Level1State,
    Level2State,
    Level3IntegrationState,
    Level4State,
    Level5State,

    # Paradigm-Specific States
    StructuralState,
    FunctionalState,
    TemporalState,
    SpatialState,
    HierarchicalState,
    ComputationalState,
    DataState,
    DependencyDecompositionState,
)


# ============================================================================
# Test Enums
# ============================================================================

def test_paradigm_type_enum():
    """Test ParadigmType enum has all 8 paradigms."""
    assert len(ParadigmType) == 8
    assert ParadigmType.STRUCTURAL.value == "structural"
    assert ParadigmType.FUNCTIONAL.value == "functional"
    assert ParadigmType.TEMPORAL.value == "temporal"
    assert ParadigmType.SPATIAL.value == "spatial"
    assert ParadigmType.HIERARCHICAL.value == "hierarchical"
    assert ParadigmType.COMPUTATIONAL.value == "computational"
    assert ParadigmType.DATA.value == "data"
    assert ParadigmType.DEPENDENCY.value == "dependency"


def test_subproblem_status_enum():
    """Test SubproblemStatus enum has all statuses."""
    assert len(SubproblemStatus) == 4
    assert SubproblemStatus.PENDING.value == "pending"
    assert SubproblemStatus.IN_PROGRESS.value == "in_progress"
    assert SubproblemStatus.COMPLETED.value == "completed"
    assert SubproblemStatus.FAILED.value == "failed"


def test_approval_action_enum():
    """Test ApprovalAction enum has all actions."""
    assert len(ApprovalAction) == 6
    assert ApprovalAction.APPROVE.value == "approve"
    assert ApprovalAction.REJECT.value == "reject"
    assert ApprovalAction.MODIFY.value == "modify"
    assert ApprovalAction.BACKTRACK.value == "backtrack"
    assert ApprovalAction.ADD_CONTEXT.value == "add_context"
    assert ApprovalAction.REQUEST_ALTERNATIVES.value == "request_alternatives"


def test_pipeline_stage_enum():
    """Test PipelineStage enum has all stages."""
    stages = list(PipelineStage)
    assert len(stages) >= 12
    assert PipelineStage.PROBLEM_INGESTION in stages
    assert PipelineStage.LEVEL1_PARADIGM_SELECTION in stages
    assert PipelineStage.COMPLETED in stages


# ============================================================================
# Test Supporting Models
# ============================================================================

def test_technique_model():
    """Test Technique TypedDict structure."""
    technique: Technique = {
        "name": "Divide and Conquer",
        "paradigm": "structural",
        "formal_definition": "T(n) = aT(n/b) + f(n)",
        "prerequisites": ["problem_is_divisible", "subproblems_independent"],
        "complexity": "O(n log n)",
        "applicability_rules": [{"rule": "problem_size > 1000", "score": 0.8}],
        "literature_references": ["CLRS Ch 4"],
        "implementation_strategy": "Recursively split, solve, merge",
    }

    assert technique["name"] == "Divide and Conquer"
    assert technique["paradigm"] == "structural"
    assert len(technique["prerequisites"]) == 2
    assert len(technique["literature_references"]) == 1

    # Test optional score
    technique["score"] = 0.91
    assert technique["score"] == 0.91


def test_subproblem_model():
    """Test Subproblem TypedDict structure."""
    subproblem: Subproblem = {
        "id": "sp-001",
        "title": "User Authentication",
        "description": "Implement user auth system",
        "paradigm": "functional",
        "source_technique": "Task Parallelism",
        "status": SubproblemStatus.PENDING,
        "dependencies": ["sp-002"],
    }

    assert subproblem["id"] == "sp-001"
    assert subproblem["status"] == SubproblemStatus.PENDING
    assert len(subproblem["dependencies"]) == 1

    # Test optional fields
    subproblem["confidence"] = 0.85
    subproblem["estimated_complexity"] = "medium"
    assert subproblem["confidence"] == 0.85


def test_solution_model():
    """Test Solution TypedDict structure."""
    solution: Solution = {
        "content": "Use JWT tokens for authentication",
        "reasoning": "Industry standard, secure, scalable",
        "confidence": 0.9,
    }

    assert solution["confidence"] == 0.9

    # Test optional fields
    solution["subproblem_id"] = "sp-001"
    solution["agent_id"] = "agent-42"
    solution["agent_pool"] = "functional"
    assert solution["agent_pool"] == "functional"


def test_approval_record_model():
    """Test ApprovalRecord TypedDict structure."""
    record: ApprovalRecord = {
        "gate": "paradigm_selection",
        "timestamp": "2025-10-30T12:00:00Z",
        "action": ApprovalAction.APPROVE,
    }

    assert record["action"] == ApprovalAction.APPROVE

    # Test optional fields
    record["user"] = "analyst@example.com"
    record["reason"] = "Looks good"
    assert record["user"] == "analyst@example.com"


def test_validation_report_model():
    """Test ValidationReport TypedDict structure."""
    report: ValidationReport = {
        "status": "valid",
        "has_critical_failures": False,
        "has_gaps": False,
        "has_conflicts": False,
        "issues": [],
        "recommendations": ["Consider adding error handling"],
    }

    assert report["status"] == "valid"
    assert not report["has_critical_failures"]
    assert len(report["recommendations"]) == 1


def test_dependency_graph_model():
    """Test DependencyGraph TypedDict structure."""
    graph: DependencyGraph = {
        "nodes": ["sp-001", "sp-002", "sp-003"],
        "edges": [
            {"from": "sp-001", "to": "sp-002", "type": "dependency"},
            {"from": "sp-002", "to": "sp-003", "type": "dependency"},
        ],
    }

    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 2

    # Test optional critical path
    graph["critical_path"] = ["sp-001", "sp-002", "sp-003"]
    assert len(graph["critical_path"]) == 3


# ============================================================================
# Test Main Pipeline State
# ============================================================================

def test_main_pipeline_state_minimal():
    """Test MainPipelineState with minimal required fields."""
    state: MainPipelineState = {
        "original_problem": "Build a collaborative text editor",
        "problem_characteristics": {
            "problem_size": "large",
            "has_real_time": True,
            "distributed": True,
        },
        "current_stage": "problem_ingestion",
    }

    assert state["original_problem"].startswith("Build")
    assert state["problem_characteristics"]["has_real_time"]
    assert state["current_stage"] == "problem_ingestion"


def test_main_pipeline_state_complete():
    """Test MainPipelineState with all fields populated."""
    state: MainPipelineState = {
        # Input
        "original_problem": "Build a collaborative text editor",
        "problem_characteristics": {"problem_size": "large"},

        # Level 1
        "selected_paradigms": ["temporal", "functional"],
        "paradigm_scores": {"temporal": 0.85, "functional": 0.78},
        "paradigm_reasoning": {"temporal": "Real-time requirements"},

        # Level 2
        "selected_techniques": {
            "temporal": {
                "name": "Event Pipeline",
                "paradigm": "temporal",
                "formal_definition": "Events -> Handlers -> State",
                "prerequisites": ["sequential_stages"],
                "complexity": "O(n)",
                "applicability_rules": [],
                "literature_references": ["SEDA"],
                "implementation_strategy": "Define event types",
            }
        },

        # Level 3.1
        "decomposed_subproblems": {
            "temporal": [
                {
                    "id": "sp-001",
                    "title": "Event streaming",
                    "description": "Real-time events",
                    "paradigm": "temporal",
                    "source_technique": "Event Pipeline",
                    "status": SubproblemStatus.COMPLETED,
                    "dependencies": [],
                }
            ]
        },

        # Level 3.2
        "integrated_subproblems": [],
        "subproblem_dependencies": {"nodes": [], "edges": []},

        # Level 4
        "agent_assignments": {"sp-001": "temporal_pool"},
        "partial_solutions": {},

        # Level 5
        "integrated_solution": {
            "content": "Complete solution",
            "reasoning": "All parts integrated",
            "confidence": 0.9,
        },
        "validation_results": {
            "status": "valid",
            "has_critical_failures": False,
            "has_gaps": False,
            "has_conflicts": False,
            "issues": [],
            "recommendations": [],
        },

        # Control
        "human_approvals": [],
        "backtrack_history": [],
        "current_stage": "completed",
        "thread_id": "thread-123",
        "started_at": "2025-10-30T10:00:00Z",
        "completed_at": "2025-10-30T12:00:00Z",
    }

    assert len(state["selected_paradigms"]) == 2
    assert "temporal" in state["selected_techniques"]
    assert len(state["decomposed_subproblems"]["temporal"]) == 1
    assert state["integrated_solution"]["confidence"] == 0.9


# ============================================================================
# Test Level-Specific States
# ============================================================================

def test_level1_state():
    """Test Level1State structure."""
    state: Level1State = {
        "original_problem": "Build API gateway",
        "problem_characteristics": {"api_count": 10},
        "problem_embedding": [0.1, 0.2, 0.3],
        "candidate_paradigms": [
            {"paradigm": "structural", "score": 0.8},
            {"paradigm": "functional", "score": 0.7},
        ],
        "selected_paradigms": ["structural"],
        "paradigm_scores": {"structural": 0.8},
    }

    assert len(state["problem_embedding"]) == 3
    assert len(state["candidate_paradigms"]) == 2
    assert state["selected_paradigms"][0] == "structural"


def test_level2_state():
    """Test Level2State structure."""
    state: Level2State = {
        "original_problem": "Build API gateway",
        "problem_characteristics": {},
        "selected_paradigms": ["structural"],
        "candidate_techniques": {
            "structural": [
                {
                    "name": "Divide and Conquer",
                    "paradigm": "structural",
                    "formal_definition": "T(n) = aT(n/b) + f(n)",
                    "prerequisites": [],
                    "complexity": "O(n log n)",
                    "applicability_rules": [],
                    "literature_references": [],
                    "implementation_strategy": "Split, solve, merge",
                }
            ]
        },
    }

    assert "structural" in state["candidate_techniques"]
    assert len(state["candidate_techniques"]["structural"]) == 1


def test_structural_state():
    """Test StructuralState for structural decomposition."""
    state: StructuralState = {
        "original_problem": "Build microservices architecture",
        "selected_technique": {
            "name": "Graph Partitioning",
            "paradigm": "structural",
            "formal_definition": "Partition G(V,E) into subgraphs",
            "prerequisites": [],
            "complexity": "O(E log V)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Build graph, partition",
        },
        "graph_representation": {"nodes": [], "edges": []},
        "identified_components": [{"id": "service-1", "name": "Auth Service"}],
    }

    assert state["selected_technique"]["name"] == "Graph Partitioning"
    assert len(state["identified_components"]) == 1


def test_functional_state():
    """Test FunctionalState for functional decomposition."""
    state: FunctionalState = {
        "original_problem": "Data processing pipeline",
        "selected_technique": {
            "name": "MapReduce",
            "paradigm": "functional",
            "formal_definition": "map + reduce",
            "prerequisites": [],
            "complexity": "O(n/p)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Define map and reduce",
        },
        "identified_operations": [{"name": "transform", "type": "map"}],
    }

    assert state["selected_technique"]["name"] == "MapReduce"


def test_temporal_state():
    """Test TemporalState for temporal decomposition."""
    state: TemporalState = {
        "original_problem": "Real-time event processing",
        "selected_technique": {
            "name": "Event Pipeline",
            "paradigm": "temporal",
            "formal_definition": "Stages with queues",
            "prerequisites": [],
            "complexity": "O(n)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Define stages",
        },
        "timeline": {"start": 0, "end": 100},
        "identified_stages": [{"name": "ingestion", "order": 1}],
    }

    assert "timeline" in state
    assert len(state["identified_stages"]) == 1


def test_level3_integration_state():
    """Test Level3IntegrationState structure."""
    state: Level3IntegrationState = {
        "decomposed_subproblems": {
            "structural": [
                {
                    "id": "sp-001",
                    "title": "Component A",
                    "description": "First component",
                    "paradigm": "structural",
                    "source_technique": "Graph Partitioning",
                    "status": SubproblemStatus.COMPLETED,
                    "dependencies": [],
                }
            ],
            "functional": [
                {
                    "id": "sp-002",
                    "title": "Operation B",
                    "description": "Second operation",
                    "paradigm": "functional",
                    "source_technique": "MapReduce",
                    "status": SubproblemStatus.COMPLETED,
                    "dependencies": [],
                }
            ],
        },
        "overlap_clusters": [["sp-001"]],
        "integrated_subproblems": [],
    }

    assert len(state["decomposed_subproblems"]) == 2
    assert "structural" in state["decomposed_subproblems"]


def test_level4_state():
    """Test Level4State structure."""
    state: Level4State = {
        "integrated_subproblems": [
            {
                "id": "sp-001",
                "title": "Subproblem 1",
                "description": "Description",
                "paradigm": "structural",
                "source_technique": "Technique",
                "status": SubproblemStatus.PENDING,
                "dependencies": [],
            }
        ],
        "subproblem_dependencies": {"nodes": ["sp-001"], "edges": []},
        "routing_decisions": {"sp-001": {"pool": "structural", "model": "gpt-4o-mini"}},
        "agent_assignments": {"sp-001": "structural_pool"},
    }

    assert len(state["integrated_subproblems"]) == 1
    assert state["agent_assignments"]["sp-001"] == "structural_pool"


def test_level5_state():
    """Test Level5State structure."""
    state: Level5State = {
        "partial_solutions": {
            "sp-001": {
                "content": "Solution content",
                "reasoning": "Why this works",
                "confidence": 0.85,
            }
        },
        "integrated_subproblems": [],
        "subproblem_dependencies": {"nodes": [], "edges": []},
        "original_problem": "Build system",
        "solution_coverage_map": {"sp-001": "covered"},
        "integrated_solution": {
            "content": "Final integrated solution",
            "reasoning": "Combined all parts",
            "confidence": 0.9,
        },
    }

    assert len(state["partial_solutions"]) == 1
    assert state["integrated_solution"]["confidence"] == 0.9


# ============================================================================
# Test All Paradigm States
# ============================================================================

@pytest.mark.parametrize("state_class,paradigm", [
    (StructuralState, "structural"),
    (FunctionalState, "functional"),
    (TemporalState, "temporal"),
    (SpatialState, "spatial"),
    (HierarchicalState, "hierarchical"),
    (ComputationalState, "computational"),
    (DataState, "data"),
    (DependencyDecompositionState, "dependency"),
])
def test_paradigm_states_have_required_fields(state_class, paradigm):
    """Test all paradigm states have required base fields."""
    # Get type hints for the state class
    hints = get_type_hints(state_class)

    # All paradigm states should have these base fields
    assert "original_problem" in hints
    assert "selected_technique" in hints
    assert "subproblems" in hints


def test_spatial_state():
    """Test SpatialState for spatial decomposition."""
    state: SpatialState = {
        "original_problem": "Geographic load balancing",
        "selected_technique": {
            "name": "Region Partitioning",
            "paradigm": "spatial",
            "formal_definition": "Partition by geography",
            "prerequisites": [],
            "complexity": "O(n)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Define regions",
        },
        "coordinate_mapping": {"region1": {"lat": 40.7, "lon": -74.0}},
    }

    assert "coordinate_mapping" in state


def test_hierarchical_state():
    """Test HierarchicalState for hierarchical decomposition."""
    state: HierarchicalState = {
        "original_problem": "Multi-tier architecture",
        "selected_technique": {
            "name": "Layer Decomposition",
            "paradigm": "hierarchical",
            "formal_definition": "Divide into layers",
            "prerequisites": [],
            "complexity": "O(n)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Define layers",
        },
        "identified_levels": [{"name": "presentation", "order": 1}],
    }

    assert len(state["identified_levels"]) == 1


def test_computational_state():
    """Test ComputationalState for computational decomposition."""
    state: ComputationalState = {
        "original_problem": "Parallel computation",
        "selected_technique": {
            "name": "Data Parallelism",
            "paradigm": "computational",
            "formal_definition": "Partition data for parallel processing",
            "prerequisites": [],
            "complexity": "O(n/p)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Split data",
        },
        "resource_profile": {"cpu": "high", "memory": "medium"},
    }

    assert state["resource_profile"]["cpu"] == "high"


def test_data_state():
    """Test DataState for data decomposition."""
    state: DataState = {
        "original_problem": "Database sharding",
        "selected_technique": {
            "name": "Horizontal Partitioning",
            "paradigm": "data",
            "formal_definition": "Partition rows",
            "prerequisites": [],
            "complexity": "O(1)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Choose partition key",
        },
        "schema_analysis": {"tables": ["users", "orders"]},
        "partition_keys": ["user_id"],
    }

    assert "user_id" in state["partition_keys"]


def test_dependency_decomposition_state():
    """Test DependencyDecompositionState for dependency decomposition."""
    state: DependencyDecompositionState = {
        "original_problem": "Task scheduling",
        "selected_technique": {
            "name": "Topological Sort",
            "paradigm": "dependency",
            "formal_definition": "Order by dependencies",
            "prerequisites": [],
            "complexity": "O(V + E)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Build DAG, sort",
        },
        "dependency_graph": {"nodes": ["task1", "task2"], "edges": []},
        "critical_path": ["task1", "task2"],
    }

    assert len(state["critical_path"]) == 2


# ============================================================================
# Test State Updates and Merging
# ============================================================================

def test_state_update_pattern():
    """Test typical state update pattern."""
    # Initial state
    state: MainPipelineState = {
        "original_problem": "Build system",
        "problem_characteristics": {},
        "current_stage": "problem_ingestion",
    }

    # Level 1 updates state
    state["selected_paradigms"] = ["structural", "functional"]
    state["paradigm_scores"] = {"structural": 0.8, "functional": 0.7}
    state["current_stage"] = "level2_technique_selection"

    assert len(state["selected_paradigms"]) == 2
    assert state["current_stage"] == "level2_technique_selection"

    # Level 2 updates state
    state["selected_techniques"] = {
        "structural": {
            "name": "Technique",
            "paradigm": "structural",
            "formal_definition": "Definition",
            "prerequisites": [],
            "complexity": "O(n)",
            "applicability_rules": [],
            "literature_references": [],
            "implementation_strategy": "Strategy",
        }
    }

    assert "structural" in state["selected_techniques"]


def test_state_serialization():
    """Test that states can be serialized to dict."""
    state: MainPipelineState = {
        "original_problem": "Test problem",
        "problem_characteristics": {"size": "large"},
        "current_stage": "problem_ingestion",
    }

    # State should be a dict
    assert isinstance(state, dict)
    assert "original_problem" in state
    assert state["problem_characteristics"]["size"] == "large"


# ============================================================================
# Test Edge Cases
# ============================================================================

def test_empty_optional_fields():
    """Test states with empty optional fields."""
    state: MainPipelineState = {
        "original_problem": "Problem",
        "problem_characteristics": {},
        "current_stage": "problem_ingestion",
    }

    # Optional fields should not be present
    assert "selected_paradigms" not in state
    assert "technique_scores" not in state
    assert "integrated_solution" not in state


def test_nested_structures():
    """Test deeply nested state structures."""
    state: MainPipelineState = {
        "original_problem": "Problem",
        "problem_characteristics": {
            "nested": {
                "level1": {
                    "level2": {
                        "value": "deep"
                    }
                }
            }
        },
        "current_stage": "problem_ingestion",
    }

    assert state["problem_characteristics"]["nested"]["level1"]["level2"]["value"] == "deep"


def test_multiple_subproblems():
    """Test state with multiple subproblems."""
    subproblems: List[Subproblem] = [
        {
            "id": f"sp-{i:03d}",
            "title": f"Subproblem {i}",
            "description": f"Description {i}",
            "paradigm": "structural",
            "source_technique": "Technique",
            "status": SubproblemStatus.PENDING,
            "dependencies": [],
        }
        for i in range(10)
    ]

    state: Level4State = {
        "integrated_subproblems": subproblems,
        "subproblem_dependencies": {"nodes": [sp["id"] for sp in subproblems], "edges": []},
    }

    assert len(state["integrated_subproblems"]) == 10
    assert len(state["subproblem_dependencies"]["nodes"]) == 10
