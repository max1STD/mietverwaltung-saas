<template>
  <AppTable :items="positions" :columns="columns">
    <template #row="{ item }">
      <td class="py-3 px-4 font-medium text-gray-900">{{ item.kategorie }}</td>
      <td class="py-3 px-4 text-sm text-gray-600 text-right">{{ formatCurrency(item.gesamtbetrag) }}</td>
      <td class="py-3 px-4 text-sm text-gray-600">{{ schluesselLabel(item.verteilungsschluessel) }}</td>
      <td class="py-3 px-4 text-sm text-gray-900 text-right font-medium">{{ formatCurrency(item.umlageanteil) }}</td>
    </template>
  </AppTable>

  <div
    v-if="positions.length > 0"
    class="mt-4 pt-4 border-t border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
  >
    <span class="text-sm text-gray-500">Summe der umlagefähigen Positionen</span>
    <span class="text-lg font-bold text-[#0D3B70]">{{ formatCurrency(totalUmlageanteil) }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AbrechnungPosition } from '@/stores/abrechnungen'
import AppTable from '@/components/ui/AppTable.vue'

const props = defineProps<{
  positions: AbrechnungPosition[]
}>()

const columns = [
  { key: 'kategorie', label: 'Kategorie' },
  { key: 'gesamtbetrag', label: 'Gesamtbetrag' },
  { key: 'verteilungsschluessel', label: 'Verteilungsschlüssel' },
  { key: 'umlageanteil', label: 'Umlageanteil' },
]

const totalUmlageanteil = computed(() => {
  return props.positions.reduce((sum, p) => sum + (p.umlageanteil || 0), 0)
})

function formatCurrency(value?: number): string {
  if (value == null) return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function schluesselLabel(schluessel?: string): string {
  switch (schluessel) {
    case 'nach_qm':
      return 'Nach Quadratmetern'
    case 'nach_personen':
      return 'Nach Personen'
    case 'nach_verbrauch':
      return 'Nach Verbrauch'
    case 'gleich':
      return 'Gleich verteilt'
    default:
      return schluessel || '–'
  }
}
</script>
