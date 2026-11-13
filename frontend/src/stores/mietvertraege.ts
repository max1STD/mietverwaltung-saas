import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Mietvertraege-Store — Verwaltung aller Mietverträge.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/mietvertraege
 * - GET /api/v1/mietvertraege/{id}
 */

export type MietvertragStatus = 'aktiv' | 'gekuendigt' | 'beendet'

export interface Mietvertrag {
  id: string
  mieter_id: string
  einheit_id: string
  objekt_id?: string
  mietbeginn: string
  mietende?: string
  kaltmiete: number
  nebenkosten_vorschuss?: number
  kaution?: number
  status?: MietvertragStatus | string
  created_at?: string
  updated_at?: string
  mieter?: {
    id: string
    name: string
  }
  einheit?: {
    id: string
    bezeichnung: string
  }
  objekt?: {
    id: string
    bezeichnung: string
  }
}

export const useMietvertraegeStore = defineStore('mietvertraege', () => {
  // State
  const mietvertraege = ref<Mietvertrag[]>([])
  const currentMietvertrag = ref<Mietvertrag | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Mietverträge des Vermieters laden.
   */
  async function fetchMietvertraege(): Promise<Mietvertrag[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Mietvertrag[]>('/mietvertraege')
      mietvertraege.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelnen Mietvertrag laden.
   */
  async function fetchMietvertrag(id: string): Promise<Mietvertrag | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Mietvertrag>(`/mietvertraege/${id}`)
      currentMietvertrag.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neuen Mietvertrag anlegen.
   */
  async function createMietvertrag(payload: Partial<Mietvertrag>): Promise<Mietvertrag | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Mietvertrag>('/mietvertraege', payload)
      mietvertraege.value.push(data)
      currentMietvertrag.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Mietvertrag aktualisieren.
   */
  async function updateMietvertrag(
    id: string,
    payload: Partial<Mietvertrag>,
  ): Promise<Mietvertrag | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Mietvertrag>(`/mietvertraege/${id}`, payload)
      const index = mietvertraege.value.findIndex((mv) => mv.id === id)
      if (index !== -1) {
        mietvertraege.value[index] = data
      }
      if (currentMietvertrag.value?.id === id) {
        currentMietvertrag.value = data
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
   * Mietvertrag löschen.
   */
  async function deleteMietvertrag(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/mietvertraege/${id}`)
      mietvertraege.value = mietvertraege.value.filter((mv) => mv.id !== id)
      if (currentMietvertrag.value?.id === id) {
        currentMietvertrag.value = null
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
   * Mietverträge eines Mieters laden (Hilfsmethode für Detailansicht).
   */
  async function fetchMietvertraegeByMieter(mieterId: string): Promise<Mietvertrag[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Mietvertrag[]>('/mietvertraege', {
        params: { mieter_id: mieterId },
      })
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Aktuellen Mietvertrag setzen.
   */
  function setCurrentMietvertrag(mv: Mietvertrag | null): void {
    currentMietvertrag.value = mv
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    mietvertraege,
    currentMietvertrag,
    loading,
    saving,
    error,
    fetchMietvertraege,
    fetchMietvertrag,
    createMietvertrag,
    updateMietvertrag,
    deleteMietvertrag,
    fetchMietvertraegeByMieter,
    setCurrentMietvertrag,
    clearError,
  }
})
