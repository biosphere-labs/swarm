'use client'

import React from 'react'
import {
  CheckCircle2,
  Circle,
  XCircle,
  Loader2,
  PauseCircle
} from 'lucide-react'
import { cn, formatDuration } from '@/lib/utils'

export type PipelineStageStatus =
  | 'active'
  | 'complete'
  | 'failed'
  | 'pending'
  | 'waiting_approval'

export interface PipelineStage {
  id: string
  name: string
  status: PipelineStageStatus
  startTime?: Date
  endTime?: Date
  duration?: number
}

interface PipelineStatusBarProps {
  stages: PipelineStage[]
  showTimestamps?: boolean
  className?: string
}

interface StageIndicatorProps {
  stage: PipelineStage
  isLast: boolean
  showTimestamp?: boolean
}

function StageIndicator({ stage, isLast, showTimestamp }: StageIndicatorProps) {
  const getIcon = () => {
    switch (stage.status) {
      case 'complete':
        return <CheckCircle2 className="w-6 h-6 text-green-500" />
      case 'active':
        return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />
      case 'waiting_approval':
        return <PauseCircle className="w-6 h-6 text-orange-500" />
      case 'pending':
      default:
        return <Circle className="w-6 h-6 text-gray-300" />
    }
  }

  const getIndicatorClasses = () => {
    const baseClasses = 'relative flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300'

    switch (stage.status) {
      case 'complete':
        return cn(baseClasses, 'bg-green-50 border-green-500 dark:bg-green-900/20')
      case 'active':
        return cn(baseClasses, 'bg-blue-50 border-blue-500 dark:bg-blue-900/20 animate-pulse-slow')
      case 'failed':
        return cn(baseClasses, 'bg-red-50 border-red-500 dark:bg-red-900/20')
      case 'waiting_approval':
        return cn(baseClasses, 'bg-orange-50 border-orange-500 dark:bg-orange-900/20')
      case 'pending':
      default:
        return cn(baseClasses, 'bg-gray-50 border-gray-300 dark:bg-gray-800')
    }
  }

  const getConnectorClasses = () => {
    const baseClasses = 'absolute left-full top-1/2 -translate-y-1/2 h-0.5 transition-all duration-500'

    switch (stage.status) {
      case 'complete':
        return cn(baseClasses, 'bg-green-500')
      case 'active':
        return cn(baseClasses, 'bg-blue-500 animate-pulse')
      default:
        return cn(baseClasses, 'bg-gray-200 dark:bg-gray-700')
    }
  }

  const getDuration = () => {
    if (stage.duration) {
      return formatDuration(stage.duration)
    }
    if (stage.startTime && stage.endTime) {
      const duration = stage.endTime.getTime() - stage.startTime.getTime()
      return formatDuration(duration)
    }
    if (stage.startTime && stage.status === 'active') {
      const duration = Date.now() - stage.startTime.getTime()
      return formatDuration(duration)
    }
    return null
  }

  return (
    <div className="relative flex flex-col items-center">
      {/* Stage Indicator */}
      <div className={getIndicatorClasses()}>
        {getIcon()}

        {/* Connector Line (hidden for last stage) */}
        {!isLast && (
          <div
            className={getConnectorClasses()}
            style={{ width: 'calc(100% + 2rem)' }}
          />
        )}
      </div>

      {/* Stage Name */}
      <div className="mt-3 text-center">
        <p className={cn(
          'text-sm font-medium transition-colors duration-300',
          stage.status === 'active' ? 'text-blue-600 dark:text-blue-400' :
          stage.status === 'complete' ? 'text-green-600 dark:text-green-400' :
          stage.status === 'failed' ? 'text-red-600 dark:text-red-400' :
          stage.status === 'waiting_approval' ? 'text-orange-600 dark:text-orange-400' :
          'text-gray-500 dark:text-gray-400'
        )}>
          {stage.name}
        </p>

        {/* Optional Duration/Timestamp */}
        {showTimestamp && getDuration() && (
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            {getDuration()}
          </p>
        )}
      </div>
    </div>
  )
}

export function PipelineStatusBar({
  stages,
  showTimestamps = true,
  className
}: PipelineStatusBarProps) {
  return (
    <div className={cn('w-full', className)}>
      {/* Desktop/Tablet: Horizontal Layout */}
      <div className="hidden md:flex md:items-start md:justify-between md:gap-8 md:px-4">
        {stages.map((stage, index) => (
          <div key={stage.id} className="flex-1 flex flex-col items-center">
            <StageIndicator
              stage={stage}
              isLast={index === stages.length - 1}
              showTimestamp={showTimestamps}
            />
          </div>
        ))}
      </div>

      {/* Mobile: Vertical Layout */}
      <div className="md:hidden space-y-6">
        {stages.map((stage, index) => (
          <div key={stage.id} className="flex items-start gap-4">
            <div className="relative">
              <StageIndicator
                stage={stage}
                isLast={index === stages.length - 1}
                showTimestamp={showTimestamps}
              />

              {/* Vertical Connector for Mobile */}
              {index < stages.length - 1 && (
                <div
                  className={cn(
                    'absolute left-1/2 top-full -translate-x-1/2 w-0.5 h-6 transition-all duration-500',
                    stage.status === 'complete' ? 'bg-green-500' :
                    stage.status === 'active' ? 'bg-blue-500 animate-pulse' :
                    'bg-gray-200 dark:bg-gray-700'
                  )}
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
