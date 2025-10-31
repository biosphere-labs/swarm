/**
 * API Route: POST /api/pipeline/[runId]/modify
 *
 * Modifies the current state of a pipeline execution.
 */

import { NextRequest, NextResponse } from 'next/server';
import { buildBackendUrl, BACKEND_ENDPOINTS, DEFAULT_TIMEOUT } from '@/lib/api-config';

interface ModifyRequest {
  modifications: Record<string, any>;
  reason?: string;
}

interface ModifyResponse {
  success: boolean;
  message: string;
  run_id: string;
  modified_state?: Record<string, any>;
}

export async function POST(
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

    // Parse and validate request body
    const body: ModifyRequest = await request.json();

    if (!body.modifications || typeof body.modifications !== 'object') {
      console.error(`[${requestId}] Validation error: Missing or invalid modifications`);
      return NextResponse.json(
        {
          success: false,
          error: {
            type: 'ValidationError',
            message: 'Modifications object is required',
            code: 'VALIDATION_005',
            details: { field: 'modifications' },
          },
        },
        { status: 400 }
      );
    }

    if (Object.keys(body.modifications).length === 0) {
      console.error(`[${requestId}] Validation error: Empty modifications`);
      return NextResponse.json(
        {
          success: false,
          error: {
            type: 'ValidationError',
            message: 'Modifications object cannot be empty',
            code: 'VALIDATION_006',
            details: { field: 'modifications' },
          },
        },
        { status: 400 }
      );
    }

    // Build backend URL
    const backendUrl = buildBackendUrl(BACKEND_ENDPOINTS.PIPELINE_MODIFY(runId));

    console.log(`[${requestId}] Modifying pipeline: ${backendUrl}`);
    console.log(`[${requestId}] Run ID: ${runId}`);
    console.log(`[${requestId}] Modifications: ${JSON.stringify(body.modifications)}`);

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

      console.log(`[${requestId}] Pipeline modified successfully in ${duration}ms`);

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
