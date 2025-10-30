/**
 * Layout utilities for hierarchical graph positioning
 */

import { Node, Edge } from 'reactflow';
import {
  Subproblem,
  SubproblemDependency,
  LayoutConfig,
  NodePosition,
} from '@/types/decomposition';

/**
 * Default layout configuration
 */
const DEFAULT_CONFIG: Required<LayoutConfig> = {
  direction: 'TB',
  nodeWidth: 200,
  nodeHeight: 100,
  rankSep: 150,
  nodeSep: 100,
};

/**
 * Build adjacency list from dependencies
 */
function buildAdjacencyList(
  dependencies: SubproblemDependency[]
): Map<string, string[]> {
  const adj = new Map<string, string[]>();

  dependencies.forEach(dep => {
    if (!adj.has(dep.source)) {
      adj.set(dep.source, []);
    }
    adj.get(dep.source)!.push(dep.target);
  });

  return adj;
}

/**
 * Topological sort using Kahn's algorithm
 * Returns array of levels, where each level contains node ids that can be processed in parallel
 */
function topologicalLevels(
  nodeIds: string[],
  dependencies: SubproblemDependency[]
): string[][] {
  const adj = buildAdjacencyList(dependencies);
  const inDegree = new Map<string, number>();

  // Initialize in-degrees
  nodeIds.forEach(id => inDegree.set(id, 0));
  dependencies.forEach(dep => {
    inDegree.set(dep.target, (inDegree.get(dep.target) || 0) + 1);
  });

  const levels: string[][] = [];
  let currentLevel = nodeIds.filter(id => inDegree.get(id) === 0);

  while (currentLevel.length > 0) {
    levels.push([...currentLevel]);
    const nextLevel: string[] = [];

    currentLevel.forEach(nodeId => {
      const neighbors = adj.get(nodeId) || [];
      neighbors.forEach(neighbor => {
        const newDegree = (inDegree.get(neighbor) || 0) - 1;
        inDegree.set(neighbor, newDegree);
        if (newDegree === 0) {
          nextLevel.push(neighbor);
        }
      });
    });

    currentLevel = nextLevel;
  }

  // Handle remaining nodes (in case of cycles)
  const processedIds = new Set(levels.flat());
  const remainingIds = nodeIds.filter(id => !processedIds.has(id));
  if (remainingIds.length > 0) {
    levels.push(remainingIds);
  }

  return levels;
}

/**
 * Calculate node positions using hierarchical layout
 */
export function calculateHierarchicalLayout(
  subproblems: Subproblem[],
  dependencies: SubproblemDependency[],
  config: LayoutConfig = {}
): Map<string, NodePosition> {
  const cfg = { ...DEFAULT_CONFIG, ...config };
  const positions = new Map<string, NodePosition>();

  if (subproblems.length === 0) {
    return positions;
  }

  // Get topological levels
  const nodeIds = subproblems.map(sp => sp.id);
  const levels = topologicalLevels(nodeIds, dependencies);

  // Calculate positions based on direction
  const isVertical = cfg.direction === 'TB' || cfg.direction === 'BT';
  const isReversed = cfg.direction === 'BT' || cfg.direction === 'RL';

  levels.forEach((level, levelIndex) => {
    const actualLevelIndex = isReversed ? levels.length - 1 - levelIndex : levelIndex;
    const levelSize = level.length;

    level.forEach((nodeId, nodeIndex) => {
      const centerOffset = (levelSize - 1) * cfg.nodeSep / 2;

      if (isVertical) {
        positions.set(nodeId, {
          x: nodeIndex * cfg.nodeSep - centerOffset,
          y: actualLevelIndex * cfg.rankSep,
        });
      } else {
        positions.set(nodeId, {
          x: actualLevelIndex * cfg.rankSep,
          y: nodeIndex * cfg.nodeSep - centerOffset,
        });
      }
    });
  });

  return positions;
}

/**
 * Convert subproblems to React Flow nodes
 */
export function subproblemsToNodes(
  subproblems: Subproblem[],
  positions: Map<string, NodePosition>
): Node[] {
  return subproblems.map(subproblem => {
    const position = positions.get(subproblem.id) || { x: 0, y: 0 };

    return {
      id: subproblem.id,
      type: 'subproblem',
      position,
      data: {
        ...subproblem,
      },
    };
  });
}

/**
 * Convert dependencies to React Flow edges
 */
export function dependenciesToEdges(
  dependencies: SubproblemDependency[]
): Edge[] {
  return dependencies.map(dep => ({
    id: dep.id,
    source: dep.source,
    target: dep.target,
    type: 'smoothstep',
    animated: dep.type === 'prerequisite',
    style: {
      stroke: dep.type === 'optional' ? '#9ca3af' : '#6366f1',
      strokeWidth: 2,
    },
    label: dep.description,
  }));
}

/**
 * Prepare graph data for React Flow
 */
export function prepareGraphData(
  subproblems: Subproblem[],
  dependencies: SubproblemDependency[],
  layoutConfig?: LayoutConfig
): { nodes: Node[]; edges: Edge[] } {
  const positions = calculateHierarchicalLayout(
    subproblems,
    dependencies,
    layoutConfig
  );

  const nodes = subproblemsToNodes(subproblems, positions);
  const edges = dependenciesToEdges(dependencies);

  return { nodes, edges };
}

/**
 * Find connected components in graph
 * Useful for detecting isolated subgraphs
 */
export function findConnectedComponents(
  subproblems: Subproblem[],
  dependencies: SubproblemDependency[]
): string[][] {
  const adj = new Map<string, Set<string>>();

  // Build undirected adjacency list
  subproblems.forEach(sp => adj.set(sp.id, new Set()));
  dependencies.forEach(dep => {
    adj.get(dep.source)?.add(dep.target);
    adj.get(dep.target)?.add(dep.source);
  });

  const visited = new Set<string>();
  const components: string[][] = [];

  function dfs(nodeId: string, component: string[]) {
    visited.add(nodeId);
    component.push(nodeId);

    adj.get(nodeId)?.forEach(neighbor => {
      if (!visited.has(neighbor)) {
        dfs(neighbor, component);
      }
    });
  }

  subproblems.forEach(sp => {
    if (!visited.has(sp.id)) {
      const component: string[] = [];
      dfs(sp.id, component);
      components.push(component);
    }
  });

  return components;
}
