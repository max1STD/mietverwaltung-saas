<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Zähler</h1>
          <p class="text-gray-500 mt-1">
            {{ authStore.isVermieter ? 'Verwalte Zählerstände für Strom, Gas, Wasser und mehr.' : 'Deine Zähler und aktuellen Ablesungen auf einen Blick.' }}
          </p>
        </div>
        <AppButton v-if="authStore.isVermieter" @click="$router.push('/zaehler/neu')">
          + Zähler anlegen
        </AppButton>
      </div>

      <AppCard padding="md" shadow="md">
        <!-- Ladezustand -->
        <div v-if="zaehlerStore.loading" class="py-12 text-center text-gray-500">
          Zähler werden geladen …
        </div>

        <!-- Leerer Zustand -->
        <AppEmptyState
          v-else-if="zaehlerStore.zaehler.length === 0"
          icon="⚡"
          title="Keine Zähler gefunden"
          :description="
            authStore.isVermieter
              ? 'Lege deinen ersten Zähler für eine Wohneinheit an.'
              : 'Für deine aktuelle Wohneinheit sind noch keine Zähler hinterlegt.'
          "
          :action-label="authStore.isVermieter ? 'Zähler anlegen' : undefined"
          @action="authStore.isVermieter ? $router.push('/zaehler/neu') : undefined"
        />

        <!-- Tabelle -->
        <AppTable
          v-else
          :items="zaehlerStore.zaehler"
          :columns="columns"
          initial-sort="bezeichnung"
        >
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/zaehler/${item.id}`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.bezeichnung }}
              </RouterLink>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatTyp(item.typ) }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.zaehlernummer || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatEinheit(item.einheit) }}</td>
            <td class="py-3 px-4 text-sm font-medium text-gray-900 text-right">
              {{ item.ablesedatum ? formatDate(item.ablesedatum) : '–' }}
            </td>
            <td class="py-3 px-4 text-center">
              <AppBadge v-if="item.ist_hauptzaehler" variant="blue">Hauptzähler</AppBadge>
            </td>
          </template>

          <template #actions="{ item }">
            <div class="flex items-center justify-end gap-2">
              <AppButton
                variant="ghost"
                size="sm"
                @click="$router.push(`/zaehler/${item.id}`)"
              >
                Details
              </AppButton>
              <AppButton
                v-if="authStore.isVermieter"
                variant="ghost"
                size="sm"
                @click="$router.push(`/zaehler/${item.id}/bearbeiten`)"
              >
                Bearbeiten
              </AppButton>
              <AppButton
                v-if="authStore.isVermieter"
                variant="danger"
                size="sm"
                :loading="zaehlerStore.saving"
                @click="deleteZaehler(item.id)"
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
import { useRouter } from 'vue-router'
import { useZaehlerStore, type Zaehler } from '@/stores/zaehler'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const zaehlerStore = useZaehlerStore()
const authStore = useAuthStore()
const router = useRouter()
const { showToast } = useToast()

const columns = [
  { key: 'bezeichnung', label: 'Bezeichnung', sortable: true },
  { key: 'typ', label: 'Typ', sortable: true },
  { key: 'zaehlernummer', label: 'Zählernummer', sortable: false },
  { key: 'einheit', label: 'Einheit', sortable: false },
  { key: 'ablesedatum', label: 'Letzte Ablesung', sortable: true, align: 'right' },
  { key: 'ist_hauptzaehler', label: '', sortable: false },
]

function formatTyp(typ: string): string {
  const labels: Record<string, string> = {
    strom: 'Strom',
    gas: 'Gas',
    wasser: 'Wasser',
    waerme: 'Wärme',
    kaltwasser: 'Kaltwasser',
    sonstiges: 'Sonstiges',
  }
  return labels[typ] || typ
}

function formatEinheit(einheit: string): string {
  const labels: Record<string, string> = {
    kwh: 'kWh',
    kwh_m3: 'kWh / m³',
    m3: 'm³',
    sonstiges: 'Sonstiges',
  }
  return labels[einheit] || einheit
}

function formatDate(value?: string | null): string {
  if (!value) return '–'
  return new Intl.DateTimeFormat('de-DE').format(new Date(value))
}

async function deleteZaehler(id: string): Promise<void> {
  if (!confirm('Zähler inklusive aller Ablesungen wirklich löschen?')) return
  const ok = await zaehlerStore.deleteZaehler(id)
  if (ok) {
    showToast('Zähler gelöscht.', 'success')
  } else {
    showToast(zaehlerStore.error?.message || 'Löschen fehlgeschlagen.', 'error')
  }
}

onMounted(() => {
  zaehlerStore.fetchZaehler()
})
</script>
