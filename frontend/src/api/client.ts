import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

/**
 * API-Client — zentraler Axios-Instance für das Backend.
 *
 * Features:
 * - Basis-URL: /api/v1 (via Vite-Proxy auf localhost:8000 in Dev)
 * - CSRF-Token aus Cookie anhängen (Double-Submit)
 * - 401-Interceptor: Refresh-Token-Versuch, dann Retry oder Redirect zu /login
 * - Fehler-Normalisierung auf ein einheitliches ApiError-Format
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface ApiError {
  message: string
  status?: number
  code?: string
  details?: Record<string, string[]>
}

export interface ApiResponse<T> {
  data: T
}

interface ValidationErrorItem {
  loc?: unknown[]
  msg?: string
  type?: string
}

let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : null
}

function subscribeTokenRefresh(cb: (token: string) => void): void {
  refreshSubscribers.push(cb)
}

function onTokenRefreshed(token: string): void {
  refreshSubscribers.forEach((cb) => cb(token))
  refreshSubscribers = []
}

function redirectToLogin(): void {
  if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
    window.location.href = '/login'
  }
}

function normalizeError(error: AxiosError | Error): ApiError {
  if (!axios.isAxiosError(error)) {
    return { message: error.message || 'Unbekannter Fehler' }
  }

  const status = error.response?.status
  const data = error.response?.data as Record<string, unknown> | undefined

  // FastAPI-Detail-Format: { detail: string | [{ msg, loc, type }] }
  let message = 'Ein Fehler ist aufgetreten. Bitte versuche es erneut.'
  let details: Record<string, string[]> | undefined
  let code: string | undefined

  if (data) {
    if (typeof data.detail === 'string') {
      message = data.detail
    } else if (Array.isArray(data.detail)) {
      message = 'Eingabe ungültig. Bitte prüfe die markierten Felder.'
      details = data.detail.reduce((acc: Record<string, string[]>, item: ValidationErrorItem) => {
        const loc = Array.isArray(item.loc) ? item.loc.filter((l: unknown) => typeof l === 'string') : []
        const field = loc.length > 0 ? (loc[loc.length - 1] as string) : 'allgemein'
        if (!acc[field]) acc[field] = []
        if (item.msg) acc[field].push(String(item.msg))
        return acc
      }, {})
    } else if (typeof data.message === 'string') {
      message = data.message
    }
    if (typeof data.code === 'string') {
      code = data.code
    }
  }

  // Deutliche deutsche Fehlermeldungen für gängige Statuscodes
  if (status === 401) {
    message = 'Sitzung abgelaufen. Bitte melde dich erneut an.'
  } else if (status === 403) {
    message = 'Zugriff verweigert.'
  } else if (status === 404) {
    message = 'Die angeforderte Ressource wurde nicht gefunden.'
  } else if (status === 422) {
    message = message || 'Eingabe ungültig. Bitte prüfe deine Angaben.'
  } else if (status && status >= 500) {
    message = 'Server-Fehler. Bitte versuche es später erneut.'
  }

  return { message, status, code, details }
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request-Interceptor: CSRF-Token anhängen
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const csrf = getCsrfToken()
    if (csrf && config.method && !['get', 'head', 'options'].includes(config.method.toLowerCase())) {
      config.headers.set('x-csrf-token', csrf)
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response-Interceptor: 401-Handling mit Refresh-Token
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    if (!originalRequest || error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(normalizeError(error))
    }

    if (originalRequest.url?.includes('/auth/refresh') || originalRequest.url?.includes('/auth/login')) {
      // Bei Refresh-/Login-Request selbst direkt zum Login
      redirectToLogin()
      return Promise.reject(normalizeError(error))
    }

    originalRequest._retry = true

    if (isRefreshing) {
      // Warten bis Refresh durch ist, dann Retry
      return new Promise((resolve) => {
        subscribeTokenRefresh(() => {
          resolve(apiClient(originalRequest))
        })
      })
    }

    isRefreshing = true

    try {
      await apiClient.post('/auth/refresh', {}, { _retry: true } as AxiosRequestConfig)
      onTokenRefreshed('refreshed')
      isRefreshing = false
      return apiClient(originalRequest)
    } catch (refreshError) {
      isRefreshing = false
      redirectToLogin()
      return Promise.reject(normalizeError(refreshError as AxiosError | Error))
    }
  },
)

export { normalizeError }
export default apiClient