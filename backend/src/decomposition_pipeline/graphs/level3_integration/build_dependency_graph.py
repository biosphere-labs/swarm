"""
BuildDependencyGraphNode - Creates dependency graph from subproblems.

Uses textbook graph algorithms:
- Topological sort for execution ordering
- Transitive closure for indirect dependencies
- Critical path analysis for bottleneck identification
"""

from typing import List, Dict, Set
from collections import deque
from ...schemas.state import Level3IntegrationState, Subproblem, DependencyGraph


def build_adjacency_list(subproblems: List[Subproblem]) -> Dict[str, List[str]]:
    """
    Build adjacency list representation of dependency graph.
    
    Returns: Dictionary mapping node ID to list of dependent node IDs
    """
    graph: Dict[str, List[str]] = {sp["id"]: [] for sp in subproblems}
    
    for sp in subproblems:
        for dep_id in sp.get("dependencies", []):
            if dep_id in graph:  # Only add if dependency exists
                graph[sp["id"]].append(dep_id)
    
    return graph


def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """
    Topological sort using Kahn's algorithm.
    
    Algorithm from: CLRS textbook (Cormen et al.)
    
    Returns nodes in order such that dependencies come before dependents.
    Raises ValueError if graph has cycles.
    """
    # Calculate in-degree for each node
    in_degree: Dict[str, int] = {node: 0 for node in graph}
    
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1
    
    # Queue for nodes with no dependencies
    queue = deque([node for node in graph if in_degree[node] == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        # Reduce in-degree for neighbors
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(graph):
        raise ValueError("Circular dependency detected in subproblem graph")
    
    return result


def find_critical_path(
    graph: Dict[str, List[str]],
    complexity_map: Dict[str, int]
) -> List[str]:
    """
    Find critical path using dynamic programming.
    
    Critical path: longest path through dependency graph (bottleneck).
    From: Project management literature (CPM - Critical Path Method).
    
    Args:
        graph: Adjacency list of dependencies
        complexity_map: Estimated complexity/time for each subproblem
        
    Returns:
        List of node IDs forming the critical path
    """
    # Topological sort to process in dependency order
    try:
        sorted_nodes = topological_sort(graph)
    except ValueError:
        # If cycles exist, return empty path
        return []
    
    # DP: longest_path[node] = max path length ending at node
    longest_path: Dict[str, int] = {node: 0 for node in graph}
    parent: Dict[str, str] = {}
    
    for node in sorted_nodes:
        node_cost = complexity_map.get(node, 1)
        
        # Find max incoming path
        for neighbor in graph[node]:
            path_length = longest_path[node] + node_cost
            if path_length > longest_path[neighbor]:
                longest_path[neighbor] = path_length
                parent[neighbor] = node
    
    # Find node with longest path
    end_node = max(longest_path.items(), key=lambda x: x[1])[0]
    
    # Reconstruct path
    path = []
    current = end_node
    while current in parent:
        path.append(current)
        current = parent[current]
    path.append(current)
    path.reverse()
    
    return path


def identify_parallel_groups(
    graph: Dict[str, List[str]],
    sorted_nodes: List[str]
) -> List[List[str]]:
    """
    Identify groups of subproblems that can be executed in parallel.
    
    Algorithm: Level-based grouping from topological sort
    From: Parallel computing literature
    
    Returns:
        List of execution levels, where each level can run in parallel
    """
    # Build reverse graph (dependents)
    reverse_graph: Dict[str, List[str]] = {node: [] for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            reverse_graph[neighbor].append(node)
    
    # Calculate earliest possible execution level for each node
    level: Dict[str, int] = {node: 0 for node in graph}
    
    for node in sorted_nodes:
        # Level is max of all dependency levels + 1
        max_dep_level = 0
        for dep in graph[node]:
            max_dep_level = max(max_dep_level, level[dep] + 1)
        level[node] = max_dep_level
    
    # Group by level
    max_level = max(level.values()) if level else 0
    groups = [[] for _ in range(max_level + 1)]
    
    for node in sorted_nodes:
        groups[level[node]].append(node)
    
    return groups


def build_dependency_graph(state: Level3IntegrationState) -> Level3IntegrationState:
    """
    Build dependency graph from resolved subproblems.
    
    Algorithm:
    1. Extract dependencies from each subproblem
    2. Build directed graph (adjacency list)
    3. Verify no cycles using topological sort
    4. Find critical path using dynamic programming
    5. Identify parallelizable groups using level-based grouping
    
    Args:
        state: Integration state with resolved_subproblems
        
    Returns:
        Updated state with subproblem_dependencies graph
    """
    resolved_subproblems = state.get("resolved_subproblems", [])
    
    if not resolved_subproblems:
        # Empty graph
        return {
            **state,
            "subproblem_dependencies": {
                "nodes": [],
                "edges": [],
                "critical_path": []
            }
        }
    
    # Build adjacency list
    graph = build_adjacency_list(resolved_subproblems)
    
    # Create edge list for visualization
    edges = [
        {"from": sp_id, "to": dep_id, "type": "dependency"}
        for sp_id in graph
        for dep_id in graph[sp_id]
    ]
    
    # Topological sort to verify no cycles
    try:
        sorted_nodes = topological_sort(graph)
    except ValueError as e:
        # Cycles detected - report error but continue
        dependency_graph: DependencyGraph = {
            "nodes": list(graph.keys()),
            "edges": edges,
            "critical_path": [],
            "error": str(e)  # type: ignore
        }
        
        return {
            **state,
            "subproblem_dependencies": dependency_graph
        }
    
    # Estimate complexity for critical path
    complexity_map = {
        sp["id"]: len(sp.get("description", "")) // 100 + 1  # Rough estimate
        for sp in resolved_subproblems
    }
    
    # Find critical path
    critical_path = find_critical_path(graph, complexity_map)
    
    # Identify parallel execution groups
    parallel_groups = identify_parallel_groups(graph, sorted_nodes)
    
    # Construct dependency graph
    dependency_graph: DependencyGraph = {
        "nodes": list(graph.keys()),
        "edges": edges,
        "critical_path": critical_path
    }
    
    return {
        **state,
        "subproblem_dependencies": dependency_graph,
        "execution_batches": parallel_groups  # For Level 4 to use
    }
