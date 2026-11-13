<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center px-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="consent-title"
        @click.self="emit('update:modelValue', false)"
      >
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm transition-opacity"></div>

        <div class="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-white rounded-2xl shadow-2xl border border-gray-200/60 p-6 sm:p-8">
          <div class="mb-6">
            <h2 id="consent-title" class="text-2xl font-semibold text-[#0D3B70]">DSGVO-Einwilligung</h2>
            <p class="mt-1 text-sm text-gray-500">Version 1.0 — Stand: 13.11.2026</p>
          </div>

          <div class="space-y-4 text-sm text-gray-700 leading-relaxed">
            <p>
              Wir nehmen den Schutz deiner Daten sehr ernst. Diese Einwilligung informiert dich über die Verarbeitung
              deiner personenbezogenen Daten gemäß der Datenschutz-Grundverordnung (DSGVO).
            </p>

            <div class="rounded-xl bg-gray-50 border border-gray-200 p-4">
              <h3 class="font-semibold text-[#0D3B70] mb-2">1. Verantwortlicher</h3>
              <p>MietVerwaltung GmbH, vertreten durch den Geschäftsführer. Kontakt: privacy@mietverwaltung.example</p>
            </div>

            <div class="rounded-xl bg-gray-50 border border-gray-200 p-4">
              <h3 class="font-semibold text-[#0D3B70] mb-2">2. Zwecke der Verarbeitung</h3>
              <ul class="list-disc pl-5 space-y-1">
                <li>Bereitstellung der Mietverwaltungs-Software</li>
                <li>Verwaltung von Vermietern, Mietern, Objekten und Einheiten</li>
                <li>Verarbeitung von Tickets, Dokumenten und Abrechnungen</li>
                <li>E-Mail-Benachrichtigungen zu relevanten Ereignissen</li>
                <li>Sicherheit und Betrugsprävention (z. B. 2FA, Audit-Log)</li>
              </ul>
            </div>

            <div class="rounded-xl bg-gray-50 border border-gray-200 p-4">
              <h3 class="font-semibold text-[#0D3B70] mb-2">3. Rechtsgrundlage</h3>
              <p>Die Verarbeitung erfolgt auf Grundlage deiner Einwilligung gemäß Art. 6 Abs. 1 lit. a DSGVO.</p>
            </div>

            <div class="rounded-xl bg-gray-50 border border-gray-200 p-4">
              <h3 class="font-semibold text-[#0D3B70] mb-2">4. Empfänger und Auftragsverarbeiter</h3>
              <p>
                Deine Daten werden ausschließlich in der Europäischen Union gespeichert. Auftragsverarbeiter
                (z. B. Rechenzentrum, E-Mail-Dienst) sind durch Auftragsverarbeitungsverträge (AVV) gebunden.
              </p>
            </div>

            <div class="rounded-xl bg-gray-50 border border-gray-200 p-4">
              <h3 class="font-semibold text-[#0D3B70] mb-2">5. Deine Rechte</h3>
              <ul class="list-disc pl-5 space-y-1">
                <li>Recht auf Auskunft, Berichtigung und Löschung</li>
                <li>Recht auf Einschränkung der Verarbeitung</li>
                <li>Recht auf Datenübertragbarkeit</li>
                <li>Widerruf der Einwilligung jederzeit mit Wirkung für die Zukunft</li>
              </ul>
            </div>

            <p class="text-xs text-gray-500">
              Mit Klick auf „Akzeptieren“ stimmst du der Verarbeitung deiner Daten für die genannten Zwecke zu.
              Ohne diese Einwilligung können wir dir leider keinen Zugang gewähren.
            </p>
          </div>

          <div class="mt-8 flex flex-col-reverse sm:flex-row gap-3">
            <AppButton variant="secondary" full-width @click="decline">Ablehnen</AppButton>
            <AppButton variant="primary" full-width @click="accept">Akzeptieren</AppButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'accept'): void
}>()

function accept() {
  emit('accept')
  emit('update:modelValue', false)
}

function decline() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>