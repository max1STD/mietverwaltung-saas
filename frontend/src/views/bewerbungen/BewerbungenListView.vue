<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Mieter-Bewerbungen</h1>
          <p class="text-gray-500 mt-1">Alle eingehenden Bewerbungen auf einen Blick.</p>
        </div>
        <AppButton
          class="w-full sm:w-auto"
          @click="$router.push('/bewerbungen/neu')"
        >
          + Bewerbung erfassen
        </AppButton>
      </div>

      <AppCard padding="md" shadow="md">
        <div class="mb-4">
          <AppInput
            id="bewerbungen-search"
            v-model="searchQuery"
            placeholder="Nach Name oder E-Mail suchen …"
            type="search"
          />
        </div>

        <div v-if="bewerbungenStore.loading" class="py-12 text-center text-gray-500">
          Bewerbungen werden geladen …
        </div>

        <AppEmptyState
          v-else-if="filteredBewerbungen.length === 0"
          icon="📝"
          title="Keine Bewerbungen gefunden"
          :description="
            searchQuery
              ? 'Keine Bewerbungen passen zu deiner Suche.'
              : 'Erfasse deine erste Bewerbung.'
          "
          :action-label="searchQuery ? 'Suche zurücksetzen' : 'Bewerbung erfassen'"
          @action="searchQuery ? (searchQuery = '') : $router.push('/bewerbungen/neu')"
        />

        <AppTable v-else :items="filteredBewerbungen" :columns="columns">
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/bewerbungen/${item.id}`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.first_name }} {{ item.last_name }}
              </RouterLink>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.einheit?.objekt_name || '–' }} — {{ item.einheit?.name || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatDate(item.applied_at) }}</td>
            <td class="py-3 px-4">
              <StatusBadge :status="item.status" />
            </td>
          </template>
        </AppTable>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBewerbungenStore, type Bewerbung, type BewerbungStatus } from '@/stores/bewerbungen'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const bewerbungenStore = useBewerbungenStore()
const searchQuery = ref('')

const columns = [
  { key: 'name', label: 'Bewerber' },
  { key: 'einheit', label: 'Einheit' },
  { key: 'applied_at', label: 'Eingegangen' },
  { key: 'status', label: 'Status' },
]

const statusOrder: Record<BewerbungStatus, number> = {
  neu: 0,
  in_pruefung: 1,
  angenommen: 2,
  abgelehnt: 3,
}

const filteredBewerbungen = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  let result = bewerbungenStore.bewerbungen
  if (query) {
    result = result.filter(
      (b: Bewerbung) =>
        `${b.first_name} ${b.last_name}`.toLowerCase().includes(query) ||
        b.email.toLowerCase().includes(query) ||
        (b.einheit?.objekt_name || '').toLowerCase().includes(query) ||
        (b.einheit?.name || '').toLowerCase().includes(query),
    )
  }
  return [...result].sort((a, b) => statusOrder[a.status] - statusOrder[b.status])
})

function formatDate(value?: string): string {
  if (!value) return '–'
  return new Date(value).toLocaleDateString('de-DE')
}

onMounted(() => {
  bewerbungenStore.fetchBewerbungen()
})
</script>
