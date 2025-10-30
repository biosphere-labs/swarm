# Human-in-the-Loop (HITL) Approval Gates

This module implements Human-in-the-Loop approval gates for the LangGraph decomposition pipeline, providing human oversight and control at critical decision points.

## Overview

HITL approval gates use LangGraph's `interrupt()` mechanism to pause pipeline execution and wait for human review. This enables:

- **Human oversight** at critical decision points
- **Quality control** before proceeding to next stages
- **Course correction** through reject, modify, and backtrack actions
- **Context enrichment** with human insights
- **Flexible configuration** of when gates activate

## Architecture

### Core Components

1. **HumanApprovalGate** - Main gate node that interrupts execution
2. **GateManager** - Coordinates gates across pipeline stages
3. **ApprovalActionHandler** - Processes human responses

### Gate Locations

Four gates are positioned at key pipeline stages:

| Gate | Level | Stage | Required |
|------|-------|-------|----------|
| `paradigm_selection` | 1 | After paradigm selection | Optional |
| `technique_selection` | 2 | After technique selection | Optional |
| `decomposition_review` | 3 | After decomposition | Optional |
| `final_solution` | 4 | Before final output | **Required** |

## Usage

### Basic Usage

```python
from decomposition_pipeline.hitl import create_approval_gates, GateManager

# Create all gates
gates = create_approval_gates()

# Add to LangGraph
from langgraph.graph import StateGraph

graph = StateGraph(MyState)
graph.add_node("review_paradigms", gates["paradigm_selection"])
graph.add_node("review_techniques", gates["technique_selection"])
graph.add_node("review_decomposition", gates["decomposition_review"])
graph.add_node("review_final", gates["final_solution"])

# Compile with checkpointer for interrupts
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("pipeline.db")
app = graph.compile(checkpointer=checkpointer)
```

### Configuration

Configure gates through settings:

```python
config = {
    "approval_gates": {
        "paradigm_selection": {
            "enabled": True,
            "auto_approve_threshold": 0.95  # Auto-approve if confidence >= 0.95
        },
        "technique_selection": {
            "enabled": False  # Skip this gate
        },
        "decomposition_review": {
            "enabled": True,
            "auto_approve_threshold": 0.90
        },
        "final_solution": {
            "enabled": True  # Always enabled (required gate)
        }
    }
}

# Pass config when calling gate
result = gate(state, config)
```

### Managing Gates

```python
from decomposition_pipeline.hitl import GateManager

# Initialize manager with config
manager = GateManager(config)

# Check gate status
status = manager.get_gate_status(state)
print(f"Current stage: {status['current_stage']}")
print(f"Total approvals: {status['total_approvals']}")

# Get approval history
history = manager.get_approval_history(state)
for approval in history:
    print(f"{approval['gate_name']}: {approval['action']} by {approval['reviewer']}")

# Validate gate sequence
is_valid = manager.validate_gate_sequence(state)
```

## Approval Actions

When a gate activates, humans can take several actions:

### 1. Approve
Continue to next stage without changes.

```python
response = {
    "action": "approve",
    "reviewer": "user@example.com",
    "notes": "Looks good"
}
```

### 2. Reject
Backtrack to previous stage and re-run.

```python
response = {
    "action": "reject",
    "reviewer": "user@example.com",
    "notes": "Please reconsider the paradigm selection"
}
```

### 3. Modify
Edit state values and continue.

```python
response = {
    "action": "modify",
    "reviewer": "user@example.com",
    "notes": "Changed to temporal paradigm",
    "modifications": {
        "selected_paradigms": ["temporal", "functional"],
        "paradigm_scores.temporal": 0.95
    }
}
```

### 4. Backtrack
Jump to specific checkpoint.

```python
response = {
    "action": "backtrack",
    "reviewer": "user@example.com",
    "notes": "Need to start over",
    "backtrack_to": "problem_ingestion"
}
```

### 5. Add Context
Provide additional information and re-run current stage.

```python
response = {
    "action": "add_context",
    "reviewer": "user@example.com",
    "notes": "Adding domain constraints",
    "additional_context": "System must handle real-time streaming data"
}
```

### 6. Request Alternatives
Generate more options to choose from.

```python
response = {
    "action": "request_alternatives",
    "reviewer": "user@example.com",
    "notes": "Want to see other paradigm options",
    "alternative_count": 5
}
```

## Processing Responses

After gate resumption, process the response:

```python
from decomposition_pipeline.hitl import process_gate_response

# After interrupt is resumed, state contains _pending_gate_response
state = process_gate_response(state)

# Response is processed and state is updated based on action
if state.get("_backtrack_requested"):
    # Handle backtracking
    target_stage = state["_backtrack_to_stage"]
    # ... backtrack logic

elif state.get("_rerun_current_stage"):
    # Re-run current stage with added context
    # ... re-run logic

elif state.get("_generate_alternatives"):
    # Generate alternative options
    count = state["_alternative_count"]
    # ... generate alternatives
```

## Auto-Approval

Gates can auto-approve when confidence is high:

```python
# Configure threshold
config = {
    "approval_gates": {
        "paradigm_selection": {
            "enabled": True,
            "auto_approve_threshold": 0.95
        }
    }
}

# Gate checks confidence and auto-approves if threshold met
# For Level 1: checks max paradigm_scores
# For Level 2: checks average technique_scores
# For Level 3: checks validation completeness_score
```

## Review Data Format

Each gate prepares stage-specific review data:

### Level 1 - Paradigm Selection
```python
{
    "gate": "paradigm_selection",
    "stage": "Level 1",
    "state_snapshot": {
        "selected_paradigms": ["structural", "functional"],
        "paradigm_scores": {"structural": 0.85, "functional": 0.78},
        "paradigm_reasoning": {...},
        "rejected_paradigms": {"temporal": 0.45}
    },
    "options": ["approve", "reject", "modify", ...],
    "context": {...}
}
```

### Level 2 - Technique Selection
```python
{
    "gate": "technique_selection",
    "stage": "Level 2",
    "state_snapshot": {
        "selected_techniques": {...},
        "technique_scores": {...},
        "technique_justification": {...}
    },
    "options": [...],
    "context": {...}
}
```

### Level 3 - Decomposition Review
```python
{
    "gate": "decomposition_review",
    "stage": "Level 3",
    "state_snapshot": {
        "integrated_subproblems": [...],
        "subproblem_dependencies": {...},
        "validation_results": {...}
    },
    "options": [...],
    "context": {...}
}
```

### Level 4 - Final Solution
```python
{
    "gate": "final_solution",
    "stage": "Level 4",
    "state_snapshot": {
        "integrated_solution": {...},
        "validation_results": {...},
        "implementation_plan": {...}
    },
    "options": [...],
    "context": {...}
}
```

## State Schema

Gates add these fields to state:

```python
class PipelineState(TypedDict):
    # ... other fields

    # Approval history
    human_approvals: List[ApprovalRecord]

    # Human-provided context
    human_context: List[Dict[str, Any]]

    # Modification history
    _modification_history: List[Dict[str, Any]]

    # Control flags (internal)
    _pending_gate_response: Optional[GateResponse]
    _backtrack_requested: Optional[bool]
    _backtrack_to_stage: Optional[str]
    _backtrack_reason: Optional[str]
    _rerun_current_stage: Optional[bool]
    _generate_alternatives: Optional[bool]
    _alternative_count: Optional[int]
```

## Testing

Run tests with pytest:

```bash
cd backend
pytest tests/decomposition_pipeline/hitl/ -v --cov=src/decomposition_pipeline/hitl
```

Current test coverage: **94%**

## Example: Complete Workflow

```python
from langgraph.graph import StateGraph, END
from decomposition_pipeline.hitl import create_approval_gates, GateManager, process_gate_response

# Create graph
graph = StateGraph(MyState)

# Create gates
gates = create_approval_gates()

# Add gates to graph
graph.add_node("level_1_analyze", analyze_node)
graph.add_node("gate_1", gates["paradigm_selection"])
graph.add_node("process_gate_1", lambda s: process_gate_response(s))

graph.add_node("level_2_select", select_node)
graph.add_node("gate_2", gates["technique_selection"])
graph.add_node("process_gate_2", lambda s: process_gate_response(s))

# ... more nodes

# Edges
graph.add_edge("level_1_analyze", "gate_1")
graph.add_edge("gate_1", "process_gate_1")

# Conditional edge based on action
def route_after_gate(state):
    if state.get("_backtrack_requested"):
        return "backtrack_handler"
    elif state.get("_rerun_current_stage"):
        return "level_1_analyze"  # Re-run
    else:
        return "level_2_select"  # Continue

graph.add_conditional_edges("process_gate_1", route_after_gate)

# Compile with checkpointer
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("pipeline.db")
app = graph.compile(checkpointer=checkpointer)

# Execute
config = {
    "configurable": {"thread_id": "thread_1"},
    "approval_gates": {
        "paradigm_selection": {"enabled": True}
    }
}

# First invocation - runs until gate 1
result = app.invoke(initial_state, config)

# Gate interrupts here - control returns to user
# User reviews and provides response through API

# Resume with response
response = {
    "action": "approve",
    "reviewer": "user@example.com",
    "notes": "Looks good"
}

# Second invocation - resumes from gate 1
result = app.invoke(response, config)
```

## References

- **brainstorm_1.md**: HITL Gates section (lines 620-695)
- **LangGraph Documentation**: [Interrupt mechanism](https://langchain-ai.github.io/langgraph/concepts/low_level/#interrupt)
- **LangGraph Checkpointing**: [State persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)

## Future Enhancements

- Support for multiple concurrent reviewers
- Voting mechanisms for conflicting decisions
- Approval delegation workflows
- Audit trail export
- Integration with notification systems
