<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Seitenkopf -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Dashboard</h1>
          <p class="text-gray-500 mt-1">Alles auf einen Blick — KPIs, Objekte, Finanzen und Insights.</p>
        </div>

        <!-- Schnellaktionen -->
        <div class="flex flex-wrap gap-2">
          <AppButton size="sm" @click="$router.push('/objekte/neu')">+ Objekt</AppButton>
          <AppButton size="sm" variant="secondary" @click="$router.push('/mieter/neu')">+ Mieter</AppButton>
          <AppButton size="sm" variant="secondary" @click="$router.push('/tickets/neu')">+ Ticket</AppButton>
          <AppButton size="sm" variant="secondary" @click="$router.push('/kosten/neu')">+ Kosten</AppButton>
        </div>
      </div>

      <!-- Ladezustand -->
      <div v-if="dashboardStore.loading && !dashboardStore.hasData" class="text-center py-12 text-gray-500">
        Dashboard wird geladen …
      </div>

      <!-- Inhalt -->
      <div v-else class="space-y-8">
        <!-- Setup-Checkliste: oberhalb des Dashboards bis 100% -->
        <SetupChecklist />

        <!-- Hero KPIs -->
        <KPIGrid>
          <KPICard
            label="Objekte"
            :value="summary?.objekte_count ?? 0"
            icon="🏠"
            to="/objekte"
          />
          <KPICard
            label="Wohneinheiten"
            :value="summary?.einheiten_count ?? 0"
            icon="🏢"
            to="/objekte"
          />
          <KPICard
            label="Mieter"
            :value="summary?.mieter_count ?? 0"
            icon="👤"
            to="/mieter"
          />
          <KPICard
            label="Offene Tickets"
            :value="summary?.offene_tickets_count ?? 0"
            variant="danger"
            icon="🎫"
            to="/tickets"
          />
        </KPIGrid>

        <!-- Zweispaltiges Layout: Objekte + Subscription -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-[#0D3B70]">Objekt-Übersicht</h2>
              <RouterLink to="/objekte" class="text-sm text-[#0D3B70] hover:underline">Alle Objekte</RouterLink>
            </div>
            <ObjectOverview :summaries="dashboardStore.objectSummaries" @upload="handlePhotoUpload" />
          </div>

          <div class="space-y-6">
            <SubscriptionWidget
              v-if="summary?.subscription"
              :subscription="summary.subscription"
            />

            <!-- Monatliche Kennzahlen -->
            <AppCard padding="md" shadow="md">
              <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Dieser Monat</h2>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Umsatz (Miete)</span>
                  <span class="text-sm font-medium text-gray-900">{{ formatCurrency(summary?.umsatz_diesen_monat ?? 0) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">Kosten</span>
                  <span class="text-sm font-medium text-red-600">{{ formatCurrency(summary?.kosten_diesen_monat ?? 0) }}</span>
                </div>
                <div class="h-px bg-gray-100" />
                <div class="flex justify-between">
                  <span class="text-sm font-medium text-gray-700">Netto</span>
                  <span
                    class="text-sm font-bold"
                    :class="((summary?.umsatz_diesen_monat ?? 0) - (summary?.kosten_diesen_monat ?? 0)) >= 0 ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ formatCurrency((summary?.umsatz_diesen_monat ?? 0) - (summary?.kosten_diesen_monat ?? 0)) }}
                  </span>
                </div>
              </div>
            </AppCard>
          </div>
        </div>

        <!-- Finanzen + Insights -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <FinanceWidget :financials="dashboardStore.financials" />
          <OpenTicketsWidget :insights="dashboardStore.insights" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useObjekteStore } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import KPICard from '@/components/dashboard/KPICard.vue'
import KPIGrid from '@/components/dashboard/KPIGrid.vue'
import ObjectOverview from '@/components/dashboard/ObjectOverview.vue'
import FinanceWidget from '@/components/dashboard/FinanceWidget.vue'
import OpenTicketsWidget from '@/components/dashboard/OpenTicketsWidget.vue'
import SubscriptionWidget from '@/components/dashboard/SubscriptionWidget.vue'
import SetupChecklist from '@/components/onboarding/SetupChecklist.vue'

const dashboardStore = useDashboardStore()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const summary = computed(() => dashboardStore.summary)

async function loadAll(): Promise<void> {
  await Promise.all([
    dashboardStore.loadDashboard(),
    objekteStore.fetchObjekte(),
  ])

  // Objekt-Kennzahlen parallel laden
  if (objekteStore.objekte.length > 0) {
    await Promise.all(
      objekteStore.objekte.map((o) => dashboardStore.fetchObjectSummary(Number(o.id))),
    )
  }
}

function formatCurrency(value?: number): string {
  if (value === undefined || value === null) return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function handlePhotoUpload(objektId: string | number, file: File): void {
  // Phase 9: Upload-Endpoint folgt in Phase 10/11
  showToast(`Foto-Upload für Objekt ${objektId} (${file.name}) — in Kürze verfügbar.`, 'info')
}

onMounted(() => {
  loadAll()
})
</script>
