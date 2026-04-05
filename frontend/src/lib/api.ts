/**
 * Axios-based HTTP client for VeloIQ backend API.
 *
 * Features:
 * - Request interceptor: attaches X-User-Id header from demo session
 * - Response interceptor: converts axios errors into typed ApiError
 * - Typed helpers: apiGet, apiPost, apiPatch, apiDelete
 * - Base URL from VITE_API_BASE_URL env var
 */

import axios, { AxiosError, type AxiosRequestConfig } from 'axios'
import { getActor } from '@/lib/demo-session'
import type { ErrorResponse } from '@/lib/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: attach X-User-Id header from demo session
apiClient.interceptors.request.use((config) => {
  config.headers['X-User-Id'] = getActor()
  return config
})

/**
 * Custom error class carrying backend ErrorResponse body.
 * Thrown by response interceptor for all non-2xx responses.
 */
export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly body: ErrorResponse

  constructor(status: number, body: ErrorResponse) {
    super(body.error ?? `HTTP ${status}`)
    this.status = status
    this.code = body.code
    this.body = body
    this.name = 'ApiError'
  }
}

// Response interceptor: convert axios errors into typed ApiError
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response) {
      const body = error.response.data ?? { error: error.message, code: 'UNKNOWN' }
      throw new ApiError(error.response.status, body)
    }
    // Network error — no response at all
    throw new ApiError(0, {
      error: error.message ?? 'Network error',
      code: 'NETWORK_ERROR',
    })
  },
)

/**
 * Type-safe GET request.
 * @param path — relative URL path (e.g., '/customers/123')
 * @param params — optional query parameters
 * @returns parsed response body of type T
 * @throws ApiError on non-2xx status
 */
export async function apiGet<T>(
  path: string,
  params?: Record<string, unknown>,
): Promise<T> {
  const response = await apiClient.get<T>(path, { params })
  return response.data
}

/**
 * Type-safe POST request.
 * @param path — relative URL path
 * @param body — request body (will be serialized to JSON)
 * @param config — optional axios config (for interceptors, timeout, etc.)
 * @returns parsed response body of type T
 * @throws ApiError on non-2xx status
 */
export async function apiPost<T, B = unknown>(
  path: string,
  body: B,
  config?: AxiosRequestConfig,
): Promise<T> {
  const response = await apiClient.post<T>(path, body, config)
  return response.data
}

/**
 * Type-safe PATCH request.
 * @param path — relative URL path
 * @param body — request body with partial fields
 * @param config — optional axios config
 * @returns parsed response body of type T
 * @throws ApiError on non-2xx status
 */
export async function apiPatch<T, B = unknown>(
  path: string,
  body: B,
  config?: AxiosRequestConfig,
): Promise<T> {
  const response = await apiClient.patch<T>(path, body, config)
  return response.data
}

/**
 * Type-safe DELETE request.
 * @param path — relative URL path
 * @returns parsed response body of type T (typically empty or a confirmation)
 * @throws ApiError on non-2xx status
 */
export async function apiDelete<T>(path: string): Promise<T> {
  const response = await apiClient.delete<T>(path)
  return response.data
}
