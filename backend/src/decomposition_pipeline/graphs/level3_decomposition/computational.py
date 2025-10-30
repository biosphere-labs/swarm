"""
Computational Decomposition Subgraph (Level 3.1.6)

Applies computational decomposition techniques like Data Parallelism,
Model Parallelism, or Mixture of Experts to break problems into
computational units.
"""

from typing import Any, Dict, List
from langgraph.graph import StateGraph, END
from decomposition_pipeline.schemas import ComputationalState, Subproblem, SubproblemStatus
import uuid


def profile_resources(state: ComputationalState) -> Dict[str, Any]:
    """
    Analyze resource requirements for the problem.

    Profiles CPU, memory, and I/O requirements.
    """
    problem = state["original_problem"]

    # Estimate resource profile
    profile = {
        "cpu_intensive": "compute" in problem.lower() or "calculate" in problem.lower(),
        "memory_intensive": "large" in problem.lower() or "dataset" in problem.lower(),
        "io_intensive": "read" in problem.lower() or "write" in problem.lower(),
        "estimated_compute_units": 4
    }

    return {"resource_profile": profile}


def analyze_workload(state: ComputationalState) -> Dict[str, Any]:
    """
    Understand computational demands and patterns.

    Analyzes how work can be distributed computationally.
    """
    profile = state.get("resource_profile", {})

    workload = {
        "type": "parallel" if profile.get("cpu_intensive") else "sequential",
        "distribution": "data_parallel" if profile.get("memory_intensive") else "task_parallel",
        "parallelism_degree": profile.get("estimated_compute_units", 1)
    }

    return {"workload_analysis": workload}


def plan_distribution(state: ComputationalState) -> Dict[str, Any]:
    """
    Create distribution strategy for computational resources.

    Plans how to distribute work across compute resources.
    """
    workload = state.get("workload_analysis", {})
    technique = state["selected_technique"]

    # Distribution based on technique
    strategy = {
        "technique": technique.get("name", ""),
        "partitions": workload.get("parallelism_degree", 1),
        "communication_pattern": "reduce" if "Data Parallelism" in technique.get("name", "") else "peer_to_peer"
    }

    return {"distribution_strategy": strategy}


def create_subproblems(state: ComputationalState) -> Dict[str, Any]:
    """
    Generate subproblems from distribution strategy.

    Converts computational partitions into subproblems.
    """
    problem = state["original_problem"]
    strategy = state.get("distribution_strategy", {})
    technique = state["selected_technique"]

    partition_count = strategy.get("partitions", 4)
    subproblems: List[Subproblem] = []

    for i in range(partition_count):
        subproblem_id = f"computational_{i+1}_{str(uuid.uuid4())[:8]}"

        subproblem: Subproblem = {
            "id": subproblem_id,
            "title": f"Implement Compute Partition {i+1}",
            "description": (
                f"Implement computational partition {i+1} of {partition_count}. "
                f"This partition handles a portion of the computational workload "
                f"using {technique['name']} pattern. "
                f"Communication pattern: {strategy.get('communication_pattern', 'default')}."
            ),
            "paradigm": "computational",
            "source_technique": technique["name"],
            "status": SubproblemStatus.PENDING,
            "dependencies": [],  # Computational partitions often independent
            "estimated_complexity": "high" if i == 0 else "medium",
            "confidence": 0.84,
            "metadata": {
                "partition_index": i,
                "total_partitions": partition_count,
                "communication_pattern": strategy.get("communication_pattern")
            }
        }
        subproblems.append(subproblem)

    return {"subproblems": subproblems}


def create_computational_decomposition_graph() -> StateGraph:
    """
    Create the computational decomposition subgraph.

    Returns:
        StateGraph configured for computational decomposition
    """
    graph = StateGraph(ComputationalState)

    graph.add_node("profile_resources", profile_resources)
    graph.add_node("analyze_workload", analyze_workload)
    graph.add_node("plan_distribution", plan_distribution)
    graph.add_node("create_subproblems", create_subproblems)

    graph.set_entry_point("profile_resources")
    graph.add_edge("profile_resources", "analyze_workload")
    graph.add_edge("analyze_workload", "plan_distribution")
    graph.add_edge("plan_distribution", "create_subproblems")
    graph.add_edge("create_subproblems", END)

    return graph.compile()
