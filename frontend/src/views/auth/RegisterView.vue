<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="bg-white p-8 rounded-2xl shadow-sm border border-gray-200 w-full max-w-md">
      <h2 class="text-2xl font-bold text-[#0D3B70] mb-6">Konto erstellen</h2>
      <form class="space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input type="text" v-model="name" required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0D3B70]" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">E-Mail</label>
          <input type="email" v-model="email" required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0D3B70]" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Passwort</label>
          <input type="password" v-model="password" required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#0D3B70]" />
        </div>
        <button type="submit"
          class="w-full bg-[#0D3B70] text-white py-2 rounded-lg hover:bg-[#2a5a9e]">
          14 Tage kostenlos testen
        </button>
      </form>
      <p class="text-sm text-gray-500 mt-4 text-center">
        Bereits registriert?
        <RouterLink to="/login" class="text-[#0D3B70] font-medium">Anmelden</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')

async function onSubmit() {
  // TODO: Phase 1 — Auth-Implementierung
  router.push('/dashboard')
}
</script>
