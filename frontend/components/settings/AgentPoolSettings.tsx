/**
 * Agent Pool Settings Component
 * Configure agent pools for different pipeline stages
 */

import React from 'react';
import { useSettingsStore } from '@/lib/settings-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

interface PoolConfigCardProps {
  poolName: string;
  displayName: string;
  description: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
}

export function AgentPoolSettings() {
  const { settings, updateAgentPool, validationErrors } = useSettingsStore();
  const { agentPools } = settings;

  const getFieldError = (field: string) => {
    return validationErrors.find((err) => err.field === field);
  };

  const getPriorityBadge = (priority?: string) => {
    switch (priority) {
      case 'critical':
        return <Badge variant="destructive" className="text-xs">Critical</Badge>;
      case 'high':
        return <Badge variant="default" className="text-xs">High</Badge>;
      case 'medium':
        return <Badge variant="outline" className="text-xs">Medium</Badge>;
      case 'low':
        return <Badge variant="outline" className="text-xs">Low</Badge>;
      default:
        return null;
    }
  };

  const poolConfigs: PoolConfigCardProps[] = [
    {
      poolName: 'paradigmSelection',
      displayName: 'Paradigm Selection Pool',
      description: 'Evaluates and selects appropriate problem-solving paradigms',
      priority: 'high',
    },
    {
      poolName: 'techniqueSelection',
      displayName: 'Technique Selection Pool',
      description: 'Identifies and ranks relevant techniques for each paradigm',
      priority: 'high',
    },
    {
      poolName: 'decomposition',
      displayName: 'Decomposition Pool',
      description: 'Breaks down problems into manageable subproblems',
      priority: 'critical',
    },
    {
      poolName: 'execution',
      displayName: 'Execution Pool',
      description: 'Executes solutions for individual subproblems',
      priority: 'critical',
    },
    {
      poolName: 'integration',
      displayName: 'Integration Pool',
      description: 'Integrates and synthesizes partial solutions',
      priority: 'medium',
    },
  ];

  const PoolConfigCard = ({ poolName, displayName, description, priority }: PoolConfigCardProps) => {
    const pool = agentPools[poolName];
    if (!pool) return null;

    const sizeError = getFieldError(`agentPools.${poolName}.size`);
    const priorityError = getFieldError(`agentPools.${poolName}.priority`);
    const concurrentError = getFieldError(`agentPools.${poolName}.maxConcurrent`);

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{displayName}</CardTitle>
            {getPriorityBadge(priority)}
          </div>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Enabled Toggle */}
          <div className="flex items-center justify-between">
            <Label htmlFor={`${poolName}-enabled`}>Enable Pool</Label>
            <Switch
              id={`${poolName}-enabled`}
              checked={pool.enabled}
              onCheckedChange={(checked) =>
                updateAgentPool(poolName, { enabled: checked })
              }
            />
          </div>

          {/* Pool Size */}
          <div className="space-y-2">
            <Label htmlFor={`${poolName}-size`}>Pool Size</Label>
            <Input
              id={`${poolName}-size`}
              type="number"
              min="1"
              max="100"
              value={pool.size}
              onChange={(e) =>
                updateAgentPool(poolName, { size: parseInt(e.target.value, 10) })
              }
              disabled={!pool.enabled}
              className={sizeError ? 'border-red-500' : ''}
            />
            {sizeError && (
              <p className="text-sm text-red-500">{sizeError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Number of agents in this pool (1-100)
            </p>
          </div>

          {/* Priority */}
          <div className="space-y-2">
            <Label htmlFor={`${poolName}-priority`}>Priority Level</Label>
            <Input
              id={`${poolName}-priority`}
              type="number"
              min="1"
              max="10"
              value={pool.priority}
              onChange={(e) =>
                updateAgentPool(poolName, { priority: parseInt(e.target.value, 10) })
              }
              disabled={!pool.enabled}
              className={priorityError ? 'border-red-500' : ''}
            />
            {priorityError && (
              <p className="text-sm text-red-500">{priorityError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Execution priority (1-10, higher is more important)
            </p>
          </div>

          {/* Max Concurrent */}
          <div className="space-y-2">
            <Label htmlFor={`${poolName}-concurrent`}>Max Concurrent Executions</Label>
            <Input
              id={`${poolName}-concurrent`}
              type="number"
              min="1"
              max={pool.size}
              value={pool.maxConcurrent}
              onChange={(e) =>
                updateAgentPool(poolName, { maxConcurrent: parseInt(e.target.value, 10) })
              }
              disabled={!pool.enabled}
              className={concurrentError ? 'border-red-500' : ''}
            />
            {concurrentError && (
              <p className="text-sm text-red-500">{concurrentError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Maximum simultaneous executions (1-{pool.size})
            </p>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Agent Pool Configuration</h2>
        <p className="text-muted-foreground">
          Configure size, priority, and concurrency for agent pools
        </p>
      </div>

      {/* Pool Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Pool Statistics</CardTitle>
          <CardDescription>
            Overview of all agent pools
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Total Pools</p>
              <p className="text-2xl font-bold">{Object.keys(agentPools).length}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Active Pools</p>
              <p className="text-2xl font-bold">
                {Object.values(agentPools).filter((p) => p.enabled).length}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Total Agents</p>
              <p className="text-2xl font-bold">
                {Object.values(agentPools).reduce((sum, p) => sum + (p.enabled ? p.size : 0), 0)}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Max Concurrent</p>
              <p className="text-2xl font-bold">
                {Object.values(agentPools).reduce(
                  (sum, p) => sum + (p.enabled ? p.maxConcurrent : 0),
                  0
                )}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Individual Pool Configurations */}
      <div className="space-y-4">
        {poolConfigs.map((config) => (
          <PoolConfigCard key={config.poolName} {...config} />
        ))}
      </div>
    </div>
  );
}
