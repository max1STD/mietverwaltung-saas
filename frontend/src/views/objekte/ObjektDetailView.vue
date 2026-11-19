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
              <p class="text-gray-500">
                Nr. {{ objekteStore.currentObjekt.public_id || '–' }} · {{ formatAddress(objekteStore.currentObjekt) }}
              </p>
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
                <dt class="text-sm text-gray-500">Zustand</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.zustand || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Bauweise</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.bauweise || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Baujahr</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.baujahr || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Anzahl Einheiten</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.anzahl_einheiten || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Wohnfläche gesamt</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatQm(objekteStore.currentObjekt.wohnflaeche_gesamt_qm) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Vermietbare Fläche</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatQm(objekteStore.currentObjekt.vermietbare_flaeche_qm) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Energieklasse</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.energieverbrauch_klasse || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Heizungsart</dt>
                <dd class="text-sm font-medium text-gray-900">{{ objekteStore.currentObjekt.heizungsart || '–' }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Denkmalschutz</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatBool(objekteStore.currentObjekt.denkmalschutz) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Kaufpreis</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(objekteStore.currentObjekt.kaufpreis) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Kaufdatum</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatDate(objekteStore.currentObjekt.kaufdatum) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Gesamtmiete IST</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(objekteStore.currentObjekt.gesamtmiete_ist) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500">Gesamtmiete SOLL</dt>
                <dd class="text-sm font-medium text-gray-900">{{ formatCurrency(objekteStore.currentObjekt.gesamtmiete_soll) }}</dd>
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
                <td class="py-3 px-4 text-sm text-gray-500 cursor-pointer" @click="$router.push(`/einheiten/${item.public_id || item.id}`)">
                  {{ item.public_id || '–' }}
                </td>
                <td class="py-3 px-4 font-medium text-gray-900 cursor-pointer hover:text-[#0D3B70]" @click="$router.push(`/einheiten/${item.public_id || item.id}`)">
                  {{ item.name }}
                </td>
                <td class="py-3 px-4 text-sm text-gray-600 cursor-pointer" @click="$router.push(`/einheiten/${item.public_id || item.id}`)">{{ item.etage ?? '–' }}</td>
                <td class="py-3 px-4 text-sm text-gray-600 cursor-pointer" @click="$router.push(`/einheiten/${item.public_id || item.id}`)">{{ item.wohnflaeche_qm ? `${item.wohnflaeche_qm} m²` : '–' }}</td>
                <td class="py-3 px-4 text-sm text-gray-600 cursor-pointer" @click="$router.push(`/einheiten/${item.public_id || item.id}`)">{{ formatCurrency(item.kaltmiete) }}</td>
                <td class="py-3 px-4 cursor-pointer" @click="$router.push(`/einheiten/${item.public_id || item.id}`)">
                  <AppBadge :variant="badgeForStatus(item.status)">{{ item.status || 'frei' }}</AppBadge>
                </td>
                <td class="py-3 px-4 text-right">
                  <AppButton size="sm" variant="ghost" @click="editEinheit(item)">
                    ✎
                  </AppButton>
                </td>
              </template>
            </AppTable>
          </AppCard>
        </div>

        <!-- Dokumente -->
        <AppCard class="mt-6" padding="md" shadow="md">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Dokumente</h2>
          <DokumenteListe
            v-if="objekteStore.currentObjekt"
            entity-type="objekt"
            :entity-id="Number(objekteStore.currentObjekt.id)"
          />
        </AppCard>
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
    <AppModal v-model="showAddEinheit" :title="editingEinheit ? 'Wohneinheit bearbeiten' : 'Neue Wohneinheit'">
      <form class="space-y-4" @submit.prevent="saveEinheit">
        <AppInput
          id="einheit-name"
          v-model="einheitForm.name"
          label="Bezeichnung"
          placeholder="z. B. Wohnung 1"
          required
          :error="einheitErrors.name"
        />
        <div class="grid grid-cols-2 gap-4">
          <AppInput
            id="einheit-etage"
            v-model="einheitForm.etage"
            label="Etage"
            type="number"
            placeholder="0"
            :error="einheitErrors.etage"
          />
          <AppInput
            id="einheit-wohnflaeche"
            v-model="einheitForm.wohnflaeche_qm"
            label="Wohnfläche (m²)"
            type="number"
            placeholder="75"
            :error="einheitErrors.wohnflaeche_qm"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <AppInput
            id="einheit-kaltmiete"
            v-model="einheitForm.kaltmiete"
            label="Kaltmiete (€)"
            type="number"
            placeholder="800"
            :error="einheitErrors.kaltmiete"
          />
          <AppInput
            id="einheit-nebenkosten"
            v-model="einheitForm.nebenkosten_vorschuss"
            label="NK-Vorschuss (€)"
            type="number"
            placeholder="150"
            :error="einheitErrors.nebenkosten_vorschuss"
          />
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <AppButton type="button" variant="ghost" @click="closeEinheitModal">
            Abbrechen
          </AppButton>
          <AppButton type="submit" :loading="objekteStore.saving">
            {{ editingEinheit ? 'Änderungen speichern' : 'Einheit speichern' }}
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
import DokumenteListe from '@/components/dokumente/DokumenteListe.vue'

const route = useRoute()
const router = useRouter()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const objektId = computed(() => String(route.params.id))
const showAddEinheit = ref(false)
const editingEinheit = ref<Einheit | null>(null)

const einheitForm = reactive({
  name: '',
  etage: '',
  wohnflaeche_qm: '',
  kaltmiete: '',
  nebenkosten_vorschuss: '',
})

const einheitColumns = [
  { key: 'public_id', label: 'Nr.' },
  { key: 'name', label: 'Bezeichnung' },
  { key: 'etage', label: 'Etage' },
  { key: 'wohnflaeche_qm', label: 'Fläche' },
  { key: 'kaltmiete', label: 'Kaltmiete' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: '' },
]

const einheitErrors = reactive({
  name: '',
  etage: '',
  wohnflaeche_qm: '',
  kaltmiete: '',
  nebenkosten_vorschuss: '',
})

function clearEinheitErrors(): void {
  einheitErrors.name = ''
  einheitErrors.etage = ''
  einheitErrors.wohnflaeche_qm = ''
  einheitErrors.kaltmiete = ''
  einheitErrors.nebenkosten_vorschuss = ''
}

function mapEinheitApiErrors(details?: Record<string, string[]>): void {
  clearEinheitErrors()
  if (!details) return
  for (const [field, messages] of Object.entries(details)) {
    const target = field as keyof typeof einheitErrors
    if (target in einheitErrors && messages.length > 0) {
      einheitErrors[target] = messages.join('. ')
    }
  }
}

function validateEinheit(): boolean {
  clearEinheitErrors()
  let valid = true
  if (!einheitForm.name.trim()) {
    einheitErrors.name = 'Bezeichnung ist erforderlich.'
    valid = false
  }
  return valid
}

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

function formatQm(value?: number | string | null): string {
  if (value == null || value === '') return '–'
  return `${new Intl.NumberFormat('de-DE').format(Number(value))} m²`
}

function formatBool(value?: boolean | null): string {
  if (value === true) return 'Ja'
  if (value === false) return 'Nein'
  return '–'
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

function editEinheit(einheit: Einheit): void {
  editingEinheit.value = einheit
  einheitForm.name = einheit.name
  einheitForm.etage = einheit.etage != null ? String(einheit.etage) : ''
  einheitForm.wohnflaeche_qm = einheit.wohnflaeche_qm != null ? String(einheit.wohnflaeche_qm) : ''
  einheitForm.kaltmiete = einheit.kaltmiete != null ? String(einheit.kaltmiete) : ''
  einheitForm.nebenkosten_vorschuss = einheit.nebenkosten_vorschuss != null ? String(einheit.nebenkosten_vorschuss) : ''
  showAddEinheit.value = true
}

function closeEinheitModal(): void {
  showAddEinheit.value = false
  editingEinheit.value = null
  resetEinheitForm()
  clearEinheitErrors()
}

async function saveEinheit(): Promise<void> {
  if (!validateEinheit()) return

  const payload: Partial<Einheit> = {
    name: einheitForm.name,
    etage: einheitForm.etage ? Number(einheitForm.etage) : undefined,
    wohnflaeche_qm: einheitForm.wohnflaeche_qm ? Number(einheitForm.wohnflaeche_qm) : undefined,
    kaltmiete: einheitForm.kaltmiete ? Number(einheitForm.kaltmiete) : undefined,
    nebenkosten_vorschuss: einheitForm.nebenkosten_vorschuss
      ? Number(einheitForm.nebenkosten_vorschuss)
      : undefined,
  }

  if (editingEinheit.value) {
    const updated = await objekteStore.updateEinheit(editingEinheit.value.id, payload)
    if (updated) {
      showToast('Wohneinheit aktualisiert.', 'success')
      closeEinheitModal()
    } else {
      mapEinheitApiErrors(objekteStore.error?.details)
      showToast(objekteStore.error?.message || 'Fehler beim Aktualisieren.', 'error')
    }
  } else {
    const einheit = await objekteStore.createEinheit(objektId.value, payload)
    if (einheit) {
      showToast('Wohneinheit hinzugefügt.', 'success')
      closeEinheitModal()
    } else {
      mapEinheitApiErrors(objekteStore.error?.details)
      showToast(objekteStore.error?.message || 'Fehler beim Speichern.', 'error')
    }
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
