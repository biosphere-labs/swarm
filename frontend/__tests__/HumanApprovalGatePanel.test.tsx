import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import HumanApprovalGatePanel from '@/components/HumanApprovalGatePanel';
import {
  GateReviewData,
  ApprovalRecord,
  CheckpointInfo,
  GateResponse,
} from '@/types/approval';

// Mock data
const mockGateData: GateReviewData = {
  gate: 'paradigm_selection',
  stage: 'Level 1',
  state_snapshot: {
    selected_paradigms: ['structural', 'functional'],
    paradigm_scores: {
      structural: 0.85,
      functional: 0.78,
    },
    paradigm_reasoning: {
      structural: 'Good for hierarchical decomposition',
      functional: 'Supports modular design',
    },
  },
  options: ['approve', 'reject', 'modify', 'backtrack'],
  context: {
    description: 'Review paradigm selection',
    level: 1,
    required: false,
    stage_description: 'Review selected decomposition paradigms.',
  },
};

const mockApprovalHistory: ApprovalRecord[] = [
  {
    gate_name: 'problem_ingestion',
    timestamp: Date.now() / 1000 - 3600,
    action: 'approve',
    reviewer: 'Alice',
    notes: 'Problem is well-defined',
  },
];

const mockCheckpoints: CheckpointInfo[] = [
  {
    checkpoint_id: 'cp1',
    stage: 'problem_ingestion',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    checkpoint_id: 'cp2',
    stage: 'paradigm_analysis',
    timestamp: new Date(Date.now() - 1800000).toISOString(),
  },
];

describe('HumanApprovalGatePanel', () => {
  const defaultProps = {
    runId: 'test-run-123',
    gateData: mockGateData,
    approvalHistory: mockApprovalHistory,
    checkpoints: mockCheckpoints,
    onApprove: jest.fn(),
    onReject: jest.fn(),
    onModify: jest.fn(),
    onBacktrack: jest.fn(),
    onAddContext: jest.fn(),
    onRequestAlternatives: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the component with gate information', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      expect(screen.getByText(/Approval Gate: paradigm_selection/i)).toBeInTheDocument();
      expect(screen.getByText(/Paradigm Selection/i)).toBeInTheDocument();
      expect(screen.getByText(/Level 1/i)).toBeInTheDocument();
    });

    it('should render reviewer name input', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      expect(screen.getByLabelText(/Your Name \(Reviewer\)/i)).toBeInTheDocument();
    });

    it('should render all action buttons', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      expect(screen.getByRole('button', { name: /^Approve$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^Reject$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^Modify$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^Backtrack$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^Add Context$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^Request Alternatives$/i })).toBeInTheDocument();
    });

    it('should disable action buttons when reviewer name is empty', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      expect(approveButton).toBeDisabled();
    });

    it('should enable action buttons when reviewer name is provided', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      expect(approveButton).not.toBeDisabled();
    });

    it('should display error when provided', () => {
      render(<HumanApprovalGatePanel {...defaultProps} error="Test error message" />);

      expect(screen.getByText(/Error: Test error message/i)).toBeInTheDocument();
    });

    it('should render approval history', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      expect(screen.getByText(/Approval History/i)).toBeInTheDocument();
      expect(screen.getByText(/problem_ingestion/i)).toBeInTheDocument();
      expect(screen.getByText(/Alice/i)).toBeInTheDocument();
    });

    it('should show required badge for required gates', () => {
      const requiredGateData = {
        ...mockGateData,
        context: { ...mockGateData.context, required: true },
      };

      render(<HumanApprovalGatePanel {...defaultProps} gateData={requiredGateData} />);

      expect(screen.getByText(/Required/i)).toBeInTheDocument();
    });
  });

  describe('State Snapshot Rendering', () => {
    it('should render Level 1 paradigm selection snapshot', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      expect(screen.getByText(/Selected Paradigms/i)).toBeInTheDocument();
      expect(screen.getByText(/structural/i)).toBeInTheDocument();
      expect(screen.getByText(/functional/i)).toBeInTheDocument();
      expect(screen.getByText(/85%/i)).toBeInTheDocument();
    });

    it('should render Level 2 technique selection snapshot', () => {
      const level2GateData: GateReviewData = {
        ...mockGateData,
        gate: 'technique_selection',
        context: { ...mockGateData.context, level: 2 },
        state_snapshot: {
          selected_techniques: {
            structural: 'Divide and Conquer',
            functional: 'Dynamic Programming',
          },
          technique_scores: {
            'Divide and Conquer': 0.92,
            'Dynamic Programming': 0.88,
          },
        },
      };

      render(<HumanApprovalGatePanel {...defaultProps} gateData={level2GateData} />);

      expect(screen.getByText(/Selected Techniques/i)).toBeInTheDocument();
      expect(screen.getByText(/Divide and Conquer/i)).toBeInTheDocument();
      expect(screen.getByText(/Dynamic Programming/i)).toBeInTheDocument();
    });

    it('should render Level 3 decomposition review snapshot', () => {
      const level3GateData: GateReviewData = {
        ...mockGateData,
        gate: 'decomposition_review',
        context: { ...mockGateData.context, level: 3 },
        state_snapshot: {
          integrated_subproblems: [
            { title: 'Subproblem 1', description: 'First subproblem' },
            { title: 'Subproblem 2', description: 'Second subproblem' },
          ],
        },
      };

      render(<HumanApprovalGatePanel {...defaultProps} gateData={level3GateData} />);

      expect(screen.getByText(/Integrated Subproblems/i)).toBeInTheDocument();
      expect(screen.getByText(/Subproblem 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Subproblem 2/i)).toBeInTheDocument();
    });

    it('should render Level 4 final solution snapshot', () => {
      const level4GateData: GateReviewData = {
        ...mockGateData,
        gate: 'final_solution',
        context: { ...mockGateData.context, level: 4 },
        state_snapshot: {
          integrated_solution: {
            content: 'Final solution content',
            confidence: 0.95,
          },
        },
      };

      render(<HumanApprovalGatePanel {...defaultProps} gateData={level4GateData} />);

      expect(screen.getByText(/Integrated Solution/i)).toBeInTheDocument();
      expect(screen.getByText(/Final solution content/i)).toBeInTheDocument();
      expect(screen.getByText(/95%/i)).toBeInTheDocument();
    });
  });

  describe('Approve Action', () => {
    it('should open approve dialog when approve button is clicked', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      fireEvent.click(approveButton);

      expect(screen.getByText(/Approve Decision/i)).toBeInTheDocument();
    });

    it('should call onApprove with correct data', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      fireEvent.click(approveButton);

      // In the dialog, click approve
      const dialogApproveButton = screen.getAllByRole('button', { name: /^Approve$/i })[1];
      fireEvent.click(dialogApproveButton);

      await waitFor(() => {
        expect(defaultProps.onApprove).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'approve',
            reviewer: 'John Doe',
          })
        );
      });
    });

    it('should include optional notes in approve request', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      fireEvent.click(approveButton);

      const notesInput = screen.getByLabelText(/Notes \(Optional\)/i);
      fireEvent.change(notesInput, { target: { value: 'Looks good to me' } });

      const dialogApproveButton = screen.getAllByRole('button', { name: /^Approve$/i })[1];
      fireEvent.click(dialogApproveButton);

      await waitFor(() => {
        expect(defaultProps.onApprove).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'approve',
            reviewer: 'John Doe',
            notes: 'Looks good to me',
          })
        );
      });
    });
  });

  describe('Reject Action', () => {
    it('should open reject dialog when reject button is clicked', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const rejectButton = screen.getByRole('button', { name: /^Reject$/i });
      fireEvent.click(rejectButton);

      expect(screen.getByText(/Reject Decision/i)).toBeInTheDocument();
    });

    it('should require reason for rejection', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const rejectButton = screen.getByRole('button', { name: /^Reject$/i });
      fireEvent.click(rejectButton);

      const dialogRejectButton = screen.getByRole('button', { name: /^Reject$/i });
      expect(dialogRejectButton).toBeDisabled();

      alertSpy.mockRestore();
    });

    it('should call onReject with reason', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const rejectButton = screen.getByRole('button', { name: /^Reject$/i });
      fireEvent.click(rejectButton);

      const reasonInput = screen.getByLabelText(/Reason for Rejection/i);
      fireEvent.change(reasonInput, { target: { value: 'Incorrect paradigm selection' } });

      const dialogRejectButton = screen.getByRole('button', { name: /^Reject$/i });
      fireEvent.click(dialogRejectButton);

      await waitFor(() => {
        expect(defaultProps.onReject).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'reject',
            reviewer: 'John Doe',
            notes: 'Incorrect paradigm selection',
          })
        );
      });
    });

    it('should allow selecting checkpoint for backtracking', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const rejectButton = screen.getByRole('button', { name: /^Reject$/i });
      fireEvent.click(rejectButton);

      const reasonInput = screen.getByLabelText(/Reason for Rejection/i);
      fireEvent.change(reasonInput, { target: { value: 'Need to restart' } });

      const checkpointSelect = screen.getByLabelText(/Backtrack to Checkpoint/i);
      fireEvent.change(checkpointSelect, { target: { value: 'cp1' } });

      const dialogRejectButton = screen.getByRole('button', { name: /^Reject$/i });
      fireEvent.click(dialogRejectButton);

      await waitFor(() => {
        expect(defaultProps.onReject).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'reject',
            reviewer: 'John Doe',
            notes: 'Need to restart',
            backtrack_to: 'cp1',
          })
        );
      });
    });
  });

  describe('Modify Action', () => {
    it('should open modify dialog when modify button is clicked', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const modifyButton = screen.getByRole('button', { name: /^Modify$/i });
      fireEvent.click(modifyButton);

      expect(screen.getByText(/Modify State/i)).toBeInTheDocument();
    });

    it('should require valid JSON for modifications', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const modifyButton = screen.getByRole('button', { name: /^Modify$/i });
      fireEvent.click(modifyButton);

      const modificationsInput = screen.getByLabelText(/Modifications \(JSON\)/i);
      fireEvent.change(modificationsInput, { target: { value: 'invalid json' } });

      const applyButton = screen.getByRole('button', { name: /Apply Modifications/i });
      fireEvent.click(applyButton);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Invalid JSON format for modifications');
      });

      alertSpy.mockRestore();
    });

    it('should call onModify with parsed JSON', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const modifyButton = screen.getByRole('button', { name: /^Modify$/i });
      fireEvent.click(modifyButton);

      const modificationsInput = screen.getByLabelText(/Modifications \(JSON\)/i);
      fireEvent.change(modificationsInput, {
        target: { value: '{"selected_paradigms": ["structural", "temporal"]}' },
      });

      const applyButton = screen.getByRole('button', { name: /Apply Modifications/i });
      fireEvent.click(applyButton);

      await waitFor(() => {
        expect(defaultProps.onModify).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'modify',
            reviewer: 'John Doe',
            modifications: { selected_paradigms: ['structural', 'temporal'] },
          })
        );
      });
    });
  });

  describe('Backtrack Action', () => {
    it('should open backtrack dialog when backtrack button is clicked', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const backtrackButton = screen.getByRole('button', { name: /^Backtrack$/i });
      fireEvent.click(backtrackButton);

      expect(screen.getByText(/Backtrack to Checkpoint/i)).toBeInTheDocument();
    });

    it('should require checkpoint selection', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const backtrackButton = screen.getByRole('button', { name: /^Backtrack$/i });
      fireEvent.click(backtrackButton);

      const dialogBacktrackButton = screen.getAllByRole('button', { name: /^Backtrack$/i })[1];
      fireEvent.click(dialogBacktrackButton);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Please select a checkpoint to backtrack to');
      });

      alertSpy.mockRestore();
    });

    it('should call onBacktrack with selected checkpoint', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const backtrackButton = screen.getByRole('button', { name: /^Backtrack$/i });
      fireEvent.click(backtrackButton);

      const checkpointSelect = screen.getByLabelText(/Select Checkpoint/i);
      fireEvent.change(checkpointSelect, { target: { value: 'cp2' } });

      const dialogBacktrackButton = screen.getAllByRole('button', { name: /^Backtrack$/i })[1];
      fireEvent.click(dialogBacktrackButton);

      await waitFor(() => {
        expect(defaultProps.onBacktrack).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'backtrack',
            reviewer: 'John Doe',
            backtrack_to: 'cp2',
          })
        );
      });
    });
  });

  describe('Add Context Action', () => {
    it('should open add context dialog when button is clicked', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const addContextButton = screen.getByRole('button', { name: /^Add Context$/i });
      fireEvent.click(addContextButton);

      expect(screen.getByText(/Add Context/i)).toBeInTheDocument();
    });

    it('should require context input', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const addContextButton = screen.getByRole('button', { name: /^Add Context$/i });
      fireEvent.click(addContextButton);

      const dialogAddContextButton = screen.getAllByRole('button', { name: /^Add Context$/i })[1];
      fireEvent.click(dialogAddContextButton);

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Please provide additional context');
      });

      alertSpy.mockRestore();
    });

    it('should call onAddContext with additional context', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const addContextButton = screen.getByRole('button', { name: /^Add Context$/i });
      fireEvent.click(addContextButton);

      const contextInput = screen.getByLabelText(/Additional Context/i);
      fireEvent.change(contextInput, {
        target: { value: 'Consider performance constraints' },
      });

      const dialogAddContextButton = screen.getAllByRole('button', { name: /^Add Context$/i })[1];
      fireEvent.click(dialogAddContextButton);

      await waitFor(() => {
        expect(defaultProps.onAddContext).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'add_context',
            reviewer: 'John Doe',
            additional_context: 'Consider performance constraints',
          })
        );
      });
    });
  });

  describe('Request Alternatives Action', () => {
    it('should open request alternatives dialog when button is clicked', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const requestAltButton = screen.getByRole('button', { name: /^Request Alternatives$/i });
      fireEvent.click(requestAltButton);

      expect(screen.getByText(/Request Alternatives/i)).toBeInTheDocument();
    });

    it('should call onRequestAlternatives with optional requirements', async () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const requestAltButton = screen.getByRole('button', { name: /^Request Alternatives$/i });
      fireEvent.click(requestAltButton);

      const requirementsInput = screen.getByLabelText(/Requirements \(Optional\)/i);
      fireEvent.change(requirementsInput, {
        target: { value: 'Focus on memory-efficient approaches' },
      });

      const dialogRequestButton = screen.getAllByRole('button', {
        name: /^Request Alternatives$/i,
      })[1];
      fireEvent.click(dialogRequestButton);

      await waitFor(() => {
        expect(defaultProps.onRequestAlternatives).toHaveBeenCalledWith(
          expect.objectContaining({
            action: 'request_alternatives',
            reviewer: 'John Doe',
            additional_context: 'Focus on memory-efficient approaches',
          })
        );
      });
    });
  });

  describe('Dialog Management', () => {
    it('should close dialog on cancel button click', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      fireEvent.click(approveButton);

      expect(screen.getByText(/Approve Decision/i)).toBeInTheDocument();

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      fireEvent.click(cancelButton);

      expect(screen.queryByText(/Approve Decision/i)).not.toBeInTheDocument();
    });

    it('should reset form fields when dialog closes', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const addContextButton = screen.getByRole('button', { name: /^Add Context$/i });
      fireEvent.click(addContextButton);

      const contextInput = screen.getByLabelText(/Additional Context/i);
      fireEvent.change(contextInput, { target: { value: 'Test context' } });

      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      fireEvent.click(cancelButton);

      // Reopen dialog
      fireEvent.click(addContextButton);

      const reopenedContextInput = screen.getByLabelText(/Additional Context/i);
      expect(reopenedContextInput).toHaveValue('');
    });
  });

  describe('Loading States', () => {
    it('should disable buttons when isLoading is true', () => {
      render(<HumanApprovalGatePanel {...defaultProps} isLoading={true} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      expect(approveButton).toBeDisabled();
    });

    it('should disable inputs when isLoading is true', () => {
      render(<HumanApprovalGatePanel {...defaultProps} isLoading={true} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      expect(reviewerInput).toBeDisabled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty approval history', () => {
      render(<HumanApprovalGatePanel {...defaultProps} approvalHistory={[]} />);

      expect(screen.queryByText(/Approval History/i)).not.toBeInTheDocument();
    });

    it('should handle empty checkpoints', () => {
      render(<HumanApprovalGatePanel {...defaultProps} checkpoints={[]} />);

      const reviewerInput = screen.getByLabelText(/Your Name \(Reviewer\)/i);
      fireEvent.change(reviewerInput, { target: { value: 'John Doe' } });

      const backtrackButton = screen.getByRole('button', { name: /^Backtrack$/i });
      fireEvent.click(backtrackButton);

      expect(screen.getByText(/No checkpoints available/i)).toBeInTheDocument();
    });

    it('should handle empty state snapshot', () => {
      const emptyGateData = {
        ...mockGateData,
        state_snapshot: {},
      };

      render(<HumanApprovalGatePanel {...defaultProps} gateData={emptyGateData} />);

      expect(screen.getByText(/No snapshot data available/i)).toBeInTheDocument();
    });

    it('should prevent submission without reviewer name', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

      render(<HumanApprovalGatePanel {...defaultProps} />);

      // Try to open approve dialog without setting reviewer
      const approveButton = screen.getByRole('button', { name: /^Approve$/i });
      expect(approveButton).toBeDisabled();

      alertSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('should have proper labels for all inputs', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      expect(screen.getByLabelText(/Your Name \(Reviewer\)/i)).toBeInTheDocument();
    });

    it('should have descriptive button text', () => {
      render(<HumanApprovalGatePanel {...defaultProps} />);

      expect(screen.getByRole('button', { name: /^Approve$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^Reject$/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /^Modify$/i })).toBeInTheDocument();
    });
  });
});
