"""
Data Decomposition Subgraph (Level 3.1.7)

Applies data decomposition techniques like Horizontal Partitioning,
Vertical Partitioning, or Feature Decomposition to break problems
by data organization.
"""

from typing import Any, Dict, List
from langgraph.graph import StateGraph, END
from decomposition_pipeline.schemas import DataState, Subproblem, SubproblemStatus
import uuid


def analyze_schema(state: DataState) -> Dict[str, Any]:
    """
    Understand data structure and organization.

    Analyzes the data schema and relationships.
    """
    problem = state["original_problem"]

    # Extract schema characteristics
    schema = {
        "entities": ["users", "transactions", "products"],
        "relationships": [
            {"from": "users", "to": "transactions", "type": "one_to_many"},
            {"from": "transactions", "to": "products", "type": "many_to_many"}
        ],
        "volume": "large" if "large" in problem.lower() else "medium"
    }

    return {"schema_analysis": schema}


def identify_partition_keys(state: DataState) -> Dict[str, Any]:
    """
    Find optimal partitioning keys for data.

    Identifies how to split data for independent processing.
    """
    schema = state.get("schema_analysis", {})
    technique = state["selected_technique"]

    # Determine partition keys based on technique
    if "Horizontal" in technique.get("name", ""):
        keys = ["user_id", "timestamp", "region"]
    elif "Vertical" in technique.get("name", ""):
        keys = ["frequently_accessed_columns", "rarely_accessed_columns"]
    else:  # Feature Decomposition
        keys = ["feature_group_1", "feature_group_2", "feature_group_3"]

    return {"partition_keys": keys}


def plan_splitting(state: DataState) -> Dict[str, Any]:
    """
    Create data splitting strategy.

    Plans how to partition data according to technique.
    """
    keys = state.get("partition_keys", [])
    technique = state["selected_technique"]

    strategy = {
        "method": technique.get("name", ""),
        "partition_count": len(keys),
        "keys": keys,
        "distribution": "hash" if "Hash" in technique.get("name", "") else "range"
    }

    return {"splitting_strategy": strategy}


def create_subproblems(state: DataState) -> Dict[str, Any]:
    """
    Generate subproblems from data partitions.

    Converts each data partition into a subproblem.
    """
    problem = state["original_problem"]
    strategy = state.get("splitting_strategy", {})
    keys = strategy.get("keys", [])
    technique = state["selected_technique"]

    subproblems: List[Subproblem] = []

    for i, key in enumerate(keys):
        subproblem_id = f"data_{i+1}_{str(uuid.uuid4())[:8]}"

        subproblem: Subproblem = {
            "id": subproblem_id,
            "title": f"Implement Data Partition: {key}",
            "description": (
                f"Implement data partition based on key: {key}. "
                f"This partition handles a subset of the data using "
                f"{technique['name']} strategy. "
                f"Distribution method: {strategy.get('distribution', 'default')}."
            ),
            "paradigm": "data",
            "source_technique": technique["name"],
            "status": SubproblemStatus.PENDING,
            "dependencies": [],  # Data partitions typically independent
            "estimated_complexity": "medium",
            "confidence": 0.87,
            "metadata": {
                "partition_key": key,
                "partition_index": i,
                "total_partitions": len(keys)
            }
        }
        subproblems.append(subproblem)

    return {"subproblems": subproblems}


def create_data_decomposition_graph() -> StateGraph:
    """
    Create the data decomposition subgraph.

    Returns:
        StateGraph configured for data decomposition
    """
    graph = StateGraph(DataState)

    graph.add_node("analyze_schema", analyze_schema)
    graph.add_node("identify_partition_keys", identify_partition_keys)
    graph.add_node("plan_splitting", plan_splitting)
    graph.add_node("create_subproblems", create_subproblems)

    graph.set_entry_point("analyze_schema")
    graph.add_edge("analyze_schema", "identify_partition_keys")
    graph.add_edge("identify_partition_keys", "plan_splitting")
    graph.add_edge("plan_splitting", "create_subproblems")
    graph.add_edge("create_subproblems", END)

    return graph.compile()
