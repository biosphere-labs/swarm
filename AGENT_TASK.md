# Agent Task: Build Level 2 Technique Selection Subgraph

## Task ID
Task #5 from todo list

## Objective
Implement the Level 2 Technique Selection Subgraph that retrieves applicable techniques from the catalog, scores them against problem characteristics, and selects the best technique for each selected paradigm.

## Requirements

### Architecture (from brainstorm_1.md)

The Level 2 subgraph consists of three main nodes:

1. **TechniqueRetrievalNode**
   - Queries technique catalog with problem + paradigm
   - Retrieves applicable techniques for each selected paradigm
   - Filters by problem characteristics
   - Output: `candidate_techniques` per paradigm

2. **TechniqueScoringNode**
   - For each candidate technique, compute applicability score
   - Uses rule-based scoring from algorithmic theory (no ML)
   - Criteria from literature: problem size thresholds, structure requirements, complexity guarantees
   - Output: `technique_scores` dict

3. **TechniqueSelectionNode**
   - Selects optimal technique per paradigm based on formal criteria
   - Validates technique prerequisites are met
   - Generates formal justification citing algorithmic literature
   - Output: `selected_techniques` dict (paradigm → technique)

### State Management

**Input State (Level2State):**
- `original_problem`: str
- `problem_characteristics`: Dict[str, Any]
- `selected_paradigms`: List[str]

**Output State:**
- `candidate_techniques`: Dict[str, List[Technique]]
- `technique_scores`: Dict[str, float]
- `technique_justification`: Dict[str, str]
- `selected_techniques`: Dict[str, Technique]

### Key Design Principles

1. **No Machine Learning**: All technique selection uses pre-defined rules from algorithmic literature
2. **Formal Justification**: Each selection must include formal reasoning citing literature
3. **Rule-Based Scoring**: Uses applicability rules defined in the technique catalog
4. **Prerequisite Validation**: Must check that problem meets technique prerequisites

## Implementation Plan

### File Structure
```
backend/src/decomposition_pipeline/graphs/level2_technique/
├── __init__.py
├── graph.py           # Main subgraph definition
├── nodes.py          # Node implementations
└── utils.py          # Helper functions for scoring/justification
```

### Node Implementations

#### 1. TechniqueRetrievalNode
```python
def retrieve_techniques(state: Level2State) -> Level2State:
    """
    Retrieve applicable techniques from catalog for each selected paradigm.

    For each paradigm:
    - Query catalog with problem characteristics
    - Get techniques that meet prerequisites
    - Filter by applicability
    """
```

#### 2. TechniqueScoringNode
```python
def score_techniques(state: Level2State) -> Level2State:
    """
    Score each candidate technique against problem characteristics.

    Uses rule-based scoring from technique catalog:
    - Evaluate applicability rules
    - Compute weighted scores
    - Rank by score
    """
```

#### 3. TechniqueSelectionNode
```python
def select_techniques(state: Level2State) -> Level2State:
    """
    Select best technique per paradigm.

    - Choose highest scoring technique
    - Validate prerequisites
    - Generate formal justification
    - Cite literature references
    """
```

### Graph Construction

```python
from langgraph.graph import StateGraph

def create_level2_graph() -> StateGraph:
    """Create the Level 2 Technique Selection subgraph."""
    graph = StateGraph(Level2State)

    # Add nodes
    graph.add_node("retrieve_techniques", retrieve_techniques)
    graph.add_node("score_techniques", score_techniques)
    graph.add_node("select_techniques", select_techniques)

    # Add edges (linear flow)
    graph.set_entry_point("retrieve_techniques")
    graph.add_edge("retrieve_techniques", "score_techniques")
    graph.add_edge("score_techniques", "select_techniques")
    graph.set_finish_point("select_techniques")

    return graph
```

## Testing Requirements

### Unit Tests

1. **Test Technique Retrieval**
   - Test retrieval for single paradigm
   - Test retrieval for multiple paradigms
   - Test filtering by prerequisites
   - Test empty results (no applicable techniques)

2. **Test Technique Scoring**
   - Test scoring with various problem characteristics
   - Test rule evaluation
   - Test weighted score calculation
   - Test ranking by score

3. **Test Technique Selection**
   - Test selection of best technique
   - Test justification generation
   - Test prerequisite validation
   - Test handling of tied scores

### Integration Tests

1. **Test Full Subgraph Execution**
   - Test end-to-end flow from paradigms to selected techniques
   - Test with realistic problem characteristics
   - Verify state transformations
   - Validate output structure

2. **Test Edge Cases**
   - No techniques meet prerequisites
   - All techniques have zero score
   - Multiple paradigms selected
   - Missing problem characteristics

## Success Criteria

- [ ] All three nodes implemented and functional
- [ ] StateGraph properly constructed with linear flow
- [ ] Technique catalog integration working
- [ ] Rule-based scoring operational
- [ ] Formal justifications generated with citations
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Type hints complete
- [ ] Docstrings complete
- [ ] No ML/learning components

## Dependencies

- `decomposition_pipeline.schemas.state.Level2State`
- `decomposition_pipeline.catalog.models.TechniqueCatalog`
- `decomposition_pipeline.catalog.techniques.get_default_catalog()`
- `langgraph.graph.StateGraph`

## Acceptance Criteria

1. Subgraph can retrieve techniques for all 8 paradigms
2. Scoring uses only rule-based methods from catalog
3. Selection produces valid technique with justification
4. All tests pass with >90% coverage
5. Code follows existing patterns in codebase
6. No external API calls or ML models used

## Timeline

Expected completion: Within current work session

## Notes

- This is a pure algorithmic implementation - no learning required
- All techniques are pre-defined in the catalog
- Selection criteria are from CS literature, not discovered
- Justifications should cite specific papers/textbooks
- Must handle case where no technique is applicable gracefully
