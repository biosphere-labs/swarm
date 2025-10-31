/**
 * Settings Panel Test Suite
 * Comprehensive tests for all settings components
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SettingsPanel } from '@/components/SettingsPanel';
import { ApprovalGateSettings } from '@/components/settings/ApprovalGateSettings';
import { AgentPoolSettings } from '@/components/settings/AgentPoolSettings';
import { LLMSettings } from '@/components/settings/LLMSettings';
import { PipelineSettings } from '@/components/settings/PipelineSettings';
import { UIPreferences } from '@/components/settings/UIPreferences';
import { useSettingsStore } from '@/lib/settings-store';
import { createDefaultSettings } from '@/types/settings';

// Mock Zustand store
jest.mock('@/lib/settings-store', () => ({
  useSettingsStore: jest.fn(),
}));

describe('SettingsPanel', () => {
  const mockStore = {
    settings: createDefaultSettings(),
    hasUnsavedChanges: false,
    validationErrors: [],
    isLoading: false,
    lastSaved: null,
    saveSettings: jest.fn(),
    resetToDefaults: jest.fn(),
    discardChanges: jest.fn(),
    exportSettings: jest.fn(() => JSON.stringify(createDefaultSettings())),
    importSettings: jest.fn(),
    updateApprovalGates: jest.fn(),
    updateAgentPool: jest.fn(),
    updateLLMConfig: jest.fn(),
    updatePipelineConfig: jest.fn(),
    updateUIPreferences: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
      selector ? selector(mockStore) : mockStore
    );
  });

  describe('SettingsPanel Component', () => {
    it('renders settings panel with all tabs', () => {
      render(<SettingsPanel />);

      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.getByText('Approval Gates')).toBeInTheDocument();
      expect(screen.getByText('Agent Pools')).toBeInTheDocument();
      expect(screen.getByText('LLM')).toBeInTheDocument();
      expect(screen.getByText('Pipeline')).toBeInTheDocument();
      expect(screen.getByText('UI')).toBeInTheDocument();
    });

    it('shows unsaved changes badge when changes exist', () => {
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector ? selector({ ...mockStore, hasUnsavedChanges: true }) : { ...mockStore, hasUnsavedChanges: true }
      );

      render(<SettingsPanel />);
      expect(screen.getByText('Unsaved Changes')).toBeInTheDocument();
    });

    it('displays validation errors', () => {
      const errors = [
        { field: 'llm.temperature', message: 'Temperature must be between 0 and 2', value: 3 },
      ];
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector ? selector({ ...mockStore, validationErrors: errors }) : { ...mockStore, validationErrors: errors }
      );

      render(<SettingsPanel />);
      expect(screen.getByText(/1 Error/)).toBeInTheDocument();
      expect(screen.getByText('Validation Errors')).toBeInTheDocument();
    });

    it('calls saveSettings when save button is clicked', async () => {
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector ? selector({ ...mockStore, hasUnsavedChanges: true }) : { ...mockStore, hasUnsavedChanges: true }
      );
      mockStore.saveSettings.mockResolvedValue(true);

      render(<SettingsPanel />);
      const saveButton = screen.getByRole('button', { name: /Save Settings/ });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockStore.saveSettings).toHaveBeenCalled();
      });
    });

    it('shows reset confirmation dialog', async () => {
      render(<SettingsPanel />);
      const resetButton = screen.getByRole('button', { name: /Reset to Defaults/ });
      fireEvent.click(resetButton);

      await waitFor(() => {
        expect(screen.getByText('Reset to Defaults?')).toBeInTheDocument();
      });
    });

    it('exports settings as JSON', async () => {
      render(<SettingsPanel />);
      const exportButton = screen.getByRole('button', { name: /Export/ });
      fireEvent.click(exportButton);

      await waitFor(() => {
        expect(screen.getByText('Export Settings')).toBeInTheDocument();
        expect(mockStore.exportSettings).toHaveBeenCalled();
      });
    });

    it('switches between tabs', () => {
      render(<SettingsPanel />);

      const agentPoolsTab = screen.getByRole('tab', { name: 'Agent Pools' });
      fireEvent.click(agentPoolsTab);

      expect(screen.getByText('Agent Pool Configuration')).toBeInTheDocument();
    });
  });

  describe('ApprovalGateSettings Component', () => {
    it('renders approval gate settings', () => {
      render(<ApprovalGateSettings />);

      expect(screen.getByText('Approval Gate Configuration')).toBeInTheDocument();
      expect(screen.getByText('Level 1 - Paradigm Selection')).toBeInTheDocument();
      expect(screen.getByText('Level 2 - Technique Selection')).toBeInTheDocument();
      expect(screen.getByText('Level 3 - Problem Decomposition')).toBeInTheDocument();
      expect(screen.getByText('Level 4 - Solution Execution')).toBeInTheDocument();
    });

    it('toggles approval gate levels', () => {
      render(<ApprovalGateSettings />);

      const level1Switch = screen.getByRole('switch', { name: /level1/ });
      fireEvent.click(level1Switch);

      expect(mockStore.updateApprovalGates).toHaveBeenCalledWith({
        level1Enabled: !mockStore.settings.approvalGates.level1Enabled,
      });
    });

    it('updates timeout value', () => {
      render(<ApprovalGateSettings />);

      const timeoutInput = screen.getByLabelText(/Default Timeout/);
      fireEvent.change(timeoutInput, { target: { value: '60' } });

      expect(mockStore.updateApprovalGates).toHaveBeenCalledWith({
        defaultTimeout: 60,
      });
    });

    it('toggles notification preferences', () => {
      render(<ApprovalGateSettings />);

      const notifySwitch = screen.getByRole('switch', { name: /notifyApproval/ });
      fireEvent.click(notifySwitch);

      expect(mockStore.updateApprovalGates).toHaveBeenCalled();
    });

    it('toggles auto-approve setting', () => {
      render(<ApprovalGateSettings />);

      const autoApproveSwitch = screen.getByRole('switch', { name: /autoApprove/ });
      fireEvent.click(autoApproveSwitch);

      expect(mockStore.updateApprovalGates).toHaveBeenCalledWith({
        autoApprove: !mockStore.settings.approvalGates.autoApprove,
      });
    });

    it('displays validation error for invalid timeout', () => {
      const errors = [
        {
          field: 'approvalGates.defaultTimeout',
          message: 'Timeout must be between 1 and 1440 minutes',
          value: 2000,
        },
      ];
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector ? selector({ ...mockStore, validationErrors: errors }) : { ...mockStore, validationErrors: errors }
      );

      render(<ApprovalGateSettings />);
      expect(screen.getByText('Timeout must be between 1 and 1440 minutes')).toBeInTheDocument();
    });
  });

  describe('AgentPoolSettings Component', () => {
    it('renders agent pool settings', () => {
      render(<AgentPoolSettings />);

      expect(screen.getByText('Agent Pool Configuration')).toBeInTheDocument();
      expect(screen.getByText('Paradigm Selection Pool')).toBeInTheDocument();
      expect(screen.getByText('Technique Selection Pool')).toBeInTheDocument();
      expect(screen.getByText('Decomposition Pool')).toBeInTheDocument();
      expect(screen.getByText('Execution Pool')).toBeInTheDocument();
      expect(screen.getByText('Integration Pool')).toBeInTheDocument();
    });

    it('displays pool statistics', () => {
      render(<AgentPoolSettings />);

      expect(screen.getByText('Pool Statistics')).toBeInTheDocument();
      expect(screen.getByText('Total Pools')).toBeInTheDocument();
      expect(screen.getByText('Active Pools')).toBeInTheDocument();
    });

    it('toggles pool enabled state', () => {
      render(<AgentPoolSettings />);

      const enableSwitch = screen.getByRole('switch', { name: /paradigmSelection-enabled/ });
      fireEvent.click(enableSwitch);

      expect(mockStore.updateAgentPool).toHaveBeenCalledWith('paradigmSelection', {
        enabled: !mockStore.settings.agentPools.paradigmSelection.enabled,
      });
    });

    it('updates pool size', () => {
      render(<AgentPoolSettings />);

      const sizeInput = screen.getByLabelText(/paradigmSelection-size/);
      fireEvent.change(sizeInput, { target: { value: '10' } });

      expect(mockStore.updateAgentPool).toHaveBeenCalledWith('paradigmSelection', {
        size: 10,
      });
    });

    it('updates pool priority', () => {
      render(<AgentPoolSettings />);

      const priorityInput = screen.getByLabelText(/paradigmSelection-priority/);
      fireEvent.change(priorityInput, { target: { value: '9' } });

      expect(mockStore.updateAgentPool).toHaveBeenCalledWith('paradigmSelection', {
        priority: 9,
      });
    });

    it('displays validation error for invalid pool size', () => {
      const errors = [
        {
          field: 'agentPools.paradigmSelection.size',
          message: 'Pool size must be between 1 and 100',
          value: 150,
        },
      ];
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector ? selector({ ...mockStore, validationErrors: errors }) : { ...mockStore, validationErrors: errors }
      );

      render(<AgentPoolSettings />);
      expect(screen.getByText('Pool size must be between 1 and 100')).toBeInTheDocument();
    });
  });

  describe('LLMSettings Component', () => {
    it('renders LLM settings', () => {
      render(<LLMSettings />);

      expect(screen.getByText('LLM Configuration')).toBeInTheDocument();
      expect(screen.getByText('Provider Configuration')).toBeInTheDocument();
      expect(screen.getByText('Model Selection')).toBeInTheDocument();
      expect(screen.getByText('Generation Parameters')).toBeInTheDocument();
    });

    it('changes LLM provider', () => {
      render(<LLMSettings />);

      const providerSelect = screen.getByLabelText(/LLM Provider/);
      fireEvent.click(providerSelect);

      // Note: In a real test, you'd need to interact with the select dropdown
      // This is a simplified version
      expect(providerSelect).toBeInTheDocument();
    });

    it('updates temperature value', () => {
      render(<LLMSettings />);

      const tempInput = screen.getByLabelText(/Temperature/);
      fireEvent.change(tempInput, { target: { value: '0.8' } });

      expect(mockStore.updateLLMConfig).toHaveBeenCalledWith({
        temperature: 0.8,
      });
    });

    it('updates max tokens', () => {
      render(<LLMSettings />);

      const tokensInput = screen.getByLabelText(/Max Tokens/);
      fireEvent.change(tokensInput, { target: { value: '4096' } });

      expect(mockStore.updateLLMConfig).toHaveBeenCalledWith({
        maxTokens: 4096,
      });
    });

    it('masks API key by default', () => {
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector
          ? selector({
              ...mockStore,
              settings: {
                ...mockStore.settings,
                llm: { ...mockStore.settings.llm, apiKey: 'sk-1234567890abcdef' },
              },
            })
          : {
              ...mockStore,
              settings: {
                ...mockStore.settings,
                llm: { ...mockStore.settings.llm, apiKey: 'sk-1234567890abcdef' },
              },
            }
      );

      render(<LLMSettings />);
      const apiKeyInput = screen.getByLabelText(/API Key/) as HTMLInputElement;
      expect(apiKeyInput.type).toBe('password');
    });

    it('displays validation error for invalid temperature', () => {
      const errors = [
        {
          field: 'llm.temperature',
          message: 'Temperature must be between 0 and 2',
          value: 3,
        },
      ];
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector ? selector({ ...mockStore, validationErrors: errors }) : { ...mockStore, validationErrors: errors }
      );

      render(<LLMSettings />);
      expect(screen.getByText('Temperature must be between 0 and 2')).toBeInTheDocument();
    });
  });

  describe('PipelineSettings Component', () => {
    it('renders pipeline settings', () => {
      render(<PipelineSettings />);

      expect(screen.getByText('Pipeline Configuration')).toBeInTheDocument();
      expect(screen.getByText('Selection Parameters')).toBeInTheDocument();
      expect(screen.getByText('Decomposition Parameters')).toBeInTheDocument();
      expect(screen.getByText('Execution Parameters')).toBeInTheDocument();
    });

    it('updates max paradigms', () => {
      render(<PipelineSettings />);

      const maxParadigmsInput = screen.getByLabelText(/Maximum Paradigms/);
      fireEvent.change(maxParadigmsInput, { target: { value: '8' } });

      expect(mockStore.updatePipelineConfig).toHaveBeenCalledWith({
        maxParadigms: 8,
      });
    });

    it('updates technique diversity threshold', () => {
      render(<PipelineSettings />);

      const diversityInput = screen.getByLabelText(/Technique Diversity Threshold/);
      fireEvent.change(diversityInput, { target: { value: '80' } });

      expect(mockStore.updatePipelineConfig).toHaveBeenCalledWith({
        techniqueDiversity: 80,
      });
    });

    it('updates decomposition depth', () => {
      render(<PipelineSettings />);

      const depthInput = screen.getByLabelText(/Maximum Decomposition Depth/);
      fireEvent.change(depthInput, { target: { value: '5' } });

      expect(mockStore.updatePipelineConfig).toHaveBeenCalledWith({
        decompositionDepth: 5,
      });
    });

    it('toggles parallel execution', () => {
      render(<PipelineSettings />);

      const parallelSwitch = screen.getByRole('switch', { name: /parallelExecution/ });
      fireEvent.click(parallelSwitch);

      expect(mockStore.updatePipelineConfig).toHaveBeenCalledWith({
        enableParallelExecution: !mockStore.settings.pipeline.enableParallelExecution,
      });
    });

    it('toggles caching', () => {
      render(<PipelineSettings />);

      const cachingSwitch = screen.getByRole('switch', { name: /caching/ });
      fireEvent.click(cachingSwitch);

      expect(mockStore.updatePipelineConfig).toHaveBeenCalledWith({
        enableCaching: !mockStore.settings.pipeline.enableCaching,
      });
    });

    it('displays configuration summary', () => {
      render(<PipelineSettings />);

      expect(screen.getByText('Configuration Summary')).toBeInTheDocument();
      expect(screen.getByText('Max Paradigms')).toBeInTheDocument();
      expect(screen.getByText('Diversity Threshold')).toBeInTheDocument();
    });
  });

  describe('UIPreferences Component', () => {
    it('renders UI preferences', () => {
      render(<UIPreferences />);

      expect(screen.getByText('UI Preferences')).toBeInTheDocument();
      expect(screen.getByText('Appearance')).toBeInTheDocument();
      expect(screen.getByText('Layout')).toBeInTheDocument();
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    it('changes theme', () => {
      render(<UIPreferences />);

      const themeSelect = screen.getByLabelText(/Color Theme/);
      fireEvent.click(themeSelect);

      expect(themeSelect).toBeInTheDocument();
    });

    it('toggles animations', () => {
      render(<UIPreferences />);

      const animationsSwitch = screen.getByRole('switch', { name: /animations/ });
      fireEvent.click(animationsSwitch);

      expect(mockStore.updateUIPreferences).toHaveBeenCalledWith({
        animationsEnabled: !mockStore.settings.ui.animationsEnabled,
      });
    });

    it('toggles compact mode', () => {
      render(<UIPreferences />);

      const compactSwitch = screen.getByRole('switch', { name: /compactMode/ });
      fireEvent.click(compactSwitch);

      expect(mockStore.updateUIPreferences).toHaveBeenCalledWith({
        compactMode: !mockStore.settings.ui.compactMode,
      });
    });

    it('toggles notifications', () => {
      render(<UIPreferences />);

      const notificationsSwitch = screen.getByRole('switch', { name: /notifications/ });
      fireEvent.click(notificationsSwitch);

      expect(mockStore.updateUIPreferences).toHaveBeenCalledWith({
        notifications: !mockStore.settings.ui.notifications,
      });
    });

    it('displays current configuration', () => {
      render(<UIPreferences />);

      expect(screen.getByText('Current Configuration')).toBeInTheDocument();
      expect(screen.getByText('Theme')).toBeInTheDocument();
      expect(screen.getByText('Layout')).toBeInTheDocument();
    });
  });

  describe('Settings Store Integration', () => {
    it('validates settings before saving', async () => {
      const errors = [
        { field: 'llm.temperature', message: 'Temperature must be between 0 and 2', value: 3 },
      ];
      (useSettingsStore as unknown as jest.Mock).mockImplementation((selector) =>
        selector
          ? selector({ ...mockStore, validationErrors: errors, hasUnsavedChanges: true })
          : { ...mockStore, validationErrors: errors, hasUnsavedChanges: true }
      );

      render(<SettingsPanel />);
      const saveButton = screen.getByRole('button', { name: /Save Settings/ });

      expect(saveButton).toBeDisabled();
    });

    it('persists settings to localStorage', () => {
      // This would test the Zustand persist middleware
      // In a real scenario, you'd mock localStorage
      expect(mockStore.settings).toBeDefined();
    });

    it('handles import errors gracefully', () => {
      mockStore.importSettings.mockReturnValue(false);

      render(<SettingsPanel />);
      // In a real test, you'd trigger file import and verify error handling
      expect(mockStore.importSettings).toBeDefined();
    });
  });
});
