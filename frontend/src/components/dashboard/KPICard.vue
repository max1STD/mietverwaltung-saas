<template>
  <component
    :is="to ? 'RouterLink' : 'div'"
    :to="to"
    class="block bg-white rounded-xl border border-gray-100 p-5 shadow-[0_4px_12px_rgba(0,0,0,0.08)] transition hover:shadow-[0_6px_16px_rgba(0,0,0,0.12)] hover:-translate-y-0.5"
    :class="{ 'cursor-pointer': to }"
  >
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm font-medium text-gray-500">{{ label }}</p>
        <p class="text-3xl font-bold mt-1" :class="valueClass">{{ formattedValue }}</p>
        <p v-if="subtitle" class="text-xs text-gray-400 mt-1">{{ subtitle }}</p>
      </div>
      <span v-if="icon" class="text-2xl">{{ icon }}</span>
    </div>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

interface Props {
  label: string
  value: string | number
  subtitle?: string
  icon?: string
  variant?: 'default' | 'danger'
  to?: RouteLocationRaw
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
})

const valueClass = computed(() =>
  props.variant === 'danger' ? 'text-red-600' : 'text-[#0D3B70]',
)

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return new Intl.NumberFormat('de-DE').format(props.value)
  }
  return props.value
})
</script>
