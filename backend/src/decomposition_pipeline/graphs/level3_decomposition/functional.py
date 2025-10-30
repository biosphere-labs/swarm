"""
Functional Decomposition Subgraph (Level 3.1.2)

Applies functional decomposition techniques like MapReduce, Fork-Join,
Pipeline Decomposition, or Task Parallelism to break problems into
functional operations.
"""

from typing import Any, Dict, List
from langgraph.graph import StateGraph, END
from decomposition_pipeline.schemas import FunctionalState, Subproblem, SubproblemStatus
import uuid


def identify_operations(state: FunctionalState) -> Dict[str, Any]:
    """
    Enumerate all operations and functions needed to solve the problem.

    Identifies distinct functional tasks that can be performed.
    """
    problem = state["original_problem"]
    technique = state["selected_technique"]

    # Extract operations from problem description
    operations = []

    # Common operation patterns
    if "process" in problem.lower() or "transform" in problem.lower():
        operations.extend([
            {"id": "op_1", "name": "Data Ingestion", "type": "input"},
            {"id": "op_2", "name": "Data Transformation", "type": "transform"},
            {"id": "op_3", "name": "Data Validation", "type": "validate"},
            {"id": "op_4", "name": "Result Aggregation", "type": "aggregate"},
        ])
    elif "calculate" in problem.lower() or "compute" in problem.lower():
        operations.extend([
            {"id": "op_1", "name": "Input Parsing", "type": "parse"},
            {"id": "op_2", "name": "Computation", "type": "compute"},
            {"id": "op_3", "name": "Result Formatting", "type": "format"},
        ])
    else:
        # Generic operations
        operations.extend([
            {"id": "op_1", "name": "Receive Input", "type": "input"},
            {"id": "op_2", "name": "Process Data", "type": "process"},
            {"id": "op_3", "name": "Generate Output", "type": "output"},
        ])

    return {
        "identified_operations": operations
    }


def analyze_dependencies(state: FunctionalState) -> Dict[str, Any]:
    """
    Analyze dependencies between operations.

    Determines which operations must complete before others can start.
    """
    operations = state.get("identified_operations", [])

    # Build dependency graph
    dependencies = []
    for i in range(len(operations) - 1):
        # Sequential dependency by default
        dependencies.append({
            "from": operations[i]["id"],
            "to": operations[i + 1]["id"],
            "type": "sequential",
            "required": True
        })

    return {
        "operation_dependencies": dependencies
    }


def group_tasks(state: FunctionalState) -> Dict[str, Any]:
    """
    Group related operations into task groups.

    Clusters operations that can be executed together or in parallel.
    """
    operations = state.get("identified_operations", [])
    dependencies = state.get("operation_dependencies", [])
    technique = state["selected_technique"]

    technique_name = technique.get("name", "")

    # Group based on technique
    if "MapReduce" in technique_name:
        task_groups = [
            {"id": "map_tasks", "operations": [op["id"] for op in operations if op["type"] in ["input", "parse", "transform"]], "phase": "map"},
            {"id": "reduce_tasks", "operations": [op["id"] for op in operations if op["type"] in ["aggregate", "compute"]], "phase": "reduce"},
            {"id": "output_tasks", "operations": [op["id"] for op in operations if op["type"] in ["output", "format"]], "phase": "output"},
        ]
    elif "Fork-Join" in technique_name:
        task_groups = [
            {"id": "fork_task", "operations": [operations[0]["id"]], "phase": "fork"},
            {"id": "parallel_tasks", "operations": [op["id"] for op in operations[1:-1]], "phase": "parallel"},
            {"id": "join_task", "operations": [operations[-1]["id"]], "phase": "join"},
        ]
    elif "Pipeline" in technique_name:
        task_groups = [
            {"id": f"stage_{i}", "operations": [op["id"]], "phase": f"stage{i}"}
            for i, op in enumerate(operations)
        ]
    else:  # Task Parallelism
        task_groups = [
            {"id": f"task_{op['id']}", "operations": [op["id"]], "phase": "independent"}
            for op in operations
        ]

    return {
        "task_groups": task_groups
    }


def create_subproblems(state: FunctionalState) -> Dict[str, Any]:
    """
    Generate subproblems from task groups.

    Converts each task group into a concrete subproblem.
    """
    problem = state["original_problem"]
    task_groups = state.get("task_groups", [])
    operations = state.get("identified_operations", [])
    technique = state["selected_technique"]

    subproblems: List[Subproblem] = []

    for i, group in enumerate(task_groups):
        group_operations = group.get("operations", [])
        operation_names = [
            op["name"] for op in operations if op["id"] in group_operations
        ]

        subproblem_id = f"functional_{i+1}_{str(uuid.uuid4())[:8]}"

        # Determine dependencies
        dependencies = []
        if i > 0 and technique["name"] != "Task Parallelism":
            # Sequential dependency for non-parallel techniques
            dependencies.append(f"functional_{i}_{str(uuid.uuid4())[:8]}")

        phase = group.get("phase", "")
        subproblem: Subproblem = {
            "id": subproblem_id,
            "title": f"Implement {phase.capitalize()} Operations",
            "description": (
                f"Implement the following functional operations: "
                f"{', '.join(operation_names)}. "
                f"These operations are part of the {phase} phase "
                f"using {technique['name']} pattern."
            ),
            "paradigm": "functional",
            "source_technique": technique["name"],
            "status": SubproblemStatus.PENDING,
            "dependencies": dependencies,
            "estimated_complexity": "medium",
            "confidence": 0.88,
            "metadata": {
                "group_id": group["id"],
                "operation_count": len(group_operations),
                "phase": phase
            }
        }
        subproblems.append(subproblem)

    return {
        "subproblems": subproblems
    }


def create_functional_decomposition_graph() -> StateGraph:
    """
    Create the functional decomposition subgraph.

    Returns:
        StateGraph configured for functional decomposition
    """
    graph = StateGraph(FunctionalState)

    # Add nodes
    graph.add_node("identify_operations", identify_operations)
    graph.add_node("analyze_dependencies", analyze_dependencies)
    graph.add_node("group_tasks", group_tasks)
    graph.add_node("create_subproblems", create_subproblems)

    # Add edges
    graph.set_entry_point("identify_operations")
    graph.add_edge("identify_operations", "analyze_dependencies")
    graph.add_edge("analyze_dependencies", "group_tasks")
    graph.add_edge("group_tasks", "create_subproblems")
    graph.add_edge("create_subproblems", END)

    return graph.compile()
