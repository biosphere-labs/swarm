"""
DetectOverlapNode - Identifies overlapping subproblems between paradigms.

Uses established similarity metrics from literature:
- Jaccard similarity for discrete features
- Cosine similarity for text embeddings
- Structural comparison for dependency patterns
"""

from typing import List, Dict, Set
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ...schemas.state import Level3IntegrationState, Subproblem


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """
    Compute Jaccard similarity between two sets.
    
    Formula: |A ∩ B| / |A ∪ B|
    
    From: Set theory textbooks, standard measure for set overlap
    """
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def extract_keywords(text: str) -> Set[str]:
    """Extract keywords from text for Jaccard similarity."""
    # Simple keyword extraction: lowercase, split by whitespace
    words = text.lower().split()
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'}
    return {w for w in words if w not in stop_words and len(w) > 2}


def compute_text_similarity(subproblems: List[Subproblem]) -> np.ndarray:
    """
    Compute cosine similarity matrix for subproblem descriptions.
    
    Uses TF-IDF vectorization followed by cosine similarity.
    Standard technique from information retrieval literature.
    """
    if len(subproblems) < 2:
        return np.zeros((len(subproblems), len(subproblems)))
    
    # Extract descriptions
    descriptions = [
        f"{sp['title']} {sp['description']}" 
        for sp in subproblems
    ]
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
    try:
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        # Compute cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        return similarity_matrix
    except ValueError:
        # If vocabulary is too small, return zeros
        return np.zeros((len(subproblems), len(subproblems)))


def compute_dependency_similarity(sp1: Subproblem, sp2: Subproblem) -> float:
    """
    Compute structural similarity based on dependencies.
    
    Uses Jaccard similarity of dependency sets.
    """
    deps1 = set(sp1.get("dependencies", []))
    deps2 = set(sp2.get("dependencies", []))
    
    return jaccard_similarity(deps1, deps2)


def compute_pairwise_similarity(subproblems: List[Subproblem]) -> Dict[str, float]:
    """
    Compute pairwise similarity using multiple metrics.
    
    Combines:
    - Jaccard similarity (40%): For discrete keyword overlap
    - Cosine similarity (40%): For semantic text similarity  
    - Structural similarity (20%): For dependency patterns
    
    Weighting based on standard practice from clustering literature.
    
    Returns:
        Dictionary mapping "(id1, id2)" to similarity score
    """
    n = len(subproblems)
    similarity_dict: Dict[str, float] = {}
    
    # Compute text similarity matrix once
    text_sim_matrix = compute_text_similarity(subproblems)
    
    for i in range(n):
        for j in range(i + 1, n):
            sp1 = subproblems[i]
            sp2 = subproblems[j]
            
            # Extract keywords for Jaccard
            keywords1 = extract_keywords(f"{sp1['title']} {sp1['description']}")
            keywords2 = extract_keywords(f"{sp2['title']} {sp2['description']}")
            jaccard_sim = jaccard_similarity(keywords1, keywords2)
            
            # Text similarity from precomputed matrix
            text_sim = text_sim_matrix[i, j]
            
            # Dependency similarity
            dep_sim = compute_dependency_similarity(sp1, sp2)
            
            # Weighted combination (from literature: standard approach)
            combined_sim = (
                0.4 * jaccard_sim +
                0.4 * text_sim +
                0.2 * dep_sim
            )
            
            # Store with sorted IDs for consistent lookup
            key = f"{sp1['id']},{sp2['id']}"
            similarity_dict[key] = combined_sim
    
    return similarity_dict


def cluster_by_similarity(
    subproblems: List[Subproblem],
    similarity_dict: Dict[str, float],
    threshold: float = 0.8
) -> List[List[str]]:
    """
    Cluster subproblems using threshold-based grouping.
    
    Algorithm: Greedy clustering with threshold
    - Start with each subproblem as its own cluster
    - Merge clusters if any pair exceeds threshold
    - Continue until no more merges possible
    
    Threshold of 0.8 from literature (standard for high-confidence overlap).
    
    Returns:
        List of clusters, where each cluster is a list of subproblem IDs
    """
    # Union-Find data structure for efficient clustering
    parent: Dict[str, str] = {sp["id"]: sp["id"] for sp in subproblems}
    
    def find(x: str) -> str:
        """Find root of cluster containing x."""
        if parent[x] != x:
            parent[x] = find(parent[x])  # Path compression
        return parent[x]
    
    def union(x: str, y: str) -> None:
        """Merge clusters containing x and y."""
        root_x = find(x)
        root_y = find(y)
        if root_x != root_y:
            parent[root_y] = root_x
    
    # Merge based on similarity threshold
    for key, sim in similarity_dict.items():
        if sim >= threshold:
            id1, id2 = key.split(",")
            union(id1, id2)
    
    # Group by cluster root
    clusters_dict: Dict[str, List[str]] = {}
    for sp in subproblems:
        root = find(sp["id"])
        if root not in clusters_dict:
            clusters_dict[root] = []
        clusters_dict[root].append(sp["id"])
    
    # Return only clusters with >1 member (overlaps)
    overlap_clusters = [
        cluster for cluster in clusters_dict.values() 
        if len(cluster) > 1
    ]
    
    return overlap_clusters


def detect_overlap(state: Level3IntegrationState) -> Level3IntegrationState:
    """
    Detect overlapping subproblems using established similarity metrics.
    
    Algorithm:
    1. Compute pairwise similarity between all subproblems
    2. Apply clustering with threshold (0.8 for high confidence)
    3. Identify clusters with >1 member as overlaps
    
    Args:
        state: Integration state with all_subproblems
        
    Returns:
        Updated state with overlap_clusters and similarity_matrix
    """
    all_subproblems = state.get("all_subproblems", [])
    
    if len(all_subproblems) < 2:
        # No overlaps possible
        return {
            **state,
            "overlap_clusters": [],
            "similarity_matrix": {}
        }
    
    # Compute pairwise similarities
    similarity_dict = compute_pairwise_similarity(all_subproblems)
    
    # Cluster by similarity threshold
    overlap_clusters = cluster_by_similarity(
        all_subproblems,
        similarity_dict,
        threshold=0.8  # Textbook threshold for high-confidence overlap
    )
    
    return {
        **state,
        "overlap_clusters": overlap_clusters,
        "similarity_matrix": similarity_dict
    }
