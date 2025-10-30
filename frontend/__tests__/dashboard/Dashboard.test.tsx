/**
 * Comprehensive test suite for Dashboard components
 * Tests DashboardLayout, DashboardNavigation, and dashboard page
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import '@testing-library/jest-dom'
import { DashboardNavigation } from '@/components/DashboardNavigation'
import { DashboardLayout } from '@/components/DashboardLayout'
import { PipelineStage } from '@/components/PipelineStatusBar'

// Mock Next.js navigation hooks
const mockPush = jest.fn()
const mockSearchParams = new URLSearchParams()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    pathname: '/dashboard',
    query: {},
  }),
  useSearchParams: () => mockSearchParams,
  usePathname: () => '/dashboard',
}))

// Mock child components to isolate testing
jest.mock('@/components/PipelineStatusBar', () => ({
  PipelineStatusBar: ({ stages }: { stages: PipelineStage[] }) => (
    <div data-testid="pipeline-status-bar">
      Pipeline Status ({stages.length} stages)
    </div>
  ),
}))

describe('DashboardNavigation', () => {
  const defaultProps = {
    collapsed: false,
    onToggleCollapse: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockSearchParams.delete('view')
  })

  describe('Rendering', () => {
    it('should render all navigation items when expanded', () => {
      render(<DashboardNavigation {...defaultProps} />)

      expect(screen.getByText('Problem Input')).toBeInTheDocument()
      expect(screen.getByText('Paradigm Selection')).toBeInTheDocument()
      expect(screen.getByText('Technique Selection')).toBeInTheDocument()
      expect(screen.getByText('Decomposition Graph')).toBeInTheDocument()
      expect(screen.getByText('Agent Pool Monitor')).toBeInTheDocument()
      expect(screen.getByText('Integration Conflicts')).toBeInTheDocument()
      expect(screen.getByText('Approval Gates')).toBeInTheDocument()
      expect(screen.getByText('Solution Output')).toBeInTheDocument()
    })

    it('should render navigation header with title', () => {
      render(<DashboardNavigation {...defaultProps} />)

      expect(screen.getByText('Navigation')).toBeInTheDocument()
    })

    it('should render footer with pipeline status', () => {
      render(<DashboardNavigation {...defaultProps} />)

      expect(screen.getByText('Pipeline Status')).toBeInTheDocument()
      expect(screen.getByText('Active')).toBeInTheDocument()
    })

    it('should render toggle button', () => {
      render(<DashboardNavigation {...defaultProps} />)

      const toggleButton = screen.getByRole('button', { name: /collapse sidebar/i })
      expect(toggleButton).toBeInTheDocument()
    })
  })

  describe('Collapsed State', () => {
    it('should hide text content when collapsed', () => {
      render(<DashboardNavigation {...defaultProps} collapsed={true} />)

      expect(screen.queryByText('Navigation')).not.toBeInTheDocument()
      expect(screen.queryByText('Define the problem to solve')).not.toBeInTheDocument()
    })

    it('should show expand button when collapsed', () => {
      render(<DashboardNavigation {...defaultProps} collapsed={true} />)

      const toggleButton = screen.getByRole('button', { name: /expand sidebar/i })
      expect(toggleButton).toBeInTheDocument()
    })

    it('should still render all navigation icons when collapsed', () => {
      const { container } = render(<DashboardNavigation {...defaultProps} collapsed={true} />)

      // Icons should still be present (8 navigation items)
      const links = container.querySelectorAll('a')
      expect(links).toHaveLength(8)
    })

    it('should hide footer when collapsed', () => {
      render(<DashboardNavigation {...defaultProps} collapsed={true} />)

      expect(screen.queryByText('Pipeline Status')).not.toBeInTheDocument()
    })
  })

  describe('Interactions', () => {
    it('should call onToggleCollapse when toggle button is clicked', () => {
      const onToggleCollapse = jest.fn()
      render(<DashboardNavigation {...defaultProps} onToggleCollapse={onToggleCollapse} />)

      const toggleButton = screen.getByRole('button', { name: /collapse sidebar/i })
      fireEvent.click(toggleButton)

      expect(onToggleCollapse).toHaveBeenCalledTimes(1)
    })

    it('should render navigation links with correct href', () => {
      const { container } = render(<DashboardNavigation {...defaultProps} />)

      const problemInputLink = container.querySelector('a[href="/dashboard?view=problem-input"]')
      expect(problemInputLink).toBeInTheDocument()

      const paradigmLink = container.querySelector('a[href="/dashboard?view=paradigm-selection"]')
      expect(paradigmLink).toBeInTheDocument()
    })
  })

  describe('Active State', () => {
    it('should highlight active view based on search params', () => {
      mockSearchParams.set('view', 'paradigm-selection')
      const { container } = render(<DashboardNavigation {...defaultProps} />)

      const paradigmLink = container.querySelector('a[href="/dashboard?view=paradigm-selection"]')
      expect(paradigmLink).toHaveClass('bg-blue-50')
    })

    it('should not highlight inactive views', () => {
      mockSearchParams.set('view', 'paradigm-selection')
      const { container } = render(<DashboardNavigation {...defaultProps} />)

      const problemInputLink = container.querySelector('a[href="/dashboard?view=problem-input"]')
      expect(problemInputLink).not.toHaveClass('bg-blue-50')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels for collapsed state', () => {
      render(<DashboardNavigation {...defaultProps} collapsed={true} />)

      const toggleButton = screen.getByLabelText('Expand sidebar')
      expect(toggleButton).toBeInTheDocument()
    })

    it('should have proper ARIA labels for expanded state', () => {
      render(<DashboardNavigation {...defaultProps} collapsed={false} />)

      const toggleButton = screen.getByLabelText('Collapse sidebar')
      expect(toggleButton).toBeInTheDocument()
    })

    it('should set title attribute on links when collapsed', () => {
      const { container } = render(<DashboardNavigation {...defaultProps} collapsed={true} />)

      const links = container.querySelectorAll('a[title]')
      expect(links.length).toBeGreaterThan(0)
    })
  })

  describe('Styling', () => {
    it('should apply custom className', () => {
      const { container } = render(
        <DashboardNavigation {...defaultProps} className="custom-class" />
      )

      const nav = container.querySelector('nav')
      expect(nav).toHaveClass('custom-class')
    })

    it('should have transition classes for collapse animation', () => {
      const { container } = render(<DashboardNavigation {...defaultProps} />)

      const nav = container.querySelector('nav')
      expect(nav).toHaveClass('transition-all')
      expect(nav).toHaveClass('duration-300')
    })

    it('should have correct width when expanded', () => {
      const { container } = render(<DashboardNavigation {...defaultProps} collapsed={false} />)

      const nav = container.querySelector('nav')
      expect(nav).toHaveClass('w-64')
    })

    it('should have correct width when collapsed', () => {
      const { container } = render(<DashboardNavigation {...defaultProps} collapsed={true} />)

      const nav = container.querySelector('nav')
      expect(nav).toHaveClass('w-16')
    })
  })
})

describe('DashboardLayout', () => {
  const mockStages: PipelineStage[] = [
    {
      id: 'stage-1',
      name: 'Input',
      status: 'complete',
      startTime: new Date('2024-01-01T10:00:00'),
      endTime: new Date('2024-01-01T10:05:00'),
    },
    {
      id: 'stage-2',
      name: 'Processing',
      status: 'active',
      startTime: new Date('2024-01-01T10:05:00'),
    },
    {
      id: 'stage-3',
      name: 'Output',
      status: 'pending',
    },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
    // Mock window.innerWidth for responsive tests
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    })
  })

  describe('Rendering', () => {
    it('should render children content', () => {
      render(
        <DashboardLayout>
          <div data-testid="test-content">Test Content</div>
        </DashboardLayout>
      )

      expect(screen.getByTestId('test-content')).toBeInTheDocument()
      expect(screen.getByText('Test Content')).toBeInTheDocument()
    })

    it('should render pipeline status bar', () => {
      render(
        <DashboardLayout pipelineStages={mockStages}>
          <div>Content</div>
        </DashboardLayout>
      )

      expect(screen.getByTestId('pipeline-status-bar')).toBeInTheDocument()
    })

    it('should render header with title', () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      expect(screen.getByText('Decomposition Pipeline')).toBeInTheDocument()
      expect(screen.getByText('Real-time control center')).toBeInTheDocument()
    })

    it('should render current view label when provided', () => {
      render(
        <DashboardLayout currentView="paradigm-selection">
          <div>Content</div>
        </DashboardLayout>
      )

      expect(screen.getByText('Current View')).toBeInTheDocument()
      expect(screen.getByText('Paradigm selection')).toBeInTheDocument()
    })

    it('should use default pipeline stages when not provided', () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      const statusBar = screen.getByTestId('pipeline-status-bar')
      expect(statusBar).toHaveTextContent('7 stages')
    })
  })

  describe('Sidebar Behavior', () => {
    it('should render navigation sidebar', () => {
      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      expect(screen.getByText('Navigation')).toBeInTheDocument()
    })

    it('should start with sidebar expanded on desktop', () => {
      const { container } = render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      const nav = container.querySelector('nav')
      expect(nav).toHaveClass('w-64')
    })
  })

  describe('Responsive Behavior', () => {
    it('should handle window resize to mobile', async () => {
      const { container } = render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      // Simulate resize to mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 500,
      })
      fireEvent(window, new Event('resize'))

      await waitFor(() => {
        const nav = container.querySelector('nav')
        expect(nav).toHaveClass('w-16')
      })
    })

    it('should not render overlay on desktop when sidebar is open', () => {
      const { container } = render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      const overlay = container.querySelector('[aria-label="Close sidebar"]')
      expect(overlay).not.toBeInTheDocument()
    })
  })

  describe('Layout Structure', () => {
    it('should have proper semantic HTML structure', () => {
      const { container } = render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      expect(container.querySelector('header')).toBeInTheDocument()
      expect(container.querySelector('aside')).toBeInTheDocument()
      expect(container.querySelector('main')).toBeInTheDocument()
      expect(container.querySelector('nav')).toBeInTheDocument()
    })

    it('should have sticky header', () => {
      const { container } = render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      const header = container.querySelector('header')
      expect(header).toHaveClass('sticky')
      expect(header).toHaveClass('top-0')
    })

    it('should have overflow handling on main content', () => {
      const { container } = render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      const main = container.querySelector('main')
      expect(main).toHaveClass('overflow-auto')
    })
  })

  describe('Styling', () => {
    it('should apply custom className', () => {
      const { container } = render(
        <DashboardLayout className="custom-layout-class">
          <div>Content</div>
        </DashboardLayout>
      )

      const layout = container.firstChild
      expect(layout).toHaveClass('custom-layout-class')
    })

    it('should have dark mode classes', () => {
      const { container } = render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      )

      const layout = container.firstChild
      expect(layout).toHaveClass('dark:bg-gray-950')
    })
  })
})

describe('Dashboard Integration', () => {
  const mockStages: PipelineStage[] = [
    { id: '1', name: 'Input', status: 'complete' },
    { id: '2', name: 'Processing', status: 'active' },
    { id: '3', name: 'Output', status: 'pending' },
  ]

  it('should integrate navigation with layout correctly', () => {
    render(
      <DashboardLayout pipelineStages={mockStages} currentView="paradigm-selection">
        <div data-testid="page-content">Dashboard Page</div>
      </DashboardLayout>
    )

    expect(screen.getByTestId('page-content')).toBeInTheDocument()
    expect(screen.getByText('Navigation')).toBeInTheDocument()
    expect(screen.getByTestId('pipeline-status-bar')).toBeInTheDocument()
  })

  it('should maintain state across view changes', () => {
    const { rerender } = render(
      <DashboardLayout currentView="problem-input">
        <div>Problem Input View</div>
      </DashboardLayout>
    )

    expect(screen.getByText('Problem input')).toBeInTheDocument()

    rerender(
      <DashboardLayout currentView="paradigm-selection">
        <div>Paradigm Selection View</div>
      </DashboardLayout>
    )

    expect(screen.getByText('Paradigm selection')).toBeInTheDocument()
  })
})

describe('View Navigation Flow', () => {
  it('should have links for all 8 required views', () => {
    const { container } = render(
      <DashboardNavigation collapsed={false} onToggleCollapse={jest.fn()} />
    )

    const expectedViews = [
      'problem-input',
      'paradigm-selection',
      'technique-selection',
      'decomposition-graph',
      'agent-pool',
      'integration-conflicts',
      'approval-gates',
      'solution-output',
    ]

    expectedViews.forEach((view) => {
      const link = container.querySelector(`a[href="/dashboard?view=${view}"]`)
      expect(link).toBeInTheDocument()
    })
  })

  it('should properly format view names in current view display', () => {
    const testCases = [
      { view: 'problem-input', expected: 'Problem input' },
      { view: 'paradigm-selection', expected: 'Paradigm selection' },
      { view: 'agent-pool', expected: 'Agent pool' },
    ]

    testCases.forEach(({ view, expected }) => {
      const { unmount } = render(
        <DashboardLayout currentView={view as any}>
          <div>Content</div>
        </DashboardLayout>
      )

      expect(screen.getByText(expected)).toBeInTheDocument()
      unmount()
    })
  })
})

describe('Edge Cases', () => {
  it('should handle missing currentView gracefully', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    )

    expect(screen.queryByText('Current View')).not.toBeInTheDocument()
  })

  it('should handle empty pipeline stages array', () => {
    render(
      <DashboardLayout pipelineStages={[]}>
        <div>Content</div>
      </DashboardLayout>
    )

    const statusBar = screen.getByTestId('pipeline-status-bar')
    expect(statusBar).toHaveTextContent('0 stages')
  })

  it('should handle rapid toggle of sidebar', () => {
    const onToggleCollapse = jest.fn()
    render(<DashboardNavigation collapsed={false} onToggleCollapse={onToggleCollapse} />)

    const toggleButton = screen.getByRole('button', { name: /collapse sidebar/i })

    fireEvent.click(toggleButton)
    fireEvent.click(toggleButton)
    fireEvent.click(toggleButton)

    expect(onToggleCollapse).toHaveBeenCalledTimes(3)
  })
})

describe('Performance', () => {
  it('should render navigation items efficiently', () => {
    const startTime = performance.now()

    render(<DashboardNavigation collapsed={false} onToggleCollapse={jest.fn()} />)

    const endTime = performance.now()
    const renderTime = endTime - startTime

    // Should render in less than 100ms
    expect(renderTime).toBeLessThan(100)
  })

  it('should handle large pipeline stages array', () => {
    const manyStages: PipelineStage[] = Array.from({ length: 50 }, (_, i) => ({
      id: `stage-${i}`,
      name: `Stage ${i}`,
      status: i < 25 ? 'complete' : i < 30 ? 'active' : 'pending',
    }))

    const startTime = performance.now()

    render(
      <DashboardLayout pipelineStages={manyStages}>
        <div>Content</div>
      </DashboardLayout>
    )

    const endTime = performance.now()
    const renderTime = endTime - startTime

    // Should handle large arrays efficiently
    expect(renderTime).toBeLessThan(200)
  })
})
