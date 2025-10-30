/**
 * Error Toast notification component.
 *
 * Provides toast notifications for displaying errors and other messages
 * with automatic dismissal and retry functionality.
 */

'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { AppError, ErrorSeverity, ErrorDisplayOptions, createErrorDisplay } from '@/types/errors';

/**
 * Toast notification data
 */
export interface Toast {
  id: string;
  title?: string;
  message: string;
  severity: ErrorSeverity;
  dismissible: boolean;
  autoHideDuration?: number;
  showRetry?: boolean;
  onRetry?: () => void;
  createdAt: number;
}

/**
 * Toast context type
 */
interface ToastContextType {
  toasts: Toast[];
  showToast: (options: Omit<Toast, 'id' | 'createdAt'>) => string;
  showError: (error: AppError) => string;
  dismissToast: (id: string) => void;
  clearAll: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

/**
 * Toast Provider Component
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback(
    (options: Omit<Toast, 'id' | 'createdAt'>): string => {
      const id = crypto.randomUUID();
      const toast: Toast = {
        ...options,
        id,
        createdAt: Date.now(),
      };

      setToasts((prev) => [...prev, toast]);

      // Auto-dismiss if duration is set
      if (options.autoHideDuration) {
        setTimeout(() => {
          dismissToast(id);
        }, options.autoHideDuration);
      }

      return id;
    },
    []
  );

  const showError = useCallback(
    (error: AppError): string => {
      const display = createErrorDisplay(error);
      return showToast({
        title: display.title,
        message: display.message,
        severity: display.severity,
        dismissible: display.dismissible ?? true,
        autoHideDuration: display.autoHideDuration,
        showRetry: display.showRetry,
        onRetry: display.onRetry,
      });
    },
    [showToast]
  );

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, showToast, showError, dismissToast, clearAll }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

/**
 * Toast Container Component
 */
function ToastContainer() {
  const context = useContext(ToastContext);
  if (!context) return null;

  const { toasts, dismissToast } = context;

  return (
    <div
      className="pointer-events-none fixed inset-0 z-50 flex flex-col items-end justify-end gap-2 p-4"
      aria-live="polite"
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <ToastNotification
          key={toast.id}
          toast={toast}
          onDismiss={() => dismissToast(toast.id)}
        />
      ))}
    </div>
  );
}

/**
 * Individual Toast Notification
 */
function ToastNotification({
  toast,
  onDismiss,
}: {
  toast: Toast;
  onDismiss: () => void;
}) {
  const [isExiting, setIsExiting] = React.useState(false);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(onDismiss, 300); // Match animation duration
  };

  const handleRetry = () => {
    if (toast.onRetry) {
      toast.onRetry();
      handleDismiss();
    }
  };

  return (
    <div
      className={`pointer-events-auto transform transition-all duration-300 ease-in-out ${
        isExiting
          ? 'translate-x-full opacity-0'
          : 'translate-x-0 opacity-100'
      }`}
      role="alert"
    >
      <div
        className={`min-w-[320px] max-w-md rounded-lg shadow-lg ${getSeverityClasses(
          toast.severity
        )}`}
      >
        <div className="flex items-start p-4">
          <div className="flex-shrink-0">{getSeverityIcon(toast.severity)}</div>

          <div className="ml-3 flex-1">
            {toast.title && (
              <h3 className="text-sm font-semibold">{toast.title}</h3>
            )}
            <p className={`text-sm ${toast.title ? 'mt-1' : ''}`}>
              {toast.message}
            </p>

            {toast.showRetry && toast.onRetry && (
              <button
                onClick={handleRetry}
                className="mt-2 text-sm font-medium underline hover:no-underline focus:outline-none"
              >
                Retry
              </button>
            )}
          </div>

          {toast.dismissible && (
            <button
              onClick={handleDismiss}
              className="ml-4 inline-flex flex-shrink-0 rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2"
              aria-label="Dismiss"
            >
              <svg
                className="h-5 w-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Get severity CSS classes
 */
function getSeverityClasses(severity: ErrorSeverity): string {
  switch (severity) {
    case ErrorSeverity.INFO:
      return 'bg-blue-50 text-blue-900 border border-blue-200';
    case ErrorSeverity.WARNING:
      return 'bg-yellow-50 text-yellow-900 border border-yellow-200';
    case ErrorSeverity.ERROR:
      return 'bg-red-50 text-red-900 border border-red-200';
    case ErrorSeverity.CRITICAL:
      return 'bg-red-100 text-red-950 border-2 border-red-500';
    default:
      return 'bg-gray-50 text-gray-900 border border-gray-200';
  }
}

/**
 * Get severity icon
 */
function getSeverityIcon(severity: ErrorSeverity): ReactNode {
  const iconClass = 'h-5 w-5';

  switch (severity) {
    case ErrorSeverity.INFO:
      return (
        <svg
          className={`${iconClass} text-blue-600`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
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
        <svg
          className={`${iconClass} text-yellow-600`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
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
        <svg
          className={`${iconClass} text-red-600`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
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
 * Hook to use toast notifications
 */
export function useToast() {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  return context;
}

/**
 * Helper hook for error toasts
 */
export function useErrorToast() {
  const { showError, showToast } = useToast();

  const showSuccess = useCallback(
    (message: string, title?: string) => {
      return showToast({
        title,
        message,
        severity: ErrorSeverity.INFO,
        dismissible: true,
        autoHideDuration: 3000,
      });
    },
    [showToast]
  );

  const showWarning = useCallback(
    (message: string, title?: string) => {
      return showToast({
        title,
        message,
        severity: ErrorSeverity.WARNING,
        dismissible: true,
        autoHideDuration: 5000,
      });
    },
    [showToast]
  );

  return {
    showError,
    showSuccess,
    showWarning,
  };
}
