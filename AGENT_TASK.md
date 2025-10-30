
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
=======
# Agent Task

**Task:** Set up backend project structure with FastAPI, LangGraph, and dependencies
**Branch:** feature/setup-backend-structure
**Started:** 2025-10-30T17:23:00Z
**Priority:** HIGH (foundational task)
**Estimated:** N/A

## Description

Set up a complete Python backend project using FastAPI and LangGraph for the Decomposition Pipeline system. This includes:

1. Initialize a UV-based Python project with proper structure
2. Configure dependencies for FastAPI, LangGraph, and related tools
3. Create a modular directory structure for the 5-level pipeline architecture
4. Set up configuration management and environment handling
5. Create initial FastAPI application with health check endpoint
6. Configure CORS for frontend integration
7. Set up development tools (linting, formatting, type checking)

## Acceptance Criteria

- UV project initialized with pyproject.toml
- All core dependencies declared (fastapi, langgraph, langchain, uvicorn, etc.)
- Directory structure follows clean architecture principles
- Backend directory contains organized modules for:
  - API endpoints (routers)
  - LangGraph subgraphs (by level)
  - State schemas
  - Agent pools
  - Utilities
- FastAPI application runs successfully with health check endpoint
- CORS configured for local development
- Development tools configured (ruff, mypy, pytest)
- README.md with setup and run instructions

## Implementation Notes

### Project Initialization (Completed)
- Initialized UV project in `backend/` directory
- Project name: `decomposition-pipeline`
- Python version: 3.13+
- Build system: Hatchling (for editable installs)

### Dependencies Installed (Completed)
**Core Dependencies:**
- fastapi 0.120.2 - Web framework
- uvicorn 0.38.0 - ASGI server
- langgraph 1.0.2 - LangGraph framework
- langchain 1.0.3 - LangChain core
- langchain-anthropic 1.0.0 - Anthropic provider
- langchain-openai 1.0.1 - OpenAI provider
- pydantic 2.12.3 - Data validation
- pydantic-settings 2.11.0 - Settings management
- python-dotenv 1.2.1 - Environment variables
- sse-starlette 3.0.2 - Server-Sent Events
- aiosqlite 0.21.0 - Async SQLite

**Dev Dependencies:**
- pytest 8.4.2 - Testing framework
- pytest-asyncio 1.2.0 - Async test support
- pytest-cov 7.0.0 - Coverage reporting
- ruff 0.14.2 - Linter and formatter
- mypy 1.18.2 - Type checker
- httpx 0.28.1 - HTTP client for tests
- hatchling 1.27.0 - Build system

### Directory Structure Created (Completed)
```
backend/
├── src/decomposition_pipeline/
│   ├── api/              # FastAPI app and routes
│   ├── graphs/           # LangGraph subgraphs by level
│   │   ├── level1_paradigm/
│   │   ├── level2_technique/
│   │   ├── level3_decomposition/
│   │   ├── level3_integration/
│   │   ├── level4_solution/
│   │   └── level5_integration/
│   ├── schemas/          # Pydantic state schemas
│   ├── agents/           # Agent pool management
│   ├── utils/            # Utility functions
│   ├── config/           # Configuration
│   └── main.py           # Entry point
├── tests/                # Test suite
├── data/                 # Data directory (gitignored)
└── configuration files
```

### Configuration Files Created (Completed)
- `pyproject.toml` - UV project configuration with dependencies
- `ruff.toml` - Linter/formatter configuration
- `mypy.ini` - Type checker configuration
- `pytest.ini` - Test configuration
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore patterns
- `README.md` - Comprehensive documentation

### FastAPI Application (Completed)
Created `src/decomposition_pipeline/api/app.py` with:
- Lifespan context manager for startup/shutdown
- CORS middleware configuration
- Three endpoints:
  - `GET /` - API information
  - `GET /health` - Health check
  - `GET /api/v1/status` - Configuration status
- Settings integration from environment

### Configuration Management (Completed)
Created `src/decomposition_pipeline/config/settings.py` with:
- Pydantic Settings for environment variable management
- API configuration (title, version, debug mode)
- CORS configuration
- LLM provider configuration (OpenAI/Anthropic)
- LangGraph configuration (checkpoints, limits)
- Agent pool configuration
- Human-in-the-loop approval gates configuration
- Logging configuration

### Tests (Completed)
Created `tests/test_api.py` with:
- Fixture for test client
- Three test cases for all endpoints
- 79% code coverage achieved
- All tests passing

### Development Tools (Completed)
- Ruff: Formatted and linted all code successfully
- Tests: All 3 tests passing with 79% coverage
- Server: Verified successful startup on port 8000

### Key Decisions
1. Used src-layout for better packaging practices
2. Separated graph subgraphs by level for clarity
3. Used pydantic-settings for configuration management
4. Configured both OpenAI and Anthropic providers
5. Made approval gates configurable per pipeline level
6. Used hatchling as build backend for UV compatibility

