<template>
  <span :class="badgeClasses">
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type BadgeVariant = 'green' | 'yellow' | 'red' | 'blue' | 'gray' | 'navy'

const props = withDefaults(
  defineProps<{
    variant?: BadgeVariant
  }>(),
  {
    variant: 'gray',
  },
)

const variantClasses: Record<BadgeVariant, string> = {
  green: 'bg-green-100 text-green-800 border-green-200',
  yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  red: 'bg-red-100 text-red-800 border-red-200',
  blue: 'bg-blue-100 text-blue-800 border-blue-200',
  gray: 'bg-gray-100 text-gray-700 border-gray-200',
  navy: 'bg-[#0D3B70]/10 text-[#0D3B70] border-[#0D3B70]/20',
}

const badgeClasses = computed(() => [
  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
  variantClasses[props.variant],
])
</script>
