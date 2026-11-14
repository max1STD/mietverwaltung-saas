<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-[#0D3B70] flex items-center justify-center text-white font-bold text-sm">MV</div>
          <span class="font-semibold text-[#0D3B70]">MietVerwaltung</span>
        </div>
        <nav class="flex gap-4">
          <RouterLink to="/login" class="text-sm text-gray-600 hover:text-[#0D3B70]">Anmelden</RouterLink>
          <RouterLink
            to="/register"
            class="text-sm bg-[#0D3B70] text-white px-4 py-2 rounded-lg hover:bg-[#2a5a9e]"
          >
            14 Tage kostenlos testen
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-16">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-[#0D3B70] mb-4">Einfach. Fair. Pro Wohneinheit.</h1>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          Keine festen Pakete — du zahlst nur für die Wohneinheiten, die du tatsächlich verwaltest.
          Jederzeit kündbar.
        </p>
      </div>

      <!-- Preis-Rechner -->
      <AppCard padding="lg" shadow="lg" class="mb-12">
        <div class="space-y-8">
          <div>
            <label class="block text-center text-sm font-medium text-gray-700 mb-4">
              Wähle deine Wohneinheiten: <span class="text-[#0D3B70] font-bold text-lg">{{ weCount }}</span>
            </label>
            <input
              v-model.number="weCount"
              type="range"
              min="1"
              max="49"
              class="w-full accent-[#0D3B70]"
            />
            <div class="flex justify-between text-xs text-gray-500 mt-2">
              <span>1 WE</span>
              <span>49 WE (max. Selbstbuchung)</span>
            </div>
          </div>

          <div class="flex justify-center gap-2">
            <button
              type="button"
              class="px-5 py-2 rounded-lg text-sm font-medium border transition-colors"
              :class="interval === 'monthly' ? 'bg-[#0D3B70] text-white border-[#0D3B70]' : 'bg-white text-gray-700 border-gray-200'"
              @click="interval = 'monthly'"
            >
              Monatlich
            </button>
            <button
              type="button"
              class="px-5 py-2 rounded-lg text-sm font-medium border transition-colors"
              :class="interval === 'yearly' ? 'bg-[#0D3B70] text-white border-[#0D3B70]' : 'bg-white text-gray-700 border-gray-200'"
              @click="interval = 'yearly'"
            >
              Jährlich
            </button>
          </div>

          <div class="text-center">
            <p class="text-gray-600 mb-1">
              {{ weCount }} Wohneinheit{{ weCount > 1 ? 'en' : '' }} à {{ formatCurrency(pricePreview?.price_per_we || '0') }} / Monat
            </p>
            <p class="text-5xl font-bold text-[#0D3B70]">
              {{ formatCurrency(interval === 'yearly' ? pricePreview?.total_yearly || '0' : pricePreview?.total_monthly || '0') }}
            </p>
            <p class="text-sm text-gray-500 mt-2">
              {{ interval === 'yearly' ? 'jährlich (2 Monate geschenkt)' : 'monatlich' }}
            </p>
          </div>

          <AppButton variant="primary" size="lg" full-width @click="startCheckout">
            14 Tage kostenlos testen
          </AppButton>
          <p class="text-xs text-center text-gray-500 mt-3">Kreditkarte erforderlich · Jederzeit kündbar</p>
        </div>
      </AppCard>

      <!-- Staffelpreise -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <AppCard
          v-for="tier in tiers"
          :key="tier.label"
          padding="md"
          shadow="sm"
          :class="{ 'ring-2 ring-[#0D3B70]': tier.active }"
        >
          <p class="text-sm font-medium text-gray-500">{{ tier.label }}</p>
          <p class="text-2xl font-bold text-[#0D3B70] mt-1">{{ formatCurrency(tier.price) }}</p>
          <p class="text-sm text-gray-600">pro WE / Monat</p>
        </AppCard>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * PricingView — Landing-Pricing mit WE-Slider und Live-Berechnung.
 */
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBillingStore } from '@/stores/billing'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const billingStore = useBillingStore()

const weCount = ref(3)
const interval = ref<'monthly' | 'yearly'>('yearly')

const tiers = computed(() => [
  {
    label: '1–5 WE',
    price: '9.75',
    active: weCount.value <= 5,
  },
  {
    label: '6–25 WE',
    price: '7.50',
    active: weCount.value >= 6 && weCount.value <= 25,
  },
  {
    label: '26–49 WE',
    price: '5.90',
    active: weCount.value >= 26,
  },
])

const pricePreview = computed(() => billingStore.pricePreview)

watch([weCount, interval], () => {
  billingStore.fetchPricePreview(weCount.value, interval.value)
}, { immediate: true })

function formatCurrency(value: string | number): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(num)
}

async function startCheckout(): Promise<void> {
  const session = await billingStore.startCheckout(weCount.value, interval.value)
  if (session?.session_url) {
    window.location.href = session.session_url
  } else {
    await router.push('/register')
  }
}
</script>
