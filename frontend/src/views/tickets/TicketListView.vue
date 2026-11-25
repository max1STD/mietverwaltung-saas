<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Tickets</h1>
          <p class="text-gray-500 mt-1">Übersicht über alle Mieteranliegen und Instandhaltungsaufträge.</p>
        </div>
        <AppButton
          class="w-full sm:w-auto"
          @click="$router.push('/tickets/neu')"
        >
          + Ticket erstellen
        </AppButton>
      </div>

      <AppCard padding="md" shadow="md">
        <!-- Status-Filter -->
        <div class="flex flex-wrap gap-2 mb-4">
          <button
            v-for="filter in statusFilters"
            :key="filter.value"
            type="button"
            class="px-3 py-1.5 rounded-full text-sm font-medium border transition-colors"
            :class="selectedStatus === filter.value
              ? 'bg-[#0D3B70] text-white border-[#0D3B70]'
              : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'"
            @click="selectedStatus = filter.value"
          >
            {{ filter.label }}
          </button>
        </div>

        <div v-if="ticketsStore.loading" class="py-12 text-center text-gray-500">
          Tickets werden geladen …
        </div>

        <AppEmptyState
          v-else-if="filteredTickets.length === 0"
          icon="🎫"
          title="Keine Tickets gefunden"
          :description="
            selectedStatus !== 'alle'
              ? 'Keine Tickets mit diesem Status vorhanden.'
              : 'Erstelle das erste Ticket, um loszulegen.'
          "
          :action-label="selectedStatus !== 'alle' ? 'Filter zurücksetzen' : 'Ticket erstellen'"
          @action="selectedStatus !== 'alle' ? (selectedStatus = 'alle') : $router.push('/tickets/neu')"
        />

        <AppTable v-else :items="filteredTickets" :columns="columns">
          <template #row="{ item }">
            <td class="py-3 px-4">
              <RouterLink
                :to="`/tickets/${item.id}`"
                class="font-medium text-[#0D3B70] hover:underline"
              >
                {{ item.titel }}
              </RouterLink>
            </td>
            <td class="py-3 px-4">
              <AppBadge :variant="badgeForStatus(item.status)">{{ item.status || 'offen' }}</AppBadge>
            </td>
            <td class="py-3 px-4">
              <AppBadge :variant="badgeForPriority(item.prioritaet)">{{ item.prioritaet || 'normal' }}</AppBadge>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.kategorie || '–' }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ item.mieter?.name || '–' }}</td>
          </template>
        </AppTable>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useTicketsStore, type Ticket, type TicketStatus, type TicketPrioritaet } from '@/stores/tickets'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const ticketsStore = useTicketsStore()

const selectedStatus = ref<'alle' | TicketStatus>('alle')

interface StatusFilter {
  value: 'alle' | TicketStatus
  label: string
}

const statusFilters: StatusFilter[] = [
  { value: 'alle', label: 'Alle' },
  { value: 'offen', label: 'Offen' },
  { value: 'in_bearbeitung', label: 'In Bearbeitung' },
  { value: 'geschlossen', label: 'Geschlossen' },
]

const columns = [
  { key: 'titel', label: 'Titel' },
  { key: 'status', label: 'Status' },
  { key: 'prioritaet', label: 'Priorität' },
  { key: 'kategorie', label: 'Kategorie' },
  { key: 'mieter', label: 'Mieter' },
]

const filteredTickets = computed(() => {
  if (selectedStatus.value === 'alle') return ticketsStore.tickets
  return ticketsStore.tickets.filter((t) => t.status === selectedStatus.value)
})

function badgeForStatus(status?: string): 'yellow' | 'blue' | 'green' | 'gray' {
  switch (status) {
    case 'offen':
      return 'yellow'
    case 'in_bearbeitung':
      return 'blue'
    case 'erledigt':
    case 'geschlossen':
      return 'green'
    default:
      return 'gray'
  }
}

function badgeForPriority(prioritaet?: string): 'red' | 'yellow' | 'blue' | 'gray' {
  switch (prioritaet as TicketPrioritaet | undefined) {
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

watch(selectedStatus, () => {
  if (selectedStatus.value === 'alle') {
    ticketsStore.fetchTickets()
  } else {
    ticketsStore.fetchTickets({ status: selectedStatus.value })
  }
})

onMounted(() => {
  ticketsStore.fetchTickets()
})
</script>
