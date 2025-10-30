/**
 * Tests for error types and utilities.
 */

import {
  AppError,
  NetworkError,
  ValidationError,
  PipelineError,
  AuthenticationError,
  ErrorSeverity,
  ErrorCategory,
  createErrorDisplay,
} from '@/types/errors';

describe('AppError', () => {
  it('creates basic error', () => {
    const error = new AppError('Test error');

    expect(error.message).toBe('Test error');
    expect(error.category).toBe(ErrorCategory.UNKNOWN);
    expect(error.severity).toBe(ErrorSeverity.ERROR);
    expect(error.timestamp).toBeInstanceOf(Date);
  });

  it('creates error with options', () => {
    const error = new AppError('Test error', {
      category: ErrorCategory.NETWORK,
      severity: ErrorSeverity.WARNING,
      code: 'NETWORK_1001',
      details: { field: 'value' },
      recoverySuggestion: 'Retry the operation',
      requestId: 'req-123',
    });

    expect(error.category).toBe(ErrorCategory.NETWORK);
    expect(error.severity).toBe(ErrorSeverity.WARNING);
    expect(error.code).toBe('NETWORK_1001');
    expect(error.details).toEqual({ field: 'value' });
    expect(error.recoverySuggestion).toBe('Retry the operation');
    expect(error.requestId).toBe('req-123');
  });

  it('creates error from backend response', () => {
    const backendError = {
      success: false as const,
      error: {
        type: 'NetworkError',
        message: 'Connection failed',
        code: 'NETWORK_1001',
        details: { url: 'https://api.example.com' },
        recovery_suggestion: 'Check your connection',
      },
      request_id: 'req-456',
    };

    const error = AppError.fromBackendError(backendError);

    expect(error.message).toBe('Connection failed');
    expect(error.category).toBe(ErrorCategory.NETWORK);
    expect(error.code).toBe('NETWORK_1001');
    expect(error.details).toEqual({ url: 'https://api.example.com' });
    expect(error.recoverySuggestion).toBe('Check your connection');
    expect(error.requestId).toBe('req-456');
  });

  it('creates error from unknown error', () => {
    const originalError = new Error('Original error');
    const error = AppError.fromUnknown(originalError);

    expect(error).toBeInstanceOf(AppError);
    expect(error.message).toBe('Original error');
    expect(error.category).toBe(ErrorCategory.UNKNOWN);
    expect(error.originalError).toBe(originalError);
  });

  it('creates error from AppError', () => {
    const originalError = new AppError('Original', {
      category: ErrorCategory.VALIDATION,
    });
    const error = AppError.fromUnknown(originalError);

    expect(error).toBe(originalError);
  });

  it('converts to JSON', () => {
    const error = new AppError('Test error', {
      category: ErrorCategory.PIPELINE,
      code: 'PIPELINE_4001',
      details: { stage: 'decomposition' },
    });

    const json = error.toJSON();

    expect(json.name).toBe('AppError');
    expect(json.message).toBe('Test error');
    expect(json.category).toBe(ErrorCategory.PIPELINE);
    expect(json.code).toBe('PIPELINE_4001');
    expect(json.details).toEqual({ stage: 'decomposition' });
    expect(json.timestamp).toBeDefined();
  });
});

describe('Specialized Error Classes', () => {
  it('creates NetworkError', () => {
    const error = new NetworkError('Connection failed');

    expect(error).toBeInstanceOf(AppError);
    expect(error.category).toBe(ErrorCategory.NETWORK);
    expect(error.message).toBe('Connection failed');
  });

  it('creates ValidationError', () => {
    const error = new ValidationError('Invalid input');

    expect(error).toBeInstanceOf(AppError);
    expect(error.category).toBe(ErrorCategory.VALIDATION);
    expect(error.severity).toBe(ErrorSeverity.WARNING);
  });

  it('creates PipelineError', () => {
    const error = new PipelineError('Pipeline failed');

    expect(error).toBeInstanceOf(AppError);
    expect(error.category).toBe(ErrorCategory.PIPELINE);
  });

  it('creates AuthenticationError', () => {
    const error = new AuthenticationError('Invalid token');

    expect(error).toBeInstanceOf(AppError);
    expect(error.category).toBe(ErrorCategory.AUTHENTICATION);
  });
});

describe('createErrorDisplay', () => {
  it('creates display options for network error', () => {
    const error = new NetworkError('Connection failed');
    const display = createErrorDisplay(error);

    expect(display.title).toBe('Connection Error');
    expect(display.message).toBe('Connection failed');
    expect(display.severity).toBe(ErrorSeverity.ERROR);
    expect(display.showRetry).toBe(true);
  });

  it('creates display options for validation error', () => {
    const error = new ValidationError('Invalid email');
    const display = createErrorDisplay(error);

    expect(display.title).toBe('Validation Error');
    expect(display.severity).toBe(ErrorSeverity.WARNING);
    expect(display.dismissible).toBe(true);
  });

  it('includes recovery suggestion', () => {
    const error = new AppError('Error occurred', {
      recoverySuggestion: 'Try again later',
    });
    const display = createErrorDisplay(error);

    expect(display.recoverySuggestion).toBe('Try again later');
  });
});

describe('Error Code Mapping', () => {
  it('maps network error codes', () => {
    const error = AppError.fromBackendError({
      success: false,
      error: {
        type: 'NetworkError',
        message: 'Failed',
        code: 'NETWORK_1001',
      },
    });

    expect(error.category).toBe(ErrorCategory.NETWORK);
  });

  it('maps validation error codes', () => {
    const error = AppError.fromBackendError({
      success: false,
      error: {
        type: 'ValidationError',
        message: 'Invalid',
        code: 'VALIDATION_2001',
      },
    });

    expect(error.category).toBe(ErrorCategory.VALIDATION);
  });

  it('maps LLM error codes', () => {
    const error = AppError.fromBackendError({
      success: false,
      error: {
        type: 'LLMError',
        message: 'API failed',
        code: 'LLM_3001',
      },
    });

    expect(error.category).toBe(ErrorCategory.LLM);
  });

  it('maps pipeline error codes', () => {
    const error = AppError.fromBackendError({
      success: false,
      error: {
        type: 'PipelineError',
        message: 'State corrupted',
        code: 'PIPELINE_4001',
      },
    });

    expect(error.category).toBe(ErrorCategory.PIPELINE);
  });

  it('handles unknown error codes', () => {
    const error = AppError.fromBackendError({
      success: false,
      error: {
        type: 'UnknownError',
        message: 'Unknown',
        code: 'UNKNOWN_0000',
      },
    });

    expect(error.category).toBe(ErrorCategory.UNKNOWN);
  });
});
