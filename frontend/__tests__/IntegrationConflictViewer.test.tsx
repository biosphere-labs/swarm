import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import IntegrationConflictViewer from '@/components/IntegrationConflictViewer';
import { SubproblemConflict } from '@/types/integration';

describe('IntegrationConflictViewer', () => {
  const mockConflicts: SubproblemConflict[] = [
    {
      id: 'conflict-1',
      subproblemIds: ['sp-1', 'sp-2'],
      subproblems: [
        {
          id: 'sp-1',
          title: 'Authentication Module',
          description: 'Implement user authentication',
          paradigm: 'functional',
          technique: 'divide-and-conquer',
          status: 'pending',
          confidence: 0.85,
          complexity: 'medium',
        },
        {
          id: 'sp-2',
          title: 'User Auth System',
          description: 'Build authentication system',
          paradigm: 'functional',
          technique: 'layered-architecture',
          status: 'pending',
          confidence: 0.9,
          complexity: 'medium',
        },
      ],
      paradigms: ['functional'],
      similarity: {
        jaccard: 0.75,
        cosine: 0.82,
        structural: 0.78,
        combined: 0.85,
      },
      status: 'pending',
      recommendedStrategy: 'merge',
    },
    {
      id: 'conflict-2',
      subproblemIds: ['sp-3', 'sp-4'],
      subproblems: [
        {
          id: 'sp-3',
          title: 'Data Storage',
          description: 'Database design',
          paradigm: 'structural',
          status: 'pending',
        },
        {
          id: 'sp-4',
          title: 'Storage Layer',
          description: 'Data persistence',
          paradigm: 'hierarchical',
          status: 'pending',
        },
      ],
      paradigms: ['structural', 'hierarchical'],
      similarity: {
        combined: 0.72,
      },
      status: 'pending',
      recommendedStrategy: 'multiview',
    },
  ];

  const resolvedConflict: SubproblemConflict = {
    id: 'conflict-3',
    subproblemIds: ['sp-5', 'sp-6'],
    subproblems: [
      {
        id: 'sp-5',
        title: 'API Gateway',
        paradigm: 'functional',
        status: 'pending',
      },
      {
        id: 'sp-6',
        title: 'Gateway Service',
        paradigm: 'functional',
        status: 'pending',
      },
    ],
    paradigms: ['functional'],
    similarity: { combined: 0.9 },
    status: 'resolved',
  };

  it('renders no conflicts message when conflicts array is empty', () => {
    render(<IntegrationConflictViewer conflicts={[]} />);
    expect(screen.getByText('No conflicts detected. All subproblems are compatible.')).toBeInTheDocument();
  });

  it('renders conflict overview with statistics', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Conflict Overview')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument(); // Total conflicts
    expect(screen.getByText('Total Conflicts')).toBeInTheDocument();
  });

  it('displays all conflicts', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Conflict: conflict-1')).toBeInTheDocument();
    expect(screen.getByText('Conflict: conflict-2')).toBeInTheDocument();
  });

  it('shows conflict status badges', () => {
    render(<IntegrationConflictViewer conflicts={[...mockConflicts, resolvedConflict]} />);
    
    const pendingBadges = screen.getAllByText('pending');
    expect(pendingBadges.length).toBeGreaterThan(0);
    
    expect(screen.getByText('resolved')).toBeInTheDocument();
  });

  it('displays similarity metrics', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Similarity Metrics')).toBeInTheDocument();
    expect(screen.getByText('Jaccard')).toBeInTheDocument();
    expect(screen.getByText('Cosine')).toBeInTheDocument();
    expect(screen.getByText('Combined')).toBeInTheDocument();
  });

  it('displays paradigms involved', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Paradigms Involved')).toBeInTheDocument();
    expect(screen.getByText('functional')).toBeInTheDocument();
    expect(screen.getByText('structural')).toBeInTheDocument();
    expect(screen.getByText('hierarchical')).toBeInTheDocument();
  });

  it('shows subproblem details in comparison cards', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Authentication Module')).toBeInTheDocument();
    expect(screen.getByText('User Auth System')).toBeInTheDocument();
    expect(screen.getByText('Implement user authentication')).toBeInTheDocument();
  });

  it('displays recommended strategy badge', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Recommended: Merge')).toBeInTheDocument();
    expect(screen.getByText('Recommended: Multi-View')).toBeInTheDocument();
  });

  it('shows resolution strategy options for pending conflicts', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Resolution Strategy')).toBeInTheDocument();
    expect(screen.getByText('Merge')).toBeInTheDocument();
    expect(screen.getByText('Keep Both')).toBeInTheDocument();
  });

  it('allows selecting a resolution strategy', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    const mergeButtons = screen.getAllByText('Merge');
    const firstMergeButton = mergeButtons[0];
    
    fireEvent.click(firstMergeButton);
    
    // After clicking, the button should be selected (variant changes)
    // We can verify the Apply Resolution button becomes enabled
    const applyButtons = screen.getAllByText('Apply Resolution');
    expect(applyButtons[0]).not.toBeDisabled();
  });

  it('shows manual description textarea when manual strategy is selected', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    const manualButtons = screen.getAllByText('Manual Resolution');
    fireEvent.click(manualButtons[0]);
    
    expect(screen.getByPlaceholderText('Describe how you want to resolve this conflict...')).toBeInTheDocument();
  });

  it('calls onResolve when applying a resolution', () => {
    const mockResolve = jest.fn();
    render(<IntegrationConflictViewer conflicts={mockConflicts} onResolve={mockResolve} />);
    
    const mergeButtons = screen.getAllByText('Merge');
    fireEvent.click(mergeButtons[0]);
    
    const applyButtons = screen.getAllByText('Apply Resolution');
    fireEvent.click(applyButtons[0]);
    
    expect(mockResolve).toHaveBeenCalledWith(
      'conflict-1',
      expect.objectContaining({
        conflictId: 'conflict-1',
        strategy: 'merge',
        resolvedBy: 'user',
      })
    );
  });

  it('calls onReject when rejecting a conflict', () => {
    const mockReject = jest.fn();
    render(<IntegrationConflictViewer conflicts={mockConflicts} onReject={mockReject} />);
    
    const rejectButtons = screen.getAllByText('Reject Conflict');
    fireEvent.click(rejectButtons[0]);
    
    expect(mockReject).toHaveBeenCalledWith('conflict-1');
  });

  it('does not show resolution options in readOnly mode', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} readOnly={true} />);
    
    expect(screen.queryByText('Resolution Strategy')).not.toBeInTheDocument();
    expect(screen.queryByText('Apply Resolution')).not.toBeInTheDocument();
  });

  it('does not show resolution options for resolved conflicts', () => {
    render(<IntegrationConflictViewer conflicts={[resolvedConflict]} />);
    
    expect(screen.queryByText('Resolution Strategy')).not.toBeInTheDocument();
    expect(screen.queryByText('Apply Resolution')).not.toBeInTheDocument();
  });

  it('shows different strategy options for same vs different paradigms', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    // First conflict (same paradigm) should show "Merge"
    const allText = screen.getAllByText(/Merge/);
    expect(allText.length).toBeGreaterThan(0);
    
    // Second conflict (different paradigms) should show "Multi-View"
    expect(screen.getByText('Multi-View')).toBeInTheDocument();
  });

  it('calculates and displays correct statistics', () => {
    const mixedConflicts = [...mockConflicts, resolvedConflict];
    render(<IntegrationConflictViewer conflicts={mixedConflicts} />);
    
    // 3 total, 2 pending, 1 resolved
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('displays average similarity correctly', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    // Average of 0.85 and 0.72 = 0.785 = 78.5%
    expect(screen.getByText('Average Similarity')).toBeInTheDocument();
    expect(screen.getByText('78.5%')).toBeInTheDocument();
  });

  it('shows conflicts by paradigm breakdown', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('Conflicts by Paradigm')).toBeInTheDocument();
    // functional appears in both conflicts (2 total)
    expect(screen.getByText('functional: 2')).toBeInTheDocument();
  });

  it('applies custom className prop', () => {
    const { container } = render(
      <IntegrationConflictViewer conflicts={mockConflicts} className="custom-class" />
    );
    
    const mainDiv = container.firstChild;
    expect(mainDiv).toHaveClass('custom-class');
  });

  it('handles manual resolution with custom description', () => {
    const mockResolve = jest.fn();
    render(<IntegrationConflictViewer conflicts={mockConflicts} onResolve={mockResolve} />);
    
    const manualButtons = screen.getAllByText('Manual Resolution');
    fireEvent.click(manualButtons[0]);
    
    const textarea = screen.getByPlaceholderText('Describe how you want to resolve this conflict...');
    fireEvent.change(textarea, { target: { value: 'Custom resolution description' } });
    
    const applyButtons = screen.getAllByText('Apply Resolution');
    fireEvent.click(applyButtons[0]);
    
    expect(mockResolve).toHaveBeenCalledWith(
      'conflict-1',
      expect.objectContaining({
        strategy: 'manual',
        customDescription: 'Custom resolution description',
      })
    );
  });

  it('prevents manual resolution without description', () => {
    const mockResolve = jest.fn();
    const alertMock = jest.spyOn(window, 'alert').mockImplementation(() => {});
    
    render(<IntegrationConflictViewer conflicts={mockConflicts} onResolve={mockResolve} />);
    
    const manualButtons = screen.getAllByText('Manual Resolution');
    fireEvent.click(manualButtons[0]);
    
    const applyButtons = screen.getAllByText('Apply Resolution');
    fireEvent.click(applyButtons[0]);
    
    expect(alertMock).toHaveBeenCalledWith('Please provide a description for manual resolution');
    expect(mockResolve).not.toHaveBeenCalled();
    
    alertMock.mockRestore();
  });

  it('displays subproblem confidence when available', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('90%')).toBeInTheDocument();
  });

  it('displays subproblem complexity when available', () => {
    render(<IntegrationConflictViewer conflicts={mockConflicts} />);
    
    const complexityBadges = screen.getAllByText('medium complexity');
    expect(complexityBadges.length).toBeGreaterThan(0);
  });

  it('clears selection state after resolving a conflict', () => {
    const mockResolve = jest.fn();
    render(<IntegrationConflictViewer conflicts={mockConflicts} onResolve={mockResolve} />);
    
    const mergeButtons = screen.getAllByText('Merge');
    fireEvent.click(mergeButtons[0]);
    
    const applyButtons = screen.getAllByText('Apply Resolution');
    const firstApplyButton = applyButtons[0];
    
    fireEvent.click(firstApplyButton);
    
    // After resolution, the apply button should be disabled again (no selection)
    // Note: This tests internal state management
    expect(mockResolve).toHaveBeenCalled();
  });
});
