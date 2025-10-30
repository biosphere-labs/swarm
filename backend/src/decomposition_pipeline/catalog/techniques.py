"""
Pre-populated catalog of algorithmic decomposition techniques.

All techniques are from established computer science literature including
textbooks (CLRS, etc.) and seminal research papers. No machine learning
or pattern discovery is used - this is a curated collection of known methods.
"""

from decomposition_pipeline.catalog.models import (
    ApplicabilityRule,
    Technique,
    TechniqueCatalog,
)


def get_structural_techniques() -> list[Technique]:
    """Structural decomposition techniques from literature."""
    return [
        Technique(
            name="Divide and Conquer",
            paradigm="structural",
            formal_definition="T(n) = aT(n/b) + f(n) where problem splits into a subproblems of size n/b",
            prerequisites=[
                "problem_is_divisible",
                "subproblems_independent",
                "subproblems_same_type",
            ],
            complexity="O(n log n) typical for balanced division",
            applicability_rules=[
                ApplicabilityRule(
                    condition="problem_size > 1000",
                    score=0.8,
                    description="Large problems benefit from recursive division",
                ),
                ApplicabilityRule(
                    condition="has_recursive_structure == True",
                    score=0.9,
                    description="Recursive structure is ideal for divide-and-conquer",
                ),
                ApplicabilityRule(
                    condition="subproblems_independent == True",
                    score=0.85,
                    description="Independent subproblems can be solved in parallel",
                ),
            ],
            literature_references=[
                "CLRS Chapter 4: Divide-and-Conquer",
                "Bentley, Programming Pearls (1986)",
            ],
            implementation_strategy="Recursively split problem into smaller subproblems, solve each independently, then merge results using combination function",
        ),
        Technique(
            name="Graph Partitioning",
            paradigm="structural",
            formal_definition="Partition graph G(V,E) into k subgraphs minimizing edge cut: min Σ cut(Vi,Vj)",
            prerequisites=[
                "problem_is_graph",
                "nodes_identifiable",
                "relationships_explicit",
            ],
            complexity="O(|E| log |V|) with METIS/KaHIP heuristics, NP-hard optimal",
            applicability_rules=[
                ApplicabilityRule(
                    condition="has_network_structure == True",
                    score=0.9,
                    description="Network/graph structure is explicitly modeled",
                ),
                ApplicabilityRule(
                    condition="relationships_explicit == True",
                    score=0.8,
                    description="Explicit relationships between components",
                ),
                ApplicabilityRule(
                    condition="minimize_dependencies == True",
                    score=0.85,
                    description="Want to minimize cross-partition dependencies",
                ),
            ],
            literature_references=[
                "Kernighan-Lin Algorithm (1970)",
                "METIS: Karypis & Kumar (1998)",
                "Spectral Graph Theory: Chung (1997)",
            ],
            implementation_strategy="Build graph representation, apply partitioning algorithm (spectral/multilevel/flow-based), create subproblems per partition",
        ),
        Technique(
            name="Tree Decomposition",
            paradigm="structural",
            formal_definition="Decompose graph into tree structure preserving local neighborhoods, treewidth tw(G) = min width over all tree decompositions",
            prerequisites=[
                "has_hierarchical_structure",
                "tree_like_relationships",
            ],
            complexity="O(n) for trees, exponential in treewidth for general graphs",
            applicability_rules=[
                ApplicabilityRule(
                    condition="has_hierarchical_structure == True",
                    score=0.9,
                    description="Clear parent-child or containment relationships",
                ),
                ApplicabilityRule(
                    condition="tree_like_relationships == True",
                    score=0.95,
                    description="Problem naturally forms tree structure",
                ),
            ],
            literature_references=[
                "Tree Decomposition: Robertson & Seymour (1984)",
                "Dynamic Programming on Trees: CLRS Chapter 15",
            ],
            implementation_strategy="Identify tree structure, decompose into subtrees, process bottom-up or top-down depending on dependencies",
        ),
        Technique(
            name="Modular Decomposition",
            paradigm="structural",
            formal_definition="Partition system S into modules M1...Mk where each module has well-defined interface and minimal coupling",
            prerequisites=[
                "has_module_boundaries",
                "interfaces_identifiable",
            ],
            complexity="O(n + m) for identification, depends on system size",
            applicability_rules=[
                ApplicabilityRule(
                    condition="has_clear_boundaries == True",
                    score=0.85,
                    description="Clear separation of concerns or modules",
                ),
                ApplicabilityRule(
                    condition="low_coupling == True",
                    score=0.9,
                    description="Modules have minimal interdependencies",
                ),
                ApplicabilityRule(
                    condition="high_cohesion == True",
                    score=0.85,
                    description="Each module has focused responsibility",
                ),
            ],
            literature_references=[
                "Parnas, On Criteria for Decomposing Systems into Modules (1972)",
                "Software Architecture Patterns: Richards & Ford (2020)",
            ],
            implementation_strategy="Identify module boundaries based on coupling/cohesion, extract interfaces, create subproblems per module",
        ),
    ]


def get_functional_techniques() -> list[Technique]:
    """Functional decomposition techniques from literature."""
    return [
        Technique(
            name="MapReduce",
            paradigm="functional",
            formal_definition="map: (k1,v1) → list(k2,v2), reduce: (k2,list(v2)) → list(v3)",
            prerequisites=[
                "operations_parallelizable",
                "associative_reduction",
                "large_dataset",
            ],
            complexity="O(n/p) with p processors, O(n) sequential",
            applicability_rules=[
                ApplicabilityRule(
                    condition="large_dataset == True",
                    score=0.9,
                    description="Large datasets benefit from parallel processing",
                ),
                ApplicabilityRule(
                    condition="embarrassingly_parallel == True",
                    score=0.95,
                    description="Operations are independent and can run in parallel",
                ),
                ApplicabilityRule(
                    condition="needs_aggregation == True",
                    score=0.85,
                    description="Results need to be aggregated/reduced",
                ),
            ],
            literature_references=[
                "Dean & Ghemawat, MapReduce: Simplified Data Processing on Large Clusters (2004)",
                "Hadoop MapReduce Documentation",
            ],
            implementation_strategy="Define map function for parallel processing, define reduce function for aggregation, distribute execution across workers",
        ),
        Technique(
            name="Fork-Join Pattern",
            paradigm="functional",
            formal_definition="Fork: spawn parallel tasks T1...Tn, Join: wait for all Ti to complete, then combine results",
            prerequisites=[
                "tasks_independent",
                "fixed_task_count",
            ],
            complexity="O(max(Ti)) with unlimited parallelism, O(Σ Ti) sequential",
            applicability_rules=[
                ApplicabilityRule(
                    condition="tasks_independent == True",
                    score=0.9,
                    description="Tasks can execute independently",
                ),
                ApplicabilityRule(
                    condition="need_all_results == True",
                    score=0.85,
                    description="All task results required for continuation",
                ),
            ],
            literature_references=[
                "Java Fork/Join Framework: Lea (2000)",
                "Work Stealing: Blumofe & Leiserson (1999)",
            ],
            implementation_strategy="Identify independent tasks, fork to parallel workers, collect and join results when all complete",
        ),
        Technique(
            name="Pipeline Decomposition",
            paradigm="functional",
            formal_definition="Stages S1→S2→...→Sn where output of Si feeds input of Si+1",
            prerequisites=[
                "sequential_stages_identifiable",
                "data_transformable",
            ],
            complexity="O(n) throughput after pipeline warmup, latency = Σ stage_times",
            applicability_rules=[
                ApplicabilityRule(
                    condition="has_clear_sequence == True",
                    score=0.9,
                    description="Clear sequential processing stages",
                ),
                ApplicabilityRule(
                    condition="each_stage_independent == True",
                    score=0.85,
                    description="Stages operate independently on data",
                ),
                ApplicabilityRule(
                    condition="high_throughput_needed == True",
                    score=0.8,
                    description="Need to maximize throughput",
                ),
            ],
            literature_references=[
                "Hennessy & Patterson, Computer Architecture (2017)",
                "Unix Pipes: McIlroy (1964)",
            ],
            implementation_strategy="Identify processing stages, define interfaces between stages, connect with queues or streams",
        ),
        Technique(
            name="Task Parallelism",
            paradigm="functional",
            formal_definition="Partition work into distinct tasks {T1, T2, ..., Tn} that can execute concurrently",
            prerequisites=[
                "multiple_distinct_operations",
                "minimal_dependencies",
            ],
            complexity="O(max(Ti)) with full parallelism",
            applicability_rules=[
                ApplicabilityRule(
                    condition="operations_diverse == True",
                    score=0.85,
                    description="Different types of operations to perform",
                ),
                ApplicabilityRule(
                    condition="minimal_dependencies == True",
                    score=0.9,
                    description="Few dependencies between tasks",
                ),
            ],
            literature_references=[
                "Task Parallel Library: Microsoft (2010)",
                "OpenMP Task Parallelism",
            ],
            implementation_strategy="Identify distinct operations, check dependencies, schedule independent tasks in parallel",
        ),
    ]


def get_temporal_techniques() -> list[Technique]:
    """Temporal decomposition techniques from literature."""
    return [
        Technique(
            name="Event Sourcing",
            paradigm="temporal",
            formal_definition="State(t) = fold(events[0:t], initial_state) - state is derived from event history",
            prerequisites=[
                "state_changes_trackable",
                "events_ordered",
                "immutable_events",
            ],
            complexity="O(n) space for n events, O(log n) query with indexing",
            applicability_rules=[
                ApplicabilityRule(
                    condition="audit_trail_needed == True",
                    score=0.95,
                    description="Need complete history of changes",
                ),
                ApplicabilityRule(
                    condition="temporal_queries_required == True",
                    score=0.9,
                    description="Need to query state at arbitrary points in time",
                ),
                ApplicabilityRule(
                    condition="undo_redo_needed == True",
                    score=0.85,
                    description="Need to replay or reverse operations",
                ),
            ],
            literature_references=[
                "Fowler, Event Sourcing (2005)",
                "Event Store Pattern: Vernon (2013)",
            ],
            implementation_strategy="Define event types, implement event store with append-only log, build projections by replaying events",
        ),
        Technique(
            name="Pipeline Stages",
            paradigm="temporal",
            formal_definition="Sequential stages {S1, S2, ..., Sn} where data flows through in order",
            prerequisites=[
                "sequential_stages_identifiable",
                "ordered_processing",
            ],
            complexity="O(n) latency, O(1) per stage with pipelining",
            applicability_rules=[
                ApplicabilityRule(
                    condition="has_clear_sequence == True",
                    score=0.9,
                    description="Clear temporal ordering of stages",
                ),
                ApplicabilityRule(
                    condition="stage_isolation_needed == True",
                    score=0.85,
                    description="Stages should be isolated for reliability",
                ),
            ],
            literature_references=[
                "SEDA: Welsh et al. (2001)",
                "Staged Event-Driven Architecture",
            ],
            implementation_strategy="Identify temporal stages, define stage boundaries, implement with queues between stages",
        ),
        Technique(
            name="Batch Processing",
            paradigm="temporal",
            formal_definition="Accumulate items into batches B of size k, process batch as unit",
            prerequisites=[
                "can_delay_processing",
                "benefits_from_batching",
            ],
            complexity="O(n/k) batch operations for n items",
            applicability_rules=[
                ApplicabilityRule(
                    condition="can_delay_processing == True",
                    score=0.8,
                    description="Acceptable to wait for batch to fill",
                ),
                ApplicabilityRule(
                    condition="batch_efficiency_high == True",
                    score=0.85,
                    description="Processing batches is more efficient",
                ),
            ],
            literature_references=[
                "Batch Processing: Kimball & Ross (2013)",
                "MapReduce Batching",
            ],
            implementation_strategy="Accumulate items into batches, trigger processing when batch full or timeout occurs",
        ),
        Technique(
            name="Stream Processing",
            paradigm="temporal",
            formal_definition="Process events as they arrive in continuous stream, applying operators op1 ∘ op2 ∘ ... ∘ opn",
            prerequisites=[
                "continuous_data_flow",
                "real_time_processing",
            ],
            complexity="O(1) per event with bounded windows",
            applicability_rules=[
                ApplicabilityRule(
                    condition="real_time_processing == True",
                    score=0.95,
                    description="Need immediate processing of events",
                ),
                ApplicabilityRule(
                    condition="continuous_data_flow == True",
                    score=0.9,
                    description="Data arrives continuously",
                ),
                ApplicabilityRule(
                    condition="low_latency_required == True",
                    score=0.85,
                    description="Low latency is critical",
                ),
            ],
            literature_references=[
                "Streaming Systems: Akidau et al. (2018)",
                "Apache Flink, Kafka Streams",
            ],
            implementation_strategy="Define stream operators, set up windowing if needed, process events as they arrive",
        ),
    ]


def get_spatial_techniques() -> list[Technique]:
    """Spatial decomposition techniques from literature."""
    return [
        Technique(
            name="Range Partitioning",
            paradigm="spatial",
            formal_definition="Partition space S into ranges [r1,r2), [r2,r3), ..., [rn-1,rn] based on key values",
            prerequisites=[
                "ordered_key_space",
                "range_identifiable",
            ],
            complexity="O(log n) lookup with B-tree index",
            applicability_rules=[
                ApplicabilityRule(
                    condition="ordered_key_space == True",
                    score=0.9,
                    description="Keys have natural ordering",
                ),
                ApplicabilityRule(
                    condition="range_queries_common == True",
                    score=0.85,
                    description="Queries often span ranges",
                ),
            ],
            literature_references=[
                "Database Systems: Ramakrishnan & Gehrke (2003)",
                "Range Partitioning in Distributed Databases",
            ],
            implementation_strategy="Choose partition keys based on access patterns, assign ranges to partitions, route queries to appropriate partition",
        ),
        Technique(
            name="Hash Partitioning",
            paradigm="spatial",
            formal_definition="Partition using hash function h: key → partition_id, ensuring uniform distribution",
            prerequisites=[
                "uniform_distribution_desired",
                "hash_function_available",
            ],
            complexity="O(1) lookup with good hash function",
            applicability_rules=[
                ApplicabilityRule(
                    condition="uniform_distribution_desired == True",
                    score=0.9,
                    description="Want even distribution across partitions",
                ),
                ApplicabilityRule(
                    condition="point_queries_common == True",
                    score=0.85,
                    description="Mostly lookup by key",
                ),
            ],
            literature_references=[
                "Consistent Hashing: Karger et al. (1997)",
                "Distributed Hash Tables",
            ],
            implementation_strategy="Choose hash function, determine partition count, route requests using hash(key) mod n",
        ),
        Technique(
            name="Geographic Decomposition",
            paradigm="spatial",
            formal_definition="Partition based on geographic regions R1, R2, ..., Rn with spatial properties",
            prerequisites=[
                "has_geographic_component",
                "location_based_access",
            ],
            complexity="O(1) with location index, O(n) without",
            applicability_rules=[
                ApplicabilityRule(
                    condition="has_geographic_component == True",
                    score=0.95,
                    description="Data has geographic attributes",
                ),
                ApplicabilityRule(
                    condition="locality_of_access == True",
                    score=0.9,
                    description="Access patterns are geographically local",
                ),
            ],
            literature_references=[
                "GIS Spatial Indexing: R-trees (Guttman 1984)",
                "Geospatial Databases",
            ],
            implementation_strategy="Define geographic regions, assign data to regions based on coordinates, use spatial indexes for queries",
        ),
        Technique(
            name="Grid Decomposition",
            paradigm="spatial",
            formal_definition="Partition space into regular grid cells Cij of equal size",
            prerequisites=[
                "regular_spatial_structure",
                "uniform_cell_size_acceptable",
            ],
            complexity="O(1) cell lookup, O(n) for spatial queries",
            applicability_rules=[
                ApplicabilityRule(
                    condition="regular_spatial_structure == True",
                    score=0.85,
                    description="Space can be divided into regular grid",
                ),
                ApplicabilityRule(
                    condition="spatial_locality == True",
                    score=0.8,
                    description="Nearby cells accessed together",
                ),
            ],
            literature_references=[
                "Spatial Data Structures: Samet (1990)",
                "Quadtree/Octree Decomposition",
            ],
            implementation_strategy="Define grid resolution, assign data to cells, process cells independently or with neighbors",
        ),
    ]


def get_hierarchical_techniques() -> list[Technique]:
    """Hierarchical decomposition techniques from literature."""
    return [
        Technique(
            name="Multi-tier Architecture",
            paradigm="hierarchical",
            formal_definition="Layers L1, L2, ..., Ln where Li can only depend on Li-1, forming strict hierarchy",
            prerequisites=[
                "layer_separation_possible",
                "abstraction_levels_clear",
            ],
            complexity="Depends on layer implementation",
            applicability_rules=[
                ApplicabilityRule(
                    condition="abstraction_levels_clear == True",
                    score=0.9,
                    description="Clear separation of abstraction levels",
                ),
                ApplicabilityRule(
                    condition="layer_independence == True",
                    score=0.85,
                    description="Layers can be developed independently",
                ),
            ],
            literature_references=[
                "Layered Architecture: Buschmann et al. (1996)",
                "Clean Architecture: Martin (2017)",
            ],
            implementation_strategy="Define layer boundaries, establish dependency rules, implement each layer with defined interfaces",
        ),
        Technique(
            name="Pyramid Decomposition",
            paradigm="hierarchical",
            formal_definition="Multi-level hierarchy where each level aggregates information from level below",
            prerequisites=[
                "supports_aggregation",
                "hierarchical_structure",
            ],
            complexity="O(log n) levels for n items with balanced tree",
            applicability_rules=[
                ApplicabilityRule(
                    condition="supports_aggregation == True",
                    score=0.9,
                    description="Can aggregate lower-level information",
                ),
                ApplicabilityRule(
                    condition="multi_resolution_needed == True",
                    score=0.85,
                    description="Need different levels of detail",
                ),
            ],
            literature_references=[
                "Image Pyramids: Burt & Adelson (1983)",
                "Hierarchical Data Structures",
            ],
            implementation_strategy="Build hierarchy bottom-up with aggregation, or top-down with refinement",
        ),
        Technique(
            name="Recursive Hierarchies",
            paradigm="hierarchical",
            formal_definition="Self-similar structure where each node contains similar structure recursively",
            prerequisites=[
                "self_similar_structure",
                "recursive_definition",
            ],
            complexity="O(n) traversal, depends on tree structure",
            applicability_rules=[
                ApplicabilityRule(
                    condition="self_similar_structure == True",
                    score=0.95,
                    description="Same pattern repeats at different scales",
                ),
                ApplicabilityRule(
                    condition="recursive_definition == True",
                    score=0.9,
                    description="Can be defined recursively",
                ),
            ],
            literature_references=[
                "Fractal Structures: Mandelbrot (1982)",
                "Recursive Data Structures: CLRS",
            ],
            implementation_strategy="Define base case and recursive case, process recursively with appropriate termination",
        ),
    ]


def get_computational_techniques() -> list[Technique]:
    """Computational decomposition techniques from literature."""
    return [
        Technique(
            name="Data Parallelism",
            paradigm="computational",
            formal_definition="Same operation applied to different data elements in parallel: ∀i: f(data[i])",
            prerequisites=[
                "uniform_operations",
                "independent_data_elements",
            ],
            complexity="O(n/p) with p processors",
            applicability_rules=[
                ApplicabilityRule(
                    condition="uniform_operations == True",
                    score=0.9,
                    description="Same operation on all data",
                ),
                ApplicabilityRule(
                    condition="large_dataset == True",
                    score=0.85,
                    description="Dataset large enough to benefit from parallelism",
                ),
            ],
            literature_references=[
                "SIMD Parallelism: Flynn (1972)",
                "GPU Computing Patterns",
            ],
            implementation_strategy="Partition data across workers, apply same operation to each partition, gather results",
        ),
        Technique(
            name="Model Parallelism",
            paradigm="computational",
            formal_definition="Partition model M into components M1, M2, ..., Mn distributed across resources",
            prerequisites=[
                "model_is_partitionable",
                "large_model_size",
            ],
            complexity="Depends on model architecture and communication overhead",
            applicability_rules=[
                ApplicabilityRule(
                    condition="model_too_large_for_single_device == True",
                    score=0.95,
                    description="Model doesn't fit on single device",
                ),
                ApplicabilityRule(
                    condition="model_is_partitionable == True",
                    score=0.9,
                    description="Model can be split into components",
                ),
            ],
            literature_references=[
                "Model Parallelism in Deep Learning",
                "Megatron-LM: Shoeybi et al. (2019)",
            ],
            implementation_strategy="Partition model across devices, implement communication for activations/gradients",
        ),
        Technique(
            name="Mixture of Experts",
            paradigm="computational",
            formal_definition="Route inputs to specialized experts: y = Σ gate(x)i * experti(x)",
            prerequisites=[
                "multiple_domains",
                "routing_possible",
            ],
            complexity="O(k) where k is number of active experts",
            applicability_rules=[
                ApplicabilityRule(
                    condition="multiple_domains == True",
                    score=0.9,
                    description="Problem spans multiple domains",
                ),
                ApplicabilityRule(
                    condition="specialization_beneficial == True",
                    score=0.85,
                    description="Specialized models outperform general",
                ),
            ],
            literature_references=[
                "Mixture of Experts: Jacobs et al. (1991)",
                "Switch Transformers: Fedus et al. (2021)",
            ],
            implementation_strategy="Train specialized experts for different domains, implement gating network for routing",
        ),
    ]


def get_data_techniques() -> list[Technique]:
    """Data decomposition techniques from literature."""
    return [
        Technique(
            name="Horizontal Partitioning",
            paradigm="data",
            formal_definition="Partition rows R = R1 ∪ R2 ∪ ... ∪ Rn where Ri ∩ Rj = ∅",
            prerequisites=[
                "tabular_data",
                "partition_key_exists",
            ],
            complexity="O(1) lookup with partition index",
            applicability_rules=[
                ApplicabilityRule(
                    condition="large_dataset == True",
                    score=0.9,
                    description="Dataset large enough to benefit from partitioning",
                ),
                ApplicabilityRule(
                    condition="locality_of_access == True",
                    score=0.85,
                    description="Access patterns show locality",
                ),
            ],
            literature_references=[
                "Database Sharding: Stonebraker (1986)",
                "Dynamo: DeCandia et al. (2007)",
            ],
            implementation_strategy="Choose partition key, define sharding function, route queries to appropriate shard",
        ),
        Technique(
            name="Vertical Partitioning",
            paradigm="data",
            formal_definition="Partition columns C = C1 ∪ C2 ∪ ... ∪ Cn, preserving primary key in each partition",
            prerequisites=[
                "column_access_patterns_distinct",
                "some_columns_rarely_accessed",
            ],
            complexity="O(1) with proper indexing",
            applicability_rules=[
                ApplicabilityRule(
                    condition="column_access_patterns_distinct == True",
                    score=0.85,
                    description="Different columns accessed in different patterns",
                ),
                ApplicabilityRule(
                    condition="wide_tables == True",
                    score=0.8,
                    description="Tables have many columns",
                ),
            ],
            literature_references=[
                "Column Stores: Stonebraker et al. (2005)",
                "Vertical Partitioning: Navathe et al. (1984)",
            ],
            implementation_strategy="Group columns by access patterns, create separate stores, include join keys",
        ),
        Technique(
            name="Feature Decomposition",
            paradigm="data",
            formal_definition="X[n×d] → X1[n×d1] ⊕ X2[n×d2] where d1+d2≤d, preserving information",
            prerequisites=[
                "high_dimensional_data",
                "features_separable",
            ],
            complexity="Depends on decomposition method (PCA is O(d²n))",
            applicability_rules=[
                ApplicabilityRule(
                    condition="high_dimensional_data == True",
                    score=0.85,
                    description="Many features/dimensions",
                ),
                ApplicabilityRule(
                    condition="feature_correlation_low == True",
                    score=0.8,
                    description="Features are relatively independent",
                ),
            ],
            literature_references=[
                "PCA: Pearson (1901), Hotelling (1933)",
                "Feature Selection: Guyon & Elisseeff (2003)",
            ],
            implementation_strategy="Analyze feature importance, group related features, create submodels or projections",
        ),
    ]


def get_dependency_techniques() -> list[Technique]:
    """Dependency decomposition techniques from literature."""
    return [
        Technique(
            name="Topological Sort",
            paradigm="dependency",
            formal_definition="Order vertices in DAG such that for edge (u,v), u comes before v in ordering",
            prerequisites=[
                "dependency_graph_is_dag",
                "dependencies_explicit",
            ],
            complexity="O(V + E) using DFS or Kahn's algorithm",
            applicability_rules=[
                ApplicabilityRule(
                    condition="dependency_graph_is_dag == True",
                    score=0.95,
                    description="No circular dependencies",
                ),
                ApplicabilityRule(
                    condition="dependencies_explicit == True",
                    score=0.9,
                    description="Dependencies are known and explicit",
                ),
            ],
            literature_references=[
                "Topological Sorting: Kahn (1962)",
                "CLRS Chapter 22: Elementary Graph Algorithms",
            ],
            implementation_strategy="Build dependency graph, run topological sort, execute tasks in sorted order",
        ),
        Technique(
            name="Critical Path Method",
            paradigm="dependency",
            formal_definition="Find longest path in DAG: CP = max path from start to end",
            prerequisites=[
                "task_durations_known",
                "dependency_graph_is_dag",
            ],
            complexity="O(V + E) to find critical path",
            applicability_rules=[
                ApplicabilityRule(
                    condition="task_durations_known == True",
                    score=0.9,
                    description="Task execution times are known or estimable",
                ),
                ApplicabilityRule(
                    condition="optimize_makespan == True",
                    score=0.95,
                    description="Want to minimize total completion time",
                ),
            ],
            literature_references=[
                "CPM: Kelley & Walker (1959)",
                "PERT: Malcolm et al. (1959)",
            ],
            implementation_strategy="Calculate earliest/latest start times, identify critical path, prioritize critical tasks",
        ),
        Technique(
            name="Async/Await Decomposition",
            paradigm="dependency",
            formal_definition="Decompose into async operations with explicit await points for dependencies",
            prerequisites=[
                "asynchronous_operations",
                "explicit_wait_points",
            ],
            complexity="Depends on underlying operations",
            applicability_rules=[
                ApplicabilityRule(
                    condition="io_bound_operations == True",
                    score=0.9,
                    description="Operations are I/O bound, not CPU bound",
                ),
                ApplicabilityRule(
                    condition="interleaving_possible == True",
                    score=0.85,
                    description="Can interleave execution of operations",
                ),
            ],
            literature_references=[
                "Async/Await Pattern: Hejlsberg et al. (2012)",
                "Promise Theory: Burgess (2015)",
            ],
            implementation_strategy="Identify async operations, mark await points for dependencies, use event loop for execution",
        ),
    ]


def get_default_catalog() -> TechniqueCatalog:
    """
    Get the default pre-populated technique catalog.

    Returns:
        TechniqueCatalog with all 8 paradigms populated with techniques
        from computer science literature.
    """
    catalog = TechniqueCatalog()

    # Add all techniques organized by paradigm
    for technique in get_structural_techniques():
        catalog.add_technique(technique)

    for technique in get_functional_techniques():
        catalog.add_technique(technique)

    for technique in get_temporal_techniques():
        catalog.add_technique(technique)

    for technique in get_spatial_techniques():
        catalog.add_technique(technique)

    for technique in get_hierarchical_techniques():
        catalog.add_technique(technique)

    for technique in get_computational_techniques():
        catalog.add_technique(technique)

    for technique in get_data_techniques():
        catalog.add_technique(technique)

    for technique in get_dependency_techniques():
        catalog.add_technique(technique)

    return catalog
