'use client';

import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  MiniMap,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  BackgroundVariant,
  NodeTypes,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { SubproblemNode, SubproblemEdge, PARADIGM_COLORS, STATUS_COLORS } from '@/types/visualization';

interface DecompositionGraphProps {
  subproblems: SubproblemNode[];
  dependencies: SubproblemEdge[];
  onNodeClick?: (node: SubproblemNode) => void;
}

// Custom node component
const CustomNode = ({ data }: { data: SubproblemNode }) => {
  const paradigmColor = PARADIGM_COLORS[data.paradigm] || '#6b7280';
  const statusColor = STATUS_COLORS[data.status] || '#9ca3af';

  return (
    <div
      className="px-4 py-2 rounded-lg border-2 bg-white shadow-lg min-w-[200px]"
      style={{
        borderColor: paradigmColor,
        boxShadow: data.status === 'in_progress' ? `0 0 10px ${statusColor}` : undefined,
      }}
    >
      <div className="font-semibold text-sm mb-1" style={{ color: paradigmColor }}>
        {data.paradigm.toUpperCase()}
      </div>
      <div className="font-medium text-gray-900 mb-1">{data.title}</div>
      <div className="text-xs text-gray-600">{data.technique}</div>
      <div className="mt-2 flex items-center gap-2">
        <div
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: statusColor }}
        />
        <span className="text-xs capitalize text-gray-700">{data.status}</span>
      </div>
      {data.assignedAgent && (
        <div className="text-xs text-gray-500 mt-1">Agent: {data.assignedAgent}</div>
      )}
    </div>
  );
};

const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

export function DecompositionGraph({
  subproblems,
  dependencies,
  onNodeClick,
}: DecompositionGraphProps) {
  // Convert our data to React Flow format
  const initialNodes: Node[] = useMemo(
    () =>
      subproblems.map((sp, index) => ({
        id: sp.id,
        type: 'custom',
        position: sp.position || { x: (index % 3) * 300, y: Math.floor(index / 3) * 150 },
        data: sp,
      })),
    [subproblems]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      dependencies.map((dep) => ({
        id: dep.id,
        source: dep.source,
        target: dep.target,
        animated: dep.animated || false,
        label: dep.label,
        style: { stroke: PARADIGM_COLORS[dep.type || 'dependency'] || '#6b7280' },
      })),
    [dependencies]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.data as SubproblemNode);
      }
    },
    [onNodeClick]
  );

  return (
    <div className="w-full h-full bg-gray-50 rounded-lg border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const data = node.data as SubproblemNode;
            return PARADIGM_COLORS[data.paradigm] || '#6b7280';
          }}
        />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}
