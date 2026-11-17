<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Ladezustand -->
      <div v-if="objekteStore.loading" class="py-12 text-center text-gray-500">
        Einheit wird geladen …
      </div>

      <template v-else-if="einheit">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <button
              class="text-gray-500 hover:text-[#0D3B70]"
              @click="$router.push(`/objekte/${einheit.objekt_id}`)"
            >
              ← Zum Objekt
            </button>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
                {{ einheit.name }}
              </h1>
              <p class="text-gray-500">
                Objekt {{ objektName }} · {{ einheit.wohnflaeche_qm }} m² · {{ formatCurrency(einheit.kaltmiete) }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <AppBadge :variant="badgeForStatus(einheit.vermietungsstatus)">
              {{ einheit.vermietungsstatus || 'frei' }}
            </AppBadge>
            <AppButton
              variant="secondary"
              @click="$router.push(`/einheiten/${einheitId}/bearbeiten`)"
            >
              Bearbeiten
            </AppButton>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-2 border-b border-gray-200 mb-6 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="px-4 py-2 text-sm font-medium whitespace-nowrap"
            :class="activeTab === tab.key ? 'text-[#0D3B70] border-b-2 border-[#0D3B70]' : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab: Stammdaten -->
        <div v-if="activeTab === 'stammdaten'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Kern-Daten -->
          <AppCard class="lg:col-span-2" padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Stammdaten</h2>
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt class="text-sm text-gray-500">Wohnfläche</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatArea(einheit.wohnflaeche_qm) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Nutzfläche</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatArea(einheit.nutzflaeche_qm) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Kaltmiete</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(einheit.kaltmiete) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">NK-Vorschuss</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(einheit.nebenkosten_vorschuss) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Etage</dt>
                <dd class="text-sm font-medium text-gray-900">{{ einheit.etage ?? '–' }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Räume</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatRooms(einheit) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Baujahr Einheit</dt>
                <dd class="text-sm font-medium text-gray-900">{{ einheit.baujahr_einheit || '–' }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Zustand</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatLabel(einheit.zustand) }}</dd>
              </div>
            </dl>

            <h3 class="text-md font-semibold text-[#0D3B70] mt-6 mb-3">Ausstattung</h3>
            <div class="flex flex-wrap gap-2">
              <AppBadge
                v-for="badge in ausstattungsBadges"
                :key="badge.key"
                :variant="badge.active ? 'navy' : 'gray'"
              >
                {{ badge.label }}
              </AppBadge>
              <span v-if="ausstattungsBadges.length === 0" class="text-sm text-gray-400">Keine Ausstattung hinterlegt</span>
            </div>

            <h3 class="text-md font-semibold text-[#0D3B70] mt-6 mb-3">Energie & Bau</h3>
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt class="text-sm text-gray-500">Energieklasse</dt>
                <dd class="text-sm font-medium text-gray-900">{{ einheit.energy_class || '–' }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Heizungsart</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatLabel(einheit.heizungsart) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Warmwasser</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatLabel(einheit.warmwasserbereitung) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Bauweise</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatLabel(einheit.bauweise) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Energieausweis</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatLabel(einheit.energieausweis_art) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Verbrauchskennwert</dt>
                <dd class="text-sm font-medium text-gray-900">{{ einheit.energieverbrauch_kennwert || '–' }}</dd>
              </div>
            </dl>
          </AppCard>

          <!-- Seitenleiste -->
          <div class="space-y-6">
            <AppCard padding="md" shadow="md">
              <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Aktueller Mieter</h2>
              <div v-if="einheit.aktueller_mieter">
                <p class="font-medium text-gray-900">{{ einheit.aktueller_mieter.name }}</p>
                <AppButton
                  size="sm"
                  variant="secondary"
                  class="mt-3"
                  @click="$router.push(`/mieter/${einheit.aktueller_mieter?.id}`)"
                >
                  Mieter öffnen
                </AppButton>
              </div>
              <AppEmptyState
                v-else
                icon="👤"
                title="Frei"
                description="Diese Einheit ist aktuell nicht vermietet."
                action-label="Mieter zuweisen"
                @action="$router.push(`/mietvertraege/neu?einheit=${einheitId}`)"
              />
            </AppCard>

            <AppCard padding="md" shadow="md">
              <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Schnellaktionen</h2>
              <div class="space-y-2">
                <AppButton size="sm" variant="secondary" class="w-full" @click="$router.push(`/tickets/neu?einheit=${einheitId}`)">
                  Ticket erstellen
                </AppButton>
                <AppButton size="sm" variant="secondary" class="w-full" @click="$router.push(`/kosten/neu?einheit=${einheitId}`)">
                  Kosten erfassen
                </AppButton>
                <AppButton size="sm" variant="secondary" class="w-full" @click="$router.push(`/mieter/neu?einheit=${einheitId}`)">
                  Mieter anlegen
                </AppButton>
              </div>
            </AppCard>
          </div>
        </div>

        <!-- Tab: Mieter-Historie -->
        <div v-else-if="activeTab === 'historie'">
          <AppCard padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Mieter-Historie</h2>
            <p class="text-sm text-gray-500">Hier werden zukünftig vergangene Mietverhältnisse dieser Einheit angezeigt.</p>
          </AppCard>
        </div>

        <!-- Tab: Dokumente -->
        <div v-else-if="activeTab === 'dokumente'">
          <AppCard padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Dokumente</h2>
            <DokumenteListe entity-type="einheit" :entity-id="Number(einheit.id)" />
          </AppCard>
        </div>
      </template>

      <!-- Einheit nicht gefunden -->
      <AppEmptyState
        v-else
        icon="🔍"
        title="Einheit nicht gefunden"
        description="Die gewünschte Einheit existiert nicht oder wurde gelöscht."
        action-label="Zur Objekt-Übersicht"
        @action="$router.push('/objekte')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObjekteStore, type Einheit } from '@/stores/objekte'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import DokumenteListe from '@/components/dokumente/DokumenteListe.vue'

const route = useRoute()
const router = useRouter()
const objekteStore = useObjekteStore()

const einheitId = computed(() => String(route.params.id))
const einheit = computed(() => {
  const all = objekteStore.objekte.flatMap((o) => o.einheiten || [])
  const fromCurrent = objekteStore.einheiten.find((e) => e.id === einheitId.value || e.public_id === einheitId.value)
  return fromCurrent || all.find((e) => e.id === einheitId.value || e.public_id === einheitId.value) || null
})
const objektName = computed(() => objekteStore.currentObjekt?.name || '')

const activeTab = ref('stammdaten')
const tabs = [
  { key: 'stammdaten', label: 'Stammdaten' },
  { key: 'historie', label: 'Mieter-Historie' },
  { key: 'dokumente', label: 'Dokumente' },
]

const ausstattungsBadges = computed(() => {
  const e = einheit.value
  if (!e) return []
  const list: { key: string; label: string; active: boolean }[] = []
  const add = (key: keyof Einheit, label: string) => {
    const val = e[key]
    if (val === true || val === false) {
      list.push({ key, label, active: !!val })
    }
  }
  add('balkon', 'Balkon')
  add('terrasse', 'Terrasse')
  add('garten', 'Garten')
  add('garage', 'Garage')
  add('stellplatz', 'Stellplatz')
  add('keller', 'Keller')
  add('aufzug', 'Aufzug')
  add('barrierefrei', 'Barrierefrei')
  add('moebliert', 'Möbliert')
  return list
})

function badgeForStatus(status?: string): 'green' | 'yellow' | 'red' | 'gray' {
  switch (status) {
    case 'vermietet':
      return 'green'
    case 'frei':
      return 'yellow'
    case 'renovierung':
    case 'gesperrt':
      return 'red'
    default:
      return 'gray'
  }
}

function formatCurrency(value?: number | string | null): string {
  if (value == null || value === '') return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(Number(value))
}

function formatArea(value?: number | string | null): string {
  if (value == null || value === '') return '–'
  return `${new Intl.NumberFormat('de-DE').format(Number(value))} m²`
}

function formatRooms(e: Einheit): string {
  if (e.rooms) return `${e.rooms} Zimmer`
  const parts = [e.wohnzimmer, e.schlafzimmer, e.badezimmer].filter((v) => v != null)
  if (parts.length === 0) return '–'
  return parts.join(' / ')
}

function formatLabel(value?: string | null): string {
  if (!value) return '–'
  return value.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

onMounted(async () => {
  if (!einheit.value) {
    // Lade alle Objekte/Einheiten, falls Direktzugriff
    await objekteStore.fetchObjekte()
  }
  if (einheit.value?.objekt_id) {
    await objekteStore.fetchObjekt(String(einheit.value.objekt_id))
  }
})
</script>
