<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70] mb-6">Einstellungen</h1>

      <AppCard padding="none" shadow="md" class="overflow-hidden">
        <!-- Tabs -->
        <div class="flex border-b border-gray-200 bg-white">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            class="flex-1 py-3 text-sm font-medium transition-colors"
            :class="activeTab === tab.id
              ? 'text-[#0D3B70] border-b-2 border-[#0D3B70]'
              : 'text-gray-500 hover:text-gray-700'"
            @click="setTab(tab.id)"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="p-4 sm:p-6 bg-white">
          <!-- Konto -->
          <div v-if="activeTab === 'konto'" class="space-y-6">
            <AppEmptyState
              icon="👤"
              title="Konto"
              description="Hier werden bald Profildaten, Passwort und Benachrichtigungseinstellungen verwaltet."
            />
          </div>

          <!-- Abo -->
          <div v-else-if="activeTab === 'abo'" class="space-y-6">
            <div v-if="billingStore.loading" class="text-center py-8 text-gray-500">
              Abo-Daten werden geladen …
            </div>

            <div v-else-if="billingStore.subscription" class="space-y-6">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-500">Aktueller Plan</p>
                  <p class="text-lg font-semibold text-[#0D3B70]">
                    Pro-WE · {{ billingStore.subscription.wohnungen_count }} Wohneinheit{{ billingStore.subscription.wohnungen_count > 1 ? 'en' : '' }}
                  </p>
                </div>
                <AppBadge :variant="billingStore.isActive ? 'green' : billingStore.isTrial ? 'blue' : 'red'">
                  {{ statusLabel }}
                </AppBadge>
              </div>

              <div class="bg-gray-50 rounded-xl p-4 space-y-2">
                <div class="flex items-baseline justify-between">
                  <span class="text-gray-600">Preis pro WE / Monat</span>
                  <span class="font-semibold text-gray-900">{{ formatCurrency(billingStore.subscription.price_per_we) }}</span>
                </div>
                <div class="flex items-baseline justify-between">
                  <span class="text-gray-600">Gesamtbetrag / Monat</span>
                  <span class="text-lg font-bold text-[#0D3B70]">{{ formatCurrency(billingStore.subscription.total_monthly) }}</span>
                </div>
                <div class="flex items-baseline justify-between">
                  <span class="text-gray-600">Gesamtbetrag / Jahr</span>
                  <span class="text-lg font-bold text-[#0D3B70]">{{ formatCurrency(billingStore.subscription.total_yearly) }}</span>
                </div>
              </div>

              <div v-if="billingStore.subscription.trial_ends_at && billingStore.isTrial" class="bg-blue-50 rounded-lg p-3 text-sm text-blue-800">
                Dein Testzeitraum endet am <strong>{{ trialEndDate }}</strong>.
              </div>

              <div class="flex flex-col sm:flex-row gap-3 pt-2">
                <RouterLink
                  to="/abo"
                  class="flex-1 inline-flex items-center justify-center py-2.5 px-4 rounded-lg text-sm font-medium bg-[#0D3B70] text-white hover:bg-[#0a2d56] transition-colors"
                >
                  Abo verwalten
                </RouterLink>
                <RouterLink
                  to="/preise"
                  class="flex-1 inline-flex items-center justify-center py-2.5 px-4 rounded-lg text-sm font-medium border border-gray-200 text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Pläne vergleichen
                </RouterLink>
              </div>
            </div>

            <div v-else class="text-center py-8 text-gray-500">
              Keine Abo-Daten verfügbar.
            </div>
          </div>

          <!-- Sicherheit -->
          <div v-else-if="activeTab === 'sicherheit'" class="space-y-6">
            <AppEmptyState
              icon="🔒"
              title="Sicherheit"
              description="Hier werden bald Zwei-Faktor-Authentifizierung, API-Keys und Sitzungen verwaltet."
            />
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import { useBillingStore } from '@/stores/billing'

const route = useRoute()
const router = useRouter()
const billingStore = useBillingStore()

const tabs = [
  { id: 'konto', label: 'Konto' },
  { id: 'abo', label: 'Abo' },
  { id: 'sicherheit', label: 'Sicherheit' },
]

const activeTab = ref('konto')

function setTab(tabId: string) {
  activeTab.value = tabId
  router.replace({ query: { ...route.query, tab: tabId } })
}

watch(() => route.query.tab, (tab) => {
  if (tab && tabs.some(t => t.id === tab)) {
    activeTab.value = tab as string
  }
}, { immediate: true })

onMounted(() => {
  billingStore.fetchSubscription()
})

const statusLabel = computed(() => {
  if (billingStore.isActive) return 'Aktiv'
  if (billingStore.isTrial) return 'Testphase'
  if (billingStore.isCancelled) return 'Gekündigt'
  return 'Inaktiv'
})

const trialEndDate = computed(() => {
  if (!billingStore.subscription?.trial_ends_at) return ''
  return new Date(billingStore.subscription.trial_ends_at).toLocaleDateString('de-DE')
})

function formatCurrency(value: string | number | undefined): string {
  const num = typeof value === 'string' ? parseFloat(value) : (value ?? 0)
  return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(num)
}
</script>
