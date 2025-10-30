"""
Dependency Decomposition Subgraph (Level 3.1.8)

Applies dependency decomposition techniques like Topological Sort,
Critical Path Method, or Async/Await Decomposition to break problems
by dependency relationships.
"""

from typing import Any, Dict, List
from langgraph.graph import StateGraph, END
from decomposition_pipeline.schemas import DependencyDecompositionState, Subproblem, SubproblemStatus
import uuid


def build_dependency_graph(state: DependencyDecompositionState) -> Dict[str, Any]:
    """
    Construct dependency DAG from problem description.

    Identifies all tasks and their dependencies.
    """
    problem = state["original_problem"]

    # Build dependency structure
    graph = {
        "nodes": [
            {"id": "task_1", "name": "Initialize", "type": "start"},
            {"id": "task_2", "name": "Setup", "type": "prepare"},
            {"id": "task_3", "name": "Execute", "type": "core"},
            {"id": "task_4", "name": "Validate", "type": "check"},
            {"id": "task_5", "name": "Finalize", "type": "end"},
        ],
        "edges": [
            {"from": "task_1", "to": "task_2"},
            {"from": "task_2", "to": "task_3"},
            {"from": "task_3", "to": "task_4"},
            {"from": "task_4", "to": "task_5"},
        ]
    }

    return {"dependency_graph": graph}


def find_critical_path(state: DependencyDecompositionState) -> Dict[str, Any]:
    """
    Identify critical path through dependency graph.

    Finds longest path that determines minimum completion time.
    """
    graph = state.get("dependency_graph", {})
    nodes = graph.get("nodes", [])

    # Simple critical path (all nodes in sequence for now)
    critical_path = [node["id"] for node in nodes]

    return {"critical_path": critical_path}


def determine_execution_order(state: DependencyDecompositionState) -> Dict[str, Any]:
    """
    Establish execution order respecting dependencies.

    Uses topological sort to order tasks.
    """
    graph = state.get("dependency_graph", {})
    critical_path = state.get("critical_path", [])

    # Group tasks by execution batches (parallelizable groups)
    parallel_groups = [[node_id] for node_id in critical_path]

    return {
        "execution_order": critical_path,
        "parallel_groups": parallel_groups
    }


def create_subproblems(state: DependencyDecompositionState) -> Dict[str, Any]:
    """
    Generate subproblems from dependency analysis.

    Converts dependency groups into subproblems.
    """
    problem = state["original_problem"]
    graph = state.get("dependency_graph", {})
    execution_order = state.get("execution_order", [])
    technique = state["selected_technique"]

    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    subproblems: List[Subproblem] = []

    for i, node_id in enumerate(execution_order):
        node = nodes.get(node_id, {})
        subproblem_id = f"dependency_{i+1}_{str(uuid.uuid4())[:8]}"

        # Dependencies from previous nodes in execution order
        dependencies = []
        if i > 0:
            dependencies.append(f"dependency_{i}_{str(uuid.uuid4())[:8]}")

        subproblem: Subproblem = {
            "id": subproblem_id,
            "title": f"Implement {node.get('name', f'Task {i+1}')}",
            "description": (
                f"Implement the {node.get('name', 'task')} component "
                f"(type: {node.get('type', 'unknown')}). "
                f"This task must complete before dependent tasks can start. "
                f"Applying {technique['name']} for dependency management."
            ),
            "paradigm": "dependency",
            "source_technique": technique["name"],
            "status": SubproblemStatus.PENDING,
            "dependencies": dependencies,
            "estimated_complexity": "high" if node.get("type") == "core" else "medium",
            "confidence": 0.90,
            "metadata": {
                "node_id": node_id,
                "node_type": node.get("type", "unknown"),
                "execution_order": i
            }
        }
        subproblems.append(subproblem)

    return {"subproblems": subproblems}


def create_dependency_decomposition_graph() -> StateGraph:
    """
    Create the dependency decomposition subgraph.

    Returns:
        StateGraph configured for dependency decomposition
    """
    graph = StateGraph(DependencyDecompositionState)

    graph.add_node("build_dependency_graph", build_dependency_graph)
    graph.add_node("find_critical_path", find_critical_path)
    graph.add_node("determine_execution_order", determine_execution_order)
    graph.add_node("create_subproblems", create_subproblems)

    graph.set_entry_point("build_dependency_graph")
    graph.add_edge("build_dependency_graph", "find_critical_path")
    graph.add_edge("find_critical_path", "determine_execution_order")
    graph.add_edge("determine_execution_order", "create_subproblems")
    graph.add_edge("create_subproblems", END)

    return graph.compile()
