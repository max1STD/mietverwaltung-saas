<template>
  <div class="flex flex-col items-center justify-center py-12 text-center">
    <div
      class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center text-2xl mb-4 text-[#0D3B70]"
    >
      {{ icon }}
    </div>
    <h3 class="text-lg font-semibold text-[#0D3B70] mb-1">{{ title }}</h3>
    <p v-if="description" class="text-sm text-gray-500 mb-5 max-w-xs">{{ description }}</p>
    <AppButton
      v-if="actionLabel"
      variant="primary"
      @click="emit('action')"
    >
      {{ actionLabel }}
    </AppButton>
  </div>
</template>

<script setup lang="ts">
import AppButton from './AppButton.vue'

const props = defineProps<{
  icon: string
  title: string
  description?: string
  actionLabel?: string
}>()

const emit = defineEmits<{
  (e: 'action'): void
}>()
</script>
