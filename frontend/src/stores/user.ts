import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'
import type { User } from './auth'

/**
 * User-Store — Profilverwaltung und DSGVO-Einwilligungen.
 */

export interface ProfileUpdatePayload {
  full_name?: string
  email?: string
  telefon?: string
}

export interface ConsentItem {
  id: string
  consent_type: string
  version: string
  accepted: boolean
  accepted_at?: string
}

export const useUserStore = defineStore('user', () => {
  // State
  const profile = ref<User | null>(null)
  const consents = ref<ConsentItem[]>([])
  const loading = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Eigene Benutzerdaten laden.
   */
  async function fetchProfile(): Promise<User | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<User>('/users/me')
      profile.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Profil aktualisieren.
   */
  async function updateProfile(payload: ProfileUpdatePayload): Promise<User | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<User>('/users/me', payload)
      profile.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Aktuelle DSGVO-Einwilligungen laden.
   */
  async function fetchConsents(): Promise<ConsentItem[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<ConsentItem[]>('/einwilligungen')
      consents.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einwilligung akzeptieren oder ablehnen.
   */
  async function updateConsent(consentType: string, version: string, accepted: boolean): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await apiClient.post('/einwilligungen', {
        consent_type: consentType,
        version,
        accepted,
      })
      await fetchConsents()
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    profile,
    consents,
    loading,
    error,
    fetchProfile,
    updateProfile,
    fetchConsents,
    updateConsent,
  }
})