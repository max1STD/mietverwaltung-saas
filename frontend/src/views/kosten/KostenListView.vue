<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Kosten</h1>
          <p class="text-gray-500 mt-1">Erfasse und verwalte alle Betriebskosten.</p>
        </div>
        <AppButton @click="$router.push('/kosten/neu')">
          + Kosten erfassen
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
            <label for="filter-objekt" class="block text-sm font-medium text-gray-700 mb-1">Objekt / Einheit</label>
            <select
              id="filter-objekt"
              v-model="filterObjekt"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="">Alle Objekte</option>
              <optgroup v-for="objekt in objekteStore.objekte" :key="objekt.id" :label="objekt.name">
                <option :value="objekt.id">{{ objekt.name }} (Gesamt)</option>
                <option
                  v-for="einheit in einheitenFuerObjekt(objekt.id)"
                  :key="einheit.id"
                  :value="`einheit:${einheit.id}`"
                >
                  {{ einheit.name }}
                </option>
              </optgroup>
            </select>
          </div>
        </div>

        <!-- Ladezustand -->
        <div v-if="kostenStore.loading || objekteStore.loading" class="py-12 text-center text-gray-500">
          Kosten werden geladen …
        </div>

        <!-- Leerer Zustand -->
        <AppEmptyState
          v-else-if="filteredKosten.length === 0"
          icon="💶"
          title="Keine Kosten gefunden"
          :description="
            filterJahr || filterObjekt
              ? 'Passe die Filter an, um Ergebnisse zu sehen.'
              : 'Erfasse deine erste Betriebskosten-Position.'
          "
          :action-label="filterJahr || filterObjekt ? 'Filter zurücksetzen' : 'Kosten erfassen'"
          @action="resetFilters() || $router.push('/kosten/neu')"
        />

        <!-- Tabelle -->
        <AppTable
          v-else
          :items="filteredKosten"
          :columns="columns"
          initial-sort="datum"
        >
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/kosten/${item.id}/bearbeiten`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.name }}
              </RouterLink>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatDate(item.datum) }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.kategorie?.name || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatObjectEinheit(item) }}</td>
            <td class="py-3 px-4 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(item.betrag) }}</td>
            <td class="py-3 px-4">
              <AppBadge :variant="item.umlagefaehig ? 'green' : 'gray'">
                {{ item.umlagefaehig ? 'Umlagefähig' : 'Nicht umlagefähig' }}
              </AppBadge>
            </td>
          </template>

          <template #actions="{ item }">
            <div class="flex items-center justify-end gap-2">
              <AppButton
                variant="ghost"
                size="sm"
                @click="$router.push(`/kosten/${item.id}/bearbeiten`)"
              >
                Bearbeiten
              </AppButton>
              <AppButton
                variant="danger"
                size="sm"
                :loading="kostenStore.saving"
                @click="deleteKosten(item.id)"
              >
                Löschen
              </AppButton>
            </div>
          </template>
        </AppTable>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useKostenStore, type Kosten } from '@/stores/kosten'
import { useObjekteStore, type Einheit } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const kostenStore = useKostenStore()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const filterJahr = ref('')
const filterObjekt = ref('')

const jahre = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 6 }, (_, i) => currentYear - i)
})

const columns = [
  { key: 'name', label: 'Bezeichnung' },
  { key: 'datum', label: 'Datum' },
  { key: 'kategorie', label: 'Kategorie' },
  { key: 'objekt', label: 'Objekt / Einheit' },
  { key: 'betrag', label: 'Betrag' },
  { key: 'umlagefaehig', label: 'Umlage' },
]

const filteredKosten = computed(() => {
  let result = [...kostenStore.kosten]

  if (filterJahr.value) {
    const jahr = Number(filterJahr.value)
    result = result.filter((k) => new Date(k.datum).getFullYear() === jahr)
  }

  if (filterObjekt.value) {
    const value = filterObjekt.value
    if (value.startsWith('einheit:')) {
      const einheitId = value.replace('einheit:', '')
      result = result.filter((k) => k.einheit_id === einheitId)
    } else {
      result = result.filter((k) => k.objekt_id === value)
    }
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

function formatObjectEinheit(kosten: Kosten): string {
  const einheitName = kosten.einheit?.name ?? kosten.einheit?.bezeichnung
  if (einheitName) {
    return `${kosten.objekt?.name || kosten.objekt?.bezeichnung || ''} / ${einheitName}`.replace(/^\s*\/\s*/, '')
  }
  return kosten.objekt?.name ?? kosten.objekt?.bezeichnung ?? '–'
}

function resetFilters(): boolean {
  filterJahr.value = ''
  filterObjekt.value = ''
  return true
}

async function deleteKosten(id: string): Promise<void> {
  const confirmed = window.confirm('Möchtest du diese Kosten wirklich löschen?')
  if (!confirmed) return

  const success = await kostenStore.deleteKosten(id)
  if (success) {
    showToast('Kosten gelöscht.', 'success')
  } else {
    showToast(kostenStore.error?.message || 'Fehler beim Löschen.', 'error')
  }
}

onMounted(async () => {
  await Promise.all([
    kostenStore.fetchKosten(),
    objekteStore.fetchObjekte(),
  ])
  // Einheiten aller Objekte laden für Filter
  for (const objekt of objekteStore.objekte) {
    await objekteStore.fetchEinheiten(objekt.id)
  }
})
</script>
