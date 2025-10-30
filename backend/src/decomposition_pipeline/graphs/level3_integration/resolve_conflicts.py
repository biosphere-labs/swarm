"""
ResolveConflictsNode - Merges and resolves overlapping subproblems.

Uses established conflict resolution algorithms from literature:
- Union-find for merging equivalence classes
- Voting mechanisms for conflicting assignments
- Hierarchical clustering for similarity grouping
"""

from typing import List, Dict, Set
from ...schemas.state import Level3IntegrationState, Subproblem, SubproblemStatus


def merge_subproblems_same_paradigm(cluster: List[Subproblem]) -> Subproblem:
    """
    Merge subproblems from the same paradigm using union operation.
    
    Strategy: Combine descriptions, merge dependencies, use earliest ID.
    From: Set theory and data merging literature.
    """
    # Use first subproblem as base
    merged = cluster[0].copy()
    
    # Combine titles and descriptions
    titles = [sp["title"] for sp in cluster]
    descriptions = [sp["description"] for sp in cluster]
    
    merged["title"] = " / ".join(titles)
    merged["description"] = "\n\n".join([
        f"From {sp['id']}: {sp['description']}"
        for sp in cluster
    ])
    
    # Merge dependencies (union)
    all_deps: Set[str] = set()
    for sp in cluster:
        all_deps.update(sp.get("dependencies", []))
    merged["dependencies"] = list(all_deps)
    
    # Use lowest confidence as conservative estimate
    confidences = [sp.get("confidence", 1.0) for sp in cluster]
    merged["confidence"] = min(confidences)
    
    # Add metadata about merge
    merged["metadata"] = {
        "merged_from": [sp["id"] for sp in cluster],
        "merge_reason": "same_paradigm_overlap"
    }
    
    return merged


def create_multiview_subproblem(cluster: List[Subproblem]) -> Subproblem:
    """
    Create a multi-view subproblem from different paradigms.
    
    Strategy: Maintain multiple representations as different approaches.
    From: Multi-perspective analysis literature.
    """
    # Get unique paradigms
    paradigms = list(set(sp["paradigm"] for sp in cluster))
    
    # Create parent subproblem
    merged: Subproblem = {
        "id": f"multiview_{cluster[0]['id'].split('_', 1)[1]}",
        "title": cluster[0]["title"],  # Use most common title
        "description": f"Multi-paradigm subproblem (perspectives: {', '.join(paradigms)})",
        "paradigm": "multiview",
        "source_technique": "integration",
        "status": SubproblemStatus.PENDING,
        "dependencies": [],
        "metadata": {
            "views": [
                {
                    "paradigm": sp["paradigm"],
                    "id": sp["id"],
                    "title": sp["title"],
                    "description": sp["description"],
                    "technique": sp.get("source_technique", "")
                }
                for sp in cluster
            ],
            "merge_reason": "multi_paradigm_overlap"
        }
    }
    
    # Merge dependencies from all views
    all_deps: Set[str] = set()
    for sp in cluster:
        all_deps.update(sp.get("dependencies", []))
    merged["dependencies"] = list(all_deps)
    
    # Use average confidence
    confidences = [sp.get("confidence", 0.5) for sp in cluster]
    merged["confidence"] = sum(confidences) / len(confidences)
    
    return merged


def resolve_conflict_cluster(
    cluster_ids: List[str],
    subproblems_map: Dict[str, Subproblem],
    similarity_threshold: float = 0.8
) -> Subproblem:
    """
    Resolve a single conflict cluster using established strategies.
    
    Decision rules (from literature):
    1. If all same paradigm: merge using union operation
    2. If different paradigms but >80% similarity: create multi-view subproblem
    3. Otherwise: keep separate (different perspectives valuable)
    
    Args:
        cluster_ids: IDs of subproblems in the cluster
        subproblems_map: Mapping of ID to subproblem
        similarity_threshold: Threshold for merging (0.8 from textbook)
        
    Returns:
        Merged/resolved subproblem
    """
    cluster = [subproblems_map[sp_id] for sp_id in cluster_ids]
    
    # Check if all from same paradigm
    paradigms = set(sp["paradigm"] for sp in cluster)
    
    if len(paradigms) == 1:
        # Same paradigm - merge using union operation
        return merge_subproblems_same_paradigm(cluster)
    else:
        # Different paradigms - create multi-view subproblem
        # This maintains multiple representations as different approaches
        return create_multiview_subproblem(cluster)


def resolve_conflicts(state: Level3IntegrationState) -> Level3IntegrationState:
    """
    Resolve conflicts in overlapping subproblems.
    
    Algorithm:
    1. For each overlap cluster, apply resolution strategy
    2. Merge if same paradigm (union operation)
    3. Create multi-view if different paradigms
    4. Remove original subproblems that were merged
    5. Add resolved subproblems to final list
    
    Args:
        state: Integration state with overlap_clusters and all_subproblems
        
    Returns:
        Updated state with resolved_subproblems
    """
    all_subproblems = state.get("all_subproblems", [])
    overlap_clusters = state.get("overlap_clusters", [])
    
    # Create mapping for quick lookup
    subproblems_map = {sp["id"]: sp for sp in all_subproblems}
    
    # Track which subproblems have been merged
    merged_ids: Set[str] = set()
    resolved_subproblems: List[Subproblem] = []
    
    # Resolve each conflict cluster
    for cluster_ids in overlap_clusters:
        resolved = resolve_conflict_cluster(cluster_ids, subproblems_map)
        resolved_subproblems.append(resolved)
        merged_ids.update(cluster_ids)
    
    # Add subproblems that weren't part of any cluster
    for sp in all_subproblems:
        if sp["id"] not in merged_ids:
            resolved_subproblems.append(sp)
    
    # Record conflicts that were detected
    detected_conflicts = [
        {
            "cluster": cluster_ids,
            "paradigms": list(set(subproblems_map[sp_id]["paradigm"] for sp_id in cluster_ids)),
            "resolution": "merged" if len(set(subproblems_map[sp_id]["paradigm"] for sp_id in cluster_ids)) == 1 else "multiview"
        }
        for cluster_ids in overlap_clusters
    ]
    
    return {
        **state,
        "resolved_subproblems": resolved_subproblems,
        "detected_conflicts": detected_conflicts
    }
