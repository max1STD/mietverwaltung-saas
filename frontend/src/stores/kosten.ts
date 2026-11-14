import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Kosten-Store — Verwaltung von Betriebskosten und Ausgaben.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/kosten
 * - GET /api/v1/kosten/{id}
 * - GET /api/v1/kostenkategorien
 * - POST /api/v1/kosten/{id}/scan (Beleg-Scan-Stub)
 */

export type Umlageschluessel = 'nach_qm' | 'nach_personen' | 'nach_verbrauch' | 'gleich'

export interface Kostenkategorie {
  id: string
  name?: string
  bezeichnung?: string
  beschreibung?: string
  umlagefaehig_standard?: boolean
}

export interface ScanErgebnis {
  betrag_vorschlag?: number
  kategorie_vorschlag?: string
  umlagefaehig_vorschlag?: boolean
  umlageschluessel_vorschlag?: Umlageschluessel
  konfidenz?: 'niedrig' | 'mittel' | 'hoch'
}

export interface Kosten {
  id: string
  name?: string
  vermieter_id?: string
  objekt_id?: string
  einheit_id?: string
  kategorie_id?: string
  kategorie?: Kostenkategorie
  objekt?: {
    id: string
    name?: string
    bezeichnung?: string
  }
  einheit?: {
    id: string
    name?: string
    bezeichnung?: string
  }
  bezeichnung: string
  betrag: number
  datum: string
  umlagefaehig: boolean
  umlageschluessel?: Umlageschluessel | string
  beleg_url?: string
  beleg_scan_status?: 'pending' | 'fertig' | 'fehler'
  scan_ergebnis?: ScanErgebnis | null
  notizen?: string
  created_at?: string
  updated_at?: string
}

export const useKostenStore = defineStore('kosten', () => {
  // State
  const kosten = ref<Kosten[]>([])
  const currentKosten = ref<Kosten | null>(null)
  const kategorien = ref<Kostenkategorie[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const scanLoading = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Kosten laden (optional gefiltert).
   */
  async function fetchKosten(params?: {
    jahr?: number
    objekt_id?: string
    einheit_id?: string
  }): Promise<Kosten[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Kosten[]>('/kosten', { params })
      kosten.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelne Kosten laden.
   */
  async function fetchKostenById(id: string): Promise<Kosten | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Kosten>(`/kosten/${id}`)
      currentKosten.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neue Kosten anlegen.
   */
  async function createKosten(payload: Partial<Kosten>): Promise<Kosten | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Kosten>('/kosten', payload)
      kosten.value.push(data)
      currentKosten.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Kosten aktualisieren.
   */
  async function updateKosten(id: string, payload: Partial<Kosten>): Promise<Kosten | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Kosten>(`/kosten/${id}`, payload)
      const index = kosten.value.findIndex((k) => k.id === id)
      if (index !== -1) {
        kosten.value[index] = data
      }
      if (currentKosten.value?.id === id) {
        currentKosten.value = data
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
   * Kosten löschen.
   */
  async function deleteKosten(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/kosten/${id}`)
      kosten.value = kosten.value.filter((k) => k.id !== id)
      if (currentKosten.value?.id === id) {
        currentKosten.value = null
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
   * Kostenkategorien laden.
   */
  async function fetchKategorien(): Promise<Kostenkategorie[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Kostenkategorie[]>('/kostenkategorien')
      kategorien.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Beleg-Scan durchführen (UI-Stub, keine echte OCR/KI).
   *
   * Liefert im Erfolgsfall ein simuliertes Scan-Ergebnis zurück,
   * das im Formular als Vorschlag übernommen werden kann.
   */
  async function scanReceipt(id: string, file?: File): Promise<ScanErgebnis | null> {
    scanLoading.value = true
    error.value = null
    try {
      const formData = new FormData()
      if (file) {
        formData.append('beleg', file)
      }
      const { data } = await apiClient.post<ScanErgebnis>(`/kosten/${id}/scan`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      // Lokales Kosten-Objekt anreichern
      const index = kosten.value.findIndex((k) => k.id === id)
      if (index !== -1) {
        kosten.value[index] = {
          ...kosten.value[index],
          scan_ergebnis: data,
          beleg_scan_status: 'fertig',
        }
      }
      if (currentKosten.value?.id === id) {
        currentKosten.value = {
          ...currentKosten.value,
          scan_ergebnis: data,
          beleg_scan_status: 'fertig',
        }
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      scanLoading.value = false
    }
  }

  /**
   * Vorschlag aus Scan-Ergebnis simulieren (für UI-Tests ohne Backend).
   */
  function simulateScanResult(): ScanErgebnis {
    return {
      betrag_vorschlag: 124.56,
      kategorie_vorschlag: 'Müllgebühren',
      umlagefaehig_vorschlag: true,
      umlageschluessel_vorschlag: 'nach_qm',
      konfidenz: 'mittel',
    }
  }

  /**
   * Aktuelle Kosten manuell setzen.
   */
  function setCurrentKosten(k: Kosten | null): void {
    currentKosten.value = k
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    kosten,
    currentKosten,
    kategorien,
    loading,
    saving,
    scanLoading,
    error,
    fetchKosten,
    fetchKostenById,
    createKosten,
    updateKosten,
    deleteKosten,
    fetchKategorien,
    scanReceipt,
    simulateScanResult,
    setCurrentKosten,
    clearError,
  }
})
