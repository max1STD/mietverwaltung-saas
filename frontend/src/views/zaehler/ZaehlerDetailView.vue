<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div class="flex items-center gap-3">
          <AppButton variant="ghost" size="sm" @click="$router.push('/zaehler')">← Zurück</AppButton>
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
              {{ zaehlerStore.currentZaehler?.bezeichnung || 'Zähler' }}
            </h1>
            <p v-if="zaehlerStore.currentZaehler" class="text-gray-500 mt-1">
              {{ formatTyp(zaehlerStore.currentZaehler.typ) }} · {{ formatEinheit(zaehlerStore.currentZaehler.einheit) }}
            </p>
          </div>
        </div>
        <div v-if="authStore.isVermieter && zaehlerStore.currentZaehler" class="flex gap-2">
          <AppButton
            variant="secondary"
            size="sm"
            @click="$router.push(`/zaehler/${zaehlerStore.currentZaehler.id}/bearbeiten`)"
          >
            Bearbeiten
          </AppButton>
          <AppButton
            variant="danger"
            size="sm"
            :loading="zaehlerStore.saving"
            @click="deleteZaehler"
          >
            Löschen
          </AppButton>
        </div>
      </div>

      <div v-if="zaehlerStore.currentZaehler" class="mt-2 flex flex-wrap gap-2 text-sm text-gray-600">
        <span v-if="zaehlerStore.currentZaehler.objekt_name">
          Objekt: <span class="font-medium text-gray-900">{{ zaehlerStore.currentZaehler.objekt_name }}</span>
        </span>
        <span v-if="zaehlerStore.currentZaehler.einheit_name" class="ml-0 sm:ml-4">
          Wohnung: <span class="font-medium text-gray-900">{{ zaehlerStore.currentZaehler.einheit_name }}</span>
        </span>
      </div>

      <!-- Ladezustand -->
      <div v-if="zaehlerStore.loading" class="py-12 text-center text-gray-500">
        Zähler wird geladen …
      </div>

      <template v-else-if="zaehlerStore.currentZaehler">
        <!-- Zähler-Metadaten -->
        <AppCard padding="md" shadow="md" class="mb-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Zählernummer</span>
              <p class="text-sm text-gray-900 mt-1">{{ zaehlerStore.currentZaehler.zaehlernummer || '–' }}</p>
            </div>
            <div>
              <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Hauptzähler</span>
              <p class="text-sm text-gray-900 mt-1">{{ zaehlerStore.currentZaehler.ist_hauptzaehler ? 'Ja' : 'Nein' }}</p>
            </div>
            <div>
              <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Letzte Ablesung</span>
              <p class="text-sm text-gray-900 mt-1">
                {{ zaehlerStore.currentZaehler.ablesedatum ? formatDate(zaehlerStore.currentZaehler.ablesedatum) : '–' }}
              </p>
            </div>
            <div>
              <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Einheit</span>
              <p class="text-sm text-gray-900 mt-1">{{ formatEinheit(zaehlerStore.currentZaehler.einheit) }}</p>
            </div>
          </div>
        </AppCard>

        <!-- Ablesungen -->
        <AppCard padding="md" shadow="md">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <h2 class="text-lg font-semibold text-[#0D3B70]">Ablesungen</h2>
            <AppButton size="sm" @click="showForm = true">+ Ablesung erfassen</AppButton>
          </div>

          <div v-if="ablesungen.length === 0" class="text-center py-8 text-gray-500">
            Noch keine Ablesungen vorhanden.
          </div>

          <div v-else class="divide-y divide-gray-100">
            <div
              v-for="ablesung in ablesungen"
              :key="ablesung.id"
              class="py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
            >
              <div class="flex-1">
                <div class="flex items-center gap-3">
                  <span class="font-medium text-gray-900">{{ formatDate(ablesung.ablesedatum) }}</span>
                  <AppBadge v-if="ablesung.ist_schaetzung" variant="yellow">Schätzung</AppBadge>
                </div>
                <p class="text-sm text-gray-500 mt-1">
                  Stand: <span class="font-medium text-gray-900">{{ formatNumber(ablesung.zaehlerstand) }}</span>
                  {{ formatEinheit(zaehlerStore.currentZaehler.einheit) }}
                  <span v-if="ablesung.verbrauch" class="ml-2">
                    (Verbrauch: {{ formatNumber(ablesung.verbrauch) }})
                  </span>
                </p>
                <div v-if="ablesung.warnings?.length" class="mt-1 space-y-1">
                  <div
                    v-for="(warning, wIndex) in ablesung.warnings"
                    :key="wIndex"
                    class="text-xs text-orange-700 bg-orange-50 px-2 py-1 rounded"
                  >
                    ⚠️ {{ warning }}
                  </div>
                </div>
                <p class="text-xs text-gray-400 mt-1">
                  Erfasst am {{ formatDateTime(ablesung.created_at) }} · Ableser: {{ ablesung.ableser || '–' }}
                </p>
                <p v-if="ablesung.notizen" class="text-sm text-gray-600 mt-1 italic">„{{ ablesung.notizen }}“</p>
              </div>

              <div v-if="authStore.isVermieter" class="flex items-center gap-2">
                <AppButton
                  variant="ghost"
                  size="sm"
                  @click="editAblesung(ablesung)"
                >
                  Bearbeiten
                </AppButton>
                <AppButton
                  variant="danger"
                  size="sm"
                  :loading="zaehlerStore.saving"
                  @click="deleteAblesung(ablesung)"
                >
                  Löschen
                </AppButton>
              </div>
            </div>
          </div>
        </AppCard>
      </template>

      <AppEmptyState
        v-else-if="!zaehlerStore.loading"
        icon="⚡"
        title="Zähler nicht gefunden"
        description="Der gewünschte Zähler existiert nicht oder du hast keinen Zugriff."
        action-label="Zurück zur Übersicht"
        @action="$router.push('/zaehler')"
      />
    </div>

    <!-- Ablesung Modal -->
    <AppModal
      v-model="showForm"
      :title="editingAblesung ? 'Ablesung bearbeiten' : 'Neue Ablesung erfassen'"
      size="md"
    >
      <form @submit.prevent="submitAblesung" class="space-y-4">
        <div>
          <label for="ablesedatum" class="block text-sm font-medium text-gray-700 mb-1">Ablesedatum *</label>
          <input
            id="ablesedatum"
            v-model="form.ablesedatum"
            type="date"
            required
            class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
          />
        </div>

        <div>
          <label for="zaehlerstand" class="block text-sm font-medium text-gray-700 mb-1">
            Zählerstand ({{ formatEinheit(zaehlerStore.currentZaehler?.einheit || '') }}) *
          </label>
          <input
            id="zaehlerstand"
            v-model="form.zaehlerstand"
            type="number"
            step="0.001"
            required
            class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
          />
        </div>

        <div>
          <label for="ableser" class="block text-sm font-medium text-gray-700 mb-1">Ableser</label>
          <input
            id="ableser"
            v-model="form.ableser"
            type="text"
            class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
          />
        </div>

        <div class="flex items-center gap-2">
          <input
            id="ist_schaetzung"
            v-model="form.ist_schaetzung"
            type="checkbox"
            class="h-4 w-4 text-[#0D3B70] border-gray-300 rounded"
          />
          <label for="ist_schaetzung" class="text-sm text-gray-700">Schätzung</label>
        </div>

        <div v-if="showZaehlerwechsel" class="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-xl">
          <input
            id="zaehlerwechsel"
            v-model="form.zaehlerwechsel"
            type="checkbox"
            class="h-4 w-4 mt-0.5 text-[#0D3B70] border-gray-300 rounded"
          />
          <div class="flex-1">
            <label for="zaehlerwechsel" class="text-sm font-medium text-yellow-900">Zählerwechsel hinterlegen</label>
            <p class="text-xs text-yellow-800 mt-0.5">
              Der eingegebene Stand ist kleiner als die vorherige Ablesung. Aktivieren Sie diesen Haken, wenn ein Zählerwechsel stattgefunden hat.
            </p>
          </div>
        </div>

        <div v-if="warnings.length" class="space-y-2">
          <div
            v-for="(warning, index) in warnings"
            :key="index"
            class="p-3 bg-orange-50 border border-orange-200 rounded-xl text-sm text-orange-900"
          >
            ⚠️ {{ warning }}
          </div>
        </div>

        <div>
          <label for="notizen" class="block text-sm font-medium text-gray-700 mb-1">Notizen</label>
          <textarea
            id="notizen"
            v-model="form.notizen"
            rows="3"
            class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
          ></textarea>
        </div>
      </form>

      <template #footer>
        <AppButton variant="ghost" @click="closeForm">Abbrechen</AppButton>
        <AppButton :loading="zaehlerStore.saving" @click="submitAblesung">
          {{ editingAblesung ? 'Speichern' : 'Erfassen' }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useZaehlerStore, type Zaehlerablesung } from '@/stores/zaehler'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppEmptyState from '@/components/ui/AppEmptyState.vue'

const zaehlerStore = useZaehlerStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const { showToast } = useToast()

const zaehlerId = computed(() => route.params.id as string)
const showForm = ref(false)
const editingAblesung = ref<Zaehlerablesung | null>(null)

const form = reactive({
  ablesedatum: '',
  zaehlerstand: '',
  ableser: '',
  ist_schaetzung: false,
  zaehlerwechsel: false,
  notizen: '',
})

const showZaehlerwechsel = computed(() => {
  if (!form.zaehlerstand || !zaehlerStore.currentZaehler?.ablesungen?.length) return false
  const stand = Number(form.zaehlerstand)
  const letzteAblesung = zaehlerStore.currentZaehler.ablesungen[0]
  return stand < Number(letzteAblesung.zaehlerstand)
})

const warnings = computed(() => {
  const list: string[] = []
  if (!form.zaehlerstand || !zaehlerStore.currentZaehler?.ablesungen?.length) return list
  const stand = Number(form.zaehlerstand)
  const letzte = zaehlerStore.currentZaehler.ablesungen[0]
  const letzterStand = Number(letzte.zaehlerstand)
  const letztesDatum = new Date(letzte.ablesedatum)
  const aktuellesDatum = form.ablesedatum ? new Date(form.ablesedatum) : new Date()

  if (stand > letzterStand) {
    const verbrauch = stand - letzterStand
    const tage = Math.max(1, Math.round((aktuellesDatum.getTime() - letztesDatum.getTime()) / (1000 * 60 * 60 * 24)))
    const verbrauchProTag = verbrauch / tage
    const typ = zaehlerStore.currentZaehler.typ
    const grenzen: Record<string, number> = {
      strom: 200,
      gas: 500,
      wasser: 5,
      waerme: 500,
      kaltwasser: 5,
      sonstiges: 1_000_000,
    }
    if (verbrauchProTag > (grenzen[typ] || grenzen.sonstiges)) {
      list.push(`Auffällig hoher Verbrauch (${verbrauchProTag.toFixed(2)} Einheiten/Tag). Bitte prüfen Sie die Ablesung auf Zahlendreher.`)
    }
    if (verbrauch === 0 && tage >= 30) {
      list.push('Kein Verbrauch über einen längeren Zeitraum erfasst. Bitte prüfen Sie, ob der Zähler in Betrieb ist.')
    }
  }
  return list
})

const ablesungen = computed(() => {
  const list = zaehlerStore.currentZaehler?.ablesungen || []
  return [...list].sort(
    (a, b) => new Date(b.ablesedatum).getTime() - new Date(a.ablesedatum).getTime(),
  )
})

function formatTyp(typ: string): string {
  const labels: Record<string, string> = {
    strom: 'Strom',
    gas: 'Gas',
    wasser: 'Wasser',
    waerme: 'Wärme',
    kaltwasser: 'Kaltwasser',
    sonstiges: 'Sonstiges',
  }
  return labels[typ] || typ
}

function formatEinheit(einheit: string): string {
  const labels: Record<string, string> = {
    kwh: 'kWh',
    kwh_m3: 'kWh / m³',
    m3: 'm³',
    sonstiges: 'Sonstiges',
  }
  return labels[einheit] || einheit
}

function formatDate(value?: string | null): string {
  if (!value) return '–'
  return new Intl.DateTimeFormat('de-DE').format(new Date(value))
}

function formatDateTime(value?: string | null): string {
  if (!value) return '–'
  return new Intl.DateTimeFormat('de-DE', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatNumber(value?: string | null): string {
  if (value === undefined || value === null) return '–'
  return new Intl.NumberFormat('de-DE', { minimumFractionDigits: 3 }).format(Number(value))
}

function resetForm(): void {
  form.ablesedatum = new Date().toISOString().split('T')[0]
  form.zaehlerstand = ''
  form.ableser = ''
  form.ist_schaetzung = false
  form.zaehlerwechsel = false
  form.notizen = ''
  editingAblesung.value = null
}

function closeForm(): void {
  showForm.value = false
  resetForm()
}

function editAblesung(ablesung: Zaehlerablesung): void {
  editingAblesung.value = ablesung
  form.ablesedatum = ablesung.ablesedatum
  form.zaehlerstand = ablesung.zaehlerstand
  form.ableser = ablesung.ableser || ''
  form.ist_schaetzung = ablesung.ist_schaetzung
  form.zaehlerwechsel = ablesung.zaehlerwechsel || false
  form.notizen = ablesung.notizen || ''
  showForm.value = true
}

async function submitAblesung(): Promise<void> {
  if (!form.ablesedatum || !form.zaehlerstand) return

  const payload = {
    ablesedatum: form.ablesedatum,
    zaehlerstand: form.zaehlerstand,
    ableser: form.ableser || null,
    ist_schaetzung: form.ist_schaetzung,
    zaehlerwechsel: form.zaehlerwechsel,
    notizen: form.notizen || null,
  }

  let ok: boolean | Zaehlerablesung | null = false
  if (editingAblesung.value) {
    const result = await zaehlerStore.updateAblesung(
      zaehlerId.value,
      editingAblesung.value.id,
      payload,
    )
    ok = result !== null
  } else {
    const result = await zaehlerStore.createAblesung(zaehlerId.value, payload)
    ok = result !== null
  }

  if (ok) {
    showToast(editingAblesung.value ? 'Ablesung aktualisiert.' : 'Ablesung erfasst.', 'success')
    closeForm()
    await zaehlerStore.fetchZaehlerDetail(zaehlerId.value)
  } else {
    showToast(zaehlerStore.error?.message || 'Speichern fehlgeschlagen.', 'error')
  }
}

async function deleteAblesung(ablesung: Zaehlerablesung): Promise<void> {
  if (!confirm('Ablesung wirklich löschen?')) return
  const ok = await zaehlerStore.deleteAblesung(zaehlerId.value, ablesung.id)
  if (ok) {
    showToast('Ablesung gelöscht.', 'success')
    await zaehlerStore.fetchZaehlerDetail(zaehlerId.value)
  } else {
    showToast(zaehlerStore.error?.message || 'Löschen fehlgeschlagen.', 'error')
  }
}

async function deleteZaehler(): Promise<void> {
  if (!zaehlerStore.currentZaehler) return
  if (!confirm('Zähler inklusive aller Ablesungen wirklich löschen?')) return
  const ok = await zaehlerStore.deleteZaehler(zaehlerStore.currentZaehler.id)
  if (ok) {
    showToast('Zähler gelöscht.', 'success')
    await router.push('/zaehler')
  } else {
    showToast(zaehlerStore.error?.message || 'Löschen fehlgeschlagen.', 'error')
  }
}

onMounted(() => {
  resetForm()
  zaehlerStore.fetchZaehlerDetail(zaehlerId.value)
})
</script>
