<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Mietzahlungen</h1>
          <p class="text-gray-500 mt-1">Soll-/Ist-Zahlungen und Mahnwesen im Blick.</p>
        </div>
        <div class="flex gap-2">
          <AppButton variant="secondary" @click="showGenerateModal = true">
            Generieren
          </AppButton>
          <AppButton @click="showCreateModal = true">
            + Zahlung anlegen
          </AppButton>
        </div>
      </div>

      <!-- KPI-Karten -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <AppCard padding="md" shadow="sm">
          <p class="text-sm text-gray-500">Offener Soll-Betrag</p>
          <p class="text-2xl font-bold text-[#0D3B70]">{{ formatCurrency(openSoll) }}</p>
        </AppCard>
        <AppCard padding="md" shadow="sm">
          <p class="text-sm text-gray-500">Eingegangene Zahlungen</p>
          <p class="text-2xl font-bold text-green-600">{{ formatCurrency(receivedTotal) }}</p>
        </AppCard>
        <AppCard padding="md" shadow="sm">
          <p class="text-sm text-gray-500">Überfällige Posten</p>
          <p class="text-2xl font-bold text-red-600">{{ overdueCount }}</p>
        </AppCard>
      </div>

      <AppCard padding="md" shadow="md">
        <!-- Filter -->
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-4">
          <div class="sm:col-span-2">
            <AppInput
              id="zahlung-search"
              v-model="searchQuery"
              placeholder="Nach Mieter oder Einheit suchen …"
              type="search"
            />
          </div>
          <div>
            <label for="filter-status" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              id="filter-status"
              v-model="filterStatus"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="">Alle Status</option>
              <option value="offen">Offen</option>
              <option value="teilweise">Teilweise</option>
              <option value="bezahlt">Bezahlt</option>
              <option value="ueberfaellig">Überfällig</option>
            </select>
          </div>
          <div>
            <label for="filter-mahnstufe" class="block text-sm font-medium text-gray-700 mb-1">Mahnstufe</label>
            <select
              id="filter-mahnstufe"
              v-model="filterMahnstufe"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="">Alle</option>
              <option value="1">Mahnung 1</option>
              <option value="2">Mahnung 2</option>
              <option value="3">Mahnung 3</option>
            </select>
          </div>
        </div>

        <!-- Ladezustand -->
        <div v-if="mietzahlungenStore.loading" class="py-12 text-center text-gray-500">
          Mietzahlungen werden geladen …
        </div>

        <!-- Leerer Zustand -->
        <AppEmptyState
          v-else-if="filteredZahlungen.length === 0"
          icon="💳"
          title="Keine Mietzahlungen gefunden"
          :description="
            searchQuery || filterStatus || filterMahnstufe
              ? 'Passe die Filter an, um Ergebnisse zu sehen.'
              : 'Lege deine erste Mietzahlung an oder generiere sie aus Verträgen.'
          "
          :action-label="searchQuery || filterStatus || filterMahnstufe ? 'Filter zurücksetzen' : 'Zahlung anlegen'"
          @action="resetFilters(); showCreateModal = true"
        />

        <!-- Tabelle -->
        <AppTable
          v-else
          :items="filteredZahlungen"
          :columns="columns"
          initial-sort="zahlungsdatum"
        >
          <template #row="{ item }">
            <td class="py-3 px-4">
              <div class="font-medium text-gray-900">{{ item.mieter?.name || '–' }}</div>
              <div class="text-xs text-gray-500">{{ item.einheit?.objekt_name }} / {{ item.einheit?.name || '–' }}</div>
            </td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ formatDate(item.zahlungsdatum) }}</td>
            <td class="py-3 px-4 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(item.betrag_soll) }}</td>
            <td class="py-3 px-4 text-sm text-gray-600 text-right">{{ formatCurrency(item.betrag_ist) }}</td>
            <td class="py-3 px-4 text-sm text-gray-600 text-right">{{ formatCurrency(item.offener_betrag) }}</td>
            <td class="py-3 px-4">
              <AppBadge :variant="badgeForStatus(mietzahlungenStore.statusFor(item))">
                {{ statusLabel(mietzahlungenStore.statusFor(item)) }}
              </AppBadge>
            </td>
            <td class="py-3 px-4">
              <span v-if="item.mahnstufe > 0" class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-100 text-red-700 text-xs font-bold">
                {{ item.mahnstufe }}
              </span>
              <span v-else class="text-sm text-gray-400">–</span>
            </td>
          </template>

          <template #actions="{ item }">
            <div class="flex items-center justify-end gap-2">
              <AppButton
                v-if="mietzahlungenStore.statusFor(item) !== 'bezahlt'"
                size="sm"
                :loading="mietzahlungenStore.saving"
                @click="markPaid(item)"
              >
                Als bezahlt markieren
              </AppButton>
              <AppButton
                v-if="item.mahnstufe < 3 && mietzahlungenStore.statusFor(item) !== 'bezahlt'"
                variant="secondary"
                size="sm"
                :loading="mietzahlungenStore.saving"
                @click="mahnen(item.id)"
              >
                Mahnen
              </AppButton>
              <AppButton
                variant="danger"
                size="sm"
                :loading="mietzahlungenStore.saving"
                @click="deleteZahlung(item.id)"
              >
                Löschen
              </AppButton>
            </div>
          </template>
        </AppTable>
      </AppCard>
    </div>

    <!-- Modal: Zahlung anlegen -->
    <AppModal v-model="showCreateModal" title="Neue Mietzahlung">
      <form class="space-y-4" @submit.prevent="createZahlung">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <AppInput
            id="new-betrag"
            v-model="createForm.betrag_soll"
            label="Soll-Betrag (€)"
            type="number"
            step="0.01"
            placeholder="0,00"
            required
          />
          <AppInput
            id="new-faellig"
            v-model="createForm.zahlungsdatum"
            label="Zahlungsdatum / Fällig am"
            type="date"
            required
          />
        </div>

        <div>
          <label for="new-vertrag" class="block text-sm font-medium text-gray-700 mb-1">Mietvertrag</label>
          <select
            id="new-vertrag"
            v-model="createForm.vertrag_id"
            required
            class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
          >
            <option value="">Bitte wählen</option>
            <option
              v-for="vertrag in vertraegeStore.mietvertraege"
              :key="vertrag.id"
              :value="vertrag.id"
            >
              {{ vertrag.mieter?.name }} — {{ vertrag.einheit?.objekt_name }} / {{ vertrag.einheit?.name }}
            </option>
          </select>
        </div>

        <AppInput
          id="new-referenz"
          v-model="createForm.zahlungsreferenz"
          label="Zahlungsreferenz / Verwendungszweck"
          placeholder="Miete Oktober 2026"
        />

        <div class="flex justify-end gap-3 pt-2">
          <AppButton type="button" variant="ghost" @click="showCreateModal = false">
            Abbrechen
          </AppButton>
          <AppButton type="submit" :loading="mietzahlungenStore.saving">
            Zahlung anlegen
          </AppButton>
        </div>
      </form>
    </AppModal>

    <!-- Modal: Generieren -->
    <AppModal v-model="showGenerateModal" title="Mietzahlungen generieren">
      <form class="space-y-4" @submit.prevent="generateZahlungen">
        <AppInput
          id="generate-monat"
          v-model="generateForm.monat"
          label="Monat"
          type="month"
          required
        />
        <p class="text-sm text-gray-500">
          Es werden für alle aktiven Mietverträge Zahlungsposten mit der Gesamtmiete (Kaltmiete + Nebenkostenvorschuss) angelegt, sofern für den Monat noch kein Posten existiert.
        </p>
        <div class="flex justify-end gap-3 pt-2">
          <AppButton type="button" variant="ghost" @click="showGenerateModal = false">
            Abbrechen
          </AppButton>
          <AppButton type="submit" :loading="mietzahlungenStore.saving">
            Generieren
          </AppButton>
        </div>
      </form>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMietzahlungenStore, type Mietzahlung, type MietzahlungStatus } from '@/stores/mietzahlungen'
import { useMietvertraegeStore, type Mietvertrag } from '@/stores/mietvertraege'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppModal from '@/components/ui/AppModal.vue'

const mietzahlungenStore = useMietzahlungenStore()
const vertraegeStore = useMietvertraegeStore()
const { showToast } = useToast()

const searchQuery = ref('')
const filterStatus = ref('')
const filterMahnstufe = ref('')
const showCreateModal = ref(false)
const showGenerateModal = ref(false)

const createForm = reactive({
  betrag_soll: '',
  zahlungsdatum: new Date().toISOString().split('T')[0],
  vertrag_id: '',
  zahlungsreferenz: '',
})

const generateForm = reactive({
  monat: new Date().toISOString().slice(0, 7),
})

const columns = [
  { key: 'mieter', label: 'Mieter / Einheit' },
  { key: 'zahlungsdatum', label: 'Zahlungsdatum' },
  { key: 'betrag_soll', label: 'Soll' },
  { key: 'betrag_ist', label: 'Ist' },
  { key: 'offener_betrag', label: 'Offen' },
  { key: 'status', label: 'Status' },
  { key: 'mahnstufe', label: 'Mahnstufe' },
]

const filteredZahlungen = computed(() => {
  let result = [...mietzahlungenStore.mietzahlungen]

  const query = searchQuery.value.toLowerCase().trim()
  if (query) {
    result = result.filter(
      (z) =>
        ((z.mieter?.name ?? '').toLowerCase().includes(query)) ||
        ((z.einheit?.name ?? '').toLowerCase().includes(query)) ||
        ((z.einheit?.objekt_name ?? '').toLowerCase().includes(query)) ||
        ((z.zahlungsreferenz ?? '').toLowerCase().includes(query)),
    )
  }

  if (filterStatus.value) {
    result = result.filter((z) => mietzahlungenStore.statusFor(z) === filterStatus.value)
  }

  if (filterMahnstufe.value) {
    result = result.filter((z) => z.mahnstufe === Number(filterMahnstufe.value))
  }

  return result
})

const openSoll = computed(() => {
  return filteredZahlungen.value
    .filter((z) => mietzahlungenStore.statusFor(z) !== 'bezahlt')
    .reduce((sum, z) => sum + (z.offener_betrag || 0), 0)
})

const receivedTotal = computed(() => {
  return filteredZahlungen.value
    .filter((z) => mietzahlungenStore.statusFor(z) === 'bezahlt')
    .reduce((sum, z) => sum + (z.betrag_ist || z.betrag_soll || 0), 0)
})

const overdueCount = computed(() => {
  return filteredZahlungen.value.filter((z) => mietzahlungenStore.statusFor(z) === 'ueberfaellig').length
})

function formatDate(value?: string | null): string {
  if (!value) return '–'
  return new Date(value).toLocaleDateString('de-DE')
}

function formatCurrency(value?: number | string | null): string {
  if (value == null) return '–'
  const num = typeof value === 'string' ? Number(value) : value
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(num)
}

function statusLabel(status?: MietzahlungStatus | string): string {
  switch (status) {
    case 'offen':
      return 'Offen'
    case 'teilweise':
      return 'Teilweise'
    case 'bezahlt':
      return 'Bezahlt'
    case 'ueberfaellig':
      return 'Überfällig'
    default:
      return status || '–'
  }
}

function badgeForStatus(status?: MietzahlungStatus | string): 'green' | 'yellow' | 'red' | 'gray' {
  switch (status) {
    case 'bezahlt':
      return 'green'
    case 'teilweise':
      return 'yellow'
    case 'ueberfaellig':
      return 'red'
    case 'offen':
      return 'gray'
    default:
      return 'gray'
  }
}

function resetFilters(): void {
  searchQuery.value = ''
  filterStatus.value = ''
  filterMahnstufe.value = ''
}

async function createZahlung(): Promise<void> {
  if (!createForm.vertrag_id) {
    showToast('Bitte wähle einen Mietvertrag aus.', 'warning')
    return
  }

  const betrag = Number(createForm.betrag_soll.replace(',', '.'))
  if (!betrag || betrag <= 0) {
    showToast('Bitte gib einen gültigen Soll-Betrag ein.', 'warning')
    return
  }

  const vertrag = vertraegeStore.mietvertraege.find((v: Mietvertrag) => v.id === createForm.vertrag_id)

  const created = await mietzahlungenStore.createMietzahlung({
    vertrag_id: createForm.vertrag_id,
    mieter_id: vertrag?.mieter_id,
    betrag_soll: betrag,
    zahlungsdatum: createForm.zahlungsdatum,
    zahlungsreferenz: createForm.zahlungsreferenz || undefined,
  })

  if (created) {
    showToast('Mietzahlung angelegt.', 'success')
    showCreateModal.value = false
    resetCreateForm()
  } else {
    showToast(mietzahlungenStore.error?.message || 'Fehler beim Anlegen.', 'error')
  }
}

function resetCreateForm(): void {
  createForm.betrag_soll = ''
  createForm.zahlungsdatum = new Date().toISOString().split('T')[0]
  createForm.vertrag_id = ''
  createForm.zahlungsreferenz = ''
}

async function markPaid(zahlung: Mietzahlung): Promise<void> {
  const betrag = zahlung.betrag_soll
  const updated = await mietzahlungenStore.markPaid(zahlung.id, {
    betrag_ist: betrag,
    zahlungsdatum: new Date().toISOString().split('T')[0],
  })

  if (updated) {
    showToast('Zahlung als bezahlt markiert.', 'success')
  } else {
    showToast(mietzahlungenStore.error?.message || 'Fehler beim Markieren.', 'error')
  }
}

async function mahnen(id: string): Promise<void> {
  const updated = await mietzahlungenStore.escalate(id)
  if (updated) {
    showToast(`Mahnstufe ${updated.mahnstufe} gesetzt.`, 'success')
  } else {
    showToast(mietzahlungenStore.error?.message || 'Fehler beim Mahnen.', 'error')
  }
}

async function deleteZahlung(id: string): Promise<void> {
  const confirmed = window.confirm('Möchtest du diese Zahlung wirklich löschen?')
  if (!confirmed) return

  const success = await mietzahlungenStore.deleteMietzahlung(id)
  if (success) {
    showToast('Zahlung gelöscht.', 'success')
  } else {
    showToast(mietzahlungenStore.error?.message || 'Fehler beim Löschen.', 'error')
  }
}

async function generateZahlungen(): Promise<void> {
  if (!generateForm.monat) {
    showToast('Bitte wähle einen Monat aus.', 'warning')
    return
  }
  const monat = `${generateForm.monat}-01`
  const generated = await mietzahlungenStore.generate(monat)
  if (generated.length) {
    showToast(`${generated.length} Zahlungsposten generiert.`, 'success')
    showGenerateModal.value = false
  } else if (mietzahlungenStore.error) {
    showToast(mietzahlungenStore.error.message || 'Fehler beim Generieren.', 'error')
  } else {
    showToast('Keine neuen Zahlungsposten notwendig.', 'info')
    showGenerateModal.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    mietzahlungenStore.fetchMietzahlungen(),
    vertraegeStore.fetchMietvertraege(),
  ])
})
</script>
