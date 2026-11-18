<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div v-if="mietvertraegeStore.loading" class="py-12 text-center text-gray-500">
        Mietvertrag wird geladen …
      </div>

      <template v-else-if="vertrag">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <button class="text-gray-500 hover:text-[#0D3B70]" @click="$router.push('/mietvertraege')">← Zurück</button>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Mietvertrag</h1>
              <p class="text-gray-500">{{ vertrag.mieter?.name || '–' }} · {{ vertrag.einheit?.objekt_name || '–' }}</p>
            </div>
          </div>
          <div class="flex gap-2">
            <AppButton
              variant="secondary"
              @click="$router.push(`/mietvertraege/${vertragId}/bearbeiten`)"
            >
              Bearbeiten
            </AppButton>
            <AppButton
              variant="danger"
              :loading="mietvertraegeStore.saving"
              @click="deleteVertrag"
            >
              Löschen
            </AppButton>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Vertragsdaten -->
          <AppCard class="lg:col-span-2" padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Vertragsdaten</h2>
            <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt class="text-sm text-gray-500">Mieter</dt>
                <dd class="text-sm font-medium text-gray-900">
                  <RouterLink :to="`/mieter/${vertrag.mieter_id}`" class="text-[#0D3B70] hover:underline">
                    {{ vertrag.mieter?.name || '–' }}
                  </RouterLink>
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Objekt / Einheit</dt>
                <dd class="text-sm font-medium text-gray-900">
                  {{ vertrag.einheit?.objekt_name || '–' }} · {{ vertrag.einheit?.name || '–' }}
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Mietbeginn</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatDate(vertrag.mietbeginn) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Mietende</dt>
                <dd class="text-sm font-medium text-gray-900">{{ vertrag.mietende ? formatDate(vertrag.mietende) : '–' }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Kaltmiete</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(vertrag.kaltmiete) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">NK-Vorschuss</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(vertrag.nebenkosten_vorschuss) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Gesamtmiete</dt>
                <dd class="text-sm font-bold text-[#0D3B70]">{{ formatCurrency(gesamtmiete) }}</dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Kaution</dt>
                <dd class="text-sm font-medium text-gray-900">
                  {{ formatCurrency(vertrag.kaution) }}
                  <AppBadge v-if="vertrag.kaution_hinterlegt" variant="green" class="ml-2">hinterlegt</AppBadge>
                  <AppBadge v-else-if="vertrag.kaution" variant="yellow" class="ml-2">ausstehend</AppBadge>
                </dd>
              </div>
              <div>
                <dt class="text-sm text-gray-500">Status</dt>
                <dd class="text-sm font-medium text-gray-900">
                  <AppBadge :variant="badgeForStatus(vertrag.status)">{{ vertrag.status || 'aktiv' }}</AppBadge>
                </dd>
              </div>
            </dl>
          </AppCard>

          <!-- Seitenleiste -->
          <div class="space-y-6">
            <AppCard padding="md" shadow="md">
              <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Schnellaktionen</h2>
              <div class="space-y-2">
                <AppButton
                  size="sm"
                  full-width
                  @click="$router.push(`/mietvertraege/${vertragId}/bearbeiten`)"
                >
                  Vertrag bearbeiten
                </AppButton>
                <AppButton
                  size="sm"
                  variant="secondary"
                  full-width
                  @click="$router.push(`/einheiten/${vertrag.einheit_id}`)"
                >
                  Einheit anzeigen
                </AppButton>
                <AppButton
                  size="sm"
                  variant="secondary"
                  full-width
                  @click="$router.push(`/mieter/${vertrag.mieter_id}`)"
                >
                  Mieter anzeigen
                </AppButton>
              </div>
            </AppCard>
          </div>
        </div>
      </template>

      <AppEmptyState
        v-else
        icon="🔍"
        title="Mietvertrag nicht gefunden"
        description="Der gewünschte Mietvertrag existiert nicht oder wurde gelöscht."
        action-label="Zurück zur Übersicht"
        @action="$router.push('/mietvertraege')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMietvertraegeStore, type Mietvertrag, type MietvertragStatus } from '@/stores/mietvertraege'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const route = useRoute()
const router = useRouter()
const mietvertraegeStore = useMietvertraegeStore()
const { showToast } = useToast()

const vertragId = computed(() => String(route.params.id))
const vertrag = computed(() => mietvertraegeStore.currentMietvertrag)

const gesamtmiete = computed(() => {
  if (!vertrag.value) return 0
  return (vertrag.value.kaltmiete || 0) + (vertrag.value.nebenkosten_vorschuss || 0)
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

function badgeForStatus(status?: string): 'green' | 'yellow' | 'red' | 'gray' {
  switch (status as MietvertragStatus | undefined) {
    case 'aktiv':
      return 'green'
    case 'gekuendigt':
      return 'yellow'
    case 'beendet':
      return 'red'
    default:
      return 'gray'
  }
}

async function deleteVertrag(): Promise<void> {
  if (!confirm('Mietvertrag wirklich löschen?')) return
  const ok = await mietvertraegeStore.deleteMietvertrag(vertragId.value)
  if (ok) {
    showToast('Mietvertrag gelöscht.', 'success')
    await router.push('/mietvertraege')
  } else {
    showToast(mietvertraegeStore.error?.message || 'Löschen fehlgeschlagen.', 'error')
  }
}

onMounted(() => {
  mietvertraegeStore.fetchMietvertrag(vertragId.value)
})
</script>
