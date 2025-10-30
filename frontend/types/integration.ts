/**
 * TypeScript types for Level 3 Integration and conflict resolution
 */

import { Subproblem } from './decomposition';

/**
 * Resolution strategy types for conflicts
 */
export type ResolutionStrategy =
  | 'merge'           // Merge subproblems (same paradigm)
  | 'multiview'       // Create multi-view subproblem (different paradigms)
  | 'keep_both'       // Keep both subproblems as separate
  | 'discard_first'   // Keep second, discard first
  | 'discard_second'  // Keep first, discard second
  | 'manual';         // Manual resolution with custom description

/**
 * Status of conflict resolution
 */
export type ConflictResolutionStatus = 'pending' | 'resolved' | 'rejected';

/**
 * Similarity metrics for conflict detection
 */
export interface SimilarityMetrics {
  jaccard?: number;      // Jaccard similarity (0-1)
  cosine?: number;       // Cosine similarity (0-1)
  structural?: number;   // Structural similarity (0-1)
  combined: number;      // Combined weighted similarity (0-1)
}

/**
 * Detected conflict between subproblems
 */
export interface SubproblemConflict {
  id: string;
  subproblemIds: string[];           // IDs of conflicting subproblems
  subproblems: Subproblem[];         // Full subproblem data
  paradigms: string[];               // Paradigms involved
  similarity: SimilarityMetrics;     // Similarity scores
  detectedAt?: string;               // ISO timestamp
  recommendedStrategy?: ResolutionStrategy;  // Backend recommendation
  status: ConflictResolutionStatus;
}

/**
 * Resolution applied to a conflict
 */
export interface ConflictResolution {
  conflictId: string;
  strategy: ResolutionStrategy;
  resolvedAt: string;                // ISO timestamp
  resolvedBy?: string;               // User ID or 'system'
  mergedSubproblem?: Subproblem;     // Result if merged/multiview
  customDescription?: string;         // For manual resolution
  notes?: string;                    // Additional notes
}

/**
 * Integration state data
 */
export interface IntegrationState {
  allSubproblems: Subproblem[];
  overlapClusters: string[][];       // Clusters of overlapping IDs
  similarityMatrix: Record<string, number>;  // "(id1,id2)" -> similarity
  detectedConflicts: SubproblemConflict[];
  resolvedSubproblems?: Subproblem[];
  resolutions?: ConflictResolution[];
}

/**
 * Props for IntegrationConflictViewer component
 */
export interface IntegrationConflictViewerProps {
  conflicts: SubproblemConflict[];
  onResolve?: (conflictId: string, resolution: ConflictResolution) => void;
  onReject?: (conflictId: string) => void;
  readOnly?: boolean;
  className?: string;
}

/**
 * Conflict filter options
 */
export interface ConflictFilter {
  status?: ConflictResolutionStatus[];
  paradigms?: string[];
  minSimilarity?: number;
  maxSimilarity?: number;
}

/**
 * Statistics about conflicts
 */
export interface ConflictStatistics {
  total: number;
  resolved: number;
  pending: number;
  rejected: number;
  byParadigm: Record<string, number>;
  averageSimilarity: number;
}
