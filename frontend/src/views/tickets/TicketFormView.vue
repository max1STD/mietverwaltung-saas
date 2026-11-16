<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div class="mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70] mb-3" @click="$router.push('/tickets')">
          ← Zurück
        </button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">Neues Ticket</h1>
      </div>

      <AppCard padding="lg" shadow="md">
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

          <!-- Für Vermieter: Dropdowns zur Zuordnung -->
          <template v-if="authStore.isVermieter">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label for="objekt-id" class="block text-sm font-medium text-gray-700 mb-1"
                >Objekt (optional)</label>
                <select
                  id="objekt-id"
                  v-model="form.objekt_id"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                >
                  <option value="">— Kein Objekt —</option>
                  <option v-for="objekt in objekteStore.objekte" :key="objekt.id" :value="objekt.id"
                  >{{ objekt.name || objekt.bezeichnung || objekt.address }}</option>
                </select>
              </div>

              <div>
                <label for="einheit-id" class="block text-sm font-medium text-gray-700 mb-1"
                >Einheit (optional)</label>
                <select
                  id="einheit-id"
                  v-model="form.einheit_id"
                  :disabled="!availableEinheiten.length"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70] disabled:bg-gray-100"
                >
                  <option value="">— Keine Einheit —</option>
                  <option v-for="einheit in availableEinheiten" :key="einheit.id" :value="einheit.id"
                  >{{ einheit.name }} {{ (einheit.aktueller_mieter ?? einheit.current_mieter) ? `(Mieter: ${(einheit.aktueller_mieter ?? einheit.current_mieter)?.name})` : '' }}</option>
                </select>
              </div>
            </div>

            <div>
              <label for="mieter-id" class="block text-sm font-medium text-gray-700 mb-1"
              >Mieter (optional)</label>
              <select
                id="mieter-id"
                v-model="form.mieter_id"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="">— Kein Mieter —</option>
                <option v-for="mieter in mieterStore.mieter" :key="mieter.id" :value="mieter.id"
                >{{ mieter.name || `${mieter.first_name} ${mieter.last_name}` }}</option>
              </select>
              <p class="mt-1 text-xs text-gray-500">Wird automatisch gesetzt, wenn eine vermietete Einheit gewählt wird.</p>
            </div>
          </template>

          <!-- Für Mieter: nur Hinweis auf automatische Zuordnung -->
          <div v-else-if="authStore.isMieter" class="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-800">
            <p>📝 Das Ticket wird automatisch deinem Objekt und deiner Wohnung zugeordnet.</p>
          </div>

          <!-- Dateianhänge -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Dateianhänge</label>
            <div class="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-[#0D3B70] transition-colors cursor-pointer" @click="fileInput?.click()">
              <input
                ref="fileInput"
                type="file"
                multiple
                accept="image/*,.pdf,.doc,.docx"
                class="hidden"
                @change="onFilesSelected"
              />
              <p class="text-gray-500">Klicke hier, um Fotos oder Dokumente hochzuladen</p>
              <p class="text-xs text-gray-400 mt-1">Bilder, PDF, Word — maximal 10 MB pro Datei</p>
            </div>
            <ul v-if="attachments.length" class="mt-3 space-y-2">
              <li v-for="(file, index) in attachments" :key="index" class="flex items-center justify-between bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm">
                <span class="truncate">{{ file.name }} ({{ formatBytes(file.size) }})</span>
                <button type="button" class="text-red-500 hover:text-red-700" @click="removeAttachment(index)">Entfernen</button>
              </li>
            </ul>
          </div>

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
import { reactive, computed, ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketsStore, type Ticket, type TicketKategorie, type TicketPrioritaet } from '@/stores/tickets'
import { useObjekteStore } from '@/stores/objekte'
import { useMieterStore } from '@/stores/mieter'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const ticketsStore = useTicketsStore()
const objekteStore = useObjekteStore()
const mieterStore = useMieterStore()
const authStore = useAuthStore()
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

const attachments = ref<File[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

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

const availableEinheiten = computed(() => {
  if (!form.objekt_id) return []
  const objekt = objekteStore.objekte.find((o) => String(o.id) === String(form.objekt_id))
  return objekt?.einheiten ?? []
})

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function onFilesSelected(event: Event): void {
  const target = event.target as HTMLInputElement
  if (target.files) {
    attachments.value.push(...Array.from(target.files))
  }
  target.value = ''
}

function removeAttachment(index: number): void {
  attachments.value.splice(index, 1)
}

function validate(): boolean {
  errors.titel = ''
  if (!form.titel.trim()) {
    errors.titel = 'Bitte gib einen Titel ein.'
    return false
  }
  return true
}

function buildPayload(): Partial<Ticket> {
  const payload: Partial<Ticket> = {
    titel: form.titel.trim(),
    beschreibung: form.beschreibung.trim() || undefined,
    kategorie: form.kategorie,
    prioritaet: form.prioritaet,
  }

  const objektId = parseInt(form.objekt_id, 10)
  if (!Number.isNaN(objektId) && objektId > 0) {
    payload.objekt_id = String(objektId)
  }

  const einheitId = parseInt(form.einheit_id, 10)
  if (!Number.isNaN(einheitId) && einheitId > 0) {
    payload.einheit_id = String(einheitId)
  }

  const mieterId = parseInt(form.mieter_id, 10)
  if (!Number.isNaN(mieterId) && mieterId > 0) {
    payload.mieter_id = String(mieterId)
  }

  return payload
}

async function handleSubmit(): Promise<void> {
  if (!validate()) return

  const created = await ticketsStore.createTicket(buildPayload())
  if (created) {
    // TODO: attachments upload wenn Backend bereit
    if (attachments.value.length) {
      showToast(`${attachments.value.length} Anhang/Anhänge werden vorbereitet (Upload folgt).`, 'info')
    }
    showToast('Ticket erfolgreich erstellt.', 'success')
    router.push(`/tickets/${created.id}`)
  } else {
    showToast(ticketsStore.error?.message || 'Fehler beim Erstellen.', 'error')
  }
}

// Wenn Einheit gewählt wird, Mieter automatisch aus aktuellem Mietvertrag füllen
watch(
  () => form.einheit_id,
  (newEinheitId) => {
    if (!newEinheitId) return
    const einheit = availableEinheiten.value.find((e) => String(e.id) === String(newEinheitId))
    const mieter = einheit?.aktueller_mieter ?? einheit?.current_mieter
    if (mieter) {
      form.mieter_id = String(mieter.id)
    }
  },
)

onMounted(async () => {
  if (authStore.isVermieter) {
    await Promise.all([
      objekteStore.fetchObjekte(),
      mieterStore.fetchMieter(),
    ])
  }
})
</script>
