# Swarm

A multi-agent problem decomposition system with a Python backend and Next.js frontend. The system takes complex problems, decomposes them through multiple paradigm lenses using specialized AI agent pools, and synthesizes integrated solutions -- all with human-in-the-loop approval gates at each stage.

## Status

**Experimental prototype.** This project was built to explore multi-agent AI orchestration patterns for parallel problem decomposition. It is not actively maintained.

## Architecture Overview

The system implements a 5-level decomposition pipeline orchestrated by LangGraph:

```
Problem Input
    |
    v
Level 1: Paradigm Selection
    |  Analyzes the problem and selects applicable decomposition paradigms
    |  (structural, functional, temporal, spatial, hierarchical, computational, data, dependency)
    v
  [Approval Gate 1]
    |
    v
Level 2: Technique Selection
    |  Selects specific algorithmic techniques from a formal catalog for each paradigm
    v
  [Approval Gate 2]
    |
    v
Level 3: Decomposition Execution + Integration
    |  Runs paradigm-specific decomposition subgraphs in parallel,
    |  then integrates results (overlap detection, conflict resolution, dependency graphing)
    v
  [Approval Gate 3]
    |
    v
Level 4: Solution Generation
    |  Routes subproblems to specialized agent pools for parallel solving
    v
Level 5: Solution Integration
    |  Merges partial solutions, fills gaps, resolves conflicts, validates completeness
    v
  [Approval Gate 4 - required]
    |
    v
Final Output
```

### Agent Pool Architecture

The backend manages three categories of agent pools:

- **Paradigm Pools (8 pools, 50 agents each):** Specialized for structural, functional, temporal, spatial, hierarchical, computational, data, and dependency decomposition. Each pool uses focused LLM instances tuned for its paradigm.

- **Domain Pools (4 pools, 20-30 agents each):** Specialized for cross-cutting concerns like API design, data processing, ML modeling, and security analysis.

- **General Pool (1 pool, 10 agents):** Uses a larger model for complex or novel problems that do not fit neatly into paradigm or domain categories.

Pools implement load balancing (least-loaded agent selection), task queuing, health monitoring, and stuck-agent recovery.

### Human-in-the-Loop Controls

Four approval gates can pause pipeline execution using LangGraph's interrupt mechanism. At each gate, a human reviewer can:

- Approve and continue
- Reject and backtrack to a previous level
- Modify the current selections
- Add additional context
- Request alternative approaches

Gates support configurable auto-approval based on confidence thresholds. Gate 4 (final review) is always required.

### Real-Time Monitoring Dashboard

The frontend provides a control center for observing and interacting with pipeline runs:

- **Pipeline Monitor:** Tracks execution progress through all 5 levels via Server-Sent Events (SSE)
- **Agent Pool Monitor:** Displays utilization, active/idle/stuck agent counts, queue sizes, and response times across all 13 pools with bar chart visualizations
- **Decomposition Graph Visualization:** Interactive ReactFlow-based graph showing subproblem structure and dependencies
- **Human Approval Panel:** Interface for reviewing and acting on approval gate requests
- **Integration Conflict Viewer:** Displays detected conflicts and overlap between paradigm decompositions

## Tech Stack

### Backend

- **Python 3.13+** with FastAPI and Uvicorn
- **LangGraph** for stateful multi-step graph orchestration with checkpointing
- **LangChain** with OpenAI and Anthropic provider support
- **SSE (sse-starlette)** for real-time event streaming to the frontend
- **SQLite** for checkpoint persistence and state recovery
- **Pydantic** for request/response validation and settings management

### Frontend

- **Next.js 14** with App Router and TypeScript
- **Tailwind CSS** with shadcn/ui (Radix UI primitives)
- **ReactFlow** for interactive graph visualization
- **Recharts** for pool utilization charts and metrics
- **Zustand** for client-side state management
- **react-markdown** with remark-gfm for rendering LLM output

## Project Structure

```
swarm/
  backend/
    src/decomposition_pipeline/
      agents/          # Agent pool management, routing, and types
      api/             # FastAPI app, pipeline and SSE routers
      catalog/         # Decomposition technique catalog and models
      checkpoint/      # State persistence and recovery
      config/          # Application settings
      errors/          # Exception types and error handlers
      graphs/          # LangGraph graph definitions
        level1_paradigm/       # Paradigm selection subgraph
        level2_technique/      # Technique selection subgraph
        level3_decomposition/  # 8 paradigm-specific decomposition subgraphs
        level3_integration/    # Cross-paradigm integration subgraph
        level4_solution/       # Parallel solution generation subgraph
        level5_integration/    # Solution synthesis subgraph
        main_graph.py          # Top-level orchestration graph
      hitl/            # Human-in-the-loop approval gates
      schemas/         # TypedDict state definitions for all levels
      middleware/      # Error handling middleware
  frontend/
    app/               # Next.js pages and API routes
    components/        # React components (monitors, visualizations, panels)
    hooks/             # Custom hooks (SSE connection)
    lib/               # API client, utilities, settings store
```

## Getting Started

### Prerequisites

- Python 3.13+ with [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- An OpenAI or Anthropic API key

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env and add your API key(s)
uv sync
uv run uvicorn decomposition_pipeline.api.app:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the control center.

## License

All rights reserved.
