<template>
  <div class="w-full">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <div class="relative">
      <input
        :id="id"
        :value="modelValue"
        :type="inputType"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :inputmode="inputmode"
        :maxlength="maxlength"
        :required="required"
        :disabled="disabled"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${id}-error` : undefined"
        class="w-full px-4 py-3 bg-white border rounded-xl text-gray-900 placeholder-gray-400 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70] disabled:bg-gray-100 disabled:cursor-not-allowed"
        :class="[error ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20' : 'border-gray-200 hover:border-gray-300']"
        @input="onInput"
        @blur="emit('blur', $event)"
      />

      <button
        v-if="type === 'password'"
        type="button"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:outline-none"
        @click="toggleVisibility"
      >
        <span v-if="showPassword">🙈</span>
        <span v-else>👁</span>
      </button>
    </div>

    <p v-if="error" :id="`${id}-error`" class="mt-1.5 text-sm text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1.5 text-sm text-gray-500">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  id: string
  modelValue: string
  label?: string
  type?: string
  placeholder?: string
  autocomplete?: string
  inputmode?: 'text' | 'decimal' | 'numeric' | 'tel' | 'search' | 'email' | 'url' | 'none'
  maxlength?: string | number
  required?: boolean
  disabled?: boolean
  error?: string
  hint?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur', event: FocusEvent): void
}>()

const showPassword = ref(false)

const inputType = computed(() => {
  if (props.type !== 'password') return props.type || 'text'
  return showPassword.value ? 'text' : 'password'
})

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

function toggleVisibility() {
  showPassword.value = !showPassword.value
}
</script>