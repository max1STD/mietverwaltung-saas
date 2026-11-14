<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Ladezustand -->
      <div v-if="objekteStore.loading" class="py-12 text-center text-gray-500">
        Objekt wird geladen …
      </div>

      <template v-else-if="objekteStore.currentObjekt">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <button
              class="text-gray-500 hover:text-[#0D3B70]"
              @click="$router.push('/objekte')"
            >
              ← Zurück
            </button>
            <div>
              <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
                {{ objekteStore.currentObjekt.name }}
              </h1>
              <p class="text-gray-500">{{ formatAddress(objekteStore.currentObjekt) }}</p>
            </div>
          </div>
          <AppButton
            variant="secondary"
            @click="$router.push(`/objekte/${objektId}/bearbeiten`)"
          >
            Objekt bearbeiten
          </AppButton>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Details -->
          <AppCard class="lg:col-span-1" padding="md" shadow="md">
            <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Details</h2>
            <dl class="space-y-3">
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Typ</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.typ || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Baujahr</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.baujahr || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Kaufpreis</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(objekteStore.currentObjekt.kaufpreis) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Kaufdatum</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatDate(objekteStore.currentObjekt.kaufdatum) }}</dd>
              </div>
            </dl>
            <div v-if="objekteStore.currentObjekt.notizen" class="mt-6">
              <h3 class="text-sm font-medium text-gray-700 mb-1">Notizen</h3>
              <p class="text-sm text-gray-600">{{ objekteStore.currentObjekt.notizen }}</p>
            </div>
          </AppCard>

          <!-- Wohneinheiten -->
          <AppCard class="lg:col-span-2" padding="none" shadow="md">
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h2 class="text-lg font-semibold text-[#0D3B70]">Wohneinheiten</h2>
              <AppButton size="sm" @click="showAddEinheit = true">
                + Einheit
              </AppButton>
            </div>

            <AppEmptyState
              v-if="objekteStore.einheiten.length === 0"
              icon="🏢"
              title="Noch keine Einheiten"
              description="Füge Wohnungen, Büros oder andere Einheiten zu diesem Objekt hinzu."
              action-label="Einheit hinzufügen"
              @action="showAddEinheit = true"
            />

            <AppTable v-else :items="objekteStore.einheiten" :columns="einheitColumns">
              <template #row="{ item }">
                <td class="py-3 px-4 font-medium text-gray-900">{{ item.name }}</td>
                <td class="py-3 px-4 text-sm text-gray-600">{{ item.etage ?? '–' }}</td>
                <td class="py-3 px-4 text-sm text-gray-600">{{ item.wohnflaeche_qm ? `${item.wohnflaeche_qm} m²` : '–' }}</td>
                <td class="py-3 px-4 text-sm text-gray-600">{{ formatCurrency(item.kaltmiete) }}</td>
                <td class="py-3 px-4">
                  <AppBadge :variant="badgeForStatus(item.status)">{{ item.status || 'frei' }}</AppBadge>
                </td>
              </template>
            </AppTable>
          </AppCard>
        </div>
      </template>

      <!-- Objekt nicht gefunden -->
      <AppEmptyState
        v-else
        icon="🔍"
        title="Objekt nicht gefunden"
        description="Das gewünschte Objekt existiert nicht oder wurde gelöscht."
        action-label="Zur Objekt-Übersicht"
        @action="$router.push('/objekte')"
      />
    </div>

    <!-- Modal: Neue Einheit -->
    <AppModal v-model="showAddEinheit" title="Neue Wohneinheit">
      <form class="space-y-4" @submit.prevent="addEinheit">
        <AppInput
          id="einheit-name"
          v-model="einheitForm.name"
          label="Bezeichnung"
          placeholder="z. B. Wohnung 1"
          required
        />
        <div class="grid grid-cols-2 gap-4">
          <AppInput
            id="einheit-etage"
            v-model="einheitForm.etage"
            label="Etage"
            type="number"
            placeholder="0"
          />
          <AppInput
            id="einheit-wohnflaeche"
            v-model="einheitForm.wohnflaeche_qm"
            label="Wohnfläche (m²)"
            type="number"
            placeholder="75"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <AppInput
            id="einheit-kaltmiete"
            v-model="einheitForm.kaltmiete"
            label="Kaltmiete (€)"
            type="number"
            placeholder="800"
          />
          <AppInput
            id="einheit-nebenkosten"
            v-model="einheitForm.nebenkosten_vorschuss"
            label="NK-Vorschuss (€)"
            type="number"
            placeholder="150"
          />
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <AppButton type="button" variant="ghost" @click="showAddEinheit = false">
            Abbrechen
          </AppButton>
          <AppButton type="submit" :loading="objekteStore.saving">
            Einheit speichern
          </AppButton>
        </div>
      </form>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObjekteStore, type Objekt, type Einheit } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'

const route = useRoute()
const router = useRouter()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const objektId = computed(() => String(route.params.id))
const showAddEinheit = ref(false)

const einheitForm = reactive({
  name: '',
  etage: '',
  wohnflaeche_qm: '',
  kaltmiete: '',
  nebenkosten_vorschuss: '',
})

const einheitColumns = [
  { key: 'name', label: 'Bezeichnung' },
  { key: 'etage', label: 'Etage' },
  { key: 'wohnflaeche_qm', label: 'Fläche' },
  { key: 'kaltmiete', label: 'Kaltmiete' },
  { key: 'status', label: 'Status' },
]

function formatAddress(objekt: Objekt): string {
  const parts = [objekt.address, [objekt.plz, objekt.ort].filter(Boolean).join(' ')]
  return parts.filter(Boolean).join(', ') || 'Keine Adresse'
}

function formatCurrency(value?: number | string | null): string {
  if (value == null || value === '') return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(Number(value))
}

function formatDate(value?: string | number | null): string {
  if (!value || value === '') return '–'
  return new Date(value).toLocaleDateString('de-DE')
}

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

async function addEinheit(): Promise<void> {
  if (!einheitForm.name.trim()) {
    showToast('Bitte gib eine Bezeichnung ein.', 'warning')
    return
  }

  const payload: Partial<Einheit> = {
    name: einheitForm.name,
    etage: einheitForm.etage ? Number(einheitForm.etage) : undefined,
    wohnflaeche_qm: einheitForm.wohnflaeche_qm ? Number(einheitForm.wohnflaeche_qm) : undefined,
    kaltmiete: einheitForm.kaltmiete ? Number(einheitForm.kaltmiete) : undefined,
    nebenkosten_vorschuss: einheitForm.nebenkosten_vorschuss
      ? Number(einheitForm.nebenkosten_vorschuss)
      : undefined,
  }

  const einheit = await objekteStore.createEinheit(objektId.value, payload)
  if (einheit) {
    showToast('Wohneinheit hinzugefügt.', 'success')
    showAddEinheit.value = false
    resetEinheitForm()
  } else {
    showToast(objekteStore.error?.message || 'Fehler beim Speichern.', 'error')
  }
}

function resetEinheitForm(): void {
  einheitForm.name = ''
  einheitForm.etage = ''
  einheitForm.wohnflaeche_qm = ''
  einheitForm.kaltmiete = ''
  einheitForm.nebenkosten_vorschuss = ''
}

onMounted(async () => {
  await objekteStore.fetchObjekt(objektId.value)
  if (objekteStore.currentObjekt) {
    await objekteStore.fetchEinheiten(objektId.value)
  }
})
</script>
