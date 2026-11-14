<template>
  <AppCard padding="none" shadow="md">
    <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
      <h2 class="text-lg font-semibold text-[#0D3B70]">Offene Tickets & Fristen</h2>
      <RouterLink to="/tickets" class="text-sm text-[#0D3B70] hover:underline">Alle Tickets</RouterLink>
    </div>

    <div v-if="!insights?.insights?.length" class="p-8 text-center text-gray-500">
      <p>🎉 Alles im grünen Bereich.</p>
      <p class="text-sm mt-1">Keine offenen Tickets, Mahnungen oder anstehenden Fristen.</p>
    </div>

    <ul v-else class="divide-y divide-gray-100">
      <li
        v-for="insight in insights.insights"
        :key="`${insight.typ}-${insight.entity_id ?? insight.titel}`"
        class="px-6 py-4 hover:bg-gray-50/50 transition-colors cursor-pointer"
        @click="navigate(insight.link)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3">
            <span class="text-xl">{{ iconFor(insight.typ) }}</span>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ insight.titel }}</p>
              <p class="text-xs text-gray-500">{{ insight.beschreibung }}</p>
            </div>
          </div>
          <AppBadge :variant="badgeVariant(insight.prioritaet)">
            {{ insight.prioritaet }}
          </AppBadge>
        </div>
      </li>
    </ul>
  </AppCard>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import type { DashboardInsights, DashboardInsight } from '@/stores/dashboard'

interface Props {
  insights?: DashboardInsights | null
}

defineProps<Props>()

const router = useRouter()

function iconFor(typ: DashboardInsight['typ']): string {
  switch (typ) {
    case 'leerstand': return '🏢'
    case 'ticket': return '🎫'
    case 'mahnung': return '⚠️'
    case 'frist': return '📅'
    default: return 'ℹ️'
  }
}

function badgeVariant(prioritaet: DashboardInsight['prioritaet']) {
  switch (prioritaet) {
    case 'dringend': return 'red'
    case 'hoch': return 'yellow'
    case 'normal': return 'blue'
    case 'niedrig': return 'gray'
    default: return 'gray'
  }
}

function navigate(link?: string): void {
  if (link) {
    router.push(link)
  }
}
</script>
