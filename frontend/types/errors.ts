/**
 * Error type definitions for the frontend application.
 *
 * Provides structured error types that align with backend error responses
 * and enable consistent error handling throughout the UI.
 */

/**
 * Error severity levels for UI display
 */
export enum ErrorSeverity {
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

/**
 * Error category for categorizing different types of errors
 */
export enum ErrorCategory {
  NETWORK = 'network',
  VALIDATION = 'validation',
  LLM = 'llm',
  PIPELINE = 'pipeline',
  AUTHENTICATION = 'authentication',
  CHECKPOINT = 'checkpoint',
  GRAPH = 'graph',
  AGENT_POOL = 'agent_pool',
  HUMAN_APPROVAL = 'human_approval',
  CONFIGURATION = 'configuration',
  UNKNOWN = 'unknown',
}

/**
 * Backend error code pattern
 */
export type ErrorCode = string;

/**
 * Backend error response structure
 */
export interface BackendError {
  type: string;
  message: string;
  code: ErrorCode;
  details?: Record<string, any>;
  recovery_suggestion?: string;
  original_error?: string;
  traceback?: string;
}

/**
 * API error response structure
 */
export interface ApiErrorResponse {
  success: false;
  error: BackendError;
  request_id?: string;
}

/**
 * Application error class for consistent error handling
 */
export class AppError extends Error {
  readonly category: ErrorCategory;
  readonly severity: ErrorSeverity;
  readonly code?: ErrorCode;
  readonly details?: Record<string, any>;
  readonly recoverySuggestion?: string;
  readonly originalError?: Error;
  readonly timestamp: Date;
  readonly requestId?: string;

  constructor(
    message: string,
    options: {
      category?: ErrorCategory;
      severity?: ErrorSeverity;
      code?: ErrorCode;
      details?: Record<string, any>;
      recoverySuggestion?: string;
      originalError?: Error;
      requestId?: string;
    } = {}
  ) {
    super(message);
    this.name = 'AppError';
    this.category = options.category || ErrorCategory.UNKNOWN;
    this.severity = options.severity || ErrorSeverity.ERROR;
    this.code = options.code;
    this.details = options.details;
    this.recoverySuggestion = options.recoverySuggestion;
    this.originalError = options.originalError;
    this.requestId = options.requestId;
    this.timestamp = new Date();

    // Maintains proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AppError);
    }
  }

  /**
   * Create AppError from backend error response
   */
  static fromBackendError(errorResponse: ApiErrorResponse): AppError {
    const { error, request_id } = errorResponse;
    const category = mapErrorCodeToCategory(error.code);
    const severity = mapCategoryToSeverity(category);

    return new AppError(error.message, {
      category,
      severity,
      code: error.code,
      details: error.details,
      recoverySuggestion: error.recovery_suggestion,
      requestId: request_id,
    });
  }

  /**
   * Create AppError from unknown error
   */
  static fromUnknown(error: unknown, context?: string): AppError {
    if (error instanceof AppError) {
      return error;
    }

    if (error instanceof Error) {
      return new AppError(context ? `${context}: ${error.message}` : error.message, {
        category: ErrorCategory.UNKNOWN,
        severity: ErrorSeverity.ERROR,
        originalError: error,
      });
    }

    return new AppError(
      context ? `${context}: ${String(error)}` : String(error),
      {
        category: ErrorCategory.UNKNOWN,
        severity: ErrorSeverity.ERROR,
      }
    );
  }

  /**
   * Convert to plain object for logging
   */
  toJSON(): Record<string, any> {
    return {
      name: this.name,
      message: this.message,
      category: this.category,
      severity: this.severity,
      code: this.code,
      details: this.details,
      recoverySuggestion: this.recoverySuggestion,
      timestamp: this.timestamp.toISOString(),
      requestId: this.requestId,
      stack: this.stack,
    };
  }
}

/**
 * Network error for connection and API failures
 */
export class NetworkError extends AppError {
  constructor(
    message: string,
    options: Omit<ConstructorParameters<typeof AppError>[1], 'category'> = {}
  ) {
    super(message, {
      ...options,
      category: ErrorCategory.NETWORK,
      severity: options.severity || ErrorSeverity.ERROR,
    });
    this.name = 'NetworkError';
  }
}

/**
 * Validation error for invalid input
 */
export class ValidationError extends AppError {
  constructor(
    message: string,
    options: Omit<ConstructorParameters<typeof AppError>[1], 'category'> = {}
  ) {
    super(message, {
      ...options,
      category: ErrorCategory.VALIDATION,
      severity: options.severity || ErrorSeverity.WARNING,
    });
    this.name = 'ValidationError';
  }
}

/**
 * Pipeline error for pipeline-specific failures
 */
export class PipelineError extends AppError {
  constructor(
    message: string,
    options: Omit<ConstructorParameters<typeof AppError>[1], 'category'> = {}
  ) {
    super(message, {
      ...options,
      category: ErrorCategory.PIPELINE,
      severity: options.severity || ErrorSeverity.ERROR,
    });
    this.name = 'PipelineError';
  }
}

/**
 * Authentication error
 */
export class AuthenticationError extends AppError {
  constructor(
    message: string,
    options: Omit<ConstructorParameters<typeof AppError>[1], 'category'> = {}
  ) {
    super(message, {
      ...options,
      category: ErrorCategory.AUTHENTICATION,
      severity: options.severity || ErrorSeverity.ERROR,
    });
    this.name = 'AuthenticationError';
  }
}

/**
 * Map error code to category
 */
function mapErrorCodeToCategory(code?: ErrorCode): ErrorCategory {
  if (!code) return ErrorCategory.UNKNOWN;

  if (code.startsWith('NETWORK_')) return ErrorCategory.NETWORK;
  if (code.startsWith('VALIDATION_')) return ErrorCategory.VALIDATION;
  if (code.startsWith('LLM_')) return ErrorCategory.LLM;
  if (code.startsWith('PIPELINE_')) return ErrorCategory.PIPELINE;
  if (code.startsWith('AUTH_')) return ErrorCategory.AUTHENTICATION;
  if (code.startsWith('CHECKPOINT_')) return ErrorCategory.CHECKPOINT;
  if (code.startsWith('GRAPH_')) return ErrorCategory.GRAPH;
  if (code.startsWith('AGENT_')) return ErrorCategory.AGENT_POOL;
  if (code.startsWith('APPROVAL_')) return ErrorCategory.HUMAN_APPROVAL;
  if (code.startsWith('CONFIG_')) return ErrorCategory.CONFIGURATION;

  return ErrorCategory.UNKNOWN;
}

/**
 * Map category to severity
 */
function mapCategoryToSeverity(category: ErrorCategory): ErrorSeverity {
  switch (category) {
    case ErrorCategory.VALIDATION:
      return ErrorSeverity.WARNING;
    case ErrorCategory.NETWORK:
    case ErrorCategory.LLM:
      return ErrorSeverity.ERROR;
    case ErrorCategory.PIPELINE:
    case ErrorCategory.GRAPH:
      return ErrorSeverity.CRITICAL;
    default:
      return ErrorSeverity.ERROR;
  }
}

/**
 * Error display options for UI components
 */
export interface ErrorDisplayOptions {
  title?: string;
  message: string;
  severity: ErrorSeverity;
  category?: ErrorCategory;
  dismissible?: boolean;
  autoHideDuration?: number;
  showRetry?: boolean;
  onRetry?: () => void;
  recoverySuggestion?: string;
}

/**
 * Create error display options from AppError
 */
export function createErrorDisplay(error: AppError): ErrorDisplayOptions {
  return {
    title: getCategoryTitle(error.category),
    message: error.message,
    severity: error.severity,
    category: error.category,
    dismissible: error.severity !== ErrorSeverity.CRITICAL,
    autoHideDuration: error.severity === ErrorSeverity.INFO ? 3000 : undefined,
    showRetry: isRetryableError(error.category),
    recoverySuggestion: error.recoverySuggestion,
  };
}

/**
 * Get display title for error category
 */
function getCategoryTitle(category: ErrorCategory): string {
  switch (category) {
    case ErrorCategory.NETWORK:
      return 'Connection Error';
    case ErrorCategory.VALIDATION:
      return 'Validation Error';
    case ErrorCategory.LLM:
      return 'AI Service Error';
    case ErrorCategory.PIPELINE:
      return 'Pipeline Error';
    case ErrorCategory.AUTHENTICATION:
      return 'Authentication Error';
    case ErrorCategory.CHECKPOINT:
      return 'Checkpoint Error';
    case ErrorCategory.GRAPH:
      return 'Graph Execution Error';
    case ErrorCategory.AGENT_POOL:
      return 'Agent Pool Error';
    case ErrorCategory.HUMAN_APPROVAL:
      return 'Approval Error';
    case ErrorCategory.CONFIGURATION:
      return 'Configuration Error';
    default:
      return 'Error';
  }
}

/**
 * Determine if error category is retryable
 */
function isRetryableError(category: ErrorCategory): boolean {
  return [
    ErrorCategory.NETWORK,
    ErrorCategory.LLM,
    ErrorCategory.AGENT_POOL,
  ].includes(category);
}
