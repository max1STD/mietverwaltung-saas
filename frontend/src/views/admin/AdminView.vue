<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="$router.push('/dashboard')">
          ← Zurück
        </button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Admin-Bereich</h1>
        <p class="text-gray-500">Verwaltung von Nutzern, Objekten und Einheiten</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <AppCard padding="md" shadow="sm" class="text-center">
          <p class="text-sm text-gray-500">Vermieter</p>
          <p class="text-2xl font-bold text-[#0D3B70]">{{ adminStore.stats?.vermieter_count ?? '–' }}</p>
        </AppCard>
        <AppCard padding="md" shadow="sm" class="text-center">
          <p class="text-sm text-gray-500">Mieter</p>
          <p class="text-2xl font-bold text-[#0D3B70]">{{ adminStore.stats?.mieter_count ?? '–' }}</p>
        </AppCard>
        <AppCard padding="md" shadow="sm" class="text-center">
          <p class="text-sm text-gray-500">Objekte</p>
          <p class="text-2xl font-bold text-[#0D3B70]">{{ adminStore.stats?.objekte_count ?? '–' }}</p>
        </AppCard>
        <AppCard padding="md" shadow="sm" class="text-center">
          <p class="text-sm text-gray-500">Einheiten</p>
          <p class="text-2xl font-bold text-[#0D3B70]">{{ adminStore.stats?.einheiten_count ?? '–' }}</p>
        </AppCard>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 mb-6">
        <nav class="flex gap-6">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="pb-2 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === tab.key ? 'border-[#0D3B70] text-[#0D3B70]' : 'border-transparent text-gray-500 hover:text-gray-700'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- User-Management -->
      <div v-if="activeTab === 'users'">
        <div class="flex flex-col sm:flex-row gap-4 mb-4">
          <AppInput
            id="user-search"
            v-model="search"
            label=""
            placeholder="Suche nach E-Mail, Name oder Firma"
            @input="debouncedSearch"
          />
          <select
            v-model="roleFilter"
            class="px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            @change="reloadUsers"
          >
            <option value="">Alle Rollen</option>
            <option value="vermieter">Vermieter</option>
            <option value="mieter">Mieter</option>
            <option value="admin">Admin</option>
          </select>
          <AppButton @click="showUserModal = true">+ Nutzer</AppButton>
        </div>

        <AppTable :items="adminStore.users" :columns="userColumns">
          <template #row="{ item }">
            <td class="py-3 px-4 font-medium text-gray-900">{{ item.full_name }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.email }}</td>
            <td class="py-3 px-4 text-sm text-gray-600 capitalize">{{ item.role }}</td>
            <td class="py-3 px-4">
              <AppBadge :variant="item.is_active ? 'green' : 'red'">{{ item.is_active ? 'Aktiv' : 'Inaktiv' }}</AppBadge>
            </td>
            <td class="py-3 px-4 text-sm text-gray-500">{{ formatDate(item.created_at) }}</td>
            <td class="py-3 px-4 text-right">
              <AppButton size="sm" variant="ghost" @click="editUser(item)">✎</AppButton>
            </td>
          </template>
        </AppTable>

        <div v-if="adminStore.userTotal > limit" class="flex justify-center gap-2 mt-4">
          <AppButton
            size="sm"
            variant="ghost"
            :disabled="skip === 0"
            @click="changePage(-1)"
          >
            ← Zurück
          </AppButton>
          <span class="text-sm text-gray-600 self-center">{{ page }} / {{ Math.ceil(adminStore.userTotal / limit) }}</span>
          <AppButton
            size="sm"
            variant="ghost"
            :disabled="skip + limit >= adminStore.userTotal"
            @click="changePage(1)"
          >
            Weiter →
          </AppButton>
        </div>
      </div>

      <!-- Objekte -->
      <div v-else-if="activeTab === 'objekte'">
        <p class="text-gray-500">Objektverwaltung kommt im nächsten Schritt.</p>
      </div>

      <!-- Einheiten -->
      <div v-else-if="activeTab === 'einheiten'">
        <p class="text-gray-500">Einheitenverwaltung kommt im nächsten Schritt.</p>
      </div>
    </div>

    <!-- Nutzer Modal -->
    <AppModal v-model="showUserModal" :title="editingUser ? 'Nutzer bearbeiten' : 'Neuen Nutzer anlegen'">
      <form class="space-y-4" @submit.prevent="saveUser">
        <AppInput
          id="user-email"
          v-model="userForm.email"
          label="E-Mail"
          type="email"
          required
          :disabled="!!editingUser"
          :error="errors.email"
        />
        <AppInput
          id="user-name"
          v-model="userForm.full_name"
          label="Vollständiger Name"
          required
          :error="errors.full_name"
        />
        <AppInput
          id="user-phone"
          v-model="userForm.phone"
          label="Telefon"
          :error="errors.phone"
        />

        <div v-if="!editingUser">
          <AppInput
            id="user-password"
            v-model="userForm.password"
            label="Passwort"
            type="password"
            required
            :error="errors.password"
          />
        </div>

        <div>
          <label for="user-role" class="block text-sm font-medium text-gray-700 mb-1">Rolle</label>
          <select
            id="user-role"
            v-model="userForm.role"
            class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            :class="{ 'border-red-500': errors.role }"
          >
            <option value="">Bitte wählen</option>
            <option value="vermieter">Vermieter</option>
            <option value="mieter">Mieter</option>
          </select>
          <p v-if="errors.role" class="mt-1 text-xs text-red-600">{{ errors.role }}</p>
        </div>

        <div v-if="userForm.role === 'mieter'">
          <label for="user-vermieter" class="block text-sm font-medium text-gray-700 mb-1">Vermieter zuweisen</label>
          <select
            id="user-vermieter"
            v-model="userForm.vermieter_id"
            class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
          >
            <option :value="null">Bitte wählen</option>
            <option v-for="v in adminStore.vermieterOptions" :key="v.id" :value="v.id">
              {{ v.full_name }} ({{ v.email }})
            </option>
          </select>
        </div>

        <BoolSelect
          id="user-active"
          v-model="userForm.is_active"
          label="Account aktiv"
        />

        <div class="flex justify-end gap-3 pt-2">
          <AppButton type="button" variant="ghost" @click="closeUserModal">Abbrechen</AppButton>
          <AppButton type="submit" :loading="adminStore.saving">Speichern</AppButton>
        </div>
      </form>

      <div v-if="editingUser" class="mt-6 pt-6 border-t border-gray-200 space-y-3">
        <div class="flex items-center gap-2">
          <AppInput
            id="reset-password"
            v-model="resetPasswordValue"
            label="Neues Passwort"
            type="password"
            :error="errors.reset_password"
          />
          <AppButton type="button" :loading="adminStore.saving" @click="doResetPassword">Zurücksetzen</AppButton>
        </div>

        <AppButton type="button" variant="danger" :loading="adminStore.saving" @click="doDeleteUser">
          Nutzer löschen
        </AppButton>
      </div>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAdminStore, type AdminUser, type AdminUserCreatePayload, type AdminUserUpdatePayload } from '@/stores/admin'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppModal from '@/components/ui/AppModal.vue'
import BoolSelect from '@/components/ui/BoolSelect.vue'

const adminStore = useAdminStore()
const { showToast } = useToast()

const activeTab = ref('users')
const tabs = [
  { key: 'users', label: 'Nutzer' },
  { key: 'objekte', label: 'Objekte' },
  { key: 'einheiten', label: 'Einheiten' },
]

const userColumns = [
  { key: 'full_name', label: 'Name' },
  { key: 'email', label: 'E-Mail' },
  { key: 'role', label: 'Rolle' },
  { key: 'is_active', label: 'Status' },
  { key: 'created_at', label: 'Erstellt' },
  { key: 'actions', label: '' },
]

const search = ref('')
const roleFilter = ref('')
const skip = ref(0)
const limit = 25
const page = computed(() => Math.floor(skip.value / limit) + 1)

const showUserModal = ref(false)
const editingUser = ref<AdminUser | null>(null)
const resetPasswordValue = ref('')

const userForm = reactive({
  email: '',
  full_name: '',
  phone: '',
  password: '',
  role: '',
  vermieter_id: null as number | null,
  is_active: 'true',
})

const errors = reactive({
  email: '',
  full_name: '',
  phone: '',
  password: '',
  role: '',
  reset_password: '',
})

function clearErrors(): void {
  errors.email = ''
  errors.full_name = ''
  errors.phone = ''
  errors.password = ''
  errors.role = ''
  errors.reset_password = ''
}

function resetUserForm(): void {
  userForm.email = ''
  userForm.full_name = ''
  userForm.phone = ''
  userForm.password = ''
  userForm.role = ''
  userForm.vermieter_id = null
  userForm.is_active = 'true'
  resetPasswordValue.value = ''
}

function closeUserModal(): void {
  showUserModal.value = false
  editingUser.value = null
  resetUserForm()
  clearErrors()
}

function editUser(user: AdminUser): void {
  editingUser.value = user
  userForm.email = user.email
  userForm.full_name = user.full_name
  userForm.phone = user.phone || ''
  userForm.role = user.role === 'admin' ? 'vermieter' : user.role
  userForm.vermieter_id = user.vermieter_id
  userForm.is_active = user.is_active ? 'true' : 'false'
  showUserModal.value = true
}

function validateUser(): boolean {
  clearErrors()
  let valid = true
  if (!editingUser.value && !userForm.email) {
    errors.email = 'E-Mail ist erforderlich.'
    valid = false
  }
  if (!userForm.full_name) {
    errors.full_name = 'Name ist erforderlich.'
    valid = false
  }
  if (!editingUser.value && userForm.password.length < 12) {
    errors.password = 'Passwort muss mindestens 12 Zeichen haben.'
    valid = false
  }
  if (!userForm.role) {
    errors.role = 'Rolle ist erforderlich.'
    valid = false
  }
  if (userForm.role === 'mieter' && !userForm.vermieter_id) {
    errors.role = 'Mieter benötigen einen Vermieter.'
    valid = false
  }
  return valid
}

async function saveUser(): Promise<void> {
  if (!validateUser()) return

  if (editingUser.value) {
    const payload: AdminUserUpdatePayload = {
      full_name: userForm.full_name,
      phone: userForm.phone || null,
      role: userForm.role as 'vermieter' | 'mieter',
      is_active: userForm.is_active === 'true',
      vermieter_id: userForm.role === 'mieter' ? userForm.vermieter_id : null,
    }
    const updated = await adminStore.updateUser(editingUser.value.id, payload)
    if (updated) {
      showToast('Nutzer aktualisiert.', 'success')
      closeUserModal()
      await reloadUsers()
    } else {
      showToast(adminStore.error?.message || 'Fehler beim Aktualisieren.', 'error')
    }
  } else {
    const payload: AdminUserCreatePayload = {
      email: userForm.email,
      password: userForm.password,
      full_name: userForm.full_name,
      role: userForm.role as 'vermieter' | 'mieter',
      vermieter_id: userForm.role === 'mieter' ? userForm.vermieter_id : null,
    }
    const created = await adminStore.createUser(payload)
    if (created) {
      showToast('Nutzer angelegt.', 'success')
      closeUserModal()
      await reloadUsers()
    } else {
      showToast(adminStore.error?.message || 'Fehler beim Anlegen.', 'error')
    }
  }
}

async function doResetPassword(): Promise<void> {
  errors.reset_password = ''
  if (!editingUser.value) return
  if (resetPasswordValue.value.length < 12) {
    errors.reset_password = 'Passwort muss mindestens 12 Zeichen haben.'
    return
  }
  const ok = await adminStore.resetPassword(editingUser.value.id, resetPasswordValue.value)
  if (ok) {
    showToast('Passwort zurückgesetzt.', 'success')
    resetPasswordValue.value = ''
  } else {
    showToast(adminStore.error?.message || 'Fehler beim Zurücksetzen.', 'error')
  }
}

async function doDeleteUser(): Promise<void> {
  if (!editingUser.value) return
  if (!confirm(`Nutzer "${editingUser.value.full_name}" wirklich löschen?`)) return
  const ok = await adminStore.deleteUser(editingUser.value.id)
  if (ok) {
    showToast('Nutzer gelöscht.', 'success')
    closeUserModal()
    await reloadUsers()
  } else {
    showToast(adminStore.error?.message || 'Fehler beim Löschen.', 'error')
  }
}

async function reloadUsers(): Promise<void> {
  await adminStore.fetchUsers({
    role: roleFilter.value || undefined,
    search: search.value || undefined,
    active_only: false,
    skip: skip.value,
    limit,
  })
}

function changePage(delta: number): void {
  skip.value = Math.max(0, skip.value + delta * limit)
  reloadUsers()
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null
function debouncedSearch(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    skip.value = 0
    reloadUsers()
  }, 300)
}

function formatDate(iso: string | null): string {
  if (!iso) return '–'
  return new Date(iso).toLocaleDateString('de-DE')
}

watch(activeTab, async (tab) => {
  if (tab === 'users') {
    await reloadUsers()
  }
})

onMounted(async () => {
  await adminStore.fetchStats()
  await adminStore.fetchUsers({ limit, skip: 0 })
})
</script>
