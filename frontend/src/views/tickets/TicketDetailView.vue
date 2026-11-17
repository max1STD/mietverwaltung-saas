<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div v-if="ticketsStore.loading" class="py-12 text-center text-gray-500">
        Ticket wird geladen …
      </div>

      <template v-else-if="ticketsStore.currentTicket">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
          <div class="flex items-start gap-3">
            <button class="text-gray-500 hover:text-[#0D3B70] mt-1" @click="$router.push('/tickets')">
              ← Zurück
            </button>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">{{ ticketsStore.currentTicket.titel }}</h1>
              <div class="flex flex-wrap items-center gap-2 mt-2">
                <AppBadge :variant="badgeForStatus(ticketsStore.currentTicket.status)">{{ ticketsStore.currentTicket.status || 'offen' }}</AppBadge>
                <AppBadge :variant="badgeForPriority(ticketsStore.currentTicket.prioritaet)">{{ ticketsStore.currentTicket.prioritaet || 'normal' }}</AppBadge>
                <span class="text-sm text-gray-500">{{ ticketsStore.currentTicket.kategorie || 'Sonstiges' }}</span>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <select
              v-model="statusUpdate"
              class="px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              @change="updateStatus"
            >
              <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
            </select>

            <select
              v-model="prioritaetUpdate"
              class="px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              @change="updatePrioritaet"
            >
              <option v-for="p in prioritaetOptions" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
        </div>

        <!-- Beschreibung -->
        <AppCard padding="md" shadow="md" class="mb-6"
        >
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-2">Beschreibung</h2>
          <p class="text-gray-700 whitespace-pre-line">
            {{ ticketsStore.currentTicket.beschreibung || 'Keine Beschreibung vorhanden.' }}
          </p>
          <div class="mt-4 text-sm text-gray-500">
            Erstellt am {{ formatDate(ticketsStore.currentTicket.created_at) }}
            <span v-if="ticketsStore.currentTicket.mieter">· {{ ticketsStore.currentTicket.mieter.name }}</span>
            <span v-if="ticketsStore.currentTicket.objekt"
              >· {{ ticketsStore.currentTicket.objekt.bezeichnung }}
            </span>
          </div>
        </AppCard>

        <!-- Kommentare -->
        <AppCard padding="md" shadow="md"
        >
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Kommentare</h2>

          <div v-if="ticketsStore.kommentare.length === 0" class="text-sm text-gray-500 mb-6">
            Noch keine Kommentare vorhanden.
          </div>

          <div v-else class="space-y-4 mb-6">
            <div
              v-for="kommentar in ticketsStore.kommentare"
              :key="kommentar.id"
              class="flex gap-3"
            >
              <div class="w-8 h-8 rounded-full bg-[#0D3B70]/10 flex items-center justify-center text-[#0D3B70] text-sm font-semibold shrink-0"
              >
                {{ (kommentar.autor_name || 'U')[0].toUpperCase() }}
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900">{{ kommentar.autor_name || 'Unbekannt' }}</span>
                  <span class="text-xs text-gray-400">{{ formatDate(kommentar.created_at) }}</span>
                  <AppBadge v-if="kommentar.intern" variant="gray">intern</AppBadge>
                </div>
                <p class="text-sm text-gray-700 mt-1">{{ kommentar.nachricht }}</p>
              </div>
            </div>
          </div>

          <form class="space-y-3" @submit.prevent="addKommentar">
            <textarea
              id="kommentar"
              v-model="neuerKommentar"
              rows="3"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              placeholder="Neuen Kommentar verfassen …"
            />
            <div class="flex items-center justify-between">
              <label class="flex items-center gap-2 text-sm text-gray-600"
              >
                <input v-model="internKommentar" type="checkbox" />
                Interner Kommentar
              </label>
              <AppButton type="submit" :loading="ticketsStore.saving">
                Kommentar hinzufügen
              </AppButton>
            </div>
          </form>
        </AppCard>

        <!-- Dokumente -->
        <AppCard padding="md" shadow="md" class="mt-6">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Dokumente</h2>
          <DokumenteListe
            entity-type="ticket"
            :entity-id="Number(ticketId)"
          />
        </AppCard>
      </template>

      <AppEmptyState
        v-else
        icon="🔍"
        title="Ticket nicht gefunden"
        description="Das gewünschte Ticket existiert nicht oder wurde gelöscht."
        action-label="Zur Ticket-Übersicht"
        @action="$router.push('/tickets')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useTicketsStore, type TicketStatus, type TicketPrioritaet } from '@/stores/tickets'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import DokumenteListe from '@/components/dokumente/DokumenteListe.vue'

const route = useRoute()
const ticketsStore = useTicketsStore()
const { showToast } = useToast()

const ticketId = computed(() => String(route.params.id))
const neuerKommentar = ref('')
const internKommentar = ref(false)

const statusOptions: TicketStatus[] = [
  'offen',
  'in_bearbeitung',
  'wartend_auf_mieter',
  'wartend_auf_handwerker',
  'erledigt',
  'geschlossen',
  'abgelehnt',
]

const prioritaetOptions: TicketPrioritaet[] = ['niedrig', 'normal', 'hoch', 'dringend']

const statusUpdate = ref<TicketStatus>('offen')
const prioritaetUpdate = ref<TicketPrioritaet>('normal')

watch(
  () => ticketsStore.currentTicket,
  (ticket) => {
    if (ticket) {
      statusUpdate.value = (ticket.status as TicketStatus) || 'offen'
      prioritaetUpdate.value = (ticket.prioritaet as TicketPrioritaet) || 'normal'
    }
  },
  { immediate: true },
)

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

function formatDate(value?: string): string {
  if (!value) return ''
  return new Date(value).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function updateStatus(): Promise<void> {
  const updated = await ticketsStore.updateTicket(ticketId.value, {
    status: statusUpdate.value,
  })
  if (updated) {
    showToast('Status aktualisiert.', 'success')
  } else {
    showToast(ticketsStore.error?.message || 'Fehler beim Aktualisieren.', 'error')
  }
}

async function updatePrioritaet(): Promise<void> {
  const updated = await ticketsStore.updateTicket(ticketId.value, {
    prioritaet: prioritaetUpdate.value,
  })
  if (updated) {
    showToast('Priorität aktualisiert.', 'success')
  } else {
    showToast(ticketsStore.error?.message || 'Fehler beim Aktualisieren.', 'error')
  }
}

async function addKommentar(): Promise<void> {
  if (!neuerKommentar.value.trim()) {
    showToast('Bitte gib einen Kommentar ein.', 'warning')
    return
  }

  const created = await ticketsStore.createKommentar(
    ticketId.value,
    neuerKommentar.value,
    internKommentar.value,
  )
  if (created) {
    showToast('Kommentar hinzugefügt.', 'success')
    neuerKommentar.value = ''
    internKommentar.value = false
  } else {
    showToast(ticketsStore.error?.message || 'Fehler beim Speichern.', 'error')
  }
}

watch(
  () => ticketId.value,
  async (id) => {
    await ticketsStore.fetchTicket(id)
    if (ticketsStore.currentTicket) {
      await ticketsStore.fetchKommentare(id)
    }
  },
)

onMounted(async () => {
  await ticketsStore.fetchTicket(ticketId.value)
  if (ticketsStore.currentTicket) {
    await ticketsStore.fetchKommentare(ticketId.value)
  }
})
</script>
