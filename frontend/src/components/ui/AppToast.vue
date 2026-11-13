<template>
  <Teleport to="body">
    <TransitionGroup
      tag="div"
      name="toast"
      class="fixed bottom-6 right-6 z-[100] flex flex-col gap-3 pointer-events-none"
      aria-live="polite"
      aria-atomic="true"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto min-w-[16rem] max-w-sm px-4 py-3 rounded-xl shadow-lg border text-sm font-medium flex items-start gap-3"
        :class="toastClasses[toast.type]"
        role="status"
      >
        <span class="mt-0.5 shrink-0">{{ iconFor(toast.type) }}</span>
        <span class="flex-1">{{ toast.message }}</span>
        <button
          type="button"
          class="shrink-0 text-current opacity-70 hover:opacity-100"
          @click="removeToast(toast.id)"
          aria-label="Schließen"
        >
          ✕
        </button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast, ToastType } from '@/composables/useToast'

const { toasts, removeToast } = useToast()

const toastClasses: Record<ToastType, string> = {
  success: 'bg-green-50 text-green-800 border-green-200',
  error: 'bg-red-50 text-red-800 border-red-200',
  info: 'bg-[#0D3B70] text-white border-[#0D3B70]',
  warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
}

function iconFor(type: ToastType): string {
  switch (type) {
    case 'success':
      return '✓'
    case 'error':
      return '⚠'
    case 'warning':
      return '▲'
    case 'info':
    default:
      return 'ℹ'
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(1rem) scale(0.95);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(1rem);
}
</style>