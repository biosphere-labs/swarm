/**
 * API client with error handling and retry logic.
 *
 * Provides a robust HTTP client for communicating with the backend API
 * with automatic retry, error handling, and request/response transformation.
 */

import {
  AppError,
  NetworkError,
  ValidationError,
  ApiErrorResponse,
  ErrorCategory,
  ErrorSeverity,
} from '@/types/errors';

/**
 * API client configuration
 */
export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  maxRetryDelay?: number;
  onError?: (error: AppError) => void;
}

/**
 * Request options
 */
export interface RequestOptions extends RequestInit {
  timeout?: number;
  retries?: number;
  params?: Record<string, string | number | boolean>;
}

/**
 * Retry configuration
 */
interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  retryableStatuses: number[];
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  baseDelay: 1000,
  maxDelay: 30000,
  retryableStatuses: [408, 429, 500, 502, 503, 504],
};

/**
 * Calculate exponential backoff delay with jitter
 */
function calculateBackoff(attempt: number, baseDelay: number, maxDelay: number): number {
  const exponentialDelay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
  // Add jitter (±25%)
  const jitter = exponentialDelay * 0.25 * (Math.random() * 2 - 1);
  return Math.max(0, exponentialDelay + jitter);
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Check if error is retryable
 */
function isRetryableError(status: number, category: ErrorCategory): boolean {
  return (
    DEFAULT_RETRY_CONFIG.retryableStatuses.includes(status) ||
    category === ErrorCategory.NETWORK ||
    category === ErrorCategory.LLM
  );
}

/**
 * API Client class
 */
export class ApiClient {
  private baseUrl: string;
  private timeout: number;
  private retryConfig: RetryConfig;
  private onError?: (error: AppError) => void;

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = config.timeout || 30000;
    this.retryConfig = {
      maxAttempts: config.retries || DEFAULT_RETRY_CONFIG.maxAttempts,
      baseDelay: config.retryDelay || DEFAULT_RETRY_CONFIG.baseDelay,
      maxDelay: config.maxRetryDelay || DEFAULT_RETRY_CONFIG.maxDelay,
      retryableStatuses: DEFAULT_RETRY_CONFIG.retryableStatuses,
    };
    this.onError = config.onError;
  }

  /**
   * Make HTTP request with retry logic
   */
  private async request<T>(
    path: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const url = this.buildUrl(path, options.params);
    const requestOptions = this.buildRequestOptions(options);
    const maxAttempts = options.retries ?? this.retryConfig.maxAttempts;

    let lastError: AppError | null = null;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await this.fetchWithTimeout(url, requestOptions);
        return await this.handleResponse<T>(response);
      } catch (error) {
        lastError = this.handleError(error);

        // Don't retry if not retryable or last attempt
        if (
          attempt >= maxAttempts - 1 ||
          !isRetryableError(
            lastError.code?.startsWith('HTTP_')
              ? parseInt(lastError.code.replace('HTTP_', ''))
              : 0,
            lastError.category
          )
        ) {
          break;
        }

        // Calculate delay and retry
        const delay = calculateBackoff(
          attempt,
          this.retryConfig.baseDelay,
          this.retryConfig.maxDelay
        );

        console.warn(
          `Request failed (attempt ${attempt + 1}/${maxAttempts}): ${lastError.message}. ` +
          `Retrying in ${delay}ms...`
        );

        await sleep(delay);
      }
    }

    // Call error callback if provided
    if (lastError && this.onError) {
      this.onError(lastError);
    }

    throw lastError;
  }

  /**
   * Build full URL with query parameters
   */
  private buildUrl(path: string, params?: Record<string, string | number | boolean>): string {
    const url = `${this.baseUrl}${path.startsWith('/') ? path : `/${path}`}`;

    if (!params || Object.keys(params).length === 0) {
      return url;
    }

    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      searchParams.append(key, String(value));
    });

    return `${url}?${searchParams.toString()}`;
  }

  /**
   * Build request options
   */
  private buildRequestOptions(options: RequestOptions): RequestInit {
    const headers = new Headers(options.headers);

    // Set default headers if not present
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    if (!headers.has('Accept')) {
      headers.set('Accept', 'application/json');
    }

    // Add request ID for tracking
    if (!headers.has('X-Request-ID')) {
      headers.set('X-Request-ID', crypto.randomUUID());
    }

    return {
      ...options,
      headers,
    };
  }

  /**
   * Fetch with timeout
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit
  ): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeout);
      return response;
    } catch (error) {
      clearTimeout(timeout);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new NetworkError('Request timeout', {
          code: 'NETWORK_1002',
          severity: ErrorSeverity.ERROR,
          details: { timeout: this.timeout },
          recoverySuggestion: 'Please try again or check your connection',
        });
      }
      throw error;
    }
  }

  /**
   * Handle response
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    // Handle successful responses
    if (response.ok) {
      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      }

      // Return text for non-JSON responses
      return (await response.text()) as unknown as T;
    }

    // Handle error responses
    let errorData: ApiErrorResponse | null = null;

    try {
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        errorData = await response.json();
      }
    } catch (e) {
      // Failed to parse error response
    }

    // Create error from backend response if available
    if (errorData && 'error' in errorData) {
      throw AppError.fromBackendError(errorData);
    }

    // Create generic HTTP error
    throw new NetworkError(
      `HTTP ${response.status}: ${response.statusText}`,
      {
        code: `HTTP_${response.status}`,
        severity: ErrorSeverity.ERROR,
        details: {
          status: response.status,
          statusText: response.statusText,
          url: response.url,
        },
      }
    );
  }

  /**
   * Handle errors
   */
  private handleError(error: unknown): AppError {
    if (error instanceof AppError) {
      return error;
    }

    if (error instanceof TypeError && error.message.includes('fetch')) {
      return new NetworkError('Network connection failed', {
        code: 'NETWORK_1001',
        severity: ErrorSeverity.ERROR,
        originalError: error as Error,
        recoverySuggestion: 'Please check your internet connection and try again',
      });
    }

    return AppError.fromUnknown(error, 'API request failed');
  }

  /**
   * GET request
   */
  async get<T>(path: string, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(path, { ...options, method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T>(
    path: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T>(
    path: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PATCH request
   */
  async patch<T>(
    path: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(path: string, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(path, { ...options, method: 'DELETE' });
  }
}

/**
 * Create default API client instance
 */
export function createApiClient(config?: Partial<ApiClientConfig>): ApiClient {
  const baseUrl = config?.baseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  return new ApiClient({
    baseUrl,
    timeout: config?.timeout || 30000,
    retries: config?.retries || 3,
    retryDelay: config?.retryDelay || 1000,
    maxRetryDelay: config?.maxRetryDelay || 30000,
    onError: config?.onError,
  });
}

/**
 * Default API client instance
 */
export const apiClient = createApiClient();
