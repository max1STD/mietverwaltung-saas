<template>
  <div class="space-y-4">
    <div class="p-4 bg-[#0D3B70]/5 rounded-xl border border-[#0D3B70]/10">
      <h4 class="text-sm font-semibold text-[#0D3B70] mb-2 flex items-center gap-2">
        <span>📷</span>
        Beleg-Scan (KI-Vorschlag)
      </h4>
      <p class="text-sm text-gray-600 mb-4">
        Lade einen Beleg hoch und erhalte automatisch einen Vorschlag für Betrag,
        Kategorie und Umlagefähigkeit.
      </p>

      <div class="space-y-3">
        <label
          for="receipt-upload"
          class="flex items-center justify-center gap-2 w-full px-4 py-6 border-2 border-dashed border-gray-300 rounded-xl bg-white hover:border-[#0D3B70] hover:bg-[#0D3B70]/5 transition-colors cursor-pointer"
        >
          <span class="text-2xl">📄</span>
          <span class="text-sm text-gray-600">
            {{ selectedFile ? selectedFile.name : 'Beleg hochladen (PDF, JPG, PNG)' }}
          </span>
          <input
            id="receipt-upload"
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            class="hidden"
            @change="onFileSelected"
          >
        </label>

        <AppButton
          full-width
          :loading="scanning"
          :disabled="!selectedFile"
          @click="startScan"
        >
          Beleg scannen
        </AppButton>
      </div>
    </div>

    <!-- Scan-Ergebnis-Vorschlag -->
    <div
      v-if="result"
      class="p-4 bg-white rounded-xl border border-gray-200 shadow-sm"
    >
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-semibold text-[#0D3B70]">Erkannter Beleg</h4>
        <AppBadge :variant="badgeForConfidence(result.konfidenz)">
          {{ confidenceLabel(result.konfidenz) }}
        </AppBadge>
      </div>

      <dl class="space-y-2 text-sm">
        <div class="flex justify-between">
          <dt class="text-gray-500">Betrag</dt>
          <dd class="font-medium text-gray-900">{{ formatCurrency(result.betrag_vorschlag) }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">Kategorie</dt>
          <dd class="font-medium text-gray-900">{{ result.kategorie_vorschlag || '–' }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">Umlagefähig</dt>
          <dd class="font-medium text-gray-900">{{ result.umlagefaehig_vorschlag ? 'Ja' : 'Nein' }}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-gray-500">Verteilung</dt>
          <dd class="font-medium text-gray-900">{{ schluesselLabel(result.umlageschluessel_vorschlag) }}</dd>
        </div>
      </dl>

      <div class="flex gap-2 mt-4">
        <AppButton
          size="sm"
          variant="ghost"
          full-width
          @click="clearResult"
        >
          Verwerfen
        </AppButton>
        <AppButton
          size="sm"
          full-width
          @click="applyResult"
        >
          Übernehmen
        </AppButton>
      </div>

      <p class="text-xs text-gray-400 mt-3">
        Hinweis: In dieser Phase ohne echte OCR/KI — das Ergebnis ist ein Platzhalter.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ScanErgebnis, Umlageschluessel } from '@/stores/kosten'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const emit = defineEmits<{
  (e: 'scan', file: File): void
  (e: 'apply', result: ScanErgebnis): void
}>()

const selectedFile = ref<File | null>(null)
const result = ref<ScanErgebnis | null>(null)

const scanning = defineModel<boolean>('scanning', { default: false })

function onFileSelected(event: Event): void {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    selectedFile.value = file
  }
}

function startScan(): void {
  if (!selectedFile.value) return
  emit('scan', selectedFile.value)
}

function setScanResult(scanResult: ScanErgebnis): void {
  result.value = scanResult
}

function clearResult(): void {
  result.value = null
  selectedFile.value = null
}

function applyResult(): void {
  if (result.value) {
    emit('apply', result.value)
  }
}

function formatCurrency(value?: number): string {
  if (value == null) return '–'
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function badgeForConfidence(
  confidence?: 'niedrig' | 'mittel' | 'hoch',
): 'green' | 'yellow' | 'gray' {
  switch (confidence) {
    case 'hoch':
      return 'green'
    case 'mittel':
      return 'yellow'
    default:
      return 'gray'
  }
}

function confidenceLabel(confidence?: 'niedrig' | 'mittel' | 'hoch'): string {
  switch (confidence) {
    case 'hoch':
      return 'Sehr sicher'
    case 'mittel':
      return 'Wahrscheinlich'
    default:
      return 'Unsicher'
  }
}

function schluesselLabel(schluessel?: Umlageschluessel | string): string {
  switch (schluessel) {
    case 'nach_qm':
      return 'Nach Quadratmetern'
    case 'nach_personen':
      return 'Nach Personen'
    case 'nach_verbrauch':
      return 'Nach Verbrauch'
    case 'gleich':
      return 'Gleich verteilt'
    default:
      return '–'
  }
}

defineExpose({
  setScanResult,
  clearResult,
})
</script>
