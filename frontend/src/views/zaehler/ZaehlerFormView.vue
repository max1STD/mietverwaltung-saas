<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="goBack">← Zurück</button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
          {{ isEdit ? 'Zähler bearbeiten' : 'Zähler anlegen' }}
        </h1>
      </div>

      <AppCard padding="lg" shadow="md">
        <form class="space-y-5" @submit.prevent="handleSubmit">
          <AppInput
            id="bezeichnung"
            v-model="form.bezeichnung"
            label="Bezeichnung"
            placeholder="z. B. Strom Hauptzähler"
            required
          />

          <AppInput
            id="zaehlernummer"
            v-model="form.zaehlernummer"
            label="Zählernummer"
            placeholder="z. B. 12345678"
          />

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="typ" class="block text-sm font-medium text-gray-700 mb-1">Typ *</label>
              <select
                id="typ"
                v-model="form.typ"
                required
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="strom">Strom</option>
                <option value="gas">Gas</option>
                <option value="wasser">Wasser</option>
                <option value="waerme">Wärme</option>
                <option value="kaltwasser">Kaltwasser</option>
                <option value="sonstiges">Sonstiges</option>
              </select>
            </div>

            <div>
              <label for="einheit" class="block text-sm font-medium text-gray-700 mb-1">Einheit *</label>
              <select
                id="einheit"
                v-model="form.einheit"
                required
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="kwh">kWh</option>
                <option value="kwh_m3">kWh / m³</option>
                <option value="m3">m³</option>
                <option value="sonstiges">Sonstiges</option>
              </select>
            </div>
          </div>

          <div>
            <label for="einheit_id" class="block text-sm font-medium text-gray-700 mb-1">Wohneinheit *</label>
            <select
              id="einheit_id"
              v-model="form.einheit_id"
              required
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="">Bitte wählen</option>
              <optgroup
                v-for="objekt in objekteStore.objekte"
                :key="objekt.id"
                :label="objekt.name"
              >
                <option
                  v-for="einheit in einheitenFuerObjekt(objekt.id)"
                  :key="einheit.id"
                  :value="einheit.id"
                >
                  {{ einheit.name }}
                </option>
              </optgroup>
            </select>
          </div>

          <div class="flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl">
            <input
              id="ist_hauptzaehler"
              v-model="form.ist_hauptzaehler"
              type="checkbox"
              class="w-5 h-5 text-[#0D3B70] border-gray-300 rounded focus:ring-[#0D3B70]"
            >
            <label for="ist_hauptzaehler" class="text-sm text-gray-700">Hauptzähler</label>
          </div>

          <div class="pt-4 flex items-center justify-end gap-3">
            <AppButton variant="ghost" type="button" @click="goBack">Abbrechen</AppButton>
            <AppButton type="submit" :loading="zaehlerStore.saving">
              {{ isEdit ? 'Speichern' : 'Anlegen' }}
            </AppButton>
          </div>
        </form>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useZaehlerStore, type ZaehlerTyp } from '@/stores/zaehler'
import { useObjekteStore, type Einheit } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'

const zaehlerStore = useZaehlerStore()
const objekteStore = useObjekteStore()
const route = useRoute()
const router = useRouter()
const { showToast } = useToast()

const isEdit = computed(() => !!route.params.id)
const zaehlerId = computed(() => route.params.id as string)

const form = reactive({
  bezeichnung: '',
  zaehlernummer: '',
  typ: 'strom' as ZaehlerTyp,
  einheit: 'kwh',
  einheit_id: '',
  ist_hauptzaehler: false,
})

function einheitenFuerObjekt(objektId: string): Einheit[] {
  return objekteStore.einheiten.filter((e: Einheit) => e.objekt_id === objektId)
}

function goBack(): void {
  if (isEdit.value) {
    router.push(`/zaehler/${zaehlerId.value}`)
  } else {
    router.push('/zaehler')
  }
}

async function handleSubmit(): Promise<void> {
  const payload = {
    bezeichnung: form.bezeichnung,
    zaehlernummer: form.zaehlernummer || null,
    typ: form.typ,
    einheit: form.einheit,
    einheit_id: Number(form.einheit_id),
    ist_hauptzaehler: form.ist_hauptzaehler,
  }

  let ok = false
  if (isEdit.value) {
    const result = await zaehlerStore.updateZaehler(zaehlerId.value, payload)
    ok = result !== null
  } else {
    const result = await zaehlerStore.createZaehler(payload)
    ok = result !== null
  }

  if (ok) {
    showToast(isEdit.value ? 'Zähler gespeichert.' : 'Zähler angelegt.', 'success')
    await router.push(isEdit.value ? `/zaehler/${zaehlerId.value}` : '/zaehler')
  } else {
    showToast(zaehlerStore.error?.message || 'Speichern fehlgeschlagen.', 'error')
  }
}

onMounted(async () => {
  await objekteStore.fetchObjekte()
  await Promise.all(objekteStore.objekte.map((o) => objekteStore.fetchEinheiten(o.id)))
  if (isEdit.value) {
    const z = await zaehlerStore.fetchZaehlerDetail(zaehlerId.value)
    if (z) {
      form.bezeichnung = z.bezeichnung
      form.zaehlernummer = z.zaehlernummer || ''
      form.typ = z.typ
      form.einheit = z.einheit
      form.einheit_id = z.einheit_id
      form.ist_hauptzaehler = z.ist_hauptzaehler
    }
  }
})
</script>
