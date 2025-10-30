'use client';

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  HumanApprovalGatePanelProps,
  ApprovalAction,
  GateResponse,
  ACTION_BUTTON_CONFIGS,
  GATE_LEVEL_DESCRIPTIONS,
  CheckpointInfo,
  ApprovalRecord,
} from '@/types/approval';

/**
 * HumanApprovalGatePanel Component
 *
 * Provides a comprehensive UI for human-in-the-loop approval gates in the decomposition pipeline.
 * Allows users to approve, reject, modify, backtrack, add context, or request alternatives.
 */
export default function HumanApprovalGatePanel({
  runId,
  gateData,
  approvalHistory = [],
  checkpoints = [],
  onApprove,
  onReject,
  onModify,
  onBacktrack,
  onAddContext,
  onRequestAlternatives,
  isLoading = false,
  error,
}: HumanApprovalGatePanelProps) {
  // Dialog states
  const [activeDialog, setActiveDialog] = useState<ApprovalAction | null>(null);

  // Form states
  const [reviewer, setReviewer] = useState('');
  const [notes, setNotes] = useState('');
  const [additionalContext, setAdditionalContext] = useState('');
  const [modifications, setModifications] = useState('');
  const [selectedCheckpoint, setSelectedCheckpoint] = useState<string>('');
  const [alternativesRequirements, setAlternativesRequirements] = useState('');

  // Processing state
  const [isProcessing, setIsProcessing] = useState(false);

  // Reset form on dialog close
  const closeDialog = () => {
    setActiveDialog(null);
    setNotes('');
    setAdditionalContext('');
    setModifications('');
    setSelectedCheckpoint('');
    setAlternativesRequirements('');
  };

  // Handle action execution
  const handleAction = async (action: ApprovalAction) => {
    if (!reviewer.trim()) {
      alert('Please enter your name as reviewer');
      return;
    }

    setIsProcessing(true);

    try {
      const baseResponse: GateResponse = {
        action,
        reviewer: reviewer.trim(),
        notes: notes.trim() || undefined,
      };

      switch (action) {
        case 'approve':
          await onApprove?.(baseResponse);
          break;

        case 'reject':
          if (!notes.trim()) {
            alert('Please provide a reason for rejection');
            setIsProcessing(false);
            return;
          }
          await onReject?.({
            ...baseResponse,
            backtrack_to: selectedCheckpoint || undefined,
          });
          break;

        case 'modify':
          if (!modifications.trim()) {
            alert('Please provide modifications');
            setIsProcessing(false);
            return;
          }
          try {
            const parsedModifications = JSON.parse(modifications);
            await onModify?.({
              ...baseResponse,
              modifications: parsedModifications,
            });
          } catch (e) {
            alert('Invalid JSON format for modifications');
            setIsProcessing(false);
            return;
          }
          break;

        case 'backtrack':
          if (!selectedCheckpoint) {
            alert('Please select a checkpoint to backtrack to');
            setIsProcessing(false);
            return;
          }
          await onBacktrack?.({
            ...baseResponse,
            backtrack_to: selectedCheckpoint,
          });
          break;

        case 'add_context':
          if (!additionalContext.trim()) {
            alert('Please provide additional context');
            setIsProcessing(false);
            return;
          }
          await onAddContext?.({
            ...baseResponse,
            additional_context: additionalContext.trim(),
          });
          break;

        case 'request_alternatives':
          await onRequestAlternatives?.({
            ...baseResponse,
            additional_context: alternativesRequirements.trim() || undefined,
          });
          break;
      }

      closeDialog();
    } catch (error) {
      console.error('Error processing action:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Open dialog or execute action directly
  const initiateAction = (action: ApprovalAction) => {
    const config = ACTION_BUTTON_CONFIGS[action];

    if (config.requiresConfirmation || config.requiresInput) {
      setActiveDialog(action);
    } else {
      handleAction(action);
    }
  };

  // Render state snapshot based on gate level
  const renderStateSnapshot = () => {
    const snapshot = gateData.state_snapshot;
    const level = gateData.context.level;

    return (
      <div className="space-y-4">
        {level === 1 && snapshot.selected_paradigms && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Selected Paradigms</h4>
            <div className="flex flex-wrap gap-2">
              {snapshot.selected_paradigms.map((paradigm: string) => (
                <Badge key={paradigm} variant="secondary" className="capitalize">
                  {paradigm}
                  {snapshot.paradigm_scores?.[paradigm] && (
                    <span className="ml-2 text-xs">
                      {(snapshot.paradigm_scores[paradigm] * 100).toFixed(0)}%
                    </span>
                  )}
                </Badge>
              ))}
            </div>
            {snapshot.paradigm_reasoning && (
              <div className="mt-3 p-3 bg-muted/50 rounded-md text-sm">
                <p className="font-semibold mb-1">Reasoning:</p>
                <pre className="whitespace-pre-wrap text-xs">
                  {JSON.stringify(snapshot.paradigm_reasoning, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        {level === 2 && snapshot.selected_techniques && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Selected Techniques</h4>
            <div className="space-y-2">
              {Object.entries(snapshot.selected_techniques).map(([paradigm, technique]) => (
                <div key={paradigm} className="p-2 border rounded-md">
                  <p className="text-xs text-muted-foreground capitalize">{paradigm}</p>
                  <p className="font-medium text-sm">{String(technique)}</p>
                  {snapshot.technique_scores?.[String(technique)] && (
                    <Badge variant="outline" className="mt-1 text-xs">
                      Score: {(snapshot.technique_scores[String(technique)] * 100).toFixed(0)}%
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {level === 3 && snapshot.integrated_subproblems && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Integrated Subproblems</h4>
            <div className="space-y-2">
              {snapshot.integrated_subproblems.map((subproblem: any, idx: number) => (
                <div key={idx} className="p-2 border rounded-md text-sm">
                  <p className="font-medium">{subproblem.title || `Subproblem ${idx + 1}`}</p>
                  {subproblem.description && (
                    <p className="text-xs text-muted-foreground mt-1">{subproblem.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {level === 4 && snapshot.integrated_solution && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Integrated Solution</h4>
            <div className="p-3 bg-muted/50 rounded-md">
              <p className="text-sm whitespace-pre-wrap">
                {snapshot.integrated_solution.content || 'No solution content available'}
              </p>
              {snapshot.integrated_solution.confidence && (
                <Badge variant="outline" className="mt-2">
                  Confidence: {(snapshot.integrated_solution.confidence * 100).toFixed(0)}%
                </Badge>
              )}
            </div>
          </div>
        )}

        {Object.keys(snapshot).length === 0 && (
          <div className="text-sm text-muted-foreground italic">No snapshot data available</div>
        )}
      </div>
    );
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-4">
      {/* Error Display */}
      {error && (
        <Card className="border-destructive bg-destructive/10">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive font-medium">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      {/* Main Gate Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Approval Gate: {gateData.gate}</CardTitle>
              <CardDescription>
                {GATE_LEVEL_DESCRIPTIONS[gateData.context.level] || gateData.stage}
                {gateData.context.required && (
                  <Badge variant="destructive" className="ml-2">
                    Required
                  </Badge>
                )}
              </CardDescription>
            </div>
            <Badge variant="outline" className="text-lg px-4 py-2">
              Level {gateData.context.level}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Gate Description */}
          <div className="p-4 bg-muted/50 rounded-md">
            <p className="text-sm">{gateData.context.stage_description || gateData.context.description}</p>
          </div>

          {/* Reviewer Name Input */}
          <div className="space-y-2">
            <Label htmlFor="reviewer-name">Your Name (Reviewer)</Label>
            <Textarea
              id="reviewer-name"
              placeholder="Enter your name..."
              value={reviewer}
              onChange={(e) => setReviewer(e.target.value)}
              className="h-10"
              disabled={isLoading || isProcessing}
            />
          </div>

          {/* State Snapshot */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Current State</h3>
            {renderStateSnapshot()}
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">Actions</h3>

            {/* Primary Actions */}
            <div className="flex gap-2">
              <Button
                onClick={() => initiateAction('approve')}
                disabled={isLoading || isProcessing || !reviewer.trim()}
                className="flex-1"
                variant="default"
              >
                Approve
              </Button>
              <Button
                onClick={() => initiateAction('reject')}
                disabled={isLoading || isProcessing || !reviewer.trim()}
                className="flex-1"
                variant="destructive"
              >
                Reject
              </Button>
            </div>

            {/* Secondary Actions */}
            <div className="grid grid-cols-2 gap-2">
              <Button
                onClick={() => initiateAction('modify')}
                disabled={isLoading || isProcessing || !reviewer.trim()}
                variant="outline"
              >
                Modify
              </Button>
              <Button
                onClick={() => initiateAction('backtrack')}
                disabled={isLoading || isProcessing || !reviewer.trim()}
                variant="outline"
              >
                Backtrack
              </Button>
              <Button
                onClick={() => initiateAction('add_context')}
                disabled={isLoading || isProcessing || !reviewer.trim()}
                variant="secondary"
              >
                Add Context
              </Button>
              <Button
                onClick={() => initiateAction('request_alternatives')}
                disabled={isLoading || isProcessing || !reviewer.trim()}
                variant="secondary"
              >
                Request Alternatives
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Approval History */}
      {approvalHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Approval History</CardTitle>
            <CardDescription>Past decisions for this pipeline run</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {approvalHistory.map((record: ApprovalRecord, idx: number) => (
                <div key={idx} className="flex items-start gap-3 p-3 border rounded-md">
                  <Badge variant={record.action === 'approve' ? 'default' : 'secondary'} className="capitalize">
                    {record.action.replace('_', ' ')}
                  </Badge>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{record.gate_name}</p>
                    <p className="text-xs text-muted-foreground">
                      by {record.reviewer} on {new Date(record.timestamp * 1000).toLocaleString()}
                    </p>
                    {record.notes && <p className="text-sm mt-1">{record.notes}</p>}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Approve Dialog (simple confirmation) */}
      <Dialog open={activeDialog === 'approve'} onOpenChange={closeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Decision</DialogTitle>
            <DialogDescription>
              Are you sure you want to approve this decision and continue to the next stage?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="approve-notes">Notes (Optional)</Label>
              <Textarea
                id="approve-notes"
                placeholder="Add any notes about your approval..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog} disabled={isProcessing}>
              Cancel
            </Button>
            <Button onClick={() => handleAction('approve')} disabled={isProcessing}>
              {isProcessing ? 'Processing...' : 'Approve'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={activeDialog === 'reject'} onOpenChange={closeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Decision</DialogTitle>
            <DialogDescription>
              This will reject the current decision and optionally backtrack to a previous checkpoint.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="reject-reason">Reason for Rejection *</Label>
              <Textarea
                id="reject-reason"
                placeholder="Explain why you are rejecting this decision..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                required
              />
            </div>
            {checkpoints.length > 0 && (
              <div className="space-y-2">
                <Label htmlFor="reject-checkpoint">Backtrack to Checkpoint (Optional)</Label>
                <select
                  id="reject-checkpoint"
                  className="w-full p-2 border rounded-md"
                  value={selectedCheckpoint}
                  onChange={(e) => setSelectedCheckpoint(e.target.value)}
                >
                  <option value="">Current stage</option>
                  {checkpoints.map((cp: CheckpointInfo) => (
                    <option key={cp.checkpoint_id} value={cp.checkpoint_id}>
                      {cp.stage} - {new Date(cp.timestamp).toLocaleString()}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog} disabled={isProcessing}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => handleAction('reject')}
              disabled={isProcessing || !notes.trim()}
            >
              {isProcessing ? 'Processing...' : 'Reject'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modify Dialog */}
      <Dialog open={activeDialog === 'modify'} onOpenChange={closeDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Modify State</DialogTitle>
            <DialogDescription>
              Modify the current pipeline state. Provide modifications as JSON.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="modifications">Modifications (JSON) *</Label>
              <Textarea
                id="modifications"
                placeholder='{"key": "value"}'
                value={modifications}
                onChange={(e) => setModifications(e.target.value)}
                className="font-mono text-xs min-h-[200px]"
                required
              />
              <p className="text-xs text-muted-foreground">
                Enter valid JSON representing the state changes you want to make.
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="modify-notes">Notes (Optional)</Label>
              <Textarea
                id="modify-notes"
                placeholder="Explain your modifications..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog} disabled={isProcessing}>
              Cancel
            </Button>
            <Button
              onClick={() => handleAction('modify')}
              disabled={isProcessing || !modifications.trim()}
            >
              {isProcessing ? 'Processing...' : 'Apply Modifications'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Backtrack Dialog */}
      <Dialog open={activeDialog === 'backtrack'} onOpenChange={closeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Backtrack to Checkpoint</DialogTitle>
            <DialogDescription>
              Select a checkpoint to return to. This will restore the pipeline state to that point.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {checkpoints.length > 0 ? (
              <div className="space-y-2">
                <Label htmlFor="backtrack-checkpoint">Select Checkpoint *</Label>
                <select
                  id="backtrack-checkpoint"
                  className="w-full p-2 border rounded-md"
                  value={selectedCheckpoint}
                  onChange={(e) => setSelectedCheckpoint(e.target.value)}
                >
                  <option value="">-- Select a checkpoint --</option>
                  {checkpoints.map((cp: CheckpointInfo) => (
                    <option key={cp.checkpoint_id} value={cp.checkpoint_id}>
                      {cp.stage} - {new Date(cp.timestamp).toLocaleString()}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No checkpoints available for backtracking.</p>
            )}
            <div className="space-y-2">
              <Label htmlFor="backtrack-reason">Reason (Optional)</Label>
              <Textarea
                id="backtrack-reason"
                placeholder="Why are you backtracking?"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog} disabled={isProcessing}>
              Cancel
            </Button>
            <Button
              onClick={() => handleAction('backtrack')}
              disabled={isProcessing || !selectedCheckpoint}
            >
              {isProcessing ? 'Processing...' : 'Backtrack'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Context Dialog */}
      <Dialog open={activeDialog === 'add_context'} onOpenChange={closeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Context</DialogTitle>
            <DialogDescription>
              Provide additional context that will be used to reprocess from the current or specified stage.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="additional-context">Additional Context *</Label>
              <Textarea
                id="additional-context"
                placeholder="Provide additional context, requirements, or constraints..."
                value={additionalContext}
                onChange={(e) => setAdditionalContext(e.target.value)}
                className="min-h-[150px]"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="context-notes">Notes (Optional)</Label>
              <Textarea
                id="context-notes"
                placeholder="Any notes about this context addition..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog} disabled={isProcessing}>
              Cancel
            </Button>
            <Button
              onClick={() => handleAction('add_context')}
              disabled={isProcessing || !additionalContext.trim()}
            >
              {isProcessing ? 'Processing...' : 'Add Context'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Request Alternatives Dialog */}
      <Dialog open={activeDialog === 'request_alternatives'} onOpenChange={closeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Request Alternatives</DialogTitle>
            <DialogDescription>
              Request alternative solutions or approaches to the current decision.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="alternatives-requirements">Requirements (Optional)</Label>
              <Textarea
                id="alternatives-requirements"
                placeholder="Specify requirements or constraints for alternatives..."
                value={alternativesRequirements}
                onChange={(e) => setAlternativesRequirements(e.target.value)}
                className="min-h-[120px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="alternatives-notes">Notes (Optional)</Label>
              <Textarea
                id="alternatives-notes"
                placeholder="Any additional notes..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog} disabled={isProcessing}>
              Cancel
            </Button>
            <Button onClick={() => handleAction('request_alternatives')} disabled={isProcessing}>
              {isProcessing ? 'Processing...' : 'Request Alternatives'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
