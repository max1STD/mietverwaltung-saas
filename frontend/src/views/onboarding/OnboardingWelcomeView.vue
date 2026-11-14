<template>
  <div class="min-h-screen bg-[#f5f5f7] pb-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 lg:pt-16">
      <AppCard padding="lg" shadow="lg" class="text-center">
        <div class="mb-6">
          <div class="w-20 h-20 bg-[#0D3B70]/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-4xl">🏠</span>
          </div>
          <h1 class="text-3xl sm:text-4xl font-bold text-[#0D3B70]">
            Willkommen bei MietVerwaltung
          </h1>
          <p class="text-gray-500 mt-3 text-lg max-w-xl mx-auto">
            Die smartere Art, deine Immobilien, Mieter und Finanzen an einem Ort zu verwalten.
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 text-left">
          <div class="bg-gray-50 rounded-xl p-4">
            <span class="text-2xl block mb-2">📊</span>
            <h3 class="font-semibold text-[#0D3B70]">Alles im Blick</h3>
            <p class="text-sm text-gray-500 mt-1">Dashboard, KPIs und Finanzen auf einen Blick.</p>
          </div>
          <div class="bg-gray-50 rounded-xl p-4">
            <span class="text-2xl block mb-2">🤝</span>
            <h3 class="font-semibold text-[#0D3B70]">Mieter & Verträge</h3>
            <p class="text-sm text-gray-500 mt-1">Stammdaten, Mietverträge und Bewerbungen einfach verwalten.</p>
          </div>
          <div class="bg-gray-50 rounded-xl p-4">
            <span class="text-2xl block mb-2">⚡</span>
            <h3 class="font-semibold text-[#0D3B70]">Schneller Start</h3>
            <p class="text-sm text-gray-500 mt-1">In wenigen Schritten mit deinem ersten Objekt loslegen.</p>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
          <AppButton size="lg" @click="startSetup">
            Setup starten
          </AppButton>
          <AppButton size="lg" variant="secondary" @click="$router.push('/dashboard')">
            Zum Dashboard
          </AppButton>
        </div>
      </AppCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router = useRouter()

function startSetup(): void {
  router.push('/objekte/neu')
}
</script>
