"""
State schemas for the LangGraph decomposition pipeline.

This module defines all state schemas used across the multi-level pipeline,
from the main orchestration state to level-specific substates.
"""

from typing import Any, Dict, List, Optional, Literal
from typing_extensions import TypedDict, NotRequired
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ParadigmType(str, Enum):
    """Decomposition paradigm types."""
    STRUCTURAL = "structural"
    FUNCTIONAL = "functional"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    HIERARCHICAL = "hierarchical"
    COMPUTATIONAL = "computational"
    DATA = "data"
    DEPENDENCY = "dependency"


class SubproblemStatus(str, Enum):
    """Status of a subproblem."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ApprovalAction(str, Enum):
    """Human approval actions."""
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    BACKTRACK = "backtrack"
    ADD_CONTEXT = "add_context"
    REQUEST_ALTERNATIVES = "request_alternatives"


class PipelineStage(str, Enum):
    """Pipeline execution stages."""
    PROBLEM_INGESTION = "problem_ingestion"
    LEVEL1_PARADIGM_SELECTION = "level1_paradigm_selection"
    GATE1_PARADIGM_APPROVAL = "gate1_paradigm_approval"
    LEVEL2_TECHNIQUE_SELECTION = "level2_technique_selection"
    GATE2_TECHNIQUE_APPROVAL = "gate2_technique_approval"
    LEVEL3_DECOMPOSITION = "level3_decomposition"
    LEVEL3_INTEGRATION = "level3_integration"
    GATE3_DECOMPOSITION_APPROVAL = "gate3_decomposition_approval"
    LEVEL4_SOLUTION_GENERATION = "level4_solution_generation"
    LEVEL5_SOLUTION_INTEGRATION = "level5_solution_integration"
    GATE4_FINAL_APPROVAL = "gate4_final_approval"
    OUTPUT_FORMATTING = "output_formatting"
    COMPLETED = "completed"


# ============================================================================
# Supporting Models
# ============================================================================

class Technique(TypedDict):
    """Algorithmic decomposition technique from catalog."""
    name: str
    paradigm: str
    formal_definition: str
    prerequisites: List[str]
    complexity: str
    applicability_rules: List[Dict[str, Any]]
    literature_references: List[str]
    implementation_strategy: str
    score: NotRequired[float]


class Subproblem(TypedDict):
    """A decomposed subproblem."""
    id: str
    title: str
    description: str
    paradigm: str
    source_technique: str
    status: SubproblemStatus
    dependencies: List[str]  # IDs of dependent subproblems
    estimated_complexity: NotRequired[str]
    confidence: NotRequired[float]
    metadata: NotRequired[Dict[str, Any]]


class Solution(TypedDict):
    """Solution for a subproblem or integrated solution."""
    subproblem_id: NotRequired[str]
    content: str
    reasoning: str
    confidence: float
    agent_id: NotRequired[str]
    agent_pool: NotRequired[str]
    validation_status: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class ApprovalRecord(TypedDict):
    """Record of human approval decision."""
    gate: str
    timestamp: str
    action: ApprovalAction
    user: NotRequired[str]
    reason: NotRequired[str]
    modifications: NotRequired[Dict[str, Any]]


class ValidationReport(TypedDict):
    """Validation results for solutions or decompositions."""
    status: Literal["valid", "invalid", "warning"]
    has_critical_failures: bool
    has_gaps: bool
    has_conflicts: bool
    issues: List[str]
    recommendations: List[str]
    metadata: NotRequired[Dict[str, Any]]


class DependencyGraph(TypedDict):
    """Graph structure for dependencies."""
    nodes: List[str]  # Subproblem IDs
    edges: List[Dict[str, str]]  # {"from": id, "to": id, "type": "dependency"}
    critical_path: NotRequired[List[str]]


# ============================================================================
# Main Pipeline State
# ============================================================================

class MainPipelineState(TypedDict):
    """
    Global state that flows through the entire main orchestration graph.

    This is the primary state container for the decomposition pipeline,
    accumulating data as it progresses through each level.
    """

    # ========== Input ==========
    original_problem: str
    problem_characteristics: Dict[str, Any]

    # ========== Level 1 Outputs: Paradigm Selection ==========
    selected_paradigms: NotRequired[List[str]]
    paradigm_scores: NotRequired[Dict[str, float]]
    paradigm_reasoning: NotRequired[Dict[str, str]]

    # ========== Level 2 Outputs: Technique Selection ==========
    selected_techniques: NotRequired[Dict[str, Technique]]  # paradigm -> technique
    technique_scores: NotRequired[Dict[str, float]]
    technique_justification: NotRequired[Dict[str, str]]

    # ========== Level 3.1 Outputs: Decomposition Execution ==========
    decomposed_subproblems: NotRequired[Dict[str, List[Subproblem]]]  # paradigm -> subproblems
    decomposition_graphs: NotRequired[Dict[str, Any]]  # visualization data

    # ========== Level 3.2 Outputs: Integration ==========
    integrated_subproblems: NotRequired[List[Subproblem]]
    subproblem_dependencies: NotRequired[DependencyGraph]

    # ========== Level 4 Outputs: Solution Generation ==========
    agent_assignments: NotRequired[Dict[str, str]]  # subproblem_id -> agent_pool
    partial_solutions: NotRequired[Dict[str, Solution]]  # subproblem_id -> solution

    # ========== Level 5 Outputs: Solution Integration ==========
    integrated_solution: NotRequired[Solution]
    validation_results: NotRequired[ValidationReport]

    # ========== Control Flow ==========
    human_approvals: NotRequired[List[ApprovalRecord]]
    backtrack_history: NotRequired[List[str]]
    current_stage: str
    thread_id: NotRequired[str]
    started_at: NotRequired[str]
    completed_at: NotRequired[str]


# ============================================================================
# Level 1: Paradigm Selection State
# ============================================================================

class Level1State(TypedDict):
    """
    State for Level 1: Paradigm Selection subgraph.

    Extends the main state with fields specific to paradigm selection analysis.
    """

    # Inherit key fields from main state
    original_problem: str
    problem_characteristics: Dict[str, Any]

    # Level 1 specific fields
    problem_embedding: NotRequired[List[float]]
    candidate_paradigms: NotRequired[List[Dict[str, Any]]]  # All paradigms with scores
    paradigm_reasoning: NotRequired[Dict[str, str]]  # Why each chosen/rejected

    # Outputs
    selected_paradigms: NotRequired[List[str]]
    paradigm_scores: NotRequired[Dict[str, float]]


# ============================================================================
# Level 2: Technique Selection State
# ============================================================================

class Level2State(TypedDict):
    """
    State for Level 2: Technique Selection subgraph.

    Extends main state with technique-specific analysis fields.
    """

    # Inherit from main state
    original_problem: str
    problem_characteristics: Dict[str, Any]
    selected_paradigms: List[str]

    # Level 2 specific fields
    candidate_techniques: NotRequired[Dict[str, List[Technique]]]  # paradigm -> techniques
    technique_scores: NotRequired[Dict[str, float]]
    technique_justification: NotRequired[Dict[str, str]]

    # Outputs
    selected_techniques: NotRequired[Dict[str, Technique]]


# ============================================================================
# Level 3.1: Paradigm-Specific Decomposition States
# ============================================================================

class StructuralState(TypedDict):
    """State for structural decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Structural-specific analysis
    graph_representation: NotRequired[Dict[str, Any]]  # NetworkGraph structure
    identified_components: NotRequired[List[Dict[str, Any]]]
    component_relationships: NotRequired[List[Dict[str, str]]]
    decomposition_tree: NotRequired[Dict[str, Any]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


class FunctionalState(TypedDict):
    """State for functional decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Functional-specific analysis
    identified_operations: NotRequired[List[Dict[str, Any]]]
    operation_dependencies: NotRequired[List[Dict[str, str]]]
    task_groups: NotRequired[List[Dict[str, Any]]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


class TemporalState(TypedDict):
    """State for temporal decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Temporal-specific analysis
    timeline: NotRequired[Dict[str, Any]]
    identified_stages: NotRequired[List[Dict[str, Any]]]
    event_sequence: NotRequired[List[Dict[str, Any]]]
    temporal_dependencies: NotRequired[List[Dict[str, str]]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


class SpatialState(TypedDict):
    """State for spatial decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Spatial-specific analysis
    coordinate_mapping: NotRequired[Dict[str, Any]]
    identified_regions: NotRequired[List[Dict[str, Any]]]
    region_boundaries: NotRequired[List[Dict[str, Any]]]
    spatial_relationships: NotRequired[List[Dict[str, str]]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


class HierarchicalState(TypedDict):
    """State for hierarchical decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Hierarchical-specific analysis
    identified_levels: NotRequired[List[Dict[str, Any]]]
    abstraction_layers: NotRequired[List[Dict[str, Any]]]
    level_relationships: NotRequired[List[Dict[str, str]]]
    hierarchy_tree: NotRequired[Dict[str, Any]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


class ComputationalState(TypedDict):
    """State for computational decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Computational-specific analysis
    resource_profile: NotRequired[Dict[str, Any]]
    workload_analysis: NotRequired[Dict[str, Any]]
    distribution_strategy: NotRequired[Dict[str, Any]]
    parallelization_opportunities: NotRequired[List[Dict[str, Any]]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


class DataState(TypedDict):
    """State for data decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Data-specific analysis
    schema_analysis: NotRequired[Dict[str, Any]]
    partition_keys: NotRequired[List[str]]
    splitting_strategy: NotRequired[Dict[str, Any]]
    data_dependencies: NotRequired[List[Dict[str, str]]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


class DependencyDecompositionState(TypedDict):
    """State for dependency decomposition subgraph."""

    # Input
    original_problem: str
    selected_technique: Technique

    # Dependency-specific analysis
    dependency_graph: NotRequired[Dict[str, Any]]
    critical_path: NotRequired[List[str]]
    execution_order: NotRequired[List[str]]
    parallel_groups: NotRequired[List[List[str]]]

    # Output
    subproblems: NotRequired[List[Subproblem]]


# ============================================================================
# Level 3.2: Integration State
# ============================================================================

class Level3IntegrationState(TypedDict):
    """
    State for Level 3.2: Integration subgraph.

    Handles merging and conflict resolution of decompositions from multiple paradigms.
    """

    # Input: All subproblems from paradigm subgraphs
    decomposed_subproblems: Dict[str, List[Subproblem]]  # paradigm -> subproblems

    # Integration analysis
    all_subproblems: NotRequired[List[Subproblem]]
    overlap_clusters: NotRequired[List[List[str]]]  # Groups of overlapping subproblem IDs
    detected_conflicts: NotRequired[List[Dict[str, Any]]]
    similarity_matrix: NotRequired[Dict[str, float]]

    # Outputs
    integrated_subproblems: NotRequired[List[Subproblem]]
    subproblem_dependencies: NotRequired[DependencyGraph]
    validation_report: NotRequired[ValidationReport]


# ============================================================================
# Level 4: Solution Generation State
# ============================================================================

class Level4State(TypedDict):
    """
    State for Level 4: Solution Generation subgraph.

    Manages agent pool assignment and parallel solution generation.
    """

    # Input
    integrated_subproblems: List[Subproblem]
    subproblem_dependencies: DependencyGraph

    # Solution generation analysis
    routing_decisions: NotRequired[Dict[str, Dict[str, Any]]]  # subproblem_id -> routing info
    execution_batches: NotRequired[List[List[str]]]  # Batches of subproblem IDs for parallel execution
    agent_pool_status: NotRequired[Dict[str, Dict[str, Any]]]
    progress_tracking: NotRequired[Dict[str, Any]]

    # Outputs
    agent_assignments: NotRequired[Dict[str, str]]  # subproblem_id -> agent_pool
    partial_solutions: NotRequired[Dict[str, Solution]]  # subproblem_id -> solution
    failed_subproblems: NotRequired[List[str]]


# ============================================================================
# Level 5: Solution Integration State
# ============================================================================

class Level5State(TypedDict):
    """
    State for Level 5: Solution Integration subgraph.

    Merges partial solutions into coherent final solution.
    """

    # Input
    partial_solutions: Dict[str, Solution]
    integrated_subproblems: List[Subproblem]
    subproblem_dependencies: DependencyGraph
    original_problem: str

    # Integration analysis
    solution_coverage_map: NotRequired[Dict[str, Any]]
    detected_conflicts: NotRequired[List[Dict[str, Any]]]
    identified_gaps: NotRequired[List[Dict[str, Any]]]
    gap_solutions: NotRequired[Dict[str, Solution]]

    # Outputs
    integrated_solution: NotRequired[Solution]
    validation_results: NotRequired[ValidationReport]
