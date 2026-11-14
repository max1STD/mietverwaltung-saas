<template>
  <AppCard padding="md" shadow="md">
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-lg font-semibold text-[#0D3B70]">Dein Abo</h2>
        <p class="text-sm text-gray-500 mt-1">
          {{ subscription.is_trial ? '14-Tage-Trial' : 'Aktives Abo' }} ·
          {{ subscription.wohnungen_count }} Wohnung{{ subscription.wohnungen_count === 1 ? '' : 'en' }}
        </p>
      </div>
      <span
        class="px-2 py-1 rounded-full text-xs font-medium"
        :class="statusClasses"
      >
        {{ statusLabel }}
      </span>
    </div>

    <div class="mt-4">
      <div class="flex justify-between items-end">
        <div>
          <p class="text-xs text-gray-500">Preis pro WE/Monat</p>
          <p class="text-2xl font-bold text-[#0D3B70]">{{ formatCurrency(subscription.price_per_we) }}</p>
        </div>
        <div class="text-right">
          <p class="text-xs text-gray-500">Gesamt/Monat</p>
          <p class="text-xl font-bold text-[#0D3B70]">{{ formatCurrency(subscription.total_monthly) }}</p>
        </div>
      </div>
    </div>

    <div v-if="subscription.is_trial && subscription.trial_ends_at" class="mt-4 text-sm text-gray-600">
      Trial endet am {{ formatDate(subscription.trial_ends_at) }}.
    </div>

    <AppButton
      class="mt-5 w-full"
      variant="secondary"
      @click="$router.push('/einstellungen?tab=abo')"
    >
      Abo verwalten
    </AppButton>
  </AppCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import type { DashboardSubscription } from '@/stores/dashboard'

interface Props {
  subscription: DashboardSubscription
}

const props = defineProps<Props>()

const statusLabel = computed(() => {
  switch (props.subscription.status) {
    case 'trial': return 'Trial'
    case 'active': return 'Aktiv'
    case 'past_due': return 'Zahlung offen'
    case 'cancelled': return 'Gekündigt'
    default: return props.subscription.status
  }
})

const statusClasses = computed(() => {
  switch (props.subscription.status) {
    case 'trial': return 'bg-blue-100 text-blue-700'
    case 'active': return 'bg-green-100 text-green-700'
    case 'past_due': return 'bg-yellow-100 text-yellow-700'
    case 'cancelled': return 'bg-red-100 text-red-700'
    default: return 'bg-gray-100 text-gray-700'
  }
})

function formatCurrency(value?: number): string {
  if (value === undefined || value === null) return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function formatDate(value?: string): string {
  if (!value) return ''
  return new Date(value).toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}
</script>
