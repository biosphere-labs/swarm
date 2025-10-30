import React from 'react'
import { render, screen } from '@testing-library/react'
import { PipelineStatusBar, PipelineStage } from '../PipelineStatusBar'

describe('PipelineStatusBar', () => {
  const mockStages: PipelineStage[] = [
    {
      id: 'level-1',
      name: 'Paradigm Selection',
      status: 'complete',
      startTime: new Date('2024-01-01T10:00:00'),
      endTime: new Date('2024-01-01T10:02:30'),
      duration: 150000,
    },
    {
      id: 'level-2',
      name: 'Technique Selection',
      status: 'active',
      startTime: new Date('2024-01-01T10:02:30'),
    },
    {
      id: 'level-3',
      name: 'Decomposition Execution',
      status: 'pending',
    },
    {
      id: 'level-4',
      name: 'Solution Generation',
      status: 'failed',
    },
    {
      id: 'level-5',
      name: 'Solution Integration',
      status: 'waiting_approval',
    },
  ]

  it('renders all stages', () => {
    render(<PipelineStatusBar stages={mockStages} />)

    // Component renders both desktop and mobile views, so use getAllByText
    expect(screen.getAllByText('Paradigm Selection')).toHaveLength(2)
    expect(screen.getAllByText('Technique Selection')).toHaveLength(2)
    expect(screen.getAllByText('Decomposition Execution')).toHaveLength(2)
    expect(screen.getAllByText('Solution Generation')).toHaveLength(2)
    expect(screen.getAllByText('Solution Integration')).toHaveLength(2)
  })

  it('displays stage names correctly', () => {
    render(<PipelineStatusBar stages={mockStages} />)

    mockStages.forEach((stage) => {
      // Each stage appears twice (desktop + mobile view)
      expect(screen.getAllByText(stage.name)).toHaveLength(2)
    })
  })

  it('shows timestamps when showTimestamps is true', () => {
    render(<PipelineStatusBar stages={mockStages} showTimestamps={true} />)

    // Should show duration for completed stage (appears twice for desktop + mobile)
    expect(screen.getAllByText('2m 30s')).toHaveLength(2)
  })

  it('hides timestamps when showTimestamps is false', () => {
    render(<PipelineStatusBar stages={mockStages} showTimestamps={false} />)

    // Should not show any duration
    expect(screen.queryByText('2m 30s')).not.toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <PipelineStatusBar stages={mockStages} className="custom-class" />
    )

    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('renders with empty stages array', () => {
    render(<PipelineStatusBar stages={[]} />)

    // Component should render without crashing
    expect(screen.queryByText('Paradigm Selection')).not.toBeInTheDocument()
  })

  it('renders complete stage with green styling', () => {
    const completeStage: PipelineStage[] = [
      {
        id: 'test',
        name: 'Test Stage',
        status: 'complete',
      },
    ]

    const { container } = render(<PipelineStatusBar stages={completeStage} />)

    // Check for green text color (both desktop and mobile views)
    const stageNames = screen.getAllByText('Test Stage')
    stageNames.forEach(stageName => {
      expect(stageName).toHaveClass('text-green-600')
    })
  })

  it('renders active stage with blue styling', () => {
    const activeStage: PipelineStage[] = [
      {
        id: 'test',
        name: 'Active Stage',
        status: 'active',
      },
    ]

    const { container } = render(<PipelineStatusBar stages={activeStage} />)

    const stageNames = screen.getAllByText('Active Stage')
    stageNames.forEach(stageName => {
      expect(stageName).toHaveClass('text-blue-600')
    })
  })

  it('renders failed stage with red styling', () => {
    const failedStage: PipelineStage[] = [
      {
        id: 'test',
        name: 'Failed Stage',
        status: 'failed',
      },
    ]

    render(<PipelineStatusBar stages={failedStage} />)

    const stageNames = screen.getAllByText('Failed Stage')
    stageNames.forEach(stageName => {
      expect(stageName).toHaveClass('text-red-600')
    })
  })

  it('renders waiting_approval stage with orange styling', () => {
    const waitingStage: PipelineStage[] = [
      {
        id: 'test',
        name: 'Waiting Stage',
        status: 'waiting_approval',
      },
    ]

    render(<PipelineStatusBar stages={waitingStage} />)

    const stageNames = screen.getAllByText('Waiting Stage')
    stageNames.forEach(stageName => {
      expect(stageName).toHaveClass('text-orange-600')
    })
  })

  it('renders pending stage with gray styling', () => {
    const pendingStage: PipelineStage[] = [
      {
        id: 'test',
        name: 'Pending Stage',
        status: 'pending',
      },
    ]

    render(<PipelineStatusBar stages={pendingStage} />)

    const stageNames = screen.getAllByText('Pending Stage')
    stageNames.forEach(stageName => {
      expect(stageName).toHaveClass('text-gray-500')
    })
  })

  it('renders all 5 pipeline stages from spec', () => {
    const allStages: PipelineStage[] = [
      { id: '1', name: 'Paradigm Selection', status: 'complete' },
      { id: '2', name: 'Technique Selection', status: 'complete' },
      { id: '3', name: 'Decomposition Execution', status: 'active' },
      { id: '4', name: 'Solution Generation', status: 'pending' },
      { id: '5', name: 'Solution Integration', status: 'pending' },
    ]

    render(<PipelineStatusBar stages={allStages} />)

    // Each stage appears twice (desktop + mobile view)
    expect(screen.getAllByText('Paradigm Selection')).toHaveLength(2)
    expect(screen.getAllByText('Technique Selection')).toHaveLength(2)
    expect(screen.getAllByText('Decomposition Execution')).toHaveLength(2)
    expect(screen.getAllByText('Solution Generation')).toHaveLength(2)
    expect(screen.getAllByText('Solution Integration')).toHaveLength(2)
  })
})
