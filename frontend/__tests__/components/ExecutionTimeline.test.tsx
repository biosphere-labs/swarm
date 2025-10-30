import React from 'react';
import { render, screen } from '@testing-library/react';
import { ExecutionTimeline } from '@/components/visualizations/ExecutionTimeline';
import { TimelineEvent } from '@/types/visualization';

// Mock D3
jest.mock('d3', () => {
  const mockChain = {
    selectAll: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    attr: jest.fn().mockReturnThis(),
    append: jest.fn().mockReturnThis(),
    call: jest.fn().mockReturnThis(),
    style: jest.fn().mockReturnThis(),
    text: jest.fn().mockReturnThis(),
    data: jest.fn().mockReturnThis(),
    enter: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
  };

  return {
    select: jest.fn().mockReturnValue(mockChain),
    scaleTime: jest.fn().mockReturnValue({
      domain: jest.fn().mockReturnThis(),
      range: jest.fn().mockReturnThis(),
    }),
    scaleBand: jest.fn().mockReturnValue({
      domain: jest.fn().mockReturnThis(),
      range: jest.fn().mockReturnThis(),
      padding: jest.fn().mockReturnThis(),
      bandwidth: jest.fn().mockReturnValue(20),
    }),
    axisBottom: jest.fn().mockReturnValue({
      ticks: jest.fn().mockReturnThis(),
      tickFormat: jest.fn().mockReturnThis(),
    }),
    axisLeft: jest.fn().mockReturnValue({
      tickSize: jest.fn().mockReturnThis(),
      tickFormat: jest.fn().mockReturnThis(),
    }),
    timeFormat: jest.fn().mockReturnValue(jest.fn()),
    min: jest.fn(),
    max: jest.fn(),
  };
});

describe('ExecutionTimeline', () => {
  const mockEvents: TimelineEvent[] = [
    {
      id: '1',
      name: 'Stage 1',
      startTime: new Date(Date.now() - 10000),
      endTime: new Date(Date.now() - 5000),
      type: 'stage',
      status: 'complete',
    },
    {
      id: '2',
      name: 'Stage 2',
      startTime: new Date(Date.now() - 5000),
      type: 'stage',
      status: 'in_progress',
    },
  ];

  it('renders timeline with title', () => {
    render(<ExecutionTimeline events={mockEvents} />);
    expect(screen.getByText('Execution Timeline')).toBeInTheDocument();
  });

  it('renders SVG element', () => {
    const { container } = render(<ExecutionTimeline events={mockEvents} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('handles empty events', () => {
    render(<ExecutionTimeline events={[]} />);
    expect(screen.getByText('Execution Timeline')).toBeInTheDocument();
  });

  it('respects custom dimensions', () => {
    const { container } = render(
      <ExecutionTimeline events={mockEvents} width={1000} height={500} />
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });
});
