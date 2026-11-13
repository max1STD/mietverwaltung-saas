<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="emit('click', $event)"
  >
    <span v-if="loading" class="inline-flex items-center gap-2">
      <span class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" aria-hidden="true"></span>
      <span>{{ loadingText || 'Bitte warten …' }}</span>
    </span>
    <span v-else>
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

const props = withDefaults(
  defineProps<{
    variant?: ButtonVariant
    size?: ButtonSize
    type?: 'button' | 'submit' | 'reset'
    loading?: boolean
    loadingText?: string
    disabled?: boolean
    fullWidth?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    type: 'button',
  },
)

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const baseClasses =
  'inline-flex items-center justify-center rounded-xl font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-6 py-3 text-base',
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-[#0D3B70] text-white shadow-md hover:bg-[#2a5a9e] hover:shadow-lg focus:ring-[#0D3B70] active:bg-[#092c54]',
  secondary:
    'bg-white text-[#0D3B70] border border-gray-200 shadow-sm hover:bg-gray-50 hover:border-gray-300 focus:ring-[#0D3B70] active:bg-gray-100',
  danger:
    'bg-red-600 text-white shadow-md hover:bg-red-700 hover:shadow-lg focus:ring-red-500 active:bg-red-800',
  ghost:
    'bg-transparent text-[#0D3B70] hover:bg-[#0D3B70]/5 focus:ring-[#0D3B70]',
}

const buttonClasses = computed(() => [
  baseClasses,
  sizeClasses[props.size],
  variantClasses[props.variant],
  props.fullWidth ? 'w-full' : '',
])
</script>