/**
 * API configuration for backend communication.
 *
 * Centralizes backend URL configuration and provides utilities
 * for building backend API endpoints.
 */

/**
 * Backend API configuration
 */
export interface BackendApiConfig {
  baseUrl: string;
  timeout: number;
}

/**
 * Get backend API base URL from environment or use default
 */
export function getBackendUrl(): string {
  // In Next.js API routes, we can use process.env directly
  // For client-side, use NEXT_PUBLIC_ prefix
  if (typeof window === 'undefined') {
    // Server-side (API routes)
    return process.env.BACKEND_API_URL || 'http://localhost:8000';
  }

  // Client-side
  return process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';
}

/**
 * Get backend API configuration
 */
export function getBackendConfig(): BackendApiConfig {
  return {
    baseUrl: getBackendUrl(),
    timeout: parseInt(process.env.BACKEND_API_TIMEOUT || '30000', 10),
  };
}

/**
 * Build backend API endpoint URL
 */
export function buildBackendUrl(path: string): string {
  const baseUrl = getBackendUrl().replace(/\/$/, ''); // Remove trailing slash
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${cleanPath}`;
}

/**
 * Default request timeout in milliseconds
 */
export const DEFAULT_TIMEOUT = 30000;

/**
 * Request timeout for long-running operations
 */
export const LONG_TIMEOUT = 120000;

/**
 * Backend API endpoints
 */
export const BACKEND_ENDPOINTS = {
  // Pipeline control
  PIPELINE_START: '/pipeline/start',
  PIPELINE_APPROVE: (runId: string) => `/pipeline/${runId}/approve`,
  PIPELINE_REJECT: (runId: string) => `/pipeline/${runId}/reject`,
  PIPELINE_MODIFY: (runId: string) => `/pipeline/${runId}/modify`,
  PIPELINE_BACKTRACK: (runId: string) => `/pipeline/${runId}/backtrack`,
  PIPELINE_ADD_CONTEXT: (runId: string) => `/pipeline/${runId}/context`,
  PIPELINE_REQUEST_ALTERNATIVES: (runId: string) => `/pipeline/${runId}/alternatives`,
  PIPELINE_STATUS: (runId: string) => `/pipeline/${runId}/status`,
  PIPELINE_STREAM: (runId: string) => `/pipeline/${runId}/stream`,
} as const;
