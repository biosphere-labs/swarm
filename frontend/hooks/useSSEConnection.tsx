'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  SSEConnectionStatus,
  PipelineState,
  SSEConnectionConfig,
  UseSSEConnectionReturn,
  DEFAULT_PIPELINE_STATE,
  DEFAULT_SSE_CONFIG,
  SSEEventType,
  StateUpdateEvent,
  StatusChangeEvent,
  StageChangeEvent,
  ApprovalRequiredEvent,
  PipelineFinishedEvent,
  ErrorEvent,
} from '@/types/sse'

/**
 * React hook for managing Server-Sent Events (SSE) connection to backend pipeline
 *
 * Handles connection lifecycle, automatic reconnection with exponential backoff,
 * event parsing, and state management.
 *
 * @param runId - Pipeline run ID to monitor
 * @param config - Optional connection configuration
 * @returns Hook interface with state, status, and control methods
 *
 * @example
 * ```tsx
 * const { state, connectionStatus, error, reconnect } = useSSEConnection('run-123');
 *
 * if (connectionStatus === 'connected') {
 *   console.log('Pipeline status:', state.status);
 *   console.log('Current stage:', state.current_stage);
 * }
 * ```
 */
export function useSSEConnection(
  runId: string | null,
  config?: SSEConnectionConfig
): UseSSEConnectionReturn {
  // Merge config with defaults
  const fullConfig = { ...DEFAULT_SSE_CONFIG, ...config }

  // State management
  const [state, setState] = useState<PipelineState>(DEFAULT_PIPELINE_STATE)
  const [connectionStatus, setConnectionStatus] = useState<SSEConnectionStatus>('disconnected')
  const [error, setError] = useState<string | null>(null)

  // Refs for connection management
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef<number>(0)
  const reconnectDelayRef = useRef<number>(fullConfig.initialReconnectDelay)
  const shouldReconnectRef = useRef<boolean>(true)

  /**
   * Log debug messages if debug mode is enabled
   */
  const log = useCallback(
    (...args: any[]) => {
      if (fullConfig.debug) {
        console.log('[useSSEConnection]', ...args)
      }
    },
    [fullConfig.debug]
  )

  /**
   * Log error messages
   */
  const logError = useCallback((...args: any[]) => {
    console.error('[useSSEConnection]', ...args)
  }, [])

  /**
   * Parse SSE event data
   */
  const parseEventData = useCallback(
    (data: string): any => {
      try {
        return JSON.parse(data)
      } catch (err) {
        logError('Failed to parse event data:', data, err)
        return null
      }
    },
    [logError]
  )

  /**
   * Update pipeline state based on event
   */
  const updateState = useCallback(
    (eventType: SSEEventType, eventData: any) => {
      log('Received event:', eventType, eventData)

      setState((prevState) => {
        const newState = { ...prevState }

        switch (eventType) {
          case 'state_update': {
            const data = eventData as StateUpdateEvent
            newState.run_id = data.run_id
            newState.status = data.status
            newState.current_stage = data.current_stage
            newState.last_update = data.timestamp
            break
          }

          case 'status_change': {
            const data = eventData as StatusChangeEvent
            newState.status = data.status
            newState.last_update = data.timestamp
            break
          }

          case 'stage_change': {
            const data = eventData as StageChangeEvent
            newState.current_stage = data.stage
            newState.last_update = data.timestamp
            break
          }

          case 'approval_required': {
            const data = eventData as ApprovalRequiredEvent
            newState.awaiting_approval = true
            newState.approval_gate = data.gate
            newState.current_stage = data.stage
            newState.last_update = data.timestamp
            break
          }

          case 'pipeline_finished': {
            const data = eventData as PipelineFinishedEvent
            newState.status = data.status
            newState.completed_at = data.completed_at
            newState.last_update = data.timestamp
            break
          }

          case 'error': {
            const data = eventData as ErrorEvent
            newState.error = data.error
            newState.last_update = data.timestamp
            setError(data.error)
            break
          }

          case 'heartbeat': {
            // Just update timestamp
            newState.last_update = eventData.timestamp
            break
          }

          default:
            log('Unknown event type:', eventType)
        }

        return newState
      })
    },
    [log]
  )

  /**
   * Close existing connection
   */
  const closeConnection = useCallback(() => {
    if (eventSourceRef.current) {
      log('Closing SSE connection')
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
  }, [log])

  /**
   * Attempt to reconnect with exponential backoff
   */
  const scheduleReconnect = useCallback(() => {
    if (!shouldReconnectRef.current) {
      log('Reconnection disabled, not scheduling')
      return
    }

    if (reconnectAttemptsRef.current >= fullConfig.maxReconnectAttempts) {
      logError(
        `Max reconnection attempts (${fullConfig.maxReconnectAttempts}) reached`
      )
      setConnectionStatus('error')
      setError(`Failed to connect after ${fullConfig.maxReconnectAttempts} attempts`)
      return
    }

    const delay = Math.min(
      reconnectDelayRef.current,
      fullConfig.maxReconnectDelay
    )

    log(
      `Scheduling reconnection attempt ${reconnectAttemptsRef.current + 1} in ${delay}ms`
    )

    reconnectTimeoutRef.current = setTimeout(() => {
      reconnectAttemptsRef.current += 1
      reconnectDelayRef.current *= fullConfig.reconnectBackoffMultiplier
      connect()
    }, delay)
  }, [fullConfig, log, logError])

  /**
   * Establish SSE connection
   */
  const connect = useCallback(() => {
    if (!runId) {
      log('No run ID provided, skipping connection')
      return
    }

    // Close existing connection
    closeConnection()

    // Build URL
    const url = `${fullConfig.baseUrl}/pipeline/${runId}/stream`
    log('Connecting to SSE endpoint:', url)

    setConnectionStatus('connecting')
    setError(null)

    try {
      // Create EventSource
      const eventSource = new EventSource(url)
      eventSourceRef.current = eventSource

      // Handle connection open
      eventSource.onopen = () => {
        log('SSE connection established')
        setConnectionStatus('connected')
        setError(null)
        reconnectAttemptsRef.current = 0
        reconnectDelayRef.current = fullConfig.initialReconnectDelay

        // Initialize state with run ID
        setState((prev) => ({ ...prev, run_id: runId }))
      }

      // Handle generic messages
      eventSource.onmessage = (event) => {
        log('Received generic message:', event.data)
        const data = parseEventData(event.data)
        if (data) {
          updateState('state_update', data)
        }
      }

      // Handle connection errors
      eventSource.onerror = (event) => {
        logError('SSE connection error:', event)

        // Check if this is a connection failure or just a disconnect
        if (eventSource.readyState === EventSource.CONNECTING) {
          log('Connection is attempting to reconnect automatically')
          setConnectionStatus('connecting')
        } else if (eventSource.readyState === EventSource.CLOSED) {
          log('Connection closed')
          setConnectionStatus('disconnected')
          closeConnection()
          scheduleReconnect()
        } else {
          setConnectionStatus('error')
          setError('Connection error occurred')
          closeConnection()
          scheduleReconnect()
        }
      }

      // Register event listeners for specific event types
      const eventTypes: SSEEventType[] = [
        'state_update',
        'status_change',
        'stage_change',
        'approval_required',
        'pipeline_finished',
        'heartbeat',
        'error',
      ]

      eventTypes.forEach((eventType) => {
        eventSource.addEventListener(eventType, (event: Event) => {
          const messageEvent = event as MessageEvent
          const data = parseEventData(messageEvent.data)
          if (data) {
            updateState(eventType, data)

            // If pipeline finished, close connection
            if (eventType === 'pipeline_finished') {
              log('Pipeline finished, closing connection')
              shouldReconnectRef.current = false
              closeConnection()
              setConnectionStatus('disconnected')
            }
          }
        })
      })
    } catch (err) {
      logError('Failed to create EventSource:', err)
      setConnectionStatus('error')
      setError(err instanceof Error ? err.message : 'Failed to connect')
      scheduleReconnect()
    }
  }, [
    runId,
    fullConfig,
    log,
    logError,
    closeConnection,
    parseEventData,
    updateState,
    scheduleReconnect,
  ])

  /**
   * Manual reconnect function
   */
  const reconnect = useCallback(() => {
    log('Manual reconnect triggered')
    shouldReconnectRef.current = true
    reconnectAttemptsRef.current = 0
    reconnectDelayRef.current = fullConfig.initialReconnectDelay
    connect()
  }, [fullConfig, log, connect])

  /**
   * Manual disconnect function
   */
  const disconnect = useCallback(() => {
    log('Manual disconnect triggered')
    shouldReconnectRef.current = false
    closeConnection()
    setConnectionStatus('disconnected')
  }, [log, closeConnection])

  /**
   * Connect on mount or when runId changes
   */
  useEffect(() => {
    if (runId) {
      shouldReconnectRef.current = true
      connect()
    }

    // Cleanup on unmount or runId change
    return () => {
      log('Cleaning up SSE connection')
      shouldReconnectRef.current = false
      closeConnection()
    }
  }, [runId, connect, closeConnection, log])

  return {
    state,
    connectionStatus,
    error,
    reconnect,
    disconnect,
    isConnected: connectionStatus === 'connected',
  }
}
