// Type definitions for visualization components

export type NodeStatus = 'pending' | 'in_progress' | 'complete' | 'failed';

export interface SubproblemNode {
  id: string;
  title: string;
  description?: string;
  paradigm: string;
  technique: string;
  status: NodeStatus;
  assignedAgent?: string;
  complexity?: number;
  position?: { x: number; y: number };
}

export interface SubproblemEdge {
  id: string;
  source: string;
  target: string;
  type?: 'dependency' | 'data_flow' | 'temporal';
  animated?: boolean;
  label?: string;
}

export interface AgentPool {
  name: string;
  paradigm: string;
  totalAgents: number;
  activeAgents: number;
  averageResponseTime: number;
  currentTasks: number;
  agents?: Agent[];
}

export interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'working' | 'stuck';
  currentTask?: string;
  taskStartTime?: Date;
}

export interface MetricData {
  timestamp: Date;
  value: number;
  label?: string;
}

export interface PipelineMetrics {
  tokenUsage: MetricData[];
  executionTime: MetricData[];
  agentUtilization: MetricData[];
  successRate: MetricData[];
}

export interface ExecutionEvent {
  id: string;
  type: 'node_enter' | 'node_exit' | 'approval_required' | 'error';
  timestamp: Date;
  nodeName: string;
  duration?: number;
  metadata?: Record<string, any>;
}

export interface TimelineEvent {
  id: string;
  name: string;
  startTime: Date;
  endTime?: Date;
  type: 'stage' | 'task' | 'approval';
  status: NodeStatus;
  children?: TimelineEvent[];
}

// Paradigm colors for consistent visualization
export const PARADIGM_COLORS: Record<string, string> = {
  structural: '#3b82f6', // blue
  functional: '#10b981', // green
  temporal: '#8b5cf6', // purple
  spatial: '#f59e0b', // amber
  hierarchical: '#ec4899', // pink
  computational: '#14b8a6', // teal
  data: '#f97316', // orange
  dependency: '#6366f1', // indigo
};

export const STATUS_COLORS: Record<NodeStatus, string> = {
  pending: '#9ca3af', // gray
  in_progress: '#3b82f6', // blue
  complete: '#10b981', // green
  failed: '#ef4444', // red
};
