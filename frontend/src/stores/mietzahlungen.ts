import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Mietzahlungen-Store — Soll-/Ist-Überwachung und Mahnwesen.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/mietzahlungen
 * - GET /api/v1/mietzahlungen/{id}
 * - POST /api/v1/mietzahlungen/{id}/bezahlen
 */

export type MietzahlungStatus = 'offen' | 'teilweise' | 'bezahlt' | 'ueberfaellig'

export interface Mietzahlung {
  id: string
  bezeichnung?: string
  vermieter_id?: string
  mieter_id: string
  mietvertrag_id?: string
  einheit_id?: string
  mieter?: {
    id: string
    name?: string
    bezeichnung?: string
  }
  einheit?: {
    id: string
    name?: string
    bezeichnung?: string
  }
  betrag_soll: number
  betrag_ist?: number
  faellig_am: string
  gezahlt_am?: string
  status: MietzahlungStatus | string
  mahnstufe: number
  referenz?: string
  notizen?: string
  created_at?: string
  updated_at?: string
}

export const useMietzahlungenStore = defineStore('mietzahlungen', () => {
  // State
  const mietzahlungen = ref<Mietzahlung[]>([])
  const currentMietzahlung = ref<Mietzahlung | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Mietzahlungen laden (optional gefiltert).
   */
  async function fetchMietzahlungen(params?: {
    status?: string
    mahnstufe?: number
    mieter_id?: string
    einheit_id?: string
  }): Promise<Mietzahlung[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Mietzahlung[]>('/mietzahlungen', { params })
      mietzahlungen.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelne Mietzahlung laden.
   */
  async function fetchMietzahlung(id: string): Promise<Mietzahlung | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Mietzahlung>(`/mietzahlungen/${id}`)
      currentMietzahlung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neue Mietzahlung anlegen.
   */
  async function createMietzahlung(payload: Partial<Mietzahlung>): Promise<Mietzahlung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Mietzahlung>('/mietzahlungen', payload)
      mietzahlungen.value.push(data)
      currentMietzahlung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Mietzahlung aktualisieren.
   */
  async function updateMietzahlung(
    id: string,
    payload: Partial<Mietzahlung>,
  ): Promise<Mietzahlung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Mietzahlung>(`/mietzahlungen/${id}`, payload)
      const index = mietzahlungen.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        mietzahlungen.value[index] = data
      }
      if (currentMietzahlung.value?.id === id) {
        currentMietzahlung.value = data
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
   * Mietzahlung löschen.
   */
  async function deleteMietzahlung(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/mietzahlungen/${id}`)
      mietzahlungen.value = mietzahlungen.value.filter((m) => m.id !== id)
      if (currentMietzahlung.value?.id === id) {
        currentMietzahlung.value = null
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
   * Mietzahlung als bezahlt markieren.
   */
  async function markPaid(
    id: string,
    payload: { betrag_ist?: number; gezahlt_am?: string } = {},
  ): Promise<Mietzahlung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Mietzahlung>(`/mietzahlungen/${id}/bezahlen`, payload)
      const index = mietzahlungen.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        mietzahlungen.value[index] = data
      }
      currentMietzahlung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Mahnstufe manuell erhöhen.
   */
  async function escalate(id: string): Promise<Mietzahlung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Mietzahlung>(`/mietzahlungen/${id}/mahnen`)
      const index = mietzahlungen.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        mietzahlungen.value[index] = data
      }
      if (currentMietzahlung.value?.id === id) {
        currentMietzahlung.value = data
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
   * Aktuelle Mietzahlung manuell setzen.
   */
  function setCurrentMietzahlung(m: Mietzahlung | null): void {
    currentMietzahlung.value = m
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    mietzahlungen,
    currentMietzahlung,
    loading,
    saving,
    error,
    fetchMietzahlungen,
    fetchMietzahlung,
    createMietzahlung,
    updateMietzahlung,
    deleteMietzahlung,
    markPaid,
    escalate,
    setCurrentMietzahlung,
    clearError,
  }
})
