'use client'

import React, { useState, useEffect } from 'react'
import { DashboardNavigation, DashboardView } from './DashboardNavigation'
import { PipelineStatusBar, PipelineStage } from './PipelineStatusBar'
import { cn } from '@/lib/utils'

interface DashboardLayoutProps {
  children: React.ReactNode
  currentView?: DashboardView
  pipelineStages?: PipelineStage[]
  className?: string
}

const defaultPipelineStages: PipelineStage[] = [
  {
    id: 'input',
    name: 'Problem Input',
    status: 'complete',
    startTime: new Date(Date.now() - 300000),
    endTime: new Date(Date.now() - 240000),
    duration: 60000
  },
  {
    id: 'paradigm',
    name: 'Paradigm Selection',
    status: 'complete',
    startTime: new Date(Date.now() - 240000),
    endTime: new Date(Date.now() - 180000),
    duration: 60000
  },
  {
    id: 'technique',
    name: 'Technique Selection',
    status: 'active',
    startTime: new Date(Date.now() - 180000)
  },
  {
    id: 'decomposition',
    name: 'Decomposition',
    status: 'pending'
  },
  {
    id: 'execution',
    name: 'Execution',
    status: 'pending'
  },
  {
    id: 'integration',
    name: 'Integration',
    status: 'pending'
  },
  {
    id: 'output',
    name: 'Output',
    status: 'pending'
  }
]

export function DashboardLayout({
  children,
  currentView,
  pipelineStages = defaultPipelineStages,
  className
}: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Handle responsive behavior
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768
      setIsMobile(mobile)
      if (mobile && !sidebarCollapsed) {
        setSidebarCollapsed(true)
      }
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const handleToggleSidebar = () => {
    setSidebarCollapsed((prev) => !prev)
  }

  return (
    <div className={cn('flex flex-col h-screen bg-gray-50 dark:bg-gray-950', className)}>
      {/* Pipeline Status Bar - Always visible at top */}
      <header className="sticky top-0 z-40 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                Decomposition Pipeline
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Real-time control center
              </p>
            </div>
            {currentView && (
              <div className="text-right">
                <div className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  Current View
                </div>
                <div className="text-lg font-semibold text-blue-600 dark:text-blue-400 capitalize">
                  {currentView.replace(/-/g, ' ')}
                </div>
              </div>
            )}
          </div>
          <PipelineStatusBar stages={pipelineStages} showTimestamps={true} />
        </div>
      </header>

      {/* Main content area with sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Navigation */}
        <aside
          className={cn(
            'flex-shrink-0 transition-all duration-300',
            isMobile && !sidebarCollapsed && 'absolute inset-y-0 left-0 z-30 shadow-xl'
          )}
        >
          <DashboardNavigation
            collapsed={sidebarCollapsed}
            onToggleCollapse={handleToggleSidebar}
          />
        </aside>

        {/* Mobile overlay when sidebar is open */}
        {isMobile && !sidebarCollapsed && (
          <div
            className="fixed inset-0 bg-black/50 z-20"
            onClick={handleToggleSidebar}
            aria-label="Close sidebar"
          />
        )}

        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <div className="h-full">{children}</div>
        </main>
      </div>
    </div>
  )
}
