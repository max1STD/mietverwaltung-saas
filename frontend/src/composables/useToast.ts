import { ref } from 'vue'

/**
 * Toast-Benachrichtigungen — globaler State für kurze Hinweise.
 *
 * Verwendung in Komponenten:
 * const { showToast, toasts } = useToast()
 * showToast('Erfolg', 'success')
 */

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
  id: number
  message: string
  type: ToastType
  duration: number
}

const toasts = ref<Toast[]>([])
let toastId = 0

export function useToast() {
  function removeToast(id: number): void {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function showToast(message: string, type: ToastType = 'info', duration = 4000): Toast {
    const id = ++toastId
    const toast: Toast = { id, message, type, duration }
    toasts.value.push(toast)

    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }

    return toast
  }

  return {
    toasts,
    showToast,
    removeToast,
  }
}

// Globale Hilfsfunktionen für Imports außerhalb von setup()
export const toastSuccess = (message: string, duration?: number) => useToast().showToast(message, 'success', duration)
export const toastError = (message: string, duration?: number) => useToast().showToast(message, 'error', duration)
export const toastInfo = (message: string, duration?: number) => useToast().showToast(message, 'info', duration)
export const toastWarning = (message: string, duration?: number) => useToast().showToast(message, 'warning', duration)