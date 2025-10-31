/**
 * Pipeline Settings Component
 * Configure core pipeline execution parameters
 */

import React from 'react';
import { useSettingsStore } from '@/lib/settings-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';

export function PipelineSettings() {
  const { settings, updatePipelineConfig, validationErrors } = useSettingsStore();
  const { pipeline } = settings;

  const getFieldError = (field: string) => {
    return validationErrors.find((err) => err.field === field);
  };

  const handleNumberChange = (field: keyof typeof pipeline, value: string) => {
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue)) {
      updatePipelineConfig({ [field]: numValue });
    }
  };

  const handleToggle = (field: keyof typeof pipeline) => {
    updatePipelineConfig({ [field]: !pipeline[field] });
  };

  const maxParadigmsError = getFieldError('pipeline.maxParadigms');
  const techniqueDiversityError = getFieldError('pipeline.techniqueDiversity');
  const decompositionDepthError = getFieldError('pipeline.decompositionDepth');
  const timeoutError = getFieldError('pipeline.timeout');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Pipeline Configuration</h2>
        <p className="text-muted-foreground">
          Configure core pipeline behavior and execution parameters
        </p>
      </div>

      {/* Selection Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Selection Parameters</CardTitle>
          <CardDescription>
            Control paradigm and technique selection behavior
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Max Paradigms */}
          <div className="space-y-2">
            <Label htmlFor="maxParadigms">Maximum Paradigms</Label>
            <Input
              id="maxParadigms"
              type="number"
              min="1"
              max="20"
              value={pipeline.maxParadigms}
              onChange={(e) => handleNumberChange('maxParadigms', e.target.value)}
              className={maxParadigmsError ? 'border-red-500' : ''}
            />
            {maxParadigmsError && (
              <p className="text-sm text-red-500">{maxParadigmsError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Maximum number of paradigms to select per problem (1-20)
            </p>
          </div>

          {/* Technique Diversity */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="techniqueDiversity">Technique Diversity Threshold</Label>
              <span className="text-sm text-muted-foreground">{pipeline.techniqueDiversity}%</span>
            </div>
            <Input
              id="techniqueDiversity"
              type="number"
              min="0"
              max="100"
              value={pipeline.techniqueDiversity}
              onChange={(e) => handleNumberChange('techniqueDiversity', e.target.value)}
              className={techniqueDiversityError ? 'border-red-500' : ''}
            />
            {techniqueDiversityError && (
              <p className="text-sm text-red-500">{techniqueDiversityError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Minimum diversity score for technique selection (0-100)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Decomposition Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Decomposition Parameters</CardTitle>
          <CardDescription>
            Configure problem decomposition behavior
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Decomposition Depth */}
          <div className="space-y-2">
            <Label htmlFor="decompositionDepth">Maximum Decomposition Depth</Label>
            <Input
              id="decompositionDepth"
              type="number"
              min="1"
              max="10"
              value={pipeline.decompositionDepth}
              onChange={(e) => handleNumberChange('decompositionDepth', e.target.value)}
              className={decompositionDepthError ? 'border-red-500' : ''}
            />
            {decompositionDepthError && (
              <p className="text-sm text-red-500">{decompositionDepthError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Maximum depth of the decomposition tree (1-10)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Execution Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Execution Parameters</CardTitle>
          <CardDescription>
            Configure execution timeouts and retry behavior
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Timeout */}
          <div className="space-y-2">
            <Label htmlFor="timeout">Pipeline Timeout (seconds)</Label>
            <Input
              id="timeout"
              type="number"
              min="10"
              max="3600"
              value={pipeline.timeout}
              onChange={(e) => handleNumberChange('timeout', e.target.value)}
              className={timeoutError ? 'border-red-500' : ''}
            />
            {timeoutError && (
              <p className="text-sm text-red-500">{timeoutError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Maximum time for entire pipeline execution (10-3600 seconds)
            </p>
          </div>

          {/* Retry Attempts */}
          <div className="space-y-2">
            <Label htmlFor="retryAttempts">Retry Attempts</Label>
            <Input
              id="retryAttempts"
              type="number"
              min="0"
              max="10"
              value={pipeline.retryAttempts}
              onChange={(e) => handleNumberChange('retryAttempts', e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Number of retry attempts on failure (0-10)
            </p>
          </div>

          {/* Retry Delay */}
          <div className="space-y-2">
            <Label htmlFor="retryDelay">Retry Delay (seconds)</Label>
            <Input
              id="retryDelay"
              type="number"
              min="0"
              max="60"
              value={pipeline.retryDelay}
              onChange={(e) => handleNumberChange('retryDelay', e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              Delay between retry attempts (0-60 seconds)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Performance Optimizations */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Optimizations</CardTitle>
          <CardDescription>
            Enable or disable performance features
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Parallel Execution */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="parallelExecution">Parallel Execution</Label>
              <p className="text-sm text-muted-foreground">
                Execute independent subproblems in parallel
              </p>
            </div>
            <Switch
              id="parallelExecution"
              checked={pipeline.enableParallelExecution}
              onCheckedChange={() => handleToggle('enableParallelExecution')}
            />
          </div>

          {/* Caching */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="caching">Result Caching</Label>
              <p className="text-sm text-muted-foreground">
                Cache intermediate results to avoid recomputation
              </p>
            </div>
            <Switch
              id="caching"
              checked={pipeline.enableCaching}
              onCheckedChange={() => handleToggle('enableCaching')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Current Configuration Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Configuration Summary</CardTitle>
          <CardDescription>
            Overview of current pipeline settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Max Paradigms</p>
              <p className="text-xl font-bold">{pipeline.maxParadigms}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Diversity Threshold</p>
              <p className="text-xl font-bold">{pipeline.techniqueDiversity}%</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Max Depth</p>
              <p className="text-xl font-bold">{pipeline.decompositionDepth}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Timeout</p>
              <p className="text-xl font-bold">{pipeline.timeout}s</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Retry Attempts</p>
              <p className="text-xl font-bold">{pipeline.retryAttempts}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Optimizations</p>
              <p className="text-xl font-bold">
                {[pipeline.enableParallelExecution && 'Parallel', pipeline.enableCaching && 'Cache']
                  .filter(Boolean)
                  .join(', ') || 'None'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
