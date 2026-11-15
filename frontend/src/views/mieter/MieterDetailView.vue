<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div v-if="mieterStore.loading" class="py-12 text-center text-gray-500">
        Mieter wird geladen …
      </div>

      <template v-else-if="mieterStore.currentMieter">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <button class="text-gray-500 hover:text-[#0D3B70]" @click="$router.push('/mieter')">
              ← Zurück
            </button>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">{{ mieterStore.currentMieter.name }}</h1>
              <p class="text-gray-500">{{ mieterStore.currentMieter.email || 'Keine E-Mail' }}</p>
            </div>
          </div>
          <AppButton
            variant="secondary"
            @click="$router.push(`/mieter/${mieterId}/bearbeiten`)"
          >
            Mieter bearbeiten
          </AppButton>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Stammdaten -->
          <AppCard class="lg:col-span-1" padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Stammdaten</h2>
            <dl class="space-y-3">
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Telefon</dt>
                <dd class="text-sm font-medium text-gray-900">{{ mieterStore.currentMieter.telefon || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Geburtsdatum</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatDate(mieterStore.currentMieter.geburtsdatum) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Adresse(n)</dt>
                <dd class="text-sm font-medium text-gray-900 text-right">
                  <span v-if="!mieterStore.currentMieter.adressen?.length">–</span>
                  <div v-else class="space-y-1">
                    <div v-for="a in mieterStore.currentMieter.adressen" :key="a.id">
                      {{ a.strasse }} {{ a.hausnummer }}, {{ a.plz }} {{ a.ort }}
                      <span v-if="a.is_primary" class="ml-1 text-[#0D3B70]">(Primär)</span>
                    </div>
                  </div>
                </dd>
              </div>
            </dl>
            <div v-if="mieterStore.currentMieter.notizen" class="mt-6">
              <h3 class="text-sm font-medium text-gray-700 mb-1">Notizen</h3>
              <p class="text-sm text-gray-600">{{ mieterStore.currentMieter.notizen }}</p>
            </div>
          </AppCard>

          <!-- Mietvertrag -->
          <AppCard class="lg:col-span-2" padding="md" shadow="md">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-[#0D3B70]">Mietvertrag</h2>
              <AppButton
                v-if="!mietvertrag"
                size="sm"
                @click="showCreateVertrag = true"
              >
                + Vertrag anlegen
              </AppButton>
            </div>

            <div v-if="mietvertraegeStore.loading" class="py-8 text-center text-gray-500">
              Vertragsdaten werden geladen …
            </div>

            <AppEmptyState
              v-else-if="!mietvertrag"
              icon="📄"
              title="Kein aktiver Mietvertrag"
              description="Diesem Mieter ist aktuell kein Mietvertrag zugeordnet."
              action-label="Vertrag anlegen"
              @action="showCreateVertrag = true"
            />

            <template v-else>
              <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <dt class="text-sm text-gray-500">Objekt / Einheit</dt>
                  <dd class="text-sm font-medium text-gray-900">
                    {{ mietvertrag.objekt?.bezeichnung || '–' }} · {{ mietvertrag.einheit?.bezeichnung || '–' }}
                  </dd>
                </div>
                <div>
                  <dt class="text-sm text-gray-500">Status</dt>
                  <dd class="text-sm font-medium text-gray-900">
                    <AppBadge :variant="badgeForVertragStatus(mietvertrag.status)">
                      {{ mietvertrag.status || 'aktiv' }}
                    </AppBadge>
                  </dd>
                </div>
                <div>
                  <dt class="text-sm text-gray-500">Mietbeginn</dt>
                  <dd class="text-sm font-medium text-gray-900">{{ formatDate(mietvertrag.mietbeginn) }}</dd>
                </div>
                <div>
                  <dt class="text-sm text-gray-500">Kaltmiete</dt>
                  <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(mietvertrag.kaltmiete) }}</dd>
                </div>
                <div>
                  <dt class="text-sm text-gray-500">NK-Vorschuss</dt>
                  <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(mietvertrag.nebenkosten_vorschuss) }}</dd>
                </div>
                <div>
                  <dt class="text-sm text-gray-500">Kaution</dt>
                  <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(mietvertrag.kaution) }}</dd>
                </div>
              </dl>
            </template>
          </AppCard>
        </div>
      </template>

      <AppEmptyState
        v-else
        icon="🔍"
        title="Mieter nicht gefunden"
        description="Der gewünschte Mieter existiert nicht oder wurde gelöscht."
        action-label="Zur Mieter-Übersicht"
        @action="$router.push('/mieter')"
      />
    </div>

    <!-- Modal: Mietvertrag anlegen -->
    <AppModal v-model="showCreateVertrag" title="Mietvertrag anlegen">
      <form class="space-y-4" @submit.prevent="createVertrag">
        <AppInput
          id="vertrag-einheit-id"
          v-model="vertragForm.einheit_id"
          label="Einheit-ID"
          placeholder="ID der Wohneinheit"
          required
        />
        <AppInput
          id="vertrag-mietbeginn"
          v-model="vertragForm.mietbeginn"
          label="Mietbeginn"
          type="date"
          required
        />
        <AppInput
          id="vertrag-kaltmiete"
          v-model="vertragForm.kaltmiete"
          label="Kaltmiete (€)"
          type="number"
          placeholder="800"
          required
        />
        <AppInput
          id="vertrag-nebenkosten"
          v-model="vertragForm.nebenkosten_vorschuss"
          label="NK-Vorschuss (€)"
          type="number"
          placeholder="150"
        />
        <AppInput
          id="vertrag-kaution"
          v-model="vertragForm.kaution"
          label="Kaution (€)"
          type="number"
          placeholder="1600"
        />

        <div class="flex justify-end gap-3 pt-2">
          <AppButton type="button" variant="ghost" @click="showCreateVertrag = false">
            Abbrechen
          </AppButton>
          <AppButton type="submit" :loading="mietvertraegeStore.saving">
            Vertrag speichern
          </AppButton>
        </div>
      </form>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMieterStore, type Mieter } from '@/stores/mieter'
import { useMietvertraegeStore, type Mietvertrag } from '@/stores/mietvertraege'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'

const route = useRoute()
const mieterStore = useMieterStore()
const mietvertraegeStore = useMietvertraegeStore()
const { showToast } = useToast()

const mieterId = computed(() => String(route.params.id))
const mietvertraege = ref<Mietvertrag[]>([])
const showCreateVertrag = ref(false)

const mietvertrag = computed(() => mietvertraege.value.find((v) => v.mieter_id === mieterId.value))

const vertragForm = reactive({
  einheit_id: '',
  mietbeginn: '',
  kaltmiete: '',
  nebenkosten_vorschuss: '',
  kaution: '',
})

function formatDate(value?: string): string {
  if (!value) return '–'
  return new Date(value).toLocaleDateString('de-DE')
}

function formatCurrency(value?: number | string): string {
  if (value == null || value === '') return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(Number(value))
}

function badgeForVertragStatus(status?: string): 'green' | 'yellow' | 'red' | 'gray' {
  switch (status) {
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

async function loadVertraege(): Promise<void> {
  const data = await mietvertraegeStore.fetchMietvertraegeByMieter(mieterId.value)
  mietvertraege.value = data
}

async function createVertrag(): Promise<void> {
  if (!vertragForm.einheit_id.trim() || !vertragForm.mietbeginn || !vertragForm.kaltmiete) {
    showToast('Bitte fülle alle Pflichtfelder aus.', 'warning')
    return
  }

  const payload: Partial<Mietvertrag> = {
    mieter_id: mieterId.value,
    einheit_id: vertragForm.einheit_id,
    mietbeginn: vertragForm.mietbeginn,
    kaltmiete: Number(vertragForm.kaltmiete),
    nebenkosten_vorschuss: vertragForm.nebenkosten_vorschuss ? Number(vertragForm.nebenkosten_vorschuss) : undefined,
    kaution: vertragForm.kaution ? Number(vertragForm.kaution) : undefined,
  }

  const created = await mietvertraegeStore.createMietvertrag(payload)
  if (created) {
    showToast('Mietvertrag angelegt.', 'success')
    showCreateVertrag.value = false
    await loadVertraege()
  } else {
    showToast(mietvertraegeStore.error?.message || 'Fehler beim Anlegen.', 'error')
  }
}

watch(
  () => mieterId.value,
  () => {
    mieterStore.fetchMieterById(mieterId.value)
    loadVertraege()
  },
)

onMounted(() => {
  mieterStore.fetchMieterById(mieterId.value)
  loadVertraege()
})
</script>
