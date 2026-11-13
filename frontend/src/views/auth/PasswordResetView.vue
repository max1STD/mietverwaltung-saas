<template>
  <div class="min-h-screen flex items-center justify-center bg-[#f5f5f7] px-4 py-12">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg border border-gray-200/60 p-8 sm:p-10">
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-semibold text-[#0D3B70] tracking-tight">Passwort zurücksetzen</h1>
        <p class="mt-2 text-sm text-gray-500">
          Gib deine E-Mail-Adresse ein. Wir senden dir einen Link zum Zurücksetzen.
        </p>
      </div>

      <div v-if="submitted" class="text-center space-y-4">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p class="text-gray-700">
          Falls ein Konto mit <strong>{{ email }}</strong> existiert, haben wir eine E-Mail zum Zurücksetzen gesendet.
        </p>
        <p class="text-sm text-gray-500">Prüfe auch deinen Spam-Ordner.</p>
        <AppButton variant="secondary" full-width @click="router.push('/login')">
          Zurück zum Login
        </AppButton>
      </div>

      <form v-else class="space-y-5" @submit.prevent="handleSubmit">
        <AppInput
          id="email"
          v-model="email"
          type="email"
          label="E-Mail"
          placeholder="name@beispiel.de"
          :error="fieldErrors.email"
          autocomplete="email"
          required
        />

        <AppButton type="submit" variant="primary" :loading="loading" full-width>
          Link senden
        </AppButton>
      </form>

      <p class="mt-6 text-center text-sm text-gray-500">
        <RouterLink to="/login" class="text-[#0D3B70] hover:text-[#2a5a9e] font-medium">
          Zurück zum Login
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '@/api/client'
import { useToast } from '@/composables/useToast'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const { showToast } = useToast()

const email = ref('')
const loading = ref(false)
const submitted = ref(false)
const fieldErrors = reactive<Record<string, string>>({})

watch(email, () => {
  delete fieldErrors.email
})

function validate(): boolean {
  delete fieldErrors.email
  if (!email.value.trim()) {
    fieldErrors.email = 'E-Mail ist erforderlich.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    fieldErrors.email = 'Bitte gib eine gültige E-Mail-Adresse ein.'
  }
  return !fieldErrors.email
}

async function handleSubmit() {
  if (!validate()) return
  loading.value = true

  try {
    await apiClient.post('/auth/password-reset', { email: email.value })
    submitted.value = true
    showToast('E-Mail zum Zurücksetzen wurde gesendet.', 'success')
  } catch (err) {
    // Aus Sicherheitsgründen immer Erfolg anzeigen, um User-Enumeration zu vermeiden
    submitted.value = true
    showToast('E-Mail zum Zurücksetzen wurde gesendet.', 'success')
  } finally {
    loading.value = false
  }
}
</script>