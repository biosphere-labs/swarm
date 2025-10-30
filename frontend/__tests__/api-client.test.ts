/**
 * Tests for API client with retry logic.
 */

import { ApiClient, createApiClient } from '@/lib/api-client';
import { NetworkError, AppError, ErrorCategory } from '@/types/errors';

// Mock fetch
global.fetch = jest.fn();

describe('ApiClient', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient({
      baseUrl: 'http://localhost:8000',
      timeout: 5000,
      retries: 3,
    });
    jest.clearAllMocks();
  });

  describe('Successful Requests', () => {
    it('makes GET request', async () => {
      const mockResponse = { data: 'test' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.get('/test');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('makes POST request', async () => {
      const mockResponse = { id: 1 };
      const postData = { name: 'test' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      const result = await client.post('/test', postData);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
        })
      );
    });

    it('handles 204 No Content', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      const result = await client.delete('/test');

      expect(result).toBeUndefined();
    });
  });

  describe('Error Handling', () => {
    it('handles network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new TypeError('Failed to fetch')
      );

      await expect(client.get('/test')).rejects.toThrow(NetworkError);
    });

    it('handles timeout errors', async () => {
      // Mock slow response
      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(resolve, 10000))
      );

      const quickClient = new ApiClient({
        baseUrl: 'http://localhost:8000',
        timeout: 100,
      });

      await expect(quickClient.get('/test')).rejects.toThrow(NetworkError);
    });

    it('handles HTTP error responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        url: 'http://localhost:8000/test',
        headers: new Headers(),
      });

      await expect(client.get('/test')).rejects.toThrow(NetworkError);
    });

    it('handles backend error responses', async () => {
      const errorResponse = {
        success: false,
        error: {
          type: 'ValidationError',
          message: 'Invalid input',
          code: 'VALIDATION_2001',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => errorResponse,
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await expect(client.get('/test')).rejects.toThrow(AppError);
      await expect(client.get('/test')).rejects.toMatchObject({
        message: 'Invalid input',
        code: 'VALIDATION_2001',
      });
    });
  });

  describe('Retry Logic', () => {
    it('retries on network error', async () => {
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new TypeError('Failed to fetch'))
        .mockRejectedValueOnce(new TypeError('Failed to fetch'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ success: true }),
          headers: new Headers({ 'content-type': 'application/json' }),
        });

      const result = await client.get('/test');

      expect(result).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('retries on 500 error', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          url: 'http://localhost:8000/test',
          headers: new Headers(),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ success: true }),
          headers: new Headers({ 'content-type': 'application/json' }),
        });

      const result = await client.get('/test');

      expect(result).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('does not retry on 400 error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        url: 'http://localhost:8000/test',
        headers: new Headers(),
      });

      await expect(client.get('/test')).rejects.toThrow();
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('respects max retry attempts', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(
        new TypeError('Failed to fetch')
      );

      await expect(client.get('/test')).rejects.toThrow(NetworkError);
      expect(global.fetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });
  });

  describe('Request Configuration', () => {
    it('adds query parameters', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await client.get('/test', { params: { page: 1, limit: 10 } });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test?page=1&limit=10',
        expect.any(Object)
      );
    });

    it('sets request headers', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
        headers: new Headers({ 'content-type': 'application/json' }),
      });

      await client.get('/test');

      const callArgs = (global.fetch as jest.Mock).mock.calls[0];
      const headers = callArgs[1].headers;

      expect(headers.get('Content-Type')).toBe('application/json');
      expect(headers.get('Accept')).toBe('application/json');
      expect(headers.has('X-Request-ID')).toBe(true);
    });
  });

  describe('Error Callback', () => {
    it('calls error callback on failure', async () => {
      const onError = jest.fn();
      const clientWithCallback = new ApiClient({
        baseUrl: 'http://localhost:8000',
        onError,
      });

      (global.fetch as jest.Mock).mockRejectedValue(
        new TypeError('Failed to fetch')
      );

      await expect(clientWithCallback.get('/test')).rejects.toThrow();

      expect(onError).toHaveBeenCalledTimes(1);
      expect(onError).toHaveBeenCalledWith(expect.any(NetworkError));
    });
  });
});

describe('createApiClient', () => {
  it('creates client with default config', () => {
    const client = createApiClient();
    expect(client).toBeInstanceOf(ApiClient);
  });

  it('creates client with custom config', () => {
    const client = createApiClient({
      baseUrl: 'https://api.example.com',
      timeout: 10000,
      retries: 5,
    });
    expect(client).toBeInstanceOf(ApiClient);
  });
});
