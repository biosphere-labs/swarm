'use client';

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  SubproblemConflict,
  ConflictResolution,
  ResolutionStrategy,
  IntegrationConflictViewerProps,
  ConflictStatistics,
} from '@/types/integration';
import { Subproblem } from '@/types/decomposition';

export default function IntegrationConflictViewer({
  conflicts,
  onResolve,
  onReject,
  readOnly = false,
  className = '',
}: IntegrationConflictViewerProps) {
  const [selectedConflictId, setSelectedConflictId] = useState<string | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<Record<string, ResolutionStrategy>>(
    {}
  );
  const [manualDescriptions, setManualDescriptions] = useState<Record<string, string>>({});

  // Compute statistics
  const statistics = useMemo<ConflictStatistics>(() => {
    const total = conflicts.length;
    const resolved = conflicts.filter((c) => c.status === 'resolved').length;
    const pending = conflicts.filter((c) => c.status === 'pending').length;
    const rejected = conflicts.filter((c) => c.status === 'rejected').length;

    const byParadigm: Record<string, number> = {};
    conflicts.forEach((conflict) => {
      conflict.paradigms.forEach((paradigm) => {
        byParadigm[paradigm] = (byParadigm[paradigm] || 0) + 1;
      });
    });

    const averageSimilarity =
      conflicts.length > 0
        ? conflicts.reduce((sum, c) => sum + c.similarity.combined, 0) / conflicts.length
        : 0;

    return { total, resolved, pending, rejected, byParadigm, averageSimilarity };
  }, [conflicts]);

  const handleStrategySelect = (conflictId: string, strategy: ResolutionStrategy) => {
    setSelectedStrategy((prev) => ({ ...prev, [conflictId]: strategy }));
  };

  const handleResolve = (conflict: SubproblemConflict) => {
    const strategy = selectedStrategy[conflict.id];
    if (!strategy) return;

    if (strategy === 'manual' && !manualDescriptions[conflict.id]?.trim()) {
      alert('Please provide a description for manual resolution');
      return;
    }

    const resolution: ConflictResolution = {
      conflictId: conflict.id,
      strategy,
      resolvedAt: new Date().toISOString(),
      resolvedBy: 'user',
      customDescription: strategy === 'manual' ? manualDescriptions[conflict.id] : undefined,
    };

    onResolve?.(conflict.id, resolution);

    // Clear selections
    setSelectedStrategy((prev) => {
      const newState = { ...prev };
      delete newState[conflict.id];
      return newState;
    });
    setManualDescriptions((prev) => {
      const newState = { ...prev };
      delete newState[conflict.id];
      return newState;
    });
  };

  const handleReject = (conflictId: string) => {
    onReject?.(conflictId);
  };

  const getStrategyOptions = (conflict: SubproblemConflict): ResolutionStrategy[] => {
    const samePar = conflict.paradigms.length === 1 || new Set(conflict.paradigms).size === 1;

    if (samePar) {
      return ['merge', 'keep_both', 'discard_first', 'discard_second', 'manual'];
    } else {
      return ['multiview', 'keep_both', 'discard_first', 'discard_second', 'manual'];
    }
  };

  const getStrategyLabel = (strategy: ResolutionStrategy): string => {
    const labels: Record<ResolutionStrategy, string> = {
      merge: 'Merge',
      multiview: 'Multi-View',
      keep_both: 'Keep Both',
      discard_first: 'Discard First',
      discard_second: 'Discard Second',
      manual: 'Manual Resolution',
    };
    return labels[strategy];
  };

  const getStrategyDescription = (strategy: ResolutionStrategy, conflict: SubproblemConflict): string => {
    const first = conflict.subproblems[0]?.title || 'first';
    const second = conflict.subproblems[1]?.title || 'second';
    const descriptions: Record<ResolutionStrategy, string> = {
      merge: 'Combine subproblems into a single merged subproblem (recommended for same paradigm)',
      multiview: 'Create a multi-view subproblem preserving different perspectives (recommended for different paradigms)',
      keep_both: 'Keep both subproblems as separate entities',
      discard_first: 'Discard "' + first + '" and keep "' + second + '"',
      discard_second: 'Discard "' + second + '" and keep "' + first + '"',
      manual: 'Provide custom resolution description',
    };
    return descriptions[strategy];
  };

  if (conflicts.length === 0) {
    return (
      <div className={'w-full ' + className}>
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            No conflicts detected. All subproblems are compatible.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={'w-full space-y-4 ' + className}>
      {/* Statistics Card */}
      <Card>
        <CardHeader>
          <CardTitle>Conflict Overview</CardTitle>
          <CardDescription>
            Summary of detected conflicts in the integration phase
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-1">
              <div className="text-2xl font-bold">{statistics.total}</div>
              <div className="text-xs text-muted-foreground">Total Conflicts</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-orange-600">{statistics.pending}</div>
              <div className="text-xs text-muted-foreground">Pending</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-green-600">{statistics.resolved}</div>
              <div className="text-xs text-muted-foreground">Resolved</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-red-600">{statistics.rejected}</div>
              <div className="text-xs text-muted-foreground">Rejected</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-sm font-semibold">Average Similarity</div>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500"
                  style={{ width: (statistics.averageSimilarity * 100) + '%' }}
                />
              </div>
              <span className="text-sm font-mono">{(statistics.averageSimilarity * 100).toFixed(1)}%</span>
            </div>
          </div>

          {Object.keys(statistics.byParadigm).length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-semibold">Conflicts by Paradigm</div>
              <div className="flex flex-wrap gap-1">
                {Object.entries(statistics.byParadigm).map(([paradigm, count]) => (
                  <Badge key={paradigm} variant="secondary" className="capitalize">
                    {paradigm}: {count}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Conflicts List */}
      <div className="space-y-4">
        {conflicts.map((conflict) => (
          <Card
            key={conflict.id}
            className={
              selectedConflictId === conflict.id
                ? 'border-blue-500 shadow-md'
                : conflict.status === 'resolved'
                ? 'border-green-500'
                : conflict.status === 'rejected'
                ? 'border-red-500'
                : ''
            }
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">Conflict: {conflict.id}</CardTitle>
                  <CardDescription>
                    {conflict.subproblems.length} conflicting subproblems detected
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Badge
                    variant={
                      conflict.status === 'resolved'
                        ? 'default'
                        : conflict.status === 'rejected'
                        ? 'destructive'
                        : 'secondary'
                    }
                    className="capitalize"
                  >
                    {conflict.status}
                  </Badge>
                  {conflict.recommendedStrategy && (
                    <Badge variant="outline" className="capitalize">
                      Recommended: {getStrategyLabel(conflict.recommendedStrategy)}
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Similarity Metrics */}
              <div className="space-y-2">
                <div className="text-sm font-semibold">Similarity Metrics</div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {conflict.similarity.jaccard !== undefined && (
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground">Jaccard</div>
                      <SimilarityBar value={conflict.similarity.jaccard} />
                    </div>
                  )}
                  {conflict.similarity.cosine !== undefined && (
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground">Cosine</div>
                      <SimilarityBar value={conflict.similarity.cosine} />
                    </div>
                  )}
                  {conflict.similarity.structural !== undefined && (
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground">Structural</div>
                      <SimilarityBar value={conflict.similarity.structural} />
                    </div>
                  )}
                  <div className="space-y-1">
                    <div className="text-xs text-muted-foreground">Combined</div>
                    <SimilarityBar value={conflict.similarity.combined} highlighted />
                  </div>
                </div>
              </div>

              {/* Paradigms */}
              <div className="space-y-2">
                <div className="text-sm font-semibold">Paradigms Involved</div>
                <div className="flex flex-wrap gap-1">
                  {conflict.paradigms.map((paradigm) => (
                    <Badge key={paradigm} variant="secondary" className="capitalize">
                      {paradigm}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Subproblems Comparison */}
              <div className="space-y-2">
                <div className="text-sm font-semibold">Conflicting Subproblems</div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {conflict.subproblems.map((subproblem, idx) => (
                    <SubproblemCard key={subproblem.id} subproblem={subproblem} index={idx + 1} />
                  ))}
                </div>
              </div>

              {/* Resolution Options */}
              {!readOnly && conflict.status === 'pending' && (
                <div className="space-y-4 pt-4 border-t">
                  <div className="text-sm font-semibold">Resolution Strategy</div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {getStrategyOptions(conflict).map((strategy) => (
                      <Button
                        key={strategy}
                        variant={
                          selectedStrategy[conflict.id] === strategy ? 'default' : 'outline'
                        }
                        className="justify-start text-left h-auto py-3"
                        onClick={() => handleStrategySelect(conflict.id, strategy)}
                      >
                        <div className="space-y-1">
                          <div className="font-semibold">{getStrategyLabel(strategy)}</div>
                          <div className="text-xs opacity-80 font-normal">
                            {getStrategyDescription(strategy, conflict)}
                          </div>
                        </div>
                      </Button>
                    ))}
                  </div>

                  {selectedStrategy[conflict.id] === 'manual' && (
                    <div className="space-y-2">
                      <Label htmlFor={'manual-desc-' + conflict.id}>Resolution Description</Label>
                      <Textarea
                        id={'manual-desc-' + conflict.id}
                        placeholder="Describe how you want to resolve this conflict..."
                        value={manualDescriptions[conflict.id] || ''}
                        onChange={(e) =>
                          setManualDescriptions((prev) => ({
                            ...prev,
                            [conflict.id]: e.target.value,
                          }))
                        }
                        className="min-h-[100px]"
                      />
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleResolve(conflict)}
                      disabled={!selectedStrategy[conflict.id]}
                      className="flex-1"
                    >
                      Apply Resolution
                    </Button>
                    <Button variant="outline" onClick={() => handleReject(conflict.id)}>
                      Reject Conflict
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// Helper component for similarity progress bar
function SimilarityBar({ value, highlighted = false }: { value: number; highlighted?: boolean }) {
  const percentage = value * 100;
  const color = value >= 0.8 ? 'bg-red-500' : value >= 0.6 ? 'bg-orange-500' : 'bg-blue-500';

  return (
    <div className="space-y-1">
      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={highlighted ? 'h-full bg-purple-500' : 'h-full ' + color}
          style={{ width: percentage + '%' }}
        />
      </div>
      <div className="text-xs font-mono">{percentage.toFixed(1)}%</div>
    </div>
  );
}

// Helper component for subproblem card
function SubproblemCard({ subproblem, index }: { subproblem: Subproblem; index: number }) {
  return (
    <div className="border rounded-lg p-4 space-y-2 bg-muted/30">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-xs text-muted-foreground">Subproblem {index}</div>
          <div className="font-semibold">{subproblem.title}</div>
          <div className="text-xs text-muted-foreground mt-1">ID: {subproblem.id}</div>
        </div>
        <Badge variant="secondary" className="capitalize">
          {subproblem.paradigm}
        </Badge>
      </div>

      {subproblem.description && (
        <div className="text-sm text-muted-foreground">{subproblem.description}</div>
      )}

      {subproblem.technique && (
        <div className="text-xs">
          <span className="text-muted-foreground">Technique:</span>{' '}
          <span className="font-mono">{subproblem.technique}</span>
        </div>
      )}

      {subproblem.confidence !== undefined && (
        <div className="text-xs">
          <span className="text-muted-foreground">Confidence:</span>{' '}
          <span className="font-mono">{(subproblem.confidence * 100).toFixed(0)}%</span>
        </div>
      )}

      {subproblem.complexity && (
        <Badge variant="outline" className="text-xs capitalize">
          {subproblem.complexity} complexity
        </Badge>
      )}
    </div>
  );
}
