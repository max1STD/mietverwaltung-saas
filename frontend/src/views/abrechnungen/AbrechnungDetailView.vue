<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Ladezustand -->
      <div v-if="abrechnungenStore.loading" class="py-12 text-center text-gray-500">
        Abrechnung wird geladen …
      </div>

      <template v-else-if="abrechnungenStore.currentAbrechnung">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <button
              class="text-gray-500 hover:text-[#0D3B70]"
              @click="$router.push('/abrechnungen')"
            >
              ← Zurück
            </button>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
                NK-Abrechnung {{ abrechnungenStore.currentAbrechnung.jahr }}
              </h1>
              <p class="text-gray-500">
                {{ abrechnungenStore.currentAbrechnung.einheit?.bezeichnung || 'Einheit' }}
                · {{ abrechnungenStore.currentAbrechnung.objekt?.bezeichnung || '–' }}
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <AppBadge :variant="badgeForStatus(abrechnungenStore.currentAbrechnung.status)">
              {{ statusLabel(abrechnungenStore.currentAbrechnung.status) }}
            </AppBadge>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Hauptbereich: Positionen -->
          <AppCard class="lg:col-span-2" padding="md" shadow="md">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-[#0D3B70]">Abrechnungspositionen</h2>
              <div class="flex gap-2">
                <AppButton
                  size="sm"
                  variant="secondary"
                  :loading="abrechnungenStore.saving"
                  :disabled="!canCalculate"
                  @click="berechnen"
                >
                  Positionen berechnen
                </AppButton>
                <AppButton
                  size="sm"
                  :loading="abrechnungenStore.saving"
                  :disabled="!canFinalize"
                  @click="finalisieren"
                >
                  Finalisieren
                </AppButton>
              </div>
            </div>

            <AppEmptyState
              v-if="!hasPositions"
              icon="🧮"
              title="Noch keine Positionen"
              description="Berechne die Abrechnung, um die Verteilung der umlagefähigen Kosten zu generieren."
              action-label="Positionen berechnen"
              @action="berechnen"
            />

            <AbrechnungPositionTable
              v-else
              :positions="abrechnungenStore.currentAbrechnung.positions || []"
            />
          </AppCard>

          <!-- Seitenleiste: Details -->
          <AppCard class="lg:col-span-1" padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Zusammenfassung</h2>
            <dl class="space-y-3 text-sm">
              <div class="flex justify-between">
                <dt class="text-gray-500">Zeitraum</dt>
                <dd class="font-medium text-gray-900">
                  {{ formatDate(abrechnungenStore.currentAbrechnung.zeitraum_von) }} –
                  {{ formatDate(abrechnungenStore.currentAbrechnung.zeitraum_bis) }}
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Gesamtkosten</dt>
                <dd class="font-medium text-gray-900">{{ formatCurrency(abrechnungenStore.currentAbrechnung.gesamtkosten) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Umlageanteil</dt>
                <dd class="font-medium text-[#0D3B70]">{{ formatCurrency(abrechnungenStore.currentAbrechnung.umlageanteil) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-gray-500">Status</dt>
                <dd class="font-medium text-gray-900">{{ statusLabel(abrechnungenStore.currentAbrechnung.status) }}</dd>
              </div>
            </dl>

            <div class="mt-6 pt-6 border-t border-gray-100">
              <AppButton
                v-if="abrechnungenStore.currentAbrechnung.status === 'finalisiert' || abrechnungenStore.currentAbrechnung.status === 'versendet'"
                full-width
                size="sm"
                variant="secondary"
                @click="downloadPdf"
              >
                📄 PDF herunterladen
              </AppButton>
            </div>
          </AppCard>
        </div>
      </template>

      <!-- Nicht gefunden -->
      <AppEmptyState
        v-else
        icon="🔍"
        title="Abrechnung nicht gefunden"
        description="Die gewünschte Abrechnung existiert nicht oder wurde gelöscht."
        action-label="Zurück zur Übersicht"
        @action="$router.push('/abrechnungen')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAbrechnungenStore, type Abrechnung, type AbrechnungStatus } from '@/stores/abrechnungen'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AbrechnungPositionTable from '@/components/abrechnung/AbrechnungPositionTable.vue'

const route = useRoute()
const router = useRouter()
const abrechnungenStore = useAbrechnungenStore()
const { showToast } = useToast()

const abrechnungId = computed(() => String(route.params.id))

const hasPositions = computed(() => {
  return (abrechnungenStore.currentAbrechnung?.positions?.length ?? 0) > 0
})

const canCalculate = computed(() => {
  const status = abrechnungenStore.currentAbrechnung?.status
  return status === 'entwurf' || status === 'berechnet'
})

const canFinalize = computed(() => {
  const status = abrechnungenStore.currentAbrechnung?.status
  return hasPositions.value && (status === 'berechnet' || status === 'entwurf')
})

function formatDate(value?: string): string {
  if (!value) return '–'
  return new Date(value).toLocaleDateString('de-DE')
}

function formatCurrency(value?: number): string {
  if (value == null) return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function statusLabel(status?: string): string {
  switch (status) {
    case 'entwurf':
      return 'Entwurf'
    case 'berechnet':
      return 'Berechnet'
    case 'finalisiert':
      return 'Finalisiert'
    case 'versendet':
      return 'Versendet'
    default:
      return status || '–'
  }
}

function badgeForStatus(status?: string): 'green' | 'yellow' | 'blue' | 'gray' {
  switch (status) {
    case 'finalisiert':
    case 'versendet':
      return 'green'
    case 'berechnet':
      return 'blue'
    case 'entwurf':
      return 'yellow'
    default:
      return 'gray'
  }
}

async function berechnen(): Promise<void> {
  const updated = await abrechnungenStore.calculatePositions(abrechnungId.value)
  if (updated) {
    showToast('Abrechnungspositionen berechnet.', 'success')
  } else {
    showToast(abrechnungenStore.error?.message || 'Fehler bei der Berechnung.', 'error')
  }
}

async function finalisieren(): Promise<void> {
  const confirmed = window.confirm(
    'Möchtest du die Abrechnung finalisieren? Anschließend können die Positionen nicht mehr geändert werden.',
  )
  if (!confirmed) return

  const updated = await abrechnungenStore.finalize(abrechnungId.value)
  if (updated) {
    showToast('Abrechnung finalisiert.', 'success')
  } else {
    showToast(abrechnungenStore.error?.message || 'Fehler beim Finalisieren.', 'error')
  }
}

function downloadPdf(): void {
  // Placeholder: PDF-Download wird in späterer Phase angebunden
  showToast('PDF-Download folgt in Phase 9.', 'info')
}

onMounted(async () => {
  await abrechnungenStore.fetchAbrechnung(abrechnungId.value)
})
</script>
