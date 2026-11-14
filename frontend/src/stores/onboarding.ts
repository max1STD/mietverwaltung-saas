import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Onboarding-Store — Fortschritt und Setup-Checkliste für neue Vermieter.
 *
 * Endpunkte:
 * - GET  /api/v1/onboarding/progress
 * - POST /api/v1/onboarding/complete-step
 */

export type OnboardingStepKey =
  | 'profile_completed'
  | 'first_objekt'
  | 'first_einheit'
  | 'first_mieter'
  | 'first_vertrag'
  | 'abo_confirmed'

export interface OnboardingStep {
  key: OnboardingStepKey
  label: string
  description: string
  is_done: boolean
  done_at?: string | null
}

export interface OnboardingProgress {
  user_id: string
  progress_percent: number
  steps: OnboardingStep[]
}

export const useOnboardingStore = defineStore('onboarding', () => {
  // State
  const progress = ref<OnboardingProgress | null>(null)
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  const progressPercent = computed(() => progress.value?.progress_percent ?? 0)

  const isDone = computed(() => progressPercent.value >= 100)

  const steps = computed<OnboardingStep[]>(() =>
    progress.value?.steps ?? [
      { key: 'profile_completed', label: 'Profil vervollständigen', description: 'Name, Kontaktdaten und Bankverbindung hinterlegen.', is_done: false },
      { key: 'first_objekt', label: 'Erstes Objekt anlegen', description: 'Leg deine erste Immobilie an.', is_done: false },
      { key: 'first_einheit', label: 'Erste Einheit anlegen', description: 'Füge dem Objekt eine Wohneinheit hinzu.', is_done: false },
      { key: 'first_mieter', label: 'Ersten Mieter eintragen', description: 'Speicher die Stammdaten deines Mieters.', is_done: false },
      { key: 'first_vertrag', label: 'Ersten Mietvertrag abschließen', description: 'Verknüpfe Mieter, Einheit und Mietkonditionen.', is_done: false },
      { key: 'abo_confirmed', label: 'Abo bestätigen', description: 'Wähle und bestätige deinen Tarif.', is_done: false },
    ],
  )

  /**
   * Onboarding-Fortschritt laden.
   */
  async function fetchProgress(): Promise<OnboardingProgress | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<OnboardingProgress>('/onboarding/progress')
      progress.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Einen Schritt manuell als erledigt markieren.
   */
  async function completeStep(step: OnboardingStepKey): Promise<OnboardingProgress | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<OnboardingProgress>('/onboarding/complete-step', { step })
      progress.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Localen Fortschritt aktualisieren (z. B. nach externen Aktionen).
   */
  function setProgress(value: OnboardingProgress | null): void {
    progress.value = value
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    progress,
    loading,
    saving,
    error,
    progressPercent,
    isDone,
    steps,
    fetchProgress,
    completeStep,
    setProgress,
    clearError,
  }
})
