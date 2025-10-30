import React from 'react';
import { render, screen } from '@testing-library/react';
import { DecompositionGraph } from '@/components/visualizations/DecompositionGraph';
import { SubproblemNode, SubproblemEdge } from '@/types/visualization';

// Mock React Flow
jest.mock('reactflow', () => ({
  __esModule: true,
  default: ({ children }: any) => <div data-testid="react-flow">{children}</div>,
  Controls: () => <div data-testid="controls" />,
  MiniMap: () => <div data-testid="minimap" />,
  Background: () => <div data-testid="background" />,
  useNodesState: (nodes: any) => [nodes, jest.fn(), jest.fn()],
  useEdgesState: (edges: any) => [edges, jest.fn(), jest.fn()],
  addEdge: jest.fn(),
  BackgroundVariant: { Dots: 'dots' },
}));

describe('DecompositionGraph', () => {
  const mockSubproblems: SubproblemNode[] = [
    {
      id: '1',
      title: 'Test Node 1',
      paradigm: 'structural',
      technique: 'Divide and Conquer',
      status: 'complete',
    },
    {
      id: '2',
      title: 'Test Node 2',
      paradigm: 'functional',
      technique: 'MapReduce',
      status: 'in_progress',
    },
  ];

  const mockDependencies: SubproblemEdge[] = [
    {
      id: 'e1-2',
      source: '1',
      target: '2',
    },
  ];

  it('renders without crashing', () => {
    render(
      <DecompositionGraph
        subproblems={mockSubproblems}
        dependencies={mockDependencies}
      />
    );
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
  });

  it('renders controls, minimap, and background', () => {
    render(
      <DecompositionGraph
        subproblems={mockSubproblems}
        dependencies={mockDependencies}
      />
    );
    expect(screen.getByTestId('controls')).toBeInTheDocument();
    expect(screen.getByTestId('minimap')).toBeInTheDocument();
    expect(screen.getByTestId('background')).toBeInTheDocument();
  });

  it('handles empty data gracefully', () => {
    render(<DecompositionGraph subproblems={[]} dependencies={[]} />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
  });
});
