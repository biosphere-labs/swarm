"""
Routing logic for Level 4: Route subproblems to appropriate agent pools.

Implements SubproblemAnalysisNode and AgentPoolSelectionNode from brainstorm_1.md lines 454-468.
"""

from typing import Dict, Any, List
from ...schemas.state import Level4State, Subproblem
from ...agents.pool import AgentPoolManager


def analyze_subproblem_requirements(
    subproblem: Subproblem
) -> Dict[str, Any]:
    """
    Analyze a subproblem to determine resource requirements and routing.

    From brainstorm_1.md lines 454-458:
    - Analyzes complexity, domain, resource needs
    - Determines optimal agent pool and model size

    Args:
        subproblem: The subproblem to analyze

    Returns:
        Dictionary with analysis results including:
        - complexity: "low", "medium", or "high"
        - domain: Optional domain specialization
        - paradigm: Source paradigm
        - estimated_duration: Estimated time in seconds
        - requires_large_model: Boolean flag
    """
    # Extract characteristics
    paradigm = subproblem.get("paradigm", "unknown")
    description = subproblem.get("description", "")
    metadata = subproblem.get("metadata", {})

    # Estimate complexity based on description length and metadata
    complexity = estimate_complexity(subproblem)

    # Detect domain specialization from description
    domain = detect_domain(description, metadata)

    # Estimate duration based on complexity
    duration_map = {"low": 30, "medium": 60, "high": 120}
    estimated_duration = duration_map.get(complexity, 60)

    # High complexity problems may benefit from larger models
    requires_large_model = complexity == "high"

    return {
        "complexity": complexity,
        "domain": domain,
        "paradigm": paradigm,
        "estimated_duration": estimated_duration,
        "requires_large_model": requires_large_model,
        "has_dependencies": len(subproblem.get("dependencies", [])) > 0,
    }


def estimate_complexity(subproblem: Subproblem) -> str:
    """
    Estimate complexity level of a subproblem.

    Uses heuristics based on:
    - Description length
    - Number of dependencies
    - Explicit complexity field if present
    - Metadata indicators

    Returns:
        "low", "medium", or "high"
    """
    # Check explicit complexity field
    if "estimated_complexity" in subproblem:
        return subproblem["estimated_complexity"].lower()

    # Heuristic based on description length
    description = subproblem.get("description", "")
    desc_length = len(description)

    # Count dependencies
    num_deps = len(subproblem.get("dependencies", []))

    # Simple scoring system
    score = 0

    # Length contribution
    if desc_length > 500:
        score += 2
    elif desc_length > 200:
        score += 1

    # Dependencies contribution
    if num_deps > 3:
        score += 2
    elif num_deps > 0:
        score += 1

    # Check for complexity indicators in description
    complexity_keywords = {
        "high": ["complex", "difficult", "advanced", "sophisticated", "intricate"],
        "low": ["simple", "basic", "straightforward", "trivial", "easy"],
    }

    desc_lower = description.lower()
    for keyword in complexity_keywords["high"]:
        if keyword in desc_lower:
            score += 1

    for keyword in complexity_keywords["low"]:
        if keyword in desc_lower:
            score -= 1

    # Map score to complexity level
    if score >= 3:
        return "high"
    elif score <= 0:
        return "low"
    else:
        return "medium"


def detect_domain(description: str, metadata: Dict[str, Any]) -> str:
    """
    Detect domain specialization from subproblem description and metadata.

    Checks for domain keywords to route to specialized agent pools.

    Returns:
        Domain name or empty string if no specific domain detected
    """
    # Check metadata first
    if "domain" in metadata:
        return metadata["domain"]

    # Domain keyword mapping
    domain_keywords = {
        "api_design": ["api", "endpoint", "rest", "graphql", "interface"],
        "data_processing": ["data", "processing", "etl", "pipeline", "transform"],
        "ml_modeling": ["machine learning", "ml", "model", "training", "prediction"],
        "security": ["security", "authentication", "authorization", "encryption", "vulnerability"],
        "frontend": ["frontend", "ui", "interface", "component", "react", "vue"],
        "backend": ["backend", "server", "service", "microservice"],
        "database": ["database", "sql", "nosql", "query", "schema", "index"],
        "networking": ["network", "socket", "protocol", "connection", "latency"],
    }

    desc_lower = description.lower()

    # Count keyword matches for each domain
    domain_scores = {}
    for domain, keywords in domain_keywords.items():
        score = sum(1 for keyword in keywords if keyword in desc_lower)
        if score > 0:
            domain_scores[domain] = score

    # Return domain with highest score, if any
    if domain_scores:
        return max(domain_scores.items(), key=lambda x: x[1])[0]

    return ""


def route_subproblems_to_pools(state: Level4State) -> Level4State:
    """
    Node function: Analyze and route all subproblems to agent pools.

    Implements AgentPoolSelectionNode from brainstorm_1.md lines 460-468.

    Args:
        state: Level4State with integrated_subproblems

    Returns:
        Updated state with routing_decisions and agent_assignments
    """
    subproblems = state.get("integrated_subproblems", [])
    if not subproblems:
        return {
            **state,
            "routing_decisions": {},
            "agent_assignments": {},
        }

    # Initialize pool manager
    pool_manager = AgentPoolManager()

    # Analyze each subproblem and determine routing
    routing_decisions = {}
    agent_assignments = {}

    for subproblem in subproblems:
        subproblem_id = subproblem["id"]

        # Analyze requirements
        analysis = analyze_subproblem_requirements(subproblem)

        # Select pool
        pool_name = pool_manager.select_pool_for_subproblem(
            paradigm=analysis["paradigm"],
            domain=analysis["domain"],
            complexity=analysis["complexity"]
        )

        # Store routing decision with justification
        routing_decisions[subproblem_id] = {
            "selected_pool": pool_name,
            "analysis": analysis,
            "reasoning": generate_routing_justification(analysis, pool_name),
        }

        # Store pool assignment
        agent_assignments[subproblem_id] = pool_name

    # Get current pool statuses
    pool_statuses = pool_manager.get_all_pool_statuses()

    return {
        **state,
        "routing_decisions": routing_decisions,
        "agent_assignments": agent_assignments,
        "agent_pool_status": pool_statuses,
    }


def generate_routing_justification(
    analysis: Dict[str, Any],
    selected_pool: str
) -> str:
    """
    Generate human-readable justification for routing decision.

    Args:
        analysis: Analysis results from analyze_subproblem_requirements
        selected_pool: Name of the selected pool

    Returns:
        Justification string
    """
    parts = [f"Selected {selected_pool} because:"]

    # Paradigm match
    if analysis["paradigm"] in selected_pool:
        parts.append(f"- Matches {analysis['paradigm']} paradigm specialization")

    # Domain match
    if analysis["domain"] and analysis["domain"] in selected_pool:
        parts.append(f"- Matches {analysis['domain']} domain expertise")

    # Complexity consideration
    if analysis["complexity"] == "high" and "general" in selected_pool:
        parts.append("- High complexity requires larger model (GPT-4o)")
    else:
        parts.append(f"- {analysis['complexity'].capitalize()} complexity suited for pool's capabilities")

    # Model consideration
    if analysis["requires_large_model"]:
        parts.append("- Complex problem benefits from larger model")

    return "\n".join(parts)
