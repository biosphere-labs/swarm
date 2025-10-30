# Agent Task: Build Agent Pool Activity Monitor

## Task ID
#23

## Objective
Build a real-time Agent Pool Activity Monitor component for the frontend that displays the status and activity of all agent pools in the decomposition pipeline.

## Context
- The backend has 13 agent pools implemented (8 paradigm pools + 5 domain/general pools)
- Each pool manages multiple agents that execute subproblem solutions
- The backend provides metrics including active/idle/stuck agents, task counts, and response times
- SSE endpoint exists for real-time pipeline updates

## Requirements

### Component: AgentPoolMonitor
**Location:** `frontend/components/AgentPoolMonitor.tsx`

**Features:**
1. Display all 13 agent pools with real-time status
2. Show metrics per pool:
   - Total agents
   - Active/Idle/Stuck agent counts
   - Current queue size
   - Average response time
   - Total tasks completed
3. Visualize pool utilization using Recharts (bar chart or similar)
4. Real-time updates via SSE connection
5. Handle SSE connection states (connecting, connected, disconnected)
6. Follow existing component patterns (shadcn/ui, Tailwind CSS)

### Pool Configuration
The component should display these pools:

**Paradigm Pools (8):**
- structural (50 agents)
- functional (50 agents)
- temporal (50 agents)
- spatial (50 agents)
- hierarchical (50 agents)
- computational (50 agents)
- data (50 agents)
- dependency (50 agents)

**Domain Pools (4):**
- api_design (30 agents)
- data_processing (30 agents)
- ml_modeling (20 agents)
- security (20 agents)

**General Pool (1):**
- general (10 agents)

### Tests
**Location:** `frontend/__tests__/AgentPoolMonitor.test.tsx`

**Test Coverage:**
1. Component renders correctly
2. Displays all pools with correct initial data
3. Updates when receiving SSE events
4. Handles connection states (connecting, connected, error, disconnected)
5. Shows correct metrics for each pool
6. Visualizations render properly
7. Error states are handled gracefully

## Technical Considerations

### Data Structure
```typescript
interface PoolMetrics {
  pool_name: string;
  total_agents: number;
  active_agents: number;
  idle_agents: number;
  stuck_agents: number;
  total_tasks_completed: number;
  average_response_time: number;
  current_queue_size: number;
  timestamp: string;
}
```

### SSE Integration
- Connect to `/api/agent-pools/stream` endpoint (or similar)
- Handle events: `pool_update`, `agent_status_change`, `heartbeat`
- Gracefully handle disconnections and reconnections
- Display connection status to user

### Styling
- Use shadcn/ui components (Card, Badge, etc.)
- Tailwind CSS for custom styling
- Responsive design (mobile and desktop)
- Color coding for agent states (idle: gray, working: blue, stuck: red)

## Deliverables
1. AgentPoolMonitor component implementation
2. Comprehensive test suite
3. WORK_SUMMARY.md documentation
4. Git commit and PR

## Success Criteria
- Component renders all 13 pools
- Real-time updates work via SSE
- Tests pass with good coverage
- Follows existing code patterns
- Responsive and accessible UI
