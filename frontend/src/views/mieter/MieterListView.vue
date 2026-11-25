<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Mieter</h1>
          <p class="text-gray-500 mt-1">Verwalte alle Mieter-Stammdaten.</p>
        </div>
        <AppButton
          class="w-full sm:w-auto"
          @click="$router.push('/mieter/neu')"
        >
          + Mieter hinzufügen
        </AppButton>
      </div>

      <AppCard padding="md" shadow="md">
        <div class="mb-4">
          <AppInput
            id="mieter-search"
            v-model="searchQuery"
            placeholder="Nach Name oder E-Mail suchen …"
            type="search"
          />
        </div>

        <div v-if="mieterStore.loading" class="py-12 text-center text-gray-500">
          Mieter werden geladen …
        </div>

        <AppEmptyState
          v-else-if="filteredMieter.length === 0"
          icon="👤"
          title="Keine Mieter gefunden"
          :description="
            searchQuery
              ? 'Keine Mieter passen zu deiner Suche.'
              : 'Lege deinen ersten Mieter an.'
          "
          :action-label="searchQuery ? 'Suche zurücksetzen' : 'Mieter anlegen'"
          @action="searchQuery ? (searchQuery = '') : $router.push('/mieter/neu')"
        />

        <AppTable v-else :items="filteredMieter" :columns="columns">
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/mieter/${item.public_id || item.id}`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.name }}
              </RouterLink>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.email || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.telefon || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatDate(item.geburtsdatum) }}</td>
          </template>

          <template #actions="{ item }">
            <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-2">
              <AppButton
                class="w-full sm:w-auto"
                variant="ghost"
                size="sm"
                @click="$router.push(`/mieter/${item.public_id || item.id}/bearbeiten`)"
              >
                Bearbeiten
              </AppButton>
              <AppButton
                class="w-full sm:w-auto"
                variant="danger"
                size="sm"
                :loading="mieterStore.saving"
                @click="deleteMieter(item.public_id || item.id)"
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
import { useMieterStore, type Mieter } from '@/stores/mieter'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const mieterStore = useMieterStore()
const { showToast } = useToast()

const searchQuery = ref('')

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'E-Mail' },
  { key: 'telefon', label: 'Telefon' },
  { key: 'geburtsdatum', label: 'Geburtsdatum' },
]

const filteredMieter = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return mieterStore.mieter

  return mieterStore.mieter.filter(
    (mieter) =>
      mieter.name.toLowerCase().includes(query) ||
      (mieter.email && mieter.email.toLowerCase().includes(query)) ||
      (mieter.telefon && mieter.telefon.toLowerCase().includes(query)),
  )
})

function formatDate(value?: string): string {
  if (!value) return '–'
  return new Date(value).toLocaleDateString('de-DE')
}

async function deleteMieter(id: string): Promise<void> {
  const confirmed = window.confirm('Möchtest du diesen Mieter wirklich löschen?')
  if (!confirmed) return

  const success = await mieterStore.deleteMieter(id)
  if (success) {
    showToast('Mieter erfolgreich gelöscht.', 'success')
  } else {
    showToast(mieterStore.error?.message || 'Fehler beim Löschen.', 'error')
  }
}

onMounted(() => {
  mieterStore.fetchMieter()
})
</script>
