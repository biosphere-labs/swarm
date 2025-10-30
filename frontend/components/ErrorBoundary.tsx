/**
 * Error Boundary component for catching React errors.
 *
 * Provides graceful error handling for the entire application
 * with fallback UI and error recovery options.
 */

'use client';

import React, { Component, ReactNode } from 'react';
import { AppError, ErrorCategory, ErrorSeverity, createErrorDisplay } from '@/types/errors';

/**
 * Error boundary props
 */
export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: AppError, reset: () => void) => ReactNode;
  onError?: (error: AppError, errorInfo: React.ErrorInfo) => void;
  resetKeys?: Array<string | number>;
}

/**
 * Error boundary state
 */
interface ErrorBoundaryState {
  error: AppError | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * Default error fallback UI
 */
function DefaultErrorFallback({
  error,
  reset,
}: {
  error: AppError;
  reset: () => void;
}) {
  const display = createErrorDisplay(error);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
        <div className="mb-4 flex items-center">
          <div className={`rounded-full p-2 ${getSeverityColor(error.severity)}`}>
            {getSeverityIcon(error.severity)}
          </div>
          <h1 className="ml-3 text-xl font-semibold text-gray-900">
            {display.title}
          </h1>
        </div>

        <div className="mb-4 space-y-2">
          <p className="text-gray-700">{error.message}</p>

          {error.recoverySuggestion && (
            <div className="rounded-md bg-blue-50 p-3">
              <p className="text-sm text-blue-800">
                <strong>Suggestion:</strong> {error.recoverySuggestion}
              </p>
            </div>
          )}

          {error.code && (
            <p className="text-xs text-gray-500">Error Code: {error.code}</p>
          )}
        </div>

        <div className="flex space-x-2">
          <button
            onClick={reset}
            className="flex-1 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Try Again
          </button>
          <button
            onClick={() => (window.location.href = '/')}
            className="flex-1 rounded-md border border-gray-300 bg-white px-4 py-2 text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Go Home
          </button>
        </div>

        {process.env.NODE_ENV === 'development' && error.stack && (
          <details className="mt-4">
            <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-900">
              Show Error Details
            </summary>
            <pre className="mt-2 overflow-auto rounded bg-gray-100 p-2 text-xs text-gray-800">
              {error.stack}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}

/**
 * Get severity color classes
 */
function getSeverityColor(severity: ErrorSeverity): string {
  switch (severity) {
    case ErrorSeverity.INFO:
      return 'bg-blue-100 text-blue-600';
    case ErrorSeverity.WARNING:
      return 'bg-yellow-100 text-yellow-600';
    case ErrorSeverity.ERROR:
      return 'bg-red-100 text-red-600';
    case ErrorSeverity.CRITICAL:
      return 'bg-red-200 text-red-700';
    default:
      return 'bg-gray-100 text-gray-600';
  }
}

/**
 * Get severity icon
 */
function getSeverityIcon(severity: ErrorSeverity): ReactNode {
  const iconClass = 'h-6 w-6';

  switch (severity) {
    case ErrorSeverity.INFO:
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    case ErrorSeverity.WARNING:
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      );
    case ErrorSeverity.ERROR:
    case ErrorSeverity.CRITICAL:
      return (
        <svg className={iconClass} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    default:
      return null;
  }
}

/**
 * Error Boundary Component
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Convert error to AppError
    const appError =
      error instanceof AppError
        ? error
        : new AppError(error.message, {
            category: ErrorCategory.UNKNOWN,
            severity: ErrorSeverity.ERROR,
            originalError: error,
          });

    return { error: appError };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Convert to AppError if needed
    const appError =
      error instanceof AppError
        ? error
        : new AppError(error.message, {
            category: ErrorCategory.UNKNOWN,
            severity: ErrorSeverity.ERROR,
            originalError: error,
          });

    this.setState({ errorInfo });

    // Call error callback if provided
    if (this.props.onError) {
      this.props.onError(appError, errorInfo);
    }

    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetKeys } = this.props;
    const { error } = this.state;

    // Reset error state if reset keys change
    if (
      error &&
      resetKeys &&
      prevProps.resetKeys &&
      !areArraysEqual(resetKeys, prevProps.resetKeys)
    ) {
      this.reset();
    }
  }

  reset = () => {
    this.setState({ error: null, errorInfo: null });
  };

  render() {
    const { error } = this.state;
    const { children, fallback } = this.props;

    if (error) {
      // Use custom fallback if provided
      if (fallback) {
        return fallback(error, this.reset);
      }

      // Use default fallback
      return <DefaultErrorFallback error={error} reset={this.reset} />;
    }

    return children;
  }
}

/**
 * Compare arrays for equality
 */
function areArraysEqual(
  arr1: Array<string | number>,
  arr2: Array<string | number>
): boolean {
  if (arr1.length !== arr2.length) return false;
  return arr1.every((value, index) => value === arr2[index]);
}

/**
 * Hook-based error boundary using the component
 */
export function useErrorBoundary() {
  const [error, setError] = React.useState<Error | null>(null);

  if (error) {
    throw error;
  }

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const throwError = React.useCallback((error: Error) => {
    setError(error);
  }, []);

  return { throwError, resetError };
}

/**
 * Higher-order component to wrap components with error boundary
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  );

  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name || 'Component'})`;

  return WrappedComponent;
}
