<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Nebenkostenabrechnungen</h1>
          <p class="text-gray-500 mt-1">Erstelle und verwalte Abrechnungen pro Einheit und Jahr.</p>
        </div>
        <AppButton @click="showCreateModal = true">
          + Abrechnung anlegen
        </AppButton>
      </div>

      <AppCard padding="md" shadow="md">
        <!-- Filter -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div>
            <label for="filter-jahr" class="block text-sm font-medium text-gray-700 mb-1">Jahr</label>
            <select
              id="filter-jahr"
              v-model="filterJahr"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="">Alle Jahre</option>
              <option v-for="j in jahre" :key="j" :value="j">{{ j }}</option>
            </select>
          </div>
          <div class="sm:col-span-2">
            <label for="filter-einheit" class="block text-sm font-medium text-gray-700 mb-1">Einheit</label>
            <select
              id="filter-einheit"
              v-model="filterEinheit"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="">Alle Einheiten</option>
              <optgroup v-for="objekt in objekteStore.objekte" :key="objekt.id" :label="objekt.bezeichnung">
                <option
                  v-for="einheit in einheitenFuerObjekt(objekt.id)"
                  :key="einheit.id"
                  :value="einheit.id"
                >
                  {{ einheit.bezeichnung }}
                </option>
              </optgroup>
            </select>
          </div>
        </div>

        <!-- Ladezustand -->
        <div v-if="abrechnungenStore.loading || objekteStore.loading" class="py-12 text-center text-gray-500">
          Abrechnungen werden geladen …
        </div>

        <!-- Leerer Zustand -->
        <AppEmptyState
          v-else-if="filteredAbrechnungen.length === 0"
          icon="📊"
          title="Keine Abrechnungen gefunden"
          :description="
            filterJahr || filterEinheit
              ? 'Passe die Filter an, um Ergebnisse zu sehen.'
              : 'Lege deine erste Nebenkostenabrechnung an.'
          "
          :action-label="filterJahr || filterEinheit ? 'Filter zurücksetzen' : 'Abrechnung anlegen'"
          @action="resetFilters() || (showCreateModal = true)"
        />

        <!-- Tabelle -->
        <AppTable
          v-else
          :items="filteredAbrechnungen"
          :columns="columns"
          initial-sort="jahr"
        >
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/abrechnungen/${item.id}`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.einheit?.bezeichnung || 'Einheit' }} / {{ item.jahr }}
              </RouterLink>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.objekt?.bezeichnung || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatDate(item.zeitraum_von) }} – {{ formatDate(item.zeitraum_bis) }}</td>
            <td class="py-3 px-4 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(item.umlageanteil) }}</td>
            <td class="py-3 px-4">
              <AppBadge :variant="badgeForStatus(item.status)">
                {{ statusLabel(item.status) }}
              </AppBadge>
            </td>
          </template>

          <template #actions="{ item }">
            <div class="flex items-center justify-end gap-2">
              <AppButton
                variant="ghost"
                size="sm"
                @click="$router.push(`/abrechnungen/${item.id}`)"
              >
                Details
              </AppButton>
              <AppButton
                variant="danger"
                size="sm"
                :loading="abrechnungenStore.saving"
                @click="deleteAbrechnung(item.id)"
              >
                Löschen
              </AppButton>
            </div>
          </template>
        </AppTable>
      </AppCard>
    </div>

    <!-- Modal: Abrechnung anlegen -->
    <AppModal v-model="showCreateModal" title="Neue Abrechnung">
      <form class="space-y-4" @submit.prevent="createAbrechnung">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label for="new-jahr" class="block text-sm font-medium text-gray-700 mb-1">Jahr</label>
            <select
              id="new-jahr"
              v-model="createForm.jahr"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option v-for="j in jahre" :key="j" :value="j">{{ j }}</option>
            </select>
          </div>
          <div>
            <label for="new-einheit" class="block text-sm font-medium text-gray-700 mb-1">Einheit</label>
            <select
              id="new-einheit"
              v-model="createForm.einheit_id"
              required
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="">Bitte wählen</option>
              <optgroup v-for="objekt in objekteStore.objekte" :key="objekt.id" :label="objekt.bezeichnung">
                <option
                  v-for="einheit in einheitenFuerObjekt(objekt.id)"
                  :key="einheit.id"
                  :value="einheit.id"
                >
                  {{ einheit.bezeichnung }}
                </option>
              </optgroup>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <AppInput
            id="new-von"
            v-model="createForm.zeitraum_von"
            label="Zeitraum von"
            type="date"
            required
          />
          <AppInput
            id="new-bis"
            v-model="createForm.zeitraum_bis"
            label="Zeitraum bis"
            type="date"
            required
          />
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <AppButton type="button" variant="ghost" @click="showCreateModal = false">
            Abbrechen
          </AppButton>
          <AppButton type="submit" :loading="abrechnungenStore.saving">
            Abrechnung anlegen
          </AppButton>
        </div>
      </form>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAbrechnungenStore, type Abrechnung, type AbrechnungStatus } from '@/stores/abrechnungen'
import { useObjekteStore, type Einheit } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'

const abrechnungenStore = useAbrechnungenStore()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const filterJahr = ref('')
const filterEinheit = ref('')
const showCreateModal = ref(false)

const currentYear = new Date().getFullYear()

const jahre = computed(() => {
  return Array.from({ length: 6 }, (_, i) => currentYear - i)
})

const createForm = reactive({
  jahr: currentYear - 1,
  einheit_id: '',
  zeitraum_von: `${currentYear - 1}-01-01`,
  zeitraum_bis: `${currentYear - 1}-12-31`,
})

const columns = [
  { key: 'einheit', label: 'Einheit / Jahr' },
  { key: 'objekt', label: 'Objekt' },
  { key: 'zeitraum', label: 'Zeitraum' },
  { key: 'umlageanteil', label: 'Umlageanteil' },
  { key: 'status', label: 'Status' },
]

const filteredAbrechnungen = computed(() => {
  let result = [...abrechnungenStore.abrechnungen]

  if (filterJahr.value) {
    result = result.filter((a) => a.jahr === Number(filterJahr.value))
  }

  if (filterEinheit.value) {
    result = result.filter((a) => a.einheit_id === filterEinheit.value)
  }

  return result
})

function einheitenFuerObjekt(objektId: string): Einheit[] {
  return objekteStore.einheiten.filter((e) => e.objekt_id === objektId)
}

function formatDate(value?: string): string {
  if (!value) return '–'
  return new Date(value).toLocaleDateString('de-DE')
}

function formatCurrency(value?: number): string {
  if (value == null) return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function statusLabel(status?: string): string {
  switch (status) {
    case 'entwurf':
      return 'Entwurf'
    case 'berechnet':
      return 'Berechnet'
    case 'finalisiert':
      return 'Finalisiert'
    case 'versendet':
      return 'Versendet'
    default:
      return status || '–'
  }
}

function badgeForStatus(status?: string): 'green' | 'yellow' | 'blue' | 'gray' {
  switch (status) {
    case 'finalisiert':
    case 'versendet':
      return 'green'
    case 'berechnet':
      return 'blue'
    case 'entwurf':
      return 'yellow'
    default:
      return 'gray'
  }
}

function resetFilters(): boolean {
  filterJahr.value = ''
  filterEinheit.value = ''
  return true
}

async function createAbrechnung(): Promise<void> {
  if (!createForm.einheit_id) {
    showToast('Bitte wähle eine Einheit aus.', 'warning')
    return
  }

  const created = await abrechnungenStore.createAbrechnung({
    jahr: Number(createForm.jahr),
    einheit_id: createForm.einheit_id,
    zeitraum_von: createForm.zeitraum_von,
    zeitraum_bis: createForm.zeitraum_bis,
  })

  if (created) {
    showToast('Abrechnung angelegt.', 'success')
    showCreateModal.value = false
    resetCreateForm()
  } else {
    showToast(abrechnungenStore.error?.message || 'Fehler beim Anlegen.', 'error')
  }
}

function resetCreateForm(): void {
  createForm.jahr = currentYear - 1
  createForm.einheit_id = ''
  createForm.zeitraum_von = `${currentYear - 1}-01-01`
  createForm.zeitraum_bis = `${currentYear - 1}-12-31`
}

async function deleteAbrechnung(id: string): Promise<void> {
  const confirmed = window.confirm('Möchtest du diese Abrechnung wirklich löschen?')
  if (!confirmed) return

  const success = await abrechnungenStore.deleteAbrechnung(id)
  if (success) {
    showToast('Abrechnung gelöscht.', 'success')
  } else {
    showToast(abrechnungenStore.error?.message || 'Fehler beim Löschen.', 'error')
  }
}

onMounted(async () => {
  await Promise.all([
    abrechnungenStore.fetchAbrechnungen(),
    objekteStore.fetchObjekte(),
  ])
  for (const objekt of objekteStore.objekte) {
    await objekteStore.fetchEinheiten(objekt.id)
  }
})
</script>
