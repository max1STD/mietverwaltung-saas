<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div v-if="bewerbungenStore.loading" class="py-12 text-center text-gray-500">
        Bewerbung wird geladen …
      </div>

      <template v-else-if="bewerbungenStore.currentBewerbung">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <button class="text-gray-500 hover:text-[#0D3B70]" @click="$router.push('/bewerbungen')">
              ← Zurück
            </button>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
                {{ bewerbung.first_name }} {{ bewerbung.last_name }}
              </h1>
              <p class="text-gray-500">Bewerbung für {{ bewerbung.einheit?.objekt_name || '–' }} — {{ bewerbung.einheit?.name || '–' }}</p>
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <AppButton
              v-if="canDecide"
              :loading="bewerbungenStore.saving"
              @click="annehmen"
            >
              Annehmen
            </AppButton>
            <AppButton
              v-if="canDecide"
              variant="danger"
              :loading="bewerbungenStore.saving"
              @click="ablehnen"
            >
              Ablehnen
            </AppButton>
            <AppButton
              variant="ghost"
              size="sm"
              @click="bearbeiten"
            >
              Bearbeiten
            </AppButton>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Persönliche Daten -->
          <AppCard class="lg:col-span-1" padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Persönliche Daten</h2>
            <dl class="space-y-3">
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">E-Mail</dt>
                <dd class="text-sm font-medium text-gray-900">{{ bewerbung.email || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Telefon</dt>
                <dd class="text-sm font-medium text-gray-900">{{ bewerbung.phone || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Status</dt>
                <dd class="text-sm font-medium text-gray-900">
                  <StatusBadge :status="bewerbung.status" />
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Eingegangen</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatDate(bewerbung.applied_at) }}</dd>
              </div>
              <div v-if="bewerbung.decided_at" class="flex justify-between">
                <dt class="text-sm text-gray-500">Entschieden am</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatDate(bewerbung.decided_at) }}</dd>
              </div>
            </dl>
          </AppCard>

          <!-- Finanzielle Daten -->
          <AppCard class="lg:col-span-2" padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Finanzielle &amp; Bonitätsdaten</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="bg-gray-50 rounded-xl p-4">
                <p class="text-sm text-gray-500">Monatliches Nettoeinkommen</p>
                <p class="text-xl font-bold text-[#0D3B70]">{{ formatCurrency(bewerbung.income_monthly) }}</p>
              </div>
              <div class="bg-gray-50 rounded-xl p-4">
                <p class="text-sm text-gray-500">Schufa-Score</p>
                <p class="text-xl font-bold text-[#0D3B70]">{{ bewerbung.schufa_score ?? '–' }}</p>
              </div>
            </div>

            <!-- Dokumente (JSONB-Stub) -->
            <div class="mt-6">
              <h3 class="text-sm font-medium text-gray-700 mb-2">Dokumente</h3>
              <ul v-if="(bewerbung.documents ?? []).length > 0" class="divide-y divide-gray-100">
                <li
                  v-for="(doc, index) in bewerbung.documents"
                  :key="index"
                  class="py-2 flex items-center justify-between"
                >
                  <span class="text-sm text-gray-900">{{ doc.name }}</span>
                  <a
                    v-if="doc.url"
                    :href="doc.url"
                    target="_blank"
                    class="text-sm text-[#0D3B70] hover:underline"
                  >
                    Ansehen
                  </a>
                </li>
              </ul>
              <p v-else class="text-sm text-gray-500">Keine Dokumente hinterlegt.</p>
            </div>
          </AppCard>
        </div>
      </template>

      <AppEmptyState
        v-else
        icon="🔍"
        title="Bewerbung nicht gefunden"
        description="Die gewünschte Bewerbung existiert nicht oder wurde gelöscht."
        action-label="Zur Bewerbungs-Übersicht"
        @action="$router.push('/bewerbungen')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBewerbungenStore, type Bewerbung, type BewerbungStatus } from '@/stores/bewerbungen'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'

const route = useRoute()
const bewerbungenStore = useBewerbungenStore()
const { showToast } = useToast()

const bewerbungId = computed(() => String(route.params.id))
const bewerbung = computed<Bewerbung>(() => bewerbungenStore.currentBewerbung as Bewerbung)

const openStatuses: BewerbungStatus[] = ['neu', 'in_pruefung']
const canDecide = computed(() => openStatuses.includes(bewerbung.value?.status))

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

async function annehmen(): Promise<void> {
  const confirmed = window.confirm('Bewerbung annehmen? Es wird automatisch ein Mieter und ein Mietvertrag angelegt.')
  if (!confirmed) return

  const result = await bewerbungenStore.annehmen(bewerbungId.value)
  if (result) {
    showToast('Bewerbung angenommen — Mieter und Mietvertrag wurden angelegt.', 'success')
  } else {
    showToast(bewerbungenStore.error?.message || 'Fehler beim Annehmen.', 'error')
  }
}

async function ablehnen(): Promise<void> {
  const confirmed = window.confirm('Bewerbung ablehnen?')
  if (!confirmed) return

  const result = await bewerbungenStore.ablehnen(bewerbungId.value)
  if (result) {
    showToast('Bewerbung abgelehnt.', 'success')
  } else {
    showToast(bewerbungenStore.error?.message || 'Fehler beim Ablehnen.', 'error')
  }
}

function bearbeiten(): void {
  // Phase 9: Optional Bearbeiten-Modal / Formular folgt
  showToast('Bearbeiten-Funktion folgt in Phase 9.', 'info')
}

watch(
  () => bewerbungId.value,
  () => {
    bewerbungenStore.fetchBewerbungById(bewerbungId.value)
  },
)

onMounted(() => {
  bewerbungenStore.fetchBewerbungById(bewerbungId.value)
})
</script>
