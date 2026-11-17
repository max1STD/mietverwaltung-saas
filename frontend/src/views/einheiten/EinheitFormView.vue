<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 lg:pt-12">
      <div class="flex items-center gap-3 mb-6">
        <button class="text-gray-500 hover:text-[#0D3B70]" @click="goBack">
          ← Zurück
        </button>
        <h1 class="text-2xl sm:text-3xl font-bold text-[#0D3B70]">
          {{ isEdit ? 'Wohneinheit bearbeiten' : 'Neue Wohneinheit' }}
        </h1>
      </div>

      <form class="space-y-6" @submit.prevent="save">
        <!-- Kern-Daten -->
        <AppCard padding="md" shadow="md">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Kern-Daten</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="e-name"
              v-model="form.name"
              label="Bezeichnung"
              placeholder="z. B. Wohnung 1"
              required
              :error="errors.name"
            />
            <AppInput
              id="e-etage"
              v-model="form.etage"
              label="Etage"
              type="number"
              placeholder="0"
              :error="errors.etage"
            />
            <AppInput
              id="e-wohnflaeche"
              v-model="form.wohnflaeche_qm"
              label="Wohnfläche (m²)"
              type="number"
              step="0.01"
              placeholder="75,00"
              required
              :error="errors.wohnflaeche_qm"
            />
            <AppInput
              id="e-nutzflaeche"
              v-model="form.nutzflaeche_qm"
              label="Nutzfläche (m²)"
              type="number"
              step="0.01"
              placeholder="85,00"
              :error="errors.nutzflaeche_qm"
            />
            <AppInput
              id="e-kaltmiete"
              v-model="form.kaltmiete"
              label="Kaltmiete (€)"
              type="number"
              step="0.01"
              placeholder="800,00"
              required
              :error="errors.kaltmiete"
            />
            <AppInput
              id="e-nebenkosten"
              v-model="form.nebenkosten_vorschuss"
              label="NK-Vorschuss (€)"
              type="number"
              step="0.01"
              placeholder="150,00"
              :error="errors.nebenkosten_vorschuss"
            />
          </div>
        </AppCard>

        <!-- Räume -->
        <AppCard padding="md" shadow="md">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Räume</h2>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <AppInput
              id="e-rooms"
              v-model="form.rooms"
              label="Zimmer gesamt"
              type="number"
              placeholder="3"
              :error="errors.rooms"
            />
            <AppInput
              id="e-wohnzimmer"
              v-model="form.wohnzimmer"
              label="Wohnzimmer"
              type="number"
              placeholder="1"
              :error="errors.wohnzimmer"
            />
            <AppInput
              id="e-schlafzimmer"
              v-model="form.schlafzimmer"
              label="Schlafzimmer"
              type="number"
              placeholder="2"
              :error="errors.schlafzimmer"
            />
            <AppInput
              id="e-badezimmer"
              v-model="form.badezimmer"
              label="Badezimmer"
              type="number"
              placeholder="1"
              :error="errors.badezimmer"
            />
          </div>
        </AppCard>

        <!-- Zusätzliche Flächen -->
        <AppCard padding="md" shadow="md">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Zusätzliche Flächen</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="e-balkon-f"
              v-model="form.balkon_flaeche_qm"
              label="Balkonfläche (m²)"
              type="number"
              step="0.01"
              :error="errors.balkon_flaeche_qm"
            />
            <AppInput
              id="e-terrasse-f"
              v-model="form.terrasse_flaeche_qm"
              label="Terrassenfläche (m²)"
              type="number"
              step="0.01"
              :error="errors.terrasse_flaeche_qm"
            />
            <AppInput
              id="e-garten-f"
              v-model="form.garten_flaeche_qm"
              label="Gartenfläche (m²)"
              type="number"
              step="0.01"
              :error="errors.garten_flaeche_qm"
            />
            <AppInput
              id="e-gewerbe-f"
              v-model="form.gewerbeflaeche_qm"
              label="Gewerbefläche (m²)"
              type="number"
              step="0.01"
              :error="errors.gewerbeflaeche_qm"
            />
          </div>
        </AppCard>

        <!-- Ausstattung -->
        <AppCard padding="md" shadow="md">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Ausstattung</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <label v-for="opt in booleanOptions" :key="opt.key" class="flex items-center gap-2 cursor-pointer">
              <input
                :checked="form[opt.key] as boolean"
                type="checkbox"
                class="w-5 h-5 rounded border-gray-300 text-[#0D3B70] focus:ring-[#0D3B70]"
                @change="form[opt.key] = ($event.target as HTMLInputElement).checked"
              />
              <span class="text-sm text-gray-700">{{ opt.label }}</span>
            </label>
          </div>
        </AppCard>

        <!-- Energie & Bau -->
        <AppCard padding="md" shadow="md">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Energie & Bau</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <AppInput
              id="e-energy"
              v-model="form.energy_class"
              label="Energieklasse"
              maxlength="2"
              placeholder="A+"
              :error="errors.energy_class"
            />
            <AppInput
              id="e-baujahr"
              v-model="form.baujahr_einheit"
              label="Baujahr Einheit"
              type="number"
              placeholder="1990"
              :error="errors.baujahr_einheit"
            />
            <div class="w-full">
              <label for="e-heizung" class="block text-sm font-medium text-gray-700 mb-1">Heizungsart</label>
              <select
                id="e-heizung"
                v-model="form.heizungsart"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="">Bitte wählen</option>
                <option v-for="o in heizungsarten" :key="o.value" :value="o.value">{{ o.label }}</option>
              </select>
            </div>
            <div class="w-full">
              <label for="e-bauweise" class="block text-sm font-medium text-gray-700 mb-1">Bauweise</label>
              <select
                id="e-bauweise"
                v-model="form.bauweise"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="">Bitte wählen</option>
                <option v-for="o in bauweisen" :key="o.value" :value="o.value">{{ o.label }}</option>
              </select>
            </div>
            <AppInput
              id="e-warmwasser"
              v-model="form.warmwasserbereitung"
              label="Warmwasserbereitung"
              placeholder="z. B. Zentral"
              :error="errors.warmwasserbereitung"
            />
            <AppInput
              id="e-fenster"
              v-model="form.fenster"
              label="Fenster"
              placeholder="z. B. Kunststoff"
              :error="errors.fenster"
            />
            <AppInput
              id="e-boden"
              v-model="form.boden"
              label="Bodenbelag"
              placeholder="z. B. Fliesen / Laminat"
              :error="errors.boden"
            />
            <AppInput
              id="e-sanitaer"
              v-model="form.sanitaer"
              label="Sanitär"
              placeholder="z. B. Standard"
              :error="errors.sanitaer"
            />
            <AppInput
              id="e-kueche"
              v-model="form.kueche"
              label="Küche"
              placeholder="z. B. Einbauküche"
              :error="errors.kueche"
            />
            <div class="w-full">
              <label for="e-energieausweis" class="block text-sm font-medium text-gray-700 mb-1">Energieausweis-Art</label>
              <select
                id="e-energieausweis"
                v-model="form.energieausweis_art"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="">Bitte wählen</option>
                <option value="verbrauchsausweis">Verbrauchsausweis</option>
                <option value="bedarfsausweis">Bedarfsausweis</option>
              </select>
            </div>
            <AppInput
              id="e-kennwert"
              v-model="form.energieverbrauch_kennwert"
              label="Verbrauchskennwert"
              type="number"
              step="0.01"
              :error="errors.energieverbrauch_kennwert"
            />
            <AppInput
              id="e-verbrauchsklasse"
              v-model="form.energieverbrauch_klasse"
              label="Verbrauchsklasse"
              maxlength="10"
              :error="errors.energieverbrauch_klasse"
            />
          </div>
        </AppCard>

        <!-- Zustand & Rechtliches -->
        <AppCard padding="md" shadow="md">
          <h2 class="text-lg font-semibold text-[#0D3B70] mb-4">Zustand & Rechtliches</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="w-full">
              <label for="e-renovierung" class="block text-sm font-medium text-gray-700 mb-1">Renovierungsstatus</label>
              <select
                id="e-renovierung"
                v-model="form.renovierungsstatus"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="">Bitte wählen</option>
                <option v-for="o in renovierungsstatusOptionen" :key="o.value" :value="o.value">{{ o.label }}</option>
              </select>
            </div>
            <div class="w-full">
              <label for="e-zustand" class="block text-sm font-medium text-gray-700 mb-1">Zustand</label>
              <select
                id="e-zustand"
                v-model="form.zustand"
                class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              >
                <option value="">Bitte wählen</option>
                <option v-for="o in zustandOptionen" :key="o.value" :value="o.value">{{ o.label }}</option>
              </select>
            </div>
            <AppInput
              id="e-last-renovation"
              v-model="form.last_renovation"
              label="Letzte Renovierung"
              type="date"
              :error="errors.last_renovation"
            />
            <AppInput
              id="e-available"
              v-model="form.available_from"
              label="Verfügbar ab"
              type="date"
              :error="errors.available_from"
            />
            <AppInput
              id="e-bewohnbar"
              v-model="form.bewohnbar_ab"
              label="Bewohnbar ab"
              type="date"
              :error="errors.bewohnbar_ab"
            />
            <div class="flex items-center gap-2 sm:col-span-2">
              <input
                id="e-denkmalschutz"
                v-model="form.denkmalschutz"
                type="checkbox"
                class="w-5 h-5 rounded border-gray-300 text-[#0D3B70] focus:ring-[#0D3B70]"
              />
              <label for="e-denkmalschutz" class="text-sm text-gray-700">Denkmalschutz</label>
              <AppInput
                v-if="form.denkmalschutz"
                id="e-denkmalschutz-bis"
                v-model="form.denkmalschutz_bis"
                label="Denkmalschutz bis"
                type="date"
                class="ml-4 flex-1"
                :error="errors.denkmalschutz_bis"
              />
            </div>
          </div>

          <div class="mt-4">
            <label for="e-anmerkungen" class="block text-sm font-medium text-gray-700 mb-1">Anmerkungen</label>
            <textarea
              id="e-anmerkungen"
              v-model="form.anmerkungen"
              rows="4"
              maxlength="4000"
              class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
              placeholder="Weitere Hinweise zur Einheit …"
            />
          </div>
        </AppCard>

        <div class="flex justify-end gap-3">
          <AppButton type="button" variant="ghost" @click="goBack">
            Abbrechen
          </AppButton>
          <AppButton type="submit" :loading="objekteStore.saving">
            {{ isEdit ? 'Änderungen speichern' : 'Einheit anlegen' }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useObjekteStore, type Einheit } from '@/stores/objekte'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'

interface FormState {
  name: string
  etage: string
  wohnflaeche_qm: string
  nutzflaeche_qm: string
  kaltmiete: string
  nebenkosten_vorschuss: string
  rooms: string
  wohnzimmer: string
  schlafzimmer: string
  badezimmer: string
  balkon_flaeche_qm: string
  terrasse_flaeche_qm: string
  garten_flaeche_qm: string
  gewerbeflaeche_qm: string
  balkon: boolean
  terrasse: boolean
  garten: boolean
  garage: boolean
  stellplatz: boolean
  keller: boolean
  aufzug: boolean
  barrierefrei: boolean
  moebliert: boolean
  energy_class: string
  baujahr_einheit: string
  heizungsart: string
  warmwasserbereitung: string
  fenster: string
  boden: string
  sanitaer: string
  kueche: string
  energieausweis_art: string
  energieverbrauch_kennwert: string
  energieverbrauch_klasse: string
  bauweise: string
  denkmalschutz: boolean
  denkmalschutz_bis: string
  last_renovation: string
  renovierungsstatus: string
  zustand: string
  available_from: string
  bewohnbar_ab: string
  anmerkungen: string
  [key: string]: string | boolean
}

const route = useRoute()
const router = useRouter()
const objekteStore = useObjekteStore()
const { showToast } = useToast()

const einheitId = computed(() => String(route.params.id))
const isEdit = computed(() => !!einheitId.value)
const objektId = computed(() => String(route.query.objekt || ''))

const booleanOptions = [
  { key: 'balkon', label: 'Balkon' },
  { key: 'terrasse', label: 'Terrasse' },
  { key: 'garten', label: 'Garten' },
  { key: 'garage', label: 'Garage' },
  { key: 'stellplatz', label: 'Stellplatz' },
  { key: 'keller', label: 'Keller' },
  { key: 'aufzug', label: 'Aufzug' },
  { key: 'barrierefrei', label: 'Barrierefrei' },
  { key: 'moebliert', label: 'Möbliert' },
]

const heizungsarten = [
  { value: 'gasetagenheizung', label: 'Gas-Etagenheizung' },
  { value: 'gaszentralheizung', label: 'Gas-Zentralheizung' },
  { value: 'fernwaerme', label: 'Fernwärme' },
  { value: 'oelheizung', label: 'Ölheizung' },
  { value: 'waermepumpe', label: 'Wärmepumpe' },
  { value: 'holzheizung', label: 'Holzheizung' },
  { value: 'elektroheizung', label: 'Elektroheizung' },
  { value: 'sonstige', label: 'Sonstige' },
]

const bauweisen = [
  { value: 'massiv', label: 'Massivbau' },
  { value: 'fertigteil', label: 'Fertigteil' },
  { value: 'holz', label: 'Holzbau' },
  { value: 'stahl', label: 'Stahlbau' },
  { value: 'sonstige', label: 'Sonstige' },
]

const renovierungsstatusOptionen = [
  { value: 'keine_renovierung', label: 'Keine Renovierung' },
  { value: 'renoviert', label: 'Renoviert' },
  { value: 'teilrenoviert', label: 'Teilrenoviert' },
  { value: 'renovierungsbeduerftig', label: 'Renovierungsbedürftig' },
  { value: 'in_renovierung', label: 'In Renovierung' },
]

const zustandOptionen = [
  { value: 'neuwertig', label: 'Neuwertig' },
  { value: 'gut', label: 'Gut' },
  { value: 'mittel', label: 'Mittel' },
  { value: 'abnutzungsspuren', label: 'Abnutzungsspuren' },
  { value: 'renovierungsbeduerftig', label: 'Renovierungsbedürftig' },
]

const form = reactive<FormState>({
  name: '',
  etage: '',
  wohnflaeche_qm: '',
  nutzflaeche_qm: '',
  kaltmiete: '',
  nebenkosten_vorschuss: '',
  rooms: '',
  wohnzimmer: '',
  schlafzimmer: '',
  badezimmer: '',
  balkon_flaeche_qm: '',
  terrasse_flaeche_qm: '',
  garten_flaeche_qm: '',
  gewerbeflaeche_qm: '',
  balkon: false,
  terrasse: false,
  garten: false,
  garage: false,
  stellplatz: false,
  keller: false,
  aufzug: false,
  barrierefrei: false,
  moebliert: false,
  energy_class: '',
  baujahr_einheit: '',
  heizungsart: '',
  warmwasserbereitung: '',
  fenster: '',
  boden: '',
  sanitaer: '',
  kueche: '',
  energieausweis_art: '',
  energieverbrauch_kennwert: '',
  energieverbrauch_klasse: '',
  bauweise: '',
  denkmalschutz: false,
  denkmalschutz_bis: '',
  last_renovation: '',
  renovierungsstatus: '',
  zustand: '',
  available_from: '',
  bewohnbar_ab: '',
  anmerkungen: '',
})

const errors = reactive({
  name: '',
  etage: '',
  wohnflaeche_qm: '',
  nutzflaeche_qm: '',
  kaltmiete: '',
  nebenkosten_vorschuss: '',
  rooms: '',
  wohnzimmer: '',
  schlafzimmer: '',
  badezimmer: '',
  balkon_flaeche_qm: '',
  terrasse_flaeche_qm: '',
  garten_flaeche_qm: '',
  gewerbeflaeche_qm: '',
  energy_class: '',
  baujahr_einheit: '',
  heizungsart: '',
  warmwasserbereitung: '',
  fenster: '',
  boden: '',
  sanitaer: '',
  kueche: '',
  energieausweis_art: '',
  energieverbrauch_kennwert: '',
  energieverbrauch_klasse: '',
  bauweise: '',
  last_renovation: '',
  available_from: '',
  bewohnbar_ab: '',
  denkmalschutz_bis: '',
})

function clearErrors(): void {
  Object.keys(errors).forEach((k) => {
    ;(errors as Record<string, string>)[k] = ''
  })
}

function validate(): boolean {
  clearErrors()
  let valid = true
  if (!form.name.trim()) {
    errors.name = 'Bezeichnung ist erforderlich.'
    valid = false
  }
  if (!form.wohnflaeche_qm || Number(form.wohnflaeche_qm) <= 0) {
    errors.wohnflaeche_qm = 'Wohnfläche muss größer als 0 sein.'
    valid = false
  }
  if (!form.kaltmiete || Number(form.kaltmiete) < 0) {
    errors.kaltmiete = 'Kaltmiete ist erforderlich.'
    valid = false
  }
  return valid
}

function numberOrUndefined(value: string): number | undefined {
  const n = value === '' ? NaN : Number(value)
  return Number.isNaN(n) ? undefined : n
}

function buildPayload(): Partial<Einheit> {
  return {
    name: form.name,
    etage: numberOrUndefined(form.etage),
    wohnflaeche_qm: numberOrUndefined(form.wohnflaeche_qm),
    nutzflaeche_qm: numberOrUndefined(form.nutzflaeche_qm),
    kaltmiete: numberOrUndefined(form.kaltmiete),
    nebenkosten_vorschuss: numberOrUndefined(form.nebenkosten_vorschuss),
    rooms: numberOrUndefined(form.rooms),
    wohnzimmer: numberOrUndefined(form.wohnzimmer),
    schlafzimmer: numberOrUndefined(form.schlafzimmer),
    badezimmer: numberOrUndefined(form.badezimmer),
    balkon_flaeche_qm: numberOrUndefined(form.balkon_flaeche_qm),
    terrasse_flaeche_qm: numberOrUndefined(form.terrasse_flaeche_qm),
    garten_flaeche_qm: numberOrUndefined(form.garten_flaeche_qm),
    gewerbeflaeche_qm: numberOrUndefined(form.gewerbeflaeche_qm),
    balkon: form.balkon,
    terrasse: form.terrasse,
    garten: form.garten,
    garage: form.garage,
    stellplatz: form.stellplatz,
    keller: form.keller,
    aufzug: form.aufzug,
    barrierefrei: form.barrierefrei,
    moebliert: form.moebliert,
    energy_class: form.energy_class || undefined,
    baujahr_einheit: numberOrUndefined(form.baujahr_einheit),
    heizungsart: form.heizungsart || undefined,
    warmwasserbereitung: form.warmwasserbereitung || undefined,
    fenster: form.fenster || undefined,
    boden: form.boden || undefined,
    sanitaer: form.sanitaer || undefined,
    kueche: form.kueche || undefined,
    energieausweis_art: form.energieausweis_art || undefined,
    energieverbrauch_kennwert: numberOrUndefined(form.energieverbrauch_kennwert),
    energieverbrauch_klasse: form.energieverbrauch_klasse || undefined,
    bauweise: form.bauweise || undefined,
    denkmalschutz: form.denkmalschutz,
    denkmalschutz_bis: form.denkmalschutz_bis || undefined,
    last_renovation: form.last_renovation || undefined,
    renovierungsstatus: form.renovierungsstatus || undefined,
    zustand: form.zustand || undefined,
    available_from: form.available_from || undefined,
    bewohnbar_ab: form.bewohnbar_ab || undefined,
    anmerkungen: form.anmerkungen || undefined,
  }
}

function populateForm(e: Einheit): void {
  form.name = e.name || ''
  form.etage = e.etage != null ? String(e.etage) : ''
  form.wohnflaeche_qm = e.wohnflaeche_qm != null ? String(e.wohnflaeche_qm) : ''
  form.nutzflaeche_qm = e.nutzflaeche_qm != null ? String(e.nutzflaeche_qm) : ''
  form.kaltmiete = e.kaltmiete != null ? String(e.kaltmiete) : ''
  form.nebenkosten_vorschuss = e.nebenkosten_vorschuss != null ? String(e.nebenkosten_vorschuss) : ''
  form.rooms = e.rooms != null ? String(e.rooms) : ''
  form.wohnzimmer = e.wohnzimmer != null ? String(e.wohnzimmer) : ''
  form.schlafzimmer = e.schlafzimmer != null ? String(e.schlafzimmer) : ''
  form.badezimmer = e.badezimmer != null ? String(e.badezimmer) : ''
  form.balkon_flaeche_qm = e.balkon_flaeche_qm != null ? String(e.balkon_flaeche_qm) : ''
  form.terrasse_flaeche_qm = e.terrasse_flaeche_qm != null ? String(e.terrasse_flaeche_qm) : ''
  form.garten_flaeche_qm = e.garten_flaeche_qm != null ? String(e.garten_flaeche_qm) : ''
  form.gewerbeflaeche_qm = e.gewerbeflaeche_qm != null ? String(e.gewerbeflaeche_qm) : ''
  form.balkon = !!e.balkon
  form.terrasse = !!e.terrasse
  form.garten = !!e.garten
  form.garage = !!e.garage
  form.stellplatz = !!e.stellplatz
  form.keller = !!e.keller
  form.aufzug = !!e.aufzug
  form.barrierefrei = !!e.barrierefrei
  form.moebliert = !!e.moebliert
  form.energy_class = e.energy_class || ''
  form.baujahr_einheit = e.baujahr_einheit != null ? String(e.baujahr_einheit) : ''
  form.heizungsart = e.heizungsart || ''
  form.warmwasserbereitung = e.warmwasserbereitung || ''
  form.fenster = e.fenster || ''
  form.boden = e.boden || ''
  form.sanitaer = e.sanitaer || ''
  form.kueche = e.kueche || ''
  form.energieausweis_art = e.energieausweis_art || ''
  form.energieverbrauch_kennwert = e.energieverbrauch_kennwert != null ? String(e.energieverbrauch_kennwert) : ''
  form.energieverbrauch_klasse = e.energieverbrauch_klasse || ''
  form.bauweise = e.bauweise || ''
  form.denkmalschutz = !!e.denkmalschutz
  form.denkmalschutz_bis = e.denkmalschutz_bis || ''
  form.last_renovation = e.last_renovation || ''
  form.renovierungsstatus = e.renovierungsstatus || ''
  form.zustand = e.zustand || ''
  form.available_from = e.available_from || ''
  form.bewohnbar_ab = e.bewohnbar_ab || ''
  form.anmerkungen = e.anmerkungen || ''
}

async function save(): Promise<void> {
  if (!validate()) return

  const payload = buildPayload()

  if (isEdit.value) {
    const updated = await objekteStore.updateEinheit(einheitId.value, payload)
    if (updated) {
      showToast('Wohneinheit aktualisiert.', 'success')
      router.push(`/einheiten/${updated.id}`)
    } else {
      showToast(objekteStore.error?.message || 'Fehler beim Aktualisieren.', 'error')
    }
  } else {
    const einheit = await objekteStore.createEinheit(objektId.value, payload)
    if (einheit) {
      showToast('Wohneinheit angelegt.', 'success')
      router.push(`/einheiten/${einheit.id}`)
    } else {
      showToast(objekteStore.error?.message || 'Fehler beim Anlegen.', 'error')
    }
  }
}

function goBack(): void {
  if (isEdit.value) {
    router.push(`/einheiten/${einheitId.value}`)
  } else if (objektId.value) {
    router.push(`/objekte/${objektId.value}`)
  } else {
    router.push('/objekte')
  }
}

onMounted(async () => {
  if (isEdit.value) {
    // Lade ueber Objekt-Liste, falls nocht nicht vorhanden
    await objekteStore.fetchObjekte()
    const all = objekteStore.objekte.flatMap((o) => o.einheiten || [])
    const found = all.find((e) => e.id === einheitId.value || e.public_id === einheitId.value)
    if (found) {
      populateForm(found)
    } else {
      showToast('Einheit nicht gefunden.', 'error')
      goBack()
    }
  }
})
</script>
