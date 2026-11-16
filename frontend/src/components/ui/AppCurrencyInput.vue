<template>
  <div class="w-full">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <div class="relative">
      <input
        :id="id"
        :value="displayValue"
        type="text"
        inputmode="decimal"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :required="required"
        :disabled="disabled"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${id}-error` : undefined"
        class="w-full px-4 py-3 bg-white border rounded-xl text-gray-900 placeholder-gray-400 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70] disabled:bg-gray-100 disabled:cursor-not-allowed"
        :class="[error ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : 'border-gray-200 hover:border-gray-300']"
        @input="onInput"
        @blur="onBlur"
      />

      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm pointer-events-none">
        €
      </span>
    </div>

    <p v-if="error" :id="`${id}-error`" class="mt-1.5 text-sm text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-sm text-gray-500">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  id: string
  modelValue: string
  label?: string
  placeholder?: string
  autocomplete?: string
  required?: boolean
  disabled?: boolean
  error?: string
  hint?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur', event: FocusEvent): void
}>()

const isFocused = ref(false)

function parseGermanNumber(value: string): number {
  const normalized = value
    .replace(/\./g, '') // Tausenderpunkte entfernen
    .replace(/,/g, '.') // Dezimalkomma in Punkt umwandeln
    .replace(/[^\d.]/g, '') // Nicht-Zahlen entfernen
  const number = parseFloat(normalized)
  return Number.isNaN(number) ? 0 : number
}

function formatGermanCurrency(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === '') return ''
  const number = typeof value === 'string' ? parseGermanNumber(value) : value
  if (Number.isNaN(number)) return ''
  return new Intl.NumberFormat('de-DE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(number)
}

const displayValue = computed(() => {
  if (isFocused.value) {
    // Während der Eingabe: rohen Wert ohne Formatierung anzeigen, aber normalisiert
    return props.modelValue
  }
  return formatGermanCurrency(props.modelValue)
})

function onInput(event: Event): void {
  const target = event.target as HTMLInputElement
  let value = target.value

  // Nur Zahlen, Komma, Punkt erlauben
  value = value.replace(/[^\d.,]/g, '')

  // Mehrere Kommas/Punkte verhindern: nur das letzte Dezimalzeichen erlauben
  const parts = value.split(/[,.]/)
  if (parts.length > 2) {
    value = parts[0] + ',' + parts.slice(1).join('')
  }

  emit('update:modelValue', value)
}

function onBlur(event: FocusEvent): void {
  isFocused.value = false
  const number = parseGermanNumber(props.modelValue)
  emit('update:modelValue', number > 0 ? String(number) : '')
  emit('blur', event)
}

watch(
  () => props.modelValue,
  () => {
    // Externe Änderungen werden beim nächsten Fokus/Blur neu formatiert
  },
)
</script>
