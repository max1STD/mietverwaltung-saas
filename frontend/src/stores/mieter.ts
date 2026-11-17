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
  public_id?: string
  vermieter_id?: string
  user_id?: string
  first_name: string
  last_name: string
  name: string
  email?: string
  telefon?: string
  geburtsdatum?: string
  notizen?: string
  status?: 'aktiv' | 'ehemalig' | 'bewerber'
  since?: string
  adressen?: Adresse[]
  buergschaften?: Buergschaft[]
  created_at?: string
  updated_at?: string
}

export interface Adresse {
  id?: string
  mieter_id?: string
  typ: 'postal' | 'residential' | 'rental_object' | 'guarantor'
  strasse: string
  hausnummer?: string
  plz: string
  ort: string
  land?: string
  is_primary?: boolean
}

export interface Buergschaft {
  id?: string
  mieter_id?: string
  buerge_first_name: string
  buerge_last_name: string
  buerge_geburtsdatum?: string
  buerge_phone?: string
  buerge_email?: string
  buerge_adresse: Adresse
  hoechstbetrag?: number | string
  gueltig_bis?: string
  status?: 'aktiv' | 'inaktiv'
  notizen?: string
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
      const index = mieter.value.findIndex((m) => m.id === id || m.public_id === id)
      if (index !== -1) {
        mieter.value[index] = data
      }
      if (currentMieter.value && (currentMieter.value.id === id || currentMieter.value.public_id === id)) {
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
      mieter.value = mieter.value.filter((m) => m.id !== id && m.public_id !== id)
      if (currentMieter.value && (currentMieter.value.id === id || currentMieter.value.public_id === id)) {
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
