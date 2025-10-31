/**
 * API Route: POST /api/pipeline/start
 *
 * Starts a new pipeline execution by proxying the request to the backend.
 */

import { NextRequest, NextResponse } from 'next/server';
import { buildBackendUrl, BACKEND_ENDPOINTS, DEFAULT_TIMEOUT } from '@/lib/api-config';

interface StartPipelineRequest {
  problem: string;
  config?: {
    max_depth?: number;
    max_agents?: number;
    timeout?: number;
  };
}

interface StartPipelineResponse {
  run_id: string;
  status: string;
  message?: string;
}

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();

  try {
    // Parse and validate request body
    const body: StartPipelineRequest = await request.json();

    if (!body.problem || typeof body.problem !== 'string' || body.problem.trim().length === 0) {
      console.error(`[${requestId}] Validation error: Missing or invalid problem`);
      return NextResponse.json(
        {
          success: false,
          error: {
            type: 'ValidationError',
            message: 'Problem description is required and must be a non-empty string',
            code: 'VALIDATION_001',
            details: { field: 'problem' },
          },
        },
        { status: 400 }
      );
    }

    // Build backend URL
    const backendUrl = buildBackendUrl(BACKEND_ENDPOINTS.PIPELINE_START);

    console.log(`[${requestId}] Starting pipeline: ${backendUrl}`);
    console.log(`[${requestId}] Problem: ${body.problem.substring(0, 100)}...`);

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

    try {
      // Proxy request to backend
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      const data = await response.json();
      const duration = Date.now() - startTime;

      if (!response.ok) {
        console.error(`[${requestId}] Backend error (${response.status}): ${JSON.stringify(data)}`);
        return NextResponse.json(data, { status: response.status });
      }

      console.log(`[${requestId}] Pipeline started successfully in ${duration}ms`);
      console.log(`[${requestId}] Run ID: ${data.run_id}`);

      return NextResponse.json(data, { status: 200 });
    } catch (fetchError) {
      clearTimeout(timeout);

      if (fetchError instanceof Error && fetchError.name === 'AbortError') {
        console.error(`[${requestId}] Request timeout after ${DEFAULT_TIMEOUT}ms`);
        return NextResponse.json(
          {
            success: false,
            error: {
              type: 'TimeoutError',
              message: 'Request to backend timed out',
              code: 'NETWORK_1002',
              details: { timeout: DEFAULT_TIMEOUT },
              recovery_suggestion: 'Please try again or check backend status',
            },
          },
          { status: 504 }
        );
      }

      throw fetchError;
    }
  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`[${requestId}] Error after ${duration}ms:`, error);

    // Handle JSON parse errors
    if (error instanceof SyntaxError) {
      return NextResponse.json(
        {
          success: false,
          error: {
            type: 'ValidationError',
            message: 'Invalid JSON in request body',
            code: 'VALIDATION_002',
            details: { originalError: error.message },
          },
        },
        { status: 400 }
      );
    }

    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return NextResponse.json(
        {
          success: false,
          error: {
            type: 'NetworkError',
            message: 'Failed to connect to backend service',
            code: 'NETWORK_1001',
            details: { originalError: error.message },
            recovery_suggestion: 'Please check if the backend service is running',
          },
        },
        { status: 503 }
      );
    }

    // Generic error
    return NextResponse.json(
      {
        success: false,
        error: {
          type: 'InternalError',
          message: 'An unexpected error occurred',
          code: 'INTERNAL_001',
          details: {
            originalError: error instanceof Error ? error.message : String(error),
          },
        },
      },
      { status: 500 }
    );
  }
}
