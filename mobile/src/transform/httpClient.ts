import type { TransformClient } from './client';
import type { TransformRequest, TransformResult } from './contracts';
import { resolveTransformBaseUrl } from './client';

/**
 * HTTP client for the product transform API.
 * POST {base}/v1/transform — same JSON contract as product/api/app.py.
 * Does not embed prompts, style sheets, or provider secrets.
 */
export class HttpTransformClient implements TransformClient {
  constructor(private readonly baseUrl: string = resolveTransformBaseUrl()) {}

  async transform(request: TransformRequest): Promise<TransformResult> {
    const url = `${this.baseUrl}/v1/transform`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(request),
    });
    let body: TransformResult;
    try {
      body = (await res.json()) as TransformResult;
    } catch {
      return {
        status: 'error',
        style: request.style,
        transform_version: 'unknown',
        error: `bad_response_${res.status}`,
      };
    }
    if (!res.ok && body.status !== 'error') {
      return {
        ...body,
        status: 'error',
        error: body.error || `http_${res.status}`,
      };
    }
    return body;
  }
}
