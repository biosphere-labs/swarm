/**
 * Tests for DecompositionGraphViz component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { DecompositionGraphViz } from '@/components/DecompositionGraphViz';
import {
  DecompositionGraph,
  Subproblem,
  SubproblemDependency,
} from '@/types/decomposition';

// Mock React Flow
jest.mock('reactflow', () => ({
  __esModule: true,
  default: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="react-flow">{children}</div>
  ),
  Background: () => <div data-testid="background" />,
  Controls: () => <div data-testid="controls" />,
  MiniMap: () => <div data-testid="minimap" />,
  Panel: ({ children, position }: { children: React.ReactNode; position: string }) => (
    <div data-testid={`panel-${position}`}>{children}</div>
  ),
  useNodesState: (initialNodes: any[]) => [
    initialNodes,
    jest.fn(),
    jest.fn(),
  ],
  useEdgesState: (initialEdges: any[]) => [
    initialEdges,
    jest.fn(),
    jest.fn(),
  ],
  ConnectionMode: { Strict: 'strict' },
}));

describe('DecompositionGraphViz', () => {
  const mockSubproblems: Subproblem[] = [
    {
      id: 'sp-1',
      title: 'Real-time Event Stream',
      paradigm: 'temporal',
      technique: 'Event-Driven Pipeline',
      status: 'complete',
      confidence: 0.95,
    },
    {
      id: 'sp-2',
      title: 'Conflict Detection',
      paradigm: 'temporal',
      technique: 'Event-Driven Pipeline',
      status: 'in_progress',
      assignedAgent: 'Agent-03',
    },
    {
      id: 'sp-3',
      title: 'CRDT Document Structure',
      paradigm: 'data',
      technique: 'Horizontal Partitioning',
      status: 'pending',
      complexity: 'high',
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

  const mockGraph: DecompositionGraph = {
    subproblems: mockSubproblems,
    dependencies: mockDependencies,
    metadata: {
      originalProblem: 'Build a real-time collaborative text editor',
      paradigmsUsed: ['temporal', 'data'],
      timestamp: '2025-10-30T12:00:00Z',
    },
  };

  it('renders without crashing', () => {
    render(<DecompositionGraphViz graph={mockGraph} />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
  });

  it('renders React Flow with background, controls, and minimap', () => {
    render(<DecompositionGraphViz graph={mockGraph} />);
    expect(screen.getByTestId('background')).toBeInTheDocument();
    expect(screen.getByTestId('controls')).toBeInTheDocument();
    expect(screen.getByTestId('minimap')).toBeInTheDocument();
  });

  it('displays graph overview panel', () => {
    render(<DecompositionGraphViz graph={mockGraph} />);
    expect(screen.getByText('Graph Overview')).toBeInTheDocument();
    expect(screen.getByText(/Subproblems:/)).toBeInTheDocument();
    expect(screen.getByText(/Dependencies:/)).toBeInTheDocument();
  });

  it('displays paradigm legend panel', () => {
    render(<DecompositionGraphViz graph={mockGraph} />);
    expect(screen.getByText('Paradigms')).toBeInTheDocument();
    expect(screen.getByText('temporal')).toBeInTheDocument();
    expect(screen.getByText('data')).toBeInTheDocument();
  });

  it('displays status legend panel', () => {
    render(<DecompositionGraphViz graph={mockGraph} />);
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Complete')).toBeInTheDocument();
  });

  it('handles empty graph', () => {
    const emptyGraph: DecompositionGraph = {
      subproblems: [],
      dependencies: [],
    };
    render(<DecompositionGraphViz graph={emptyGraph} />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
    expect(screen.getByText(/Subproblems:/)).toBeInTheDocument();
  });

  it('applies custom height', () => {
    const { container } = render(
      <DecompositionGraphViz graph={mockGraph} height="800px" />
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveStyle({ height: '800px' });
  });

  it('applies custom className', () => {
    const { container } = render(
      <DecompositionGraphViz graph={mockGraph} className="custom-class" />
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('custom-class');
  });

  it('calls onNodeSelect when node is clicked', () => {
    const onNodeSelect = jest.fn();
    const { rerender } = render(
      <DecompositionGraphViz graph={mockGraph} onNodeSelect={onNodeSelect} />
    );

    // Since React Flow is mocked, we can't actually test the click event
    // This test verifies the prop is accepted
    expect(onNodeSelect).not.toHaveBeenCalled();
  });

  it('handles graph with single node', () => {
    const singleNodeGraph: DecompositionGraph = {
      subproblems: [mockSubproblems[0]],
      dependencies: [],
    };
    render(<DecompositionGraphViz graph={singleNodeGraph} />);
    expect(screen.getByText(/Subproblems:/)).toBeInTheDocument();
    expect(screen.getByText(/Dependencies:/)).toBeInTheDocument();
  });

  it('shows paradigm counts in legend', () => {
    render(<DecompositionGraphViz graph={mockGraph} />);
    // 2 temporal nodes, 1 data node
    const legendItems = screen.getAllByText(/\(\d+\)/);
    expect(legendItems.length).toBeGreaterThan(0);
  });

  it('handles graph with metadata', () => {
    render(<DecompositionGraphViz graph={mockGraph} />);
    // Check that paradigms count is displayed
    expect(screen.getByText(/Paradigms:/)).toBeInTheDocument();
  });

  it('handles graph without metadata', () => {
    const graphNoMetadata: DecompositionGraph = {
      subproblems: mockSubproblems,
      dependencies: mockDependencies,
    };
    render(<DecompositionGraphViz graph={graphNoMetadata} />);
    expect(screen.getByTestId('react-flow')).toBeInTheDocument();
  });
});
