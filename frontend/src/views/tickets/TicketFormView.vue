<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="$router.push('/tickets')">
          ← Zurück
        </button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Neues Ticket</h1>
      </div>

      <AppCard padding="lg" shadow="md"
        >
        <form class="space-y-5" @submit.prevent="handleSubmit">
          <AppInput
            id="titel"
            v-model="form.titel"
            label="Titel"
            placeholder="Kurze Beschreibung des Anliegens"
            required
            :error="errors.titel"
          />

          <div>
            <label for="beschreibung" class="block text-sm font-medium text-gray-700 mb-1"
            >Beschreibung</label>
            <textarea
              id="beschreibung"
              v-model="form.beschreibung"
              rows="5"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              placeholder="Detaillierte Beschreibung des Problems …"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="kategorie" class="block text-sm font-medium text-gray-700 mb-1"
              >Kategorie</label>
              <select
                id="kategorie"
                v-model="form.kategorie"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option v-for="option in kategorieOptions" :key="option.value" :value="option.value"
                >{{ option.label }}</option>
              </select>
            </div>

            <div>
              <label for="prioritaet" class="block text-sm font-medium text-gray-700 mb-1"
              >Priorität</label>
              <select
                id="prioritaet"
                v-model="form.prioritaet"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option v-for="option in prioritaetOptions" :key="option.value" :value="option.value"
                >{{ option.label }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="objekt-id"
              v-model="form.objekt_id"
              label="Objekt (optional)"
              placeholder="Objekt-ID"
              hint="Verknüpfung mit einem bestehenden Objekt"
            />
            <AppInput
              id="einheit-id"
              v-model="form.einheit_id"
              label="Einheit (optional)"
              placeholder="Einheit-ID"
              hint="Verknüpfung mit einer Wohneinheit"
            />
          </div>

          <AppInput
            id="mieter-id"
            v-model="form.mieter_id"
            label="Mieter (optional)"
            placeholder="Mieter-ID"
          />

          <div class="flex items-center justify-end gap-3 pt-4">
            <AppButton type="button" variant="ghost" @click="$router.push('/tickets')">
              Abbrechen
            </AppButton>
            <AppButton type="submit" :loading="ticketsStore.saving">
              Ticket erstellen
            </AppButton>
          </div>
        </form>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketsStore, type Ticket, type TicketKategorie, type TicketPrioritaet } from '@/stores/tickets'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const ticketsStore = useTicketsStore()
const { showToast } = useToast()

const form = reactive({
  titel: '',
  beschreibung: '',
  kategorie: 'sonstiges' as TicketKategorie,
  prioritaet: 'normal' as TicketPrioritaet,
  objekt_id: '',
  einheit_id: '',
  mieter_id: '',
})

const errors = reactive({
  titel: '',
})

const kategorieOptions: { value: TicketKategorie; label: string }[] = [
  { value: 'heizung', label: 'Heizung' },
  { value: 'wasser', label: 'Wasser' },
  { value: 'elektrik', label: 'Elektrik' },
  { value: 'schimmel', label: 'Schimmel' },
  { value: 'sanitaer', label: 'Sanitär' },
  { value: 'schluessel', label: 'Schlüssel' },
  { value: 'sauberkeit', label: 'Sauberkeit' },
  { value: 'sonstiges', label: 'Sonstiges' },
]

const prioritaetOptions: { value: TicketPrioritaet; label: string }[] = [
  { value: 'niedrig', label: 'Niedrig' },
  { value: 'normal', label: 'Normal' },
  { value: 'hoch', label: 'Hoch' },
  { value: 'dringend', label: 'Dringend' },
]

function validate(): boolean {
  errors.titel = ''
  if (!form.titel.trim()) {
    errors.titel = 'Bitte gib einen Titel ein.'
    return false
  }
  return true
}

function buildPayload(): Partial<Ticket> {
  return {
    titel: form.titel.trim(),
    beschreibung: form.beschreibung.trim() || undefined,
    kategorie: form.kategorie,
    prioritaet: form.prioritaet,
    objekt_id: form.objekt_id.trim() || undefined,
    einheit_id: form.einheit_id.trim() || undefined,
    mieter_id: form.mieter_id.trim() || undefined,
  }
}

async function handleSubmit(): Promise<void> {
  if (!validate()) return

  const created = await ticketsStore.createTicket(buildPayload())
  if (created) {
    showToast('Ticket erfolgreich erstellt.', 'success')
    router.push(`/tickets/${created.id}`)
  } else {
    showToast(ticketsStore.error?.message || 'Fehler beim Erstellen.', 'error')
  }
}
</script>
