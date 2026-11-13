import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * useApi — Wrapper für API-Aufrufe mit Loading-State und Fehlerbehandlung.
 *
 * const { loading, error, execute } = useApi()
 * const result = await execute(() => apiClient.get('/users/me'))
 */

export interface UseApiOptions {
  resetErrorOnExecute?: boolean
}

export function useApi<T = unknown>(options: UseApiOptions = {}) {
  const loading = ref(false)
  const error = ref<ApiError | null>(null)
  const data = ref<T | null>(null)

  async function execute<R = T>(fn: () => Promise<R>): Promise<R | null> {
    loading.value = true
    if (options.resetErrorOnExecute !== false) {
      error.value = null
    }

    try {
      const result = await fn()
      data.value = result as unknown as T
      return result
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    data,
    execute,
  }
}

/**
 * Hilfsfunktion für einfache GET/POST/PUT/PATCH/DELETE-Aufrufe.
 */
export async function apiCall<T>(
  method: 'get' | 'post' | 'put' | 'patch' | 'delete',
  url: string,
  payload?: unknown,
): Promise<{ data: T | null; error: ApiError | null }> {
  try {
    const args: [string, unknown?] = payload !== undefined ? [url, payload] : [url]
    const response =
      method === 'get' || method === 'delete'
        ? await apiClient[method](url)
        : await apiClient[method](...args)
    return { data: response.data as T, error: null }
  } catch (err) {
    return { data: null, error: normalizeError(err as Error) }
  }
}