'use client'

import React from 'react'
import Link from 'next/link'
import { useSearchParams, usePathname } from 'next/navigation'
import {
  FileText,
  Target,
  Wrench,
  GitBranch,
  Users,
  AlertTriangle,
  CheckCircle,
  FileOutput,
  ChevronLeft,
  ChevronRight,
  Menu
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

export type DashboardView =
  | 'problem-input'
  | 'paradigm-selection'
  | 'technique-selection'
  | 'decomposition-graph'
  | 'agent-pool'
  | 'integration-conflicts'
  | 'approval-gates'
  | 'solution-output'

interface NavigationItem {
  id: DashboardView
  label: string
  icon: React.ElementType
  description: string
}

const navigationItems: NavigationItem[] = [
  {
    id: 'problem-input',
    label: 'Problem Input',
    icon: FileText,
    description: 'Define the problem to solve'
  },
  {
    id: 'paradigm-selection',
    label: 'Paradigm Selection',
    icon: Target,
    description: 'Choose decomposition paradigms'
  },
  {
    id: 'technique-selection',
    label: 'Technique Selection',
    icon: Wrench,
    description: 'Select algorithmic techniques'
  },
  {
    id: 'decomposition-graph',
    label: 'Decomposition Graph',
    icon: GitBranch,
    description: 'View subproblem structure'
  },
  {
    id: 'agent-pool',
    label: 'Agent Pool Monitor',
    icon: Users,
    description: 'Monitor agent activity'
  },
  {
    id: 'integration-conflicts',
    label: 'Integration Conflicts',
    icon: AlertTriangle,
    description: 'Resolve integration issues'
  },
  {
    id: 'approval-gates',
    label: 'Approval Gates',
    icon: CheckCircle,
    description: 'Human approval checkpoints'
  },
  {
    id: 'solution-output',
    label: 'Solution Output',
    icon: FileOutput,
    description: 'Final solution output'
  }
]

interface DashboardNavigationProps {
  collapsed: boolean
  onToggleCollapse: () => void
  className?: string
}

export function DashboardNavigation({
  collapsed,
  onToggleCollapse,
  className
}: DashboardNavigationProps) {
  const searchParams = useSearchParams()
  const pathname = usePathname()
  const currentView = searchParams.get('view') as DashboardView | null

  return (
    <nav
      className={cn(
        'flex flex-col h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Menu className="w-5 h-5 text-blue-600" />
            <h2 className="font-semibold text-sm">Navigation</h2>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
          className={cn('p-2', collapsed && 'mx-auto')}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </Button>
      </div>

      {/* Navigation Items */}
      <div className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.id

            return (
              <li key={item.id}>
                <Link
                  href={`/dashboard?view=${item.id}`}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors duration-200',
                    'hover:bg-gray-100 dark:hover:bg-gray-800',
                    isActive && 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
                    !isActive && 'text-gray-700 dark:text-gray-300',
                    collapsed && 'justify-center'
                  )}
                  title={collapsed ? item.label : undefined}
                >
                  <Icon
                    className={cn(
                      'w-5 h-5 flex-shrink-0',
                      isActive && 'text-blue-600 dark:text-blue-400'
                    )}
                  />
                  {!collapsed && (
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{item.label}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {item.description}
                      </div>
                    </div>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </div>

      {/* Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-800">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            <div className="font-medium mb-1">Pipeline Status</div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span>Active</span>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
