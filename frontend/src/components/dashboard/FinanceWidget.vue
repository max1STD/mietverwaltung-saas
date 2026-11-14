<template>
  <AppCard padding="md" shadow="md">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-[#0D3B70]">Finanzen (12 Monate)</h2>
      <div class="text-right">
        <p class="text-xs text-gray-500">Ø Netto/Monat</p>
        <p class="text-sm font-bold text-[#0D3B70]">{{ formatCurrency(averageNetto) }}</p>
      </div>
    </div>

    <div v-if="!financials?.monate?.length" class="text-center text-gray-500 py-8">
      Noch keine Finanzdaten verfügbar.
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="monat in financials.monate"
        :key="monat.monat"
        class="group"
      >
        <div class="flex items-center justify-between text-sm mb-1">
          <span class="text-gray-600 w-16">{{ monat.label }}</span>
          <div class="flex-1 mx-3 h-8 relative">
            <!-- Einnahmen-Bar (navy) -->
            <div
              class="absolute left-0 bg-[#0D3B70] rounded-l transition-all duration-500"
              :style="barStyle(monat.einnahmen, 'einnahmen')"
            />
            <!-- Kosten-Bar (rot) -->
            <div
              class="absolute bg-red-400 rounded-r transition-all duration-500"
              :style="barStyle(monat.kosten, 'kosten', monat.einnahmen)"
            />
          </div>
          <span class="text-xs font-medium text-gray-900 w-20 text-right">{{ formatCurrency(monat.netto) }}</span>
        </div>
      </div>
    </div>

    <div class="mt-6 grid grid-cols-3 gap-4 text-center">
      <div>
        <p class="text-xs text-gray-500">Einnahmen</p>
        <p class="text-sm font-bold text-[#0D3B70]">{{ formatCurrency(financials?.summe_einnahmen ?? 0) }}</p>
      </div>
      <div>
        <p class="text-xs text-gray-500">Kosten</p>
        <p class="text-sm font-bold text-red-600">{{ formatCurrency(financials?.summe_kosten ?? 0) }}</p>
      </div>
      <div>
        <p class="text-xs text-gray-500">Netto</p>
        <p
          class="text-sm font-bold"
          :class="(financials?.summe_netto ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'"
        >
          {{ formatCurrency(financials?.summe_netto ?? 0) }}
        </p>
      </div>
    </div>
  </AppCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppCard from '@/components/ui/AppCard.vue'
import type { DashboardFinancials } from '@/stores/dashboard'

interface Props {
  financials?: DashboardFinancials | null
}

const props = defineProps<Props>()

const maxValue = computed(() => {
  if (!props.financials?.monate?.length) return 1
  return Math.max(
    ...props.financials.monate.map((m) => Math.max(m.einnahmen, m.kosten)),
    1,
  )
})

const averageNetto = computed(() => {
  if (!props.financials?.monate?.length) return 0
  const sum = props.financials.monate.reduce((acc, m) => acc + m.netto, 0)
  return sum / props.financials.monate.length
})

function formatCurrency(value?: number): string {
  if (value === undefined || value === null) return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function barStyle(value: number, type: 'einnahmen' | 'kosten', offsetEinnahmen = 0) {
  const width = `${Math.min((value / maxValue.value) * 100, 100)}%`
  if (type === 'einnahmen') {
    return {
      width,
      top: '4px',
      bottom: '4px',
      left: '0',
    }
  }
  // Kosten-Bar startet nach der Einnahmen-Bar
  const leftPct = Math.min((offsetEinnahmen / maxValue.value) * 100, 100)
  return {
    width,
    top: '12px',
    bottom: '12px',
    left: `${leftPct}%`,
  }
}
</script>
