/**
 * TypeScript types for Server-Sent Events (SSE) connection and events
 */

/**
 * SSE connection states
 */
export type SSEConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

/**
 * Pipeline run status
 */
export type PipelineStatus = 'unknown' | 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

/**
 * Pipeline execution stages
 */
export type PipelineStage =
  | 'unknown'
  | 'initialization'
  | 'level1_paradigm'
  | 'level2_technique'
  | 'level3_decomposition'
  | 'level3_integration'
  | 'level4_solution'
  | 'level5_integration'
  | 'finalization';

/**
 * SSE event types sent by the backend
 */
export type SSEEventType =
  | 'state_update'
  | 'status_change'
  | 'stage_change'
  | 'approval_required'
  | 'pipeline_finished'
  | 'heartbeat'
  | 'error';

/**
 * Base SSE event structure
 */
export interface SSEEvent {
  run_id: string;
  timestamp?: string;
}

/**
 * State update event - complete state snapshot
 */
export interface StateUpdateEvent extends SSEEvent {
  status: PipelineStatus;
  current_stage: PipelineStage;
}

/**
 * Status change event - pipeline status changed
 */
export interface StatusChangeEvent extends SSEEvent {
  status: PipelineStatus;
}

/**
 * Stage change event - pipeline moved to new stage
 */
export interface StageChangeEvent extends SSEEvent {
  stage: PipelineStage;
}

/**
 * Approval required event - human-in-the-loop gate
 */
export interface ApprovalRequiredEvent extends SSEEvent {
  gate: string;
  stage: PipelineStage;
}

/**
 * Pipeline finished event - final state
 */
export interface PipelineFinishedEvent extends SSEEvent {
  status: PipelineStatus;
  completed_at?: string;
}

/**
 * Heartbeat event - keep connection alive
 */
export interface HeartbeatEvent extends SSEEvent {
  // Inherits timestamp from SSEEvent
}

/**
 * Error event - connection or pipeline error
 */
export interface ErrorEvent extends SSEEvent {
  error: string;
}

/**
 * Union type of all possible event payloads
 */
export type SSEEventPayload =
  | StateUpdateEvent
  | StatusChangeEvent
  | StageChangeEvent
  | ApprovalRequiredEvent
  | PipelineFinishedEvent
  | HeartbeatEvent
  | ErrorEvent;

/**
 * Full SSE event with type and data
 */
export interface SSEFullEvent {
  type: SSEEventType;
  data: SSEEventPayload;
}

/**
 * Pipeline state managed by SSE hook
 */
export interface PipelineState {
  run_id: string | null;
  status: PipelineStatus;
  current_stage: PipelineStage;
  awaiting_approval: boolean;
  approval_gate?: string;
  completed_at?: string;
  error?: string;
  last_update?: string;
}

/**
 * SSE connection configuration
 */
export interface SSEConnectionConfig {
  /**
   * Base URL for the API (default: /api)
   */
  baseUrl?: string;

  /**
   * Maximum number of reconnection attempts (default: 5)
   */
  maxReconnectAttempts?: number;

  /**
   * Initial reconnection delay in ms (default: 1000)
   */
  initialReconnectDelay?: number;

  /**
   * Maximum reconnection delay in ms (default: 30000)
   */
  maxReconnectDelay?: number;

  /**
   * Reconnection backoff multiplier (default: 2)
   */
  reconnectBackoffMultiplier?: number;

  /**
   * Enable debug logging (default: false)
   */
  debug?: boolean;
}

/**
 * Return type of useSSEConnection hook
 */
export interface UseSSEConnectionReturn {
  /**
   * Current pipeline state
   */
  state: PipelineState;

  /**
   * Current connection status
   */
  connectionStatus: SSEConnectionStatus;

  /**
   * Error message if connection failed
   */
  error: string | null;

  /**
   * Manually trigger reconnection
   */
  reconnect: () => void;

  /**
   * Close the connection manually
   */
  disconnect: () => void;

  /**
   * Check if currently connected
   */
  isConnected: boolean;
}

/**
 * Default initial pipeline state
 */
export const DEFAULT_PIPELINE_STATE: PipelineState = {
  run_id: null,
  status: 'unknown',
  current_stage: 'unknown',
  awaiting_approval: false,
};

/**
 * Default SSE connection configuration
 */
export const DEFAULT_SSE_CONFIG: Required<SSEConnectionConfig> = {
  baseUrl: '/api',
  maxReconnectAttempts: 5,
  initialReconnectDelay: 1000,
  maxReconnectDelay: 30000,
  reconnectBackoffMultiplier: 2,
  debug: false,
};
