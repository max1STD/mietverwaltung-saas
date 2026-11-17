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
        <form class="space-y-8" @submit.prevent="handleSubmit">
          <!-- Basis -->
          <section>
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Basis</h2>
            <div class="space-y-4">
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

              <ul
                v-if="streetSuggestions.length > 0"
                class="-mt-2 bg-white border border-gray-200 rounded-xl shadow-sm max-h-48 overflow-auto"
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

              <AppInput
                id="adresszusatz"
                v-model="form.adresszusatz"
                label="Adresszusatz"
                placeholder="z. B. Hinterhaus"
                :error="errors.adresszusatz"
              />

              <div class="grid grid-cols-3 gap-4">
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
                <AppInput
                  id="land"
                  v-model="form.land"
                  label="Land (ISO)"
                  placeholder="DE"
                  maxlength="2"
                  :error="errors.land"
                />
              </div>
            </div>
          </section>

          <!-- Allgemein -->
          <section>
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Allgemein</h2>
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

              <div>
                <label for="zustand" class="block text-sm font-medium text-gray-700 mb-1">Zustand</label>
                <select
                  id="zustand"
                  v-model="form.zustand"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                >
                  <option value="">Bitte wählen</option>
                  <option value="neuwertig">Neuwertig</option>
                  <option value="gut">Gut</option>
                  <option value="mittel">Mittel</option>
                  <option value="abnutzungsspuren">Abnutzungsspuren</option>
                  <option value="renovierungsbeduerftig">Renovierungsbedürftig</option>
                </select>
              </div>

              <AppInput
                id="baujahr"
                v-model="form.baujahr"
                label="Baujahr"
                type="number"
                placeholder="1990"
                :error="errors.baujahr"
              />
              <AppInput
                id="baujahr_objekt"
                v-model="form.baujahr_objekt"
                label="Baujahr Objekt"
                type="number"
                placeholder="1990"
                :error="errors.baujahr_objekt"
              />
              <AppInput
                id="anzahl_einheiten"
                v-model="form.anzahl_einheiten"
                label="Anzahl Einheiten"
                type="number"
                placeholder="1"
                :error="errors.anzahl_einheiten"
              />

              <div>
                <label for="bauweise" class="block text-sm font-medium text-gray-700 mb-1">Bauweise</label>
                <select
                  id="bauweise"
                  v-model="form.bauweise"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                >
                  <option value="">Bitte wählen</option>
                  <option value="massiv">Massiv</option>
                  <option value="fertigteil">Fertigteil</option>
                  <option value="holz">Holz</option>
                  <option value="stahl">Stahl</option>
                  <option value="sonstige">Sonstige</option>
                </select>
              </div>
            </div>
          </section>

          <!-- Flächen -->
          <section>
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Flächen (m²)</h2>
            <div class="grid grid-cols-2 gap-4">
              <AppInput
                id="grundstuecksflaeche_qm"
                v-model="form.grundstuecksflaeche_qm"
                label="Grundstücksfläche"
                type="number"
                step="0.01"
                placeholder="0,00"
                :error="errors.grundstuecksflaeche_qm"
              />
              <AppInput
                id="wohnflaeche_gesamt_qm"
                v-model="form.wohnflaeche_gesamt_qm"
                label="Wohnfläche gesamt"
                type="number"
                step="0.01"
                placeholder="0,00"
                :error="errors.wohnflaeche_gesamt_qm"
              />
              <AppInput
                id="nutzflaeche_gesamt_qm"
                v-model="form.nutzflaeche_gesamt_qm"
                label="Nutzfläche gesamt"
                type="number"
                step="0.01"
                placeholder="0,00"
                :error="errors.nutzflaeche_gesamt_qm"
              />
              <AppInput
                id="vermietbare_flaeche_qm"
                v-model="form.vermietbare_flaeche_qm"
                label="Vermietbare Fläche"
                type="number"
                step="0.01"
                placeholder="0,00"
                :error="errors.vermietbare_flaeche_qm"
              />
            </div>
          </section>

          <!-- Energie -->
          <section>
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Energie & Heizung</h2>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="energieausweis_art" class="block text-sm font-medium text-gray-700 mb-1">Energieausweis</label>
                <select
                  id="energieausweis_art"
                  v-model="form.energieausweis_art"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                >
                  <option value="">Bitte wählen</option>
                  <option value="verbrauchsausweis">Verbrauchsausweis</option>
                  <option value="bedarfsausweis">Bedarfsausweis</option>
                </select>
              </div>
              <AppInput
                id="energieausweis_gueltig_bis"
                v-model="form.energieausweis_gueltig_bis"
                label="Gültig bis"
                type="date"
                :error="errors.energieausweis_gueltig_bis"
              />
              <AppInput
                id="energieverbrauch_kennwert"
                v-model="form.energieverbrauch_kennwert"
                label="Verbrauchskennwert (kWh/m²·a)"
                type="number"
                step="0.01"
                placeholder="0,00"
                :error="errors.energieverbrauch_kennwert"
              />
              <AppInput
                id="energieverbrauch_klasse"
                v-model="form.energieverbrauch_klasse"
                label="Energieklasse"
                placeholder="A+"
                maxlength="10"
                :error="errors.energieverbrauch_klasse"
              />

              <div>
                <label for="heizungsart" class="block text-sm font-medium text-gray-700 mb-1">Heizungsart</label>
                <select
                  id="heizungsart"
                  v-model="form.heizungsart"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                >
                  <option value="">Bitte wählen</option>
                  <option value="gasetagenheizung">Gas-Etagenheizung</option>
                  <option value="gaszentralheizung">Gas-Zentralheizung</option>
                  <option value="fernwaerme">Fernwärme</option>
                  <option value="oelheizung">Ölheizung</option>
                  <option value="waermepumpe">Wärmepumpe</option>
                  <option value="holzheizung">Holzheizung</option>
                  <option value="elektroheizung">Elektroheizung</option>
                  <option value="sonstige">Sonstige</option>
                </select>
              </div>

              <AppInput
                id="warmwasserbereitung"
                v-model="form.warmwasserbereitung"
                label="Warmwasserbereitung"
                placeholder="Zentral / Decentral"
                maxlength="50"
                :error="errors.warmwasserbereitung"
              />

              <BoolSelect id="solaranlage" v-model="form.solaranlage" label="Solaranlage" />
            </div>
          </section>

          <!-- Finanzierung -->
          <section>
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Finanzierung & Mieten</h2>
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
              <AppCurrencyInput
                id="eigenkapital"
                v-model="form.eigenkapital"
                label="Eigenkapital"
                placeholder="50.000,00"
                :error="errors.eigenkapital"
              />
              <AppCurrencyInput
                id="darlehen_betrag"
                v-model="form.darlehen_betrag"
                label="Darlehensbetrag"
                placeholder="200.000,00"
                :error="errors.darlehen_betrag"
              />
              <AppInput
                id="zinssatz"
                v-model="form.zinssatz"
                label="Zinssatz (%)"
                type="number"
                step="0.01"
                placeholder="3,5"
                :error="errors.zinssatz"
              />
              <AppInput
                id="tilgung"
                v-model="form.tilgung"
                label="Tilgung (%)"
                type="number"
                step="0.01"
                placeholder="2,0"
                :error="errors.tilgung"
              />
              <AppCurrencyInput
                id="monatliche_rate"
                v-model="form.monatliche_rate"
                label="Monatliche Rate"
                placeholder="1.000,00"
                :error="errors.monatliche_rate"
              />
              <AppCurrencyInput
                id="gesamtmiete_ist"
                v-model="form.gesamtmiete_ist"
                label="Gesamtmiete IST"
                placeholder="2.000,00"
                :error="errors.gesamtmiete_ist"
              />
              <AppCurrencyInput
                id="gesamtmiete_soll"
                v-model="form.gesamtmiete_soll"
                label="Gesamtmiete SOLL"
                placeholder="2.200,00"
                :error="errors.gesamtmiete_soll"
              />
            </div>
          </section>

          <!-- Ausstattung -->
          <section>
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Ausstattung & Sonstiges</h2>
            <div class="grid grid-cols-2 gap-4">
              <BoolSelect id="denkmalschutz" v-model="form.denkmalschutz" label="Denkmalschutz" />
              <AppInput
                id="denkmalschutz_bis"
                v-model="form.denkmalschutz_bis"
                label="Denkmalschutz gültig bis"
                type="date"
                :error="errors.denkmalschutz_bis"
              />
              <BoolSelect id="barrierefrei" v-model="form.barrierefrei" label="Barrierefrei" />
              <BoolSelect id="aufzug" v-model="form.aufzug" label="Aufzug" />
              <BoolSelect id="gartennutzung" v-model="form.gartennutzung" label="Gartennutzung" />
            </div>
          </section>

          <!-- Lage / Notizen -->
          <section>
            <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Lage & Notizen</h2>
            <div class="space-y-4">
              <div>
                <label for="lagebeschreibung" class="block text-sm font-medium text-gray-700 mb-1">Lagebeschreibung</label>
                <textarea
                  id="lagebeschreibung"
                  v-model="form.lagebeschreibung"
                  rows="3"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                  :class="{ 'border-red-500': errors.lagebeschreibung }"
                  placeholder="Lage, Umgebung, ÖPNV …"
                ></textarea>
                <p v-if="errors.lagebeschreibung" class="mt-1 text-xs text-red-600">{{ errors.lagebeschreibung }}</p>
              </div>

              <div>
                <label for="anmerkungen" class="block text-sm font-medium text-gray-700 mb-1">Anmerkungen</label>
                <textarea
                  id="anmerkungen"
                  v-model="form.anmerkungen"
                  rows="3"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                  :class="{ 'border-red-500': errors.anmerkungen }"
                  placeholder="Weitere Anmerkungen …"
                ></textarea>
                <p v-if="errors.anmerkungen" class="mt-1 text-xs text-red-600">{{ errors.anmerkungen }}</p>
              </div>

              <div>
                <label for="notizen" class="block text-sm font-medium text-gray-700 mb-1">Interne Notizen</label>
                <textarea
                  id="notizen"
                  v-model="form.notizen"
                  rows="3"
                  class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
                  :class="{ 'border-red-500': errors.notizen }"
                  placeholder="Interne Notizen …"
                ></textarea>
                <p v-if="errors.notizen" class="mt-1 text-xs text-red-600">{{ errors.notizen }}</p>
              </div>
            </div>
          </section>

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
import apiClient from '@/api/client'
import AppCard from '@/components/ui/AppCard.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppCurrencyInput from '@/components/ui/AppCurrencyInput.vue'
import BoolSelect from '@/components/ui/BoolSelect.vue'

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

type BoolFormValue = 'true' | 'false' | ''

function toBoolForm(value: boolean | null | undefined): BoolFormValue {
  if (value === true) return 'true'
  if (value === false) return 'false'
  return ''
}

function fromBoolForm(value: BoolFormValue): boolean | null {
  if (value === 'true') return true
  if (value === 'false') return false
  return null
}

const form = reactive({
  name: '',
  address: '',
  plz: '',
  ort: '',
  land: '',
  adresszusatz: '',
  typ: '' as ObjektTyp | '',
  baujahr: '',
  baujahr_objekt: '',
  anzahl_einheiten: '',
  bauweise: '',
  zustand: '',
  grundstuecksflaeche_qm: '',
  wohnflaeche_gesamt_qm: '',
  nutzflaeche_gesamt_qm: '',
  vermietbare_flaeche_qm: '',
  energieausweis_art: '',
  energieausweis_gueltig_bis: '',
  energieverbrauch_kennwert: '',
  energieverbrauch_klasse: '',
  heizungsart: '',
  warmwasserbereitung: '',
  solaranlage: '' as BoolFormValue,
  kaufpreis: '',
  kaufdatum: '',
  eigenkapital: '',
  darlehen_betrag: '',
  zinssatz: '',
  tilgung: '',
  monatliche_rate: '',
  gesamtmiete_ist: '',
  gesamtmiete_soll: '',
  denkmalschutz: '' as BoolFormValue,
  denkmalschutz_bis: '',
  barrierefrei: '' as BoolFormValue,
  aufzug: '' as BoolFormValue,
  gartennutzung: '' as BoolFormValue,
  lagebeschreibung: '',
  anmerkungen: '',
  notizen: '',
})

const errors = reactive<Record<keyof typeof form, string>>({
  name: '',
  address: '',
  plz: '',
  ort: '',
  land: '',
  adresszusatz: '',
  typ: '',
  baujahr: '',
  baujahr_objekt: '',
  anzahl_einheiten: '',
  bauweise: '',
  zustand: '',
  grundstuecksflaeche_qm: '',
  wohnflaeche_gesamt_qm: '',
  nutzflaeche_gesamt_qm: '',
  vermietbare_flaeche_qm: '',
  energieausweis_art: '',
  energieausweis_gueltig_bis: '',
  energieverbrauch_kennwert: '',
  energieverbrauch_klasse: '',
  heizungsart: '',
  warmwasserbereitung: '',
  solaranlage: '',
  kaufpreis: '',
  kaufdatum: '',
  eigenkapital: '',
  darlehen_betrag: '',
  zinssatz: '',
  tilgung: '',
  monatliche_rate: '',
  gesamtmiete_ist: '',
  gesamtmiete_soll: '',
  denkmalschutz: '',
  denkmalschutz_bis: '',
  barrierefrei: '',
  aufzug: '',
  gartennutzung: '',
  lagebeschreibung: '',
  anmerkungen: '',
  notizen: '',
})

function clearErrors(): void {
  for (const key of Object.keys(errors) as (keyof typeof errors)[]) {
    errors[key] = ''
  }
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
  form.land = objekt.land || ''
  form.adresszusatz = objekt.adresszusatz || ''
  form.typ = (objekt.typ as ObjektTyp) || ''
  form.baujahr = objekt.baujahr ? String(objekt.baujahr) : ''
  form.baujahr_objekt = objekt.baujahr_objekt ? String(objekt.baujahr_objekt) : ''
  form.anzahl_einheiten = objekt.anzahl_einheiten ? String(objekt.anzahl_einheiten) : ''
  form.bauweise = objekt.bauweise || ''
  form.zustand = objekt.zustand || ''
  form.grundstuecksflaeche_qm = objekt.grundstuecksflaeche_qm ? String(objekt.grundstuecksflaeche_qm) : ''
  form.wohnflaeche_gesamt_qm = objekt.wohnflaeche_gesamt_qm ? String(objekt.wohnflaeche_gesamt_qm) : ''
  form.nutzflaeche_gesamt_qm = objekt.nutzflaeche_gesamt_qm ? String(objekt.nutzflaeche_gesamt_qm) : ''
  form.vermietbare_flaeche_qm = objekt.vermietbare_flaeche_qm ? String(objekt.vermietbare_flaeche_qm) : ''
  form.energieausweis_art = objekt.energieausweis_art || ''
  form.energieausweis_gueltig_bis = objekt.energieausweis_gueltig_bis || ''
  form.energieverbrauch_kennwert = objekt.energieverbrauch_kennwert ? String(objekt.energieverbrauch_kennwert) : ''
  form.energieverbrauch_klasse = objekt.energieverbrauch_klasse || ''
  form.heizungsart = objekt.heizungsart || ''
  form.warmwasserbereitung = objekt.warmwasserbereitung || ''
  form.solaranlage = toBoolForm(objekt.solaranlage)
  form.kaufpreis = objekt.kaufpreis ? String(objekt.kaufpreis) : ''
  form.kaufdatum = objekt.kaufdatum || ''
  form.eigenkapital = objekt.eigenkapital ? String(objekt.eigenkapital) : ''
  form.darlehen_betrag = objekt.darlehen_betrag ? String(objekt.darlehen_betrag) : ''
  form.zinssatz = objekt.zinssatz ? String(objekt.zinssatz) : ''
  form.tilgung = objekt.tilgung ? String(objekt.tilgung) : ''
  form.monatliche_rate = objekt.monatliche_rate ? String(objekt.monatliche_rate) : ''
  form.gesamtmiete_ist = objekt.gesamtmiete_ist ? String(objekt.gesamtmiete_ist) : ''
  form.gesamtmiete_soll = objekt.gesamtmiete_soll ? String(objekt.gesamtmiete_soll) : ''
  form.denkmalschutz = toBoolForm(objekt.denkmalschutz)
  form.denkmalschutz_bis = objekt.denkmalschutz_bis || ''
  form.barrierefrei = toBoolForm(objekt.barrierefrei)
  form.aufzug = toBoolForm(objekt.aufzug)
  form.gartennutzung = toBoolForm(objekt.gartennutzung)
  form.lagebeschreibung = objekt.lagebeschreibung || ''
  form.anmerkungen = objekt.anmerkungen || ''
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

function validateYear(value: string, field: keyof typeof errors): boolean {
  if (!value) return true
  const year = Number(value)
  const currentYear = new Date().getFullYear()
  if (Number.isNaN(year) || year < 1000 || year > currentYear + 5) {
    errors[field] = `Jahr muss zwischen 1000 und ${currentYear + 5} liegen.`
    return false
  }
  return true
}

function validateNonNegativeNumber(value: string, field: keyof typeof errors, label: string): boolean {
  if (!value) return true
  const num = Number(value)
  if (Number.isNaN(num) || num < 0) {
    errors[field] = `${label} darf nicht negativ sein.`
    return false
  }
  return true
}

function validatePercent(value: string, field: keyof typeof errors, label: string): boolean {
  if (!value) return true
  const num = Number(value)
  if (Number.isNaN(num) || num < 0 || num > 100) {
    errors[field] = `${label} muss zwischen 0 und 100 liegen.`
    return false
  }
  return true
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

  if (!validateYear(form.baujahr, 'baujahr')) valid = false
  if (!validateYear(form.baujahr_objekt, 'baujahr_objekt')) valid = false
  if (!validateNonNegativeNumber(form.anzahl_einheiten, 'anzahl_einheiten', 'Anzahl Einheiten')) valid = false
  if (!validateNonNegativeNumber(form.grundstuecksflaeche_qm, 'grundstuecksflaeche_qm', 'Grundstücksfläche')) valid = false
  if (!validateNonNegativeNumber(form.wohnflaeche_gesamt_qm, 'wohnflaeche_gesamt_qm', 'Wohnfläche')) valid = false
  if (!validateNonNegativeNumber(form.nutzflaeche_gesamt_qm, 'nutzflaeche_gesamt_qm', 'Nutzfläche')) valid = false
  if (!validateNonNegativeNumber(form.vermietbare_flaeche_qm, 'vermietbare_flaeche_qm', 'Vermietbare Fläche')) valid = false
  if (!validateNonNegativeNumber(form.energieverbrauch_kennwert, 'energieverbrauch_kennwert', 'Verbrauchskennwert')) valid = false
  if (!validatePercent(form.zinssatz, 'zinssatz', 'Zinssatz')) valid = false
  if (!validatePercent(form.tilgung, 'tilgung', 'Tilgung')) valid = false

  return valid
}

function optionalNumber(value: string): number | undefined {
  return value ? Number(value) : undefined
}

function buildPayload(): Partial<Objekt> {
  return {
    name: form.name.trim(),
    address: form.address.trim() || undefined,
    plz: form.plz.trim() || undefined,
    ort: form.ort.trim() || undefined,
    land: form.land.trim().toUpperCase() || undefined,
    adresszusatz: form.adresszusatz.trim() || undefined,
    typ: form.typ || undefined,
    baujahr: optionalNumber(form.baujahr),
    baujahr_objekt: optionalNumber(form.baujahr_objekt),
    anzahl_einheiten: optionalNumber(form.anzahl_einheiten),
    bauweise: form.bauweise || undefined,
    zustand: form.zustand || undefined,
    grundstuecksflaeche_qm: optionalNumber(form.grundstuecksflaeche_qm),
    wohnflaeche_gesamt_qm: optionalNumber(form.wohnflaeche_gesamt_qm),
    nutzflaeche_gesamt_qm: optionalNumber(form.nutzflaeche_gesamt_qm),
    vermietbare_flaeche_qm: optionalNumber(form.vermietbare_flaeche_qm),
    energieausweis_art: form.energieausweis_art || undefined,
    energieausweis_gueltig_bis: form.energieausweis_gueltig_bis || undefined,
    energieverbrauch_kennwert: optionalNumber(form.energieverbrauch_kennwert),
    energieverbrauch_klasse: form.energieverbrauch_klasse.trim() || undefined,
    heizungsart: form.heizungsart || undefined,
    warmwasserbereitung: form.warmwasserbereitung.trim() || undefined,
    solaranlage: fromBoolForm(form.solaranlage),
    kaufpreis: optionalNumber(form.kaufpreis),
    kaufdatum: form.kaufdatum || undefined,
    eigenkapital: optionalNumber(form.eigenkapital),
    darlehen_betrag: optionalNumber(form.darlehen_betrag),
    zinssatz: optionalNumber(form.zinssatz),
    tilgung: optionalNumber(form.tilgung),
    monatliche_rate: optionalNumber(form.monatliche_rate),
    gesamtmiete_ist: optionalNumber(form.gesamtmiete_ist),
    gesamtmiete_soll: optionalNumber(form.gesamtmiete_soll),
    denkmalschutz: fromBoolForm(form.denkmalschutz),
    denkmalschutz_bis: form.denkmalschutz_bis || undefined,
    barrierefrei: fromBoolForm(form.barrierefrei),
    aufzug: fromBoolForm(form.aufzug),
    gartennutzung: fromBoolForm(form.gartennutzung),
    lagebeschreibung: form.lagebeschreibung.trim() || undefined,
    anmerkungen: form.anmerkungen.trim() || undefined,
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
