/**
 * Decomposition Graph Visualization Component
 * Uses React Flow to display hierarchical decomposition structure
 */

'use client';

import { useCallback, useMemo, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { SubproblemNode } from './SubproblemNode';
import {
  DecompositionGraph,
  LayoutConfig,
  PARADIGM_COLORS,
  ParadigmType,
} from '@/types/decomposition';
import { prepareGraphData } from '@/lib/layoutUtils';

const nodeTypes = {
  subproblem: SubproblemNode,
};

interface DecompositionGraphVizProps {
  /** Graph data containing subproblems and dependencies */
  graph: DecompositionGraph;
  /** Layout configuration */
  layoutConfig?: LayoutConfig;
  /** Callback when a node is selected */
  onNodeSelect?: (nodeId: string | null) => void;
  /** Height of the component */
  height?: string | number;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Main decomposition graph visualization component
 */
export function DecompositionGraphViz({
  graph,
  layoutConfig,
  onNodeSelect,
  height = '600px',
  className = '',
}: DecompositionGraphVizProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Prepare graph data with layout
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    return prepareGraphData(
      graph.subproblems,
      graph.dependencies,
      layoutConfig
    );
  }, [graph.subproblems, graph.dependencies, layoutConfig]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Handle node click
  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      setSelectedNodeId(node.id);
      onNodeSelect?.(node.id);
    },
    [onNodeSelect]
  );

  // Handle pane click (deselect)
  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
    onNodeSelect?.(null);
  }, [onNodeSelect]);

  // Calculate paradigm statistics
  const paradigmStats = useMemo(() => {
    const stats = new Map<ParadigmType, number>();
    graph.subproblems.forEach(sp => {
      stats.set(sp.paradigm, (stats.get(sp.paradigm) || 0) + 1);
    });
    return stats;
  }, [graph.subproblems]);

  // MiniMap node color function
  const minimapNodeColor = useCallback((node: Node) => {
    const paradigm = node.data.paradigm as ParadigmType;
    const colorClass = PARADIGM_COLORS[paradigm];
    // Extract color from Tailwind class (simplified)
    const colorMap: Record<string, string> = {
      'bg-blue-500': '#3b82f6',
      'bg-green-500': '#22c55e',
      'bg-purple-500': '#a855f7',
      'bg-yellow-500': '#eab308',
      'bg-red-500': '#ef4444',
      'bg-indigo-500': '#6366f1',
      'bg-teal-500': '#14b8a6',
      'bg-orange-500': '#f97316',
    };
    const bgClass = colorClass.split(' ')[0];
    return colorMap[bgClass] || '#9ca3af';
  }, []);

  return (
    <div className={className} style={{ height }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Strict}
        fitView
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      >
        <Background />
        <Controls />
        <MiniMap
          nodeColor={minimapNodeColor}
          nodeStrokeWidth={3}
          zoomable
          pannable
        />

        {/* Info Panel */}
        <Panel position="top-left" className="bg-white rounded-lg shadow-lg p-4 m-2">
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">
              Graph Overview
            </h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div>
                <span className="font-medium">Subproblems:</span>{' '}
                {graph.subproblems.length}
              </div>
              <div>
                <span className="font-medium">Dependencies:</span>{' '}
                {graph.dependencies.length}
              </div>
              {graph.metadata?.paradigmsUsed && (
                <div>
                  <span className="font-medium">Paradigms:</span>{' '}
                  {graph.metadata.paradigmsUsed.length}
                </div>
              )}
            </div>
          </div>
        </Panel>

        {/* Legend Panel */}
        <Panel position="top-right" className="bg-white rounded-lg shadow-lg p-4 m-2">
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">Paradigms</h3>
            <div className="space-y-1">
              {Array.from(paradigmStats.entries()).map(([paradigm, count]) => (
                <div key={paradigm} className="flex items-center gap-2 text-xs">
                  <div
                    className={`w-4 h-4 rounded border-2 ${PARADIGM_COLORS[paradigm]}`}
                  />
                  <span className="text-gray-700 capitalize">
                    {paradigm}
                  </span>
                  <span className="text-gray-500">({count})</span>
                </div>
              ))}
            </div>
          </div>
        </Panel>

        {/* Status Legend */}
        <Panel position="bottom-right" className="bg-white rounded-lg shadow-lg p-4 m-2">
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">Status</h3>
            <div className="space-y-1 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-gray-400 bg-white" />
                <span className="text-gray-700">Pending</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-yellow-400 bg-white animate-pulse" />
                <span className="text-gray-700">In Progress</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded border-2 border-green-400 bg-white" />
                <span className="text-gray-700">Complete</span>
              </div>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
