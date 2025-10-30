# Agent Task: Define Core State Schemas

## Task Description
Define core state schemas for the LangGraph decomposition pipeline, including MainPipelineState, Level1State, Level2State, Level3 states (per paradigm), Level4State, and Level5State.

## Context
The state schemas define the data structures that flow through the multi-level LangGraph pipeline. Each level has specific state requirements based on the decomposition process outlined in brainstorm_1.md.

## Key Requirements

### MainPipelineState (Global State)
The main state that flows through the entire pipeline, containing:
- Original problem and characteristics
- Selected paradigms and scores
- Selected techniques and justifications
- Decomposed subproblems from all paradigms
- Integrated subproblems and dependencies
- Agent assignments and partial solutions
- Final integrated solution and validation
- Control flow metadata (approvals, backtracking, current stage)

### Level 1: Paradigm Selection State
- Problem embedding and characteristics
- Candidate paradigms with scores
- Selected paradigms (1-3 typically)
- Reasoning for selection/rejection

### Level 2: Technique Selection State
- Candidate techniques per paradigm
- Technique scores and applicability
- Selected techniques mapping
- Formal justifications from literature

### Level 3.1: Decomposition States (Per Paradigm)
Each of the 8 paradigms needs its own state:
- StructuralState: Graph representation, components, relationships
- FunctionalState: Operations, task groups, dependencies
- TemporalState: Timeline, stages, event sequences
- SpatialState: Coordinates, regions, boundaries
- HierarchicalState: Levels, abstractions, layers
- ComputationalState: Resources, workload, distribution
- DataState: Schema, partition keys, splitting
- DependencyState: Dependency graph, critical path, ordering

### Level 3.2: Integration State
- All subproblems from all paradigms
- Overlap detection and clusters
- Conflict resolution results
- Final integrated subproblem list
- Dependency graph

### Level 4: Solution Generation State
- Routing decisions per subproblem
- Agent pool assignments
- Partial solutions from agents
- Progress tracking
- Completion status

### Level 5: Solution Integration State
- Solution coverage map
- Detected conflicts
- Gap identification
- Integrated solution
- Validation results

## Implementation Plan

1. Create `backend/src/decomposition_pipeline/schemas/state.py` with all state definitions
2. Use Pydantic BaseModel or TypedDict for state schemas
3. Include proper type hints and documentation
4. Define nested models for complex structures (Technique, Subproblem, Solution, etc.)
5. Ensure compatibility with LangGraph's state management

## Supporting Models
Also need to define:
- Technique: Name, paradigm, definition, prerequisites, complexity, references
- Subproblem: ID, title, description, paradigm, dependencies, status
- Solution: Content, confidence, reasoning, validation
- ApprovalRecord: Gate, timestamp, action, user, reason
- ValidationReport: Status, issues, recommendations

## Testing
Write comprehensive tests for:
- State schema validation
- State merging/updating
- Type checking
- Serialization/deserialization

## Success Criteria
- All state schemas defined according to brainstorm_1.md
- Proper type hints and documentation
- Tests pass with 100% coverage
- Schemas work with LangGraph's StateGraph

## References
- brainstorm_1.md: STATE SCHEMA DESIGN section (lines 110-167)
- LangGraph documentation on state management
