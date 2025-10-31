/**
 * API Route: GET /api/pipeline/[runId]/status
 *
 * Retrieves the current status of a pipeline execution.
 */

import { NextRequest, NextResponse } from 'next/server';
import { buildBackendUrl, BACKEND_ENDPOINTS, DEFAULT_TIMEOUT } from '@/lib/api-config';

interface PipelineStatusResponse {
  run_id: string;
  status: string;
  current_stage?: string;
  progress?: number;
  start_time?: string;
  end_time?: string;
  error?: string;
  metadata?: Record<string, any>;
}

export async function GET(
  request: NextRequest,
  { params }: { params: { runId: string } }
) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();
  const { runId } = params;

  try {
    // Validate runId
    if (!runId || typeof runId !== 'string' || runId.trim().length === 0) {
      console.error(`[${requestId}] Validation error: Invalid runId`);
      return NextResponse.json(
        {
          success: false,
          error: {
            type: 'ValidationError',
            message: 'Run ID is required and must be a non-empty string',
            code: 'VALIDATION_003',
            details: { field: 'runId' },
          },
        },
        { status: 400 }
      );
    }

    // Build backend URL
    const backendUrl = buildBackendUrl(BACKEND_ENDPOINTS.PIPELINE_STATUS(runId));

    console.log(`[${requestId}] Fetching pipeline status: ${backendUrl}`);
    console.log(`[${requestId}] Run ID: ${runId}`);

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

    try {
      // Proxy request to backend
      const response = await fetch(backendUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'X-Request-ID': requestId,
        },
        signal: controller.signal,
      });

      clearTimeout(timeout);

      const data = await response.json();
      const duration = Date.now() - startTime;

      if (!response.ok) {
        console.error(`[${requestId}] Backend error (${response.status}): ${JSON.stringify(data)}`);
        return NextResponse.json(data, { status: response.status });
      }

      console.log(`[${requestId}] Pipeline status fetched successfully in ${duration}ms`);
      console.log(`[${requestId}] Status: ${data.status}`);

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
