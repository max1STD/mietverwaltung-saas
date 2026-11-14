<template>
  <span
    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
    :class="badgeClasses"
  >
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export type BadgeStatus = 'neu' | 'in_pruefung' | 'angenommen' | 'abgelehnt' | string

const props = defineProps<{
  status: BadgeStatus
}>()

const config: Record<string, { label: string; classes: string }> = {
  neu: { label: 'Neu', classes: 'bg-blue-100 text-blue-800' },
  in_pruefung: { label: 'In Prüfung', classes: 'bg-yellow-100 text-yellow-800' },
  angenommen: { label: 'Angenommen', classes: 'bg-green-100 text-green-800' },
  abgelehnt: { label: 'Abgelehnt', classes: 'bg-red-100 text-red-800' },
}

const resolved = computed(() => config[props.status] || { label: props.status, classes: 'bg-gray-100 text-gray-800' })

const label = computed(() => resolved.value.label)
const badgeClasses = computed(() => resolved.value.classes)
</script>
