<template>
  <div class="min-h-screen flex items-center justify-center bg-[#f5f5f7] px-4 py-12">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg border border-gray-200/60 p-8 sm:p-10">
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-semibold text-[#0D3B70] tracking-tight">Konto erstellen</h1>
        <p class="mt-2 text-sm text-gray-500">Starte mit 14 Tagen kostenlos. Keine Kreditkarte nötig.</p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmit">
        <AppInput
          id="full_name"
          v-model="fullName"
          type="text"
          label="Vollständiger Name"
          placeholder="Max Mustermann"
          :error="fieldErrors.full_name"
          autocomplete="name"
          required
        />

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
          placeholder="Mindestens 8 Zeichen"
          :error="fieldErrors.password"
          autocomplete="new-password"
          required
        />

        <div class="rounded-xl bg-gray-50 p-4 border border-gray-200">
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              v-model="dsgvoConsent"
              class="mt-1 rounded border-gray-300 text-[#0D3B70] focus:ring-[#0D3B70]"
              required
            />
            <span class="text-sm text-gray-600 leading-relaxed">
              Ich akzeptiere die
              <button type="button" class="text-[#0D3B70] hover:text-[#2a5a9e] font-medium underline" @click="showConsent = true">
                DSGVO-Einwilligung
              </button>
              zur Verarbeitung meiner Daten gemäß Art. 6 DSGVO.
            </span>
          </label>
          <p v-if="fieldErrors.dsgvo" class="mt-2 text-sm text-red-600">{{ fieldErrors.dsgvo }}</p>
        </div>

        <AppButton type="submit" variant="primary" :loading="authStore.loading" full-width>
          14 Tage kostenlos testen
        </AppButton>
      </form>

      <p class="mt-6 text-center text-sm text-gray-500">
        Bereits registriert?
        <RouterLink to="/login" class="text-[#0D3B70] hover:text-[#2a5a9e] font-medium ml-1">
          Anmelden
        </RouterLink>
      </p>
    </div>
  </div>

  <ConsentModal v-model="showConsent" @accept="dsgvoConsent = true" />
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConsentModal from '@/components/ConsentModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

const fullName = ref('')
const email = ref('')
const password = ref('')
const dsgvoConsent = ref(false)
const showConsent = ref(false)
const fieldErrors = reactive<Record<string, string>>({})

function validate(): boolean {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])

  if (!fullName.value.trim()) {
    fieldErrors.full_name = 'Name ist erforderlich.'
  }

  if (!email.value.trim()) {
    fieldErrors.email = 'E-Mail ist erforderlich.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    fieldErrors.email = 'Bitte gib eine gültige E-Mail-Adresse ein.'
  }

  if (!password.value) {
    fieldErrors.password = 'Passwort ist erforderlich.'
  } else if (password.value.length < 8) {
    fieldErrors.password = 'Passwort muss mindestens 8 Zeichen lang sein.'
  }

  if (!dsgvoConsent.value) {
    fieldErrors.dsgvo = 'Bitte akzeptiere die DSGVO-Einwilligung.'
  }

  return Object.keys(fieldErrors).length === 0
}

watch([fullName, email, password, dsgvoConsent], () => {
  Object.keys(fieldErrors).forEach((k) => delete fieldErrors[k])
})

async function handleSubmit() {
  if (!validate()) return

  const ok = await authStore.register({
    email: email.value,
    password: password.value,
    full_name: fullName.value,
  })

  if (!ok) {
    showToast(authStore.error?.message || 'Registrierung fehlgeschlagen.', 'error')
    return
  }

  showToast('Konto erfolgreich erstellt. Richte jetzt die Zwei-Faktor-Authentifizierung ein.', 'success')
  await router.push('/2fa-setup')
}
</script>