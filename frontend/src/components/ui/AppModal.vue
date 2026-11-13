<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        @keydown.esc="close"
      >
        <!-- Hintergrund-Overlay -->
        <div
          class="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
          @click="close"
        />

        <!-- Modal-Inhalt -->
        <div
          class="relative bg-white rounded-2xl shadow-xl w-full max-h-[90vh] overflow-y-auto"
          :class="sizeClasses[size]"
        >
          <!-- Header -->
          <div
            v-if="title || showClose"
            class="flex items-center justify-between px-6 py-4 border-b border-gray-100"
          >
            <h3 v-if="title" class="text-lg font-semibold text-[#0D3B70]">
              {{ title }}
            </h3>
            <button
              v-if="showClose"
              type="button"
              class="text-gray-400 hover:text-gray-600 focus:outline-none p-1 rounded-lg hover:bg-gray-100"
              aria-label="Schließen"
              @click="close"
            >
              ✕
            </button>
          </div>

          <!-- Body -->
          <div class="p-6">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
type ModalSize = 'sm' | 'md' | 'lg' | 'xl'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    size?: ModalSize
    showClose?: boolean
  }>(),
  {
    size: 'md',
    showClose: true,
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const sizeClasses: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}

function close(): void {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
