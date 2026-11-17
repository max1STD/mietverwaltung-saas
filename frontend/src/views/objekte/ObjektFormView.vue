<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="goBack">
          ← Zurück
        </button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
          {{ isEdit ? 'Objekt bearbeiten' : 'Neues Objekt' }}
        </h1>
      </div>

      <AppCard padding="lg" shadow="md">
        <form class="space-y-5" @submit.prevent="handleSubmit">
          <AppInput
            id="name"
            v-model="form.name"
            label="Bezeichnung"
            placeholder="z. B. Musterstraße 12"
            required
            :error="errors.name"
          />

          <AppInput
            id="address"
            v-model="form.address"
            label="Adresse"
            placeholder="Straße und Hausnummer"
            :error="errors.address"
            @input="debouncedStreetSearch"
          />

          <!-- Straßen-Autocomplete-Vorschläge -->
          <ul
            v-if="streetSuggestions.length > 0"
            class="-mt-2 mb-2 bg-white border border-gray-200 rounded-xl shadow-sm max-h-48 overflow-auto"
          >
            <li
              v-for="(suggestion, index) in streetSuggestions"
              :key="index"
              class="px-4 py-2 text-sm text-gray-700 hover:bg-[#0D3B70]/5 cursor-pointer"
              @click="selectStreet(suggestion)"
            >
              {{ suggestion }}
            </li>
          </ul>

          <div class="grid grid-cols-2 gap-4">
            <AppInput
              id="plz"
              v-model="form.plz"
              label="PLZ"
              placeholder="12345"
              maxlength="5"
              inputmode="numeric"
              :error="errors.plz"
              @blur="lookupOrt"
            />
            <AppInput
              id="ort"
              v-model="form.ort"
              label="Ort"
              placeholder="Berlin"
              :error="errors.ort"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="typ" class="block text-sm font-medium text-gray-700 mb-1">Typ</label>
              <select
                id="typ"
                v-model="form.typ"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                :class="{ 'border-red-500': errors.typ }"
              >
                <option value="">Bitte wählen</option>
                <option v-for="option in typOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <p v-if="errors.typ" class="mt-1 text-xs text-red-600">{{ errors.typ }}</p>
            </div>

            <AppInput
              id="baujahr"
              v-model="form.baujahr"
              label="Baujahr"
              type="number"
              placeholder="1990"
              :error="errors.baujahr"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <AppCurrencyInput
              id="kaufpreis"
              v-model="form.kaufpreis"
              label="Kaufpreis"
              placeholder="250.000,00"
              :error="errors.kaufpreis"
            />
            <AppInput
              id="kaufdatum"
              v-model="form.kaufdatum"
              label="Kaufdatum"
              type="date"
              :error="errors.kaufdatum"
            />
          </div>

          <div>
            <label for="notizen" class="block text-sm font-medium text-gray-700 mb-1">Notizen</label>
            <textarea
              id="notizen"
              v-model="form.notizen"
              rows="4"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              :class="{ 'border-red-500': errors.notizen }"
              placeholder="Interne Notizen …"
            ></textarea>
            <p v-if="errors.notizen" class="mt-1 text-xs text-red-600">{{ errors.notizen }}</p>
          </div>

          <div class="flex items-center justify-end gap-3 pt-4">
            <AppButton type="button" variant="ghost" @click="goBack">
              Abbrechen
            </AppButton>
            <AppButton type="submit" :loading="objekteStore.saving">
              {{ isEdit ? 'Änderungen speichern' : 'Objekt anlegen' }}
            </AppButton>
          </div>
        </form>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObjekteStore, type Objekt, type ObjektTyp } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import apiClient from '@/api/client'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppCurrencyInput from '@/components/ui/AppCurrencyInput.vue'

const route = useRoute()
const router = useRouter()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const objektId = computed(() => route.params.id as string | undefined)
const isEdit = computed(() => !!objektId.value)

const typOptions: { value: ObjektTyp | ''; label: string }[] = [
  { value: 'einfamilienhaus', label: 'Einfamilienhaus' },
  { value: 'mehrfamilienhaus', label: 'Mehrfamilienhaus' },
  { value: 'doppelhaushaelfte', label: 'Doppelhaushälfte' },
  { value: 'reihenhaus', label: 'Reihenhaus' },
  { value: 'gewerbe', label: 'Gewerbe' },
  { value: 'grundstueck', label: 'Grundstück' },
  { value: 'sonstiges', label: 'Sonstiges' },
]

const form = reactive({
  name: '',
  address: '',
  plz: '',
  ort: '',
  typ: '' as ObjektTyp | '',
  baujahr: '',
  kaufpreis: '',
  kaufdatum: '',
  notizen: '',
})

const errors = reactive({
  name: '',
  address: '',
  plz: '',
  ort: '',
  typ: '',
  baujahr: '',
  kaufpreis: '',
  kaufdatum: '',
  notizen: '',
})

function clearErrors(): void {
  errors.name = ''
  errors.address = ''
  errors.plz = ''
  errors.ort = ''
  errors.typ = ''
  errors.baujahr = ''
  errors.kaufpreis = ''
  errors.kaufdatum = ''
  errors.notizen = ''
}

function mapApiErrors(details?: Record<string, string[]>): void {
  clearErrors()
  if (!details) return
  for (const [field, messages] of Object.entries(details)) {
    const target = field as keyof typeof errors
    if (target in errors && messages.length > 0) {
      errors[target] = messages.join('. ')
    }
  }
}

const streetSuggestions = ref<string[]>([])
let streetSearchTimeout: ReturnType<typeof setTimeout> | null = null

function populateForm(objekt: Objekt): void {
  form.name = objekt.name
  form.address = objekt.address || ''
  form.plz = objekt.plz || ''
  form.ort = objekt.ort || ''
  form.typ = (objekt.typ as ObjektTyp) || ''
  form.baujahr = objekt.baujahr ? String(objekt.baujahr) : ''
  form.kaufpreis = objekt.kaufpreis ? String(objekt.kaufpreis) : ''
  form.kaufdatum = objekt.kaufdatum || ''
  form.notizen = objekt.notizen || ''
}

async function lookupOrt(): Promise<void> {
  const plz = form.plz.trim()
  if (plz.length !== 5 || !/^\d{5}$/.test(plz)) return

  try {
    const { data } = await apiClient.get<{ plz: string; orte: string[] }>(`/geo/plz/${plz}`)
    if (data.orte.length === 1) {
      form.ort = data.orte[0]
    }
  } catch {
    // Offline-Fallback: Eingabe bleibt erhalten.
  }
}

function debouncedStreetSearch(): void {
  if (streetSearchTimeout) {
    clearTimeout(streetSearchTimeout)
  }
  streetSearchTimeout = setTimeout(() => {
    searchStreets()
  }, 300)
}

async function searchStreets(): Promise<void> {
  const q = form.address.trim()
  const plz = form.plz.trim()
  const ort = form.ort.trim()
  if (!q || q.length < 2) {
    streetSuggestions.value = []
    return
  }

  try {
    const params: Record<string, string> = { q }
    if (plz) params.plz = plz
    if (ort) params.ort = ort
    const { data } = await apiClient.get<{ strassen: string[] }>('/geo/strassen', { params })
    streetSuggestions.value = data.strassen
  } catch {
    streetSuggestions.value = []
  }
}

function selectStreet(street: string): void {
  form.address = street
  streetSuggestions.value = []
}

function validate(): boolean {
  clearErrors()

  let valid = true
  if (!form.name.trim()) {
    errors.name = 'Bitte gib eine Bezeichnung ein.'
    valid = false
  }

  if (form.plz && !/^\d{5}$/.test(form.plz)) {
    errors.plz = 'PLZ muss aus 5 Ziffern bestehen.'
    valid = false
  }

  if (form.baujahr) {
    const year = Number(form.baujahr)
    const currentYear = new Date().getFullYear()
    if (Number.isNaN(year) || year < 1500 || year > currentYear + 5) {
      errors.baujahr = `Baujahr muss zwischen 1500 und ${currentYear + 5} liegen.`
      valid = false
    }
  }

  if (form.kaufpreis) {
    const price = Number(form.kaufpreis)
    if (Number.isNaN(price) || price < 0) {
      errors.kaufpreis = 'Kaufpreis darf nicht negativ sein.'
      valid = false
    }
  }

  return valid
}

function buildPayload(): Partial<Objekt> {
  return {
    name: form.name.trim(),
    address: form.address.trim() || undefined,
    plz: form.plz.trim() || undefined,
    ort: form.ort.trim() || undefined,
    typ: form.typ || undefined,
    baujahr: form.baujahr ? Number(form.baujahr) : undefined,
    kaufpreis: form.kaufpreis ? Number(form.kaufpreis) : undefined,
    kaufdatum: form.kaufdatum || undefined,
    notizen: form.notizen.trim() || undefined,
  }
}

async function handleSubmit(): Promise<void> {
  clearErrors()
  if (!validate()) return

  const payload = buildPayload()

  if (isEdit.value && objektId.value) {
    const updated = await objekteStore.updateObjekt(objektId.value, payload)
    if (updated) {
      showToast('Objekt aktualisiert.', 'success')
      router.push(`/objekte/${updated.public_id || updated.id}`)
    } else {
      mapApiErrors(objekteStore.error?.details)
      showToast(objekteStore.error?.message || 'Fehler beim Speichern.', 'error')
    }
  } else {
    const created = await objekteStore.createObjekt(payload)
    if (created) {
      showToast('Objekt erfolgreich angelegt.', 'success')
      router.push(`/objekte/${created.public_id || created.id}`)
    } else {
      mapApiErrors(objekteStore.error?.details)
      showToast(objekteStore.error?.message || 'Fehler beim Anlegen.', 'error')
    }
  }
}

function goBack(): void {
  if (isEdit.value && objektId.value) {
    router.push(`/objekte/${objektId.value}`)
  } else {
    router.push('/objekte')
  }
}

onMounted(async () => {
  if (isEdit.value && objektId.value) {
    const objekt = await objekteStore.fetchObjekt(objektId.value)
    if (objekt) {
      populateForm(objekt)
    }
  }
})
</script>
