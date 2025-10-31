/**
 * Settings Store
 * Zustand-based state management for application settings
 * Handles persistence to localStorage and provides actions for settings management
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
  Settings,
  createDefaultSettings,
  validateSettings,
  SettingsValidationError,
} from '@/types/settings';

/**
 * Settings Store State
 */
interface SettingsState {
  settings: Settings;
  isLoading: boolean;
  hasUnsavedChanges: boolean;
  validationErrors: SettingsValidationError[];
  lastSaved: string | null;
}

/**
 * Settings Store Actions
 */
interface SettingsActions {
  // Update settings
  updateSettings: (updates: Partial<Settings>) => void;
  updateApprovalGates: (updates: Partial<Settings['approvalGates']>) => void;
  updateAgentPool: (poolName: string, updates: Partial<Settings['agentPools']['paradigmSelection']>) => void;
  updateLLMConfig: (updates: Partial<Settings['llm']>) => void;
  updatePipelineConfig: (updates: Partial<Settings['pipeline']>) => void;
  updateUIPreferences: (updates: Partial<Settings['ui']>) => void;

  // Save and reset
  saveSettings: () => Promise<boolean>;
  resetToDefaults: () => void;
  discardChanges: () => void;

  // Import/Export
  exportSettings: () => string;
  importSettings: (json: string) => boolean;

  // Validation
  validateCurrentSettings: () => boolean;
  clearValidationErrors: () => void;

  // Loading state
  setLoading: (loading: boolean) => void;
}

/**
 * Settings Store Type
 */
type SettingsStore = SettingsState & SettingsActions;

/**
 * Create Settings Store with Persistence
 */
export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      // Initial State
      settings: createDefaultSettings(),
      isLoading: false,
      hasUnsavedChanges: false,
      validationErrors: [],
      lastSaved: null,

      // Update Settings
      updateSettings: (updates: Partial<Settings>) => {
        set((state) => {
          const newSettings = { ...state.settings, ...updates };
          const errors = validateSettings(newSettings);

          return {
            settings: newSettings,
            hasUnsavedChanges: true,
            validationErrors: errors,
          };
        });
      },

      // Update Approval Gates
      updateApprovalGates: (updates: Partial<Settings['approvalGates']>) => {
        set((state) => {
          const newSettings = {
            ...state.settings,
            approvalGates: { ...state.settings.approvalGates, ...updates },
          };
          const errors = validateSettings(newSettings);

          return {
            settings: newSettings,
            hasUnsavedChanges: true,
            validationErrors: errors,
          };
        });
      },

      // Update Agent Pool
      updateAgentPool: (
        poolName: string,
        updates: Partial<Settings['agentPools']['paradigmSelection']>
      ) => {
        set((state) => {
          const newSettings = {
            ...state.settings,
            agentPools: {
              ...state.settings.agentPools,
              [poolName]: {
                ...state.settings.agentPools[poolName],
                ...updates,
              },
            },
          };
          const errors = validateSettings(newSettings);

          return {
            settings: newSettings,
            hasUnsavedChanges: true,
            validationErrors: errors,
          };
        });
      },

      // Update LLM Config
      updateLLMConfig: (updates: Partial<Settings['llm']>) => {
        set((state) => {
          const newSettings = {
            ...state.settings,
            llm: { ...state.settings.llm, ...updates },
          };
          const errors = validateSettings(newSettings);

          return {
            settings: newSettings,
            hasUnsavedChanges: true,
            validationErrors: errors,
          };
        });
      },

      // Update Pipeline Config
      updatePipelineConfig: (updates: Partial<Settings['pipeline']>) => {
        set((state) => {
          const newSettings = {
            ...state.settings,
            pipeline: { ...state.settings.pipeline, ...updates },
          };
          const errors = validateSettings(newSettings);

          return {
            settings: newSettings,
            hasUnsavedChanges: true,
            validationErrors: errors,
          };
        });
      },

      // Update UI Preferences
      updateUIPreferences: (updates: Partial<Settings['ui']>) => {
        set((state) => {
          const newSettings = {
            ...state.settings,
            ui: { ...state.settings.ui, ...updates },
          };

          // Apply theme immediately
          if (updates.theme) {
            applyTheme(updates.theme);
          }

          return {
            settings: newSettings,
            hasUnsavedChanges: true,
          };
        });
      },

      // Save Settings
      saveSettings: async () => {
        const state = get();
        const errors = validateSettings(state.settings);

        if (errors.length > 0) {
          set({ validationErrors: errors });
          return false;
        }

        try {
          set({ isLoading: true });

          // Update timestamp
          const updatedSettings = {
            ...state.settings,
            lastModified: new Date().toISOString(),
          };

          // TODO: Send to backend API if needed
          // await fetch('/api/settings', {
          //   method: 'POST',
          //   headers: { 'Content-Type': 'application/json' },
          //   body: JSON.stringify(updatedSettings),
          // });

          set({
            settings: updatedSettings,
            hasUnsavedChanges: false,
            validationErrors: [],
            lastSaved: new Date().toISOString(),
            isLoading: false,
          });

          return true;
        } catch (error) {
          console.error('Failed to save settings:', error);
          set({ isLoading: false });
          return false;
        }
      },

      // Reset to Defaults
      resetToDefaults: () => {
        const defaultSettings = createDefaultSettings();
        set({
          settings: defaultSettings,
          hasUnsavedChanges: true,
          validationErrors: [],
        });
      },

      // Discard Changes
      discardChanges: () => {
        // Reload from localStorage
        const stored = localStorage.getItem('settings-storage');
        if (stored) {
          try {
            const { state } = JSON.parse(stored);
            set({
              settings: state.settings,
              hasUnsavedChanges: false,
              validationErrors: [],
            });
          } catch (error) {
            console.error('Failed to discard changes:', error);
          }
        }
      },

      // Export Settings
      exportSettings: () => {
        const state = get();
        return JSON.stringify(state.settings, null, 2);
      },

      // Import Settings
      importSettings: (json: string) => {
        try {
          const imported = JSON.parse(json) as Settings;
          const errors = validateSettings(imported);

          if (errors.length > 0) {
            set({ validationErrors: errors });
            return false;
          }

          set({
            settings: imported,
            hasUnsavedChanges: true,
            validationErrors: [],
          });

          return true;
        } catch (error) {
          console.error('Failed to import settings:', error);
          return false;
        }
      },

      // Validate Current Settings
      validateCurrentSettings: () => {
        const state = get();
        const errors = validateSettings(state.settings);
        set({ validationErrors: errors });
        return errors.length === 0;
      },

      // Clear Validation Errors
      clearValidationErrors: () => {
        set({ validationErrors: [] });
      },

      // Set Loading
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'settings-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        settings: state.settings,
        lastSaved: state.lastSaved,
      }),
    }
  )
);

/**
 * Apply Theme to Document
 */
function applyTheme(theme: Settings['ui']['theme']) {
  const root = document.documentElement;

  if (theme === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.classList.toggle('dark', prefersDark);
  } else {
    root.classList.toggle('dark', theme === 'dark');
  }
}

/**
 * Initialize Theme on Mount
 */
if (typeof window !== 'undefined') {
  // Apply theme from stored settings
  const stored = localStorage.getItem('settings-storage');
  if (stored) {
    try {
      const { state } = JSON.parse(stored);
      applyTheme(state.settings.ui.theme);
    } catch (error) {
      console.error('Failed to apply theme:', error);
    }
  }

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    const stored = localStorage.getItem('settings-storage');
    if (stored) {
      try {
        const { state } = JSON.parse(stored);
        if (state.settings.ui.theme === 'system') {
          document.documentElement.classList.toggle('dark', e.matches);
        }
      } catch (error) {
        console.error('Failed to apply system theme:', error);
      }
    }
  });
}

/**
 * Keyboard Shortcuts Hook
 */
export function useSettingsKeyboardShortcuts() {
  const saveSettings = useSettingsStore((state) => state.saveSettings);

  if (typeof window !== 'undefined') {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+S or Cmd+S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveSettings();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }
}
