import type { TransformRequest, TransformResult } from './contracts';

/**
 * Provider-agnostic transform boundary for the mobile app.
 * Implementations: mock (local) or HTTP → product/api POST /v1/transform.
 */
export interface TransformClient {
  transform(request: TransformRequest): Promise<TransformResult>;
}

export type TransformMode = 'mock' | 'http';

export function resolveTransformMode(): TransformMode {
  // EXPO_PUBLIC_TRANSFORM_MODE=mock|http  (default mock)
  const raw = (process.env.EXPO_PUBLIC_TRANSFORM_MODE || 'mock').toLowerCase();
  return raw === 'http' ? 'http' : 'mock';
}

export function resolveTransformBaseUrl(): string {
  return (
    process.env.EXPO_PUBLIC_TRANSFORM_API_URL ||
    'http://127.0.0.1:8080'
  ).replace(/\/$/, '');
}
