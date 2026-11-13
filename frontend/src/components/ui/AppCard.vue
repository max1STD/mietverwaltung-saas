<template>
  <div :class="cardClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type PaddingSize = 'none' | 'sm' | 'md' | 'lg'
type ShadowSize = 'none' | 'sm' | 'md' | 'lg'

const props = withDefaults(
  defineProps<{
    padding?: PaddingSize
    shadow?: ShadowSize
    hover?: boolean
  }>(),
  {
    padding: 'md',
    shadow: 'md',
    hover: false,
  },
)

const paddingClasses: Record<PaddingSize, string> = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
}

const shadowClasses: Record<ShadowSize, string> = {
  none: '',
  sm: 'shadow-sm',
  md: 'shadow-[0_4px_12px_rgba(0,0,0,0.08)]',
  lg: 'shadow-lg',
}

const cardClasses = computed(() => [
  'bg-white rounded-xl border border-gray-100 transition-all duration-150',
  paddingClasses[props.padding],
  shadowClasses[props.shadow],
  props.hover ? 'hover:shadow-lg hover:-translate-y-0.5 cursor-pointer' : '',
])
</script>
