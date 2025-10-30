'use client'

import React, { useState, useEffect } from 'react'
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Circle,
  Loader2,
  Users,
  Clock,
  ListTodo,
  Zap
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

// SSE Connection States
export type SSEConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error'

// Pool Metrics Interface
export interface PoolMetrics {
  pool_name: string
  total_agents: number
  active_agents: number
  idle_agents: number
  stuck_agents: number
  total_tasks_completed: number
  average_response_time: number
  current_queue_size: number
  timestamp: string
}

// Agent Pool Monitor Props
interface AgentPoolMonitorProps {
  apiEndpoint?: string
  refreshInterval?: number
  className?: string
}

// Pool Type Classification
const POOL_TYPES = {
  paradigm: [
    'structural',
    'functional',
    'temporal',
    'spatial',
    'hierarchical',
    'computational',
    'data',
    'dependency'
  ],
  domain: ['api_design', 'data_processing', 'ml_modeling', 'security'],
  general: ['general']
}

// Color mapping for pool types
const POOL_TYPE_COLORS: Record<string, string> = {
  structural: '#3b82f6',
  functional: '#10b981',
  temporal: '#8b5cf6',
  spatial: '#f59e0b',
  hierarchical: '#ec4899',
  computational: '#14b8a6',
  data: '#f97316',
  dependency: '#6366f1',
  api_design: '#06b6d4',
  data_processing: '#84cc16',
  ml_modeling: '#a855f7',
  security: '#f43f5e',
  general: '#64748b'
}

// Format response time for display
function formatResponseTime(seconds: number): string {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`
  }
  return `${seconds.toFixed(2)}s`
}

// Calculate utilization percentage
function calculateUtilization(active: number, total: number): number {
  if (total === 0) return 0
  return Math.round((active / total) * 100)
}

// Connection Status Badge Component
function ConnectionStatusBadge({ state }: { state: SSEConnectionState }) {
  const config = {
    disconnected: {
      icon: Circle,
      label: 'Disconnected',
      className: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
    },
    connecting: {
      icon: Loader2,
      label: 'Connecting',
      className: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400'
    },
    connected: {
      icon: CheckCircle2,
      label: 'Connected',
      className: 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
    },
    error: {
      icon: AlertCircle,
      label: 'Error',
      className: 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
    }
  }

  const { icon: Icon, label, className } = config[state]

  return (
    <Badge variant="outline" className={cn('flex items-center gap-1', className)}>
      <Icon className={cn('w-3 h-3', state === 'connecting' && 'animate-spin')} />
      {label}
    </Badge>
  )
}

// Pool Card Component
function PoolCard({ pool, type }: { pool: PoolMetrics; type: 'paradigm' | 'domain' | 'general' }) {
  const utilization = calculateUtilization(pool.active_agents, pool.total_agents)
  const color = POOL_TYPE_COLORS[pool.pool_name] || '#64748b'

  return (
    <Card className="p-4 hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: color }}
            />
            <h3 className="font-semibold text-sm capitalize">
              {pool.pool_name.replace(/_/g, ' ')}
            </h3>
          </div>
          <Badge variant="outline" className="text-xs">
            {type === 'paradigm' ? 'Paradigm' : type === 'domain' ? 'Domain' : 'General'}
          </Badge>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold">{utilization}%</div>
          <div className="text-xs text-gray-500">utilization</div>
        </div>
      </div>

      {/* Agent Status */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="flex items-center gap-1">
          <Zap className="w-4 h-4 text-blue-500" />
          <div>
            <div className="text-xs text-gray-500">Active</div>
            <div className="font-semibold">{pool.active_agents}</div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Circle className="w-4 h-4 text-gray-400" />
          <div>
            <div className="text-xs text-gray-500">Idle</div>
            <div className="font-semibold">{pool.idle_agents}</div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <AlertCircle className="w-4 h-4 text-red-500" />
          <div>
            <div className="text-xs text-gray-500">Stuck</div>
            <div className="font-semibold">{pool.stuck_agents}</div>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-1 pt-3 border-t">
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1 text-gray-600">
            <Users className="w-3 h-3" />
            Total Agents
          </span>
          <span className="font-semibold">{pool.total_agents}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1 text-gray-600">
            <ListTodo className="w-3 h-3" />
            Queue Size
          </span>
          <span className="font-semibold">{pool.current_queue_size}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1 text-gray-600">
            <CheckCircle2 className="w-3 h-3" />
            Completed
          </span>
          <span className="font-semibold">{pool.total_tasks_completed}</span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1 text-gray-600">
            <Clock className="w-3 h-3" />
            Avg Response
          </span>
          <span className="font-semibold">{formatResponseTime(pool.average_response_time)}</span>
        </div>
      </div>
    </Card>
  )
}

// Utilization Bar Chart Component
function UtilizationChart({ pools }: { pools: PoolMetrics[] }) {
  const chartData = pools.map((pool) => ({
    name: pool.pool_name.replace(/_/g, ' '),
    active: pool.active_agents,
    idle: pool.idle_agents,
    stuck: pool.stuck_agents,
    utilization: calculateUtilization(pool.active_agents, pool.total_agents)
  }))

  return (
    <Card className="p-4">
      <h3 className="text-lg font-semibold mb-4">Pool Utilization Overview</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 100 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="name"
            stroke="#6b7280"
            style={{ fontSize: '11px' }}
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Legend />
          <Bar dataKey="active" stackId="a" fill="#3b82f6" name="Active" />
          <Bar dataKey="idle" stackId="a" fill="#9ca3af" name="Idle" />
          <Bar dataKey="stuck" stackId="a" fill="#ef4444" name="Stuck" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}

// Main Agent Pool Monitor Component
export function AgentPoolMonitor({
  apiEndpoint = '/api/agent-pools',
  refreshInterval = 2000,
  className
}: AgentPoolMonitorProps) {
  const [connectionState, setConnectionState] = useState<SSEConnectionState>('disconnected')
  const [pools, setPools] = useState<Map<string, PoolMetrics>>(new Map())
  const [error, setError] = useState<string | null>(null)

  // Initialize with default pool data
  useEffect(() => {
    const initializePools = () => {
      const initialPools = new Map<string, PoolMetrics>()

      // Initialize paradigm pools
      POOL_TYPES.paradigm.forEach((name) => {
        initialPools.set(name, {
          pool_name: name,
          total_agents: 50,
          active_agents: 0,
          idle_agents: 50,
          stuck_agents: 0,
          total_tasks_completed: 0,
          average_response_time: 0,
          current_queue_size: 0,
          timestamp: new Date().toISOString()
        })
      })

      // Initialize domain pools
      POOL_TYPES.domain.forEach((name) => {
        const size = name === 'ml_modeling' || name === 'security' ? 20 : 30
        initialPools.set(name, {
          pool_name: name,
          total_agents: size,
          active_agents: 0,
          idle_agents: size,
          stuck_agents: 0,
          total_tasks_completed: 0,
          average_response_time: 0,
          current_queue_size: 0,
          timestamp: new Date().toISOString()
        })
      })

      // Initialize general pool
      initialPools.set('general', {
        pool_name: 'general',
        total_agents: 10,
        active_agents: 0,
        idle_agents: 10,
        stuck_agents: 0,
        total_tasks_completed: 0,
        average_response_time: 0,
        current_queue_size: 0,
        timestamp: new Date().toISOString()
      })

      setPools(initialPools)
    }

    initializePools()
  }, [])

  // Fetch pool data via HTTP polling (SSE fallback)
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null

    const fetchPoolData = async () => {
      try {
        setConnectionState('connecting')
        const response = await fetch(`${apiEndpoint}/metrics`)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()

        // Update pools with fetched data
        setPools((prevPools) => {
          const newPools = new Map(prevPools)

          // data could be an array or an object with pool names as keys
          if (Array.isArray(data)) {
            data.forEach((poolData: PoolMetrics) => {
              newPools.set(poolData.pool_name, poolData)
            })
          } else if (typeof data === 'object' && data !== null) {
            Object.entries(data).forEach(([name, poolData]) => {
              newPools.set(name, poolData as PoolMetrics)
            })
          }

          return newPools
        })

        setConnectionState('connected')
        setError(null)
      } catch (err) {
        console.error('Error fetching pool data:', err)
        setConnectionState('error')
        setError(err instanceof Error ? err.message : 'Failed to fetch pool data')
      }
    }

    // Initial fetch
    fetchPoolData()

    // Set up polling
    intervalId = setInterval(fetchPoolData, refreshInterval)

    // Cleanup
    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [apiEndpoint, refreshInterval])

  // Organize pools by type
  const paradigmPools = Array.from(pools.values()).filter((p) =>
    POOL_TYPES.paradigm.includes(p.pool_name)
  )
  const domainPools = Array.from(pools.values()).filter((p) =>
    POOL_TYPES.domain.includes(p.pool_name)
  )
  const generalPools = Array.from(pools.values()).filter((p) =>
    POOL_TYPES.general.includes(p.pool_name)
  )

  // Calculate summary stats
  const totalAgents = Array.from(pools.values()).reduce((sum, p) => sum + p.total_agents, 0)
  const totalActive = Array.from(pools.values()).reduce((sum, p) => sum + p.active_agents, 0)
  const totalIdle = Array.from(pools.values()).reduce((sum, p) => sum + p.idle_agents, 0)
  const totalStuck = Array.from(pools.values()).reduce((sum, p) => sum + p.stuck_agents, 0)

  return (
    <div className={cn('w-full space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Activity className="w-6 h-6" />
            Agent Pool Monitor
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Real-time monitoring of {pools.size} agent pools
          </p>
        </div>
        <ConnectionStatusBadge state={connectionState} />
      </div>

      {/* Error Alert */}
      {error && (
        <Card className="p-4 border-red-200 bg-red-50 dark:bg-red-900/10">
          <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
            <AlertCircle className="w-5 h-5" />
            <div>
              <p className="font-semibold">Connection Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Users className="w-4 h-4" />
            <span className="text-sm">Total Agents</span>
          </div>
          <div className="text-2xl font-bold">{totalAgents}</div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-2 text-blue-600 mb-1">
            <Zap className="w-4 h-4" />
            <span className="text-sm">Active</span>
          </div>
          <div className="text-2xl font-bold text-blue-600">{totalActive}</div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Circle className="w-4 h-4" />
            <span className="text-sm">Idle</span>
          </div>
          <div className="text-2xl font-bold">{totalIdle}</div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-2 text-red-600 mb-1">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">Stuck</span>
          </div>
          <div className="text-2xl font-bold text-red-600">{totalStuck}</div>
        </Card>
      </div>

      {/* Utilization Chart */}
      <UtilizationChart pools={Array.from(pools.values())} />

      {/* Paradigm Pools */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Paradigm Pools (8)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {paradigmPools.map((pool) => (
            <PoolCard key={pool.pool_name} pool={pool} type="paradigm" />
          ))}
        </div>
      </div>

      {/* Domain Pools */}
      <div>
        <h3 className="text-xl font-semibold mb-4">Domain Pools (4)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {domainPools.map((pool) => (
            <PoolCard key={pool.pool_name} pool={pool} type="domain" />
          ))}
        </div>
      </div>

      {/* General Pool */}
      <div>
        <h3 className="text-xl font-semibold mb-4">General Pool (1)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {generalPools.map((pool) => (
            <PoolCard key={pool.pool_name} pool={pool} type="general" />
          ))}
        </div>
      </div>
    </div>
  )
}
