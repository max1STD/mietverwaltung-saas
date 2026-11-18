<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="goBack">← Zurück</button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
          {{ isEdit ? 'Mietvertrag bearbeiten' : 'Mietvertrag anlegen' }}
        </h1>
      </div>

      <AppCard padding="lg" shadow="md">
        <form class="space-y-5" @submit.prevent="handleSubmit">
          <div>
            <label for="mieter_id" class="block text-sm font-medium text-gray-700 mb-1">Mieter *</label>
            <select
              id="mieter_id"
              v-model="form.mieter_id"
              required
              :disabled="isEdit"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70] disabled:bg-gray-100"
            >
              <option value="">Bitte wählen</option>
              <option v-for="mieter in mieterStore.mieter" :key="mieter.id" :value="mieter.id">
                {{ mieter.name }}
              </option>
            </select>
          </div>

          <div>
            <label for="einheit_id" class="block text-sm font-medium text-gray-700 mb-1">Wohneinheit *</label>
            <select
              id="einheit_id"
              v-model="form.einheit_id"
              required
              :disabled="isEdit"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70] disabled:bg-gray-100"
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

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="mietbeginn"
              v-model="form.mietbeginn"
              label="Mietbeginn *"
              type="date"
              required
            />
            <AppInput
              id="mietende"
              v-model="form.mietende"
              label="Mietende"
              type="date"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="kaltmiete"
              v-model="form.kaltmiete"
              label="Kaltmiete (€) *"
              type="number"
              step="0.01"
              placeholder="800"
              required
            />
            <AppInput
              id="nebenkosten_vorschuss"
              v-model="form.nebenkosten_vorschuss"
              label="NK-Vorschuss (€) *"
              type="number"
              step="0.01"
              placeholder="150"
              required
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="kaution"
              v-model="form.kaution"
              label="Kaution (€)"
              type="number"
              step="0.01"
              placeholder="1600"
            />

            <div class="flex items-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl">
              <input
                id="kaution_hinterlegt"
                v-model="form.kaution_hinterlegt"
                type="checkbox"
                class="w-5 h-5 text-[#0D3B70] border-gray-300 rounded focus:ring-[#0D3B70]"
              >
              <label for="kaution_hinterlegt" class="text-sm text-gray-700">Kaution hinterlegt</label>
            </div>
          </div>

          <div v-if="isEdit">
            <label for="status" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              id="status"
              v-model="form.status"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
            >
              <option value="aktiv">Aktiv</option>
              <option value="gekuendigt">Gekündigt</option>
              <option value="beendet">Beendet</option>
            </select>
          </div>

          <div class="pt-4 flex items-center justify-end gap-3">
            <AppButton variant="ghost" type="button" @click="goBack">Abbrechen</AppButton>
            <AppButton type="submit" :loading="mietvertraegeStore.saving">
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
import { useMietvertraegeStore, type MietvertragStatus } from '@/stores/mietvertraege'
import { useMieterStore, type Mieter } from '@/stores/mieter'
import { useObjekteStore, type Einheit } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'

const mietvertraegeStore = useMietvertraegeStore()
const mieterStore = useMieterStore()
const objekteStore = useObjekteStore()
const route = useRoute()
const router = useRouter()
const { showToast } = useToast()

const isEdit = computed(() => !!route.params.id)
const vertragId = computed(() => route.params.id as string)
const preselectedMieterId = computed(() => route.query.mieter_id as string | undefined)

const form = reactive({
  mieter_id: '',
  einheit_id: '',
  mietbeginn: '',
  mietende: '',
  kaltmiete: '',
  nebenkosten_vorschuss: '',
  kaution: '',
  kaution_hinterlegt: false,
  status: 'aktiv' as MietvertragStatus,
})

function einheitenFuerObjekt(objektId: string): Einheit[] {
  return objekteStore.einheiten.filter((e: Einheit) => e.objekt_id === objektId)
}

function goBack(): void {
  if (isEdit.value) {
    router.push(`/mietvertraege/${vertragId.value}`)
  } else {
    router.push('/mietvertraege')
  }
}

async function handleSubmit(): Promise<void> {
  const payload: Record<string, unknown> = {
    mietbeginn: form.mietbeginn,
    mietende: form.mietende || null,
    kaltmiete: Number(form.kaltmiete),
    nebenkosten_vorschuss: Number(form.nebenkosten_vorschuss),
    kaution: form.kaution ? Number(form.kaution) : null,
    kaution_hinterlegt: form.kaution_hinterlegt,
  }

  if (!isEdit.value) {
    payload.mieter_id = Number(form.mieter_id)
    payload.einheit_id = Number(form.einheit_id)
  } else {
    payload.status = form.status
  }

  let ok = false
  if (isEdit.value) {
    const result = await mietvertraegeStore.updateMietvertrag(vertragId.value, payload)
    ok = result !== null
  } else {
    const result = await mietvertraegeStore.createMietvertrag(payload)
    ok = result !== null
  }

  if (ok) {
    showToast(isEdit.value ? 'Mietvertrag gespeichert.' : 'Mietvertrag angelegt.', 'success')
    await router.push(isEdit.value ? `/mietvertraege/${vertragId.value}` : '/mietvertraege')
  } else {
    showToast(mietvertraegeStore.error?.message || 'Speichern fehlgeschlagen.', 'error')
  }
}

onMounted(async () => {
  await Promise.all([
    mieterStore.fetchMieter(),
    objekteStore.fetchObjekte(),
  ])
  await Promise.all(objekteStore.objekte.map((o) => objekteStore.fetchEinheiten(o.id)))

  if (preselectedMieterId.value) {
    form.mieter_id = preselectedMieterId.value
  }

  if (isEdit.value) {
    const v = await mietvertraegeStore.fetchMietvertrag(vertragId.value)
    if (v) {
      form.mieter_id = v.mieter_id
      form.einheit_id = v.einheit_id
      form.mietbeginn = v.mietbeginn
      form.mietende = v.mietende || ''
      form.kaltmiete = String(v.kaltmiete)
      form.nebenkosten_vorschuss = String(v.nebenkosten_vorschuss || '')
      form.kaution = v.kaution != null ? String(v.kaution) : ''
      form.kaution_hinterlegt = v.kaution_hinterlegt || false
      form.status = (v.status as MietvertragStatus) || 'aktiv'
    }
  }
})
</script>
