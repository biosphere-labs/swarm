/**
 * Custom React Flow node component for displaying subproblems
 */

'use client';

import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { cn } from '@/lib/utils';
import {
  Subproblem,
  PARADIGM_COLORS,
  STATUS_COLORS,
} from '@/types/decomposition';

interface SubproblemNodeData extends Subproblem {}

/**
 * Custom node component for subproblems in decomposition graph
 */
export const SubproblemNode = memo(({ data, selected }: NodeProps<SubproblemNodeData>) => {
  const paradigmColor = PARADIGM_COLORS[data.paradigm];
  const statusColor = STATUS_COLORS[data.status];

  // Status icon
  const StatusIcon = () => {
    switch (data.status) {
      case 'complete':
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'in_progress':
        return (
          <svg className="w-4 h-4 text-yellow-600 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  // Complexity badge color
  const complexityColor = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
  }[data.complexity || 'medium'];

  return (
    <div
      className={cn(
        'rounded-lg border-2 bg-white shadow-lg transition-all',
        paradigmColor,
        statusColor,
        selected && 'ring-4 ring-blue-300 shadow-xl'
      )}
      style={{ width: 200, minHeight: 100 }}
    >
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-gray-400"
      />

      {/* Node content */}
      <div className="p-3 space-y-2">
        {/* Header with status icon */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900 line-clamp-2" title={data.title}>
              {data.title}
            </h3>
          </div>
          <div className="flex-shrink-0">
            <StatusIcon />
          </div>
        </div>

        {/* Paradigm badge */}
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-white bg-opacity-90 text-gray-700">
            {data.paradigm}
          </span>
          {data.complexity && (
            <span className={cn('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', complexityColor)}>
              {data.complexity}
            </span>
          )}
        </div>

        {/* Technique */}
        {data.technique && (
          <div className="text-xs text-gray-600 truncate" title={data.technique}>
            {data.technique}
          </div>
        )}

        {/* Assigned agent */}
        {data.assignedAgent && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span className="truncate">{data.assignedAgent}</span>
          </div>
        )}

        {/* Confidence indicator */}
        {data.confidence !== undefined && (
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all"
                style={{ width: `${data.confidence * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 flex-shrink-0">
              {Math.round(data.confidence * 100)}%
            </span>
          </div>
        )}
      </div>

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-gray-400"
      />
    </div>
  );
});

SubproblemNode.displayName = 'SubproblemNode';
