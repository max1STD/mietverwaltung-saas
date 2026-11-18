import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Mietzahlungen-Store — Soll-/Ist-Überwachung und Mahnwesen.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/mietzahlungen
 * - GET /api/v1/mietzahlungen/{id}
 * - POST /api/v1/mietzahlungen/{id}/mark-paid
 * - POST /api/v1/mietzahlungen/{id}/mahnstufe
 * - POST /api/v1/mietzahlungen/actions/generate
 */

export type MietzahlungStatus = 'offen' | 'teilweise' | 'bezahlt' | 'ueberfaellig'

export interface Mietzahlung {
  id: string
  vermieter_id?: string
  mieter_id?: string
  vertrag_id?: string
  mieter?: {
    id: string
    name?: string
  }
  einheit?: {
    id: string
    name?: string
    objekt_name?: string
  }
  vertrag?: {
    id: string
    miete_cold?: string | number
    nebenkosten_voraus?: string | number
  }
  betrag_soll: number
  betrag_ist?: number | null
  offener_betrag: number
  zahlungsdatum: string | null
  mahnstufe: number
  zahlungsreferenz?: string | null
  created_at?: string
  updated_at?: string | null
  deleted_at?: string | null
}

export interface MietzahlungCreatePayload {
  vertrag_id: string
  mieter_id?: string
  betrag_soll: number
  betrag_ist?: number
  zahlungsdatum?: string
  zahlungsreferenz?: string
}

export interface MarkPaidPayload {
  betrag_ist: number
  zahlungsdatum: string
}

export const useMietzahlungenStore = defineStore('mietzahlungen', () => {
  // State
  const mietzahlungen = ref<Mietzahlung[]>([])
  const currentMietzahlung = ref<Mietzahlung | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  function statusFor(zahlung: Mietzahlung): MietzahlungStatus {
    const ist = zahlung.betrag_ist ?? 0
    if (ist >= zahlung.betrag_soll) return 'bezahlt'
    if (ist > 0) return 'teilweise'
    // Einfache Überfälligkeitsheuristik: Fälligkeitsdatum liegt in der Vergangenheit
    if (zahlung.zahlungsdatum && new Date(zahlung.zahlungsdatum) < new Date() && ist === 0) {
      return 'ueberfaellig'
    }
    return 'offen'
  }

  /**
   * Alle Mietzahlungen laden (optional gefiltert).
   */
  async function fetchMietzahlungen(params?: {
    offen?: boolean
    mieter_id?: string
    vertrag_id?: string
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
  async function createMietzahlung(payload: MietzahlungCreatePayload): Promise<Mietzahlung | null> {
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
    payload: Partial<MietzahlungCreatePayload>,
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
  async function markPaid(id: string, payload: MarkPaidPayload): Promise<Mietzahlung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Mietzahlung>(`/mietzahlungen/${id}/mark-paid`, payload)
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
      const { data } = await apiClient.post<Mietzahlung>(`/mietzahlungen/${id}/mahnstufe`)
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
   * Mietzahlungen für einen Monat aus aktiven Verträgen generieren.
   */
  async function generate(monat: string): Promise<Mietzahlung[]> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Mietzahlung[]>('/mietzahlungen/actions/generate', { monat })
      // Neu generierte anhängen, bestehende nicht überschreiben
      const existingIds = new Set(mietzahlungen.value.map((m) => m.id))
      for (const z of data) {
        if (!existingIds.has(z.id)) {
          mietzahlungen.value.push(z)
        }
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      saving.value = false
    }
  }

  function setCurrentMietzahlung(m: Mietzahlung | null): void {
    currentMietzahlung.value = m
  }

  function clearError(): void {
    error.value = null
  }

  return {
    mietzahlungen,
    currentMietzahlung,
    loading,
    saving,
    error,
    statusFor,
    fetchMietzahlungen,
    fetchMietzahlung,
    createMietzahlung,
    updateMietzahlung,
    deleteMietzahlung,
    markPaid,
    escalate,
    generate,
    setCurrentMietzahlung,
    clearError,
  }
})
