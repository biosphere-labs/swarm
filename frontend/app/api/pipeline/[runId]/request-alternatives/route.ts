/**
 * API Route: POST /api/pipeline/[runId]/request-alternatives
 *
 * Requests alternative solutions or approaches for a pipeline stage.
 */

import { NextRequest, NextResponse } from 'next/server';
import { buildBackendUrl, BACKEND_ENDPOINTS, DEFAULT_TIMEOUT } from '@/lib/api-config';

interface RequestAlternativesRequest {
  stage?: string;
  count?: number;
  criteria?: string[];
}

interface RequestAlternativesResponse {
  success: boolean;
  message: string;
  run_id: string;
  alternatives?: Array<{
    id: string;
    description: string;
    score?: number;
  }>;
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

    // Parse request body (all fields are optional)
    let body: RequestAlternativesRequest = {};
    try {
      body = await request.json();
    } catch (e) {
      // Empty body is acceptable
      body = {};
    }

    // Validate count if provided
    if (body.count !== undefined) {
      if (typeof body.count !== 'number' || body.count < 1 || body.count > 10) {
        console.error(`[${requestId}] Validation error: Invalid count`);
        return NextResponse.json(
          {
            success: false,
            error: {
              type: 'ValidationError',
              message: 'Count must be a number between 1 and 10',
              code: 'VALIDATION_010',
              details: { field: 'count', value: body.count },
            },
          },
          { status: 400 }
        );
      }
    }

    // Validate criteria if provided
    if (body.criteria !== undefined && !Array.isArray(body.criteria)) {
      console.error(`[${requestId}] Validation error: Invalid criteria`);
      return NextResponse.json(
        {
          success: false,
          error: {
            type: 'ValidationError',
            message: 'Criteria must be an array of strings',
            code: 'VALIDATION_011',
            details: { field: 'criteria' },
          },
        },
        { status: 400 }
      );
    }

    // Build backend URL
    const backendUrl = buildBackendUrl(BACKEND_ENDPOINTS.PIPELINE_REQUEST_ALTERNATIVES(runId));

    console.log(`[${requestId}] Requesting alternatives: ${backendUrl}`);
    console.log(`[${requestId}] Run ID: ${runId}`);
    if (body.stage) {
      console.log(`[${requestId}] Stage: ${body.stage}`);
    }
    if (body.count) {
      console.log(`[${requestId}] Count: ${body.count}`);
    }

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

      console.log(`[${requestId}] Alternatives requested successfully in ${duration}ms`);

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

    // Handle JSON parse errors (only if body was required)
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
