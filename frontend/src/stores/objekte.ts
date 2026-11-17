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
  public_id?: string
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
  grundstuecksflaeche_qm?: number | null
  wohnflaeche_gesamt_qm?: number | null
  nutzflaeche_gesamt_qm?: number | null
  vermietbare_flaeche_qm?: number | null
  anzahl_einheiten?: number | null
  baujahr_objekt?: number | null
  bauweise?: string | null
  zustand?: string | null
  denkmalschutz?: boolean | null
  denkmalschutz_bis?: string | null
  energieausweis_art?: string | null
  energieausweis_gueltig_bis?: string | null
  energieverbrauch_kennwert?: number | null
  energieverbrauch_klasse?: string | null
  heizungsart?: string | null
  warmwasserbereitung?: string | null
  solaranlage?: boolean | null
  land?: string | null
  adresszusatz?: string | null
  lagebeschreibung?: string | null
  kaufpreis_pro_qm?: number | null
  gesamtmiete_ist?: number | null
  gesamtmiete_soll?: number | null
  barrierefrei?: boolean | null
  aufzug?: boolean | null
  gartennutzung?: boolean | null
  anmerkungen?: string | null
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
  public_id?: string
  objekt_id: string
  name: string
  etage?: number
  wohnflaeche_qm?: number
  nutzflaeche_qm?: number
  balkon_flaeche_qm?: number
  terrasse_flaeche_qm?: number
  garten_flaeche_qm?: number
  gewerbeflaeche_qm?: number
  rooms?: number
  wohnzimmer?: number
  schlafzimmer?: number
  badezimmer?: number
  kaltmiete?: number
  nebenkosten_vorschuss?: number
  status?: EinheitStatus | string
  energy_class?: string
  baujahr_einheit?: number
  heizungsart?: string
  warmwasserbereitung?: string
  fenster?: string
  boden?: string
  sanitaer?: string
  kueche?: string
  energieausweis_art?: string
  energieverbrauch_kennwert?: number
  energieverbrauch_klasse?: string
  bauweise?: string
  denkmalschutz?: boolean
  denkmalschutz_bis?: string
  last_renovation?: string
  renovierungsstatus?: string
  zustand?: string
  available_from?: string
  bewohnbar_ab?: string
  anmerkungen?: string
  balkon?: boolean
  terrasse?: boolean
  garten?: boolean
  garage?: boolean
  stellplatz?: boolean
  keller?: boolean
  aufzug?: boolean
  barrierefrei?: boolean
  moebliert?: boolean
  created_at?: string
  updated_at?: string
  aktueller_mieter?: {
    id: string
    name: string
  }
  /** Legacy alias fuer aktueller_mieter */
  current_mieter?: {
    id: string
    name: string
  }
  vermietungsstatus?: string
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
      const index = objekte.value.findIndex((o) => o.id === id || o.public_id === id)
      if (index !== -1) {
        objekte.value[index] = data
      }
      if (currentObjekt.value && (currentObjekt.value.id === id || currentObjekt.value.public_id === id)) {
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
      objekte.value = objekte.value.filter((o) => o.id !== id && o.public_id !== id)
      if (currentObjekt.value && (currentObjekt.value.id === id || currentObjekt.value.public_id === id)) {
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
      const index = einheiten.value.findIndex((e) => e.id === id || e.public_id === id)
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
      einheiten.value = einheiten.value.filter((e) => e.id !== id && e.public_id !== id)
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
