<template>
  <AppCard v-if="!onboardingStore.isDone" padding="md" shadow="md" class="mb-8">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
      <div>
        <h2 class="text-lg font-semibold text-[#0D3B70]">Setup-Checkliste</h2>
        <p class="text-sm text-gray-500">
          Schließe die ersten Schritte ab, um MietVerwaltung vollständig nutzen zu können.
        </p>
      </div>
      <div class="text-right">
        <span class="text-2xl font-bold text-[#0D3B70]">{{ onboardingStore.progressPercent }}%</span>
      </div>
    </div>

    <!-- Progress-Bar -->
    <div class="w-full bg-gray-100 rounded-full h-2.5 mb-6">
      <div
        class="bg-[#0D3B70] h-2.5 rounded-full transition-all duration-500"
        :style="{ width: `${onboardingStore.progressPercent}%` }"
      />
    </div>

    <!-- Schritte -->
    <ul class="space-y-3">
      <li
        v-for="step in onboardingStore.steps"
        :key="step.key"
        class="flex items-start gap-3 p-3 rounded-xl transition-colors"
        :class="step.is_done ? 'bg-green-50' : 'bg-gray-50'"
      >
        <div
          class="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5"
          :class="step.is_done ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500'"
        >
          <span v-if="step.is_done">✓</span>
          <span v-else class="text-xs">{{ stepNumber(step.key) }}</span>
        </div>

        <div class="flex-1">
          <p
            class="font-medium"
            :class="step.is_done ? 'text-green-800 line-through' : 'text-gray-800'"
          >
            {{ step.label }}
          </p>
          <p class="text-sm text-gray-500">{{ step.description }}</p>
        </div>

        <AppButton
          v-if="!step.is_done"
          variant="secondary"
          size="sm"
          :loading="onboardingStore.saving"
          @click="complete(step.key)"
        >
          Erledigt
        </AppButton>
      </li>
    </ul>
  </AppCard>
</template>

<script setup lang="ts">
import { useOnboardingStore, type OnboardingStepKey } from '@/stores/onboarding'
import { useToast } from '@/composables/useToast'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'

const onboardingStore = useOnboardingStore()
const { showToast } = useToast()

const orderedSteps: OnboardingStepKey[] = [
  'profile_completed',
  'first_objekt',
  'first_einheit',
  'first_mieter',
  'first_vertrag',
  'abo_confirmed',
]

function stepNumber(key: OnboardingStepKey): number {
  return orderedSteps.indexOf(key) + 1
}

async function complete(key: OnboardingStepKey): Promise<void> {
  const result = await onboardingStore.completeStep(key)
  if (result) {
    showToast('Schritt als erledigt markiert.', 'success')
  } else {
    showToast(onboardingStore.error?.message || 'Fehler beim Speichern.', 'error')
  }
}
</script>
