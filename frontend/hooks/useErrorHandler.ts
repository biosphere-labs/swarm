/**
 * Error handler hook for consistent error handling in components.
 *
 * Provides utilities for handling errors with logging, toast notifications,
 * and error recovery.
 */

'use client';

import { useCallback, useState } from 'react';
import { AppError, ErrorCategory, ErrorSeverity } from '@/types/errors';
import { useToast } from '@/components/ErrorToast';

/**
 * Error handler options
 */
export interface ErrorHandlerOptions {
  showToast?: boolean;
  logToConsole?: boolean;
  rethrow?: boolean;
  context?: string;
  onError?: (error: AppError) => void;
}

/**
 * Error handler state
 */
export interface ErrorHandlerState {
  error: AppError | null;
  isError: boolean;
  clearError: () => void;
}

/**
 * Hook for handling errors with toast notifications and logging
 */
export function useErrorHandler(
  defaultOptions: ErrorHandlerOptions = {}
): {
  handleError: (error: unknown, options?: ErrorHandlerOptions) => void;
  error: AppError | null;
  isError: boolean;
  clearError: () => void;
} {
  const [error, setError] = useState<AppError | null>(null);
  const { showError: showErrorToast } = useToast();

  const handleError = useCallback(
    (error: unknown, options: ErrorHandlerOptions = {}) => {
      const mergedOptions = { ...defaultOptions, ...options };

      // Convert to AppError
      const appError = AppError.fromUnknown(error, mergedOptions.context);

      // Set error state
      setError(appError);

      // Show toast notification
      if (mergedOptions.showToast !== false) {
        showErrorToast(appError);
      }

      // Log to console in development
      if (
        mergedOptions.logToConsole !== false &&
        process.env.NODE_ENV === 'development'
      ) {
        console.error('Error handled by useErrorHandler:', appError.toJSON());
      }

      // Call custom error callback
      if (mergedOptions.onError) {
        mergedOptions.onError(appError);
      }

      // Rethrow if requested
      if (mergedOptions.rethrow) {
        throw appError;
      }
    },
    [defaultOptions, showErrorToast]
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    handleError,
    error,
    isError: error !== null,
    clearError,
  };
}

/**
 * Hook for handling async operations with error handling
 */
export function useAsyncError<T extends (...args: any[]) => Promise<any>>(
  asyncFn: T,
  options: ErrorHandlerOptions = {}
): {
  execute: (...args: Parameters<T>) => Promise<ReturnType<T> | null>;
  loading: boolean;
  error: AppError | null;
  data: Awaited<ReturnType<T>> | null;
  reset: () => void;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AppError | null>(null);
  const [data, setData] = useState<Awaited<ReturnType<T>> | null>(null);
  const { showError: showErrorToast } = useToast();

  const execute = useCallback(
    async (...args: Parameters<T>): Promise<ReturnType<T> | null> => {
      setLoading(true);
      setError(null);

      try {
        const result = await asyncFn(...args);
        setData(result);
        return result;
      } catch (err) {
        const appError = AppError.fromUnknown(err, options.context);
        setError(appError);

        // Show toast notification
        if (options.showToast !== false) {
          showErrorToast(appError);
        }

        // Log to console in development
        if (
          options.logToConsole !== false &&
          process.env.NODE_ENV === 'development'
        ) {
          console.error('Error in async operation:', appError.toJSON());
        }

        // Call custom error callback
        if (options.onError) {
          options.onError(appError);
        }

        if (options.rethrow) {
          throw appError;
        }

        return null;
      } finally {
        setLoading(false);
      }
    },
    [asyncFn, options, showErrorToast]
  );

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);

  return {
    execute,
    loading,
    error,
    data,
    reset,
  };
}

/**
 * Hook for retry logic with error handling
 */
export function useRetry<T extends (...args: any[]) => Promise<any>>(
  asyncFn: T,
  options: {
    maxAttempts?: number;
    delay?: number;
    backoff?: boolean;
    retryableErrors?: ErrorCategory[];
  } & ErrorHandlerOptions = {}
): {
  execute: (...args: Parameters<T>) => Promise<ReturnType<T> | null>;
  loading: boolean;
  error: AppError | null;
  data: Awaited<ReturnType<T>> | null;
  attempt: number;
  reset: () => void;
} {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = true,
    retryableErrors = [
      ErrorCategory.NETWORK,
      ErrorCategory.LLM,
      ErrorCategory.AGENT_POOL,
    ],
    ...errorOptions
  } = options;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AppError | null>(null);
  const [data, setData] = useState<Awaited<ReturnType<T>> | null>(null);
  const [attempt, setAttempt] = useState(0);
  const { showError: showErrorToast } = useToast();

  const execute = useCallback(
    async (...args: Parameters<T>): Promise<ReturnType<T> | null> => {
      setLoading(true);
      setError(null);
      setAttempt(0);

      for (let i = 0; i < maxAttempts; i++) {
        setAttempt(i + 1);

        try {
          const result = await asyncFn(...args);
          setData(result);
          setLoading(false);
          return result;
        } catch (err) {
          const appError = AppError.fromUnknown(err, errorOptions.context);
          setError(appError);

          // Check if error is retryable
          const isRetryable = retryableErrors.includes(appError.category);
          const isLastAttempt = i >= maxAttempts - 1;

          if (!isRetryable || isLastAttempt) {
            // Show toast notification on final failure
            if (errorOptions.showToast !== false) {
              showErrorToast(appError);
            }

            // Log to console
            if (
              errorOptions.logToConsole !== false &&
              process.env.NODE_ENV === 'development'
            ) {
              console.error('Error in retry operation:', appError.toJSON());
            }

            // Call custom error callback
            if (errorOptions.onError) {
              errorOptions.onError(appError);
            }

            setLoading(false);

            if (errorOptions.rethrow) {
              throw appError;
            }

            return null;
          }

          // Calculate delay with optional backoff
          const currentDelay = backoff ? delay * Math.pow(2, i) : delay;

          console.warn(
            `Attempt ${i + 1}/${maxAttempts} failed. Retrying in ${currentDelay}ms...`
          );

          // Wait before retrying
          await new Promise((resolve) => setTimeout(resolve, currentDelay));
        }
      }

      setLoading(false);
      return null;
    },
    [
      asyncFn,
      maxAttempts,
      delay,
      backoff,
      retryableErrors,
      errorOptions,
      showErrorToast,
    ]
  );

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
    setAttempt(0);
  }, []);

  return {
    execute,
    loading,
    error,
    data,
    attempt,
    reset,
  };
}

/**
 * Hook for graceful degradation with fallback values
 */
export function useGracefulDegradation<T>(
  fetchFn: () => Promise<T>,
  fallbackValue: T,
  options: ErrorHandlerOptions = {}
): {
  data: T;
  loading: boolean;
  error: AppError | null;
  isUsingFallback: boolean;
  retry: () => Promise<void>;
} {
  const [data, setData] = useState<T>(fallbackValue);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AppError | null>(null);
  const [isUsingFallback, setIsUsingFallback] = useState(true);
  const { handleError } = useErrorHandler(options);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchFn();
      setData(result);
      setIsUsingFallback(false);
    } catch (err) {
      const appError = AppError.fromUnknown(err, options.context);
      setError(appError);
      setData(fallbackValue);
      setIsUsingFallback(true);

      // Handle error (with toast if enabled)
      handleError(err, {
        ...options,
        showToast: options.showToast !== false,
        severity: ErrorSeverity.WARNING,
      } as any);
    } finally {
      setLoading(false);
    }
  }, [fetchFn, fallbackValue, options, handleError]);

  // Fetch on mount
  React.useEffect(() => {
    fetch();
  }, [fetch]);

  return {
    data,
    loading,
    error,
    isUsingFallback,
    retry: fetch,
  };
}

// Re-export React to avoid import issues
import React from 'react';
