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
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="first_name"
              v-model="form.first_name"
              label="Vorname"
              placeholder="Max"
              required
              :error="errors.first_name"
            />
            <AppInput
              id="last_name"
              v-model="form.last_name"
              label="Nachname"
              placeholder="Mustermann"
              required
              :error="errors.last_name"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="email"
              v-model="form.email"
              label="E-Mail"
              type="email"
              placeholder="mieter@beispiel.de"
              autocomplete="email"
              :error="errors.email"
            />
            <AppInput
              id="telefon"
              v-model="form.telefon"
              label="Telefon"
              type="tel"
              placeholder="+49 170 1234567"
              autocomplete="tel"
            />
          </div>

          <AppInput
            id="geburtsdatum"
            v-model="form.geburtsdatum"
            label="Geburtsdatum"
            type="date"
          />

          <!-- Adressen -->
          <div class="border-t border-gray-100 pt-6">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-lg font-semibold text-[#0D3B70]">Adressen</h2>
              <AppButton type="button" size="sm" variant="secondary" @click="addAdresse">
                + Adresse
              </AppButton>
            </div>

            <div v-for="(adresse, index) in form.adressen" :key="index" class="bg-gray-50 rounded-xl p-4 mb-3">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-medium text-gray-700">Adresse {{ index + 1 }}</span>
                <button type="button" class="text-red-500 text-sm hover:underline" @click="removeAdresse(index)">Entfernen</button>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <AppInput :id="`adresse-typ-${index}`" v-model="adresse.typ" label="Typ" :error="errors.adressen[index]?.typ" />
                <AppInput :id="`adresse-strasse-${index}`" v-model="adresse.strasse" label="Straße" :error="errors.adressen[index]?.strasse" />
                <AppInput :id="`adresse-hausnummer-${index}`" v-model="adresse.hausnummer" label="Hausnummer" />
                <AppInput :id="`adresse-plz-${index}`" v-model="adresse.plz" label="PLZ" maxlength="5" :error="errors.adressen[index]?.plz" />
                <AppInput :id="`adresse-ort-${index}`" v-model="adresse.ort" label="Ort" :error="errors.adressen[index]?.ort" />
                <AppInput :id="`adresse-land-${index}`" v-model="adresse.land" label="Land" />
              </div>
              <label class="flex items-center gap-2 mt-3 text-sm text-gray-700">
                <input v-model="adresse.is_primary" type="checkbox" />
                Primäre Adresse
              </label>
            </div>
          </div>

          <!-- Bürge -->
          <div class="border-t border-gray-100 pt-6">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-lg font-semibold text-[#0D3B70]">Mietbürge (§ 765 BGB)</h2>
              <AppButton type="button" size="sm" variant="secondary" @click="addBuergschaft">
                + Bürge
              </AppButton>
            </div>

            <div v-for="(bg, index) in form.buergschaften" :key="`b-${index}`" class="bg-gray-50 rounded-xl p-4 mb-3">
              <div class="flex items-center justify-between mb-3">
                <span class="text-sm font-medium text-gray-700">Bürge {{ index + 1 }}</span>
                <button type="button" class="text-red-500 text-sm hover:underline" @click="removeBuergschaft(index)">Entfernen</button>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <AppInput :id="`bg-vorname-${index}`" v-model="bg.buerge_first_name" label="Vorname" />
                <AppInput :id="`bg-nachname-${index}`" v-model="bg.buerge_last_name" label="Nachname" />
                <AppInput :id="`bg-geburtsdatum-${index}`" v-model="bg.buerge_geburtsdatum" label="Geburtsdatum" type="date" />
                <AppInput :id="`bg-telefon-${index}`" v-model="bg.buerge_phone" label="Telefon" />
                <AppInput :id="`bg-email-${index}`" v-model="bg.buerge_email" label="E-Mail" type="email" />
                <AppInput :id="`bg-betrag-${index}`" v-model="bg.hoechstbetrag" label="Höchstbetrag (€)" type="number" />
                <AppInput :id="`bg-bis-${index}`" v-model="bg.gueltig_bis" label="Gültig bis" type="date" />
                <AppInput :id="`bg-status-${index}`" v-model="bg.status" label="Status" />
              </div>

              <div class="grid grid-cols-2 gap-3 mt-3">
                <AppInput :id="`bg-strasse-${index}`" v-model="bg.buerge_adresse.strasse" label="Straße" />
                <AppInput :id="`bg-hausnummer-${index}`" v-model="bg.buerge_adresse.hausnummer" label="Hausnummer" />
                <AppInput :id="`bg-plz-${index}`" v-model="bg.buerge_adresse.plz" label="PLZ" />
                <AppInput :id="`bg-ort-${index}`" v-model="bg.buerge_adresse.ort" label="Ort" />
              </div>

              <div class="mt-3">
                <label :for="`bg-notizen-${index}`" class="block text-sm font-medium text-gray-700 mb-1">Notizen</label>
                <textarea
                  :id="`bg-notizen-${index}`"
                  v-model="bg.notizen"
                  rows="2"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                  placeholder="Bürgschafts-Notizen …"
                />
              </div>
            </div>
          </div>

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
import { useMieterStore, type Mieter, type Adresse, type Buergschaft } from '@/stores/mieter'
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

function emptyAdresse() {
  return {
    typ: 'postal' as const,
    strasse: '',
    hausnummer: '',
    plz: '',
    ort: '',
    land: 'DE',
    is_primary: false,
  }
}

function emptyBuergschaft() {
  return {
    buerge_first_name: '',
    buerge_last_name: '',
    buerge_geburtsdatum: '',
    buerge_phone: '',
    buerge_email: '',
    hoechstbetrag: '',
    gueltig_bis: '',
    status: 'aktiv' as const,
    notizen: '',
    buerge_adresse: { ...emptyAdresse(), typ: 'guarantor' as const },
  }
}

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  telefon: '',
  geburtsdatum: '',
  notizen: '',
  adressen: [] as {
    id?: string
    typ: 'postal' | 'residential' | 'rental_object' | 'guarantor'
    strasse: string
    hausnummer: string
    plz: string
    ort: string
    land: string
    is_primary: boolean
  }[],
  buergschaften: [] as {
    id?: string
    buerge_first_name: string
    buerge_last_name: string
    buerge_geburtsdatum: string
    buerge_phone: string
    buerge_email: string
    hoechstbetrag: string
    gueltig_bis: string
    status: 'aktiv' | 'inaktiv'
    notizen: string
    buerge_adresse: {
      id?: string
      typ: 'postal' | 'residential' | 'rental_object' | 'guarantor'
      strasse: string
      hausnummer: string
      plz: string
      ort: string
      land: string
      is_primary: boolean
    }
  }[],
})

const errors = reactive({
  first_name: '',
  last_name: '',
  email: '',
  adressen: [] as Record<string, string>[],
})

function addAdresse(): void {
  form.adressen.push(emptyAdresse())
}

function removeAdresse(index: number): void {
  form.adressen.splice(index, 1)
}

function addBuergschaft(): void {
  form.buergschaften.push(emptyBuergschaft())
}

function removeBuergschaft(index: number): void {
  form.buergschaften.splice(index, 1)
}

function populateForm(mieter: Mieter): void {
  form.first_name = mieter.first_name
  form.last_name = mieter.last_name
  form.email = mieter.email || ''
  form.telefon = mieter.telefon || ''
  form.geburtsdatum = mieter.geburtsdatum || ''
  form.notizen = mieter.notizen || ''
  form.adressen = (mieter.adressen || []).map(a => ({
    id: a.id,
    typ: a.typ || 'postal',
    strasse: a.strasse || '',
    hausnummer: a.hausnummer || '',
    plz: a.plz || '',
    ort: a.ort || '',
    land: a.land || 'DE',
    is_primary: a.is_primary ?? false,
  }))
  form.buergschaften = (mieter.buergschaften || []).map(b => ({
    ...emptyBuergschaft(),
    buerge_first_name: b.buerge_first_name || '',
    buerge_last_name: b.buerge_last_name || '',
    buerge_geburtsdatum: b.buerge_geburtsdatum || '',
    buerge_phone: b.buerge_phone || '',
    buerge_email: b.buerge_email || '',
    hoechstbetrag: b.hoechstbetrag != null ? String(b.hoechstbetrag) : '',
    gueltig_bis: b.gueltig_bis || '',
    status: b.status || 'aktiv',
    notizen: b.notizen || '',
    buerge_adresse: {
      id: b.buerge_adresse?.id,
      typ: 'guarantor',
      strasse: b.buerge_adresse?.strasse || '',
      hausnummer: b.buerge_adresse?.hausnummer || '',
      plz: b.buerge_adresse?.plz || '',
      ort: b.buerge_adresse?.ort || '',
      land: b.buerge_adresse?.land || 'DE',
      is_primary: b.buerge_adresse?.is_primary ?? false,
    },
  }))
}

function validate(): boolean {
  errors.first_name = ''
  errors.last_name = ''
  errors.email = ''
  errors.adressen = []

  let valid = true
  if (!form.first_name.trim()) {
    errors.first_name = 'Bitte gib einen Vornamen ein.'
    valid = false
  }
  if (!form.last_name.trim()) {
    errors.last_name = 'Bitte gib einen Nachnamen ein.'
    valid = false
  }

  if (form.email && !isValidEmail(form.email)) {
    errors.email = 'Bitte gib eine gültige E-Mail-Adresse ein.'
    valid = false
  }

  form.adressen.forEach((a, i) => {
    const ae: Record<string, string> = {}
    if (!a.strasse.trim()) ae.strasse = 'Straße erforderlich.'
    if (!a.plz.trim()) ae.plz = 'PLZ erforderlich.'
    if (!a.ort.trim()) ae.ort = 'Ort erforderlich.'
    if (Object.keys(ae).length) {
      errors.adressen[i] = ae
      valid = false
    }
  })

  return valid
}

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function buildPayload(): Partial<Mieter> {
  return {
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    email: form.email.trim() || undefined,
    telefon: form.telefon.trim() || undefined,
    geburtsdatum: form.geburtsdatum || undefined,
    notizen: form.notizen.trim() || undefined,
    adressen: form.adressen.length > 0 ? form.adressen : undefined,
    buergschaften: form.buergschaften.length > 0 ? form.buergschaften : undefined,
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
