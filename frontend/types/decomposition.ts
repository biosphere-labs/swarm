/**
 * TypeScript types for decomposition graph visualization
 */

/**
 * Decomposition paradigm types
 */
export type ParadigmType =
  | 'structural'
  | 'functional'
  | 'temporal'
  | 'spatial'
  | 'hierarchical'
  | 'computational'
  | 'data'
  | 'dependency';

/**
 * Subproblem status types
 */
export type SubproblemStatus = 'pending' | 'in_progress' | 'complete';

/**
 * Subproblem node in decomposition graph
 */
export interface Subproblem {
  id: string;
  title: string;
  description?: string;
  paradigm: ParadigmType;
  technique?: string;
  status: SubproblemStatus;
  assignedAgent?: string;
  confidence?: number;
  complexity?: 'low' | 'medium' | 'high';
  metadata?: Record<string, any>;
}

/**
 * Dependency between subproblems
 */
export interface SubproblemDependency {
  id: string;
  source: string; // source subproblem id
  target: string; // target subproblem id
  type?: 'prerequisite' | 'parallel' | 'optional';
  description?: string;
}

/**
 * Decomposition graph data structure
 */
export interface DecompositionGraph {
  subproblems: Subproblem[];
  dependencies: SubproblemDependency[];
  metadata?: {
    originalProblem?: string;
    paradigmsUsed?: ParadigmType[];
    timestamp?: string;
  };
}

/**
 * Node position in graph layout
 */
export interface NodePosition {
  x: number;
  y: number;
}

/**
 * Layout configuration options
 */
export interface LayoutConfig {
  direction?: 'TB' | 'BT' | 'LR' | 'RL'; // Top-Bottom, Bottom-Top, Left-Right, Right-Left
  nodeWidth?: number;
  nodeHeight?: number;
  rankSep?: number; // separation between ranks
  nodeSep?: number; // separation between nodes in same rank
}

/**
 * Paradigm color mapping
 */
export const PARADIGM_COLORS: Record<ParadigmType, string> = {
  structural: 'bg-blue-500 border-blue-600',
  functional: 'bg-green-500 border-green-600',
  temporal: 'bg-purple-500 border-purple-600',
  spatial: 'bg-yellow-500 border-yellow-600',
  hierarchical: 'bg-red-500 border-red-600',
  computational: 'bg-indigo-500 border-indigo-600',
  data: 'bg-teal-500 border-teal-600',
  dependency: 'bg-orange-500 border-orange-600',
};

/**
 * Status color mapping
 */
export const STATUS_COLORS: Record<SubproblemStatus, string> = {
  pending: 'border-gray-400',
  in_progress: 'border-yellow-400 animate-pulse',
  complete: 'border-green-400',
};
