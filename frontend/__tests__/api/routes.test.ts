/**
 * Comprehensive tests for API routes
 *
 * Tests all pipeline control API routes including:
 * - Request validation
 * - Backend proxying
 * - Error handling
 * - Timeout handling
 * - Response transformation
 */

import { NextRequest } from 'next/server';
import { POST as startPipeline } from '@/app/api/pipeline/start/route';
import { POST as approvePipeline } from '@/app/api/pipeline/[runId]/approve/route';
import { POST as rejectPipeline } from '@/app/api/pipeline/[runId]/reject/route';
import { POST as modifyPipeline } from '@/app/api/pipeline/[runId]/modify/route';
import { POST as backtrackPipeline } from '@/app/api/pipeline/[runId]/backtrack/route';
import { POST as addContext } from '@/app/api/pipeline/[runId]/add-context/route';
import { POST as requestAlternatives } from '@/app/api/pipeline/[runId]/request-alternatives/route';
import { GET as getStatus } from '@/app/api/pipeline/[runId]/status/route';

// Mock fetch globally
global.fetch = jest.fn();

// Mock crypto.randomUUID
global.crypto = {
  randomUUID: () => 'test-request-id-123',
} as any;

describe('API Routes - Pipeline Control', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('POST /api/pipeline/start', () => {
    it('should start a pipeline successfully', async () => {
      const mockResponse = {
        run_id: 'run-123',
        status: 'running',
        message: 'Pipeline started successfully',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: JSON.stringify({
          problem: 'Test problem description',
          config: { max_depth: 5 },
        }),
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.run_id).toBe('run-123');
      expect(data.status).toBe('running');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/pipeline/start'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should reject empty problem', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: JSON.stringify({ problem: '' }),
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('VALIDATION_001');
    });

    it('should reject missing problem', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: JSON.stringify({}),
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.error.code).toBe('VALIDATION_001');
    });

    it('should handle backend errors', async () => {
      const mockError = {
        success: false,
        error: {
          type: 'PipelineError',
          message: 'Failed to initialize pipeline',
          code: 'PIPELINE_001',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => mockError,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: JSON.stringify({ problem: 'Test problem' }),
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.error.code).toBe('PIPELINE_001');
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new TypeError('fetch failed'));

      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: JSON.stringify({ problem: 'Test problem' }),
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(503);
      expect(data.error.code).toBe('NETWORK_1001');
    });

    it('should handle invalid JSON', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: 'invalid json',
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_002');
    });
  });

  describe('POST /api/pipeline/[runId]/approve', () => {
    const mockParams = { params: { runId: 'run-123' } };

    it('should approve pipeline successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Pipeline approved',
        run_id: 'run-123',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/approve', {
        method: 'POST',
        body: JSON.stringify({ comment: 'Looks good' }),
      });

      const response = await approvePipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.run_id).toBe('run-123');
    });

    it('should handle empty body', async () => {
      const mockResponse = {
        success: true,
        message: 'Pipeline approved',
        run_id: 'run-123',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/approve', {
        method: 'POST',
        body: JSON.stringify({}),
      });

      const response = await approvePipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it('should reject invalid runId', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline//approve', {
        method: 'POST',
        body: JSON.stringify({}),
      });

      const response = await approvePipeline(request, { params: { runId: '' } });
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_003');
    });
  });

  describe('POST /api/pipeline/[runId]/reject', () => {
    const mockParams = { params: { runId: 'run-123' } };

    it('should reject pipeline successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Pipeline rejected',
        run_id: 'run-123',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/reject', {
        method: 'POST',
        body: JSON.stringify({
          reason: 'Incorrect approach',
          comment: 'Please try alternative method',
        }),
      });

      const response = await rejectPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.run_id).toBe('run-123');
    });

    it('should require reason field', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/reject', {
        method: 'POST',
        body: JSON.stringify({ comment: 'No reason provided' }),
      });

      const response = await rejectPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_004');
    });

    it('should reject empty reason', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/reject', {
        method: 'POST',
        body: JSON.stringify({ reason: '   ' }),
      });

      const response = await rejectPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_004');
    });
  });

  describe('POST /api/pipeline/[runId]/modify', () => {
    const mockParams = { params: { runId: 'run-123' } };

    it('should modify pipeline successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Pipeline modified',
        run_id: 'run-123',
        modified_state: { key: 'value' },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/modify', {
        method: 'POST',
        body: JSON.stringify({
          modifications: { max_depth: 10, timeout: 300 },
          reason: 'Increase limits',
        }),
      });

      const response = await modifyPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.run_id).toBe('run-123');
    });

    it('should require modifications field', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/modify', {
        method: 'POST',
        body: JSON.stringify({ reason: 'Test' }),
      });

      const response = await modifyPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_005');
    });

    it('should reject empty modifications', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/modify', {
        method: 'POST',
        body: JSON.stringify({ modifications: {} }),
      });

      const response = await modifyPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_006');
    });

    it('should reject invalid modifications type', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/modify', {
        method: 'POST',
        body: JSON.stringify({ modifications: 'invalid' }),
      });

      const response = await modifyPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_005');
    });
  });

  describe('POST /api/pipeline/[runId]/backtrack', () => {
    const mockParams = { params: { runId: 'run-123' } };

    it('should backtrack to target stage successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Pipeline backtracked',
        run_id: 'run-123',
        current_stage: 'decomposition',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/backtrack', {
        method: 'POST',
        body: JSON.stringify({
          target_stage: 'decomposition',
          reason: 'Incorrect decomposition',
        }),
      });

      const response = await backtrackPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.current_stage).toBe('decomposition');
    });

    it('should backtrack to checkpoint successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Pipeline backtracked',
        run_id: 'run-123',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/backtrack', {
        method: 'POST',
        body: JSON.stringify({ checkpoint_id: 'checkpoint-456' }),
      });

      const response = await backtrackPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it('should require target_stage or checkpoint_id', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/backtrack', {
        method: 'POST',
        body: JSON.stringify({ reason: 'Test' }),
      });

      const response = await backtrackPipeline(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_007');
    });
  });

  describe('POST /api/pipeline/[runId]/add-context', () => {
    const mockParams = { params: { runId: 'run-123' } };

    it('should add string context successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Context added',
        run_id: 'run-123',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/add-context', {
        method: 'POST',
        body: JSON.stringify({
          context: 'Additional context information',
          context_type: 'text',
        }),
      });

      const response = await addContext(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it('should add object context successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Context added',
        run_id: 'run-123',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/add-context', {
        method: 'POST',
        body: JSON.stringify({
          context: { key: 'value', data: [1, 2, 3] },
        }),
      });

      const response = await addContext(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it('should require context field', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/add-context', {
        method: 'POST',
        body: JSON.stringify({}),
      });

      const response = await addContext(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_008');
    });

    it('should reject empty string context', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/add-context', {
        method: 'POST',
        body: JSON.stringify({ context: '   ' }),
      });

      const response = await addContext(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_009');
    });
  });

  describe('POST /api/pipeline/[runId]/request-alternatives', () => {
    const mockParams = { params: { runId: 'run-123' } };

    it('should request alternatives successfully', async () => {
      const mockResponse = {
        success: true,
        message: 'Alternatives requested',
        run_id: 'run-123',
        alternatives: [
          { id: 'alt-1', description: 'Alternative 1', score: 0.9 },
          { id: 'alt-2', description: 'Alternative 2', score: 0.8 },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest(
        'http://localhost:3000/api/pipeline/run-123/request-alternatives',
        {
          method: 'POST',
          body: JSON.stringify({
            stage: 'decomposition',
            count: 3,
            criteria: ['accuracy', 'efficiency'],
          }),
        }
      );

      const response = await requestAlternatives(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.alternatives).toHaveLength(2);
    });

    it('should handle empty body', async () => {
      const mockResponse = {
        success: true,
        message: 'Alternatives requested',
        run_id: 'run-123',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest(
        'http://localhost:3000/api/pipeline/run-123/request-alternatives',
        {
          method: 'POST',
          body: JSON.stringify({}),
        }
      );

      const response = await requestAlternatives(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
    });

    it('should reject invalid count', async () => {
      const request = new NextRequest(
        'http://localhost:3000/api/pipeline/run-123/request-alternatives',
        {
          method: 'POST',
          body: JSON.stringify({ count: 20 }),
        }
      );

      const response = await requestAlternatives(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_010');
    });

    it('should reject invalid criteria type', async () => {
      const request = new NextRequest(
        'http://localhost:3000/api/pipeline/run-123/request-alternatives',
        {
          method: 'POST',
          body: JSON.stringify({ criteria: 'not-an-array' }),
        }
      );

      const response = await requestAlternatives(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_011');
    });
  });

  describe('GET /api/pipeline/[runId]/status', () => {
    const mockParams = { params: { runId: 'run-123' } };

    it('should get pipeline status successfully', async () => {
      const mockResponse = {
        run_id: 'run-123',
        status: 'running',
        current_stage: 'execution',
        progress: 0.6,
        start_time: '2024-01-01T00:00:00Z',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/status', {
        method: 'GET',
      });

      const response = await getStatus(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.run_id).toBe('run-123');
      expect(data.status).toBe('running');
      expect(data.progress).toBe(0.6);
    });

    it('should handle completed pipeline', async () => {
      const mockResponse = {
        run_id: 'run-123',
        status: 'completed',
        current_stage: 'integration',
        progress: 1.0,
        start_time: '2024-01-01T00:00:00Z',
        end_time: '2024-01-01T00:10:00Z',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/status', {
        method: 'GET',
      });

      const response = await getStatus(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.status).toBe('completed');
      expect(data.end_time).toBeDefined();
    });

    it('should handle failed pipeline', async () => {
      const mockResponse = {
        run_id: 'run-123',
        status: 'failed',
        error: 'Pipeline execution failed',
        start_time: '2024-01-01T00:00:00Z',
        end_time: '2024-01-01T00:05:00Z',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-123/status', {
        method: 'GET',
      });

      const response = await getStatus(request, mockParams);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.status).toBe('failed');
      expect(data.error).toBeDefined();
    });

    it('should handle not found pipeline', async () => {
      const mockError = {
        success: false,
        error: {
          type: 'NotFoundError',
          message: 'Pipeline not found',
          code: 'PIPELINE_404',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => mockError,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/run-999/status', {
        method: 'GET',
      });

      const response = await getStatus(request, { params: { runId: 'run-999' } });
      const data = await response.json();

      expect(response.status).toBe(404);
      expect(data.error.code).toBe('PIPELINE_404');
    });

    it('should reject invalid runId', async () => {
      const request = new NextRequest('http://localhost:3000/api/pipeline//status', {
        method: 'GET',
      });

      const response = await getStatus(request, { params: { runId: '' } });
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error.code).toBe('VALIDATION_003');
    });
  });

  describe('Error Handling', () => {
    it('should handle timeout errors', async () => {
      const abortError = new Error('The operation was aborted');
      abortError.name = 'AbortError';
      (global.fetch as jest.Mock).mockRejectedValueOnce(abortError);

      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: JSON.stringify({ problem: 'Test problem' }),
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(504);
      expect(data.error.code).toBe('NETWORK_1002');
    });

    it('should pass through backend error status codes', async () => {
      const mockError = {
        success: false,
        error: {
          type: 'ValidationError',
          message: 'Invalid configuration',
          code: 'VALIDATION_100',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => mockError,
      });

      const request = new NextRequest('http://localhost:3000/api/pipeline/start', {
        method: 'POST',
        body: JSON.stringify({ problem: 'Test' }),
      });

      const response = await startPipeline(request);
      const data = await response.json();

      expect(response.status).toBe(422);
      expect(data.error.code).toBe('VALIDATION_100');
    });
  });
});
