import React from 'react'
import { render, screen, waitFor, act } from '@testing-library/react'
import { AgentPoolMonitor, PoolMetrics, SSEConnectionState } from '@/components/AgentPoolMonitor'

// Mock fetch API
global.fetch = jest.fn()

// Mock Recharts components
jest.mock('recharts', () => ({
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }: any) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  Cell: () => <div data-testid="cell" />
}))

describe('AgentPoolMonitor', () => {
  const mockPoolData: Record<string, PoolMetrics> = {
    structural: {
      pool_name: 'structural',
      total_agents: 50,
      active_agents: 10,
      idle_agents: 38,
      stuck_agents: 2,
      total_tasks_completed: 100,
      average_response_time: 1.5,
      current_queue_size: 5,
      timestamp: '2025-10-30T12:00:00Z'
    },
    functional: {
      pool_name: 'functional',
      total_agents: 50,
      active_agents: 15,
      idle_agents: 35,
      stuck_agents: 0,
      total_tasks_completed: 150,
      average_response_time: 2.0,
      current_queue_size: 0,
      timestamp: '2025-10-30T12:00:00Z'
    },
    temporal: {
      pool_name: 'temporal',
      total_agents: 50,
      active_agents: 5,
      idle_agents: 45,
      stuck_agents: 0,
      total_tasks_completed: 50,
      average_response_time: 1.2,
      current_queue_size: 2,
      timestamp: '2025-10-30T12:00:00Z'
    },
    spatial: {
      pool_name: 'spatial',
      total_agents: 50,
      active_agents: 8,
      idle_agents: 42,
      stuck_agents: 0,
      total_tasks_completed: 75,
      average_response_time: 1.8,
      current_queue_size: 1,
      timestamp: '2025-10-30T12:00:00Z'
    },
    hierarchical: {
      pool_name: 'hierarchical',
      total_agents: 50,
      active_agents: 12,
      idle_agents: 38,
      stuck_agents: 0,
      total_tasks_completed: 120,
      average_response_time: 1.6,
      current_queue_size: 3,
      timestamp: '2025-10-30T12:00:00Z'
    },
    computational: {
      pool_name: 'computational',
      total_agents: 50,
      active_agents: 20,
      idle_agents: 30,
      stuck_agents: 0,
      total_tasks_completed: 200,
      average_response_time: 2.5,
      current_queue_size: 8,
      timestamp: '2025-10-30T12:00:00Z'
    },
    data: {
      pool_name: 'data',
      total_agents: 50,
      active_agents: 18,
      idle_agents: 32,
      stuck_agents: 0,
      total_tasks_completed: 180,
      average_response_time: 2.2,
      current_queue_size: 6,
      timestamp: '2025-10-30T12:00:00Z'
    },
    dependency: {
      pool_name: 'dependency',
      total_agents: 50,
      active_agents: 7,
      idle_agents: 43,
      stuck_agents: 0,
      total_tasks_completed: 70,
      average_response_time: 1.4,
      current_queue_size: 2,
      timestamp: '2025-10-30T12:00:00Z'
    },
    api_design: {
      pool_name: 'api_design',
      total_agents: 30,
      active_agents: 10,
      idle_agents: 20,
      stuck_agents: 0,
      total_tasks_completed: 90,
      average_response_time: 1.7,
      current_queue_size: 4,
      timestamp: '2025-10-30T12:00:00Z'
    },
    data_processing: {
      pool_name: 'data_processing',
      total_agents: 30,
      active_agents: 12,
      idle_agents: 18,
      stuck_agents: 0,
      total_tasks_completed: 110,
      average_response_time: 1.9,
      current_queue_size: 5,
      timestamp: '2025-10-30T12:00:00Z'
    },
    ml_modeling: {
      pool_name: 'ml_modeling',
      total_agents: 20,
      active_agents: 8,
      idle_agents: 12,
      stuck_agents: 0,
      total_tasks_completed: 60,
      average_response_time: 3.0,
      current_queue_size: 3,
      timestamp: '2025-10-30T12:00:00Z'
    },
    security: {
      pool_name: 'security',
      total_agents: 20,
      active_agents: 5,
      idle_agents: 15,
      stuck_agents: 0,
      total_tasks_completed: 40,
      average_response_time: 2.8,
      current_queue_size: 2,
      timestamp: '2025-10-30T12:00:00Z'
    },
    general: {
      pool_name: 'general',
      total_agents: 10,
      active_agents: 3,
      idle_agents: 7,
      stuck_agents: 0,
      total_tasks_completed: 25,
      average_response_time: 3.5,
      current_queue_size: 1,
      timestamp: '2025-10-30T12:00:00Z'
    }
  }

  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('renders the component with header and title', () => {
    render(<AgentPoolMonitor />)

    expect(screen.getByText('Agent Pool Monitor')).toBeInTheDocument()
    expect(screen.getByText(/Real-time monitoring of/)).toBeInTheDocument()
  })

  it('displays connection status badge', () => {
    render(<AgentPoolMonitor />)

    // Initially should show connecting or disconnected
    expect(
      screen.getByText('Disconnected') || screen.getByText('Connecting')
    ).toBeInTheDocument()
  })

  it('shows summary statistics', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPoolData
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(screen.getByText('Total Agents')).toBeInTheDocument()
      expect(screen.getByText('Active')).toBeInTheDocument()
      expect(screen.getByText('Idle')).toBeInTheDocument()
      expect(screen.getByText('Stuck')).toBeInTheDocument()
    })
  })

  it('displays all 13 pools correctly', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPoolData
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      // Check for paradigm pools
      expect(screen.getByText('Paradigm Pools (8)')).toBeInTheDocument()
      expect(screen.getByText('structural')).toBeInTheDocument()
      expect(screen.getByText('functional')).toBeInTheDocument()
      expect(screen.getByText('temporal')).toBeInTheDocument()
      expect(screen.getByText('spatial')).toBeInTheDocument()
      expect(screen.getByText('hierarchical')).toBeInTheDocument()
      expect(screen.getByText('computational')).toBeInTheDocument()
      expect(screen.getByText('data')).toBeInTheDocument()
      expect(screen.getByText('dependency')).toBeInTheDocument()

      // Check for domain pools
      expect(screen.getByText('Domain Pools (4)')).toBeInTheDocument()
      expect(screen.getByText('api design')).toBeInTheDocument()
      expect(screen.getByText('data processing')).toBeInTheDocument()
      expect(screen.getByText('ml modeling')).toBeInTheDocument()
      expect(screen.getByText('security')).toBeInTheDocument()

      // Check for general pool
      expect(screen.getByText('General Pool (1)')).toBeInTheDocument()
      expect(screen.getByText('general')).toBeInTheDocument()
    })
  })

  it('shows correct metrics for each pool', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPoolData
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      // Check structural pool metrics
      const structuralMetrics = mockPoolData.structural
      expect(screen.getByText('20%')).toBeInTheDocument() // utilization
      expect(screen.getByText('100')).toBeInTheDocument() // completed tasks
      expect(screen.getByText('1.50s')).toBeInTheDocument() // response time
    })
  })

  it('renders utilization chart', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPoolData
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(screen.getByText('Pool Utilization Overview')).toBeInTheDocument()
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
    })
  })

  it('updates when receiving new data', async () => {
    const initialData = { ...mockPoolData }
    const updatedData = {
      ...mockPoolData,
      structural: {
        ...mockPoolData.structural,
        active_agents: 20,
        idle_agents: 28,
        total_tasks_completed: 150
      }
    }

    ;(global.fetch as jest.Mock)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => initialData
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => updatedData
      })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(screen.getByText('100')).toBeInTheDocument()
    })

    // Advance time to trigger refresh
    await act(async () => {
      jest.advanceTimersByTime(1000)
    })

    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument()
    })
  })

  it('handles fetch error gracefully', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(screen.getByText('Connection Error')).toBeInTheDocument()
      expect(screen.getByText('Network error')).toBeInTheDocument()
      expect(screen.getByText('Error')).toBeInTheDocument()
    })
  })

  it('handles HTTP error status', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(screen.getByText('Connection Error')).toBeInTheDocument()
      expect(screen.getByText(/HTTP 500/)).toBeInTheDocument()
    })
  })

  it('shows connecting state during fetch', async () => {
    ;(global.fetch as jest.Mock).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => mockPoolData
              }),
            500
          )
        })
    )

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(50)
    })

    expect(screen.getByText('Connecting')).toBeInTheDocument()

    await act(async () => {
      jest.advanceTimersByTime(500)
    })

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument()
    })
  })

  it('displays stuck agents correctly', async () => {
    const dataWithStuck = {
      ...mockPoolData,
      structural: {
        ...mockPoolData.structural,
        active_agents: 8,
        idle_agents: 36,
        stuck_agents: 6
      }
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => dataWithStuck
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      // Should show 6 stuck agents total (from structural pool)
      const stuckBadges = screen.getAllByText('6')
      expect(stuckBadges.length).toBeGreaterThan(0)
    })
  })

  it('formats response time correctly', async () => {
    const dataWithVariousTimes = {
      structural: {
        ...mockPoolData.structural,
        average_response_time: 0.5 // Should show as 500ms
      },
      functional: {
        ...mockPoolData.functional,
        average_response_time: 2.5 // Should show as 2.50s
      }
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => dataWithVariousTimes
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(screen.getByText('500ms')).toBeInTheDocument()
      expect(screen.getByText('2.50s')).toBeInTheDocument()
    })
  })

  it('cleans up on unmount', async () => {
    const clearIntervalSpy = jest.spyOn(global, 'clearInterval')

    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => mockPoolData
    })

    const { unmount } = render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    unmount()

    expect(clearIntervalSpy).toHaveBeenCalled()
  })

  it('uses custom API endpoint', async () => {
    const customEndpoint = '/custom/api/pools'

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPoolData
    })

    render(<AgentPoolMonitor apiEndpoint={customEndpoint} refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(`${customEndpoint}/metrics`)
    })
  })

  it('handles empty data response', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({})
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    // Should still render with initial/default data
    await waitFor(() => {
      expect(screen.getByText('Agent Pool Monitor')).toBeInTheDocument()
      expect(screen.getByText('Paradigm Pools (8)')).toBeInTheDocument()
    })
  })

  it('handles array format response', async () => {
    const arrayData = Object.values(mockPoolData)

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => arrayData
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      expect(screen.getByText('structural')).toBeInTheDocument()
      expect(screen.getByText('functional')).toBeInTheDocument()
    })
  })

  it('calculates summary statistics correctly', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPoolData
    })

    render(<AgentPoolMonitor refreshInterval={1000} />)

    await act(async () => {
      jest.advanceTimersByTime(100)
    })

    await waitFor(() => {
      // Total agents: 8*50 + 2*30 + 2*20 + 10 = 510
      expect(screen.getByText('510')).toBeInTheDocument()

      // Total active: 10+15+5+8+12+20+18+7+10+12+8+5+3 = 133
      expect(screen.getByText('133')).toBeInTheDocument()

      // Total stuck: 2 (from structural pool)
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })
})
