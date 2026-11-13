<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Seitenkopf -->
      <div class="mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Dashboard</h1>
        <p class="text-gray-500 mt-1">Übersicht über deine Immobilien, Mieter und offenen Tickets.</p>
      </div>

      <!-- Stats-Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <AppCard padding="md" shadow="md">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Objekte</p>
              <p class="text-3xl font-bold text-[#0D3B70] mt-1">{{ stats.objekte }}</p>
            </div>
            <span class="text-2xl">🏠</span>
          </div>
        </AppCard>

        <AppCard padding="md" shadow="md">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Wohneinheiten</p>
              <p class="text-3xl font-bold text-[#0D3B70] mt-1">{{ stats.einheiten }}</p>
            </div>
            <span class="text-2xl">🏢</span>
          </div>
        </AppCard>

        <AppCard padding="md" shadow="md">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Mieter</p>
              <p class="text-3xl font-bold text-[#0D3B70] mt-1">{{ stats.mieter }}</p>
            </div>
            <span class="text-2xl">👤</span>
          </div>
        </AppCard>

        <AppCard padding="md" shadow="md">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Offene Tickets</p>
              <p class="text-3xl font-bold text-red-600 mt-1">{{ stats.offeneTickets }}</p>
            </div>
            <span class="text-2xl">🎫</span>
          </div>
        </AppCard>
      </div>

      <!-- Hauptbereich: Letzte Aktivität + Offene Tickets -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Letzte Aktivität -->
        <AppCard class="lg:col-span-2" padding="none" shadow="md">
          <div class="px-6 py-4 border-b border-gray-100">
            <h2 class="text-lg font-semibold text-[#0D3B70]">Neueste Aktivität</h2>
          </div>

          <div v-if="loading" class="p-8 text-center text-gray-500">
            Daten werden geladen …
          </div>

          <AppEmptyState
            v-else-if="recentActivity.length === 0"
            icon="📋"
            title="Noch keine Aktivität"
            description="Sobald du Objekte, Mieter oder Tickets anlegst, erscheint hier eine Übersicht."
            action-label="Erstes Objekt anlegen"
            @action="$router.push('/objekte/neu')"
          />

          <ul v-else class="divide-y divide-gray-100">
            <li
              v-for="activity in recentActivity"
              :key="activity.id"
              class="px-6 py-4 flex items-start gap-4 hover:bg-gray-50/50 transition-colors"
            >
              <span class="text-xl">{{ activity.icon }}</span>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ activity.title }}</p>
                <p class="text-xs text-gray-500">{{ activity.subtitle }}</p>
              </div>
              <span class="text-xs text-gray-400 whitespace-nowrap">{{ activity.date }}</span>
            </li>
          </ul>
        </AppCard>

        <!-- Offene Tickets -->
        <AppCard padding="none" shadow="md">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-[#0D3B70]">Offene Tickets</h2>
            <RouterLink to="/tickets" class="text-sm text-[#0D3B70] hover:underline">Alle anzeigen</RouterLink>
          </div>

          <div v-if="loading" class="p-8 text-center text-gray-500">
            Daten werden geladen …
          </div>

          <AppEmptyState
            v-else-if="offeneTickets.length === 0"
            icon="✅"
            title="Alles erledigt"
            description="Keine offenen Tickets vorhanden."
            action-label="Ticket erstellen"
            @action="$router.push('/tickets/neu')"
          />

          <ul v-else class="divide-y divide-gray-100">
            <li
              v-for="ticket in offeneTickets"
              :key="ticket.id"
              class="px-6 py-4 hover:bg-gray-50/50 transition-colors cursor-pointer"
              @click="$router.push(`/tickets/${ticket.id}`)"
            >
              <div class="flex items-start justify-between gap-2 mb-1">
                <p class="text-sm font-medium text-gray-900 line-clamp-1">{{ ticket.titel }}</p>
                <AppBadge :variant="badgeForPriority(ticket.prioritaet)">
                  {{ ticket.prioritaet || 'normal' }}
                </AppBadge>
              </div>
              <p class="text-xs text-gray-500 line-clamp-1">
                {{ ticket.objekt?.bezeichnung || ticket.einheit?.bezeichnung || 'Kein Objekt' }}
              </p>
            </li>
          </ul>
        </AppCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useObjekteStore } from '@/stores/objekte'
import { useMieterStore } from '@/stores/mieter'
import { useTicketsStore, type Ticket } from '@/stores/tickets'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

interface ActivityItem {
  id: string
  icon: string
  title: string
  subtitle: string
  date: string
}

const objekteStore = useObjekteStore()
const mieterStore = useMieterStore()
const ticketsStore = useTicketsStore()
const { showToast } = useToast()

const loading = ref(true)

const stats = computed(() => ({
  objekte: objekteStore.objekte.length,
  einheiten: objekteStore.objekte.reduce(
    (sum, objekt) => sum + (objekt.einheiten_count || 0),
    0,
  ),
  mieter: mieterStore.mieter.length,
  offeneTickets: ticketsStore.tickets.filter(
    (t) => t.status === 'offen' || t.status === 'in_bearbeitung',
  ).length,
}))

const offeneTickets = computed(() =>
  ticketsStore.tickets
    .filter((t) => t.status === 'offen' || t.status === 'in_bearbeitung')
    .slice(0, 5),
)

const recentActivity = computed(() => {
  const items: ActivityItem[] = []

  objekteStore.objekte.slice(0, 3).forEach((objekt) => {
    items.push({
      id: `obj-${objekt.id}`,
      icon: '🏠',
      title: objekt.bezeichnung,
      subtitle: `Objekt · ${objekt.adresse || 'Keine Adresse'}`,
      date: formatDate(objekt.created_at),
    })
  })

  mieterStore.mieter.slice(0, 3).forEach((m) => {
    items.push({
      id: `mieter-${m.id}`,
      icon: '👤',
      title: m.name,
      subtitle: 'Mieter angelegt',
      date: formatDate(m.created_at),
    })
  })

  ticketsStore.tickets.slice(0, 3).forEach((ticket) => {
    items.push({
      id: `ticket-${ticket.id}`,
      icon: '🎫',
      title: ticket.titel,
      subtitle: `Ticket · ${ticket.status || 'offen'}`,
      date: formatDate(ticket.created_at),
    })
  })

  return items
    .sort(
      (a, b) =>
        new Date(b.date || '1970-01-01').getTime() -
        new Date(a.date || '1970-01-01').getTime(),
    )
    .slice(0, 6)
})

function badgeForPriority(prioritaet?: string): 'red' | 'yellow' | 'blue' | 'gray' {
  switch (prioritaet) {
    case 'dringend':
    case 'hoch':
      return 'red'
    case 'normal':
      return 'yellow'
    case 'niedrig':
      return 'blue'
    default:
      return 'gray'
  }
}

function formatDate(value?: string): string {
  if (!value) return ''
  const date = new Date(value)
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      objekteStore.fetchObjekte(),
      mieterStore.fetchMieter(),
      ticketsStore.fetchTickets(),
    ])
  } catch {
    showToast('Fehler beim Laden des Dashboards.', 'error')
  } finally {
    loading.value = false
  }
})
</script>
