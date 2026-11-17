<template>
  <div>
    <label :for="id" class="block text-sm font-medium text-gray-700 mb-1">{{ label }}</label>
    <select
      :id="id"
      :value="modelValue"
      class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#0D3B70]/20 focus:border-[#0D3B70]"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option value="">Bitte wählen</option>
      <option value="true">Ja</option>
      <option value="false">Nein</option>
    </select>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  id: string
  label: string
  modelValue: string
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>
