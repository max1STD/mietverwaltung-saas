import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

export interface AdminUser {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'vermieter' | 'mieter'
  is_active: boolean
  email_verified: boolean
  phone: string | null
  firma: string | null
  vermieter_id: number | null
  created_at: string | null
}

export interface AdminUserCreatePayload {
  email: string
  password: string
  full_name: string
  role: 'vermieter' | 'mieter'
  vermieter_id?: number | null
}

export interface AdminUserUpdatePayload {
  full_name?: string
  phone?: string | null
  role?: 'admin' | 'vermieter' | 'mieter'
  is_active?: boolean
  vermieter_id?: number | null
}

export interface AdminStats {
  vermieter_count: number
  mieter_count: number
  objekte_count: number
  einheiten_count: number
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

export const useAdminStore = defineStore('admin', () => {
  const users = ref<AdminUser[]>([])
  const userTotal = ref(0)
  const stats = ref<AdminStats | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  const vermieterOptions = computed(() =>
    users.value.filter((u) => u.role === 'vermieter' && u.is_active),
  )

  function resetError(): void {
    error.value = null
  }

  async function fetchStats(): Promise<AdminStats | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<AdminStats>('/admin/stats')
      stats.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  async function fetchUsers(params: {
    role?: string
    search?: string
    active_only?: boolean
    skip?: number
    limit?: number
  } = {}): Promise<PaginatedResponse<AdminUser> | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<PaginatedResponse<AdminUser>>('/admin/users', {
        params,
      })
      users.value = data.items
      userTotal.value = data.total
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  async function createUser(payload: AdminUserCreatePayload): Promise<AdminUser | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<AdminUser>('/admin/users', payload)
      users.value.unshift(data)
      userTotal.value += 1
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  async function updateUser(id: number, payload: AdminUserUpdatePayload): Promise<AdminUser | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<AdminUser>(`/admin/users/${id}`, payload)
      const index = users.value.findIndex((u) => u.id === id)
      if (index !== -1) {
        users.value[index] = data
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  async function resetPassword(id: number, newPassword: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.post(`/admin/users/${id}/reset-password`, { new_password: newPassword })
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      saving.value = false
    }
  }

  async function deleteUser(id: number): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/admin/users/${id}`)
      users.value = users.value.filter((u) => u.id !== id)
      userTotal.value = Math.max(0, userTotal.value - 1)
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      saving.value = false
    }
  }

  return {
    users,
    userTotal,
    stats,
    loading,
    saving,
    error,
    vermieterOptions,
    fetchStats,
    fetchUsers,
    createUser,
    updateUser,
    resetPassword,
    deleteUser,
    resetError,
  }
})
