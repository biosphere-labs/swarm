/**
 * Tests for layout utility functions
 */

import {
  calculateHierarchicalLayout,
  subproblemsToNodes,
  dependenciesToEdges,
  prepareGraphData,
  findConnectedComponents,
} from '@/lib/layoutUtils';
import { Subproblem, SubproblemDependency } from '@/types/decomposition';

describe('layoutUtils', () => {
  const mockSubproblems: Subproblem[] = [
    {
      id: 'sp-1',
      title: 'Node 1',
      paradigm: 'structural',
      status: 'complete',
    },
    {
      id: 'sp-2',
      title: 'Node 2',
      paradigm: 'functional',
      status: 'in_progress',
    },
    {
      id: 'sp-3',
      title: 'Node 3',
      paradigm: 'data',
      status: 'pending',
    },
  ];

  const mockDependencies: SubproblemDependency[] = [
    {
      id: 'dep-1',
      source: 'sp-1',
      target: 'sp-2',
      type: 'prerequisite',
    },
    {
      id: 'dep-2',
      source: 'sp-2',
      target: 'sp-3',
      type: 'prerequisite',
    },
  ];

  describe('calculateHierarchicalLayout', () => {
    it('calculates positions for simple linear graph', () => {
      const positions = calculateHierarchicalLayout(
        mockSubproblems,
        mockDependencies
      );

      expect(positions.size).toBe(3);
      expect(positions.has('sp-1')).toBe(true);
      expect(positions.has('sp-2')).toBe(true);
      expect(positions.has('sp-3')).toBe(true);
    });

    it('handles empty graph', () => {
      const positions = calculateHierarchicalLayout([], []);
      expect(positions.size).toBe(0);
    });

    it('handles graph with no dependencies', () => {
      const positions = calculateHierarchicalLayout(mockSubproblems, []);
      expect(positions.size).toBe(3);
      // All nodes should be at same level
      const yPositions = Array.from(positions.values()).map(p => p.y);
      expect(new Set(yPositions).size).toBe(1);
    });

    it('positions nodes in topological order (TB direction)', () => {
      const positions = calculateHierarchicalLayout(
        mockSubproblems,
        mockDependencies,
        { direction: 'TB' }
      );

      const pos1 = positions.get('sp-1')!;
      const pos2 = positions.get('sp-2')!;
      const pos3 = positions.get('sp-3')!;

      // sp-1 should be above sp-2, sp-2 above sp-3
      expect(pos1.y).toBeLessThan(pos2.y);
      expect(pos2.y).toBeLessThan(pos3.y);
    });

    it('positions nodes in topological order (LR direction)', () => {
      const positions = calculateHierarchicalLayout(
        mockSubproblems,
        mockDependencies,
        { direction: 'LR' }
      );

      const pos1 = positions.get('sp-1')!;
      const pos2 = positions.get('sp-2')!;
      const pos3 = positions.get('sp-3')!;

      // sp-1 should be left of sp-2, sp-2 left of sp-3
      expect(pos1.x).toBeLessThan(pos2.x);
      expect(pos2.x).toBeLessThan(pos3.x);
    });

    it('handles parallel nodes', () => {
      const parallelDeps: SubproblemDependency[] = [
        { id: 'dep-1', source: 'sp-1', target: 'sp-2' },
        { id: 'dep-2', source: 'sp-1', target: 'sp-3' },
      ];

      const positions = calculateHierarchicalLayout(
        mockSubproblems,
        parallelDeps
      );

      const pos2 = positions.get('sp-2')!;
      const pos3 = positions.get('sp-3')!;

      // sp-2 and sp-3 should be at same level (same y)
      expect(pos2.y).toBe(pos3.y);
    });

    it('respects custom node separation', () => {
      const positions1 = calculateHierarchicalLayout(
        mockSubproblems,
        mockDependencies,
        { nodeSep: 100 }
      );

      const positions2 = calculateHierarchicalLayout(
        mockSubproblems,
        mockDependencies,
        { nodeSep: 200 }
      );

      // For single node at top level, position should be same
      // But for parallel nodes at same level, separation should differ
      expect(positions1.size).toBe(3);
      expect(positions2.size).toBe(3);
    });

    it('handles cyclic dependencies gracefully', () => {
      const cyclicDeps: SubproblemDependency[] = [
        { id: 'dep-1', source: 'sp-1', target: 'sp-2' },
        { id: 'dep-2', source: 'sp-2', target: 'sp-3' },
        { id: 'dep-3', source: 'sp-3', target: 'sp-1' }, // Creates cycle
      ];

      const positions = calculateHierarchicalLayout(
        mockSubproblems,
        cyclicDeps
      );

      // Should still position all nodes
      expect(positions.size).toBe(3);
    });
  });

  describe('subproblemsToNodes', () => {
    it('converts subproblems to React Flow nodes', () => {
      const positions = new Map([
        ['sp-1', { x: 0, y: 0 }],
        ['sp-2', { x: 0, y: 100 }],
      ]);

      const nodes = subproblemsToNodes(mockSubproblems.slice(0, 2), positions);

      expect(nodes).toHaveLength(2);
      expect(nodes[0]).toMatchObject({
        id: 'sp-1',
        type: 'subproblem',
        position: { x: 0, y: 0 },
      });
      expect(nodes[0].data).toMatchObject(mockSubproblems[0]);
    });

    it('handles missing positions with default', () => {
      const positions = new Map([['sp-1', { x: 100, y: 200 }]]);

      const nodes = subproblemsToNodes(mockSubproblems, positions);

      expect(nodes).toHaveLength(3);
      expect(nodes[0].position).toEqual({ x: 100, y: 200 });
      expect(nodes[1].position).toEqual({ x: 0, y: 0 }); // Default position
    });
  });

  describe('dependenciesToEdges', () => {
    it('converts dependencies to React Flow edges', () => {
      const edges = dependenciesToEdges(mockDependencies);

      expect(edges).toHaveLength(2);
      expect(edges[0]).toMatchObject({
        id: 'dep-1',
        source: 'sp-1',
        target: 'sp-2',
        type: 'smoothstep',
        animated: true, // prerequisite type
      });
    });

    it('handles different dependency types', () => {
      const deps: SubproblemDependency[] = [
        { id: 'dep-1', source: 'sp-1', target: 'sp-2', type: 'prerequisite' },
        { id: 'dep-2', source: 'sp-2', target: 'sp-3', type: 'optional' },
        { id: 'dep-3', source: 'sp-1', target: 'sp-3', type: 'parallel' },
      ];

      const edges = dependenciesToEdges(deps);

      expect(edges[0].animated).toBe(true); // prerequisite
      expect(edges[1].animated).toBe(false); // optional
      expect(edges[1].style?.stroke).toBe('#9ca3af'); // optional color
    });

    it('handles empty dependencies', () => {
      const edges = dependenciesToEdges([]);
      expect(edges).toHaveLength(0);
    });
  });

  describe('prepareGraphData', () => {
    it('prepares complete graph data', () => {
      const result = prepareGraphData(mockSubproblems, mockDependencies);

      expect(result.nodes).toHaveLength(3);
      expect(result.edges).toHaveLength(2);
      expect(result.nodes[0].type).toBe('subproblem');
      expect(result.edges[0].type).toBe('smoothstep');
    });

    it('handles empty graph', () => {
      const result = prepareGraphData([], []);

      expect(result.nodes).toHaveLength(0);
      expect(result.edges).toHaveLength(0);
    });

    it('applies layout configuration', () => {
      const result1 = prepareGraphData(mockSubproblems, mockDependencies, {
        direction: 'TB',
      });
      const result2 = prepareGraphData(mockSubproblems, mockDependencies, {
        direction: 'LR',
      });

      // Should create nodes and edges
      expect(result1.nodes.length).toBe(3);
      expect(result2.nodes.length).toBe(3);
      expect(result1.edges.length).toBe(2);
      expect(result2.edges.length).toBe(2);
    });
  });

  describe('findConnectedComponents', () => {
    it('finds single connected component', () => {
      const components = findConnectedComponents(
        mockSubproblems,
        mockDependencies
      );

      expect(components).toHaveLength(1);
      expect(components[0]).toHaveLength(3);
    });

    it('finds multiple connected components', () => {
      const disconnectedSubproblems: Subproblem[] = [
        ...mockSubproblems,
        {
          id: 'sp-4',
          title: 'Isolated Node',
          paradigm: 'temporal',
          status: 'pending',
        },
      ];

      const components = findConnectedComponents(
        disconnectedSubproblems,
        mockDependencies
      );

      expect(components).toHaveLength(2);
      expect(components[0].length + components[1].length).toBe(4);
    });

    it('handles graph with no edges', () => {
      const components = findConnectedComponents(mockSubproblems, []);

      // Each node is its own component
      expect(components).toHaveLength(3);
      expect(components[0]).toHaveLength(1);
    });

    it('handles empty graph', () => {
      const components = findConnectedComponents([], []);
      expect(components).toHaveLength(0);
    });

    it('handles bidirectional dependencies correctly', () => {
      const bidirectionalDeps: SubproblemDependency[] = [
        { id: 'dep-1', source: 'sp-1', target: 'sp-2' },
        { id: 'dep-2', source: 'sp-2', target: 'sp-1' }, // Reverse direction
      ];

      const components = findConnectedComponents(
        mockSubproblems.slice(0, 2),
        bidirectionalDeps
      );

      // Should still be one component
      expect(components).toHaveLength(1);
      expect(components[0]).toHaveLength(2);
    });
  });
});
