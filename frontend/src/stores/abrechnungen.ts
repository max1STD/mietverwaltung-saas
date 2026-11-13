import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Abrechnungen-Store — Nebenkostenabrechnungen pro Einheit/Jahr.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/abrechnungen
 * - GET /api/v1/abrechnungen/{id}
 * - POST /api/v1/abrechnungen/{id}/berechnen
 * - POST /api/v1/abrechnungen/{id}/finalisieren
 */

export type AbrechnungStatus = 'entwurf' | 'berechnet' | 'finalisiert' | 'versendet'

export interface AbrechnungPosition {
  id: string
  abrechnung_id: string
  kategorie: string
  gesamtbetrag: number
  verteilungsschluessel: string
  umlageanteil: number
  verteilt_auf_qm?: number
  verteilt_auf_personen?: number
  verbrauch_einheit?: string
  notizen?: string
  created_at?: string
  updated_at?: string
}

export interface Abrechnung {
  id: string
  vermieter_id?: string
  objekt_id?: string
  einheit_id: string
  einheit?: {
    id: string
    bezeichnung: string
  }
  objekt?: {
    id: string
    bezeichnung: string
  }
  jahr: number
  zeitraum_von: string
  zeitraum_bis: string
  status: AbrechnungStatus | string
  gesamtkosten?: number
  umlageanteil?: number
  positions?: AbrechnungPosition[]
  created_at?: string
  updated_at?: string
}

export const useAbrechnungenStore = defineStore('abrechnungen', () => {
  // State
  const abrechnungen = ref<Abrechnung[]>([])
  const currentAbrechnung = ref<Abrechnung | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Abrechnungen laden (optional gefiltert).
   */
  async function fetchAbrechnungen(params?: {
    jahr?: number
    einheit_id?: string
    objekt_id?: string
    status?: string
  }): Promise<Abrechnung[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Abrechnung[]>('/abrechnungen', { params })
      abrechnungen.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelne Abrechnung inklusive Positionen laden.
   */
  async function fetchAbrechnung(id: string): Promise<Abrechnung | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Abrechnung>(`/abrechnungen/${id}`)
      currentAbrechnung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neue Abrechnung anlegen.
   */
  async function createAbrechnung(payload: Partial<Abrechnung>): Promise<Abrechnung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Abrechnung>('/abrechnungen', payload)
      abrechnungen.value.push(data)
      currentAbrechnung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Abrechnung aktualisieren (nur im Entwurf-Status).
   */
  async function updateAbrechnung(
    id: string,
    payload: Partial<Abrechnung>,
  ): Promise<Abrechnung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Abrechnung>(`/abrechnungen/${id}`, payload)
      const index = abrechnungen.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        abrechnungen.value[index] = data
      }
      if (currentAbrechnung.value?.id === id) {
        currentAbrechnung.value = data
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
   * Abrechnung löschen.
   */
  async function deleteAbrechnung(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/abrechnungen/${id}`)
      abrechnungen.value = abrechnungen.value.filter((a) => a.id !== id)
      if (currentAbrechnung.value?.id === id) {
        currentAbrechnung.value = null
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
   * Abrechnungspositionen berechnen lassen.
   */
  async function calculatePositions(id: string): Promise<Abrechnung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Abrechnung>(`/abrechnungen/${id}/berechnen`)
      const index = abrechnungen.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        abrechnungen.value[index] = data
      }
      currentAbrechnung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Abrechnung finalisieren.
   */
  async function finalize(id: string): Promise<Abrechnung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Abrechnung>(`/abrechnungen/${id}/finalisieren`)
      const index = abrechnungen.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        abrechnungen.value[index] = data
      }
      currentAbrechnung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Aktuelle Abrechnung manuell setzen.
   */
  function setCurrentAbrechnung(a: Abrechnung | null): void {
    currentAbrechnung.value = a
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    abrechnungen,
    currentAbrechnung,
    loading,
    saving,
    error,
    fetchAbrechnungen,
    fetchAbrechnung,
    createAbrechnung,
    updateAbrechnung,
    deleteAbrechnung,
    calculatePositions,
    finalize,
    setCurrentAbrechnung,
    clearError,
  }
})
