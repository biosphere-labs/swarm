/**
 * Settings Type Definitions
 * Comprehensive type system for application-wide configuration
 */

// LLM Provider Options
export type LLMProvider = 'openai' | 'together' | 'anthropic' | 'ollama';

// Theme Options
export type Theme = 'light' | 'dark' | 'system';

// Dashboard Layout Options
export type DashboardLayout = 'sidebar' | 'topbar';

/**
 * Approval Gate Configuration
 * Controls HITL (Human-In-The-Loop) approval gates at different pipeline levels
 */
export interface ApprovalGateConfig {
  level1Enabled: boolean;
  level2Enabled: boolean;
  level3Enabled: boolean;
  level4Enabled: boolean;
  defaultTimeout: number; // minutes
  autoApprove: boolean;
  notifyOnApproval: boolean;
  notifyOnRejection: boolean;
  notifyOnTimeout: boolean;
}

/**
 * Agent Pool Configuration
 * Defines settings for individual agent pools
 */
export interface AgentPoolConfig {
  enabled: boolean;
  size: number;
  priority: number; // 1-10, higher is more important
  maxConcurrent: number; // max concurrent executions
  description?: string;
}

/**
 * Agent Pools Configuration Map
 * Maps pool names to their configurations
 */
export interface AgentPoolsConfig {
  paradigmSelection: AgentPoolConfig;
  techniqueSelection: AgentPoolConfig;
  decomposition: AgentPoolConfig;
  execution: AgentPoolConfig;
  integration: AgentPoolConfig;
  [key: string]: AgentPoolConfig; // Allow dynamic pool names
}

/**
 * LLM Configuration
 * Settings for Language Model interactions
 */
export interface LLMConfig {
  provider: LLMProvider;
  defaultModel: string;
  level1Model?: string; // Paradigm Selection
  level2Model?: string; // Technique Selection
  level3Model?: string; // Decomposition
  level4Model?: string; // Execution
  temperature: number; // 0.0 - 2.0
  maxTokens: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  apiKey?: string; // Masked in UI
  apiEndpoint?: string; // Custom endpoint for Ollama
}

/**
 * Pipeline Configuration
 * Core pipeline execution parameters
 */
export interface PipelineConfig {
  maxParadigms: number; // Max number of paradigms to select
  techniqueDiversity: number; // 0-100, diversity threshold
  decompositionDepth: number; // Max decomposition tree depth
  timeout: number; // seconds
  retryAttempts: number;
  retryDelay: number; // seconds
  enableParallelExecution: boolean;
  enableCaching: boolean;
}

/**
 * UI Preferences
 * User interface customization settings
 */
export interface UIPreferences {
  theme: Theme;
  dashboardLayout: DashboardLayout;
  notifications: boolean;
  soundEffects: boolean;
  animationsEnabled: boolean;
  compactMode: boolean;
  showAdvancedOptions: boolean;
  defaultView: 'dashboard' | 'pipeline' | 'settings';
}

/**
 * Complete Settings Configuration
 * Root settings object containing all configuration categories
 */
export interface Settings {
  approvalGates: ApprovalGateConfig;
  agentPools: AgentPoolsConfig;
  llm: LLMConfig;
  pipeline: PipelineConfig;
  ui: UIPreferences;
  version: string; // Settings schema version
  lastModified?: string; // ISO timestamp
}

/**
 * Default Settings
 * Factory function to create default settings object
 */
export const createDefaultSettings = (): Settings => ({
  approvalGates: {
    level1Enabled: false,
    level2Enabled: true,
    level3Enabled: false,
    level4Enabled: true,
    defaultTimeout: 30,
    autoApprove: false,
    notifyOnApproval: true,
    notifyOnRejection: true,
    notifyOnTimeout: true,
  },
  agentPools: {
    paradigmSelection: {
      enabled: true,
      size: 5,
      priority: 8,
      maxConcurrent: 3,
      description: 'Paradigm selection and evaluation pool',
    },
    techniqueSelection: {
      enabled: true,
      size: 10,
      priority: 7,
      maxConcurrent: 5,
      description: 'Technique selection and ranking pool',
    },
    decomposition: {
      enabled: true,
      size: 8,
      priority: 9,
      maxConcurrent: 4,
      description: 'Problem decomposition pool',
    },
    execution: {
      enabled: true,
      size: 15,
      priority: 10,
      maxConcurrent: 10,
      description: 'Solution execution pool',
    },
    integration: {
      enabled: true,
      size: 5,
      priority: 6,
      maxConcurrent: 2,
      description: 'Solution integration and synthesis pool',
    },
  },
  llm: {
    provider: 'openai',
    defaultModel: 'gpt-4',
    level1Model: 'gpt-4',
    level2Model: 'gpt-4',
    level3Model: 'gpt-4',
    level4Model: 'gpt-4-turbo',
    temperature: 0.7,
    maxTokens: 2048,
    topP: 1.0,
    frequencyPenalty: 0.0,
    presencePenalty: 0.0,
  },
  pipeline: {
    maxParadigms: 5,
    techniqueDiversity: 70,
    decompositionDepth: 3,
    timeout: 300,
    retryAttempts: 3,
    retryDelay: 5,
    enableParallelExecution: true,
    enableCaching: true,
  },
  ui: {
    theme: 'system',
    dashboardLayout: 'sidebar',
    notifications: true,
    soundEffects: false,
    animationsEnabled: true,
    compactMode: false,
    showAdvancedOptions: false,
    defaultView: 'dashboard',
  },
  version: '1.0.0',
});

/**
 * Settings Validation Error
 */
export class SettingsValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public value: any
  ) {
    super(message);
    this.name = 'SettingsValidationError';
  }
}

/**
 * Validate Settings
 * Validates settings object for correctness
 */
export const validateSettings = (settings: Partial<Settings>): SettingsValidationError[] => {
  const errors: SettingsValidationError[] = [];

  // Validate Approval Gates
  if (settings.approvalGates) {
    const { defaultTimeout } = settings.approvalGates;
    if (defaultTimeout !== undefined && (defaultTimeout < 1 || defaultTimeout > 1440)) {
      errors.push(
        new SettingsValidationError(
          'Timeout must be between 1 and 1440 minutes',
          'approvalGates.defaultTimeout',
          defaultTimeout
        )
      );
    }
  }

  // Validate Agent Pools
  if (settings.agentPools) {
    Object.entries(settings.agentPools).forEach(([poolName, config]) => {
      if (config.size < 1 || config.size > 100) {
        errors.push(
          new SettingsValidationError(
            'Pool size must be between 1 and 100',
            `agentPools.${poolName}.size`,
            config.size
          )
        );
      }
      if (config.priority < 1 || config.priority > 10) {
        errors.push(
          new SettingsValidationError(
            'Priority must be between 1 and 10',
            `agentPools.${poolName}.priority`,
            config.priority
          )
        );
      }
      if (config.maxConcurrent < 1 || config.maxConcurrent > config.size) {
        errors.push(
          new SettingsValidationError(
            'Max concurrent must be between 1 and pool size',
            `agentPools.${poolName}.maxConcurrent`,
            config.maxConcurrent
          )
        );
      }
    });
  }

  // Validate LLM Config
  if (settings.llm) {
    const { temperature, maxTokens } = settings.llm;
    if (temperature !== undefined && (temperature < 0 || temperature > 2)) {
      errors.push(
        new SettingsValidationError(
          'Temperature must be between 0 and 2',
          'llm.temperature',
          temperature
        )
      );
    }
    if (maxTokens !== undefined && (maxTokens < 1 || maxTokens > 32000)) {
      errors.push(
        new SettingsValidationError(
          'Max tokens must be between 1 and 32000',
          'llm.maxTokens',
          maxTokens
        )
      );
    }
  }

  // Validate Pipeline Config
  if (settings.pipeline) {
    const { maxParadigms, techniqueDiversity, decompositionDepth, timeout } = settings.pipeline;
    if (maxParadigms !== undefined && (maxParadigms < 1 || maxParadigms > 20)) {
      errors.push(
        new SettingsValidationError(
          'Max paradigms must be between 1 and 20',
          'pipeline.maxParadigms',
          maxParadigms
        )
      );
    }
    if (techniqueDiversity !== undefined && (techniqueDiversity < 0 || techniqueDiversity > 100)) {
      errors.push(
        new SettingsValidationError(
          'Technique diversity must be between 0 and 100',
          'pipeline.techniqueDiversity',
          techniqueDiversity
        )
      );
    }
    if (decompositionDepth !== undefined && (decompositionDepth < 1 || decompositionDepth > 10)) {
      errors.push(
        new SettingsValidationError(
          'Decomposition depth must be between 1 and 10',
          'pipeline.decompositionDepth',
          decompositionDepth
        )
      );
    }
    if (timeout !== undefined && (timeout < 10 || timeout > 3600)) {
      errors.push(
        new SettingsValidationError(
          'Timeout must be between 10 and 3600 seconds',
          'pipeline.timeout',
          timeout
        )
      );
    }
  }

  return errors;
};

/**
 * LLM Model Options by Provider
 */
export const LLM_MODELS: Record<LLMProvider, string[]> = {
  openai: [
    'gpt-4',
    'gpt-4-turbo',
    'gpt-4-turbo-preview',
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k',
  ],
  together: [
    'meta-llama/Llama-2-70b-chat-hf',
    'meta-llama/Llama-2-13b-chat-hf',
    'mistralai/Mixtral-8x7B-Instruct-v0.1',
    'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO',
  ],
  anthropic: [
    'claude-3-opus-20240229',
    'claude-3-sonnet-20240229',
    'claude-3-haiku-20240307',
    'claude-2.1',
    'claude-2.0',
  ],
  ollama: [
    'llama2',
    'mistral',
    'mixtral',
    'codellama',
    'phi',
  ],
};
