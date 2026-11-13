import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Mieter-Store — Verwaltung aller Mieter-Stammdaten.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/mieter
 * - GET /api/v1/mieter/{id}
 */

export interface Mieter {
  id: string
  vermieter_id?: string
  user_id?: string
  name: string
  email?: string
  telefon?: string
  geburtsdatum?: string
  adresse?: string
  notizen?: string
  created_at?: string
  updated_at?: string
}

export const useMieterStore = defineStore('mieter', () => {
  // State
  const mieter = ref<Mieter[]>([])
  const currentMieter = ref<Mieter | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Mieter des Vermieters laden.
   */
  async function fetchMieter(): Promise<Mieter[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Mieter[]>('/mieter')
      mieter.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelnen Mieter laden.
   */
  async function fetchMieterById(id: string): Promise<Mieter | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Mieter>(`/mieter/${id}`)
      currentMieter.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neuen Mieter anlegen.
   */
  async function createMieter(payload: Partial<Mieter>): Promise<Mieter | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Mieter>('/mieter', payload)
      mieter.value.push(data)
      currentMieter.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Mieter aktualisieren.
   */
  async function updateMieter(id: string, payload: Partial<Mieter>): Promise<Mieter | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Mieter>(`/mieter/${id}`, payload)
      const index = mieter.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        mieter.value[index] = data
      }
      if (currentMieter.value?.id === id) {
        currentMieter.value = data
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Mieter löschen.
   */
  async function deleteMieter(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/mieter/${id}`)
      mieter.value = mieter.value.filter((m) => m.id !== id)
      if (currentMieter.value?.id === id) {
        currentMieter.value = null
      }
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      saving.value = false
    }
  }

  /**
   * Aktuellen Mieter manuell setzen.
   */
  function setCurrentMieter(m: Mieter | null): void {
    currentMieter.value = m
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    mieter,
    currentMieter,
    loading,
    saving,
    error,
    fetchMieter,
    fetchMieterById,
    createMieter,
    updateMieter,
    deleteMieter,
    setCurrentMieter,
    clearError,
  }
})
