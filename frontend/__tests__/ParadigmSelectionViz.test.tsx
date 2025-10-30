import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ParadigmSelectionViz, ParadigmSelectionData } from '@/components/ParadigmSelectionViz';

describe('ParadigmSelectionViz', () => {
  const mockData: ParadigmSelectionData = {
    selectedParadigms: ['temporal', 'functional', 'data'],
    paradigmScores: {
      structural: 0.45,
      functional: 0.78,
      temporal: 0.85,
      spatial: 0.22,
      hierarchical: 0.38,
      computational: 0.45,
      data: 0.72,
      dependency: 0.38,
    },
    paradigmReasoning: {
      structural: 'Problem has some structural elements but not dominant',
      functional: 'Clear operation separation makes functional decomposition applicable',
      temporal: 'Real-time synchronization needs require temporal decomposition',
      spatial: 'Not spatially distributed',
      hierarchical: 'Flat structure, minimal hierarchy',
      computational: 'Not compute intensive',
      data: 'Document storage requirements favor data decomposition',
      dependency: 'Simple dependencies',
    },
  };

  describe('Rendering', () => {
    it('renders the component with title', () => {
      render(<ParadigmSelectionViz data={mockData} />);
      expect(screen.getByText('Selected Decomposition Paradigms')).toBeInTheDocument();
    });

    it('renders all 8 paradigms', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      expect(screen.getByRole('heading', { name: 'Structural' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Functional' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Temporal' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Spatial' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Hierarchical' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Computational' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Data' })).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'Dependency' })).toBeInTheDocument();
    });

    it('displays paradigm descriptions', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      expect(screen.getByText('Graph/component decomposition')).toBeInTheDocument();
      expect(screen.getByText('Operation/task decomposition')).toBeInTheDocument();
      expect(screen.getByText('Time/stage decomposition')).toBeInTheDocument();
    });
  });

  describe('Score Visualization', () => {
    it('displays scores as percentages', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      expect(screen.getByText('85%')).toBeInTheDocument(); // temporal
      expect(screen.getByText('78%')).toBeInTheDocument(); // functional
      expect(screen.getByText('72%')).toBeInTheDocument(); // data
    });

    it('renders progress bars for all paradigms', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const progressBars = screen.getAllByRole('progressbar');
      expect(progressBars).toHaveLength(8);
    });

    it('sets correct progress bar values', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const temporalBar = screen.getByLabelText(/Temporal score: 85%/i);
      expect(temporalBar).toHaveAttribute('aria-valuenow', '85');
      expect(temporalBar).toHaveAttribute('aria-valuemin', '0');
      expect(temporalBar).toHaveAttribute('aria-valuemax', '100');
    });

    it('applies correct width to progress bars', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const temporalBar = screen.getByLabelText(/Temporal score: 85%/i);
      expect(temporalBar).toHaveStyle({ width: '85%' });
    });
  });

  describe('Selection Status', () => {
    it('shows "Selected" badge for selected paradigms', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const selectedBadges = screen.getAllByText('Selected');
      expect(selectedBadges).toHaveLength(3); // temporal, functional, data
    });

    it('does not show "Selected" badge for unselected paradigms', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      // Check that structural (0.45) does not have a selected badge nearby
      const structuralSection = screen.getByText('Structural').closest('div');
      const selectedBadgesInStructural = within(structuralSection!).queryAllByText('Selected');
      expect(selectedBadgesInStructural).toHaveLength(0);
    });

    it('displays summary of selected paradigms', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      expect(screen.getByText('3 of 8')).toBeInTheDocument();
    });

    it('shows selected paradigm names in summary', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      // Check that selected paradigms appear in summary badges at the bottom
      const summarySection = screen.getByText('Selected Paradigms:').closest('div')?.parentElement;

      // In the summary, each selected paradigm appears once as a badge
      const temporalBadges = within(summarySection!).getAllByText('Temporal');
      const functionalBadges = within(summarySection!).getAllByText('Functional');
      const dataBadges = within(summarySection!).getAllByText('Data');

      expect(temporalBadges.length).toBeGreaterThanOrEqual(1);
      expect(functionalBadges.length).toBeGreaterThanOrEqual(1);
      expect(dataBadges.length).toBeGreaterThanOrEqual(1);
    });
  });

  describe('Reasoning Display', () => {
    it('hides reasoning by default', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      expect(screen.queryByText('Real-time synchronization needs require temporal decomposition')).not.toBeInTheDocument();
    });

    it('shows reasoning when "Show Reasoning" button is clicked', async () => {
      const user = userEvent.setup();
      render(<ParadigmSelectionViz data={mockData} />);

      const showButtons = screen.getAllByText('Show Reasoning');
      await user.click(showButtons[0]); // Click first "Show Reasoning" button

      // Should show reasoning for one paradigm
      expect(screen.getByText(/Problem has some structural elements/i)).toBeInTheDocument();
    });

    it('hides reasoning when "Hide Reasoning" button is clicked', async () => {
      const user = userEvent.setup();
      render(<ParadigmSelectionViz data={mockData} />);

      const showButtons = screen.getAllByText('Show Reasoning');
      await user.click(showButtons[0]);

      const hideButton = screen.getByText('Hide Reasoning');
      await user.click(hideButton);

      expect(screen.queryByText(/Problem has some structural elements/i)).not.toBeInTheDocument();
    });

    it('toggles only one reasoning section at a time', async () => {
      const user = userEvent.setup();
      render(<ParadigmSelectionViz data={mockData} />);

      const showButtons = screen.getAllByText('Show Reasoning');

      // Click first button
      await user.click(showButtons[0]);
      expect(screen.getByText(/Problem has some structural elements/i)).toBeInTheDocument();

      // Click second button
      await user.click(showButtons[1]);
      expect(screen.queryByText(/Problem has some structural elements/i)).not.toBeInTheDocument();
      expect(screen.getByText(/Clear operation separation/i)).toBeInTheDocument();
    });

    it('sets correct aria-expanded attribute', async () => {
      const user = userEvent.setup();
      render(<ParadigmSelectionViz data={mockData} />);

      const showButtons = screen.getAllByText('Show Reasoning');
      const firstButton = showButtons[0];

      expect(firstButton).toHaveAttribute('aria-expanded', 'false');

      await user.click(firstButton);

      const hideButton = screen.getByText('Hide Reasoning');
      expect(hideButton).toHaveAttribute('aria-expanded', 'true');
    });
  });

  describe('Color Coding', () => {
    it('applies green color to high-scoring paradigms (>0.6)', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const temporalBar = screen.getByLabelText(/Temporal score: 85%/i);
      expect(temporalBar).toHaveClass('bg-green-500');
    });

    it('applies yellow color to medium-scoring paradigms (0.3-0.6)', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const structuralBar = screen.getByLabelText(/Structural score: 45%/i);
      expect(structuralBar).toHaveClass('bg-yellow-500');
    });

    it('applies gray color to low-scoring paradigms (<0.3)', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const spatialBar = screen.getByLabelText(/Spatial score: 22%/i);
      expect(spatialBar).toHaveClass('bg-gray-300');
    });

    it('applies green color to selected paradigms regardless of score', () => {
      const dataWithLowSelectedScore: ParadigmSelectionData = {
        selectedParadigms: ['structural'],
        paradigmScores: { structural: 0.35 },
        paradigmReasoning: { structural: 'Selected despite lower score' },
      };

      render(<ParadigmSelectionViz data={dataWithLowSelectedScore} />);

      const structuralBar = screen.getByLabelText(/Structural score: 35%/i);
      expect(structuralBar).toHaveClass('bg-green-500');
    });
  });

  describe('Edge Cases', () => {
    it('handles empty data gracefully', () => {
      const emptyData: ParadigmSelectionData = {
        selectedParadigms: [],
        paradigmScores: {},
        paradigmReasoning: {},
      };

      render(<ParadigmSelectionViz data={emptyData} />);

      expect(screen.getByText('0 of 8')).toBeInTheDocument();
      expect(screen.getAllByText('0%')).toHaveLength(8);
    });

    it('handles missing paradigm data', () => {
      const partialData: ParadigmSelectionData = {
        selectedParadigms: ['temporal'],
        paradigmScores: { temporal: 0.85 },
        paradigmReasoning: { temporal: 'Only temporal provided' },
      };

      render(<ParadigmSelectionViz data={partialData} />);

      // Should still render all 8 paradigms
      expect(screen.getByText('Structural')).toBeInTheDocument();
      expect(screen.getByText('Functional')).toBeInTheDocument();
    });

    it('handles score of 0', () => {
      const zeroScoreData: ParadigmSelectionData = {
        selectedParadigms: [],
        paradigmScores: { structural: 0 },
        paradigmReasoning: { structural: 'Not applicable' },
      };

      render(<ParadigmSelectionViz data={zeroScoreData} />);

      const structuralBar = screen.getByLabelText(/Structural score: 0%/i);
      expect(structuralBar).toHaveStyle({ width: '0%' });
    });

    it('handles score of 1 (100%)', () => {
      const maxScoreData: ParadigmSelectionData = {
        selectedParadigms: ['temporal'],
        paradigmScores: { temporal: 1.0 },
        paradigmReasoning: { temporal: 'Perfect fit' },
      };

      render(<ParadigmSelectionViz data={maxScoreData} />);

      expect(screen.getByText('100%')).toBeInTheDocument();
      const temporalBar = screen.getByLabelText(/Temporal score: 100%/i);
      expect(temporalBar).toHaveStyle({ width: '100%' });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels for progress bars', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      expect(screen.getByLabelText(/Temporal score: 85%/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Functional score: 78%/i)).toBeInTheDocument();
    });

    it('reasoning buttons have proper aria-expanded attributes', () => {
      render(<ParadigmSelectionViz data={mockData} />);

      const buttons = screen.getAllByText('Show Reasoning');
      buttons.forEach(button => {
        expect(button).toHaveAttribute('aria-expanded');
      });
    });

    it('reasoning sections have proper ids', async () => {
      const user = userEvent.setup();
      render(<ParadigmSelectionViz data={mockData} />);

      const showButtons = screen.getAllByText('Show Reasoning');
      await user.click(showButtons[0]);

      const reasoningSection = screen.getByText(/Problem has some structural elements/i).closest('div');
      expect(reasoningSection).toHaveAttribute('id', 'reasoning-structural');
    });

    it('reasoning buttons control corresponding sections', async () => {
      const user = userEvent.setup();
      render(<ParadigmSelectionViz data={mockData} />);

      const showButtons = screen.getAllByText('Show Reasoning');
      const firstButton = showButtons[0];

      await user.click(firstButton);

      const hideButton = screen.getByText('Hide Reasoning');
      expect(hideButton).toHaveAttribute('aria-controls', 'reasoning-structural');
    });
  });

  describe('Custom className', () => {
    it('applies custom className to root element', () => {
      const { container } = render(
        <ParadigmSelectionViz data={mockData} className="custom-class" />
      );

      const card = container.querySelector('.custom-class');
      expect(card).toBeInTheDocument();
    });
  });
});
