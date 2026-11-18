import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Zähler-Store — Verwaltung von Zählern (Strom/Gas/Wasser) und deren Ablesungen.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/zaehler
 * - GET/POST/PATCH/DELETE /api/v1/zaehler/{id}/ablesungen
 */

export type ZaehlerTyp = 'strom' | 'gas' | 'wasser' | 'waerme' | 'kaltwasser' | 'sonstiges'

export interface Zaehler {
  id: string
  vermieter_id: string
  einheit_id: string
  bezeichnung: string
  zaehlernummer?: string | null
  typ: ZaehlerTyp
  einheit: string
  ist_hauptzaehler: boolean
  ablesedatum?: string | null
  created_at?: string
  updated_at?: string
  deleted_at?: string | null
}

export interface ZaehlerMitAblesungen extends Zaehler {
  ablesungen: Zaehlerablesung[]
}

export interface Zaehlerablesung {
  id: string
  vermieter_id: string
  zaehler_id: string
  ablesedatum: string
  zaehlerstand: string
  verbrauch?: string | null
  ableser?: string | null
  notizen?: string | null
  ist_schaetzung: boolean
  created_at?: string
  updated_at?: string
  deleted_at?: string | null
}

export const useZaehlerStore = defineStore('zaehler', () => {
  const zaehler = ref<Zaehler[]>([])
  const currentZaehler = ref<ZaehlerMitAblesungen | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  async function fetchZaehler(einheitId?: string): Promise<Zaehler[]> {
    loading.value = true
    error.value = null
    try {
      const params = einheitId && String(einheitId).trim() !== '' ? { einheit_id: einheitId } : {}
      const { data } = await apiClient.get<Zaehler[]>('/zaehler', { params })
      zaehler.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  async function fetchZaehlerDetail(id: string): Promise<ZaehlerMitAblesungen | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<ZaehlerMitAblesungen>(`/zaehler/${id}`)
      currentZaehler.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  async function createZaehler(payload: Record<string, unknown>): Promise<Zaehler | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Zaehler>('/zaehler', payload)
      zaehler.value.push(data)
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  async function updateZaehler(id: string, payload: Record<string, unknown>): Promise<Zaehler | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Zaehler>(`/zaehler/${id}`, payload)
      const index = zaehler.value.findIndex((z) => z.id === id)
      if (index !== -1) {
        zaehler.value[index] = data
      }
      if (currentZaehler.value && currentZaehler.value.id === id) {
        currentZaehler.value = { ...currentZaehler.value, ...data }
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  async function deleteZaehler(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/zaehler/${id}`)
      zaehler.value = zaehler.value.filter((z) => z.id !== id)
      if (currentZaehler.value && currentZaehler.value.id === id) {
        currentZaehler.value = null
      }
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      saving.value = false
    }
  }

  async function createAblesung(
    zaehlerId: string,
    payload: Partial<Zaehlerablesung>,
  ): Promise<Zaehlerablesung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Zaehlerablesung>(
        `/zaehler/${zaehlerId}/ablesungen`,
        payload,
      )
      if (currentZaehler.value && currentZaehler.value.id === zaehlerId) {
        currentZaehler.value.ablesungen.unshift(data)
        currentZaehler.value.ablesungen.sort(
          (a, b) => new Date(b.ablesedatum).getTime() - new Date(a.ablesedatum).getTime(),
        )
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  async function updateAblesung(
    zaehlerId: string,
    ablesungId: string,
    payload: Partial<Zaehlerablesung>,
  ): Promise<Zaehlerablesung | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Zaehlerablesung>(
        `/zaehler/${zaehlerId}/ablesungen/${ablesungId}`,
        payload,
      )
      if (currentZaehler.value && currentZaehler.value.id === zaehlerId) {
        const index = currentZaehler.value.ablesungen.findIndex((a) => a.id === ablesungId)
        if (index !== -1) {
          currentZaehler.value.ablesungen[index] = data
        }
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  async function deleteAblesung(zaehlerId: string, ablesungId: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/zaehler/${zaehlerId}/ablesungen/${ablesungId}`)
      if (currentZaehler.value && currentZaehler.value.id === zaehlerId) {
        currentZaehler.value.ablesungen = currentZaehler.value.ablesungen.filter(
          (a) => a.id !== ablesungId,
        )
      }
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      saving.value = false
    }
  }

  function clearError(): void {
    error.value = null
  }

  function clearCurrent(): void {
    currentZaehler.value = null
  }

  return {
    zaehler,
    currentZaehler,
    loading,
    saving,
    error,
    fetchZaehler,
    fetchZaehlerDetail,
    createZaehler,
    updateZaehler,
    deleteZaehler,
    createAblesung,
    updateAblesung,
    deleteAblesung,
    clearError,
    clearCurrent,
  }
})
