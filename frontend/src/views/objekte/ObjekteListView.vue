<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Objekte</h1>
          <p class="text-gray-500 mt-1">Verwalte alle deine Immobilien an einem Ort.</p>
        </div>
        <AppButton @click="$router.push('/objekte/neu')">
          + Objekt hinzufügen
        </AppButton>
      </div>

      <AppCard padding="md" shadow="md">
        <!-- Suchleiste -->
        <div class="mb-4">
          <AppInput
            id="objekte-search"
            v-model="searchQuery"
            placeholder="Nach Bezeichnung oder Adresse suchen …"
            type="search"
          />
        </div>

        <!-- Ladezustand -->
        <div v-if="objekteStore.loading" class="py-12 text-center text-gray-500">
          Objekte werden geladen …
        </div>

        <!-- Leerer Zustand -->
        <AppEmptyState
          v-else-if="filteredObjekte.length === 0"
          icon="🏠"
          title="Keine Objekte gefunden"
          :description="
            searchQuery
              ? 'Keine Objekte passen zu deiner Suche.'
              : 'Lege dein erstes Objekt an, um loszulegen.'
          "
          :action-label="searchQuery ? 'Suche zurücksetzen' : 'Objekt anlegen'"
          @action="searchQuery ? (searchQuery = '') : $router.push('/objekte/neu')"
        />

        <!-- Tabelle -->
        <AppTable
          v-else
          :items="filteredObjekte"
          :columns="columns"
        >
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/objekte/${item.id}`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.bezeichnung }}
              </RouterLink>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatAddress(item) }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.typ || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.einheiten_count || 0 }}</td>
          </template>

          <template #actions="{ item }">
            <div class="flex items-center justify-end gap-2">
              <AppButton
                variant="ghost"
                size="sm"
                @click="$router.push(`/objekte/${item.id}/bearbeiten`)"
              >
                Bearbeiten
              </AppButton>
              <AppButton
                variant="danger"
                size="sm"
                :loading="objekteStore.saving"
                @click="deleteObjekt(item.id)"
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
import { useObjekteStore, type Objekt } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const objekteStore = useObjekteStore()
const { showToast } = useToast()

const searchQuery = ref('')

const columns = [
  { key: 'bezeichnung', label: 'Bezeichnung' },
  { key: 'adresse', label: 'Adresse' },
  { key: 'typ', label: 'Typ' },
  { key: 'einheiten_count', label: 'Einheiten' },
]

const filteredObjekte = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return objekteStore.objekte

  return objekteStore.objekte.filter(
    (objekt) =>
      objekt.bezeichnung.toLowerCase().includes(query) ||
      (objekt.adresse && objekt.adresse.toLowerCase().includes(query)) ||
      (objekt.ort && objekt.ort.toLowerCase().includes(query)),
  )
})

function formatAddress(objekt: Objekt): string {
  const parts = [objekt.adresse, [objekt.plz, objekt.ort].filter(Boolean).join(' ')]
  return parts.filter(Boolean).join(', ') || '–'
}

async function deleteObjekt(id: string): Promise<void> {
  const confirmed = window.confirm(
    'Möchtest du dieses Objekt wirklich löschen? Alle zugehörigen Einheiten werden mitgelöscht.',
  )
  if (!confirmed) return

  const success = await objekteStore.deleteObjekt(id)
  if (success) {
    showToast('Objekt erfolgreich gelöscht.', 'success')
  } else {
    showToast(objekteStore.error?.message || 'Fehler beim Löschen.', 'error')
  }
}

onMounted(() => {
  objekteStore.fetchObjekte()
})
</script>
