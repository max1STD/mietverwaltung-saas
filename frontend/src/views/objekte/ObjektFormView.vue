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
          />

          <div class="grid grid-cols-2 gap-4">
            <AppInput
              id="plz"
              v-model="form.plz"
              label="PLZ"
              placeholder="12345"
              maxlength="5"
              inputmode="numeric"
            />
            <AppInput
              id="ort"
              v-model="form.ort"
              label="Ort"
              placeholder="Berlin"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="typ" class="block text-sm font-medium text-gray-700 mb-1">Typ</label>
              <select
                id="typ"
                v-model="form.typ"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="">Bitte wählen</option>
                <option v-for="option in typOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <AppInput
              id="baujahr"
              v-model="form.baujahr"
              label="Baujahr"
              type="number"
              placeholder="1990"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <AppInput
              id="kaufpreis"
              v-model="form.kaufpreis"
              label="Kaufpreis (€)"
              type="number"
              placeholder="250000"
            />
            <AppInput
              id="kaufdatum"
              v-model="form.kaufdatum"
              label="Kaufdatum"
              type="date"
            />
          </div>

          <div>
            <label for="notizen" class="block text-sm font-medium text-gray-700 mb-1">Notizen</label>
            <textarea
              id="notizen"
              v-model="form.notizen"
              rows="4"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              placeholder="Interne Notizen zum Objekt …"
            />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObjekteStore, type Objekt, type ObjektTyp } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

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
})

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

function validate(): boolean {
  errors.name = ''
  errors.address = ''

  let valid = true
  if (!form.name.trim()) {
    errors.name = 'Bitte gib eine Bezeichnung ein.'
    valid = false
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
  if (!validate()) return

  const payload = buildPayload()

  if (isEdit.value && objektId.value) {
    const updated = await objekteStore.updateObjekt(objektId.value, payload)
    if (updated) {
      showToast('Objekt aktualisiert.', 'success')
      router.push(`/objekte/${updated.id}`)
    } else {
      showToast(objekteStore.error?.message || 'Fehler beim Speichern.', 'error')
    }
  } else {
    const created = await objekteStore.createObjekt(payload)
    if (created) {
      showToast('Objekt erfolgreich angelegt.', 'success')
      router.push(`/objekte/${created.id}`)
    } else {
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
