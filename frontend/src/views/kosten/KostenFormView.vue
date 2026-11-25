<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="goBack">
          ← Zurück
        </button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
          {{ isEdit ? 'Kosten bearbeiten' : 'Kosten erfassen' }}
        </h1>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Hauptformular -->
        <AppCard class="lg:col-span-2" padding="lg" shadow="md">
          <form class="space-y-5" @submit.prevent="handleSubmit">
            <AppInput
              id="name"
              v-model="form.name"
              label="Bezeichnung"
              placeholder="z. B. Müllgebühren 2026"
              required
              :error="errors.name"
            />

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <AppInput
                id="betrag"
                v-model="form.betrag"
                label="Betrag (€)"
                type="number"
                step="0.01"
                placeholder="0,00"
                required
                :error="errors.betrag"
              />
              <AppInput
                id="datum"
                v-model="form.datum"
                label="Datum"
                type="date"
                required
              />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label for="kategorie" class="block text-sm font-medium text-gray-700 mb-1">Kategorie</label>
                <select
                  id="kategorie"
                  v-model="form.kategorie_id"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                >
                  <option value="">Bitte wählen</option>
                  <option
                    v-for="kat in kostenStore.kategorien"
                    :key="kat.id"
                    :value="kat.id"
                  >
                    {{ kat.name }}
                  </option>
                </select>
              </div>

              <div>
                <label for="objekt" class="block text-sm font-medium text-gray-700 mb-1">Objekt / Einheit</label>
                <select
                  id="objekt"
                  v-model="selectedObjektEinheit"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                >
                  <option value="">Bitte wählen</option>
                  <optgroup
                    v-for="objekt in objekteStore.objekte"
                    :key="objekt.id"
                    :label="objekt.name"
                  >
                    <option :value="`objekt:${objekt.id}`">{{ objekt.name }} (Gesamt)</option>
                    <option
                      v-for="einheit in einheitenFuerObjekt(objekt.id)"
                      :key="einheit.id"
                      :value="`einheit:${einheit.id}:${objekt.id}`"
                    >
                      {{ einheit.name }}
                    </option>
                  </optgroup>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl">
                <input
                  id="umlagefaehig"
                  v-model="form.umlagefaehig"
                  type="checkbox"
                  class="w-5 h-5 text-[#0D3B70] border-gray-300 rounded focus:ring-[#0D3B70]"
                >
                <label for="umlagefaehig" class="text-sm text-gray-700">Umlagefähig</label>
              </div>

              <div>
                <label for="umlageschluessel" class="block text-sm font-medium text-gray-700 mb-1">Verteilungsschlüssel</label>
                <select
                  id="umlageschluessel"
                  v-model="form.umlageschluessel"
                  :disabled="!form.umlagefaehig"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70] disabled:bg-gray-100"
                >
                  <option v-for="opt in schluesselOptions" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label for="notizen" class="block text-sm font-medium text-gray-700 mb-1">Notizen</label>
              <textarea
                id="notizen"
                v-model="form.notizen"
                rows="3"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                placeholder="Interne Notizen zur Kostenposition …"
              />
            </div>

            <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-3 pt-4">
            <AppButton class="w-full sm:w-auto" type="button" variant="ghost" @click="goBack">
                Abbrechen
              </AppButton>
              <AppButton class="w-full sm:w-auto" type="submit" :loading="kostenStore.saving">
                {{ isEdit ? 'Änderungen speichern' : 'Kosten speichern' }}
              </AppButton>
            </div>
          </form>
        </AppCard>

        <!-- Beleg-Scan-Panel -->
        <div class="lg:col-span-1">
          <ReceiptScanPanel
            ref="scanPanel"
            v-model:scanning="kostenStore.scanLoading"
            @scan="onScan"
            @apply="onScanApply"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useKostenStore, type Kosten, type Umlageschluessel } from '@/stores/kosten'
import { useObjekteStore, type Einheit } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ReceiptScanPanel from '@/components/kosten/ReceiptScanPanel.vue'

const route = useRoute()
const router = useRouter()
const kostenStore = useKostenStore()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const kostenId = computed(() => route.params.id as string | undefined)
const isEdit = computed(() => !!kostenId.value)

const scanPanel = ref<InstanceType<typeof ReceiptScanPanel> | null>(null)

const schluesselOptions: { value: Umlageschluessel; label: string }[] = [
  { value: 'nach_qm', label: 'Nach Quadratmetern' },
  { value: 'nach_personen', label: 'Nach Personen' },
  { value: 'nach_verbrauch', label: 'Nach Verbrauch' },
  { value: 'gleich', label: 'Gleich verteilt' },
]

const form = reactive({
  name: '',
  betrag: '',
  datum: '',
  kategorie_id: '',
  objekt_id: '',
  einheit_id: '',
  umlagefaehig: true,
  umlageschluessel: 'nach_qm' as Umlageschluessel,
  notizen: '',
})

const selectedObjektEinheit = ref('')

const errors = reactive({
  name: '',
  betrag: '',
})

watch(selectedObjektEinheit, (value) => {
  form.objekt_id = ''
  form.einheit_id = ''
  if (value.startsWith('objekt:')) {
    form.objekt_id = value.replace('objekt:', '')
  } else if (value.startsWith('einheit:')) {
    const parts = value.split(':')
    if (parts.length >= 3) {
      form.einheit_id = parts[1]
      form.objekt_id = parts[2]
    }
  }
})

watch(
  () => form.umlagefaehig,
  (value) => {
    if (!value) {
      form.umlageschluessel = 'gleich'
    }
  },
)

function einheitenFuerObjekt(objektId: string): Einheit[] {
  return objekteStore.einheiten.filter((e) => e.objekt_id === objektId)
}

function populateForm(kosten: Kosten): void {
  form.name = kosten.name || ''
  form.betrag = kosten.betrag ? String(kosten.betrag) : ''
  form.datum = kosten.datum ? kosten.datum.split('T')[0] : ''
  form.kategorie_id = kosten.kategorie_id || ''
  form.umlagefaehig = kosten.umlagefaehig ?? true
  form.umlageschluessel = (kosten.umlageschluessel as Umlageschluessel) || 'nach_qm'
  form.notizen = kosten.notizen || ''
  form.objekt_id = kosten.objekt_id || ''
  form.einheit_id = kosten.einheit_id || ''

  if (kosten.einheit_id && kosten.objekt_id) {
    selectedObjektEinheit.value = `einheit:${kosten.einheit_id}:${kosten.objekt_id}`
  } else if (kosten.objekt_id) {
    selectedObjektEinheit.value = `objekt:${kosten.objekt_id}`
  } else {
    selectedObjektEinheit.value = ''
  }
}

function validate(): boolean {
  errors.name = ''
  errors.betrag = ''

  let valid = true
  if (!form.name.trim()) {
    errors.name = 'Bitte gib eine Bezeichnung ein.'
    valid = false
  }

  const betragNum = Number(form.betrag.replace(',', '.'))
  if (!form.betrag || Number.isNaN(betragNum) || betragNum <= 0) {
    errors.betrag = 'Bitte gib einen gültigen Betrag ein.'
    valid = false
  }

  return valid
}

function buildPayload(): Partial<Kosten> {
  return {
    name: form.name.trim(),
    betrag: Number(form.betrag.replace(',', '.')),
    datum: form.datum,
    kategorie_id: form.kategorie_id || undefined,
    objekt_id: form.objekt_id || undefined,
    einheit_id: form.einheit_id || undefined,
    umlagefaehig: form.umlagefaehig,
    umlageschluessel: form.umlagefaehig ? form.umlageschluessel : undefined,
    notizen: form.notizen.trim() || undefined,
  }
}

async function handleSubmit(): Promise<void> {
  if (!validate()) return

  const payload = buildPayload()

  if (isEdit.value && kostenId.value) {
    const updated = await kostenStore.updateKosten(kostenId.value, payload)
    if (updated) {
      showToast('Kosten aktualisiert.', 'success')
      router.push('/kosten')
    } else {
      showToast(kostenStore.error?.message || 'Fehler beim Speichern.', 'error')
    }
  } else {
    const created = await kostenStore.createKosten(payload)
    if (created) {
      showToast('Kosten erfasst.', 'success')
      router.push('/kosten')
    } else {
      showToast(kostenStore.error?.message || 'Fehler beim Speichern.', 'error')
    }
  }
}

async function onScan(file: File): Promise<void> {
  let result = kostenStore.simulateScanResult()

  // Wenn Backend-Endpunkt vorhanden, diesen bevorzugen
  if (isEdit.value && kostenId.value) {
    const backendResult = await kostenStore.scanReceipt(kostenId.value, file)
    if (backendResult) {
      result = backendResult
    }
  }

  scanPanel.value?.setScanResult(result)
}

function onScanApply(scanResult: { betrag_vorschlag?: number; kategorie_vorschlag?: string; umlagefaehig_vorschlag?: boolean; umlageschluessel_vorschlag?: Umlageschluessel | string }): void {
  if (scanResult.betrag_vorschlag != null) {
    form.betrag = String(scanResult.betrag_vorschlag)
  }
  if (scanResult.kategorie_vorschlag) {
    const kategorie = kostenStore.kategorien.find(
      (k) => (k.name ?? k.bezeichnung ?? '').toLowerCase() === scanResult.kategorie_vorschlag?.toLowerCase(),
    )
    form.kategorie_id = kategorie?.id || ''
  }
  if (scanResult.umlagefaehig_vorschlag != null) {
    form.umlagefaehig = scanResult.umlagefaehig_vorschlag
  }
  if (scanResult.umlageschluessel_vorschlag) {
    form.umlageschluessel = scanResult.umlageschluessel_vorschlag as Umlageschluessel
  }
  showToast('Scan-Vorschlag übernommen.', 'info')
}

function goBack(): void {
  router.push('/kosten')
}

onMounted(async () => {
  await Promise.all([
    kostenStore.fetchKategorien(),
    objekteStore.fetchObjekte(),
  ])

  for (const objekt of objekteStore.objekte) {
    await objekteStore.fetchEinheiten(objekt.id)
  }

  if (isEdit.value && kostenId.value) {
    const kosten = await kostenStore.fetchKostenById(kostenId.value)
    if (kosten) {
      populateForm(kosten)
    }
  } else {
    form.datum = new Date().toISOString().split('T')[0]
  }
})
</script>
