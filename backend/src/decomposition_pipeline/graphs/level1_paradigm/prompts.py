"""
LLM prompts for Level 1 Paradigm Selection.

Contains prompt templates for problem characterization and paradigm scoring.
"""

# Prompt for characterizing the problem
CHARACTERIZATION_PROMPT = """Analyze the following problem and extract its key characteristics.

Problem:
{problem}

Extract the following characteristics:
1. Problem Size: Estimate the scale/size (small/medium/large)
2. Data Characteristics: What data is involved? (volume, structure, etc.)
3. Structure: Does the problem have inherent structure? (graph, hierarchy, sequence, etc.)
4. Dependencies: Are there dependencies between components?
5. Timing Constraints: Any real-time or temporal requirements?
6. Distribution Needs: Does it need to be distributed/parallel?
7. Computational Intensity: Is it compute-heavy?
8. Domain: What domain does this belong to? (API design, data processing, ML, etc.)

Return your analysis as a JSON object with these keys:
- problem_size: "small" | "medium" | "large"
- has_graph_structure: boolean
- has_hierarchy: boolean
- has_sequence: boolean
- has_spatial_aspects: boolean
- parallelizable: boolean
- has_cycles: boolean
- compute_intensive: boolean
- memory_intensive: boolean
- real_time: boolean
- distributed: boolean
- data_volume: "small" | "medium" | "large"
- complexity_estimate: string (brief estimate)
- domain: string
"""

# Paradigm descriptions for scoring
PARADIGM_DESCRIPTIONS = {
    "structural": """
**Structural Decomposition** breaks problems based on components and their relationships.
- Focuses on: Graph structures, modules, components, interfaces
- Techniques: Divide-and-Conquer, Graph Partitioning, Modular Decomposition
- Best for: Problems with clear component boundaries, graph-like structures
- Indicators: "components", "modules", "relationships", "graph", "tree", "network"
""",
    "functional": """
**Functional Decomposition** breaks problems based on operations and tasks.
- Focuses on: Operations, tasks, functions, transformations
- Techniques: Task Parallelism, Pipeline Decomposition, MapReduce, Fork-Join
- Best for: Problems defined by operations/workflows
- Indicators: "operations", "tasks", "workflow", "pipeline", "processing steps"
""",
    "temporal": """
**Temporal Decomposition** breaks problems based on time and event ordering.
- Focuses on: Stages, events, timelines, sequences
- Techniques: Event Sourcing, Pipeline Stages, Batch/Stream Processing
- Best for: Time-sensitive problems, event-driven systems
- Indicators: "real-time", "events", "timeline", "stages", "asynchronous"
""",
    "spatial": """
**Spatial Decomposition** breaks problems based on location or physical distribution.
- Focuses on: Regions, locations, geographic distribution
- Techniques: Range Partitioning, Hash Partitioning, Geographic Decomposition
- Best for: Geographically distributed systems, spatial data
- Indicators: "location", "region", "distributed", "geographic", "spatial"
""",
    "hierarchical": """
**Hierarchical Decomposition** breaks problems based on levels of abstraction.
- Focuses on: Layers, levels, abstractions, pyramids
- Techniques: Multi-tier Architecture, Pyramid Decomposition
- Best for: Problems with clear layering or abstraction levels
- Indicators: "layers", "levels", "hierarchy", "abstraction", "tiers"
""",
    "computational": """
**Computational Decomposition** breaks problems based on computational resources.
- Focuses on: Workload distribution, resource allocation, parallelization
- Techniques: Model Parallelism, Data Parallelism, Mixture of Experts
- Best for: Compute-intensive problems requiring parallel processing
- Indicators: "compute-heavy", "parallel", "GPU", "distributed computing"
""",
    "data": """
**Data Decomposition** breaks problems based on data organization.
- Focuses on: Data partitioning, sharding, feature decomposition
- Techniques: Horizontal/Vertical Partitioning, Feature Decomposition
- Best for: Data-intensive problems, database design
- Indicators: "database", "data partitioning", "sharding", "features", "schema"
""",
    "dependency": """
**Dependency Decomposition** breaks problems based on execution dependencies.
- Focuses on: Dependencies, execution order, critical paths
- Techniques: Topological Sort, Critical Path Method, Async/Await
- Best for: Problems with complex dependencies and ordering constraints
- Indicators: "dependencies", "ordering", "prerequisites", "DAG", "workflow"
""",
}

# Paradigm scoring prompt template
PARADIGM_SCORING_PROMPT = """You are analyzing a problem to determine how well it fits the {paradigm} decomposition paradigm.

**Problem:**
{problem}

**Problem Characteristics:**
{characteristics}

**Paradigm: {paradigm_name}**
{paradigm_description}

**Scoring Criteria:**
Evaluate on a scale of 0.0 to 1.0 how well this paradigm applies:
- 0.9-1.0: Excellent fit, paradigm strongly applies
- 0.7-0.8: Good fit, paradigm clearly applies
- 0.5-0.6: Moderate fit, paradigm somewhat applies
- 0.3-0.4: Weak fit, paradigm marginally applies
- 0.0-0.2: Poor fit, paradigm does not apply

Consider:
1. Does the problem description mention paradigm-specific indicators?
2. Do the problem characteristics align with this paradigm?
3. Would this paradigm provide valuable insights for decomposition?

Return a JSON object with:
- score: float (0.0-1.0)
- reasoning: string (2-3 sentences explaining the score)
- key_indicators: list of strings (specific phrases/characteristics that influenced the score)
"""

def get_characterization_prompt(problem: str) -> str:
    """Generate the problem characterization prompt."""
    return CHARACTERIZATION_PROMPT.format(problem=problem)


def get_paradigm_scoring_prompt(
    problem: str,
    characteristics: dict,
    paradigm: str
) -> str:
    """Generate the paradigm scoring prompt for a specific paradigm."""
    paradigm_description = PARADIGM_DESCRIPTIONS.get(
        paradigm,
        "No description available for this paradigm."
    )
    paradigm_name = paradigm.replace("_", " ").title()

    return PARADIGM_SCORING_PROMPT.format(
        paradigm=paradigm,
        paradigm_name=paradigm_name,
        paradigm_description=paradigm_description,
        problem=problem,
        characteristics=str(characteristics),
    )
