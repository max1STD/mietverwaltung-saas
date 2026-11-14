<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70] mb-6">Mein Abonnement</h1>

      <AppCard padding="lg" shadow="md">
        <div v-if="billingStore.loading" class="text-center py-8 text-gray-500">
          Abo-Daten werden geladen …
        </div>

        <div v-else-if="billingStore.subscription" class="space-y-6">
          <!-- Status-Badge -->
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-500">Aktueller Plan</p>
              <p class="text-lg font-semibold text-[#0D3B70]">Pro-WE · {{ billingStore.subscription.wohnungen_count }} Wohneinheit{{ billingStore.subscription.wohnungen_count > 1 ? 'en' : '' }}</p>
            </div>
            <span
              class="px-3 py-1 rounded-full text-sm font-medium"
              :class="statusClasses"
            >
              {{ statusLabel }}
            </span>
          </div>

          <!-- Preis -->
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="flex items-baseline justify-between">
              <span class="text-gray-600">Preis pro WE / Monat</span>
              <span class="text-lg font-semibold text-gray-900">{{ formatCurrency(billingStore.subscription.price_per_we) }}</span>
            </div>
            <div class="flex items-baseline justify-between mt-2">
              <span class="text-gray-600">Gesamtbetrag / Monat</span>
              <span class="text-xl font-bold text-[#0D3B70]">{{ formatCurrency(billingStore.subscription.total_monthly) }}</span>
            </div>
            <div class="flex items-baseline justify-between mt-2">
              <span class="text-gray-600">Gesamtbetrag / Jahr</span>
              <span class="text-xl font-bold text-[#0D3B70]">{{ formatCurrency(billingStore.subscription.total_yearly) }}</span>
            </div>
            <p class="text-xs text-gray-500 mt-2">Jährliche Zahlung = 2 Monate geschenkt.</p>
          </div>

          <!-- WE-Anzahl & Intervall anpassen -->
          <div class="space-y-4">
            <label class="block text-sm font-medium text-gray-700">Wohneinheiten: {{ weCount }}</label>
            <input
              v-model.number="weCount"
              type="range"
              min="1"
              max="49"
              class="w-full accent-[#0D3B70]"
            />
            <div class="flex gap-2">
              <button
                type="button"
                class="flex-1 py-2 rounded-lg text-sm font-medium border transition-colors"
                :class="interval === 'monthly' ? 'bg-[#0D3B70] text-white border-[#0D3B70]' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'"
                @click="interval = 'monthly'"
              >
                Monatlich
              </button>
              <button
                type="button"
                class="flex-1 py-2 rounded-lg text-sm font-medium border transition-colors"
                :class="interval === 'yearly' ? 'bg-[#0D3B70] text-white border-[#0D3B70]' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'"
                @click="interval = 'yearly'"
              >
                Jährlich (2 Monate geschenkt)
              </button>
            </div>
            <AppButton
              variant="primary"
              full-width
              :loading="billingStore.loading"
              @click="applyChanges"
            >
              Änderung übernehmen
            </AppButton>
          </div>

          <!-- Aktionen -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4 border-t border-gray-100">
            <AppButton variant="secondary" @click="openPortal">
              Zahlungsmethode verwalten
            </AppButton>
            <AppButton variant="danger" @click="confirmCancel">
              Abo kündigen
            </AppButton>
          </div>

          <!-- Trial-Hinweis -->
          <div v-if="billingStore.isTrial" class="text-sm text-gray-600 bg-blue-50 rounded-lg p-3">
            Du befindest dich in der 14-tägigen Testphase. Nach Ablauf beginnt die automatische Abbuchung.
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-500">
          Keine Abo-Daten verfügbar.
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SubscriptionView — Verwaltung des eigenen Abonnements.
 */
import { ref, computed, onMounted } from 'vue'
import { useBillingStore } from '@/stores/billing'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'

const billingStore = useBillingStore()

const weCount = ref(1)
const interval = ref<'monthly' | 'yearly'>('yearly')

onMounted(async () => {
  await billingStore.fetchSubscription()
  if (billingStore.subscription) {
    weCount.value = billingStore.subscription.wohnungen_count
    interval.value = billingStore.subscription.billing_cycle
  }
})

const statusLabel = computed(() => {
  const status = billingStore.subscription?.status
  if (status === 'trial') return 'Testphase'
  if (status === 'active') return 'Aktiv'
  if (status === 'past_due') return 'Zahlung ausstehend'
  if (status === 'cancelled') return 'Gekündigt'
  return status
})

const statusClasses = computed(() => {
  const status = billingStore.subscription?.status
  if (status === 'trial') return 'bg-blue-100 text-blue-800'
  if (status === 'active') return 'bg-green-100 text-green-800'
  if (status === 'past_due') return 'bg-yellow-100 text-yellow-800'
  if (status === 'cancelled') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
})

function formatCurrency(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(num)
}

async function applyChanges(): Promise<void> {
  await billingStore.updateSubscription(weCount.value, interval.value)
}

async function openPortal(): Promise<void> {
  const portal = await billingStore.openCustomerPortal()
  if (portal?.url) {
    window.location.href = portal.url
  }
}

async function confirmCancel(): Promise<void> {
  const confirmed = window.confirm('Möchtest du dein Abonnement wirklich zum Periodenende kündigen?')
  if (confirmed) {
    await billingStore.cancelSubscription('User-Kündigung über Dashboard')
  }
}
</script>
