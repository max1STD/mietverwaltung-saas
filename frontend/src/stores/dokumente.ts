import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/api/client'
import type { ApiError } from '@/api/client'

export interface Dokument {
  id: number
  entity_type: string
  entity_id: number
  titel: string
  typ: string
  jahr: number | null
  file_name: string
  file_size: number
  content_type: string
  status: string
  ocr_status?: string | null
  ocr_text?: string | null
  ocr_confidence?: number | null
  created_at: string
  upload_error: string | null
}

export interface DokumentOcrResult {
  id: number
  ocr_status: string
  ocr_text: string | null
  ocr_confidence: number | null
  ocr_engine: string | null
  ocr_finished_at: string | null
}

export type DokumentTyp =
  | 'mietvertrag'
  | 'nebenkostenabrechnung'
  | 'korrespondenz'
  | 'foto'
  | 'rechnung'
  | 'sonstiges'

export const useDokumenteStore = defineStore('dokumente', () => {
  const dokumente = ref<Dokument[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  const count = computed(() => dokumente.value.length)

  function resetError(): void {
    error.value = null
  }

  async function fetchDokumente(entityType?: string, entityId?: number): Promise<Dokument[]> {
    loading.value = true
    resetError()
    try {
      const params: Record<string, string | number> = {}
      if (entityType) params.entity_type = entityType
      if (entityId !== undefined) params.entity_id = entityId
      const response = await apiClient.get('/dokumente/', { params })
      dokumente.value = response.data.items || []
      return dokumente.value
    } catch (err) {
      error.value = err as ApiError
      return []
    } finally {
      loading.value = false
    }
  }

  async function uploadDokument(
    entityType: string,
    entityId: number,
    file: File,
    titel: string,
    typ: DokumentTyp = 'sonstiges',
    jahr?: number,
  ): Promise<Dokument | null> {
    saving.value = true
    resetError()
    try {
      const formData = new FormData()
      formData.append('entity_type', entityType)
      formData.append('entity_id', String(entityId))
      formData.append('titel', titel)
      formData.append('typ', typ)
      formData.append('file', file)
      if (jahr !== undefined) formData.append('jahr', String(jahr))

      const response = await apiClient.post('/dokumente/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      dokumente.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err as ApiError
      return null
    } finally {
      saving.value = false
    }
  }

  async function deleteDokument(id: number): Promise<boolean> {
    saving.value = true
    resetError()
    try {
      await apiClient.delete(`/dokumente/${id}`)
      dokumente.value = dokumente.value.filter((d) => d.id !== id)
      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    } finally {
      saving.value = false
    }
  }

  function downloadUrl(id: number): string {
    return `/api/v1/dokumente/${id}/download`
  }

  function previewUrl(id: number): string {
    return `/api/v1/dokumente/${id}/preview`
  }

  async function fetchOcrText(id: number): Promise<DokumentOcrResult | null> {
    try {
      const response = await apiClient.get(`/dokumente/${id}/ocr`)
      return response.data
    } catch (err) {
      error.value = err as ApiError
      return null
    }
  }

  return {
    dokumente,
    loading,
    saving,
    error,
    count,
    fetchDokumente,
    uploadDokument,
    deleteDokument,
    downloadUrl,
    previewUrl,
    fetchOcrText,
    resetError,
  }
})
