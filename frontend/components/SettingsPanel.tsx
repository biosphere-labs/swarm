/**
 * Settings Panel Component
 * Main settings and configuration panel with tabbed interface
 */

import React, { useState, useEffect } from 'react';
import { useSettingsStore } from '@/lib/settings-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ApprovalGateSettings } from '@/components/settings/ApprovalGateSettings';
import { AgentPoolSettings } from '@/components/settings/AgentPoolSettings';
import { LLMSettings } from '@/components/settings/LLMSettings';
import { PipelineSettings } from '@/components/settings/PipelineSettings';
import { UIPreferences } from '@/components/settings/UIPreferences';
import {
  Save,
  RotateCcw,
  Download,
  Upload,
  AlertCircle,
  CheckCircle,
  Settings,
} from 'lucide-react';

export function SettingsPanel() {
  const {
    settings,
    hasUnsavedChanges,
    validationErrors,
    isLoading,
    lastSaved,
    saveSettings,
    resetToDefaults,
    discardChanges,
    exportSettings,
    importSettings,
  } = useSettingsStore();

  const [activeTab, setActiveTab] = useState('approval-gates');
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [showDiscardDialog, setShowDiscardDialog] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [exportedJson, setExportedJson] = useState('');
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Keyboard shortcut for save (Ctrl+S)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Warn about unsaved changes on navigation
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  const handleSave = async () => {
    const success = await saveSettings();
    setSaveStatus(success ? 'success' : 'error');
    setTimeout(() => setSaveStatus('idle'), 3000);
  };

  const handleReset = () => {
    resetToDefaults();
    setShowResetDialog(false);
  };

  const handleDiscard = () => {
    discardChanges();
    setShowDiscardDialog(false);
  };

  const handleExport = () => {
    const json = exportSettings();
    setExportedJson(json);
    setShowExportDialog(true);
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const text = await file.text();
        const success = importSettings(text);
        setSaveStatus(success ? 'success' : 'error');
        setTimeout(() => setSaveStatus('idle'), 3000);
      }
    };
    input.click();
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(exportedJson);
  };

  const downloadJson = () => {
    const blob = new Blob([exportedJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `swarm-settings-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const hasErrors = validationErrors.length > 0;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Settings className="h-8 w-8" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
            <p className="text-muted-foreground">
              Configure your SWARM pipeline settings and preferences
            </p>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center gap-2">
          {hasUnsavedChanges && (
            <Badge variant="outline" className="gap-1">
              <AlertCircle className="h-3 w-3" />
              Unsaved Changes
            </Badge>
          )}
          {hasErrors && (
            <Badge variant="destructive" className="gap-1">
              <AlertCircle className="h-3 w-3" />
              {validationErrors.length} Error{validationErrors.length > 1 ? 's' : ''}
            </Badge>
          )}
          {saveStatus === 'success' && (
            <Badge variant="default" className="gap-1 bg-green-500">
              <CheckCircle className="h-3 w-3" />
              Saved
            </Badge>
          )}
          {lastSaved && (
            <p className="text-sm text-muted-foreground">
              Last saved: {new Date(lastSaved).toLocaleString()}
            </p>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
          <CardDescription>
            Save, reset, or import/export your settings
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={handleSave}
              disabled={!hasUnsavedChanges || hasErrors || isLoading}
              className="gap-2"
            >
              <Save className="h-4 w-4" />
              Save Settings {hasUnsavedChanges && '*'}
            </Button>

            <Button
              onClick={() => setShowDiscardDialog(true)}
              disabled={!hasUnsavedChanges || isLoading}
              variant="outline"
              className="gap-2"
            >
              <RotateCcw className="h-4 w-4" />
              Discard Changes
            </Button>

            <Button
              onClick={() => setShowResetDialog(true)}
              disabled={isLoading}
              variant="outline"
              className="gap-2"
            >
              <RotateCcw className="h-4 w-4" />
              Reset to Defaults
            </Button>

            <div className="flex-1" />

            <Button
              onClick={handleExport}
              disabled={isLoading}
              variant="outline"
              className="gap-2"
            >
              <Download className="h-4 w-4" />
              Export
            </Button>

            <Button
              onClick={handleImport}
              disabled={isLoading}
              variant="outline"
              className="gap-2"
            >
              <Upload className="h-4 w-4" />
              Import
            </Button>
          </div>

          {/* Keyboard Shortcut Hint */}
          <p className="mt-4 text-sm text-muted-foreground">
            Tip: Press <kbd className="px-2 py-1 bg-muted rounded">Ctrl+S</kbd> to save
            settings quickly
          </p>
        </CardContent>
      </Card>

      {/* Validation Errors */}
      {hasErrors && (
        <Card className="border-red-500">
          <CardHeader>
            <CardTitle className="text-red-500 flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Validation Errors
            </CardTitle>
            <CardDescription>
              Please fix the following errors before saving
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {validationErrors.map((error, index) => (
                <li key={index} className="text-sm">
                  <span className="font-semibold">{error.field}:</span> {error.message}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="approval-gates">Approval Gates</TabsTrigger>
          <TabsTrigger value="agent-pools">Agent Pools</TabsTrigger>
          <TabsTrigger value="llm">LLM</TabsTrigger>
          <TabsTrigger value="pipeline">Pipeline</TabsTrigger>
          <TabsTrigger value="ui">UI</TabsTrigger>
        </TabsList>

        <TabsContent value="approval-gates" className="mt-6">
          <ApprovalGateSettings />
        </TabsContent>

        <TabsContent value="agent-pools" className="mt-6">
          <AgentPoolSettings />
        </TabsContent>

        <TabsContent value="llm" className="mt-6">
          <LLMSettings />
        </TabsContent>

        <TabsContent value="pipeline" className="mt-6">
          <PipelineSettings />
        </TabsContent>

        <TabsContent value="ui" className="mt-6">
          <UIPreferences />
        </TabsContent>
      </Tabs>

      {/* Reset Confirmation Dialog */}
      <Dialog open={showResetDialog} onOpenChange={setShowResetDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reset to Defaults?</DialogTitle>
            <DialogDescription>
              This will reset all settings to their default values. Any unsaved changes
              will be lost. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowResetDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleReset}>
              Reset to Defaults
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Discard Changes Confirmation Dialog */}
      <Dialog open={showDiscardDialog} onOpenChange={setShowDiscardDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Discard Changes?</DialogTitle>
            <DialogDescription>
              This will discard all unsaved changes and restore the last saved settings.
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDiscardDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDiscard}>
              Discard Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Export Dialog */}
      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Export Settings</DialogTitle>
            <DialogDescription>
              Copy the JSON below or download it as a file
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <textarea
              readOnly
              value={exportedJson}
              className="w-full h-64 p-4 font-mono text-sm border rounded-md"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExportDialog(false)}>
              Close
            </Button>
            <Button variant="outline" onClick={copyToClipboard}>
              Copy to Clipboard
            </Button>
            <Button onClick={downloadJson}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
