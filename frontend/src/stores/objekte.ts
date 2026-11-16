import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Objekte-Store — Verwaltung von Immobilien und deren Wohneinheiten.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/objekte
 * - GET /api/v1/objekte/{id}
 * - GET/POST /api/v1/objekte/{objekt_id}/einheiten
 * - PATCH/DELETE /api/v1/einheiten/{id}
 */

export type ObjektTyp =
  | 'einfamilienhaus'
  | 'mehrfamilienhaus'
  | 'doppelhaushaelfte'
  | 'reihenhaus'
  | 'gewerbe'
  | 'grundstueck'
  | 'sonstiges'

export interface Objekt {
  id: string
  vermieter_id: string
  name: string
  /** Alias für ältere Komponenten */
  bezeichnung?: string
  address: string
  /** Alias für ältere Komponenten */
  adresse?: string
  plz?: string
  ort?: string
  typ?: ObjektTyp | string
  baujahr?: number | null
  kaufpreis?: number | null
  kaufdatum?: string | null
  eigenkapital?: number | null
  darlehen_betrag?: number | null
  zinssatz?: number | null
  tilgung?: number | null
  monatliche_rate?: number | null
  foto_url?: string | null
  notizen?: string
  created_at?: string
  updated_at?: string
  deleted_at?: string | null
  einheiten?: Einheit[]
  einheiten_count?: number
}

export type EinheitStatus = 'vermietet' | 'frei' | 'renovierung' | 'gesperrt'

export interface Einheit {
  id: string
  objekt_id: string
  name: string
  etage?: number
  wohnflaeche_qm?: number
  zimmer?: number
  kaltmiete?: number
  nebenkosten_vorschuss?: number
  status?: EinheitStatus | string
  energieklasse?: string
  letzte_renovierung?: string
  verfuegbar_ab?: string
  created_at?: string
  updated_at?: string
  aktueller_mieter?: {
    id: string
    name: string
  }
  /** Legacy alias für aktueller_mieter */
  current_mieter?: {
    id: string
    name: string
  }
}

export const useObjekteStore = defineStore('objekte', () => {
  // State
  const objekte = ref<Objekt[]>([])
  const currentObjekt = ref<Objekt | null>(null)
  const einheiten = ref<Einheit[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Objekte des Vermieters laden.
   */
  async function fetchObjekte(): Promise<Objekt[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Objekt[]>('/objekte')
      objekte.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelnes Objekt inklusive Detaildaten laden.
   */
  async function fetchObjekt(id: string): Promise<Objekt | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Objekt>(`/objekte/${id}`)
      currentObjekt.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neues Objekt anlegen.
   */
  async function createObjekt(payload: Partial<Objekt>): Promise<Objekt | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Objekt>('/objekte', payload)
      objekte.value.push(data)
      currentObjekt.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Bestehendes Objekt aktualisieren.
   */
  async function updateObjekt(id: string, payload: Partial<Objekt>): Promise<Objekt | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Objekt>(`/objekte/${id}`, payload)
      const index = objekte.value.findIndex((o) => o.id === id)
      if (index !== -1) {
        objekte.value[index] = data
      }
      if (currentObjekt.value?.id === id) {
        currentObjekt.value = data
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
   * Objekt löschen.
   */
  async function deleteObjekt(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/objekte/${id}`)
      objekte.value = objekte.value.filter((o) => o.id !== id)
      if (currentObjekt.value?.id === id) {
        currentObjekt.value = null
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
   * Einheiten eines Objekts laden.
   */
  async function fetchEinheiten(objektId: string): Promise<Einheit[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Einheit[]>(`/objekte/${objektId}/einheiten`)
      einheiten.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Neue Einheit zu einem Objekt hinzufügen.
   */
  async function createEinheit(objektId: string, payload: Partial<Einheit>): Promise<Einheit | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Einheit>(`/objekte/${objektId}/einheiten`, {
        ...payload,
        objekt_id: objektId,
      })
      einheiten.value.push(data)
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Einheit aktualisieren.
   */
  async function updateEinheit(id: string, payload: Partial<Einheit>): Promise<Einheit | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Einheit>(`/einheiten/${id}`, payload)
      const index = einheiten.value.findIndex((e) => e.id === id)
      if (index !== -1) {
        einheiten.value[index] = data
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
   * Einheit löschen.
   */
  async function deleteEinheit(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/einheiten/${id}`)
      einheiten.value = einheiten.value.filter((e) => e.id !== id)
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      saving.value = false
    }
  }

  /**
   * Aktuelles Objekt manuell setzen (z. B. aus einer Liste).
   */
  function setCurrentObjekt(objekt: Objekt | null): void {
    currentObjekt.value = objekt
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    objekte,
    currentObjekt,
    einheiten,
    loading,
    saving,
    error,
    fetchObjekte,
    fetchObjekt,
    createObjekt,
    updateObjekt,
    deleteObjekt,
    fetchEinheiten,
    createEinheit,
    updateEinheit,
    deleteEinheit,
    setCurrentObjekt,
    clearError,
  }
})
