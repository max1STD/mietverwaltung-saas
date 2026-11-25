<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Mietverträge</h1>
          <p class="text-gray-500 mt-1">Übersicht aller aktiven und beendeten Mietverträge.</p>
        </div>
        <AppButton
          class="w-full sm:w-auto"
          @click="$router.push(\'/mietvertraege/neu\')"
          + Mietvertrag anlegen
        </AppButton>
      </div>

      <AppCard padding="md" shadow="md">
        <div v-if="mietvertraegeStore.loading" class="py-12 text-center text-gray-500">
          Mietverträge werden geladen …
        </div>

        <AppEmptyState
          v-else-if="mietvertraegeStore.mietvertraege.length === 0"
          icon="📄"
          title="Keine Mietverträge"
          description="Lege deinen ersten Mietvertrag an."
          action-label="Mietvertrag anlegen"
          @action="$router.push('/mietvertraege/neu')"
        />

        <AppTable v-else :items="mietvertraegeStore.mietvertraege" :columns="columns"
        >
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/mietvertraege/${item.id}`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.mieter?.name || '–' }}
              </RouterLink>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.einheit?.objekt_name || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.einheit?.name || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatDate(item.mietbeginn) }}</td>
            <td class="py-3 px-4 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(item.kaltmiete) }}</td>
            <td class="py-3 px-4">
              <AppBadge :variant="badgeForStatus(item.status)">{{ item.status || 'aktiv' }}
              </AppBadge>
            </td>
          </template>

          <template #actions="{ item }">
            <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-2">
              <AppButton
                class="w-full sm:w-auto"
                variant="ghost"
                size="sm"
                @click="$router.push(`/mietvertraege/${item.id}`)"
              >
                Details
              </AppButton>
              <AppButton
                class="w-full sm:w-auto"
                variant="ghost"
                size="sm"
                @click="$router.push(`/mietvertraege/${item.id}/bearbeiten`)"
              >
                Bearbeiten
              </AppButton>
              <AppButton
                class="w-full sm:w-auto"
                variant="danger"
                size="sm"
                :loading="mietvertraegeStore.saving"
                @click="deleteVertrag(item.id)"
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
import { onMounted } from 'vue'
import { useMietvertraegeStore, type Mietvertrag, type MietvertragStatus } from '@/stores/mietvertraege'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const mietvertraegeStore = useMietvertraegeStore()
const { showToast } = useToast()

const columns = [
  { key: 'mieter', label: 'Mieter' },
  { key: 'objekt', label: 'Objekt' },
  { key: 'einheit', label: 'Einheit' },
  { key: 'mietbeginn', label: 'Mietbeginn' },
  { key: 'kaltmiete', label: 'Kaltmiete' },
  { key: 'status', label: 'Status' },
]

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

function badgeForStatus(status?: string): 'green' | 'yellow' | 'red' | 'gray' {
  switch (status as MietvertragStatus | undefined) {
    case 'aktiv':
      return 'green'
    case 'gekuendigt':
      return 'yellow'
    case 'beendet':
      return 'red'
    default:
      return 'gray'
  }
}

async function deleteVertrag(id: string): Promise<void> {
  if (!confirm('Mietvertrag wirklich löschen?')) return
  const ok = await mietvertraegeStore.deleteMietvertrag(id)
  if (ok) {
    showToast('Mietvertrag gelöscht.', 'success')
  } else {
    showToast(mietvertraegeStore.error?.message || 'Löschen fehlgeschlagen.', 'error')
  }
}

onMounted(() => {
  mietvertraegeStore.fetchMietvertraege()
})
</script>
