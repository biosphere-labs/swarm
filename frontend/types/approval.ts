/**
 * TypeScript types for Human-in-the-Loop approval gates
 * Corresponds to backend types in decomposition_pipeline/hitl/types.py
 */

/**
 * Approval action types
 */
export type ApprovalAction =
  | 'approve'
  | 'reject'
  | 'modify'
  | 'backtrack'
  | 'add_context'
  | 'request_alternatives';

/**
 * Record of a human approval decision
 */
export interface ApprovalRecord {
  gate_name: string;
  timestamp: number;
  action: ApprovalAction;
  reviewer: string;
  notes?: string;
  modifications?: Record<string, any>;
}

/**
 * Configuration for an approval gate
 */
export interface GateConfig {
  name: string;
  enabled: boolean;
  required: boolean;
  level: number;
  description: string;
}

/**
 * Data prepared for human review at a gate
 */
export interface GateReviewData {
  gate: string;
  stage: string;
  state_snapshot: Record<string, any>;
  options: string[];
  alternatives?: Array<Record<string, any>>;
  context: {
    description: string;
    level: number;
    required: boolean;
    stage_description?: string;
  };
}

/**
 * Response from human at approval gate
 */
export interface GateResponse {
  action: ApprovalAction;
  reviewer: string;
  notes?: string;
  modifications?: Record<string, any>;
  selected_alternative?: number;
  additional_context?: string;
  backtrack_to?: string;
}

/**
 * Checkpoint information for backtracking
 */
export interface CheckpointInfo {
  checkpoint_id: string;
  stage: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

/**
 * Props for HumanApprovalGatePanel component
 */
export interface HumanApprovalGatePanelProps {
  runId: string;
  gateData: GateReviewData;
  approvalHistory?: ApprovalRecord[];
  checkpoints?: CheckpointInfo[];
  onApprove?: (response: GateResponse) => void;
  onReject?: (response: GateResponse) => void;
  onModify?: (response: GateResponse) => void;
  onBacktrack?: (response: GateResponse) => void;
  onAddContext?: (response: GateResponse) => void;
  onRequestAlternatives?: (response: GateResponse) => void;
  isLoading?: boolean;
  error?: string;
}

/**
 * API request types
 */
export interface ApproveRequest {
  reviewer: string;
  notes?: string;
  modifications?: Record<string, any>;
}

export interface RejectRequest {
  reviewer: string;
  reason: string;
  backtrack_to?: string;
}

export interface ModifyStateRequest {
  reviewer: string;
  modifications: Record<string, any>;
  notes?: string;
  continue_after?: boolean;
}

export interface BacktrackRequest {
  reviewer: string;
  checkpoint_id?: string;
  stage?: string;
  reason?: string;
}

export interface AddContextRequest {
  reviewer: string;
  additional_context: string;
  rerun_from?: string;
}

export interface RequestAlternativesRequest {
  reviewer: string;
  requirements?: string;
  count?: number;
}

/**
 * API response types
 */
export interface SuccessResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
}

export interface ErrorResponse {
  success: false;
  error: string;
  detail?: string;
}

/**
 * Gate level descriptions
 */
export const GATE_LEVEL_DESCRIPTIONS: Record<number, string> = {
  1: 'Paradigm Selection',
  2: 'Technique Selection',
  3: 'Decomposition Review',
  4: 'Final Solution Review',
};

/**
 * Action button configurations
 */
export interface ActionButtonConfig {
  action: ApprovalAction;
  label: string;
  description: string;
  variant: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  requiresConfirmation: boolean;
  requiresInput: boolean;
  icon?: string;
}

export const ACTION_BUTTON_CONFIGS: Record<ApprovalAction, ActionButtonConfig> = {
  approve: {
    action: 'approve',
    label: 'Approve',
    description: 'Approve and continue to next stage',
    variant: 'default',
    requiresConfirmation: false,
    requiresInput: false,
  },
  reject: {
    action: 'reject',
    label: 'Reject',
    description: 'Reject current decision and backtrack',
    variant: 'destructive',
    requiresConfirmation: true,
    requiresInput: true,
  },
  modify: {
    action: 'modify',
    label: 'Modify',
    description: 'Modify the current state',
    variant: 'outline',
    requiresConfirmation: false,
    requiresInput: true,
  },
  backtrack: {
    action: 'backtrack',
    label: 'Backtrack',
    description: 'Return to a previous checkpoint',
    variant: 'outline',
    requiresConfirmation: true,
    requiresInput: true,
  },
  add_context: {
    action: 'add_context',
    label: 'Add Context',
    description: 'Provide additional context for reprocessing',
    variant: 'secondary',
    requiresConfirmation: false,
    requiresInput: true,
  },
  request_alternatives: {
    action: 'request_alternatives',
    label: 'Request Alternatives',
    description: 'Request alternative solutions',
    variant: 'secondary',
    requiresConfirmation: false,
    requiresInput: true,
  },
};
