/**
 * Approval Gate Settings Component
 * Configure HITL approval gates for different pipeline levels
 */

import React from 'react';
import { useSettingsStore } from '@/lib/settings-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

export function ApprovalGateSettings() {
  const { settings, updateApprovalGates, validationErrors } = useSettingsStore();
  const { approvalGates } = settings;

  const getFieldError = (field: string) => {
    return validationErrors.find((err) => err.field === field);
  };

  const handleToggle = (field: keyof typeof approvalGates) => {
    updateApprovalGates({ [field]: !approvalGates[field] });
  };

  const handleNumberChange = (field: keyof typeof approvalGates, value: string) => {
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue)) {
      updateApprovalGates({ [field]: numValue });
    }
  };

  const timeoutError = getFieldError('approvalGates.defaultTimeout');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Approval Gate Configuration</h2>
        <p className="text-muted-foreground">
          Configure human-in-the-loop approval gates for different pipeline levels
        </p>
      </div>

      {/* Level Gates */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Level Gates</CardTitle>
          <CardDescription>
            Enable or disable approval gates for specific pipeline levels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Level 1 - Paradigm Selection */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label htmlFor="level1">Level 1 - Paradigm Selection</Label>
                <Badge variant="outline" className="text-xs">
                  Optional
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Approve selected problem-solving paradigms before proceeding
              </p>
            </div>
            <Switch
              id="level1"
              checked={approvalGates.level1Enabled}
              onCheckedChange={() => handleToggle('level1Enabled')}
            />
          </div>

          {/* Level 2 - Technique Selection */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label htmlFor="level2">Level 2 - Technique Selection</Label>
                <Badge variant="default" className="text-xs">
                  Recommended
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Review and approve selected techniques for each paradigm
              </p>
            </div>
            <Switch
              id="level2"
              checked={approvalGates.level2Enabled}
              onCheckedChange={() => handleToggle('level2Enabled')}
            />
          </div>

          {/* Level 3 - Decomposition */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label htmlFor="level3">Level 3 - Problem Decomposition</Label>
                <Badge variant="outline" className="text-xs">
                  Optional
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Verify problem decomposition tree before execution
              </p>
            </div>
            <Switch
              id="level3"
              checked={approvalGates.level3Enabled}
              onCheckedChange={() => handleToggle('level3Enabled')}
            />
          </div>

          {/* Level 4 - Execution */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Label htmlFor="level4">Level 4 - Solution Execution</Label>
                <Badge variant="default" className="text-xs">
                  Critical
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Review and approve solutions before integration
              </p>
            </div>
            <Switch
              id="level4"
              checked={approvalGates.level4Enabled}
              onCheckedChange={() => handleToggle('level4Enabled')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Timeout Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Timeout Settings</CardTitle>
          <CardDescription>
            Configure default timeout for approval requests
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="timeout">Default Timeout (minutes)</Label>
            <Input
              id="timeout"
              type="number"
              min="1"
              max="1440"
              value={approvalGates.defaultTimeout}
              onChange={(e) => handleNumberChange('defaultTimeout', e.target.value)}
              className={timeoutError ? 'border-red-500' : ''}
            />
            {timeoutError && (
              <p className="text-sm text-red-500">{timeoutError.message}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Time limit for responding to approval requests (1-1440 minutes)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Notification Preferences</CardTitle>
          <CardDescription>
            Configure when to receive notifications about approval gates
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notifyApproval">Notify on Approval</Label>
              <p className="text-sm text-muted-foreground">
                Receive notifications when approvals are granted
              </p>
            </div>
            <Switch
              id="notifyApproval"
              checked={approvalGates.notifyOnApproval}
              onCheckedChange={() => handleToggle('notifyOnApproval')}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notifyRejection">Notify on Rejection</Label>
              <p className="text-sm text-muted-foreground">
                Receive notifications when approvals are rejected
              </p>
            </div>
            <Switch
              id="notifyRejection"
              checked={approvalGates.notifyOnRejection}
              onCheckedChange={() => handleToggle('notifyOnRejection')}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="notifyTimeout">Notify on Timeout</Label>
              <p className="text-sm text-muted-foreground">
                Receive notifications when approval requests time out
              </p>
            </div>
            <Switch
              id="notifyTimeout"
              checked={approvalGates.notifyOnTimeout}
              onCheckedChange={() => handleToggle('notifyOnTimeout')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Auto-Approve */}
      <Card>
        <CardHeader>
          <CardTitle>Auto-Approve</CardTitle>
          <CardDescription>
            Automatically approve all gates (not recommended for production)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="autoApprove">Enable Auto-Approve</Label>
              <p className="text-sm text-muted-foreground">
                Bypass manual approval and automatically proceed
              </p>
            </div>
            <Switch
              id="autoApprove"
              checked={approvalGates.autoApprove}
              onCheckedChange={() => handleToggle('autoApprove')}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
