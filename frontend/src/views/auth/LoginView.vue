<template>
  <div class="min-h-screen flex items-center justify-center bg-[#f5f5f7] px-4 py-12">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg border border-gray-200/60 p-8 sm:p-10">
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-semibold text-[#0D3B70] tracking-tight">Anmelden</h1>
        <p class="mt-2 text-sm text-gray-500">Melde dich an, um deine Mietverwaltung zu öffnen.</p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmit">
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

        <AppInput
          id="password"
          v-model="password"
          type="password"
          label="Passwort"
          placeholder="••••••••"
          :error="fieldErrors.password"
          autocomplete="current-password"
          required
        />

        <div class="flex items-center justify-between text-sm">
          <label class="inline-flex items-center gap-2 text-gray-600">
            <input type="checkbox" v-model="rememberMe" class="rounded border-gray-300 text-[#0D3B70] focus:ring-[#0D3B70]" />
            Angemeldet bleiben
          </label>
          <RouterLink to="/password-reset" class="text-[#0D3B70] hover:text-[#2a5a9e] font-medium">
            Passwort vergessen?
          </RouterLink>
        </div>

        <AppButton type="submit" variant="primary" :loading="authStore.loading" full-width>
          Anmelden
        </AppButton>
      </form>

      <p class="mt-6 text-center text-sm text-gray-500">
        Noch kein Konto?
        <RouterLink to="/register" class="text-[#0D3B70] hover:text-[#2a5a9e] font-medium ml-1">
          Registrieren
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { showToast } = useToast()

const email = ref('')
const password = ref('')
const rememberMe = ref(true)
const fieldErrors = reactive<Record<string, string>>({})

function validate(): boolean {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])

  if (!email.value.trim()) {
    fieldErrors.email = 'E-Mail ist erforderlich.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    fieldErrors.email = 'Bitte gib eine gültige E-Mail-Adresse ein.'
  }

  if (!password.value) {
    fieldErrors.password = 'Passwort ist erforderlich.'
  }

  return Object.keys(fieldErrors).length === 0
}

watch([email, password], () => {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
})

async function handleSubmit() {
  if (!validate()) return

  try {
    const result = await authStore.login(email.value, password.value, rememberMe.value)

    // Bei requires_2fa hat das Backend ein Temp-Token gesetzt.
    if (result.requires_2fa) {
      showToast('Bitte verifiziere die Zwei-Faktor-Authentifizierung.', 'info')
      await router.push('/2fa-setup')
      return
    }

    // Nur weiterleiten, wenn der Store wirklich authentifiziert ist.
    if (!authStore.isAuthenticated) {
      showToast('Anmeldung fehlgeschlagen.', 'error')
      return
    }

    showToast('Erfolgreich angemeldet.', 'success')
    // Admin-User landet direkt im Admin-Panel, alle anderen auf Dashboard/Redirect.
    const redirect = authStore.isAdmin ? '/admin' : ((route.query.redirect as string) || '/dashboard')
    await router.push(redirect)
  } catch {
    showToast(authStore.error?.message || 'Anmeldung fehlgeschlagen.', 'error')
  }
}
</script>