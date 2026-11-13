<template>
  <div class="min-h-screen flex items-center justify-center bg-[#f5f5f7] px-4 py-12">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg border border-gray-200/60 p-8 sm:p-10">
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-semibold text-[#0D3B70] tracking-tight">Zwei-Faktor-Authentifizierung</h1>
        <p class="mt-2 text-sm text-gray-500">
          Sichere dein Konto mit einem Authenticator-App wie Google Authenticator, Authy oder 1Password.
        </p>
      </div>

      <div v-if="setupLoading" class="py-12 text-center text-gray-500">
        <span class="inline-block w-8 h-8 border-4 border-[#0D3B70] border-t-transparent rounded-full animate-spin"></span>
        <p class="mt-4 text-sm">QR-Code wird geladen …</p>
      </div>

      <template v-else>
        <div v-if="qrCodeUrl" class="flex flex-col items-center mb-6">
          <div class="bg-white p-3 rounded-xl border border-gray-200 shadow-sm">
            <img :src="qrCodeUrl" alt="TOTP QR-Code" class="w-48 h-48" />
          </div>
          <p class="mt-4 text-xs text-gray-500 text-center max-w-xs">
            Scanne den QR-Code oder gib den Secret-Code manuell ein:
          </p>
          <button
            type="button"
            class="mt-2 text-xs font-mono text-gray-700 bg-gray-100 px-3 py-1 rounded-lg break-all max-w-full"
            @click="copySecret"
          >
            {{ secret }}
          </button>
        </div>

        <form class="space-y-5" @submit.prevent="handleVerify">
          <AppInput
            id="totp"
            v-model="code"
            type="text"
            label="6-stelliger Code"
            placeholder="000000"
            :error="fieldErrors.code"
            autocomplete="one-time-code"
            inputmode="numeric"
            maxlength="6"
            required
          />

          <AppButton type="submit" variant="primary" :loading="authStore.loading" full-width>
            Verifizieren
          </AppButton>

          <AppButton
            type="button"
            variant="secondary"
            :disabled="authStore.loading"
            full-width
            @click="handleSkip"
          >
            Überspringen (wird beim nächsten Login erzwungen)
          </AppButton>
        </form>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

const code = ref('')
const qrCodeUrl = ref('')
const secret = ref('')
const setupLoading = ref(false)
const fieldErrors = reactive<Record<string, string>>({})

onMounted(async () => {
  setupLoading.value = true
  const data = await authStore.setup2fa()
  if (data) {
    qrCodeUrl.value = data.qr_code_url
    secret.value = data.secret
  } else {
    showToast(authStore.error?.message || 'QR-Code konnte nicht geladen werden.', 'error')
  }
  setupLoading.value = false
})

watch(code, () => {
  delete fieldErrors.code
})

function validate(): boolean {
  delete fieldErrors.code
  if (!/^\d{6}$/.test(code.value)) {
    fieldErrors.code = 'Bitte gib den 6-stelligen Code aus deiner Authenticator-App ein.'
    return false
  }
  return true
}

async function handleVerify() {
  if (!validate()) return

  const ok = await authStore.verify2fa(code.value)
  if (!ok) {
    showToast(authStore.error?.message || 'Code ungültig. Bitte versuche es erneut.', 'error')
    return
  }

  showToast('Zwei-Faktor-Authentifizierung erfolgreich eingerichtet.', 'success')
  await router.push('/dashboard')
}

function handleSkip() {
  authStore.skip2fa()
  showToast('Du kannst 2FA später unter "Sicherheit" einrichten.', 'warning')
  router.push('/dashboard')
}

function copySecret() {
  if (!secret.value) return
  navigator.clipboard.writeText(secret.value).then(() => {
    showToast('Secret in Zwischenablage kopiert.', 'success')
  })
}
</script>