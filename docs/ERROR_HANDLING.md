# Error Handling Documentation

## Overview

The Decomposition Pipeline implements comprehensive error handling and fallback strategies across both backend and frontend. This document describes the error handling architecture, error types, retry strategies, and best practices.

## Table of Contents

1. [Backend Error Handling](#backend-error-handling)
2. [Frontend Error Handling](#frontend-error-handling)
3. [Error Categories](#error-categories)
4. [Retry Strategies](#retry-strategies)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

---

## Backend Error Handling

### Architecture

The backend error handling system consists of:

1. **Custom Exception Classes** - Structured error types with standardized codes
2. **Error Handlers** - FastAPI exception handlers for different error types
3. **Middleware** - Request tracking and error logging middleware
4. **Retry Utilities** - Decorators for automatic retry with exponential backoff

### Error Hierarchy

```
PipelineError (base)
├── NetworkError
├── ValidationError
├── LLMError
│   ├── RateLimitError
│   └── QuotaExceededError
├── PipelineStateError
├── AuthenticationError
├── CheckpointError
├── GraphExecutionError
├── AgentPoolError
├── HumanApprovalError
├── ConfigurationError
└── TimeoutError
```

### Error Codes

All errors include standardized error codes for easy identification:

- `NETWORK_1xxx` - Network-related errors
- `VALIDATION_2xxx` - Input validation errors
- `LLM_3xxx` - LLM API errors
- `PIPELINE_4xxx` - Pipeline state errors
- `AUTH_5xxx` - Authentication errors
- `CHECKPOINT_6xxx` - Checkpoint errors
- `GRAPH_7xxx` - Graph execution errors
- `AGENT_8xxx` - Agent pool errors
- `APPROVAL_9xxx` - Human approval errors
- `CONFIG_10xxx` - Configuration errors

### Custom Exception Example

```python
from decomposition_pipeline.errors import ValidationError, ErrorCode

raise ValidationError(
    "Invalid email format",
    error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
    field_name="email",
    recovery_suggestion="Please provide a valid email address"
)
```

### Error Response Format

All API errors return a standardized JSON response:

```json
{
  "success": false,
  "error": {
    "type": "ValidationError",
    "message": "Invalid email format",
    "code": "VALIDATION_2004",
    "details": {
      "field_name": "email"
    },
    "recovery_suggestion": "Please provide a valid email address"
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Middleware

#### ErrorHandlingMiddleware

Provides request tracking and error logging:

```python
from decomposition_pipeline.middleware import ErrorHandlingMiddleware

app.add_middleware(
    ErrorHandlingMiddleware,
    enable_request_logging=True
)
```

Features:
- Automatic request ID generation
- Request/response logging
- Duration tracking
- Structured error logging

### Retry Decorators

#### Basic Retry

```python
from decomposition_pipeline.utils.retry import retry

@retry(max_attempts=3, base_delay=1.0)
def call_external_api():
    # API call that might fail
    pass
```

#### Async Retry

```python
from decomposition_pipeline.utils.retry import async_retry

@async_retry(max_attempts=3, base_delay=1.0)
async def call_llm_api():
    # Async API call
    pass
```

#### Pre-configured Decorators

```python
from decomposition_pipeline.utils.retry import (
    retry_on_network_error,
    retry_on_llm_error,
)

@retry_on_llm_error
async def generate_completion():
    # LLM call with automatic retry on rate limits
    pass
```

---

## Frontend Error Handling

### Architecture

The frontend error handling system includes:

1. **Error Types** - TypeScript error classes mirroring backend errors
2. **API Client** - HTTP client with automatic retry and error handling
3. **Error Boundary** - React component for catching rendering errors
4. **Error Toast** - Global notification system for error messages
5. **Error Handler Hooks** - React hooks for consistent error handling

### Error Types

#### AppError

Base error class for all application errors:

```typescript
import { AppError, ErrorCategory, ErrorSeverity } from '@/types/errors';

const error = new AppError('Something went wrong', {
  category: ErrorCategory.NETWORK,
  severity: ErrorSeverity.ERROR,
  code: 'NETWORK_1001',
  recoverySuggestion: 'Check your internet connection',
});
```

#### Specialized Errors

```typescript
import { NetworkError, ValidationError, PipelineError } from '@/types/errors';

// Network error
throw new NetworkError('Connection failed');

// Validation error
throw new ValidationError('Invalid email format', {
  details: { field: 'email' },
});

// Pipeline error
throw new PipelineError('Pipeline execution failed');
```

### API Client

The API client provides automatic retry and error handling:

```typescript
import { apiClient } from '@/lib/api-client';

try {
  const data = await apiClient.get('/api/v1/pipeline/status');
} catch (error) {
  // Error is automatically converted to AppError
  console.error(error);
}
```

Features:
- Automatic retry on network errors
- Exponential backoff with jitter
- Request timeout handling
- Structured error conversion

### Error Boundary

Wrap components to catch rendering errors:

```tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <YourComponent />
    </ErrorBoundary>
  );
}
```

Custom fallback UI:

```tsx
<ErrorBoundary
  fallback={(error, reset) => (
    <div>
      <h1>Error: {error.message}</h1>
      <button onClick={reset}>Try Again</button>
    </div>
  )}
>
  <YourComponent />
</ErrorBoundary>
```

### Error Toast

Global error notifications:

```tsx
import { ToastProvider, useToast } from '@/components/ErrorToast';

function App() {
  return (
    <ToastProvider>
      <YourApp />
    </ToastProvider>
  );
}

function YourComponent() {
  const { showError } = useToast();

  const handleError = (error: AppError) => {
    showError(error);
  };
}
```

### Error Handler Hooks

#### useErrorHandler

```typescript
import { useErrorHandler } from '@/hooks/useErrorHandler';

function MyComponent() {
  const { handleError, error, isError, clearError } = useErrorHandler({
    showToast: true,
    logToConsole: true,
  });

  try {
    // Some operation
  } catch (err) {
    handleError(err, { context: 'Loading data' });
  }
}
```

#### useAsyncError

```typescript
import { useAsyncError } from '@/hooks/useErrorHandler';

function MyComponent() {
  const { execute, loading, error, data } = useAsyncError(
    async () => {
      return await fetchData();
    },
    { showToast: true }
  );

  return (
    <button onClick={() => execute()} disabled={loading}>
      Load Data
    </button>
  );
}
```

#### useRetry

```typescript
import { useRetry } from '@/hooks/useErrorHandler';

function MyComponent() {
  const { execute, loading, error, attempt } = useRetry(
    async () => {
      return await fetchData();
    },
    { maxAttempts: 3, delay: 1000 }
  );

  return (
    <div>
      <button onClick={() => execute()}>Load</button>
      {loading && <p>Attempt {attempt}/3...</p>}
    </div>
  );
}
```

#### useGracefulDegradation

```typescript
import { useGracefulDegradation } from '@/hooks/useErrorHandler';

function MyComponent() {
  const { data, isUsingFallback, retry } = useGracefulDegradation(
    async () => await fetchUserData(),
    { name: 'Guest', email: '' } // Fallback value
  );

  return (
    <div>
      <p>Welcome, {data.name}!</p>
      {isUsingFallback && (
        <button onClick={retry}>Retry</button>
      )}
    </div>
  );
}
```

---

## Error Categories

### Network Errors
- Connection failures
- Timeouts
- DNS errors
- SSL/TLS errors

**Retry**: Yes (automatic)
**User Action**: Check connection, retry

### Validation Errors
- Invalid input format
- Missing required fields
- Schema mismatches
- Constraint violations

**Retry**: No
**User Action**: Correct input data

### LLM Errors
- API failures
- Rate limits
- Quota exceeded
- Model not available
- Context length exceeded

**Retry**: Yes (with backoff)
**User Action**: Wait and retry, or check quota

### Pipeline Errors
- State corruption
- Missing dependencies
- Invalid stage transitions
- Execution failures

**Retry**: Sometimes (depends on error)
**User Action**: Contact support or restart

### Authentication Errors
- Invalid tokens
- Expired sessions
- Insufficient permissions

**Retry**: No
**User Action**: Re-authenticate

---

## Retry Strategies

### Exponential Backoff

The retry system uses exponential backoff with jitter:

```
Delay = min(base_delay * 2^attempt ± jitter, max_delay)
```

Default configuration:
- Base delay: 1 second
- Max delay: 60 seconds
- Jitter: ±25%
- Max attempts: 3

### Retryable Errors

By default, these error categories are retryable:
- Network errors
- LLM errors (including rate limits)
- Timeout errors
- 5xx HTTP errors (server errors)

### Non-retryable Errors

These errors are not retried:
- Validation errors
- Authentication errors
- 4xx HTTP errors (except 408, 429)

---

## Best Practices

### Backend

1. **Use Specific Error Types**
   ```python
   # Good
   raise ValidationError("Invalid email", field_name="email")

   # Avoid
   raise Exception("Invalid email")
   ```

2. **Provide Recovery Suggestions**
   ```python
   raise NetworkError(
       "Connection failed",
       recovery_suggestion="Check your network connection and retry"
   )
   ```

3. **Include Context in Details**
   ```python
   raise LLMError(
       "API call failed",
       provider="openai",
       model="gpt-4",
       details={"status_code": 500}
   )
   ```

4. **Use Retry Decorators for External Calls**
   ```python
   @retry_on_llm_error
   async def call_llm():
       # LLM API call
       pass
   ```

5. **Log Errors with Context**
   ```python
   logger.error(
       "Pipeline execution failed",
       extra={"run_id": run_id, "stage": stage},
       exc_info=True
   )
   ```

### Frontend

1. **Use Error Boundaries for Component Trees**
   ```tsx
   <ErrorBoundary>
     <MainApp />
   </ErrorBoundary>
   ```

2. **Handle Errors at Appropriate Level**
   ```typescript
   // Component-level for user feedback
   const { handleError } = useErrorHandler({ showToast: true });

   // Silent for background operations
   const { handleError: logError } = useErrorHandler({ showToast: false });
   ```

3. **Provide User-Friendly Messages**
   ```typescript
   try {
     await apiCall();
   } catch (error) {
     handleError(error, {
       context: 'We could not load your data'
     });
   }
   ```

4. **Use Graceful Degradation**
   ```typescript
   const { data, isUsingFallback } = useGracefulDegradation(
     fetchData,
     defaultData
   );
   ```

5. **Show Retry Options for Retryable Errors**
   ```tsx
   {error && isRetryableError(error) && (
     <button onClick={retry}>Retry</button>
   )}
   ```

---

## Examples

### Backend: Handling LLM API Call

```python
from decomposition_pipeline.errors import LLMError, ErrorCode
from decomposition_pipeline.utils.retry import async_retry_on_llm_error

@async_retry_on_llm_error
async def generate_paradigm_analysis(problem: str) -> str:
    try:
        response = await llm_client.generate(
            prompt=problem,
            model="claude-3-5-sonnet"
        )
        return response.content
    except RateLimitError as e:
        # Will be automatically retried
        raise
    except Exception as e:
        raise LLMError(
            "Failed to generate paradigm analysis",
            provider="anthropic",
            model="claude-3-5-sonnet",
            original_exception=e
        )
```

### Frontend: Making API Call with Error Handling

```typescript
import { useAsyncError } from '@/hooks/useErrorHandler';
import { apiClient } from '@/lib/api-client';

function PipelineControl() {
  const { execute: startPipeline, loading, error } = useAsyncError(
    async (problem: string) => {
      return await apiClient.post('/api/v1/pipeline/start', {
        problem,
      });
    },
    {
      showToast: true,
      context: 'Starting pipeline',
    }
  );

  return (
    <div>
      <button
        onClick={() => startPipeline('Analyze this problem')}
        disabled={loading}
      >
        {loading ? 'Starting...' : 'Start Pipeline'}
      </button>
      {error && (
        <div className="error">
          {error.message}
          {error.recoverySuggestion && (
            <p>Suggestion: {error.recoverySuggestion}</p>
          )}
        </div>
      )}
    </div>
  );
}
```

### Full-Stack Error Flow

1. **Backend Exception**
   ```python
   raise ValidationError(
       "Problem description is too short",
       error_code=ErrorCode.VALIDATION_CONSTRAINT_VIOLATION,
       field_name="problem",
       details={"min_length": 10, "actual_length": 5},
       recovery_suggestion="Please provide a problem description of at least 10 characters"
   )
   ```

2. **FastAPI Error Handler**
   ```python
   # Automatically converts to JSON response
   {
     "success": false,
     "error": {
       "type": "ValidationError",
       "message": "Problem description is too short",
       "code": "VALIDATION_2005",
       "details": {
         "field_name": "problem",
         "min_length": 10,
         "actual_length": 5
       },
       "recovery_suggestion": "Please provide a problem description of at least 10 characters"
     },
     "request_id": "req-123"
   }
   ```

3. **Frontend API Client**
   ```typescript
   // Automatically converts to AppError
   const error = AppError.fromBackendError(response);
   ```

4. **Error Display**
   ```typescript
   // Shows toast notification
   showError(error);
   // Displays: "Problem description is too short"
   // With suggestion: "Please provide a problem description of at least 10 characters"
   ```

---

## Testing Error Handling

### Backend Tests

```python
def test_validation_error():
    error = ValidationError("Invalid input", field_name="email")
    assert error.error_code == ErrorCode.VALIDATION_INVALID_INPUT
    assert error.details["field_name"] == "email"

def test_retry_on_network_error():
    @retry(max_attempts=3, base_delay=0.01)
    def failing_func():
        if failing_func.call_count < 2:
            failing_func.call_count += 1
            raise NetworkError("Connection failed")
        return "success"

    failing_func.call_count = 0
    result = failing_func()
    assert result == "success"
    assert failing_func.call_count == 2
```

### Frontend Tests

```typescript
test('handles API error', async () => {
  const error = new NetworkError('Connection failed');
  const { result } = renderHook(() => useErrorHandler());

  act(() => {
    result.current.handleError(error);
  });

  expect(result.current.error).toBe(error);
  expect(result.current.isError).toBe(true);
});

test('retries on failure', async () => {
  let attempts = 0;
  const fn = jest.fn().mockImplementation(async () => {
    attempts++;
    if (attempts < 3) throw new NetworkError('Failed');
    return 'success';
  });

  const { result } = renderHook(() => useRetry(fn, { maxAttempts: 3 }));

  await act(async () => {
    await result.current.execute();
  });

  expect(result.current.data).toBe('success');
  expect(attempts).toBe(3);
});
```

---

## Monitoring and Debugging

### Error Logging

All errors are logged with structured data:

```python
logger.error(
    "Pipeline execution failed",
    extra={
        "error_code": error.error_code.value,
        "request_id": request_id,
        "user_id": user_id,
        "stage": current_stage,
    },
    exc_info=True
)
```

### Request Tracking

Every request has a unique ID for tracing:

```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

### Error Metrics

Key metrics to monitor:
- Error rate by category
- Retry success rate
- Average retry attempts
- Error response times
- Most common error codes

---

## Future Improvements

1. **Circuit Breaker Pattern** - Prevent cascading failures
2. **Error Aggregation** - Group similar errors for analysis
3. **Distributed Tracing** - Track errors across services
4. **Sentry Integration** - Automatic error reporting
5. **Custom Retry Strategies** - Per-endpoint retry configuration
6. **Error Recovery Workflows** - Automated recovery actions

---

For more information, see the source code:
- Backend: `backend/src/decomposition_pipeline/errors/`
- Frontend: `frontend/types/errors.ts`, `frontend/lib/api-client.ts`
