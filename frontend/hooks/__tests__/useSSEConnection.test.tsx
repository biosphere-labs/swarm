import { renderHook, act, waitFor } from '@testing-library/react'
import { useSSEConnection } from '../useSSEConnection'
import {
  SSEConnectionStatus,
  PipelineStatus,
  PipelineStage,
  StateUpdateEvent,
  StatusChangeEvent,
  StageChangeEvent,
  ApprovalRequiredEvent,
  PipelineFinishedEvent,
  ErrorEvent,
} from '@/types/sse'

/**
 * Mock EventSource implementation for testing
 */
class MockEventSource {
  url: string
  readyState: number = 0 // CONNECTING
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  private listeners: Map<string, Set<(event: Event) => void>> = new Map()

  static CONNECTING = 0
  static OPEN = 1
  static CLOSED = 2

  constructor(url: string) {
    this.url = url
    // Simulate async connection
    setTimeout(() => this.simulateOpen(), 10)
  }

  addEventListener(type: string, listener: (event: Event) => void) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }
    this.listeners.get(type)!.add(listener)
  }

  removeEventListener(type: string, listener: (event: Event) => void) {
    this.listeners.get(type)?.delete(listener)
  }

  close() {
    this.readyState = MockEventSource.CLOSED
  }

  // Test helpers
  simulateOpen() {
    this.readyState = MockEventSource.OPEN
    if (this.onopen) {
      this.onopen(new Event('open'))
    }
  }

  simulateMessage(data: string, eventType?: string) {
    const event = new MessageEvent(eventType || 'message', { data })

    if (eventType) {
      const listeners = this.listeners.get(eventType)
      if (listeners) {
        listeners.forEach((listener) => listener(event))
      }
    } else if (this.onmessage) {
      this.onmessage(event)
    }
  }

  simulateError() {
    this.readyState = MockEventSource.CLOSED
    if (this.onerror) {
      this.onerror(new Event('error'))
    }
  }
}

// Store mock instances for test access
let mockEventSourceInstances: MockEventSource[] = []

// Mock EventSource globally
beforeAll(() => {
  // @ts-ignore
  global.EventSource = jest.fn((url: string) => {
    const instance = new MockEventSource(url)
    mockEventSourceInstances.push(instance)
    return instance
  })
})

// Clear instances after each test
afterEach(() => {
  mockEventSourceInstances = []
  jest.clearAllMocks()
  jest.clearAllTimers()
})

// Use fake timers
beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.runOnlyPendingTimers()
  jest.useRealTimers()
})

describe('useSSEConnection', () => {
  describe('Initial State', () => {
    it('should start with disconnected status when no runId provided', () => {
      const { result } = renderHook(() => useSSEConnection(null))

      expect(result.current.connectionStatus).toBe('disconnected')
      expect(result.current.error).toBeNull()
      expect(result.current.isConnected).toBe(false)
      expect(result.current.state.run_id).toBeNull()
      expect(result.current.state.status).toBe('unknown')
    })

    it('should initialize with default pipeline state', () => {
      const { result } = renderHook(() => useSSEConnection(null))

      expect(result.current.state).toEqual({
        run_id: null,
        status: 'unknown',
        current_stage: 'unknown',
        awaiting_approval: false,
      })
    })

    it('should expose reconnect and disconnect methods', () => {
      const { result } = renderHook(() => useSSEConnection(null))

      expect(typeof result.current.reconnect).toBe('function')
      expect(typeof result.current.disconnect).toBe('function')
    })
  })

  describe('Connection Lifecycle', () => {
    it('should establish connection when runId is provided', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      // Should start connecting
      expect(result.current.connectionStatus).toBe('connecting')

      // Wait for connection to open
      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      await waitFor(() => {
        expect(result.current.connectionStatus).toBe('connected')
      })

      expect(result.current.isConnected).toBe(true)
      expect(result.current.error).toBeNull()
    })

    it('should build correct SSE endpoint URL', () => {
      renderHook(() => useSSEConnection('test-run-123'))

      expect(global.EventSource).toHaveBeenCalledWith(
        '/api/pipeline/test-run-123/stream'
      )
    })

    it('should use custom baseUrl from config', () => {
      renderHook(() =>
        useSSEConnection('test-run-123', { baseUrl: '/custom-api' })
      )

      expect(global.EventSource).toHaveBeenCalledWith(
        '/custom-api/pipeline/test-run-123/stream'
      )
    })

    it('should close connection when unmounted', async () => {
      const { unmount } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      const mockInstance = mockEventSourceInstances[0]
      expect(mockInstance.readyState).toBe(MockEventSource.OPEN)

      unmount()

      expect(mockInstance.readyState).toBe(MockEventSource.CLOSED)
    })

    it('should reconnect when runId changes', async () => {
      const { rerender } = renderHook(
        ({ runId }) => useSSEConnection(runId),
        { initialProps: { runId: 'run-1' } }
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(mockEventSourceInstances).toHaveLength(1)
      expect(mockEventSourceInstances[0].url).toContain('run-1')

      // Change runId
      rerender({ runId: 'run-2' })

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(mockEventSourceInstances).toHaveLength(2)
      expect(mockEventSourceInstances[1].url).toContain('run-2')
    })
  })

  describe('Event Handling', () => {
    it('should handle state_update event', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      const stateUpdate: StateUpdateEvent = {
        run_id: 'test-run-123',
        status: 'running',
        current_stage: 'level1_paradigm',
        timestamp: '2025-01-01T00:00:00Z',
      }

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          JSON.stringify(stateUpdate),
          'state_update'
        )
      })

      expect(result.current.state.status).toBe('running')
      expect(result.current.state.current_stage).toBe('level1_paradigm')
      expect(result.current.state.last_update).toBe('2025-01-01T00:00:00Z')
    })

    it('should handle status_change event', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      const statusChange: StatusChangeEvent = {
        run_id: 'test-run-123',
        status: 'completed',
        timestamp: '2025-01-01T00:01:00Z',
      }

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          JSON.stringify(statusChange),
          'status_change'
        )
      })

      expect(result.current.state.status).toBe('completed')
      expect(result.current.state.last_update).toBe('2025-01-01T00:01:00Z')
    })

    it('should handle stage_change event', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      const stageChange: StageChangeEvent = {
        run_id: 'test-run-123',
        stage: 'level2_technique',
        timestamp: '2025-01-01T00:02:00Z',
      }

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          JSON.stringify(stageChange),
          'stage_change'
        )
      })

      expect(result.current.state.current_stage).toBe('level2_technique')
      expect(result.current.state.last_update).toBe('2025-01-01T00:02:00Z')
    })

    it('should handle approval_required event', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      const approvalRequired: ApprovalRequiredEvent = {
        run_id: 'test-run-123',
        gate: 'paradigm_selection',
        stage: 'level1_paradigm',
        timestamp: '2025-01-01T00:03:00Z',
      }

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          JSON.stringify(approvalRequired),
          'approval_required'
        )
      })

      expect(result.current.state.awaiting_approval).toBe(true)
      expect(result.current.state.approval_gate).toBe('paradigm_selection')
      expect(result.current.state.current_stage).toBe('level1_paradigm')
    })

    it('should handle pipeline_finished event and close connection', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(result.current.connectionStatus).toBe('connected')

      const pipelineFinished: PipelineFinishedEvent = {
        run_id: 'test-run-123',
        status: 'completed',
        completed_at: '2025-01-01T00:10:00Z',
        timestamp: '2025-01-01T00:10:00Z',
      }

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          JSON.stringify(pipelineFinished),
          'pipeline_finished'
        )
      })

      expect(result.current.state.status).toBe('completed')
      expect(result.current.state.completed_at).toBe('2025-01-01T00:10:00Z')
      expect(result.current.connectionStatus).toBe('disconnected')
    })

    it('should handle error event', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      const errorEvent: ErrorEvent = {
        run_id: 'test-run-123',
        error: 'Pipeline execution failed',
        timestamp: '2025-01-01T00:05:00Z',
      }

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          JSON.stringify(errorEvent),
          'error'
        )
      })

      expect(result.current.state.error).toBe('Pipeline execution failed')
      expect(result.current.error).toBe('Pipeline execution failed')
    })

    it('should handle heartbeat event', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      const heartbeat = {
        run_id: 'test-run-123',
        timestamp: '2025-01-01T00:06:00Z',
      }

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          JSON.stringify(heartbeat),
          'heartbeat'
        )
      })

      expect(result.current.state.last_update).toBe('2025-01-01T00:06:00Z')
    })

    it('should handle malformed JSON gracefully', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation()

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      await act(async () => {
        mockEventSourceInstances[0].simulateMessage(
          'invalid json',
          'state_update'
        )
      })

      // State should remain unchanged
      expect(result.current.state.status).toBe('unknown')
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })
  })

  describe('Error Handling and Reconnection', () => {
    it('should set error status when connection fails', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      await act(async () => {
        mockEventSourceInstances[0].simulateError()
      })

      await waitFor(() => {
        expect(result.current.connectionStatus).toBe('disconnected')
      })
    })

    it('should attempt reconnection with exponential backoff', async () => {
      const { result } = renderHook(() =>
        useSSEConnection('test-run-123', {
          initialReconnectDelay: 1000,
          reconnectBackoffMultiplier: 2,
        })
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // Simulate first error
      await act(async () => {
        mockEventSourceInstances[0].simulateError()
      })

      expect(mockEventSourceInstances).toHaveLength(1)

      // First reconnection attempt (1000ms)
      await act(async () => {
        jest.advanceTimersByTime(1000)
      })

      expect(mockEventSourceInstances).toHaveLength(2)

      // Simulate second error
      await act(async () => {
        mockEventSourceInstances[1].simulateError()
      })

      // Second reconnection attempt (2000ms)
      await act(async () => {
        jest.advanceTimersByTime(2000)
      })

      expect(mockEventSourceInstances).toHaveLength(3)
    })

    it('should stop reconnecting after max attempts', async () => {
      const { result } = renderHook(() =>
        useSSEConnection('test-run-123', {
          maxReconnectAttempts: 3,
          initialReconnectDelay: 100,
        })
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // Simulate errors and reconnections
      for (let i = 0; i < 3; i++) {
        await act(async () => {
          mockEventSourceInstances[i].simulateError()
        })

        await act(async () => {
          jest.advanceTimersByTime(1000)
        })
      }

      // Final error after max attempts
      await act(async () => {
        mockEventSourceInstances[3].simulateError()
      })

      await act(async () => {
        jest.advanceTimersByTime(5000)
      })

      // Should not create more instances
      expect(mockEventSourceInstances).toHaveLength(4)
      expect(result.current.connectionStatus).toBe('error')
      expect(result.current.error).toContain('Failed to connect after 3 attempts')
    })

    it('should respect max reconnection delay', async () => {
      renderHook(() =>
        useSSEConnection('test-run-123', {
          initialReconnectDelay: 1000,
          maxReconnectDelay: 3000,
          reconnectBackoffMultiplier: 10, // Would normally grow very large
        })
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // First error
      await act(async () => {
        mockEventSourceInstances[0].simulateError()
      })

      // First reconnection (1000ms)
      await act(async () => {
        jest.advanceTimersByTime(1000)
      })

      // Second error
      await act(async () => {
        mockEventSourceInstances[1].simulateError()
      })

      // Second reconnection should be capped at 3000ms, not 10000ms
      await act(async () => {
        jest.advanceTimersByTime(2999)
      })

      expect(mockEventSourceInstances).toHaveLength(2)

      await act(async () => {
        jest.advanceTimersByTime(1)
      })

      expect(mockEventSourceInstances).toHaveLength(3)
    })

    it('should reset reconnection attempts on successful connection', async () => {
      const { result } = renderHook(() =>
        useSSEConnection('test-run-123', {
          initialReconnectDelay: 100,
        })
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // First error
      await act(async () => {
        mockEventSourceInstances[0].simulateError()
      })

      // Reconnect
      await act(async () => {
        jest.advanceTimersByTime(100)
      })

      // Successful connection
      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(result.current.connectionStatus).toBe('connected')

      // Second error
      await act(async () => {
        mockEventSourceInstances[1].simulateError()
      })

      // Should use initial delay again, not increased delay
      await act(async () => {
        jest.advanceTimersByTime(100)
      })

      expect(mockEventSourceInstances).toHaveLength(3)
    })
  })

  describe('Manual Control', () => {
    it('should allow manual reconnection', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(mockEventSourceInstances).toHaveLength(1)

      // Manual reconnect
      await act(async () => {
        result.current.reconnect()
      })

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(mockEventSourceInstances).toHaveLength(2)
    })

    it('should reset reconnection attempts on manual reconnect', async () => {
      const { result } = renderHook(() =>
        useSSEConnection('test-run-123', {
          maxReconnectAttempts: 2,
          initialReconnectDelay: 100,
        })
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // Exhaust reconnection attempts
      for (let i = 0; i < 2; i++) {
        await act(async () => {
          mockEventSourceInstances[i].simulateError()
        })

        await act(async () => {
          jest.advanceTimersByTime(1000)
        })
      }

      // Final error
      await act(async () => {
        mockEventSourceInstances[2].simulateError()
      })

      expect(result.current.connectionStatus).toBe('error')

      // Manual reconnect should reset attempts
      await act(async () => {
        result.current.reconnect()
      })

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(result.current.connectionStatus).toBe('connected')
    })

    it('should allow manual disconnection', async () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(result.current.connectionStatus).toBe('connected')

      await act(async () => {
        result.current.disconnect()
      })

      expect(result.current.connectionStatus).toBe('disconnected')
      expect(mockEventSourceInstances[0].readyState).toBe(MockEventSource.CLOSED)
    })

    it('should prevent automatic reconnection after manual disconnect', async () => {
      const { result } = renderHook(() =>
        useSSEConnection('test-run-123', {
          initialReconnectDelay: 100,
        })
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // Manual disconnect
      await act(async () => {
        result.current.disconnect()
      })

      // Wait for potential reconnection
      await act(async () => {
        jest.advanceTimersByTime(5000)
      })

      // Should not have created new connection
      expect(mockEventSourceInstances).toHaveLength(1)
    })
  })

  describe('Configuration', () => {
    it('should use default configuration values', () => {
      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      expect(global.EventSource).toHaveBeenCalledWith(
        '/api/pipeline/test-run-123/stream'
      )
    })

    it('should allow custom configuration', () => {
      renderHook(() =>
        useSSEConnection('test-run-123', {
          baseUrl: '/custom',
          maxReconnectAttempts: 10,
          initialReconnectDelay: 500,
          maxReconnectDelay: 60000,
          reconnectBackoffMultiplier: 1.5,
        })
      )

      expect(global.EventSource).toHaveBeenCalledWith(
        '/custom/pipeline/test-run-123/stream'
      )
    })

    it('should respect debug flag', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation()

      renderHook(() => useSSEConnection('test-run-123', { debug: true }))

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      expect(consoleSpy).toHaveBeenCalledWith(
        '[useSSEConnection]',
        expect.any(String),
        expect.anything()
      )

      consoleSpy.mockRestore()
    })
  })

  describe('Edge Cases', () => {
    it('should handle null runId gracefully', () => {
      const { result } = renderHook(() => useSSEConnection(null))

      expect(result.current.connectionStatus).toBe('disconnected')
      expect(global.EventSource).not.toHaveBeenCalled()
    })

    it('should handle empty string runId', () => {
      const { result } = renderHook(() => useSSEConnection(''))

      // Empty string is falsy, should not connect
      expect(result.current.connectionStatus).toBe('disconnected')
    })

    it('should handle rapid runId changes', async () => {
      const { rerender } = renderHook(
        ({ runId }) => useSSEConnection(runId),
        { initialProps: { runId: 'run-1' } }
      )

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // Rapidly change runId multiple times
      rerender({ runId: 'run-2' })
      rerender({ runId: 'run-3' })
      rerender({ runId: 'run-4' })

      await act(async () => {
        jest.advanceTimersByTime(50)
      })

      // Should have closed old connections and created new one
      expect(mockEventSourceInstances.length).toBeGreaterThan(1)
      expect(mockEventSourceInstances[mockEventSourceInstances.length - 1].url).toContain(
        'run-4'
      )
    })

    it('should handle connection that never opens', async () => {
      // Create a mock that never calls onopen
      class StuckEventSource extends MockEventSource {
        simulateOpen() {
          // Don't call onopen
          this.readyState = MockEventSource.CONNECTING
        }
      }

      // @ts-ignore
      global.EventSource = jest.fn((url: string) => {
        const instance = new StuckEventSource(url)
        mockEventSourceInstances.push(instance)
        return instance
      })

      const { result } = renderHook(() => useSSEConnection('test-run-123'))

      await act(async () => {
        jest.advanceTimersByTime(5000)
      })

      // Should remain in connecting state
      expect(result.current.connectionStatus).toBe('connecting')
    })
  })
})
