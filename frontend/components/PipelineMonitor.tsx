'use client'

import React from 'react'
import { useSSEConnection } from '@/hooks/useSSEConnection'
import {
  Activity,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  WifiOff,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface PipelineMonitorProps {
  runId: string | null
  className?: string
  onApprovalRequired?: (gate: string) => void
}

/**
 * Example component demonstrating usage of useSSEConnection hook
 *
 * Monitors a pipeline run in real-time using Server-Sent Events
 */
export function PipelineMonitor({
  runId,
  className,
  onApprovalRequired,
}: PipelineMonitorProps) {
  const { state, connectionStatus, error, reconnect, disconnect, isConnected } =
    useSSEConnection(runId, {
      debug: process.env.NODE_ENV === 'development',
    })

  // Trigger approval callback when needed
  React.useEffect(() => {
    if (state.awaiting_approval && state.approval_gate && onApprovalRequired) {
      onApprovalRequired(state.approval_gate)
    }
  }, [state.awaiting_approval, state.approval_gate, onApprovalRequired])

  // Connection status indicator
  const ConnectionBadge = () => {
    const statusConfig = {
      disconnected: {
        icon: WifiOff,
        label: 'Disconnected',
        className: 'bg-gray-100 text-gray-700',
      },
      connecting: {
        icon: Loader2,
        label: 'Connecting',
        className: 'bg-yellow-100 text-yellow-700',
      },
      connected: {
        icon: Zap,
        label: 'Live',
        className: 'bg-green-100 text-green-700',
      },
      error: {
        icon: XCircle,
        label: 'Error',
        className: 'bg-red-100 text-red-700',
      },
    }

    const config = statusConfig[connectionStatus]
    const Icon = config.icon

    return (
      <Badge variant="outline" className={cn('flex items-center gap-1', config.className)}>
        <Icon
          className={cn('w-3 h-3', connectionStatus === 'connecting' && 'animate-spin')}
        />
        {config.label}
      </Badge>
    )
  }

  // Pipeline status indicator
  const PipelineStatusBadge = () => {
    const statusConfig = {
      unknown: { icon: Activity, label: 'Unknown', color: 'gray' },
      pending: { icon: Activity, label: 'Pending', color: 'blue' },
      running: { icon: Loader2, label: 'Running', color: 'blue' },
      completed: { icon: CheckCircle2, label: 'Completed', color: 'green' },
      failed: { icon: XCircle, label: 'Failed', color: 'red' },
      cancelled: { icon: XCircle, label: 'Cancelled', color: 'gray' },
    }

    const config = statusConfig[state.status] || statusConfig.unknown
    const Icon = config.icon

    return (
      <div className="flex items-center gap-2">
        <Icon
          className={cn(
            'w-5 h-5',
            config.color === 'blue' && 'text-blue-500',
            config.color === 'green' && 'text-green-500',
            config.color === 'red' && 'text-red-500',
            config.color === 'gray' && 'text-gray-500',
            state.status === 'running' && 'animate-spin'
          )}
        />
        <span className="font-semibold">{config.label}</span>
      </div>
    )
  }

  // Format stage name for display
  const formatStage = (stage: string): string => {
    return stage
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  if (!runId) {
    return (
      <Card className={cn('p-6', className)}>
        <div className="text-center text-gray-500">
          <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No pipeline run selected</p>
        </div>
      </Card>
    )
  }

  return (
    <Card className={cn('p-6 space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Pipeline Monitor
          </h2>
          <p className="text-sm text-gray-600 mt-1">Run ID: {runId}</p>
        </div>
        <ConnectionBadge />
      </div>

      {/* Connection Error */}
      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-red-900">Connection Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
            <Button onClick={reconnect} size="sm" variant="outline">
              Retry
            </Button>
          </div>
        </div>
      )}

      {/* Pipeline Status */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">Status</span>
          <PipelineStatusBadge />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-600">Current Stage</span>
          <span className="font-semibold">{formatStage(state.current_stage)}</span>
        </div>

        {state.last_update && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Last Update</span>
            <span className="text-sm">
              {new Date(state.last_update).toLocaleTimeString()}
            </span>
          </div>
        )}

        {state.completed_at && (
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Completed At</span>
            <span className="text-sm">
              {new Date(state.completed_at).toLocaleString()}
            </span>
          </div>
        )}
      </div>

      {/* Approval Required */}
      {state.awaiting_approval && (
        <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-900">Approval Required</h3>
              <p className="text-sm text-yellow-700 mt-1">
                The pipeline is waiting for approval at gate: {state.approval_gate}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* State Error */}
      {state.error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4">
          <div className="flex items-start gap-3">
            <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-red-900">Pipeline Error</h3>
              <p className="text-sm text-red-700 mt-1">{state.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Connection Controls */}
      <div className="flex gap-2 pt-4 border-t">
        <Button onClick={reconnect} variant="outline" size="sm" disabled={isConnected}>
          Reconnect
        </Button>
        <Button onClick={disconnect} variant="outline" size="sm" disabled={!isConnected}>
          Disconnect
        </Button>
      </div>
    </Card>
  )
}
