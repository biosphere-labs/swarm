"""
Routing logic for selecting optimal agent pools for subproblems.

This module implements the pool selection strategy:
1. Check paradigm pool first (if subproblem has source_paradigm)
2. Score domain matches for domain pools
3. Use general pool as fallback

The routing is rule-based using keyword matching and semantic analysis.
"""

import logging
import re
from typing import Dict, List, Any, Optional

from .agent_types import AgentPool, PARADIGM_POOL_CONFIGS, DOMAIN_POOL_CONFIGS

logger = logging.getLogger(__name__)

# Domain keyword mappings for matching
DOMAIN_KEYWORDS = {
    "api_design": [
        "api", "rest", "graphql", "endpoint", "route", "http", "request",
        "response", "service", "microservice", "rpc", "grpc", "swagger",
        "openapi", "interface", "contract"
    ],
    "data_processing": [
        "data", "pipeline", "etl", "transform", "batch", "stream", "processing",
        "ingestion", "database", "sql", "query", "storage", "warehouse",
        "dataflow", "parse", "extract", "load", "clean", "aggregate"
    ],
    "ml_modeling": [
        "machine learning", "ml", "model", "training", "inference", "neural",
        "deep learning", "classification", "regression", "clustering",
        "prediction", "algorithm", "feature", "dataset", "accuracy",
        "tensorflow", "pytorch", "scikit"
    ],
    "security": [
        "security", "authentication", "authorization", "encryption", "decrypt",
        "cryptography", "token", "jwt", "oauth", "permission", "access control",
        "vulnerability", "attack", "secure", "privacy", "audit", "compliance"
    ],
}


def select_pool_for_subproblem(
    subproblem: Dict[str, Any],
    pools: Dict[str, AgentPool]
) -> str:
    """
    Select the most appropriate pool for a subproblem.

    Priority order:
    1. Paradigm pool (if source_paradigm specified and pool exists)
    2. Domain pool (if domain match score > 0.7)
    3. General pool (fallback)

    Args:
        subproblem: Dictionary with subproblem details including:
            - id: Subproblem identifier
            - title: Short description
            - description: Full description
            - source_paradigm: Optional paradigm that created this subproblem
            - domain: Optional explicit domain hint
        pools: Available agent pools

    Returns:
        Name of selected pool
    """
    # Strategy 1: Check paradigm pool first
    source_paradigm = subproblem.get("source_paradigm")
    if source_paradigm and source_paradigm in pools:
        logger.info(
            f"Selected paradigm pool '{source_paradigm}' for subproblem "
            f"{subproblem.get('id')}"
        )
        return source_paradigm

    # Strategy 2: Check explicit domain hint
    explicit_domain = subproblem.get("domain")
    if explicit_domain and explicit_domain in pools:
        logger.info(
            f"Selected explicit domain pool '{explicit_domain}' for subproblem "
            f"{subproblem.get('id')}"
        )
        return explicit_domain

    # Strategy 3: Score domain matches
    domain_scores = {}
    for domain in DOMAIN_POOL_CONFIGS.keys():
        if domain in pools:
            score = score_domain_match(subproblem, domain)
            domain_scores[domain] = score

    if domain_scores:
        best_domain, best_score = max(domain_scores.items(), key=lambda x: x[1])

        if best_score > 0.2:  # Lower threshold for better matching
            logger.info(
                f"Selected domain pool '{best_domain}' for subproblem "
                f"{subproblem.get('id')} (score: {best_score:.2f})"
            )
            return best_domain

    # Strategy 4: Fallback to general pool
    logger.info(
        f"Selected general pool for subproblem {subproblem.get('id')} "
        f"(no strong domain match)"
    )
    return "general"


def score_domain_match(subproblem: Dict[str, Any], domain: str) -> float:
    """
    Score how well a subproblem matches a domain.

    Uses keyword matching and text analysis.

    Args:
        subproblem: Subproblem dictionary
        domain: Domain name to score against

    Returns:
        Score between 0.0 and 1.0
    """
    # Get text to analyze
    text_parts = []

    title = subproblem.get("title", "")
    if title:
        text_parts.append(title)

    description = subproblem.get("description", "")
    if description:
        text_parts.append(description)

    if not text_parts:
        return 0.0

    combined_text = " ".join(text_parts).lower()

    # Get keywords for this domain
    keywords = DOMAIN_KEYWORDS.get(domain, [])
    if not keywords:
        return 0.0

    # Count keyword matches
    matches = 0
    total_keywords = len(keywords)

    for keyword in keywords:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, combined_text):
            matches += 1

    # Calculate score
    score = matches / total_keywords

    # Boost score if multiple keywords match (indicates stronger signal)
    if matches >= 3:
        score = min(score * 1.5, 1.0)

    return score


def should_use_general_pool(
    subproblem: Dict[str, Any],
    domain_scores: Dict[str, float]
) -> bool:
    """
    Determine if general pool should be used.

    General pool is used when:
    - No domain scores above threshold (0.7)
    - No explicit paradigm or domain specified
    - Problem is novel or complex

    Args:
        subproblem: Subproblem dictionary
        domain_scores: Pre-computed domain scores

    Returns:
        True if general pool should be used
    """
    # Check if any domain score is strong
    if domain_scores and max(domain_scores.values()) > 0.2:
        return False

    # Check for explicit routing
    if subproblem.get("source_paradigm") or subproblem.get("domain"):
        return False

    # Check complexity markers (keywords that suggest general pool)
    complexity_markers = [
        "novel", "complex", "unknown", "unclear", "ambiguous",
        "experimental", "research", "prototype", "exploratory"
    ]

    text = (
        subproblem.get("title", "") + " " +
        subproblem.get("description", "")
    ).lower()

    for marker in complexity_markers:
        if marker in text:
            logger.info(
                f"Detected complexity marker '{marker}' in subproblem "
                f"{subproblem.get('id')}, suggesting general pool"
            )
            return True

    return True


def get_routing_explanation(
    subproblem: Dict[str, Any],
    selected_pool: str,
    pools: Dict[str, AgentPool]
) -> Dict[str, Any]:
    """
    Generate detailed explanation of routing decision.

    Useful for debugging and observability.

    Args:
        subproblem: Subproblem dictionary
        selected_pool: Name of selected pool
        pools: Available pools

    Returns:
        Dictionary with routing decision explanation
    """
    explanation = {
        "subproblem_id": subproblem.get("id"),
        "selected_pool": selected_pool,
        "reasoning": [],
    }

    # Check paradigm routing
    source_paradigm = subproblem.get("source_paradigm")
    if source_paradigm:
        explanation["reasoning"].append({
            "strategy": "paradigm",
            "value": source_paradigm,
            "matched": source_paradigm == selected_pool
        })

    # Check explicit domain
    explicit_domain = subproblem.get("domain")
    if explicit_domain:
        explanation["reasoning"].append({
            "strategy": "explicit_domain",
            "value": explicit_domain,
            "matched": explicit_domain == selected_pool
        })

    # Check domain scores
    domain_scores = {}
    for domain in DOMAIN_POOL_CONFIGS.keys():
        if domain in pools:
            score = score_domain_match(subproblem, domain)
            domain_scores[domain] = score

    explanation["domain_scores"] = domain_scores

    if domain_scores:
        best_domain, best_score = max(domain_scores.items(), key=lambda x: x[1])
        explanation["reasoning"].append({
            "strategy": "domain_matching",
            "best_domain": best_domain,
            "best_score": best_score,
            "threshold": 0.7,
            "matched": best_domain == selected_pool and best_score > 0.7
        })

    # General pool fallback
    if selected_pool == "general":
        explanation["reasoning"].append({
            "strategy": "general_fallback",
            "reason": "No strong paradigm or domain match"
        })

    return explanation


def batch_route_subproblems(
    subproblems: List[Dict[str, Any]],
    pools: Dict[str, AgentPool]
) -> Dict[str, List[str]]:
    """
    Route multiple subproblems to pools in batch.

    Useful for analyzing routing patterns and load distribution.

    Args:
        subproblems: List of subproblem dictionaries
        pools: Available pools

    Returns:
        Dictionary mapping pool names to lists of subproblem IDs
    """
    routing = {pool_name: [] for pool_name in pools.keys()}

    for subproblem in subproblems:
        pool_name = select_pool_for_subproblem(subproblem, pools)
        subproblem_id = subproblem.get("id", "unknown")
        routing[pool_name].append(subproblem_id)

    # Log distribution
    logger.info("Batch routing complete:")
    for pool_name, subproblem_ids in routing.items():
        if subproblem_ids:
            logger.info(f"  {pool_name}: {len(subproblem_ids)} subproblems")

    return routing


def recommend_pool_scaling(
    routing: Dict[str, List[str]],
    pools: Dict[str, AgentPool]
) -> Dict[str, Dict[str, Any]]:
    """
    Recommend pool scaling based on routing distribution.

    Analyzes expected load and suggests pool size adjustments.

    Args:
        routing: Output from batch_route_subproblems
        pools: Current pools

    Returns:
        Dictionary with scaling recommendations per pool
    """
    recommendations = {}

    for pool_name, subproblem_ids in routing.items():
        pool = pools.get(pool_name)
        if not pool:
            continue

        expected_load = len(subproblem_ids)
        current_capacity = pool.config.size

        recommendation = {
            "expected_load": expected_load,
            "current_capacity": current_capacity,
            "utilization": expected_load / current_capacity if current_capacity > 0 else 0,
            "action": "none",
            "suggested_size": current_capacity
        }

        # Recommend scaling if utilization is high or low
        if expected_load > current_capacity * 0.8:
            # High utilization - recommend scale up
            suggested_size = int(expected_load * 1.25)  # 25% buffer
            recommendation["action"] = "scale_up"
            recommendation["suggested_size"] = suggested_size
            recommendation["reason"] = f"High utilization ({recommendation['utilization']:.1%})"

        elif expected_load < current_capacity * 0.3 and current_capacity > 10:
            # Low utilization - recommend scale down
            suggested_size = max(int(expected_load * 1.5), 10)  # 50% buffer, min 10
            recommendation["action"] = "scale_down"
            recommendation["suggested_size"] = suggested_size
            recommendation["reason"] = f"Low utilization ({recommendation['utilization']:.1%})"

        recommendations[pool_name] = recommendation

    return recommendations
