import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { PipelineMonitor } from '../PipelineMonitor'
import { useSSEConnection } from '@/hooks/useSSEConnection'

// Mock the SSE hook
jest.mock('@/hooks/useSSEConnection')

const mockUseSSEConnection = useSSEConnection as jest.MockedFunction<
  typeof useSSEConnection
>

describe('PipelineMonitor', () => {
  const mockReconnect = jest.fn()
  const mockDisconnect = jest.fn()

  const defaultMockReturn = {
    state: {
      run_id: 'test-run-123',
      status: 'unknown' as const,
      current_stage: 'unknown' as const,
      awaiting_approval: false,
    },
    connectionStatus: 'disconnected' as const,
    error: null,
    reconnect: mockReconnect,
    disconnect: mockDisconnect,
    isConnected: false,
  }

  beforeEach(() => {
    jest.clearAllMocks()
    mockUseSSEConnection.mockReturnValue(defaultMockReturn)
  })

  describe('Initial Render', () => {
    it('should render without runId', () => {
      render(<PipelineMonitor runId={null} />)

      expect(screen.getByText('No pipeline run selected')).toBeInTheDocument()
    })

    it('should render with runId', () => {
      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Pipeline Monitor')).toBeInTheDocument()
      expect(screen.getByText(/Run ID: test-run-123/)).toBeInTheDocument()
    })

    it('should display disconnected status by default', () => {
      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Disconnected')).toBeInTheDocument()
    })

    it('should display unknown pipeline status by default', () => {
      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Unknown')).toBeInTheDocument()
    })
  })

  describe('Connection Status', () => {
    it('should display connecting status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        connectionStatus: 'connecting',
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Connecting')).toBeInTheDocument()
    })

    it('should display connected status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        connectionStatus: 'connected',
        isConnected: true,
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Live')).toBeInTheDocument()
    })

    it('should display error status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        connectionStatus: 'error',
        error: 'Connection failed',
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Error')).toBeInTheDocument()
    })
  })

  describe('Pipeline Status', () => {
    it('should display pending status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          status: 'pending',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Pending')).toBeInTheDocument()
    })

    it('should display running status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          status: 'running',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Running')).toBeInTheDocument()
    })

    it('should display completed status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          status: 'completed',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Completed')).toBeInTheDocument()
    })

    it('should display failed status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          status: 'failed',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Failed')).toBeInTheDocument()
    })

    it('should display cancelled status', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          status: 'cancelled',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Cancelled')).toBeInTheDocument()
    })
  })

  describe('Pipeline Stage', () => {
    it('should display current stage', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          current_stage: 'level1_paradigm',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Level1 Paradigm')).toBeInTheDocument()
    })

    it('should format stage names correctly', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          current_stage: 'level3_decomposition',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Level3 Decomposition')).toBeInTheDocument()
    })
  })

  describe('Timestamps', () => {
    it('should display last update time', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          last_update: '2025-01-01T12:00:00Z',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Last Update')).toBeInTheDocument()
      // Time display will vary by locale, just check it exists
    })

    it('should display completed time when pipeline is done', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          status: 'completed',
          completed_at: '2025-01-01T12:30:00Z',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Completed At')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should display connection error message', () => {
      const errorMessage = 'Failed to connect to server'
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        connectionStatus: 'error',
        error: errorMessage,
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Connection Error')).toBeInTheDocument()
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })

    it('should display pipeline error from state', () => {
      const errorMessage = 'Pipeline execution failed'
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          error: errorMessage,
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Pipeline Error')).toBeInTheDocument()
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })

    it('should show retry button on connection error', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        connectionStatus: 'error',
        error: 'Connection failed',
      })

      render(<PipelineMonitor runId="test-run-123" />)

      const retryButton = screen.getByText('Retry')
      expect(retryButton).toBeInTheDocument()

      fireEvent.click(retryButton)
      expect(mockReconnect).toHaveBeenCalledTimes(1)
    })
  })

  describe('Approval Required', () => {
    it('should display approval required message', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          awaiting_approval: true,
          approval_gate: 'paradigm_selection',
        },
      })

      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Approval Required')).toBeInTheDocument()
      expect(
        screen.getByText(/waiting for approval at gate: paradigm_selection/)
      ).toBeInTheDocument()
    })

    it('should call onApprovalRequired callback', () => {
      const onApprovalRequired = jest.fn()

      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        state: {
          ...defaultMockReturn.state,
          awaiting_approval: true,
          approval_gate: 'technique_selection',
        },
      })

      render(
        <PipelineMonitor runId="test-run-123" onApprovalRequired={onApprovalRequired} />
      )

      expect(onApprovalRequired).toHaveBeenCalledWith('technique_selection')
    })

    it('should not call onApprovalRequired when not awaiting approval', () => {
      const onApprovalRequired = jest.fn()

      render(
        <PipelineMonitor runId="test-run-123" onApprovalRequired={onApprovalRequired} />
      )

      expect(onApprovalRequired).not.toHaveBeenCalled()
    })
  })

  describe('Connection Controls', () => {
    it('should have reconnect and disconnect buttons', () => {
      render(<PipelineMonitor runId="test-run-123" />)

      expect(screen.getByText('Reconnect')).toBeInTheDocument()
      expect(screen.getByText('Disconnect')).toBeInTheDocument()
    })

    it('should call reconnect when button clicked', () => {
      render(<PipelineMonitor runId="test-run-123" />)

      const reconnectButton = screen.getByText('Reconnect')
      fireEvent.click(reconnectButton)

      expect(mockReconnect).toHaveBeenCalledTimes(1)
    })

    it('should call disconnect when button clicked', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        connectionStatus: 'connected',
        isConnected: true,
      })

      render(<PipelineMonitor runId="test-run-123" />)

      const disconnectButton = screen.getByText('Disconnect')
      fireEvent.click(disconnectButton)

      expect(mockDisconnect).toHaveBeenCalledTimes(1)
    })

    it('should disable reconnect button when connected', () => {
      mockUseSSEConnection.mockReturnValue({
        ...defaultMockReturn,
        connectionStatus: 'connected',
        isConnected: true,
      })

      render(<PipelineMonitor runId="test-run-123" />)

      const reconnectButton = screen.getByText('Reconnect')
      expect(reconnectButton).toBeDisabled()
    })

    it('should disable disconnect button when not connected', () => {
      render(<PipelineMonitor runId="test-run-123" />)

      const disconnectButton = screen.getByText('Disconnect')
      expect(disconnectButton).toBeDisabled()
    })
  })

  describe('Custom Styling', () => {
    it('should apply custom className', () => {
      const { container } = render(
        <PipelineMonitor runId="test-run-123" className="custom-class" />
      )

      const card = container.querySelector('.custom-class')
      expect(card).toBeInTheDocument()
    })
  })

  describe('Integration', () => {
    it('should pass runId to useSSEConnection hook', () => {
      render(<PipelineMonitor runId="test-run-123" />)

      expect(mockUseSSEConnection).toHaveBeenCalledWith('test-run-123', {
        debug: false,
      })
    })

    it('should enable debug mode in development', () => {
      const originalEnv = process.env.NODE_ENV
      process.env.NODE_ENV = 'development'

      render(<PipelineMonitor runId="test-run-123" />)

      expect(mockUseSSEConnection).toHaveBeenCalledWith('test-run-123', {
        debug: true,
      })

      process.env.NODE_ENV = originalEnv
    })
  })
})
