import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Auth-Store — verwaltet Authentifizierung, 2FA-Status und Benutzer-Session.
 *
 * Verwendung:
 * - register(): Registrierung mit DSGVO-Einwilligung, Cookie-Login.
 * - login(): E-Mail/Passwort-Login. Bei requires_2fa -> Redirect zu /2fa-setup.
 * - verify2fa(): TOTP-Code verifizieren, danach vollständig authentifiziert.
 * - logout(): Server-Logout + lokaler State reset.
 * - refreshToken(): Access-Token erneuern (wird auch vom API-Client-Interceptor genutzt).
 * - fetchUser(): Aktuelles Profil laden.
 */

export interface User {
  id: string
  email: string
  full_name: string
  role: 'vermieter' | 'mieter' | 'admin'
  is_2fa_enabled: boolean
  is_2fa_verified: boolean
  created_at?: string
  updated_at?: string
}

export interface LoginResponse {
  requires_2fa: boolean
  user?: User
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  role?: string
}

export interface TwoFactorSetupResponse {
  secret: string
  qr_code_url: string
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const requires2fa = ref(false)
  const loading = ref(false)
  const error = ref<ApiError | null>(null)

  // Getters
  const isVermieter = computed(() => user.value?.role === 'vermieter')
  const isMieter = computed(() => user.value?.role === 'mieter')
  const isAdmin = computed(() => user.value?.role === 'admin')

  /**
   * Hilfsfunktion: Setzt den authentifizierten Benutzer.
   */
  function setAuthenticated(u: User, needs2fa: boolean): void {
    user.value = u
    isAuthenticated.value = true
    requires2fa.value = needs2fa && !u.is_2fa_verified
    error.value = null
  }

  /**
   * Hilfsfunktion: Löscht den lokalen Auth-State.
   */
  function clearAuth(): void {
    user.value = null
    isAuthenticated.value = false
    requires2fa.value = false
    error.value = null
  }

  /**
   * Registrierung eines neuen Vermieter-Kontos.
   */
  async function register(payload: RegisterPayload): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<User>('/auth/register', {
        ...payload,
        role: payload.role || 'vermieter',
      })
      setAuthenticated(data, true) // Nach Registrierung ist 2FA noch nicht eingerichtet
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Login mit E-Mail und Passwort.
   */
  async function login(email: string, password: string, rememberMe: boolean = false): Promise<LoginResponse> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<LoginResponse>('/auth/login', { email, password, remember_me: rememberMe })
      if (data.user) {
        setAuthenticated(data.user, data.requires_2fa)
      } else if (data.requires_2fa) {
        // Teilauthentifiziert: Backend hat Session-Cookie gesetzt, aber 2FA ausstehend
        isAuthenticated.value = true
        requires2fa.value = true
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      // Bei Login-Fehler alten Auth-State verwerfen — sonst bleibt
      // eine vorherige Session aktiv und der User kommt trotz
      // falschem Passwort ins Dashboard.
      clearAuth()
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 2FA-Setup (TOTP-Secret + QR-Code) abrufen.
   */
  async function setup2fa(): Promise<TwoFactorSetupResponse | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<TwoFactorSetupResponse>('/auth/2fa/setup')
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 2FA-Code verifizieren.
   */
  async function verify2fa(code: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<{ success: boolean; user?: User }>('/auth/2fa/verify', { code })
      if (data.success && data.user) {
        setAuthenticated(data.user, false)
      }
      return data.success
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 2FA-Setup überspringen (lokaler Flag; Backend erzwingt es beim nächsten Login).
   */
  function skip2fa(): void {
    requires2fa.value = false
  }

  /**
   * Access-Token erneuern.
   */
  async function refreshToken(): Promise<boolean> {
    try {
      await apiClient.post('/auth/refresh')
      return true
    } catch {
      clearAuth()
      return false
    }
  }

  /**
   * Benutzer abmelden.
   */
  async function logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } finally {
      clearAuth()
    }
  }

  /**
   * Aktuelles Benutzerprofil laden.
   */
  async function fetchUser(): Promise<User | null> {
    try {
      const { data } = await apiClient.get<User>('/users/me')
      user.value = data
      isAuthenticated.value = true
      requires2fa.value = data.is_2fa_enabled && !data.is_2fa_verified
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      clearAuth()
      return null
    }
  }

  return {
    user,
    isAuthenticated,
    requires2fa,
    loading,
    error,
    isVermieter,
    isMieter,
    isAdmin,
    register,
    login,
    setup2fa,
    verify2fa,
    skip2fa,
    refreshToken,
    logout,
    fetchUser,
    clearAuth,
  }
})