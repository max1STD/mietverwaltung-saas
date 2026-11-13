<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="goBack">
          ← Zurück
        </button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
          {{ isEdit ? 'Mieter bearbeiten' : 'Neuer Mieter' }}
        </h1>
      </div>

      <AppCard padding="lg" shadow="md">
        <form class="space-y-5" @submit.prevent="handleSubmit">
          <AppInput
            id="name"
            v-model="form.name"
            label="Name"
            placeholder="Vor- und Nachname"
            required
            :error="errors.name"
          />

          <AppInput
            id="email"
            v-model="form.email"
            label="E-Mail"
            type="email"
            placeholder="mieter@beispiel.de"
            autocomplete="email"
            :error="errors.email"
          />

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="telefon"
              v-model="form.telefon"
              label="Telefon"
              type="tel"
              placeholder="+49 170 1234567"
              autocomplete="tel"
            />
            <AppInput
              id="geburtsdatum"
              v-model="form.geburtsdatum"
              label="Geburtsdatum"
              type="date"
            />
          </div>

          <AppInput
            id="adresse"
            v-model="form.adresse"
            label="Adresse"
            placeholder="Aktuelle Wohnanschrift des Mieters"
            autocomplete="street-address"
          />

          <div>
            <label for="notizen" class="block text-sm font-medium text-gray-700 mb-1">Notizen</label>
            <textarea
              id="notizen"
              v-model="form.notizen"
              rows="4"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              placeholder="Interne Notizen …"
            />
          </div>

          <div class="flex items-center justify-end gap-3 pt-4">
            <AppButton type="button" variant="ghost" @click="goBack">
              Abbrechen
            </AppButton>
            <AppButton type="submit" :loading="mieterStore.saving">
              {{ isEdit ? 'Änderungen speichern' : 'Mieter anlegen' }}
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
import { useMieterStore, type Mieter } from '@/stores/mieter'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const route = useRoute()
const router = useRouter()
const mieterStore = useMieterStore()
const { showToast } = useToast()

const mieterId = computed(() => route.params.id as string | undefined)
const isEdit = computed(() => !!mieterId.value)

const form = reactive({
  name: '',
  email: '',
  telefon: '',
  geburtsdatum: '',
  adresse: '',
  notizen: '',
})

const errors = reactive({
  name: '',
  email: '',
})

function populateForm(mieter: Mieter): void {
  form.name = mieter.name
  form.email = mieter.email || ''
  form.telefon = mieter.telefon || ''
  form.geburtsdatum = mieter.geburtsdatum || ''
  form.adresse = mieter.adresse || ''
  form.notizen = mieter.notizen || ''
}

function validate(): boolean {
  errors.name = ''
  errors.email = ''

  let valid = true
  if (!form.name.trim()) {
    errors.name = 'Bitte gib einen Namen ein.'
    valid = false
  }

  if (form.email && !isValidEmail(form.email)) {
    errors.email = 'Bitte gib eine gültige E-Mail-Adresse ein.'
    valid = false
  }

  return valid
}

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function buildPayload(): Partial<Mieter> {
  return {
    name: form.name.trim(),
    email: form.email.trim() || undefined,
    telefon: form.telefon.trim() || undefined,
    geburtsdatum: form.geburtsdatum || undefined,
    adresse: form.adresse.trim() || undefined,
    notizen: form.notizen.trim() || undefined,
  }
}

async function handleSubmit(): Promise<void> {
  if (!validate()) return

  const payload = buildPayload()

  if (isEdit.value && mieterId.value) {
    const updated = await mieterStore.updateMieter(mieterId.value, payload)
    if (updated) {
      showToast('Mieter aktualisiert.', 'success')
      router.push(`/mieter/${updated.id}`)
    } else {
      showToast(mieterStore.error?.message || 'Fehler beim Speichern.', 'error')
    }
  } else {
    const created = await mieterStore.createMieter(payload)
    if (created) {
      showToast('Mieter erfolgreich angelegt.', 'success')
      router.push(`/mieter/${created.id}`)
    } else {
      showToast(mieterStore.error?.message || 'Fehler beim Anlegen.', 'error')
    }
  }
}

function goBack(): void {
  if (isEdit.value && mieterId.value) {
    router.push(`/mieter/${mieterId.value}`)
  } else {
    router.push('/mieter')
  }
}

onMounted(async () => {
  if (isEdit.value && mieterId.value) {
    const mieter = await mieterStore.fetchMieterById(mieterId.value)
    if (mieter) {
      populateForm(mieter)
    }
  }
})
</script>
