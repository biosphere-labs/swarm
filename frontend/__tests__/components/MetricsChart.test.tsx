import React from 'react';
import { render, screen } from '@testing-library/react';
import { MetricsChart, MultiMetricsChart } from '@/components/visualizations/MetricsChart';
import { MetricData } from '@/types/visualization';

// Mock Recharts components
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  Area: () => <div data-testid="area" />,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }: any) => (
    <div data-testid="responsive-container">{children}</div>
  ),
}));

describe('MetricsChart', () => {
  const mockData: MetricData[] = [
    { timestamp: new Date(), value: 100 },
    { timestamp: new Date(), value: 150 },
    { timestamp: new Date(), value: 120 },
  ];

  it('renders line chart by default', () => {
    render(<MetricsChart data={mockData} title="Test Chart" />);
    expect(screen.getByText('Test Chart')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });

  it('renders area chart when type is area', () => {
    render(<MetricsChart data={mockData} title="Area Chart" type="area" />);
    expect(screen.getByTestId('area-chart')).toBeInTheDocument();
  });

  it('renders bar chart when type is bar', () => {
    render(<MetricsChart data={mockData} title="Bar Chart" type="bar" />);
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
  });

  it('handles empty data', () => {
    render(<MetricsChart data={[]} title="Empty Chart" />);
    expect(screen.getByText('Empty Chart')).toBeInTheDocument();
  });
});

describe('MultiMetricsChart', () => {
  const mockDatasets = [
    {
      data: [
        { timestamp: new Date(), value: 100 },
        { timestamp: new Date(), value: 150 },
      ],
      label: 'Metric 1',
      color: '#3b82f6',
    },
    {
      data: [
        { timestamp: new Date(), value: 200 },
        { timestamp: new Date(), value: 250 },
      ],
      label: 'Metric 2',
      color: '#10b981',
    },
  ];

  it('renders multi-line chart', () => {
    render(<MultiMetricsChart datasets={mockDatasets} title="Multi Chart" />);
    expect(screen.getByText('Multi Chart')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
  });
});
