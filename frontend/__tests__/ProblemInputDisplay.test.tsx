import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProblemInputDisplay from '@/components/ProblemInputDisplay';
import { extractCharacteristics } from '@/lib/extractCharacteristics';

// Mock the extractCharacteristics function
jest.mock('@/lib/extractCharacteristics');

const mockExtractCharacteristics = extractCharacteristics as jest.MockedFunction<
  typeof extractCharacteristics
>;

describe('ProblemInputDisplay', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockExtractCharacteristics.mockReturnValue({
      size: {
        estimated: 'medium',
        linesOfCode: 2000,
        confidence: 0.8,
      },
      complexity: {
        level: 'high',
        factors: ['algorithms', 'realTime'],
        confidence: 0.75,
      },
      structure: {
        types: ['graph', 'hierarchy'],
        confidence: 0.7,
      },
      resources: {
        compute: 'medium',
        memory: 'high',
        realTime: true,
        distributed: false,
        confidence: 0.6,
      },
      domains: {
        detected: ['api', 'data'],
        confidence: 0.65,
      },
      constraints: {
        timing: ['100ms'],
        dependencies: ['requires'],
        technical: ['performance: fast'],
        confidence: 0.5,
      },
    });
  });

  describe('Rendering', () => {
    it('should render the component with initial state', () => {
      render(<ProblemInputDisplay />);

      expect(screen.getByRole('heading', { name: /Problem Description/i })).toBeInTheDocument();
      expect(screen.getByLabelText('Problem description input')).toBeInTheDocument();
      expect(screen.getByText('Start Pipeline')).toBeInTheDocument();
    });

    it('should render with initial problem text', () => {
      const initialText = 'Test problem description';
      render(<ProblemInputDisplay initialProblem={initialText} />);

      const textarea = screen.getByLabelText('Problem description input');
      expect(textarea).toHaveValue(initialText);
    });

    it('should display help text when no problem is entered', () => {
      render(<ProblemInputDisplay />);

      expect(screen.getByText('Tips for better extraction:')).toBeInTheDocument();
    });
  });

  describe('Text Input', () => {
    it('should update character and word count as user types', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, { target: { value: 'Hello world test' } });

      expect(screen.getByText(/3 words/)).toBeInTheDocument();
      expect(screen.getByText(/16 characters/)).toBeInTheDocument();
    });

    it('should handle multiline text correctly', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      const multilineText = 'Line one\nLine two\nLine three';
      fireEvent.change(textarea, { target: { value: multilineText } });

      expect(textarea).toHaveValue(multilineText);
      expect(screen.getByText(/6 words/)).toBeInTheDocument();
    });

    it('should clear text when clear button is clicked', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, { target: { value: 'Test text' } });

      const clearButton = screen.getByText('Clear');
      fireEvent.click(clearButton);

      expect(textarea).toHaveValue('');
    });
  });

  describe('Characteristics Extraction', () => {
    it('should extract characteristics after user stops typing', async () => {
      jest.useFakeTimers();
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, {
        target: { value: 'Build a real-time collaborative text editor' },
      });

      // Fast-forward debounce timer
      await act(async () => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(mockExtractCharacteristics).toHaveBeenCalledWith(
          'Build a real-time collaborative text editor'
        );
      });

      jest.useRealTimers();
    });

    it('should not extract characteristics for very short text', async () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, { target: { value: 'Short' } });

      await waitFor(() => {
        expect(mockExtractCharacteristics).not.toHaveBeenCalled();
      });
    });

    it('should display extracted characteristics', async () => {
      jest.useFakeTimers();
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, {
        target: { value: 'Build a real-time collaborative text editor with complex algorithms' },
      });

      await act(async () => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(screen.getByRole('heading', { name: /Extracted Characteristics/i })).toBeInTheDocument();
        expect(screen.getAllByText('medium').length).toBeGreaterThan(0);
        expect(screen.getAllByText('high').length).toBeGreaterThan(0);
        expect(screen.getByText('80% confidence')).toBeInTheDocument();
      });

      jest.useRealTimers();
    });

    it('should display all characteristic sections', async () => {
      jest.useFakeTimers();
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, {
        target: { value: 'Build a complex real-time system with APIs and data processing' },
      });

      await act(async () => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        expect(screen.getByText('Size Estimate')).toBeInTheDocument();
        expect(screen.getByText('Complexity')).toBeInTheDocument();
        expect(screen.getByText('Detected Structure')).toBeInTheDocument();
        expect(screen.getByText('Resource Requirements')).toBeInTheDocument();
        expect(screen.getByText('Domain Hints')).toBeInTheDocument();
        expect(screen.getByText('Detected Constraints')).toBeInTheDocument();
      });

      jest.useRealTimers();
    });
  });

  describe('Submit Functionality', () => {
    it('should disable submit button when no text is entered', () => {
      render(<ProblemInputDisplay />);

      const submitButton = screen.getByText('Start Pipeline');
      expect(submitButton).toBeDisabled();
    });

    it('should enable submit button after characteristics are extracted', async () => {
      jest.useFakeTimers();
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, {
        target: { value: 'Build a real-time system' },
      });

      await act(async () => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        const submitButton = screen.getByText('Start Pipeline');
        expect(submitButton).not.toBeDisabled();
      });

      jest.useRealTimers();
    });

    it('should call onSubmit with problem text and characteristics', async () => {
      jest.useFakeTimers();
      const mockOnSubmit = jest.fn();
      render(<ProblemInputDisplay onSubmit={mockOnSubmit} />);

      const textarea = screen.getByLabelText('Problem description input');
      const problemText = 'Build a real-time collaborative text editor';
      fireEvent.change(textarea, { target: { value: problemText } });

      await act(async () => {
        jest.advanceTimersByTime(500);
      });

      await waitFor(() => {
        const submitButton = screen.getByText('Start Pipeline');
        expect(submitButton).not.toBeDisabled();
      });

      const submitButton = screen.getByText('Start Pipeline');
      fireEvent.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith(
        problemText,
        expect.objectContaining({
          size: expect.any(Object),
          complexity: expect.any(Object),
          structure: expect.any(Object),
          resources: expect.any(Object),
          domains: expect.any(Object),
          constraints: expect.any(Object),
        })
      );

      jest.useRealTimers();
    });

    it('should show analyzing state while processing', async () => {
      jest.useFakeTimers();
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, {
        target: { value: 'Build a real-time system' },
      });

      // Don't advance timer yet
      await waitFor(() => {
        expect(screen.getByText('Analyzing...')).toBeInTheDocument();
      });

      jest.useRealTimers();
    });
  });

  describe('Preview Functionality', () => {
    it('should show preview when button is clicked', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, { target: { value: 'Test preview content' } });

      const showPreviewButton = screen.getByText('Show Preview');
      fireEvent.click(showPreviewButton);

      expect(screen.getByText('Preview')).toBeInTheDocument();
      // Query for the preview text within the preview section
      expect(screen.getAllByText('Test preview content').length).toBeGreaterThan(0);
    });

    it('should hide preview when button is clicked again', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, { target: { value: 'Test preview content' } });

      const showPreviewButton = screen.getByText('Show Preview');
      fireEvent.click(showPreviewButton);

      expect(screen.getByText('Preview')).toBeInTheDocument();

      const hidePreviewButton = screen.getByText('Hide Preview');
      fireEvent.click(hidePreviewButton);

      // Check that preview heading is not visible
      expect(screen.queryByRole('heading', { name: 'Preview' })).not.toBeInTheDocument();
    });

    it('should disable preview button when no text is entered', () => {
      render(<ProblemInputDisplay />);

      const previewButton = screen.getByText('Show Preview');
      expect(previewButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper aria labels', () => {
      render(<ProblemInputDisplay />);

      expect(screen.getByLabelText('Problem description input')).toBeInTheDocument();
    });

    it('should have descriptive button text', () => {
      render(<ProblemInputDisplay />);

      expect(screen.getByText('Start Pipeline')).toBeInTheDocument();
      expect(screen.getByText('Clear')).toBeInTheDocument();
      expect(screen.getByText('Show Preview')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty string after clearing', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      fireEvent.change(textarea, { target: { value: 'Test' } });
      fireEvent.change(textarea, { target: { value: '' } });

      expect(screen.getByText(/0 words • 0 characters/)).toBeInTheDocument();
    });

    it('should handle special characters in text', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      const specialText = 'Test @#$% special <html> & chars';
      fireEvent.change(textarea, { target: { value: specialText } });

      expect(textarea).toHaveValue(specialText);
    });

    it('should handle very long text', () => {
      render(<ProblemInputDisplay />);

      const textarea = screen.getByLabelText('Problem description input');
      const longText = 'word '.repeat(1000);
      fireEvent.change(textarea, { target: { value: longText } });

      expect(screen.getByText(/1000 words/)).toBeInTheDocument();
    });
  });
});
