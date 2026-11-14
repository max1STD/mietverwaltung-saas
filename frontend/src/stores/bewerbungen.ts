import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Bewerbungen-Store — Verwaltung eingehender Mieter-Bewerbungen.
 *
 * Endpunkte:
 * - GET    /api/v1/bewerbungen
 * - POST   /api/v1/bewerbungen
 * - PATCH  /api/v1/bewerbungen/{id}
 * - DELETE /api/v1/bewerbungen/{id}
 * - POST   /api/v1/bewerbungen/{id}/annehmen
 * - POST   /api/v1/bewerbungen/{id}/ablehnen
 */

export type BewerbungStatus = 'neu' | 'in_pruefung' | 'angenommen' | 'abgelehnt'

export interface BewerbungNestedEinheit {
  id: string
  name: string
  objekt_name: string
}

export interface BewerbungDocument {
  name: string
  url: string
  uploaded_at?: string
}

export interface Bewerbung {
  id: string
  vermieter_id: string
  einheit_id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  income_monthly?: number
  schufa_score?: number
  documents?: BewerbungDocument[]
  status: BewerbungStatus
  applied_at?: string
  decided_at?: string | null
  decided_by?: string | null
  created_at?: string
  updated_at?: string
  einheit?: BewerbungNestedEinheit | null
}

export interface BewerbungCreatePayload {
  einheit_id: string
  first_name: string
  last_name: string
  email: string
  phone?: string
  income_monthly?: number
  schufa_score?: number
  documents?: BewerbungDocument[]
}

export interface BewerbungUpdatePayload {
  status?: BewerbungStatus
  income_monthly?: number
  schufa_score?: number
  documents?: BewerbungDocument[]
  first_name?: string
  last_name?: string
  email?: string
  phone?: string
}

export const useBewerbungenStore = defineStore('bewerbungen', () => {
  // State
  const bewerbungen = ref<Bewerbung[]>([])
  const currentBewerbung = ref<Bewerbung | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Bewerbungen des Vermieters laden.
   */
  async function fetchBewerbungen(): Promise<Bewerbung[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Bewerbung[]>('/bewerbungen')
      bewerbungen.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelne Bewerbung laden.
   */
  async function fetchBewerbungById(id: string): Promise<Bewerbung | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Bewerbung>(`/bewerbungen/${id}`)
      currentBewerbung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neue Bewerbung anlegen (z. B. manueller Eintrag oder externer Import).
   */
  async function createBewerbung(payload: BewerbungCreatePayload): Promise<Bewerbung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Bewerbung>('/bewerbungen', payload)
      bewerbungen.value.unshift(data)
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Bewerbung aktualisieren.
   */
  async function updateBewerbung(id: string, payload: BewerbungUpdatePayload): Promise<Bewerbung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Bewerbung>(`/bewerbungen/${id}`, payload)
      const index = bewerbungen.value.findIndex((b) => b.id === id)
      if (index !== -1) {
        bewerbungen.value[index] = data
      }
      if (currentBewerbung.value?.id === id) {
        currentBewerbung.value = data
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
   * Bewerbung löschen (soft).
   */
  async function deleteBewerbung(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/bewerbungen/${id}`)
      bewerbungen.value = bewerbungen.value.filter((b) => b.id !== id)
      if (currentBewerbung.value?.id === id) {
        currentBewerbung.value = null
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
   * Bewerbung annehmen — erzeugt Mieter und Mietvertrag.
   */
  async function annehmen(id: string): Promise<Bewerbung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Bewerbung>(`/bewerbungen/${id}/annehmen`, {})
      const index = bewerbungen.value.findIndex((b) => b.id === id)
      if (index !== -1) {
        bewerbungen.value[index] = data
      }
      currentBewerbung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Bewerbung ablehnen.
   */
  async function ablehnen(id: string, grund?: string): Promise<Bewerbung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Bewerbung>(`/bewerbungen/${id}/ablehnen`, { grund })
      const index = bewerbungen.value.findIndex((b) => b.id === id)
      if (index !== -1) {
        bewerbungen.value[index] = data
      }
      currentBewerbung.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Aktuelle Bewerbung manuell setzen.
   */
  function setCurrentBewerbung(b: Bewerbung | null): void {
    currentBewerbung.value = b
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    bewerbungen,
    currentBewerbung,
    loading,
    saving,
    error,
    fetchBewerbungen,
    fetchBewerbungById,
    createBewerbung,
    updateBewerbung,
    deleteBewerbung,
    annehmen,
    ablehnen,
    setCurrentBewerbung,
    clearError,
  }
})
